"""score-alignment: audit alignment quality without running the LLM.

Reads chapter JSON files, scores each verse using the composite penalty scorer,
and writes a full per-verse TSV report to a file (never stdout — see below).
A human-readable summary (needs_retry breakdown by named reason, plus a
statistically "suspect" verse list) is printed to stdout by default. Useful
for deciding which chapters need retry-alignment and for tuning thresholds.

The full per-verse TSV is deliberately file-only: it is too much raw data to
visually scan for offenders. The stdout summary is the primary interface;
the TSV is there for tooling / spreadsheet review of everything at once.

CLI entry point: score-alignment
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path

from text_align import ROOT
from text_align.align.acai_common import ACAI_TYPES, build_word_entity_map, load_acai_entities
from text_align.config import load_config_from_args, require

from .clean import run_clean_pass
from .cost_estimate import DEFAULT_GLOO_RATES_CACHE, CostEstimate, estimate_retry_cost, fetch_gloo_rates
from .coverage import find_low_coverage_verses
from .retry import _filter_chapter_files, discover_chapter_files
from .scoring import ScoringConfig, VerseScore, find_suspect_verses, resolve_neq_baseline, score_chapter_file
from .source import load_source_verses
from .util import _CORPUS_ID, _chapter_id_from_path


_SOURCES_DIR = ROOT / "data" / "sources"

_TSV_FIELDS = [
    "verse_id",
    "composite",
    "signal_1",
    "signal_2",
    "signal_3",
    "signal_4",
    "signal_5",
    "needs_retry",
    "coverage_flagged",
    "structural_errors",
    "article_neq",
    "semantic_low_sim",
    "acai_unaligned",
    "smear_1toN",
    "smear_1toN_delta",
]



def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="LLM-REFINED")

    p = argparse.ArgumentParser(
        description=(
            "Score alignment quality for chapter JSON files and report per-verse "
            "penalty scores. Does not call the LLM."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--alignment-dir", default=None, type=Path,
                   help="Directory containing chapter JSON files to score")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code, e.g. eng")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID (used for path derivation only)")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing target TSVs (enables signal 2 scoring)")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing SBLGNT.tsv and WLCM.tsv (default: {_SOURCES_DIR})")
    p.add_argument("--corpus", default=None, choices=["ot", "nt"],
                   help="Corpus: 'nt' for SBLGNT, 'ot' for WLCM")
    p.add_argument("--score-retry-threshold", type=float, default=0.25,
                   help="Penalty threshold for needs_retry flag (default: 0.25)")
    p.add_argument("--neq-baseline", type=float, default=None,
                   help="Expected natural NEQ rate for signal 3 (NEQ overuse), for "
                        "either corpus. Defaults to a testament-aware value "
                        "(nt: 0.07, ot: 0.16) when omitted. Since one edition's config "
                        "covers both --corpus nt and --corpus ot runs, prefer "
                        "--neq-baseline-nt / --neq-baseline-ot (or the matching YAML "
                        "keys) to set them independently — actual rates vary "
                        "several-fold with translation style.")
    p.add_argument("--neq-baseline-nt", type=float, default=None,
                   help="Override --neq-baseline for --corpus nt only.")
    p.add_argument("--neq-baseline-ot", type=float, default=None,
                   help="Override --neq-baseline for --corpus ot only.")
    p.add_argument("--min-unaligned-src", type=int, default=2,
                   help="Also flag verses with N or more unaligned source tokens (default: 2)")
    p.add_argument("--suspect-stddev", type=float, default=2.5,
                   help="Suspect-verse threshold: mean + N*stddev of composite scores "
                        "across all verses scored in this run, computed corpus-wide "
                        "(default: 2.5)")
    p.add_argument("--output", default=None, type=Path,
                   help="Write full per-verse TSV report to this file "
                        "(default: output/score_YYYY-MM-DD.tsv). The TSV is always "
                        "written to a file, never stdout.")
    p.add_argument("--semantic-detail-output", action="store_true", default=False,
                   help="Write per-record semantic similarity details to output/semantic_detail_YYYY-MM-DD.tsv")
    p.add_argument("--flagged-only", action="store_true", default=False,
                   help="Only write verses where needs_retry is True to the TSV file "
                        "(does not affect the stdout summary)")
    p.add_argument("--semantic-model", default="sentence-transformers/LaBSE",
                   help="sentence-transformers model for semantic similarity check "
                        "(default: sentence-transformers/LaBSE). Pass empty string to disable.")
    p.add_argument("--semantic-threshold", type=float, default=0.35,
                   help="Cosine similarity below which a record is flagged (default: 0.35)")
    p.add_argument("--acai-data-dir", default=None, type=Path,
                   help="Path to ACAI root directory (omit to disable the ACAI-unaligned check)")
    p.add_argument("--acai-types", nargs="+", default=ACAI_TYPES,
                   help=f"ACAI entity types to load (default: {ACAI_TYPES})")
    p.add_argument("--include-acai-pronominals", action="store_true",
                   help="Include pronominal referents in ACAI entity data")
    p.add_argument("--llm-provider", default=None,
                   help="Provider to estimate retry cost for (Gloo-only; other providers "
                        "report cost as unknown). Defaults to retry_llm_provider or "
                        "llm_provider from --config if set.")
    p.add_argument("--llm-model", default=None,
                   help="Model to estimate retry cost for. Defaults to retry_llm_model or "
                        "llm_model from --config if set.")

    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--book", default=None, metavar="BB")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"))
    range_group.add_argument("--chapter", default=None, metavar="BBCCC")
    range_group.add_argument("--chapter-range", default=None, nargs=2,
                             metavar=("START", "END"))

    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "alignment_dir", "target_language", "corpus")

    # Cost estimation targets whichever model retry-alignment would actually
    # use — mirror its retry_llm_* > llm_* precedence (retry_cli.py).
    args.llm_provider = getattr(args, "retry_llm_provider", None) or args.llm_provider
    args.llm_model    = getattr(args, "retry_llm_model",    None) or args.llm_model

    return args


def _verse_reasons(vs: VerseScore, config: ScoringConfig, coverage_flagged: bool) -> list[str]:
    """Human-readable reasons a verse is flagged/suspect, most-significant weighted
    signal first, then any unconditional (non-composite) checks that fired."""
    contributions = {
        "source coverage gaps": config.w1 * vs.signal_1,
        "target coverage gaps": config.w2 * vs.signal_2,
        "NEQ overuse":          config.w3 * vs.signal_3,
        "token smearing":       config.w4 * vs.signal_4,
    }
    dominant, dominant_val = max(contributions.items(), key=lambda kv: kv[1])
    reasons: list[str] = [dominant] if dominant_val > 0 else []
    if vs.signal_4 > config.smear_forced_retry_threshold and "token smearing" not in reasons:
        reasons.append("token smearing")
    if coverage_flagged:
        reasons.append("low source coverage")
    if vs.article_neq_count:
        reasons.append("NEQ'd article")
    if vs.semantic_low_sim_count:
        reasons.append("low semantic similarity")
    if vs.acai_unaligned_count:
        reasons.append("unaligned ACAI entity")
    if vs.smear_1toN_count:
        reasons.append("wide 1:N grouping")
    return reasons or ["(unspecified)"]


def _format_ids(ids: list[str], cap: int = 6) -> str:
    shown = ids[:cap]
    text = ", ".join(shown)
    if len(ids) > cap:
        text += f", +{len(ids) - cap} more"
    return text


def _cost_suffix(cost: CostEstimate | None, n: int) -> str:
    if cost is None or n == 0:
        return ""
    return f"  [~${cost.cost:.2f} est. retry cost, ~${cost.cost / n:.3f}/verse]"


def _resolve_cost_estimator(
    llm_provider: str | None,
    llm_model: str | None,
    target_verses: dict | None,
    chapter_paths: dict[str, Path],
    source_verses: dict,
    target_language: str,
    corpus_id: str,
) -> tuple[Callable[[list[str]], "CostEstimate | None"], str | None]:
    """Returns (estimator_fn(verse_ids) -> CostEstimate | None, unavailable_reason).

    unavailable_reason is None when estimation is possible; otherwise it's a
    short human-readable explanation (or "" when no model was configured at
    all, in which case callers should stay silent rather than warn).
    """
    if not (llm_provider and llm_model):
        return (lambda _ids: None), ""
    if target_verses is None:
        return (lambda _ids: None), "requires --target-tsv-dir"
    if llm_provider != "gloo":
        return (lambda _ids: None), "cost estimation is Gloo-only"

    gloo_rates = fetch_gloo_rates(DEFAULT_GLOO_RATES_CACHE)
    if llm_model not in gloo_rates:
        return (lambda _ids: None), f"model {llm_model!r} not found in the live Gloo catalog"

    def estimator(verse_ids: list[str]) -> CostEstimate | None:
        if not verse_ids:
            return None
        return estimate_retry_cost(
            verse_ids, chapter_paths, source_verses, target_verses,
            target_language, corpus_id, llm_provider, llm_model, gloo_rates,
        )

    return estimator, None


def _print_summary(
    all_scores: list[VerseScore],
    all_coverage_flagged: set[str],
    scoring_config: ScoringConfig,
    suspect_k: float,
    target_language: str,
    corpus: str,
    corpus_id: str,
    n_chapters: int,
    tsv_path: Path,
    chapter_paths: dict[str, Path],
    source_verses: dict,
    target_verses: dict | None,
    llm_provider: str | None,
    llm_model: str | None,
) -> None:
    total = len(all_scores)
    if total == 0:
        print("No verses scored.")
        return

    def is_flagged(vs: VerseScore) -> bool:
        return vs.needs_retry or vs.verse_id in all_coverage_flagged

    flagged_scores = [vs for vs in all_scores if is_flagged(vs)]

    print(f"score-alignment — {target_language} ({corpus}), {n_chapters} chapter(s), {total} verse(s)\n")

    # Retry cost estimate — see cost_estimate.py. Gloo-only; requires a
    # resolved provider/model (CLI --llm-provider/--llm-model, or
    # retry_llm_*/llm_* from --config) and --target-tsv-dir. Silent when no
    # model is configured at all (cost estimation wasn't asked for); a short
    # reason is printed once when a model IS configured but estimation still
    # isn't possible (missing target text, non-Gloo provider, unknown model).
    estimator, unavailable_reason = _resolve_cost_estimator(
        llm_provider, llm_model, target_verses, chapter_paths,
        source_verses, target_language, corpus_id,
    )
    if unavailable_reason:
        print(f"  (retry cost estimate unavailable for {llm_provider}/{llm_model}: "
              f"{unavailable_reason})\n")

    bad_cost = estimator([vs.verse_id for vs in flagged_scores])
    pct = 100 * len(flagged_scores) / total
    print(f"needs_retry: {len(flagged_scores)} ({pct:.1f}%){_cost_suffix(bad_cost, len(flagged_scores))}")
    if flagged_scores:
        reason_ids: dict[str, list[str]] = {}
        for vs in flagged_scores:
            for reason in _verse_reasons(vs, scoring_config, vs.verse_id in all_coverage_flagged):
                reason_ids.setdefault(reason, []).append(vs.verse_id)
        for reason, ids in sorted(reason_ids.items(), key=lambda kv: -len(kv[1])):
            print(f"  {reason}: {len(ids)}   [{_format_ids(ids)}]")
    print()

    # Suspect verses: corpus-wide mean + k*stddev of composite, computed across
    # every verse scored in this run, excluding anything already flagged.
    flagged_ids = {vs.verse_id for vs in flagged_scores}
    suspects, bar = find_suspect_verses(all_scores, flagged_ids, suspect_k)
    suspect_cost = estimator([vs.verse_id for vs in suspects])

    spct = 100 * len(suspects) / total
    print(f"suspect (composite > mean+{suspect_k:g}σ={bar:.3f}, below retry threshold): "
          f"{len(suspects)} ({spct:.1f}%){_cost_suffix(suspect_cost, len(suspects))}")
    for vs in suspects:
        reasons = ", ".join(_verse_reasons(vs, scoring_config, False))
        print(f"  {vs.verse_id}  composite={vs.composite:.3f}  {reasons}")
    if suspects:
        verse_list = ",".join(vs.verse_id for vs in suspects)
        print(f"\n  --verse-list for retry-alignment:\n  {verse_list}")
    print()

    print(f"Full per-verse detail: {tsv_path}")


def main() -> None:
    args = parse_args()
    if args.output is None:
        args.output = Path("output") / f"score_{date.today()}.tsv"
    if args.semantic_detail_output:
        args.semantic_detail_output = Path("output") / f"semantic_detail_{date.today()}.tsv"
    corpus_id = _CORPUS_ID[args.corpus]

    chapter_files = discover_chapter_files(args.alignment_dir, corpus_id)
    chapter_files = _filter_chapter_files(chapter_files, args)
    if not chapter_files:
        raise SystemExit("No chapter JSON files found in --alignment-dir.")
    chapter_paths: dict[str, Path] = {_chapter_id_from_path(cf): cf for cf in chapter_files}

    print(f"score-alignment: {args.target_language}", file=sys.stderr)
    print(f"  Alignment dir:   {args.alignment_dir}", file=sys.stderr)
    print(f"  Retry threshold: score>{args.score_retry_threshold:.2f} or unaligned-src>={args.min_unaligned_src}", file=sys.stderr)
    if args.semantic_model:
        if not (args.target_tsv_dir and args.target_edition):
            print(
                "  Warning: --semantic-model requires --target-tsv-dir and --target-edition; "
                "semantic check will be skipped.",
                file=sys.stderr,
            )
        else:
            print(f"  Semantic model:  {args.semantic_model} (threshold={args.semantic_threshold:.2f})", file=sys.stderr)
    print(f"  Chapters:        {len(chapter_files)}", file=sys.stderr)

    print(f"  Loading source tokens ({corpus_id}) ...", file=sys.stderr)
    source_verses = load_source_verses(args.sources_dir, args.corpus)

    target_verses = None
    if args.target_tsv_dir and args.target_edition:
        from text_align.migrate.tsv import process_usfm_tsv
        print(f"  Loading target tokens ({args.target_edition}) ...", file=sys.stderr)
        target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)

    acai_src_ids: set[str] | None = None
    if args.acai_data_dir is not None:
        print(f"  Loading ACAI entities ({args.acai_data_dir}) ...", file=sys.stderr)
        acai_entities = load_acai_entities(
            args.acai_data_dir, args.acai_types, args.corpus,
            include_pronominals=args.include_acai_pronominals,
        )
        acai_src_ids = set(build_word_entity_map(acai_entities).keys())
        print(f"  ACAI-tagged source tokens: {len(acai_src_ids)}", file=sys.stderr)

    print("  Cleaning alignment files ...", file=sys.stderr)
    files_changed, dropped, repaired = run_clean_pass(chapter_files, source_verses, target_verses)
    if files_changed:
        print(
            f"  Cleaned {files_changed} file(s): "
            f"{dropped} record(s) dropped, {repaired} record(s) repaired.",
            file=sys.stderr,
        )

    neq_baseline = resolve_neq_baseline(args)
    print(f"  NEQ baseline: {neq_baseline:.3f}", file=sys.stderr)
    scoring_config = ScoringConfig(
        retry_threshold=args.score_retry_threshold,
        neq_baseline=neq_baseline,
        semantic_model=args.semantic_model,
        semantic_threshold=args.semantic_threshold,
    )

    semantic_details: list | None = [] if args.semantic_detail_output else None

    all_scores: list[VerseScore] = []
    all_coverage_flagged: set[str] = set()
    for cf in chapter_files:
        verse_scores = score_chapter_file(
            cf, source_verses, args.target_language, scoring_config,
            target_verses=target_verses,
            record_details=semantic_details,
            acai_src_ids=acai_src_ids,
        )
        all_scores.extend(verse_scores)
        all_coverage_flagged.update(
            spec.verse_id
            for spec in find_low_coverage_verses(cf, source_verses, args.min_unaligned_src,
                                                  target_verses=target_verses)
        )

    tsv_scores = all_scores
    if args.flagged_only:
        tsv_scores = [
            vs for vs in all_scores
            if vs.needs_retry or vs.verse_id in all_coverage_flagged
        ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as out_stream:
        writer = csv.DictWriter(out_stream, fieldnames=_TSV_FIELDS, delimiter="\t")
        writer.writeheader()
        for vs in tsv_scores:
            coverage_flagged = vs.verse_id in all_coverage_flagged
            writer.writerow({
                "verse_id":          vs.verse_id,
                "composite":         f"{vs.composite:.4f}",
                "signal_1":          f"{vs.signal_1:.4f}",
                "signal_2":          f"{vs.signal_2:.4f}",
                "signal_3":          f"{vs.signal_3:.4f}",
                "signal_4":          f"{vs.signal_4:.4f}",
                "signal_5":          f"{vs.signal_5:.4f}",
                "needs_retry":       str(vs.needs_retry or coverage_flagged),
                "coverage_flagged":  str(coverage_flagged),
                "structural_errors": vs.structural_errors,
                "article_neq":       vs.article_neq_count,
                "semantic_low_sim":  vs.semantic_low_sim_count,
                "acai_unaligned":    vs.acai_unaligned_count,
                "smear_1toN":        vs.smear_1toN_count,
                "smear_1toN_delta":  (f"{vs.smear_1toN_max_delta:+.4f}"
                                      if vs.smear_1toN_max_delta is not None else ""),
            })

    if semantic_details is not None and args.semantic_detail_output:
        _DETAIL_FIELDS = [
            "verse_id", "src_ids", "src_lemmas", "src_gloss", "src_gloss_alt",
            "tgt_ids", "tgt_text", "similarity", "below_threshold",
        ]
        args.semantic_detail_output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.semantic_detail_output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_DETAIL_FIELDS, delimiter="\t")
            writer.writeheader()
            writer.writerows(semantic_details)
        print(
            f"  Semantic detail: {len(semantic_details)} record(s) → {args.semantic_detail_output}",
            file=sys.stderr,
        )

    _print_summary(
        all_scores, all_coverage_flagged, scoring_config, args.suspect_stddev,
        args.target_language, args.corpus, corpus_id, len(chapter_files), args.output,
        chapter_paths, source_verses, target_verses, args.llm_provider, args.llm_model,
    )


if __name__ == "__main__":
    main()
