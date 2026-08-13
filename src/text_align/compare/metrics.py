"""Per-verse and aggregate precision/recall/F1 between our alignment links and
Biblica's reference links, plus TSV/stdout reporting.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

from text_align.burrito.AlignmentGroup import AlignmentRecord

from .links import translate_target_links, verse_links


@dataclass
class VerseComparison:
    """Comparison result for one verse's links (agreement, ours-only, Biblica-only)."""

    verse_id: str
    our_link_count: int
    biblica_link_count: int
    agree_count: int
    precision: float
    recall: float
    f1: float
    our_only: set[tuple[str, str]] = field(default_factory=set)
    biblica_only: set[tuple[str, str]] = field(default_factory=set)
    unmatched_biblica_target_ids: int = 0


def _prf(agree: int, ours: int, theirs: int) -> tuple[float, float, float]:
    precision = 1.0 if ours == 0 else agree / ours
    recall = 1.0 if theirs == 0 else agree / theirs
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def compare_verse(
    verse_id: str,
    our_records: list[AlignmentRecord],
    biblica_records: list[AlignmentRecord],
    id_map: dict[str, str],
) -> VerseComparison:
    """Compare one verse's links: ours (primary+secondary) vs. Biblica's (translated
    into our target-id space via *id_map*)."""
    our = verse_links(our_records)
    biblica_raw = verse_links(biblica_records)
    biblica, unmatched = translate_target_links(biblica_raw, id_map)

    agree = our & biblica
    precision, recall, f1 = _prf(len(agree), len(our), len(biblica))
    return VerseComparison(
        verse_id=verse_id,
        our_link_count=len(our),
        biblica_link_count=len(biblica),
        agree_count=len(agree),
        precision=precision,
        recall=recall,
        f1=f1,
        our_only=our - biblica,
        biblica_only=biblica - our,
        unmatched_biblica_target_ids=unmatched,
    )


def compare_chapters(
    our_verse_records: dict[str, list[AlignmentRecord]],
    biblica_verse_records: dict[str, list[AlignmentRecord]],
    id_map: dict[str, str],
) -> list[VerseComparison]:
    """Compare every verse present in *both* readers' verse-record maps.

    Biblica's reference may not cover the same material we've aligned (or
    vice versa) — comparison scope is the intersection, not "every chapter
    we've generated".
    """
    shared_verses = sorted(set(our_verse_records) & set(biblica_verse_records))
    return [
        compare_verse(vid, our_verse_records[vid], biblica_verse_records[vid], id_map)
        for vid in shared_verses
    ]


def aggregate_prf(comparisons: list[VerseComparison]) -> tuple[float, float, float]:
    """Micro-averaged precision/recall/F1 across all compared verses."""
    agree = sum(c.agree_count for c in comparisons)
    ours = sum(c.our_link_count for c in comparisons)
    theirs = sum(c.biblica_link_count for c in comparisons)
    return _prf(agree, ours, theirs)


def _format_links(links: set[tuple[str, str]], cap: int = 6) -> str:
    shown = sorted(links)[:cap]
    text = ", ".join(f"{s}:{t}" for s, t in shown)
    if len(links) > cap:
        text += f", +{len(links) - cap} more"
    return text


_TSV_FIELDS = [
    "verse_id", "our_link_count", "biblica_link_count", "agree_count",
    "precision", "recall", "f1", "unmatched_biblica_target_ids",
    "our_only_links", "biblica_only_links",
]


def write_comparison_tsv(comparisons: list[VerseComparison], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_TSV_FIELDS, delimiter="\t")
        writer.writeheader()
        for c in comparisons:
            writer.writerow({
                "verse_id": c.verse_id,
                "our_link_count": c.our_link_count,
                "biblica_link_count": c.biblica_link_count,
                "agree_count": c.agree_count,
                "precision": f"{c.precision:.4f}",
                "recall": f"{c.recall:.4f}",
                "f1": f"{c.f1:.4f}",
                "unmatched_biblica_target_ids": c.unmatched_biblica_target_ids,
                "our_only_links": _format_links(c.our_only),
                "biblica_only_links": _format_links(c.biblica_only),
            })


def print_summary(
    comparisons: list[VerseComparison],
    our_only_verses: set[str],
    biblica_only_verses: set[str],
    tsv_path: Path,
) -> None:
    total = len(comparisons)
    if total == 0:
        print("No verses in common between our alignments and Biblica's reference.", file=sys.stderr)
        return
    precision, recall, f1 = aggregate_prf(comparisons)
    total_unmatched = sum(c.unmatched_biblica_target_ids for c in comparisons)
    print(f"compare-alignment — {total} verse(s) compared", file=sys.stderr)
    print(f"  precision={precision:.4f}  recall={recall:.4f}  f1={f1:.4f}", file=sys.stderr)
    if total_unmatched:
        print(
            f"  {total_unmatched} Biblica target id(s) had no match in our target TSV "
            "after diff-based id reconciliation (excluded from scoring, not from the run)",
            file=sys.stderr,
        )
    if our_only_verses:
        print(f"  {len(our_only_verses)} verse(s) we aligned but Biblica's reference doesn't cover", file=sys.stderr)
    if biblica_only_verses:
        print(f"  {len(biblica_only_verses)} verse(s) in Biblica's reference we haven't aligned yet", file=sys.stderr)
    worst = sorted(comparisons, key=lambda c: c.f1)[:10]
    print("  Lowest-F1 verses:", file=sys.stderr)
    for c in worst:
        print(f"    {c.verse_id}  f1={c.f1:.3f}  precision={c.precision:.3f}  recall={c.recall:.3f}", file=sys.stderr)
    print(f"  Full per-verse detail: {tsv_path}", file=sys.stderr)
