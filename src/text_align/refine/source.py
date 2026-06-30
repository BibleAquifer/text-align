"""Load SBLGNT / WLCM source TSVs into verse-keyed token lists for refine-alignment."""

from pathlib import Path

from biblelib.word import BCVWPID

from text_align.burrito.source import Source, SourceReader

from .util import _CORPUS_ID


def collect_source_verse_range(
    source_verses: dict[str, list[Source]],
    start_vid: str,
    end_vid: str,
) -> list[Source]:
    """Return all source tokens for verse IDs in the inclusive range [start_vid, end_vid].

    Verse IDs are 8-digit zero-padded BBCCCVVV strings; lexicographic comparison
    equals numeric ordering, so cross-chapter and cross-book ranges work correctly.
    Tokens from all matching verses are merged and returned sorted by token ID.
    """
    tokens = [t for vid, ts in source_verses.items() if start_vid <= vid <= end_vid for t in ts]
    return sorted(tokens, key=lambda t: t.id)


def load_source_verses(sources_dir: Path | str, corpus: str) -> dict[str, list[Source]]:
    """Load a source TSV and return a dict of BCV ID → ordered list of Source tokens.

    Uses the same BCV key format as ``process_usfm_tsv`` so source and target
    verse dicts can be looked up with the same key.

    Args:
        sources_dir: Directory containing SBLGNT.tsv and WLCM.tsv.
        corpus: ``"nt"`` for SBLGNT, ``"ot"`` for WLCM.
    """
    sources_dir = Path(sources_dir)
    filename = f"{_CORPUS_ID[corpus]}.tsv"
    reader = SourceReader(sources_dir / filename)

    verses: dict[str, list[Source]] = {}
    for token in reader.values():
        bcv = BCVWPID(token.id).to_bcvid
        verses.setdefault(bcv, []).append(token)

    # Ensure tokens are in canonical word-position order within each verse
    return {bcv: sorted(tokens, key=lambda t: t.id) for bcv, tokens in verses.items()}
