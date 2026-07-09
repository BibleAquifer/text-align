"""refine-alignment: LLM-assisted Stage 2 alignment refinement.

Takes automated alignment candidates (ACAI, SIM-MIGRATED, DIFF-MIGRATED) for a
target edition, presents each verse to an LLM with source and target tokens, and
produces a refined alignment JSON applying alignment-principles guidelines.

Output is one JSON file per chapter: {corpus_id}-{edition}-{BB}-{CCC}-manual.json

CLI entry point: refine-alignment
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

from biblelib.word import BCVWPID

from text_align import ROOT
from text_align.config import load_config_from_args, require
from text_align.migrate.alignment_io import load_alignment_json, write_alignment_json
from text_align.migrate.tsv import process_usfm_tsv

from .llm import LLMClient
from .prompt import build_batch_message, build_system_prompt, detect_phenomena, infer_testament
from .source import collect_source_verse_range, load_source_verses
from .util import _CORPUS_ID


ALIGNMENT_SOURCE_TYPES = ["ACAI", "SIM-MIGRATED", "DIFF-MIGRATED", "MERGED", "FASTALIGN", "REVISED"]

# Diagnostic threshold for all-secondary sanitization.
# Warn if sanitized records are >= this fraction of total AND >= the minimum count.
_SANITIZE_WARN_PCT = 0.02   # 2%
_SANITIZE_WARN_MIN = 5      # absolute floor to suppress noise on small runs

_SOURCES_DIR = ROOT / "data" / "sources"
_JOBS_DIR = ROOT / "jobs"


# ---------------------------------------------------------------------------
# Candidate loading
# ---------------------------------------------------------------------------

def load_candidate_records(path: Path) -> dict[str, list[dict]]:
    """Load an alignment JSON and return records grouped by verse BCV ID.

    Handles both flat (``alignment["records"]``) and SB 0.4 grouped
    (``alignment["groups"][*]["records"]``) formats transparently.
    """
    data = load_alignment_json(path)
    if "records" in data:
        raw_records = data["records"]
    elif "groups" in data:
        raw_records = []
        for group in data.get("groups", []):
            raw_records.extend(group.get("records", []))
    else:
        return {}

    verses: dict[str, list[dict]] = {}
    for rec in raw_records:
        src_ids = rec.get("source") or []
        if not src_ids:
            continue
        verse_id = BCVWPID(src_ids[0]).to_bcvid
        verses.setdefault(verse_id, []).append({
            "source": src_ids,
            "target": rec.get("target") or [],
        })
    return verses


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------

def build_output_alignment(
    records: list[dict],
    corpus: str,
    edition: str,
    creator: str,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    reasoning_effort: str | None = None,
    prior_llm: dict | None = None,
) -> dict[str, Any]:
    """Build an SB 0.4 groups alignment structure from LLM-refined records.

    NEQ records (``meta.rel == "NEQ"``) are separated from regular records and
    their token IDs are written into ``meta.nonEquivalent`` at the group level.
    The output file contains no ``meta.rel`` fields.

    When ``prior_llm`` is supplied (retry pass), it is stored as ``"llm"`` (the
    original refine-pass model) and the new model info goes in ``"retry_llm"``.
    """
    neq_source: list[str] = []
    neq_target: list[str] = []
    regular: list[dict] = []

    for rec in records:
        meta = rec.get("meta") or {}
        if meta.get("rel") == "NEQ":
            neq_source.extend(rec.get("source") or [])
            neq_target.extend(rec.get("target") or [])
        else:
            clean_meta: dict = {}
            secondary = meta.get("secondary") or {}
            sec_src = secondary.get("source") or []
            sec_tgt = secondary.get("target") or []
            if sec_src or sec_tgt:
                clean_meta["secondary"] = {}
                if sec_src:
                    clean_meta["secondary"]["source"] = sec_src
                if sec_tgt:
                    clean_meta["secondary"]["target"] = sec_tgt
            if meta.get("is_idiom"):
                clean_meta["is_idiom"] = True

            out_rec: dict = {
                "source": rec.get("source") or [],
                "target": rec.get("target") or [],
            }
            if clean_meta:
                out_rec["meta"] = clean_meta
            regular.append(out_rec)

    group_meta: dict = {"creator": creator, "conformsTo": "0.4"}
    if llm_provider or llm_model:
        model_info: dict = {}
        if llm_provider:
            model_info["provider"] = llm_provider
        if llm_model:
            model_info["model"] = llm_model
        if reasoning_effort:
            model_info["reasoning_effort"] = reasoning_effort
        if prior_llm:
            group_meta["llm"] = prior_llm
            group_meta["retry_llm"] = model_info
        else:
            group_meta["llm"] = model_info
    elif prior_llm:
        group_meta["llm"] = prior_llm
    if neq_source or neq_target:
        non_equiv: dict = {}
        if neq_source:
            non_equiv["source"] = neq_source
        if neq_target:
            non_equiv["target"] = neq_target
        group_meta["nonEquivalent"] = non_equiv

    return {
        "format": "alignment",
        "version": "0.4",
        "groups": [{
            "type": "translation",
            "meta": group_meta,
            "documents": [
                {"scheme": "BCVWP", "docid": corpus},
                {"scheme": "BCVWP", "docid": edition},
            ],
            "roles": ["source", "target"],
            "records": regular,
        }],
    }


def _write_chapter_file(
    chapter_id: str,
    records: list[dict],
    corpus_id: str,
    target_edition: str,
    output_dir: Path,
    creator: str,
    llm_provider: str | None,
    llm_model: str | None,
    reasoning_effort: str | None,
) -> Path:
    """Write one chapter's records to a chapter-based JSON file.

    Returns the output path.
    """
    book_id = chapter_id[:2]
    chap_num = chapter_id[2:]
    out_path = output_dir / f"{corpus_id}-{target_edition}-{book_id}-{chap_num}-manual.json"

    output = build_output_alignment(
        records, corpus_id, target_edition, creator,
        llm_provider=llm_provider, llm_model=llm_model, reasoning_effort=reasoning_effort,
    )
    write_alignment_json(output, out_path)
    return out_path


# ---------------------------------------------------------------------------
# Range filtering
# ---------------------------------------------------------------------------

def _filter_verse_ids(verse_ids: list[str], args: argparse.Namespace) -> list[str]:
    """Return the subset of verse_ids matching the active range filter on args.

    Checks (in order): --verse, --verse-range, --book, --book-range,
    --chapter, --chapter-range.  When no filter is active, returns verse_ids
    unchanged.
    """
    if getattr(args, "verse", None):
        vid = args.verse
        result = [vid] if vid in set(verse_ids) else []
        if not result:
            print(f"Verse {vid} not found in verse set — skipping.")
        return result

    if getattr(args, "verse_range", None):
        start, end = args.verse_range
        return [v for v in verse_ids if start <= v <= end]

    if getattr(args, "book", None):
        book = str(args.book).zfill(2)
        return [v for v in verse_ids if v[:2] == book]

    if getattr(args, "book_range", None):
        start = str(args.book_range[0]).zfill(2)
        end = str(args.book_range[1]).zfill(2)
        return [v for v in verse_ids if start <= v[:2] <= end]

    if getattr(args, "chapter", None):
        chap = str(args.chapter).zfill(5)
        return [v for v in verse_ids if v[:5] == chap]

    if getattr(args, "chapter_range", None):
        start = str(args.chapter_range[0]).zfill(5)
        end = str(args.chapter_range[1]).zfill(5)
        return [v for v in verse_ids if start <= v[:5] <= end]

    return verse_ids


# ---------------------------------------------------------------------------
# Per-corpus processing
# ---------------------------------------------------------------------------

def process_corpus(
    corpus: str,
    target_edition: str,
    target_language: str,
    target_tsv_dir: Path,
    exp_dir: Path,
    output_dir: Path,
    sources_dir: Path,
    alignment_sources: list[str],
    llm_client: LLMClient,
    batch_size: int,
    max_retries: int,
    creator: str,
    args: argparse.Namespace | None = None,
    from_scratch: bool = False,
    batch_mode: str = "sync",
    jobs_dir: Path = _JOBS_DIR,
    skip_existing: bool = False,
) -> None:
    """Process one corpus (``"nt"`` or ``"ot"``) and write chapter-based output JSON files."""
    corpus_id = _CORPUS_ID[corpus]
    print(f"\n--- {corpus.upper()} ({corpus_id}) ---")

    print(f"Loading source tokens ({corpus_id}) ...")
    source_verses = load_source_verses(sources_dir, corpus)

    print(f"Loading target tokens ({target_edition}) ...")
    target_verses = process_usfm_tsv(target_tsv_dir, target_edition)

    # Load candidate alignments for each requested source type
    candidates_by_type: dict[str, dict[str, list[dict]]] = {}
    if not from_scratch:
        for src_type in alignment_sources:
            path = exp_dir / src_type / f"{corpus_id}-{target_edition}-manual.json"
            if path.exists():
                print(f"Loading candidates: {path.name}")
                candidates_by_type[src_type] = load_candidate_records(path)
            else:
                print(f"Candidate file not found, skipping: {path}")

        if not candidates_by_type:
            print("No candidate files found — aligning from scratch.")

    # Universe of verse IDs.  With candidates: intersection of candidate verses and
    # source tokens.  Without: every source verse that also has target tokens.
    if candidates_by_type:
        candidate_ids: set[str] = set()
        for recs in candidates_by_type.values():
            candidate_ids.update(recs.keys())
        verse_ids = sorted(candidate_ids & set(source_verses.keys()))
    else:
        # Key by target (BSB) verse ID; resolve each to its source verse via the
        # source_verse field in the target tokens, which handles versification
        # differences (e.g. Jonah: Hebrew 2:1 = English 1:17).
        verse_ids = sorted(
            vid for vid, tv in target_verses.items()
            if tv.words and next(iter(tv.words.values())).source_verse in source_verses
        )

    # Apply range filter
    if args is not None:
        verse_ids = _filter_verse_ids(verse_ids, args)

    if not verse_ids:
        print("No verses to process — skipping.")
        return

    # Group verse IDs by chapter (vid[:5] = BBCCC)
    chapters: dict[str, list[str]] = {}
    for vid in verse_ids:
        chapters.setdefault(vid[:5], []).append(vid)

    total_verses = len(verse_ids)
    total_chapters = len(chapters)
    print(f"Processing {total_verses} verses across {total_chapters} chapter(s) ...")

    output_dir.mkdir(parents=True, exist_ok=True)

    if batch_mode == "async":
        _process_corpus_async(
            chapters=chapters,
            source_verses=source_verses,
            target_verses=target_verses,
            candidates_by_type=candidates_by_type,
            corpus_id=corpus_id,
            target_edition=target_edition,
            target_language=target_language,
            target_tsv_dir=target_tsv_dir,
            output_dir=output_dir,
            sources_dir=sources_dir,
            corpus=corpus,
            llm_client=llm_client,
            batch_size=batch_size,
            creator=creator,
            jobs_dir=jobs_dir,
            skip_existing=skip_existing,
        )
    else:
        _process_corpus_sync(
            chapters=chapters,
            source_verses=source_verses,
            target_verses=target_verses,
            candidates_by_type=candidates_by_type,
            corpus_id=corpus_id,
            target_edition=target_edition,
            target_language=target_language,
            output_dir=output_dir,
            llm_client=llm_client,
            batch_size=batch_size,
            max_retries=max_retries,
            creator=creator,
            skip_existing=skip_existing,
        )


def _process_corpus_sync(
    chapters: dict[str, list[str]],
    source_verses: dict,
    target_verses: dict,
    candidates_by_type: dict[str, dict[str, list[dict]]],
    corpus_id: str,
    target_edition: str,
    target_language: str,
    output_dir: Path,
    llm_client: LLMClient,
    batch_size: int,
    max_retries: int,
    creator: str,
    skip_existing: bool = False,
) -> None:
    """Synchronous path: call LLM per batch, write one file per chapter."""
    all_san_details_total: list[str] = []
    all_errors_total: list[str] = []
    total_records = 0

    for chapter_id, chapter_verse_ids in chapters.items():
        if skip_existing:
            out_path = output_dir / f"{corpus_id}-{target_edition}-{chapter_id[:2]}-{chapter_id[2:]}-manual.json"
            if out_path.exists():
                print(f"  Chapter {chapter_id}: skipping (output exists)")
                continue
        chapter_records: list[dict] = []
        chapter_errors: list[str] = []
        chapter_san: list[str] = []

        total_batches = (len(chapter_verse_ids) + batch_size - 1) // batch_size
        missed: dict[str, list[str]] = {}

        for batch_num, batch_start in enumerate(range(0, len(chapter_verse_ids), batch_size), 1):
            batch_ids = chapter_verse_ids[batch_start:batch_start + batch_size]

            verse_batch = []
            verse_source_ids: dict[str, set[str]] = {}
            verse_target_ids: dict[str, set[str]] = {}

            for verse_id in batch_ids:
                tgt_verse = target_verses.get(verse_id)
                tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
                if tgt_verse and tgt_verse.words:
                    src_start = next(iter(tgt_verse.words.values())).source_verse
                    src_end = tgt_verse.source_verse_range_end
                    if src_end and src_end > src_start:
                        src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                    else:
                        src_tokens = source_verses.get(src_start, [])
                else:
                    src_tokens = []

                cands = {
                    src_type: recs[verse_id]
                    for src_type, recs in candidates_by_type.items()
                    if verse_id in recs
                }
                verse_source_ids[verse_id] = {t.id for t in src_tokens}
                verse_target_ids[verse_id] = {t.id for t in tgt_tokens}
                verse_batch.append((verse_id, src_tokens, tgt_tokens, cands))

            all_src = [t for _, src, _, _ in verse_batch for t in src]
            testament = infer_testament(all_src)
            phenomena = detect_phenomena(all_src)
            system_msg = build_system_prompt(phenomena, target_language, testament=testament)
            user_msg, batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)

            print(
                f"  Chapter {chapter_id} batch {batch_num}/{total_batches}: "
                f"calling LLM ({len(batch_ids)} verses) ...", flush=True,
            )
            try:
                results, errors, san_details = llm_client.call_batch(
                    system_prompt=system_msg,
                    user_message=user_msg,
                    verse_source_ids=verse_source_ids,
                    verse_target_ids=verse_target_ids,
                    verse_token_maps=batch_maps,
                    max_retries=max_retries,
                )
            except RuntimeError as exc:
                verse_list = ", ".join(batch_ids)
                print(
                    f"  Chapter {chapter_id} batch {batch_num}/{total_batches}: "
                    f"all retries exhausted ({exc}) — missed: {verse_list}"
                )
                results, errors, san_details = {}, [], []
                for vid in batch_ids:
                    missed.setdefault(vid, []).append(f"API error: {exc}")

            for vid in batch_ids:
                if vid not in results and vid not in missed:
                    reason = next(
                        (e for e in errors if "no tool call" in e or "no records" in e),
                        errors[0] if errors else "no records returned",
                    )
                    missed.setdefault(vid, []).append(reason)

            n_records = sum(len(r) for r in results.values())
            status = f"{len(results)}/{len(batch_ids)} verses, {n_records} records"
            if errors:
                status += f", {len(errors)} error(s)"
            print(f"  Chapter {chapter_id} batch {batch_num}/{total_batches}: {status}")

            for recs in results.values():
                chapter_records.extend(recs)
            chapter_errors.extend(errors)
            chapter_san.extend(san_details)

        if missed:
            print(f"  Chapter {chapter_id}: resubmitting {len(missed)} verse(s) individually ...")
            for verse_id in list(missed.keys()):
                tgt_verse = target_verses.get(verse_id)
                tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
                if tgt_verse and tgt_verse.words:
                    src_start = next(iter(tgt_verse.words.values())).source_verse
                    src_end = tgt_verse.source_verse_range_end
                    if src_end and src_end > src_start:
                        src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                    else:
                        src_tokens = source_verses.get(src_start, [])
                else:
                    src_tokens = []
                cands = {
                    src_type: recs[verse_id]
                    for src_type, recs in candidates_by_type.items()
                    if verse_id in recs
                }
                verse_batch = [(verse_id, src_tokens, tgt_tokens, cands)]
                all_src = [t for _, src, _, _ in verse_batch for t in src]
                testament = infer_testament(all_src)
                phenomena = detect_phenomena(all_src)
                system_msg = build_system_prompt(phenomena, target_language, testament=testament)
                user_msg, batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)
                try:
                    r_results, r_errors, r_san = llm_client.call_batch(
                        system_prompt=system_msg,
                        user_message=user_msg,
                        verse_source_ids={verse_id: {t.id for t in src_tokens}},
                        verse_target_ids={verse_id: {t.id for t in tgt_tokens}},
                        verse_token_maps=batch_maps,
                        max_retries=max_retries,
                    )
                except RuntimeError as exc:
                    missed[verse_id].append(f"individual retry: API error: {exc}")
                    print(
                        f"  Chapter {chapter_id} resubmit {verse_id}: "
                        f"all retries exhausted — {exc}"
                    )
                    continue
                if verse_id not in r_results:
                    reason = next(
                        (e for e in r_errors if "no tool call" in e or "no records" in e),
                        r_errors[0] if r_errors else "no records returned",
                    )
                    missed[verse_id].append(f"individual retry: {reason}")
                    n_r = 0
                    status = "0/1 verses, 0 records"
                    if r_errors:
                        status += f", {len(r_errors)} error(s)"
                    print(f"  Chapter {chapter_id} resubmit {verse_id}: {status}")
                    chapter_errors.extend(r_errors)
                    continue
                del missed[verse_id]
                n_r = sum(len(v) for v in r_results.values())
                status = f"{len(r_results)}/1 verses, {n_r} records"
                if r_errors:
                    status += f", {len(r_errors)} error(s)"
                print(f"  Chapter {chapter_id} resubmit {verse_id}: {status}")
                for recs in r_results.values():
                    chapter_records.extend(recs)
                chapter_errors.extend(r_errors)
                chapter_san.extend(r_san)
            if missed:
                print(f"  Chapter {chapter_id}: {len(missed)} verse(s) permanently unresolved:")
                for vid, reasons in missed.items():
                    print(f"    {vid}: {' → '.join(reasons)}")

        out_path = _write_chapter_file(
            chapter_id, chapter_records, corpus_id, target_edition, output_dir,
            creator, llm_client.provider, llm_client.model, llm_client.reasoning_effort,
        )
        n_neq = sum(1 for r in chapter_records if (r.get("meta") or {}).get("rel") == "NEQ")
        print(
            f"  → {out_path.name}  "
            f"({len(chapter_records)} records, {n_neq} NEQ)"
        )

        total_records += len(chapter_records)
        all_errors_total.extend(chapter_errors)
        all_san_details_total.extend(chapter_san)

    # Summary
    print(f"\n  Total: {total_records} records across {len(chapters)} chapter(s)")

    n_sanitized = len(all_san_details_total)
    if n_sanitized:
        san_pct = n_sanitized / total_records * 100 if total_records else 0
        san_msg = f"  {n_sanitized} record(s) sanitized — {san_pct:.1f}% of records"
        if n_sanitized >= _SANITIZE_WARN_MIN and san_pct >= _SANITIZE_WARN_PCT * 100:
            print(f"  !! PROMPT REVIEW SUGGESTED: {san_msg.strip()}")
            for detail in all_san_details_total:
                print(f"       {detail}")
        else:
            print(san_msg)

    if all_errors_total:
        print(f"  {len(all_errors_total)} unresolved validation error(s):")
        for err in all_errors_total[:10]:
            print(f"    {err}")
        if len(all_errors_total) > 10:
            print(f"    ... and {len(all_errors_total) - 10} more")


def _process_corpus_async(
    chapters: dict[str, list[str]],
    source_verses: dict,
    target_verses: dict,
    candidates_by_type: dict[str, dict[str, list[dict]]],
    corpus_id: str,
    target_edition: str,
    target_language: str,
    target_tsv_dir: Path,
    output_dir: Path,
    sources_dir: Path,
    corpus: str,
    llm_client: LLMClient,
    batch_size: int,
    creator: str,
    jobs_dir: Path,
    skip_existing: bool = False,
) -> None:
    """Async path: build all request payloads and submit to provider batch API."""
    from .async_batch import submit_batch_job

    chapter_batches: list[dict] = []

    for chapter_id, chapter_verse_ids in chapters.items():
        if skip_existing:
            out_path = output_dir / f"{corpus_id}-{target_edition}-{chapter_id[:2]}-{chapter_id[2:]}-manual.json"
            if out_path.exists():
                print(f"  Chapter {chapter_id}: skipping (output exists)")
                continue
        for batch_index, batch_start in enumerate(range(0, len(chapter_verse_ids), batch_size)):
            batch_ids = chapter_verse_ids[batch_start:batch_start + batch_size]

            verse_batch = []
            for verse_id in batch_ids:
                tgt_verse = target_verses.get(verse_id)
                tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
                if tgt_verse and tgt_verse.words:
                    src_start = next(iter(tgt_verse.words.values())).source_verse
                    src_end = tgt_verse.source_verse_range_end
                    if src_end and src_end > src_start:
                        src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                    else:
                        src_tokens = source_verses.get(src_start, [])
                else:
                    src_tokens = []
                cands = {
                    src_type: recs[verse_id]
                    for src_type, recs in candidates_by_type.items()
                    if verse_id in recs
                }
                verse_batch.append((verse_id, src_tokens, tgt_tokens, cands))

            all_src = [t for _, src, _, _ in verse_batch for t in src]
            testament = infer_testament(all_src)
            phenomena = detect_phenomena(all_src)
            system_msg = build_system_prompt(phenomena, target_language, testament=testament)
            user_msg, _batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)

            chapter_batches.append({
                "chapter_id": chapter_id,
                "batch_index": batch_index,
                "verse_ids": batch_ids,
                "system_prompt": system_msg,
                "user_message": user_msg,
            })

    print(f"  Submitting {len(chapter_batches)} request(s) to {llm_client.provider} batch API ...")

    job_metadata_base = {
        "target_edition": target_edition,
        "target_language": target_language,
        "corpus": corpus,
        "corpus_id": corpus_id,
        "output_dir": str(output_dir),
        "creator": creator,
        "sources_dir": str(sources_dir),
        "target_tsv_dir": str(target_tsv_dir),
    }

    job_id, meta_path = submit_batch_job(
        provider=llm_client.provider,
        model=llm_client.model,
        reasoning_effort=llm_client.reasoning_effort,
        chapter_batches=chapter_batches,
        jobs_dir=jobs_dir,
        job_metadata_base=job_metadata_base,
        temperature=llm_client.temperature,
        max_output_tokens=llm_client.max_output_tokens,
    )

    print(f"  Submitted: {job_id}")
    print(f"  Job metadata: {meta_path}")
    from .fetch_batch import fetch_wait
    fetch_wait(meta_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    # Pre-parse --output-suffix so load_config_from_args can derive output_dir
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--output-suffix", default="LLM-REFINED")
    pre_args, _ = pre.parse_known_args()

    config_defaults = load_config_from_args(output_suffix=pre_args.output_suffix)

    p = argparse.ArgumentParser(
        description=(
            "Refine alignment candidates with an LLM, applying alignment-principles "
            "guidelines (primary/secondary, idiom flags, NEQ). "
            "Writes one JSON file per chapter."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code, e.g. eng")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID, e.g. NIV11")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<edition>.tsv and nt_<edition>.tsv")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory to write refined alignment JSON files")
    p.add_argument("--output-suffix", default="LLM-REFINED",
                   help="Output subdirectory name under exp/ (default: LLM-REFINED)")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help="Directory containing SBLGNT.tsv and WLCM.tsv "
                        f"(default: {_SOURCES_DIR})")
    p.add_argument("--alignment-sources", default=None, nargs="+",
                   choices=ALIGNMENT_SOURCE_TYPES,
                   help=f"Candidate types to load (default: all — "
                        f"{', '.join(ALIGNMENT_SOURCE_TYPES)})")
    p.add_argument("--corpora", "--corpus", default=["ot", "nt"], nargs="+", choices=["ot", "nt"],
                   help="Corpora to process (default: ot nt)")
    p.add_argument("--llm-provider", default="openai",
                   choices=["openai", "anthropic", "google", "openrouter", "gloo", "ollama"],
                   help="LLM provider (default: openai)")
    p.add_argument("--llm-model", default="gpt-5.4-mini",
                   help="Model name for the chosen provider (default: gpt-5.4-mini)")
    p.add_argument("--reasoning-effort", default=None,
                   choices=["none", "minimal", "low", "medium", "high"],
                   help="OpenAI reasoning_effort (default: model default; "
                        "none/minimal for speed, high for quality)")
    p.add_argument("--batch-size", type=int, default=5,
                   help="Verses per LLM call (default: 5)")
    p.add_argument("--max-retries", type=int, default=2,
                   help="Retry attempts on validation failure (default: 2)")
    p.add_argument("--max-api-retries", type=int, default=4,
                   help="Retry attempts on transient API errors (429/503) with "
                        "exponential backoff — 2s, 4s, 8s, … (default: 4)")
    p.add_argument("--temperature", type=float, default=1,
                   help="Sampling temperature sent explicitly to the provider "
                        "(default: 1).  Fixing this value ensures sync and async "
                        "batch runs use identical generation parameters.  "
                        "Not applied to OpenAI reasoning models.")
    p.add_argument("--max-output-tokens", type=int, default=4000,
                   help="Hard cap on response tokens (default: 32000).  Matches "
                        "the Anthropic budget and gives thinking models headroom "
                        "before the tool call output.  Explicit matching prevents "
                        "silent truncation differences between sync and async batch runs.")
    p.add_argument("--creator", default="text-align",
                   help="Creator string for alignment meta (default: text-align)")
    p.add_argument("--from-scratch", action="store_true", default=False,
                   help="Skip candidate loading and align entirely from source/target tokens")
    p.add_argument("--skip-existing", action="store_true", default=False,
                   help="Skip chapters whose output file already exists. "
                        "Pass in GHA so re-triggered jobs don't redo completed chapters.")
    p.add_argument("--batch-mode", choices=["sync", "async"], default="sync",
                   help="sync: call LLM and write results immediately (default); "
                        "async: submit to provider batch API, then block until "
                        "results are ready and write chapter files (same output as sync)")
    p.add_argument("--jobs-dir", default=_JOBS_DIR, type=Path,
                   help=f"Directory for async batch job metadata (default: {_JOBS_DIR})")

    # Range filtering — all mutually exclusive
    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--verse", default=None, metavar="BCV",
                             help="Process a single verse BCV for testing, e.g. 41004003")
    range_group.add_argument("--verse-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Process a BCV range, e.g. --verse-range 41004001 41004020")
    range_group.add_argument("--book", default=None, metavar="BB",
                             help="Process a single book, e.g. --book 41 (Mark)")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Process a range of books, e.g. --book-range 41 44")
    range_group.add_argument("--chapter", default=None, metavar="BBCCC",
                             help="Process a single chapter, e.g. --chapter 41003 (Mark 3)")
    range_group.add_argument("--chapter-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Process a range of chapters, e.g. --chapter-range 41001 41016")

    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "target_language", "target_edition", "target_tsv_dir", "output_dir")

    if args.alignment_sources is None:
        args.alignment_sources = ALIGNMENT_SOURCE_TYPES

    return args


def main() -> None:
    args = parse_args()
    _start = time.time()

    # output_dir = exp_dir / output_suffix; recover exp_dir for candidate lookup
    exp_dir = args.output_dir.parent

    print(f"refine-alignment: {args.target_edition} ({args.target_language})")
    effort_str = f" (reasoning_effort={args.reasoning_effort})" if args.reasoning_effort else ""
    print(f"  Provider:  {args.llm_provider} / {args.llm_model}{effort_str}")
    if args.from_scratch:
        print(f"  Sources:   (from scratch — no candidates)")
    else:
        print(f"  Sources:   {', '.join(args.alignment_sources)}")
    if args.skip_existing:
        print(f"  Skip existing: yes")
    print(f"  Output:    {args.output_dir}")
    print(f"  Mode:      {args.batch_mode}")

    # Print active range filter
    if args.verse:
        print(f"  Filter:    verse {args.verse}")
    elif args.verse_range:
        print(f"  Filter:    verse range {args.verse_range[0]}–{args.verse_range[1]}")
    elif args.book:
        print(f"  Filter:    book {args.book}")
    elif args.book_range:
        print(f"  Filter:    book range {args.book_range[0]}–{args.book_range[1]}")
    elif args.chapter:
        print(f"  Filter:    chapter {args.chapter}")
    elif args.chapter_range:
        print(f"  Filter:    chapter range {args.chapter_range[0]}–{args.chapter_range[1]}")

    llm_client = LLMClient(
        provider=args.llm_provider,
        model=args.llm_model,
        reasoning_effort=args.reasoning_effort,
        max_api_retries=args.max_api_retries,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )

    for corpus in args.corpora:
        process_corpus(
            corpus=corpus,
            target_edition=args.target_edition,
            target_language=args.target_language,
            target_tsv_dir=args.target_tsv_dir,
            exp_dir=exp_dir,
            output_dir=args.output_dir,
            sources_dir=args.sources_dir,
            alignment_sources=args.alignment_sources,
            llm_client=llm_client,
            batch_size=args.batch_size,
            max_retries=args.max_retries,
            creator=args.creator,
            args=args,
            from_scratch=args.from_scratch,
            batch_mode=args.batch_mode,
            jobs_dir=args.jobs_dir,
            skip_existing=args.skip_existing,
        )

    if args.llm_provider == "openrouter" and llm_client.session_cost:
        print(f"\nOpenRouter session cost: ${llm_client.session_cost:.4f}")
    elapsed = time.time() - _start
    print(f"  Elapsed:   {elapsed // 3600:.0f}h {elapsed % 3600 // 60:.0f}m {elapsed % 60:.0f}s")


if __name__ == "__main__":
    main()
