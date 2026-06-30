"""clean-alignments: validate and repair chapter JSON alignment files in place.

CLI entry point: clean-alignments
"""

from __future__ import annotations

import argparse
from pathlib import Path

from text_align import ROOT
from text_align.config import load_config_from_args, require
from text_align.migrate.tsv import process_usfm_tsv

from .clean import run_clean_pass
from .retry import _filter_chapter_files, discover_chapter_files
from .source import load_source_verses
from .util import _CORPUS_ID


_SOURCES_DIR = ROOT / "data" / "sources"


def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="LLM-REFINED")

    p = argparse.ArgumentParser(
        description=(
            "Validate and repair chapter alignment JSON files in place. "
            "Drops or repairs records with invalid token references, "
            "duplicate source/target tokens, or secondary-primary conflicts. "
            "Run before score-alignment or render-alignment to ensure all "
            "tools see the same data."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--alignment-dir", default=None, type=Path,
                   help="Directory containing chapter JSON files to clean")
    p.add_argument("--corpus", default=None, choices=["ot", "nt"],
                   help="Corpus: 'nt' for SBLGNT, 'ot' for WLCM")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID, e.g. BSB")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing target edition TSVs")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing SBLGNT.tsv and WLCM.tsv (default: {_SOURCES_DIR})")

    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--book", default=None, metavar="BB",
                             help="Limit to a single book, e.g. --book 66")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Limit to a book range, e.g. --book-range 65 66")
    range_group.add_argument("--chapter", default=None, metavar="BBCCC",
                             help="Limit to a single chapter, e.g. --chapter 66007")
    range_group.add_argument("--chapter-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Limit to a chapter range, e.g. --chapter-range 66001 66022")

    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "alignment_dir", "corpus", "target_edition", "target_tsv_dir")
    return args


def main() -> None:
    args = parse_args()
    corpus_id = _CORPUS_ID[args.corpus]

    chapter_files = discover_chapter_files(args.alignment_dir)
    chapter_files = _filter_chapter_files(chapter_files, args)
    if not chapter_files:
        raise SystemExit("No chapter JSON files found in --alignment-dir.")

    print(f"clean-alignments: {args.target_edition}")
    print(f"  Alignment dir: {args.alignment_dir}")
    print(f"  {len(chapter_files)} chapter file(s)")

    print(f"  Loading source tokens ({corpus_id}) ...")
    source_verses = load_source_verses(args.sources_dir, args.corpus)

    print(f"  Loading target tokens ({args.target_edition}) ...")
    target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)

    files_changed, dropped, repaired = run_clean_pass(
        chapter_files, source_verses, target_verses
    )

    if files_changed:
        print(
            f"  Cleaned {files_changed} file(s): "
            f"{dropped} record(s) dropped, {repaired} record(s) repaired."
        )
    else:
        print("  All files clean — no changes needed.")
