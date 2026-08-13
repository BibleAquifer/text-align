"""Extract comparable source->target links from AlignmentRecords, and
reconcile target token ids between two independently-tokenized target TSVs.
"""

from text_align.burrito.AlignmentGroup import AlignmentRecord
from text_align.migrate.diff import build_remap


def record_links(rec: AlignmentRecord) -> set[tuple[str, str]]:
    """Return the (source_id, target_id) cross product implied by one record.

    Both primary and secondary source selectors count — Biblica's SB 0.3
    format has no primary/secondary distinction, so records on both sides
    are compared using their full ``source_selectors`` list.
    """
    return {(src, tgt) for src in rec.source_selectors for tgt in rec.target_selectors}


def verse_links(records: list[AlignmentRecord]) -> set[tuple[str, str]]:
    """Return the union of record_links() over a verse's records."""
    links: set[tuple[str, str]] = set()
    for rec in records:
        links |= record_links(rec)
    return links


def build_target_id_map(our_target_verses: dict, biblica_target_verses: dict) -> dict[str, str]:
    """Return a Biblica target token id -> our target token id map.

    Reuses ``migrate.diff.build_remap``, which already tolerates minor
    tokenization differences (punctuation/hyphen/apostrophe splitting) via
    word-level diffing, with a fast path when the two verses' text is
    identical (the common case). ``build_remap(source_verses, target_verses)``
    maps source-side ids to target-side ids for every verse present in both,
    so calling it with Biblica as "source" and ours as "target" gives the
    Biblica-id -> our-id direction directly.
    """
    return build_remap(biblica_target_verses, our_target_verses)


def translate_target_links(
    links: set[tuple[str, str]], id_map: dict[str, str],
) -> tuple[set[tuple[str, str]], int]:
    """Translate the target half of each (source_id, target_id) link through id_map.

    Returns (translated_links, unmatched_count). A link whose target id has
    no entry in id_map (the diff assigned it to an insert/delete rather than
    an equal span) is dropped from the returned set and counted as unmatched,
    rather than failing the whole verse.
    """
    translated: set[tuple[str, str]] = set()
    unmatched = 0
    for src, tgt in links:
        mapped = id_map.get(tgt)
        if mapped is None:
            unmatched += 1
            continue
        translated.add((src, mapped))
    return translated, unmatched
