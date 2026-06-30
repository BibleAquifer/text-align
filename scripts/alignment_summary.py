#!/usr/bin/env python3
"""Whole-run alignment summary for a completed refine+retry NT run.

Reads chapter JSON files from the LLM-REFINED directory, compares verse
coverage against SBLGNT.tsv, and reports chapters complete, failed chapters,
verses aligned, failed verses, and verses retried.

Usage:
    poetry run python scripts/alignment_summary.py --config BSB --corpus nt
    poetry run python scripts/alignment_summary.py --config BSB --corpus nt --markdown
        (--markdown emits GFM for $GITHUB_STEP_SUMMARY)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from text_align import ROOT
from text_align.config import derive_paths, load_config

_SOURCES_DIR = ROOT / "data" / "sources"

_NT_BOOK_NAMES: dict[str, str] = {
    "40": "Matt",    "41": "Mark",    "42": "Luke",    "43": "John",
    "44": "Acts",    "45": "Rom",     "46": "1 Cor",   "47": "2 Cor",
    "48": "Gal",     "49": "Eph",     "50": "Phil",    "51": "Col",
    "52": "1 Thess", "53": "2 Thess", "54": "1 Tim",   "55": "2 Tim",
    "56": "Titus",   "57": "Phlm",    "58": "Heb",     "59": "James",
    "60": "1 Pet",   "61": "2 Pet",   "62": "1 John",  "63": "2 John",
    "64": "3 John",  "65": "Jude",    "66": "Rev",
}

_OT_BOOK_NAMES: dict[str, str] = {
    "01": "Gen",   "02": "Exod",  "03": "Lev",   "04": "Num",   "05": "Deut",
    "06": "Josh",  "07": "Judg",  "08": "Ruth",  "09": "1 Sam", "10": "2 Sam",
    "11": "1 Kgs", "12": "2 Kgs", "13": "1 Chr", "14": "2 Chr", "15": "Ezra",
    "16": "Neh",   "17": "Esth",  "18": "Job",   "19": "Ps",    "20": "Prov",
    "21": "Eccl",  "22": "Song",  "23": "Isa",   "24": "Jer",   "25": "Lam",
    "26": "Ezek",  "27": "Dan",   "28": "Hos",   "29": "Joel",  "30": "Amos",
    "31": "Obad",  "32": "Jonah", "33": "Mic",   "34": "Nah",   "35": "Hab",
    "36": "Zeph",  "37": "Hag",   "38": "Zech",  "39": "Mal",
}

_OT_SECTIONS: dict[str, tuple[str, str]] = {
    "law":      ("01", "05"),
    "history":  ("06", "17"),
    "poetry":   ("18", "22"),
    "prophets": ("23", "39"),
}


def _chapter_name(chapter_id: str) -> str:
    book_num = chapter_id[:2]
    book = (
        _NT_BOOK_NAMES.get(book_num)
        or _OT_BOOK_NAMES.get(book_num)
        or book_num
    )
    return f"{book} {int(chapter_id[2:])}"


# ---------------------------------------------------------------------------
# Source verse loading
# ---------------------------------------------------------------------------

def _load_source_chapters(sources_dir: Path, corpus_id: str) -> dict[str, list[str]]:
    """Return chapter_id -> sorted list of verse IDs from the source TSV.

    Token IDs in SBLGNT.tsv have an 'n' prefix: n BBCCCVVVWWW.
    Verse ID = positions 1:9; chapter ID = positions 1:6.
    """
    tsv = sources_dir / f"{corpus_id}.tsv"
    chapters: dict[str, set[str]] = {}
    with tsv.open(encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            tid = line.split("\t", 1)[0]
            if len(tid) < 9:
                continue
            # strip leading letter prefix (n / o)
            numeric = tid.lstrip("no")
            if len(numeric) < 8:
                continue
            verse_id = numeric[:8]
            chapter_id = numeric[:5]
            chapters.setdefault(chapter_id, set()).add(verse_id)
    return {ch: sorted(vids) for ch, vids in sorted(chapters.items())}


# ---------------------------------------------------------------------------
# Chapter JSON reading
# ---------------------------------------------------------------------------

def _aligned_verse_ids(chapter_path: Path) -> set[str]:
    """Return the set of verse IDs that have at least one record in the chapter JSON.

    Verse IDs are derived from source token IDs in both regular records and the
    nonEquivalent section (tokens stored without prefix: BBCCCVVVWWW).
    """
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


# ---------------------------------------------------------------------------
# Sidecar reading
# ---------------------------------------------------------------------------

def _collect_retried_verses(output_dir: Path) -> set[str]:
    """Union all retried_verses arrays from .retries.json sidecars."""
    retried: set[str] = set()
    for sidecar in output_dir.glob("*.retries.json"):
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            retried.update(data.get("retried_verses", []))
        except (json.JSONDecodeError, OSError):
            pass
    return retried


# ---------------------------------------------------------------------------
# Summary computation
# ---------------------------------------------------------------------------

def compute_summary(
    source_chapters: dict[str, list[str]],
    output_dir: Path,
    corpus_id: str,
    edition: str,
) -> dict:
    """Compute summary statistics across all source chapters."""
    total_chapters = len(source_chapters)
    total_verses = sum(len(vids) for vids in source_chapters.values())

    complete_chapters: list[str] = []
    failed_chapters: list[str] = []
    failed_verses: list[str] = []
    aligned_verse_count = 0

    for chapter_id, src_verse_ids in source_chapters.items():
        bb, ccc = chapter_id[:2], chapter_id[2:]
        json_path = output_dir / f"{corpus_id}-{edition}-{bb}-{ccc}-manual.json"

        if not json_path.exists():
            failed_chapters.append(chapter_id)
            failed_verses.extend(src_verse_ids)
            continue

        aligned = _aligned_verse_ids(json_path)
        if not aligned:
            failed_chapters.append(chapter_id)
            failed_verses.extend(src_verse_ids)
            continue

        complete_chapters.append(chapter_id)
        for vid in src_verse_ids:
            if vid in aligned:
                aligned_verse_count += 1
            else:
                failed_verses.append(vid)

    retried_verses = _collect_retried_verses(output_dir)

    return {
        "total_chapters": total_chapters,
        "complete_chapters": complete_chapters,
        "failed_chapters": failed_chapters,
        "total_verses": total_verses,
        "aligned_verses": aligned_verse_count,
        "failed_verses": sorted(failed_verses),
        "retried_verses": retried_verses,
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def _fmt_int(n: int) -> str:
    return f"{n:,}"


def print_plain(s: dict, edition: str, corpus: str) -> None:
    print(f"Alignment Summary — {edition} {corpus.upper()}")
    print()
    print(f"  Chapters complete : {len(s['complete_chapters'])} / {s['total_chapters']}")
    print(f"  Failed chapters   : {len(s['failed_chapters'])}")
    print(f"  Verses aligned    : {_fmt_int(s['aligned_verses'])} / {_fmt_int(s['total_verses'])}")
    print(f"  Failed verses     : {_fmt_int(len(s['failed_verses']))}")
    print(f"  Verses retried    : {_fmt_int(len(s['retried_verses']))}")

    if s["failed_chapters"]:
        print("\nFailed chapters:")
        for ch in s["failed_chapters"]:
            print(f"  {ch}  {_chapter_name(ch)}")

    if s["failed_verses"]:
        first20 = s["failed_verses"][:20]
        print(f"\nFailed verses (first {len(first20)} of {len(s['failed_verses'])}):")
        print("  " + "  ".join(first20))


def print_markdown(s: dict, edition: str, corpus: str) -> None:
    print(f"## Alignment Summary — {edition} {corpus.upper()}")
    print()
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Chapters complete | {len(s['complete_chapters'])} / {s['total_chapters']} |")
    print(f"| Failed chapters   | {len(s['failed_chapters'])} |")
    print(f"| Verses aligned    | {_fmt_int(s['aligned_verses'])} / {_fmt_int(s['total_verses'])} |")
    print(f"| Failed verses     | {_fmt_int(len(s['failed_verses']))} |")
    print(f"| Verses retried    | {_fmt_int(len(s['retried_verses']))} |")

    if s["failed_chapters"]:
        print()
        print("### Failed chapters")
        for ch in s["failed_chapters"]:
            print(f"- {ch}  {_chapter_name(ch)}")

    if s["failed_verses"]:
        first20 = s["failed_verses"][:20]
        rest = len(s["failed_verses"]) - len(first20)
        print()
        print(f"### Failed verses (first {len(first20)} of {len(s['failed_verses'])})")
        print("```")
        print("  ".join(first20))
        if rest:
            print(f"... and {rest} more")
        print("```")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml")
    p.add_argument("--corpus", default="nt", choices=["nt", "ot"],
                   help="Corpus to summarise (default: nt)")
    p.add_argument("--section", choices=list(_OT_SECTIONS), default=None,
                   help="OT canonical section (law/history/poetry/prophets); "
                        "limits summary to that section when provided")
    p.add_argument("--edition", default=None,
                   help="Target edition ID, e.g. BSB")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory containing LLM-REFINED chapter JSON files")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing source TSV files (default: {_SOURCES_DIR})")
    p.add_argument("--markdown", action="store_true",
                   help="Emit GitHub-flavoured markdown (for $GITHUB_STEP_SUMMARY)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    corpus_id = "WLCM" if args.corpus == "ot" else "SBLGNT"
    edition = args.edition
    output_dir = args.output_dir

    if args.config:
        raw = load_config(args.config)
        config = derive_paths(raw, output_suffix="LLM-REFINED")
        edition = edition or config.get("target_edition")
        output_dir = output_dir or config.get("output_dir")

    if not edition:
        raise SystemExit("error: --edition is required (or set via --config)")
    if not output_dir:
        raise SystemExit("error: --output-dir is required (or set via --config)")

    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise SystemExit(f"error: output-dir does not exist: {output_dir}")

    source_chapters = _load_source_chapters(args.sources_dir, corpus_id)
    if args.corpus == "ot" and args.section:
        lo, hi = _OT_SECTIONS[args.section]
        source_chapters = {
            ch: vids for ch, vids in source_chapters.items()
            if lo <= ch[:2] <= hi
        }
    summary = compute_summary(source_chapters, output_dir, corpus_id, edition)

    if args.markdown:
        print_markdown(summary, edition, args.corpus)
    else:
        print_plain(summary, edition, args.corpus)


if __name__ == "__main__":
    main()
