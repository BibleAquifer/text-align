"""diff-migrate: migrate alignments from one translation to another using text diffs.

Uses diff_match_patch word-mode diffs to identify same-text spans between a
reference (source) translation and an unaligned (target) translation, then
remaps alignment target token IDs across those matched spans.

CLI entry point: ``diff-migrate``
"""

import argparse
from pathlib import Path

from . import diff_match_patch as dmp_module

from text_align.config import load_config_from_args, require
from .alignment_io import create_new_alignments, load_alignment_json, write_alignment_json
from .tsv import dump_verse_text, process_usfm_tsv


# ---------------------------------------------------------------------------
# Diff helpers
# ---------------------------------------------------------------------------

def diff_word_mode(text1: str, text2: str) -> list[tuple[int, str]]:
    """Return word-level diffs between *text1* and *text2*.

    Uses diff_match_patch's linesToWords trick to operate at word granularity.
    """
    dmp = dmp_module.diff_match_patch()
    initial = dmp.diff_linesToWords(text1, text2)
    diffs = dmp.diff_main(initial[0], initial[1], False)
    dmp.diff_charsToLines(diffs, initial[2])
    return diffs


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def build_remap(
    source_verses: dict,
    target_verses: dict,
    verbose: bool = False,
) -> dict[str, str]:
    """Build a source-token-ID → target-token-ID remap dict via word diffs."""
    remap: dict[str, str] = {}
    for verse_id, target_verse in target_verses.items():
        if verse_id not in source_verses:
            if verbose:
                print(f"Verse {verse_id} not in source TSV, skipping")
            continue

        source_tokens = list(source_verses[verse_id].words.values())
        target_tokens = list(target_verse.words.values())
        source_text = dump_verse_text(source_tokens)
        target_text = dump_verse_text(target_tokens)

        if source_text == target_text and len(source_tokens) == len(target_tokens):
            # identical verses: direct 1-to-1 remap
            for src, trg in zip(source_tokens, target_tokens):
                remap[src.id] = trg.id
        else:
            diffs = diff_word_mode(source_text, target_text)
            if verbose:
                print(f"{verse_id}: {diffs}")
            src_i = trg_i = 0
            for op, text in diffs:
                tokens = [t for t in text.split(" ") if t]
                if op == 0:  # equal
                    for _ in tokens:
                        if src_i < len(source_tokens) and trg_i < len(target_tokens):
                            remap[source_tokens[src_i].id] = target_tokens[trg_i].id
                            src_i += 1
                            trg_i += 1
                elif op == -1:  # delete (source only)
                    src_i += len(tokens)
                elif op == 1:  # insert (target only)
                    trg_i += len(tokens)
    return remap


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="DIFF-MIGRATED")

    p = argparse.ArgumentParser(
        description=(
            "Migrate alignments from a reference translation to a similar translation "
            "using word-level text diffs."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--source-edition", default=None,
                   help="Source (reference) edition ID, e.g. NIV11")
    p.add_argument("--target-edition", default=None,
                   help="Target (unaligned) edition ID, e.g. NIrV")
    p.add_argument("--source-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<source>.tsv and nt_<source>.tsv")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<target>.tsv and nt_<target>.tsv")
    p.add_argument("--source-alignment-dir", default=None, type=Path,
                   help="Directory containing source alignment JSON files")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory to write migrated alignment JSON files")
    p.add_argument("--ot-corpus", default="WLCM",
                   help="OT source corpus ID (default: WLCM)")
    p.add_argument("--nt-corpus", default="SBLGNT",
                   help="NT source corpus ID (default: SBLGNT)")
    p.add_argument("--creator", default="text-align",
                   help="Creator string written into alignment meta (default: text-align)")
    p.add_argument("--verbose", action="store_true",
                   help="Print diff output for each verse")
    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "source_edition", "target_edition",
            "source_tsv_dir", "target_tsv_dir", "source_alignment_dir", "output_dir")
    return args


def main() -> None:
    args = parse_args()

    print("Loading source TSV ...")
    source_verses = process_usfm_tsv(args.source_tsv_dir, args.source_edition)
    print("Loading target TSV ...")
    target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)

    print("Building remap via word diffs ...")
    remap = build_remap(source_verses, target_verses, verbose=args.verbose)
    print(f"Remap contains {len(remap)} token ID mappings.")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for corpus in (args.ot_corpus, args.nt_corpus):
        src_path = args.source_alignment_dir / f"{corpus}-{args.source_edition}-manual.json"
        if not src_path.exists():
            print(f"Source alignment not found, skipping: {src_path}")
            continue
        print(f"Migrating {src_path.name} ...")
        src_alignments = load_alignment_json(src_path)
        new_alignments = create_new_alignments(
            src_alignments, remap, corpus, args.target_edition, creator=args.creator
        )
        out_path = args.output_dir / f"{corpus}-{args.target_edition}-manual.json"
        write_alignment_json(new_alignments, out_path)
        print(f"  → {out_path}  ({len(new_alignments['groups'][0]['records'])} records)")


if __name__ == "__main__":
    main()
