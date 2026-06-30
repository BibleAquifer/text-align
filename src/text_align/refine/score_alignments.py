"""score-alignment: audit alignment quality without running the LLM.

Reads chapter JSON files, scores each verse using the composite penalty scorer,
and writes a TSV report to stdout (or --output). Useful for deciding which
chapters need retry-alignment and for tuning the scoring thresholds.

CLI entry point: score-alignment
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from text_align import ROOT
from text_align.config import load_config_from_args, require

from .clean import run_clean_pass
from .coverage import find_low_coverage_verses
from .retry import _filter_chapter_files, discover_chapter_files
from .scoring import ScoringConfig, VerseScore, score_chapter_file
from .source import load_source_verses
from .util import _CORPUS_ID


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
    p.add_argument("--min-unaligned-src", type=int, default=2,
                   help="Also flag verses with N or more unaligned source tokens (default: 2)")
    p.add_argument("--output", default=None, type=Path,
                   help="Write TSV report to this file (default: stdout)")
    p.add_argument("--semantic-detail-output", action="store_true", default=False,
                   help="Write per-record semantic similarity details to output/semantic_detail_YYYY-MM-DD.tsv")
    p.add_argument("--flagged-only", action="store_true", default=False,
                   help="Only output verses where needs_retry is True")
    p.add_argument("--semantic-model", default="sentence-transformers/LaBSE",
                   help="sentence-transformers model for semantic similarity check "
                        "(default: sentence-transformers/LaBSE). Pass empty string to disable.")
    p.add_argument("--semantic-threshold", type=float, default=0.35,
                   help="Cosine similarity below which a record is flagged (default: 0.35)")

    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--book", default=None, metavar="BB")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"))
    range_group.add_argument("--chapter", default=None, metavar="BBCCC")
    range_group.add_argument("--chapter-range", default=None, nargs=2,
                             metavar=("START", "END"))

    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "alignment_dir", "target_language", "corpus")
    return args


def main() -> None:
    args = parse_args()
    if args.semantic_detail_output:
        from datetime import date
        args.semantic_detail_output = Path("output") / f"semantic_detail_{date.today()}.tsv"
    corpus_id = _CORPUS_ID[args.corpus]

    chapter_files = discover_chapter_files(args.alignment_dir)
    chapter_files = _filter_chapter_files(chapter_files, args)
    if not chapter_files:
        raise SystemExit("No chapter JSON files found in --alignment-dir.")

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

    print("  Cleaning alignment files ...", file=sys.stderr)
    files_changed, dropped, repaired = run_clean_pass(chapter_files, source_verses, target_verses)
    if files_changed:
        print(
            f"  Cleaned {files_changed} file(s): "
            f"{dropped} record(s) dropped, {repaired} record(s) repaired.",
            file=sys.stderr,
        )

    scoring_config = ScoringConfig(
        retry_threshold=args.score_retry_threshold,
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
        )
        all_scores.extend(verse_scores)
        all_coverage_flagged.update(
            spec.verse_id
            for spec in find_low_coverage_verses(cf, source_verses, args.min_unaligned_src,
                                                  target_verses=target_verses)
        )

    if args.flagged_only:
        all_scores = [
            vs for vs in all_scores
            if vs.needs_retry or vs.verse_id in all_coverage_flagged
        ]

    total = len(all_scores)
    flagged = sum(
        1 for vs in all_scores
        if vs.needs_retry or vs.verse_id in all_coverage_flagged
    )
    print(
        f"  Scored {total} verse(s); {flagged} flagged for retry "
        f"({100*flagged/total:.1f}%)" if total else "  No verses scored.",
        file=sys.stderr,
    )

    out_stream = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        writer = csv.DictWriter(out_stream, fieldnames=_TSV_FIELDS, delimiter="\t")
        writer.writeheader()
        for vs in all_scores:
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
            })
    finally:
        if args.output:
            out_stream.close()

    if semantic_details is not None and args.semantic_detail_output:
        _DETAIL_FIELDS = [
            "verse_id", "src_ids", "src_lemmas", "src_gloss", "src_gloss_alt",
            "tgt_ids", "tgt_text", "similarity", "below_threshold",
        ]
        with open(args.semantic_detail_output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_DETAIL_FIELDS, delimiter="\t")
            writer.writeheader()
            writer.writerows(semantic_details)
        print(
            f"  Semantic detail: {len(semantic_details)} record(s) → {args.semantic_detail_output}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
