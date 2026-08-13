"""compare-alignment: compare our SB 0.4 alignments against a partner's
(Biblica) hand-curated SB 0.3 reference alignment for the same translation.

Reports per-verse and aggregate precision/recall/F1 over source->target
links (both primary and secondary source ids count), restricted to the
intersection of verse coverage between the two alignment sources. Target
token ids are reconciled between the two independently-tokenized TSVs via
a word-level diff (see compare/links.py, reusing migrate/diff.py's
build_remap) rather than assumed identical.

CLI entry point: compare-alignment
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from text_align import ROOT
from text_align.config import load_config_from_args, require
from text_align.migrate.tsv import process_usfm_tsv
from text_align.refine.refine import _filter_verse_ids
from text_align.refine.retry import _filter_chapter_files, discover_chapter_files
from text_align.refine.source import load_source_verses
from text_align.refine.util import _CORPUS_ID
from text_align.burrito.AlignmentSet import AlignmentSet
from text_align.burrito.alignments import AlignmentsReader

from .biblica import load_biblica_reader, load_biblica_target_verses
from .compare_html import flatten_target_text, render_verse_table, write_comparison_html
from .links import build_target_id_map
from .metrics import compare_chapters, print_summary, write_comparison_tsv

_SOURCES_DIR = ROOT / "data" / "sources"


def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="LLM-REFINED")

    p = argparse.ArgumentParser(
        description=(
            "Compare our alignment output against Biblica's hand-curated SB 0.3 "
            "reference alignment for the same translation."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--alignment-dir", default=None, type=Path,
                   help="Directory containing our chapter JSON files to compare")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code, e.g. hin — also used as Biblica's "
                        "alignments-<code> directory suffix")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID, e.g. IRVHin")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing our target TSVs")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing SBLGNT.tsv and WLCM.tsv (default: {_SOURCES_DIR})")
    p.add_argument("--corpus", default=None, choices=["ot", "nt"],
                   help="Corpus: 'nt' for SBLGNT, 'ot' for WLCM")
    p.add_argument("--clear-root", default="~/git/Clear-Bible", metavar="PATH",
                   help="Root of Biblica's Clear-Bible checkout, containing "
                        "alignments-<lang>/ repos (default: ~/git/Clear-Bible)")
    p.add_argument("--biblica-reference-file", default=None,
                   help="Explicit Biblica reference alignment filename/path override "
                        "(default: {sourceid}-{targetid}-manual.json). Prefer the "
                        "corpus-specific config keys below when NT/OT need different files.")
    p.add_argument("--biblica-reference-file-nt", default=None,
                   help="Override --biblica-reference-file for --corpus nt only.")
    p.add_argument("--biblica-reference-file-ot", default=None,
                   help="Override --biblica-reference-file for --corpus ot only.")
    p.add_argument("--output", default=None, type=Path,
                   help="Write per-verse comparison TSV to this file "
                        "(default: output/<target-edition>/compare_YYYY-MM-DD.tsv)")
    p.add_argument("--html-output", nargs="?", const="", default=None, type=str,
                   help="Also write a per-verse HTML side-by-side diff. Pass a path, "
                        "or bare --html-output for the default "
                        "output/<target-edition>/compare_YYYY-MM-DD.html")

    range_group = p.add_mutually_exclusive_group()
    range_group.add_argument("--verse", default=None, metavar="BCV",
                             help="Compare a single verse BCV, e.g. --verse 41004003")
    range_group.add_argument("--verse-range", default=None, nargs=2, metavar=("START", "END"),
                             help="Compare a BCV range, e.g. --verse-range 41004001 41004020")
    range_group.add_argument("--book", default=None, metavar="BB")
    range_group.add_argument("--book-range", default=None, nargs=2, metavar=("START", "END"))
    range_group.add_argument("--chapter", default=None, metavar="BBCCC")
    range_group.add_argument("--chapter-range", default=None, nargs=2,
                             metavar=("START", "END"))

    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "alignment_dir", "target_language", "target_edition",
            "target_tsv_dir", "corpus")
    return args


def _resolve_reference_override(args: argparse.Namespace) -> str | None:
    corpus_specific = getattr(args, f"biblica_reference_file_{args.corpus}", None)
    return corpus_specific or args.biblica_reference_file


def main() -> None:
    args = parse_args()
    if args.output is None:
        args.output = Path("output") / args.target_edition / f"compare_{date.today()}.tsv"
    # Bare --html-output lands in the same folder as --output (default or custom),
    # using the same date-stamped basename with a .html extension.
    if args.html_output == "":
        args.html_output = args.output.parent / f"compare_{date.today()}.html"
    elif args.html_output is not None:
        args.html_output = Path(args.html_output)

    sourceid = _CORPUS_ID[args.corpus]

    print(f"compare-alignment: {args.target_language}/{args.target_edition} ({args.corpus})")
    print(f"  Our alignment dir: {args.alignment_dir}")
    print(f"  Biblica root:      {args.clear_root}")

    chapter_files = discover_chapter_files(args.alignment_dir, sourceid)
    chapter_files = _filter_chapter_files(chapter_files, args)
    if not chapter_files:
        raise SystemExit("No chapter JSON files found in --alignment-dir.")
    print(f"  Chapters:          {len(chapter_files)}")

    alset = AlignmentSet(
        targetlanguage=args.target_language,
        targetid=args.target_edition,
        sourceid=sourceid,
        langdatapath=args.target_tsv_dir.parent.parent,
        alignmentpath_override=chapter_files[0],
    )
    our_reader = AlignmentsReader.from_chapter_files(chapter_files, alset)

    reference_override = _resolve_reference_override(args)
    biblica_reader = load_biblica_reader(
        args.clear_root, args.target_language, sourceid, args.target_edition,
        args.target_language, reference_override,
    )
    print(f"  Biblica reference: {len(biblica_reader.alignmentgroup.records)} record(s)")

    print("  Loading target TSVs ...")
    our_target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)
    biblica_target_verses = load_biblica_target_verses(
        args.clear_root, args.target_language, args.target_edition
    )
    id_map = build_target_id_map(our_target_verses, biblica_target_verses)

    our_verse_records = our_reader.alignmentgroup.verserecords()
    biblica_verse_records = biblica_reader.alignmentgroup.verserecords()
    # --book/--book-range/--chapter/--chapter-range already narrowed which of our
    # chapter files got loaded (via _filter_chapter_files above); Biblica's reader
    # always loads the whole reference file, and --verse/--verse-range operate at
    # finer-than-chapter granularity either way, so apply the same range filter to
    # both sides' verse-record maps here to pin the final comparison scope exactly.
    our_scope = set(_filter_verse_ids(sorted(our_verse_records), args))
    biblica_scope = set(_filter_verse_ids(sorted(biblica_verse_records), args))
    our_verse_records = {v: r for v, r in our_verse_records.items() if v in our_scope}
    biblica_verse_records = {v: r for v, r in biblica_verse_records.items() if v in biblica_scope}

    comparisons = compare_chapters(our_verse_records, biblica_verse_records, id_map)

    our_only_verses = set(our_verse_records) - set(biblica_verse_records)
    biblica_only_verses = set(biblica_verse_records) - set(our_verse_records)

    write_comparison_tsv(comparisons, args.output)
    print_summary(comparisons, our_only_verses, biblica_only_verses, args.output)

    if args.html_output:
        print(f"  Loading source tokens ({sourceid}) ...")
        source_verses = load_source_verses(args.sources_dir, args.corpus)
        our_target_text = flatten_target_text(our_target_verses)
        biblica_target_text = flatten_target_text(biblica_target_verses)
        sections = [
            render_verse_table(
                c.verse_id, c, source_verses.get(c.verse_id, []),
                our_verse_records[c.verse_id], biblica_verse_records[c.verse_id],
                id_map, our_target_text, biblica_target_text,
            )
            for c in comparisons
        ]
        write_comparison_html(
            sections, args.html_output,
            title=f"{args.target_edition} vs. Biblica reference ({sourceid})",
            comparisons=comparisons,
        )
        print(f"  HTML diff: {args.html_output}")


if __name__ == "__main__":
    main()
