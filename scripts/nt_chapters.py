#!/usr/bin/env python3
"""NT chapter matrix and status reporter.

Usage:
    poetry run python scripts/nt_chapters.py
        Human-readable table of all NT chapters with verse counts.

    poetry run python scripts/nt_chapters.py --json [--chapter BBCCC]
        JSON array for GHA matrix input (<=256 entries; short chapters bundled).
        Each entry: {"id", "start", "end", "label"}.
        Use --chapter to emit a single-entry matrix (for GHA re-run of one chapter).

    poetry run python scripts/nt_chapters.py --status --config BSB
    poetry run python scripts/nt_chapters.py --status --edition BSB --output-dir PATH
        Per-chapter DONE/PENDING with summary line.
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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_nt_chapters(sources_dir: Path) -> list[tuple[str, int]]:
    """Return sorted (chapter_id, verse_count) pairs from SBLGNT.tsv.

    chapter_id is a 5-char BBCCC string; verse_count is the number of
    distinct BBCCCVVV verse IDs in that chapter.
    """
    tsv = sources_dir / "SBLGNT.tsv"
    verses_by_chapter: dict[str, set[str]] = {}
    with tsv.open(encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            tid = line.split("\t", 1)[0]
            if not tid.startswith("n"):
                continue
            # n BBCCCVVVWWW: positions 1:9 = verse ID, 1:6 = chapter ID
            verses_by_chapter.setdefault(tid[1:6], set()).add(tid[1:9])
    return [(ch, len(vs)) for ch, vs in sorted(verses_by_chapter.items())]


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _chapter_name(chapter_id: str) -> str:
    book = _NT_BOOK_NAMES.get(chapter_id[:2], chapter_id[:2])
    return f"{book} {int(chapter_id[2:])}"


def _chapter_label(chapter_id: str, verse_count: int) -> str:
    return f"{_chapter_name(chapter_id)} ({verse_count}v)"


# ---------------------------------------------------------------------------
# Matrix building with short-chapter bundling (item D)
# ---------------------------------------------------------------------------

def _build_matrix(chapters: list[tuple[str, int]], max_entries: int = 256) -> list[dict]:
    """Return GHA matrix entries, bundling adjacent short chapters until len <= max_entries.

    Each entry has:
        id     — unique string key, e.g. "40001" or "63001-64001"
        start  — first chapter_id in the entry
        end    — last chapter_id in the entry (same as start for single chapters)
        label  — human-readable description for GHA job display
    """
    # Internal working list: each item is a list of (chapter_id, verse_count) pairs
    entries: list[list[tuple[str, int]]] = [[(ch, vc)] for ch, vc in chapters]

    while len(entries) > max_entries:
        # Find the single-chapter entry with fewest verses
        single_entries = [(i, e[0][1]) for i, e in enumerate(entries) if len(e) == 1]
        if not single_entries:
            break  # all already bundled — shouldn't happen given NT size
        idx, _ = min(single_entries, key=lambda x: x[1])
        # Merge with next entry, or previous if idx is the last
        neighbor = idx + 1 if idx + 1 < len(entries) else idx - 1
        lo, hi = min(idx, neighbor), max(idx, neighbor)
        merged = entries[lo] + entries[hi]
        entries = entries[:lo] + [merged] + entries[hi + 1:]

    result = []
    for e in entries:
        start = e[0][0]
        end = e[-1][0]
        total_vc = sum(vc for _, vc in e)
        if len(e) == 1:
            label = _chapter_label(start, total_vc)
            entry_id = start
        else:
            parts = " + ".join(_chapter_name(ch) for ch, _ in e)
            label = f"{parts} ({total_vc}v)"
            entry_id = f"{start}-{end}"
        result.append({"id": entry_id, "start": start, "end": end, "label": label})
    return result


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_table(chapters: list[tuple[str, int]]) -> None:
    print(f"{'Chapter':<8}  {'Name':<18}  {'Verses':>6}")
    print("-" * 36)
    for ch, vc in chapters:
        print(f"{ch:<8}  {_chapter_name(ch):<18}  {vc:>6}")
    total_vc = sum(vc for _, vc in chapters)
    print(f"\nTotal: {len(chapters)} chapters, {total_vc} verses")


def cmd_json(
    chapters: list[tuple[str, int]],
    single_chapter: str | None = None,
    book: str | None = None,
) -> None:
    """Emit the GHA matrix JSON.

    When single_chapter is set, emit a single-entry matrix for that chapter.
    When book is set (2-digit BB), emit one entry per chapter in that book.
    Otherwise emit the full bundled NT matrix.
    """
    if single_chapter:
        ch_id = str(single_chapter).zfill(5)
        vc = next((v for c, v in chapters if c == ch_id), 0)
        entries = [{"id": ch_id, "start": ch_id, "end": ch_id,
                    "label": _chapter_label(ch_id, vc)}]
        print(json.dumps(entries, ensure_ascii=False))
        print("# 1 matrix entry (single-chapter override)", file=sys.stderr)
        return

    if book:
        bb = str(book).zfill(2)
        book_chapters = [(ch, vc) for ch, vc in chapters if ch[:2] == bb]
        entries = [
            {"id": ch, "start": ch, "end": ch, "label": _chapter_label(ch, vc)}
            for ch, vc in book_chapters
        ]
        print(json.dumps(entries, ensure_ascii=False))
        print(f"# {len(entries)} matrix entries (book {bb})", file=sys.stderr)
        return

    entries = _build_matrix(chapters)
    bundled = sum(1 for e in entries if e["start"] != e["end"])
    print(json.dumps(entries, ensure_ascii=False))
    print(
        f"# {len(entries)} matrix entries "
        f"({bundled} bundled from {len(chapters)} chapters)",
        file=sys.stderr,
    )


def cmd_status(
    chapters: list[tuple[str, int]],
    edition: str,
    output_dir: Path,
) -> None:
    total_chapters = len(chapters)
    total_verses = sum(vc for _, vc in chapters)
    done_chapters = done_verses = 0

    for ch, vc in chapters:
        json_path = output_dir / f"SBLGNT-{edition}-{ch[:2]}-{ch[2:]}-manual.json"
        done = json_path.exists()
        status = "DONE   " if done else "PENDING"
        print(f"{status}  {ch}  {_chapter_name(ch)}")
        if done:
            done_chapters += 1
            done_verses += vc

    print(
        f"\n{done_chapters}/{total_chapters} chapters complete, "
        f"{done_verses}/{total_verses} verses done"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--json", action="store_true",
                   help="Emit GHA matrix JSON (<=256 entries; short chapters bundled)")
    p.add_argument("--status", action="store_true",
                   help="Show per-chapter completion status")
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml")
    p.add_argument("--edition", default=None,
                   help="Target edition ID, e.g. BSB (required for --status if not in --config)")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory containing LLM-REFINED chapter JSON files "
                        "(overrides config derivation)")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing SBLGNT.tsv (default: {_SOURCES_DIR})")
    p.add_argument("--chapter", default=None, metavar="BBCCC",
                   help="With --json: emit a single-entry matrix for this chapter")
    p.add_argument("--book", default=None, metavar="BB",
                   help="With --json: emit one entry per chapter for this book (e.g. 41 for Mark)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    chapters = _load_nt_chapters(args.sources_dir)

    if args.json:
        cmd_json(chapters, single_chapter=args.chapter, book=args.book)
        return

    if args.status:
        edition = args.edition
        output_dir = args.output_dir

        if args.config:
            raw = load_config(args.config)
            config = derive_paths(raw, output_suffix="LLM-REFINED")
            edition = edition or config.get("target_edition")
            output_dir = output_dir or config.get("output_dir")

        if not edition:
            raise SystemExit("error: --edition is required for --status")
        if not output_dir:
            raise SystemExit(
                "error: cannot derive output-dir — supply --output-dir or --config"
            )

        cmd_status(chapters, edition, Path(output_dir))
        return

    cmd_table(chapters)


if __name__ == "__main__":
    main()
