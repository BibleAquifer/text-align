"""retry-alignment: re-align verses with too many unaligned source tokens.

After fetch-batch writes chapter JSON files, this command identifies verses
where more than N source tokens are unaligned and re-aligns them from scratch
(blank-slate — no candidates passed to the LLM).

CLI entry point: retry-alignment
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from text_align import ROOT
from text_align.config import load_config_from_args, require
from text_align.migrate.tsv import process_usfm_tsv

from .clean import run_clean_pass
from .coverage import VerseRetrySpec, find_low_coverage_verses
from .llm import LLMClient
from .retry import (
    _filter_chapter_files,
    build_retry_chapter_batches,
    discover_chapter_files,
    retry_chapter_sync,
)
from .scoring import ScoringConfig, score_chapter_file
from .source import load_source_verses
from .util import _CORPUS_ID, _chapter_id_from_path


_SOURCES_DIR = ROOT / "data" / "sources"
_JOBS_DIR = ROOT / "jobs"


def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="LLM-REFINED")

    p = argparse.ArgumentParser(
        description=(
            "Re-align verses with too many unaligned source tokens. "
            "Evaluates existing chapter JSON files, flags verses where more than "
            "N source tokens are unaligned, and re-aligns them from scratch."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--alignment-dir", default=None, type=Path,
                   help="Directory containing chapter JSON files to evaluate and retry")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code, e.g. eng")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID, e.g. OENGB")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<edition>.tsv and nt_<edition>.tsv")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing SBLGNT.tsv and WLCM.tsv (default: {_SOURCES_DIR})")
    p.add_argument("--corpus", default=None, choices=["ot", "nt"],
                   help="Corpus: 'nt' for SBLGNT, 'ot' for WLCM")
    p.add_argument("--llm-provider", default="anthropic",
                   choices=["openai", "anthropic", "google", "openrouter", "gloo", "ollama"],
                   help="LLM provider (default: anthropic)")
    p.add_argument("--llm-model", default=None,
                   help="Model name for the chosen provider")
    p.add_argument("--reasoning-effort", default=None,
                   choices=["none", "minimal", "low", "medium", "high"],
                   help="Reasoning effort level")
    p.add_argument("--batch-size", type=int, default=5,
                   help="Verses per LLM call (default: 5)")
    p.add_argument("--max-retries", type=int, default=2,
                   help="Retry attempts on validation failure (default: 2)")
    p.add_argument("--max-api-retries", type=int, default=4,
                   help="Retry attempts on transient API errors with exponential backoff (default: 4)")
    p.add_argument("--temperature", type=float, default=1,
                   help="Sampling temperature (default: 1)")
    p.add_argument("--max-output-tokens", type=int, default=4000,
                   help="Hard cap on response tokens (default: 4000)")
    p.add_argument("--creator", default="text-align",
                   help="Creator string for alignment meta (default: text-align)")
    p.add_argument("--score-retry-threshold", type=float, default=0.25,
                   help="Composite penalty threshold above which a verse is retried (default: 0.25)")
    p.add_argument("--min-unaligned-src", type=int, default=2,
                   help="Also retry verses with N or more unaligned source tokens (default: 2)")
    p.add_argument("--batch-mode", choices=["sync", "async"], default="sync",
                   help="sync: re-align immediately and write results (default); "
                        "async: submit to provider batch API, then block until "
                        "results are ready and merge verse records (same output as sync)")
    p.add_argument("--jobs-dir", default=_JOBS_DIR, type=Path,
                   help=f"Directory for async batch job metadata (default: {_JOBS_DIR})")
    p.add_argument("--dry-run", action="store_true", default=False,
                   help="Report flagged verses without calling the LLM")
    p.add_argument("--semantic-model", default="sentence-transformers/LaBSE",
                   help="sentence-transformers model for semantic similarity check "
                        "(default: sentence-transformers/LaBSE). Pass empty string to disable.")
    p.add_argument("--semantic-threshold", type=float, default=0.35,
                   help="Cosine similarity below which a record is flagged (default: 0.35)")

    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--verse", default=None, metavar="BBCCCVVV",
                             help="Force-retry a single verse regardless of score, e.g. --verse 41004003")
    range_group.add_argument("--verse-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Force-retry a verse range regardless of score, e.g. --verse-range 41004001 41004020")
    range_group.add_argument("--verse-list", default=None, metavar="VIDS",
                             help="Comma-separated verse IDs to force-retry regardless of score, "
                                  "e.g. --verse-list 62002002,62003010")
    range_group.add_argument("--verse-list-file", default=None, type=Path, metavar="FILE",
                             help="File of verse IDs to force-retry regardless of score "
                                  "(one BBCCCVVV per line; blank lines and # comments ignored)")
    range_group.add_argument("--book", default=None, metavar="BB",
                             help="Limit to a single book, e.g. --book 66")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Limit to a book range, e.g. --book-range 65 66")
    range_group.add_argument("--chapter", default=None, metavar="BBCCC",
                             help="Limit to a single chapter, e.g. --chapter 66007")
    range_group.add_argument("--chapter-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Limit to a chapter range, e.g. --chapter-range 66001 66022")

    p.add_argument("--retry-failed", action="store_true", default=False,
                   help="Retry verses with no alignment records in --alignment-dir "
                        "(skips scoring; combine with --book/--chapter/etc. to limit scope)")

    p.add_argument("--fallback-threshold", type=float, default=0.25,
                   help="If flagged verses / total verses >= this value, use the refine model "
                        "instead of the retry model (default: 0.25)")

    p.set_defaults(**config_defaults)
    args = p.parse_args()

    if args.retry_failed and any([
        getattr(args, "verse", None),
        getattr(args, "verse_range", None),
        getattr(args, "verse_list", None),
        getattr(args, "verse_list_file", None),
    ]):
        p.error("--retry-failed cannot be combined with --verse, --verse-range, --verse-list, or --verse-list-file")

    # Save refine-phase model settings before retry overrides are applied.
    args._refine_llm_provider    = args.llm_provider
    args._refine_llm_model       = args.llm_model
    args._refine_reasoning_effort = args.reasoning_effort
    args._refine_max_output_tokens = args.max_output_tokens

    # Retry-specific model keys fall back to the refine model keys when absent.
    # This allows a single config to use one model for both passes, or separate
    # configs to specify different models per pass.
    args.llm_provider     = getattr(args, "retry_llm_provider",     None) or args.llm_provider
    args.llm_model        = getattr(args, "retry_llm_model",        None) or args.llm_model
    args.reasoning_effort = getattr(args, "retry_reasoning_effort", None) or args.reasoning_effort
    args.max_output_tokens = getattr(args, "retry_max_output_tokens", None) or args.max_output_tokens

    require(args, "alignment_dir", "target_language", "target_edition", "target_tsv_dir", "corpus")

    if args.llm_model is None and not args.dry_run:
        raise SystemExit(
            "error: --llm-model is required (or set in --config) unless --dry-run"
        )

    return args


def _effort_str(effort: str | None) -> str:
    return f" (reasoning_effort={effort})" if effort else ""


def _aligned_verse_ids(chapter_path: Path) -> set[str]:
    try:
        data = json.loads(chapter_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    verse_ids: set[str] = set()
    for group in data.get("groups", []):
        for rec in group.get("records", []):
            for src_id in rec.get("source", []):
                if len(src_id) >= 8:
                    verse_ids.add(src_id[:8])
        neq_src = (group.get("meta") or {}).get("nonEquivalent", {}).get("source", [])
        for src_id in neq_src:
            if len(src_id) >= 8:
                verse_ids.add(src_id[:8])
    return verse_ids


def _collect_failed_verses(
    chapter_files: list[Path],
    source_verses: dict,
) -> frozenset[str]:
    failed: set[str] = set()
    for cf in chapter_files:
        chapter_id = _chapter_id_from_path(cf)
        src_verse_ids = {vid for vid in source_verses if vid[:5] == chapter_id}
        aligned = _aligned_verse_ids(cf)
        failed.update(src_verse_ids - aligned)
    return frozenset(failed)


def _write_retry_sidecars(
    retry_specs_by_chapter: dict[str, list[VerseRetrySpec]],
    chapter_paths: dict[str, Path],
    target_edition: str,
) -> None:
    """Write (or update) a .retries.json sidecar for each retried chapter.

    On repeated runs the passes count increments and retried_verses accumulates
    the union across all passes.
    """
    for chapter_id, specs in retry_specs_by_chapter.items():
        chapter_path = chapter_paths[chapter_id]
        sidecar_path = chapter_path.parent / (chapter_path.stem + ".retries.json")

        new_verses = {spec.verse_id for spec in specs}
        passes = 1
        prior_verses: set[str] = set()
        if sidecar_path.exists():
            try:
                existing = json.loads(sidecar_path.read_text(encoding="utf-8"))
                passes = existing.get("passes", 0) + 1
                prior_verses = set(existing.get("retried_verses", []))
            except (json.JSONDecodeError, KeyError):
                pass

        sidecar_path.write_text(
            json.dumps(
                {
                    "edition": target_edition,
                    "chapter_id": chapter_id,
                    "passes": passes,
                    "retried_verses": sorted(prior_verses | new_verses),
                },
                indent=2,
            ),
            encoding="utf-8",
        )


def main() -> None:
    args = parse_args()
    _start = time.time()
    corpus_id = _CORPUS_ID[args.corpus]

    print(f"retry-alignment: {args.target_edition} ({args.target_language})")
    print(f"  Alignment dir:   {args.alignment_dir}")
    print(f"  Retry threshold: score>{args.score_retry_threshold:.2f} or unaligned-src>={args.min_unaligned_src}")
    if not args.dry_run:
        print(f"  Mode:            {args.batch_mode}")

    # Build forced-verse set from --verse-list, --verse-list-file, or --retry-failed
    forced_verse_set: frozenset[str] | None = None
    verse_list_arg: str | None = getattr(args, "verse_list", None)
    verse_list_file: Path | None = getattr(args, "verse_list_file", None)
    retry_failed: bool = getattr(args, "retry_failed", False)
    if verse_list_arg:
        forced_verse_set = frozenset(v.strip() for v in verse_list_arg.split(",") if v.strip())
        print(f"  Force-retry list: {len(forced_verse_set)} verse(s) (--verse-list)")
    elif verse_list_file:
        lines = verse_list_file.read_text().splitlines()
        forced_verse_set = frozenset(
            ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")
        )
        print(f"  Force-retry list: {len(forced_verse_set)} verse(s) from {verse_list_file}")

    # Discover and filter chapter files
    chapter_files = discover_chapter_files(args.alignment_dir)
    chapter_files = _filter_chapter_files(chapter_files, args, forced_verse_set)
    if not chapter_files:
        raise SystemExit("No chapter JSON files found in --alignment-dir.")
    print(f"  Evaluating {len(chapter_files)} chapter file(s) ...")

    # Load source and target tokens (needed for clean pass and scoring)
    print(f"  Loading source tokens ({corpus_id}) ...")
    source_verses = load_source_verses(args.sources_dir, args.corpus)
    print(f"  Loading target tokens ({args.target_edition}) ...")
    target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)

    print("  Cleaning alignment files ...")
    files_changed, dropped, repaired = run_clean_pass(chapter_files, source_verses, target_verses)
    if files_changed:
        print(
            f"  Cleaned {files_changed} file(s): "
            f"{dropped} record(s) dropped, {repaired} record(s) repaired."
        )

    if retry_failed:
        forced_verse_set = _collect_failed_verses(chapter_files, source_verses)
        print(f"  Retry-failed mode: {len(forced_verse_set)} verse(s) with no records — skipping scoring")
        if not forced_verse_set:
            print("  No failed verses found — nothing to retry.")
            return

    retry_specs_by_chapter: dict[str, list[VerseRetrySpec]] = {}
    chapter_paths: dict[str, Path] = {}

    if forced_verse_set:
        # Exclusive mode: skip scoring and retry exactly the listed verses.
        chapter_file_by_id = {_chapter_id_from_path(cf): cf for cf in chapter_files}
        for vid in sorted(forced_verse_set):
            cid = vid[:5]
            if cid in chapter_file_by_id:
                retry_specs_by_chapter.setdefault(cid, []).append(
                    VerseRetrySpec(verse_id=vid, chapter_id=cid, uncovered_src_ids=[], uncovered_count=0)
                )
                chapter_paths[cid] = chapter_file_by_id[cid]
            else:
                print(f"  Warning: no chapter file for verse {vid} (chapter {cid}) — skipped")
        total_flagged = sum(len(s) for s in retry_specs_by_chapter.values())
        print(f"  Exclusive verse-list mode: {total_flagged} verse(s) — skipping scoring")
        used_fallback = False
    else:
        scoring_config = ScoringConfig(
            retry_threshold=args.score_retry_threshold,
            semantic_model=args.semantic_model,
            semantic_threshold=args.semantic_threshold,
        )

        # Verse-level force-include: these verses are retried regardless of score.
        forced_verse: str | None = getattr(args, "verse", None)
        forced_verse_range: list[str] | None = getattr(args, "verse_range", None)

        def _is_forced(vid: str) -> bool:
            if forced_verse:
                return vid == forced_verse
            if forced_verse_range:
                return forced_verse_range[0] <= vid <= forced_verse_range[1]
            return False

        total_verse_count = 0

        for cf in chapter_files:
            chapter_id = _chapter_id_from_path(cf)
            verse_scores = score_chapter_file(
                cf, source_verses, args.target_language, scoring_config,
                target_verses=target_verses,
            )
            total_verse_count += len(verse_scores)
            coverage_flagged = {
                spec.verse_id
                for spec in find_low_coverage_verses(cf, source_verses, args.min_unaligned_src,
                                                      target_verses=target_verses)
            }
            specs = [
                VerseRetrySpec(
                    verse_id=vs.verse_id,
                    chapter_id=chapter_id,
                    uncovered_src_ids=[],
                    uncovered_count=0,
                )
                for vs in verse_scores
                if vs.needs_retry or vs.verse_id in coverage_flagged or _is_forced(vs.verse_id)
            ]
            if specs:
                retry_specs_by_chapter[chapter_id] = specs
                chapter_paths[chapter_id] = cf

        total_flagged = sum(len(s) for s in retry_specs_by_chapter.values())

        # Fallback to refine model when flagged rate is high enough that targeted
        # retry with the expensive model is not warranted.
        flagged_rate = total_flagged / total_verse_count if total_verse_count else 0.0
        retry_differs = (
            args.llm_model != args._refine_llm_model
            or args.llm_provider != args._refine_llm_provider
        )
        used_fallback = False
        if retry_differs and flagged_rate >= args.fallback_threshold:
            args.llm_provider      = args._refine_llm_provider
            args.llm_model         = args._refine_llm_model
            args.reasoning_effort  = args._refine_reasoning_effort
            args.max_output_tokens = args._refine_max_output_tokens
            used_fallback = True
            print(
                f"\n  Flagged rate {flagged_rate:.1%} >= {args.fallback_threshold:.0%} — "
                f"falling back to refine model"
            )

    if not retry_specs_by_chapter:
        print("\n  No verses flagged — nothing to retry.")
        return

    print(
        f"  Using: {args.llm_provider} / {args.llm_model}"
        f"{_effort_str(args.reasoning_effort)}"
    )

    print(f"\n  {total_flagged} verse(s) flagged across {len(retry_specs_by_chapter)} chapter(s):")
    for chapter_id in sorted(retry_specs_by_chapter):
        for spec in retry_specs_by_chapter[chapter_id]:
            print(f"    {spec.verse_id}")

    if args.dry_run:
        return

    llm_client = LLMClient(
        provider=args.llm_provider,
        model=args.llm_model,
        reasoning_effort=args.reasoning_effort,
        max_api_retries=args.max_api_retries,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )

    if args.batch_mode == "async":
        _run_async(
            args, corpus_id, source_verses, target_verses,
            retry_specs_by_chapter, llm_client,
        )
    else:
        _run_sync(
            args, corpus_id, source_verses, target_verses,
            retry_specs_by_chapter, chapter_paths, llm_client,
        )

    _write_retry_sidecars(retry_specs_by_chapter, chapter_paths, args.target_edition)

    if args.llm_provider == "openrouter" and llm_client.session_cost:
        print(f"\nOpenRouter session cost: ${llm_client.session_cost:.4f}")
    elapsed = time.time() - _start
    print(f"  Elapsed:   {elapsed // 3600:.0f}h {elapsed % 3600 // 60:.0f}m {elapsed % 60:.0f}s")

    if used_fallback:
        sys.exit(2)


def _run_sync(
    args: argparse.Namespace,
    corpus_id: str,
    source_verses: dict,
    target_verses: dict,
    retry_specs_by_chapter: dict[str, list[VerseRetrySpec]],
    chapter_paths: dict[str, Path],
    llm_client: LLMClient,
) -> None:
    total_replaced = 0
    total_errors: list[str] = []

    for chapter_id in sorted(retry_specs_by_chapter):
        specs = retry_specs_by_chapter[chapter_id]
        chapter_path = chapter_paths[chapter_id]
        print(f"\n  Chapter {chapter_id}: retrying {len(specs)} verse(s) ...")

        n_replaced, errors = retry_chapter_sync(
            chapter_json_path=chapter_path,
            retry_specs=specs,
            source_verses=source_verses,
            target_verses=target_verses,
            target_language=args.target_language,
            llm_client=llm_client,
            batch_size=args.batch_size,
            max_retries=args.max_retries,
            corpus_id=corpus_id,
            target_edition=args.target_edition,
            creator=args.creator,
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
            reasoning_effort=args.reasoning_effort,
        )
        print(f"  → {chapter_path.name}: {n_replaced} verse(s) replaced")

        if errors:
            print(f"    {len(errors)} validation error(s):")
            for err in errors[:5]:
                print(f"      {err}")
            if len(errors) > 5:
                print(f"      ... and {len(errors) - 5} more")

        total_replaced += n_replaced
        total_errors.extend(errors)

    print(
        f"\n  Total: {total_replaced} verse(s) replaced "
        f"across {len(retry_specs_by_chapter)} chapter(s)"
    )
    if total_errors:
        print(f"  {len(total_errors)} total validation error(s)")


def _run_async(
    args: argparse.Namespace,
    corpus_id: str,
    source_verses: dict,
    target_verses: dict,
    retry_specs_by_chapter: dict[str, list[VerseRetrySpec]],
    llm_client: LLMClient,
) -> None:
    from .async_batch import submit_batch_job

    chapter_batches = build_retry_chapter_batches(
        retry_specs_by_chapter=retry_specs_by_chapter,
        source_verses=source_verses,
        target_verses=target_verses,
        target_language=args.target_language,
        batch_size=args.batch_size,
        corpus_id=corpus_id,
    )

    print(f"\n  Submitting {len(chapter_batches)} request(s) to {args.llm_provider} batch API ...")

    job_metadata_base = {
        "job_type": "retry",
        "target_edition": args.target_edition,
        "target_language": args.target_language,
        "corpus": args.corpus,
        "corpus_id": corpus_id,
        "output_dir": str(args.alignment_dir),
        "creator": args.creator,
        "sources_dir": str(args.sources_dir),
        "target_tsv_dir": str(args.target_tsv_dir),
    }

    job_id, meta_path = submit_batch_job(
        provider=args.llm_provider,
        model=args.llm_model,
        reasoning_effort=args.reasoning_effort,
        chapter_batches=chapter_batches,
        jobs_dir=args.jobs_dir,
        job_metadata_base=job_metadata_base,
        temperature=llm_client.temperature,
        max_output_tokens=llm_client.max_output_tokens,
    )

    print(f"  Submitted: {job_id}")
    print(f"  Job metadata: {meta_path}")
    from .fetch_batch import fetch_wait
    fetch_wait(meta_path)


if __name__ == "__main__":
    main()
