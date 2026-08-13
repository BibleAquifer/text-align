"""Render a per-verse HTML diff of our alignment vs. Biblica's reference alignment.

Deliberately a standalone renderer rather than an extension of
``render/html.py``'s ``write_verse`` — that function's idiom/multi-primary
cell-merging logic is tuned for rendering a single alignment and isn't a good
graft point for a second, independently-tokenized alignment source. This
renders one row per source token instead: simpler, and sufficient for a
reviewer to see where the two systems agree or disagree.
"""

from __future__ import annotations

import html as htmlmod
from pathlib import Path

from text_align.burrito.AlignmentGroup import AlignmentRecord
from text_align.burrito.source import Source
from text_align.migrate.models import MigrateVerse

from .links import translate_target_links, verse_links
from .metrics import VerseComparison

_CSS = """
<style>
body { font-family: sans-serif; margin: 1.5em; }
table { border-collapse: collapse; margin-bottom: 1.5em; width: 100%; }
th, td { border: 1px solid #ccc; padding: 4px 8px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
tr.agree, .legend span.agree { background: #e6f4ea; }
tr.partial, .legend span.partial { background: #fff8e1; }
tr.ours_only, .legend span.ours_only { background: #e3f0ff; }
tr.biblica_only, .legend span.biblica_only { background: #fde8e8; }
tr.unaligned, .legend span.unaligned { background: #f5f5f5; color: #888; }
.verse-header { margin-top: 2em; }
.stats { color: #555; font-size: 0.9em; }
.legend span { display: inline-block; padding: 2px 8px; margin-right: 8px; border: 1px solid #ccc; }
.worst-f1 { border: 1px solid #ccc; padding: 0.75em 1.5em; background: #fafafa; }
.worst-f1 li { margin: 0.2em 0; }
</style>
"""

_LEGEND = (
    '<div class="legend">'
    '<span class="agree">agree</span>'
    '<span class="partial">partial</span>'
    '<span class="ours_only">ours only</span>'
    '<span class="biblica_only">Biblica only</span>'
    '<span class="unaligned">unaligned (both)</span>'
    "</div>"
)


def _esc(text: str) -> str:
    return htmlmod.escape(text or "")


def _verse_anchor(verse_id: str) -> str:
    return f"v-{verse_id}"


def _row_status(our_ids: set[str], biblica_ids: set[str]) -> str:
    if not our_ids and not biblica_ids:
        return "unaligned"
    if our_ids == biblica_ids:
        return "agree"
    if our_ids & biblica_ids:
        return "partial"
    if our_ids and not biblica_ids:
        return "ours_only"
    return "biblica_only"


def flatten_target_text(target_verses: dict[str, MigrateVerse]) -> dict[str, str]:
    """Flatten a BCV-keyed target-verse dict into a token id -> text lookup."""
    return {
        tid: word.text
        for verse in target_verses.values()
        for tid, word in verse.words.items()
    }


def render_verse_table(
    verse_id: str,
    comparison: VerseComparison,
    src_tokens: list[Source],
    our_records: list[AlignmentRecord],
    biblica_records: list[AlignmentRecord],
    id_map: dict[str, str],
    our_target_text: dict[str, str],
    biblica_target_text: dict[str, str],
) -> str:
    """Render one verse as an HTML section: one row per source token."""
    our_by_src: dict[str, set[str]] = {}
    for s, t in verse_links(our_records):
        our_by_src.setdefault(s, set()).add(t)

    biblica_raw_by_src: dict[str, set[str]] = {}
    for s, t in verse_links(biblica_records):
        biblica_raw_by_src.setdefault(s, set()).add(t)

    rows: list[str] = []
    for src in src_tokens:
        our_ids = our_by_src.get(src.id, set())
        biblica_raw_ids = biblica_raw_by_src.get(src.id, set())
        biblica_translated, _ = translate_target_links(
            {(src.id, t) for t in biblica_raw_ids}, id_map
        )
        biblica_ids = {t for _, t in biblica_translated}

        status = _row_status(our_ids, biblica_ids)
        our_text = ", ".join(our_target_text.get(t, f"[{t}]") for t in sorted(our_ids)) or "—"
        biblica_text = (
            ", ".join(biblica_target_text.get(t, f"[{t}]") for t in sorted(biblica_raw_ids)) or "—"
        )
        rows.append(
            f'<tr class="{status}">'
            f"<td>{_esc(src.id)}</td>"
            f"<td>{_esc(src.text)}</td>"
            f"<td>{_esc(src.gloss)}</td>"
            f"<td>{_esc(our_text)}</td>"
            f"<td>{_esc(biblica_text)}</td>"
            f"<td>{status}</td>"
            "</tr>"
        )

    stats = (
        f'<div class="stats">precision={comparison.precision:.3f} '
        f"recall={comparison.recall:.3f} f1={comparison.f1:.3f} "
        f"({comparison.agree_count}/{comparison.our_link_count} ours, "
        f"{comparison.agree_count}/{comparison.biblica_link_count} Biblica)</div>"
    )
    return (
        f'<h3 class="verse-header" id="{_verse_anchor(verse_id)}">{_esc(verse_id)}</h3>{stats}'
        "<table><tr><th>src id</th><th>src text</th><th>gloss</th>"
        "<th>ours</th><th>Biblica</th><th>status</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def render_worst_f1_list(comparisons: list[VerseComparison], n: int = 5) -> str:
    """Render a bulleted list of the *n* lowest-F1 verses, linking down to their sections."""
    worst = sorted(comparisons, key=lambda c: c.f1)[:n]
    items = "".join(
        f'<li><a href="#{_verse_anchor(c.verse_id)}">{_esc(c.verse_id)}</a> '
        f"— f1={c.f1:.3f} (precision={c.precision:.3f}, recall={c.recall:.3f})</li>"
        for c in worst
    )
    return f'<div class="worst-f1"><strong>Lowest-F1 verses:</strong><ul>{items}</ul></div>'


def write_comparison_html(
    sections: list[str],
    output: Path,
    title: str = "Alignment comparison",
    comparisons: list[VerseComparison] | None = None,
    worst_n: int = 5,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(f"<html>\n<head>\n<meta charset=\"utf-8\">\n<title>{_esc(title)}</title>\n{_CSS}</head>\n<body>\n")
        f.write(f"<h1>{_esc(title)}</h1>\n{_LEGEND}\n")
        if comparisons:
            f.write(render_worst_f1_list(comparisons, worst_n))
            f.write("\n")
        for section in sections:
            f.write(section)
            f.write("\n")
        f.write("</body>\n</html>\n")
