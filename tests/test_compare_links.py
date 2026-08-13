"""Tests for compare/links.py and compare/metrics.py — link extraction, id
reconciliation, and precision/recall/F1 arithmetic, using synthetic data
(no real Biblica/Clear-Bible checkout required).
"""

from text_align.burrito.AlignmentGroup import (
    AlignmentReference,
    AlignmentRecord,
    Document,
    Metadata,
)
from text_align.compare.links import build_target_id_map, record_links, translate_target_links, verse_links
from text_align.compare.metrics import compare_chapters, compare_verse

SRC_DOC = Document(docid="SBLGNT")
TGT_DOC = Document(docid="OENGB")


def _rec(source_ids: list[str], target_ids: list[str], rec_id: str | None = None) -> AlignmentRecord:
    meta = Metadata(id=rec_id or source_ids[0])
    return AlignmentRecord(
        meta=meta,
        references={
            "source": AlignmentReference(document=SRC_DOC, selectors=source_ids),
            "target": AlignmentReference(document=TGT_DOC, selectors=target_ids),
        },
    )


# ---------------------------------------------------------------------------
# record_links / verse_links
# ---------------------------------------------------------------------------

class TestRecordLinks:
    def test_one_to_one(self):
        rec = _rec(["40001001001"], ["40001001001"])
        assert record_links(rec) == {("40001001001", "40001001001")}

    def test_n_to_m_cross_product(self):
        rec = _rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])
        assert record_links(rec) == {
            ("40001001001", "40001001001"),
            ("40001001001", "40001001002"),
            ("40001001002", "40001001001"),
            ("40001001002", "40001001002"),
        }

    def test_secondary_source_included(self):
        # Our N:M records with a secondary source id still contribute their
        # full source_selectors to the cross product — primary and
        # secondary both count (per project decision).
        rec = _rec(["40001001001", "40001001002"], ["40001001003"])
        rec.meta.secondary = {"source": ["40001001001"]}
        assert record_links(rec) == {
            ("40001001001", "40001001003"),
            ("40001001002", "40001001003"),
        }


class TestVerseLinks:
    def test_union_across_records(self):
        recs = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(["40001001002"], ["40001001002"]),
        ]
        assert verse_links(recs) == {
            ("40001001001", "40001001001"),
            ("40001001002", "40001001002"),
        }

    def test_empty_records(self):
        assert verse_links([]) == set()


# ---------------------------------------------------------------------------
# id remap
# ---------------------------------------------------------------------------

class TestBuildTargetIdMap:
    def test_identical_verses_direct_map(self):
        import types

        def verse(words: dict[str, str]) -> "types.SimpleNamespace":
            return types.SimpleNamespace(
                words={tid: types.SimpleNamespace(id=tid, text=text) for tid, text in words.items()}
            )

        our = {"40001001": verse({"40001001001": "in", "40001001002": "the"})}
        their = {"40001001": verse({"40001001001": "in", "40001001002": "the"})}
        id_map = build_target_id_map(our, their)
        assert id_map == {"40001001001": "40001001001", "40001001002": "40001001002"}


class TestTranslateTargetLinks:
    def test_full_translation(self):
        links = {("40001001001", "b1"), ("40001001002", "b2")}
        id_map = {"b1": "o1", "b2": "o2"}
        translated, unmatched = translate_target_links(links, id_map)
        assert translated == {("40001001001", "o1"), ("40001001002", "o2")}
        assert unmatched == 0

    def test_unmatched_ids_dropped_and_counted(self):
        links = {("40001001001", "b1"), ("40001001002", "b_missing")}
        id_map = {"b1": "o1"}
        translated, unmatched = translate_target_links(links, id_map)
        assert translated == {("40001001001", "o1")}
        assert unmatched == 1


# ---------------------------------------------------------------------------
# compare_verse / compare_chapters
# ---------------------------------------------------------------------------

class TestCompareVerse:
    def test_perfect_agreement(self):
        our = [_rec(["40001001001"], ["o1"])]
        biblica = [_rec(["40001001001"], ["b1"])]
        id_map = {"b1": "o1"}
        c = compare_verse("40001001", our, biblica, id_map)
        assert c.precision == 1.0
        assert c.recall == 1.0
        assert c.f1 == 1.0
        assert c.agree_count == 1
        assert c.our_only == set()
        assert c.biblica_only == set()

    def test_partial_overlap(self):
        our = [_rec(["40001001001", "40001001002"], ["o1"])]
        biblica = [_rec(["40001001001"], ["b1"])]
        id_map = {"b1": "o1"}
        c = compare_verse("40001001", our, biblica, id_map)
        # our links: (s1,o1), (s2,o1); biblica links: (s1,o1)
        assert c.agree_count == 1
        assert c.our_link_count == 2
        assert c.biblica_link_count == 1
        assert c.precision == 0.5
        assert c.recall == 1.0

    def test_both_empty_is_trivially_perfect(self):
        c = compare_verse("40001001", [], [], {})
        assert c.precision == 1.0
        assert c.recall == 1.0
        assert c.f1 == 1.0
        assert c.agree_count == 0

    def test_no_overlap(self):
        our = [_rec(["40001001001"], ["o1"])]
        biblica = [_rec(["40001001002"], ["b1"])]
        id_map = {"b1": "o2"}
        c = compare_verse("40001001", our, biblica, id_map)
        assert c.precision == 0.0
        assert c.recall == 0.0
        assert c.f1 == 0.0

    def test_unmatched_biblica_target_id_excluded_from_agreement(self):
        our = [_rec(["40001001001"], ["o1"])]
        biblica = [_rec(["40001001001"], ["b_missing"])]
        c = compare_verse("40001001", our, biblica, {})
        assert c.unmatched_biblica_target_ids == 1
        assert c.biblica_link_count == 0
        # our-side link still counts, biblica side dropped -> recall trivially 1.0 (no biblica links)
        assert c.recall == 1.0
        assert c.precision == 0.0


class TestCompareChapters:
    def test_restricts_to_verse_intersection(self):
        our = {
            "40001001": [_rec(["40001001001"], ["o1"])],
            "40001002": [_rec(["40001002001"], ["o2"])],
        }
        biblica = {
            "40001001": [_rec(["40001001001"], ["b1"])],
            "40001003": [_rec(["40001003001"], ["b3"])],
        }
        id_map = {"b1": "o1"}
        comparisons = compare_chapters(our, biblica, id_map)
        assert [c.verse_id for c in comparisons] == ["40001001"]
