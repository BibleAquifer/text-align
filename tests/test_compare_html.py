"""Tests for compare/compare_html.py — the lowest-F1 index list."""

from text_align.compare.compare_html import render_worst_f1_list
from text_align.compare.metrics import VerseComparison


def _cv(verse_id: str, f1: float) -> VerseComparison:
    return VerseComparison(
        verse_id=verse_id, our_link_count=1, biblica_link_count=1,
        agree_count=1, precision=f1, recall=f1, f1=f1,
    )


class TestRenderWorstF1List:
    def test_excludes_zero_scores(self):
        comparisons = [_cv("40001001", 0.0), _cv("40001002", 0.5), _cv("40001003", 0.0)]
        html = render_worst_f1_list(comparisons)
        assert "40001002" in html
        assert "40001001" not in html
        assert "40001003" not in html

    def test_sorts_ascending_and_caps_at_n(self):
        comparisons = [_cv(f"4000100{i}", score) for i, score in enumerate([0.9, 0.3, 0.6, 0.1, 0.7, 0.4], start=1)]
        html = render_worst_f1_list(comparisons, n=3)
        # lowest three non-zero scores: 0.1, 0.3, 0.4
        assert "f1=0.100" in html
        assert "f1=0.300" in html
        assert "f1=0.400" in html
        assert "f1=0.600" not in html

    def test_all_zero_yields_empty_list(self):
        comparisons = [_cv("40001001", 0.0), _cv("40001002", 0.0)]
        html = render_worst_f1_list(comparisons)
        assert "<ul></ul>" in html
