"""Coverage evaluation for alignment chapter JSON files.

Identifies verses where more than N source tokens appear in neither any record's
source list nor the chapter-level nonEquivalent.source set.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from text_align.migrate.alignment_io import load_alignment_json

from .util import _chapter_id_from_path


@dataclass
class CoverageStats:
    verse_id: str
    src_total: int
    src_covered: int
    uncovered_src_ids: list[str] = field(default_factory=list)

    @property
    def uncovered_count(self) -> int:
        return self.src_total - self.src_covered


@dataclass
class VerseRetrySpec:
    verse_id: str
    chapter_id: str  # BBCCC
    uncovered_src_ids: list[str]
    uncovered_count: int


def find_low_coverage_verses(
    chapter_json_path: Path,
    source_verses: dict[str, list],
    min_unaligned_src: int = 2,
    target_verses: Any | None = None,
) -> list[VerseRetrySpec]:
    """Return retry specs for verses with at least min_unaligned_src unaligned source tokens.

    A source token is considered covered if it appears in any record's source list
    or in the chapter-level nonEquivalent.source set.

    When target_verses is provided, iterates BSB verse IDs and resolves source tokens
    via the source_verse mapping — required for OT chapters with versification shifts.
    """
    data = load_alignment_json(chapter_json_path)
    groups = data.get("groups", [])
    if not groups:
        return []

    group = groups[0]
    records: list[dict] = group.get("records", [])
    neq_source: set[str] = set(group.get("meta", {}).get("nonEquivalent", {}).get("source", []))

    # Build covered set keyed by WLCM/SBLGNT source verse prefix
    covered_by_src_verse: dict[str, set[str]] = {}
    for rec in records:
        for sid in rec.get("source") or []:
            covered_by_src_verse.setdefault(sid[:8], set()).add(sid)
    for sid in neq_source:
        covered_by_src_verse.setdefault(sid[:8], set()).add(sid)

    chapter_id = _chapter_id_from_path(chapter_json_path)
    retry_specs: list[VerseRetrySpec] = []

    if target_verses is not None:
        # OT-aware path: iterate BSB verse IDs and look up source tokens via
        # the source_verse mapping to handle versification shifts correctly.
        for verse_id in sorted(v for v in target_verses if v[:5] == chapter_id):
            tgt_verse = target_verses.get(verse_id)
            if tgt_verse and tgt_verse.words:
                src_start = next(iter(tgt_verse.words.values())).source_verse
                src_end = tgt_verse.source_verse_range_end
                if src_end and src_end > src_start:
                    all_src_ids = {
                        t.id
                        for vid, tokens in source_verses.items()
                        if src_start <= vid <= src_end
                        for t in tokens
                    }
                    covered: set[str] = set()
                    for vid in (v for v in source_verses if src_start <= v <= src_end):
                        covered |= covered_by_src_verse.get(vid, set())
                else:
                    all_src_ids = {t.id for t in source_verses.get(src_start, [])}
                    covered = covered_by_src_verse.get(src_start, set())
            else:
                all_src_ids = {t.id for t in source_verses.get(verse_id, [])}
                covered = covered_by_src_verse.get(verse_id, set())
            uncovered = sorted(all_src_ids - covered)
            if len(uncovered) >= min_unaligned_src:
                retry_specs.append(VerseRetrySpec(
                    verse_id=verse_id,
                    chapter_id=chapter_id,
                    uncovered_src_ids=uncovered,
                    uncovered_count=len(uncovered),
                ))
    else:
        # NT path (or no target TSV): iterate source verse IDs directly.
        for verse_id in sorted(v for v in source_verses if v[:5] == chapter_id):
            all_src_ids = {t.id for t in source_verses[verse_id]}
            covered = covered_by_src_verse.get(verse_id, set())
            uncovered = sorted(all_src_ids - covered)
            if len(uncovered) >= min_unaligned_src:
                retry_specs.append(VerseRetrySpec(
                    verse_id=verse_id,
                    chapter_id=chapter_id,
                    uncovered_src_ids=uncovered,
                    uncovered_count=len(uncovered),
                ))

    return retry_specs
