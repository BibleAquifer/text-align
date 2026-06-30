"""TSV reading utilities for alignment migration."""

import csv
from pathlib import Path

import pandas as pd
import regex as re
from biblelib.word import BCVWPID, BCVID

from .models import MigrateTarget, MigrateVerse, y_or_n


def process_usfm_tsv(target_data_dir: Path | str, edition: str) -> dict[str, MigrateVerse]:
    """Read kathairo target TSVs and return a dict of BCV ID → MigrateVerse.

    Expects ``ot_{edition}.tsv`` and ``nt_{edition}.tsv`` under *target_data_dir*.
    Tokens with ``exclude=True`` are silently dropped (not included in verse.words).
    Optional columns ``id_range_end`` and ``source_verse_range_end`` are read when
    present; absent columns default to empty string on the resulting MigrateTarget.
    """
    target_data_dir = Path(target_data_dir)
    verses: dict[str, MigrateVerse] = {}
    for corpus in ("ot", "nt"):
        tsv_path = target_data_dir / f"{corpus}_{edition}.tsv"
        if not tsv_path.exists():
            print(f"TSV not found, skipping: {tsv_path}")
            continue
        print(f"Processing {tsv_path.name}")
        df = pd.read_csv(tsv_path, sep="\t", header=0, dtype=str, encoding="utf-8", keep_default_na=False, quoting=csv.QUOTE_NONE)
        for row in df.index:
            source_verse = BCVWPID(df["id"][row]).to_bcvid
            if source_verse not in verses:
                bcv = BCVID(source_verse)
                verses[source_verse] = MigrateVerse(
                    id=bcv.ID,
                    book=str(int(bcv.book_ID)),
                    chapter=str(int(bcv.chapter_ID)),
                    verse=str(int(bcv.verse_ID)),
                    usfm=bcv.to_usfm(),
                )
            word = MigrateTarget(
                id=df["id"][row],
                source_verse=df["source_verse"][row],
                text=df["text"][row],
                skip_space_after=y_or_n(df["skip_space_after"][row]),
                exclude=y_or_n(df["exclude"][row]),
                id_range_end=df["id_range_end"][row] if "id_range_end" in df.columns else "",
                source_verse_range_end=df["source_verse_range_end"][row] if "source_verse_range_end" in df.columns else "",
            )
            if "required" in df.columns:
                word.required = y_or_n(df["required"][row])
            # Propagate the verse-level source range end (take the maximum across
            # all tokens, including excluded ones — it's a verse-level property).
            if word.source_verse_range_end:
                verse = verses[source_verse]
                if word.source_verse_range_end > verse.source_verse_range_end:
                    verse.source_verse_range_end = word.source_verse_range_end
            if not word.exclude:
                verses[source_verse].words[df["id"][row]] = word
    return verses


def dump_verse_text(tokens: list[MigrateTarget]) -> str:
    """Return a lowercased, whitespace-normalised string of token texts."""
    verse_text = " ".join(token.text.lower() for token in tokens)
    verse_text = re.sub(r"\s+", " ", verse_text)
    return verse_text.strip()


def get_wordlist(tokens: list[MigrateTarget]) -> list[str]:
    """Return a list of token text strings (preserving case) for similarity encoding."""
    return [token.text for token in tokens]
