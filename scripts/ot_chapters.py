#!/usr/bin/env python3
"""OT chapter matrix and status reporter.

Usage:
    poetry run python scripts/ot_chapters.py
        Human-readable table of all OT chapters with verse counts.

    poetry run python scripts/ot_chapters.py --json --section law
        JSON array for GHA matrix input (<=256 entries; short chapters bundled).
        Each entry: {"id", "start", "end", "label"}.
        --section is required for --json unless --chapter or --book is given.
        Use --chapter to emit a single-entry matrix (for GHA re-run of one chapter).

    poetry run python scripts/ot_chapters.py --status --config BSB --section law
    poetry run python scripts/ot_chapters.py --status --edition BSB --output-dir PATH
        Per-chapter DONE/PENDING with summary line.

Sections:
    law       Gen–Deut   (books 01–05,  187 chapters)
    history   Josh–Esth  (books 06–17,  249 chapters)
    poetry    Job–Song   (books 18–22,  243 chapters)
    prophets  Isa–Mal    (books 23–39,  250 chapters)
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

# Inclusive book-number ranges for each canonical section
_SECTIONS: dict[str, tuple[str, str]] = {
    "law":      ("01", "05"),
    "history":  ("06", "17"),
    "poetry":   ("18", "22"),
    "prophets": ("23", "39"),
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_ot_chapters(
    sources_dir: Path,
    section: str | None = None,
) -> list[tuple[str, int]]:
    """Return sorted (chapter_id, verse_count) pairs from WLCM.tsv.

    chapter_id is a 5-char BBCCC string; verse_count is the number of
    distinct BBCCCVVV verse IDs in that chapter.
    If section is given, only chapters within that book range are returned.
    """
    tsv = sources_dir / "WLCM.tsv"
    book_lo = book_hi = None
    if section:
        lo, hi = _SECTIONS[section]
        book_lo, book_hi = lo, hi

    verses_by_chapter: dict[str, set[str]] = {}
    with tsv.open(encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            tid = line.split("\t", 1)[0]
            if not tid.startswith("o"):
                continue
            # o BBCCCVVVWWWP — positions 1:6 = chapter ID (BBCCC)
            if len(tid) < 9:
                continue
            ch_id = tid[1:6]
            if book_lo and not (book_lo <= ch_id[:2] <= book_hi):
                continue
            verses_by_chapter.setdefault(ch_id, set()).add(tid[1:9])
    return [(ch, len(vs)) for ch, vs in sorted(verses_by_chapter.items())]


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _chapter_name(chapter_id: str) -> str:
    book = _OT_BOOK_NAMES.get(chapter_id[:2], chapter_id[:2])
    return f"{book} {int(chapter_id[2:])}"


def _chapter_label(chapter_id: str, verse_count: int) -> str:
    return f"{_chapter_name(chapter_id)} ({verse_count}v)"


# ---------------------------------------------------------------------------
# Matrix building with short-chapter bundling
# ---------------------------------------------------------------------------

def _build_matrix(chapters: list[tuple[str, int]], max_entries: int = 256) -> list[dict]:
    """Return GHA matrix entries, bundling adjacent short chapters until len <= max_entries.

    Each entry has:
        id     — unique string key, e.g. "01001" or "31001-32001"
        start  — first chapter_id in the entry
        end    — last chapter_id in the entry (same as start for single chapters)
        label  — human-readable description for GHA job display
    """
    entries: list[list[tuple[str, int]]] = [[(ch, vc)] for ch, vc in chapters]

    while len(entries) > max_entries:
        single_entries = [(i, e[0][1]) for i, e in enumerate(entries) if len(e) == 1]
        if not single_entries:
            break
        idx, _ = min(single_entries, key=lambda x: x[1])
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
    section: str | None = None,
) -> None:
    """Emit the GHA matrix JSON.

    When single_chapter is set, emit a single-entry matrix for that chapter.
    When book is set (2-digit BB), emit one entry per chapter in that book.
    Otherwise emit the full bundled matrix for the given section.
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

    if len(chapters) > 256 and not section:
        raise SystemExit(
            "error: full OT is 929 chapters — use --section law/history/poetry/prophets"
        )

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
        json_path = output_dir / f"WLCM-{edition}-{ch[:2]}-{ch[2:]}-manual.json"
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
    p.add_argument("--section", choices=list(_SECTIONS), default=None,
                   help="Canonical section to process (required for --json full run)")
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml")
    p.add_argument("--edition", default=None,
                   help="Target edition ID, e.g. BSB (required for --status if not in --config)")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory containing LLM-REFINED chapter JSON files "
                        "(overrides config derivation)")
    p.add_argument("--sources-dir", default=_SOURCES_DIR, type=Path,
                   help=f"Directory containing WLCM.tsv (default: {_SOURCES_DIR})")
    p.add_argument("--chapter", default=None, metavar="BBCCC",
                   help="With --json: emit a single-entry matrix for this chapter")
    p.add_argument("--book", default=None, metavar="BB",
                   help="With --json: emit one entry per chapter for this book (e.g. 01 for Gen)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    chapters = _load_ot_chapters(args.sources_dir, section=args.section)

    if args.json:
        cmd_json(chapters, single_chapter=args.chapter, book=args.book,
                 section=args.section)
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
