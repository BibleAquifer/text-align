"""Tests for refine/scoring.py — composite alignment quality scorer."""

import types

import pytest

from text_align.refine.scoring import (
    ScoringConfig,
    VerseScore,
    _is_adjacent,
    _word_pos,
    score_chapter,
    score_verse,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VID = "40001001"  # Matthew 1:1
CONFIG = ScoringConfig()


def _src(token_id: str, pos: str = "noun") -> types.SimpleNamespace:
    """Minimal stand-in for a Source token: only .id and .pos are needed."""
    return types.SimpleNamespace(id=token_id, pos=pos)


def _tids(n: int) -> list[str]:
    """Return n sequential token IDs rooted at VID."""
    return [f"{VID}{str(i).zfill(3)}" for i in range(1, n + 1)]


def _rec(src: list, tgt: list, meta: dict | None = None) -> dict:
    r: dict = {"source": src, "target": tgt}
    if meta:
        r["meta"] = meta
    return r


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_word_pos_three_digit(self):
        assert _word_pos("40001001001") == 1
        assert _word_pos("40001001010") == 10
        assert _word_pos("40001001099") == 99

    def test_is_adjacent_single_token(self):
        assert _is_adjacent(["40001001001"])

    def test_is_adjacent_consecutive(self):
        assert _is_adjacent(["40001001001", "40001001002", "40001001003"])

    def test_is_adjacent_non_consecutive(self):
        assert not _is_adjacent(["40001001001", "40001001003"])

    def test_is_adjacent_two_tokens_gap(self):
        assert not _is_adjacent(["40001001002", "40001001005"])


# ---------------------------------------------------------------------------
# Signal 1 — weighted source coverage
# ---------------------------------------------------------------------------

class TestSignal1:
    def test_full_coverage_zero_penalty(self):
        src = [_src("40001001001", "noun")]
        records = [_rec(["40001001001"], ["40001001001"])]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_1 == 0.0

    def test_no_coverage_full_penalty(self):
        src = [_src("40001001001", "noun")]
        vs = score_verse(VID, [], set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_1 == 1.0

    def test_neq_token_counts_as_covered(self):
        src = [_src("40001001001", "noun")]
        vs = score_verse(VID, [], {"40001001001"}, set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_1 == 0.0

    def test_partial_coverage(self):
        src = [_src("40001001001", "noun"), _src("40001001002", "noun")]
        records = [_rec(["40001001001"], ["40001001001"])]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert 0.0 < vs.signal_1 < 1.0

    def test_article_penalized_less_than_verb(self):
        """Uncovered article contributes less signal_1 than uncovered verb.

        With two tokens (verb + article), each case covers one and leaves one
        uncovered.  The uncovered-article case must score lower because the
        article's POS weight (0.1) is much smaller than the verb's (1.0).
        """
        verb_id, art_id = "40001001001", "40001001002"
        src = [_src(verb_id, "verb"), _src(art_id, "art")]
        # article covered, verb uncovered
        vs_verb_uncov = score_verse(
            VID, [_rec([art_id], [art_id])], set(), set(), src, set(), None, "eng", CONFIG
        )
        # verb covered, article uncovered
        vs_art_uncov = score_verse(
            VID, [_rec([verb_id], [verb_id])], set(), set(), src, set(), None, "eng", CONFIG
        )
        assert vs_art_uncov.signal_1 < vs_verb_uncov.signal_1

    def test_empty_source_tokens_no_error(self):
        vs = score_verse(VID, [], set(), set(), [], set(), None, "eng", CONFIG)
        assert vs.signal_1 == 0.0


# ---------------------------------------------------------------------------
# Signal 2 — translation content-word coverage
# ---------------------------------------------------------------------------

class TestSignal2:
    def test_no_target_tsv_signal_zero(self):
        src = [_src("40001001001", "noun")]
        tgt_ids = {"40001001001"}
        vs = score_verse(VID, [], set(), set(), src, tgt_ids, None, "eng", CONFIG)
        assert vs.signal_2 == 0.0

    def test_unaligned_content_word_penalized(self):
        src = [_src("40001001001", "noun")]
        tgt_ids = {"40001001001"}
        tgt_text = {"40001001001": "resurrection"}
        vs = score_verse(VID, [], set(), set(), src, tgt_ids, tgt_text, "eng", CONFIG)
        assert vs.signal_2 == 1.0

    def test_aligned_content_word_no_penalty(self):
        src = [_src("40001001001", "noun")]
        records = [_rec(["40001001001"], ["40001001001"])]
        tgt_ids = {"40001001001"}
        tgt_text = {"40001001001": "resurrection"}
        vs = score_verse(VID, records, set(), set(), src, tgt_ids, tgt_text, "eng", CONFIG)
        assert vs.signal_2 == 0.0

    def test_stopword_not_penalized(self):
        src = [_src("40001001001", "noun")]
        tgt_ids = {"40001001001"}
        tgt_text = {"40001001001": "the"}  # English stopword
        vs = score_verse(VID, [], set(), set(), src, tgt_ids, tgt_text, "eng", CONFIG)
        assert vs.signal_2 == 0.0

    def test_neq_target_counts_as_covered(self):
        src = [_src("40001001001", "noun")]
        tgt_ids = {"40001001001"}
        tgt_text = {"40001001001": "resurrection"}
        vs = score_verse(VID, [], set(), {"40001001001"}, src, tgt_ids, tgt_text, "eng", CONFIG)
        assert vs.signal_2 == 0.0


# ---------------------------------------------------------------------------
# Signal 3 — NEQ overuse
# ---------------------------------------------------------------------------

class TestSignal3:
    def test_no_neq_zero_penalty(self):
        src = [_src(f"{VID}{str(i).zfill(3)}", "noun") for i in range(1, 6)]
        vs = score_verse(VID, [], set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_3 == 0.0

    def test_neq_at_baseline_zero_penalty(self):
        # Default baseline = 10%; 1 of 10 tokens NEQ'd = exactly 10%
        src = [_src(f"{VID}{str(i).zfill(3)}", "noun") for i in range(1, 11)]
        neq = {f"{VID}001"}
        vs = score_verse(VID, [], neq, set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_3 == pytest.approx(0.0)

    def test_neq_above_baseline_positive_penalty(self):
        src = [_src(f"{VID}{str(i).zfill(3)}", "noun") for i in range(1, 6)]
        neq = {f"{VID}001", f"{VID}002", f"{VID}003"}  # 3/5 = 60%
        vs = score_verse(VID, [], neq, set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_3 > 0.0


# ---------------------------------------------------------------------------
# Signal 4 — token smearing
# ---------------------------------------------------------------------------

class TestSignal4:
    def test_nm_non_idiom_record_penalized(self):
        """2-primary-src × 2-primary-tgt without is_idiom is smearing."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001"), _src("40001001002")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 > 0.0

    def test_idiom_flag_exempts_record(self):
        """is_idiom=True suppresses the smearing signal."""
        records = [_rec(
            ["40001001001", "40001001002"],
            ["40001001001", "40001001002"],
            meta={"is_idiom": True},
        )]
        src = [_src("40001001001"), _src("40001001002")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_one_to_many_not_smearing(self):
        """1 primary src, many primary tgt — only one side is multi, not smearing."""
        records = [_rec(["40001001001"], ["40001001001", "40001001002"])]
        src = [_src("40001001001")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_secondary_tokens_not_counted_as_primary(self):
        """A 2-src record where one src is secondary has only 1 primary — not smearing."""
        records = [_rec(
            ["40001001001", "40001001002"],
            ["40001001001", "40001001002"],
            meta={"secondary": {"source": ["40001001002"]}},
        )]
        src = [_src("40001001001"), _src("40001001002")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_adjacent_tokens_boost_smearing(self):
        """Consecutive token IDs on both sides trigger the adjacency multiplier."""
        # Adjacent: positions 1,2 on both sides
        rec_adj = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        # Non-adjacent source: positions 1,3
        rec_gap = [_rec(["40001001001", "40001001003"], ["40001001001", "40001001002"])]
        src = [_src("40001001001"), _src("40001001002"), _src("40001001003")]
        vs_adj = score_verse(VID, rec_adj, set(), set(), src, set(), None, "eng", CONFIG)
        vs_gap = score_verse(VID, rec_gap, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs_adj.signal_4 > vs_gap.signal_4

    # -- POS-aware bound-morpheme exclusions ----------------------------------

    def test_det_noun_not_smearing(self):
        """NT article (det) + noun grouped together is legitimate — not smearing."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001", "det"), _src("40001001002", "noun")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_conj_noun_not_smearing(self):
        """NT conjunction + noun grouped together is not smearing."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001", "conj"), _src("40001001002", "noun")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_prep_noun_still_smearing(self):
        """NT prep + noun grouped together is smearing — prepositions are independent."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001", "prep"), _src("40001001002", "noun")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 > 0.0

    def test_prep_det_noun_still_smearing(self):
        """NT prep+det+noun: det is excluded but prep+noun remain — still smearing."""
        records = [_rec(
            ["40001001001", "40001001002", "40001001003"],
            ["40001001001", "40001001002"],
        )]
        src = [
            _src("40001001001", "prep"),
            _src("40001001002", "det"),
            _src("40001001003", "noun"),
        ]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 > 0.0

    def test_ot_particle_not_smearing(self):
        """OT particle (full-word POS code) + noun is not smearing."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001", "particle"), _src("40001001002", "noun")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0

    def test_ot_suffix_not_smearing(self):
        """OT pronominal suffix grouped with its host noun is not smearing."""
        records = [_rec(["40001001001", "40001001002"], ["40001001001", "40001001002"])]
        src = [_src("40001001001", "noun"), _src("40001001002", "suffix")]
        vs = score_verse(VID, records, set(), set(), src, set(), None, "eng", CONFIG)
        assert vs.signal_4 == 0.0


# ---------------------------------------------------------------------------
# Article NEQ flag
# ---------------------------------------------------------------------------

class TestArticleNEQ:
    def test_article_in_neq_counted(self):
        src = [_src("40001001001", "art")]
        vs = score_verse(VID, [], {"40001001001"}, set(), src, set(), None, "eng", CONFIG)
        assert vs.article_neq_count == 1

    def test_det_in_neq_counted(self):
        src = [_src("40001001001", "det")]
        vs = score_verse(VID, [], {"40001001001"}, set(), src, set(), None, "eng", CONFIG)
        assert vs.article_neq_count == 1

    def test_noun_in_neq_not_counted(self):
        src = [_src("40001001001", "noun")]
        vs = score_verse(VID, [], {"40001001001"}, set(), src, set(), None, "eng", CONFIG)
        assert vs.article_neq_count == 0


# ---------------------------------------------------------------------------
# score_chapter — composite, signal 5, needs_retry
# ---------------------------------------------------------------------------

class TestScoreChapter:
    def test_composite_is_weighted_sum_of_signals(self):
        vs = VerseScore(verse_id=VID, signal_1=1.0, signal_2=0.0, signal_3=0.0, signal_4=0.0)
        score_chapter([vs], CONFIG)
        assert vs.composite == pytest.approx(CONFIG.w1 * 1.0)

    def test_high_smearing_forces_retry_below_composite_threshold(self):
        """signal_4 above smear_forced_retry_threshold triggers retry even if composite is low."""
        vs = VerseScore(verse_id=VID, signal_4=0.30)  # composite = w4*0.30 = 0.12, below 0.25
        score_chapter([vs], CONFIG)
        assert vs.composite < CONFIG.retry_threshold
        assert vs.needs_retry

    def test_low_smearing_does_not_force_retry(self):
        """signal_4 below smear_forced_retry_threshold does not force retry on its own."""
        vs = VerseScore(verse_id=VID, signal_4=0.20)
        score_chapter([vs], CONFIG)
        assert not vs.needs_retry

    def test_needs_retry_when_composite_above_threshold(self):
        config = ScoringConfig(w1=1.0, w2=0.0, w3=0.0, w4=0.0, retry_threshold=0.5)
        vs = VerseScore(verse_id=VID, signal_1=1.0)
        score_chapter([vs], config)
        assert vs.needs_retry

    def test_no_retry_when_composite_below_threshold(self):
        vs = VerseScore(verse_id=VID)  # all signals 0.0
        score_chapter([vs], CONFIG)
        assert not vs.needs_retry

    def test_article_neq_forces_retry_regardless_of_score(self):
        vs = VerseScore(verse_id=VID, article_neq_count=1)  # composite = 0
        score_chapter([vs], CONFIG)
        assert vs.needs_retry

    def test_signal_5_zero_for_single_verse(self):
        vs = VerseScore(verse_id=VID, signal_1=1.0)
        score_chapter([vs], CONFIG)
        assert vs.signal_5 == 0.0

    def test_signal_5_nonzero_for_outlier_verse(self):
        """A verse much worse than the chapter mean should get a non-zero signal 5."""
        vss = [
            VerseScore(verse_id=f"{VID[:6]}{str(i).zfill(3)}", signal_1=0.0)
            for i in range(1, 6)
        ]
        # Make the last verse an extreme outlier
        vss[-1].signal_1 = 1.0
        score_chapter(vss, CONFIG)
        assert vss[-1].signal_5 > 0.0
        for vs in vss[:-1]:
            assert vs.signal_5 == 0.0

    def test_all_verses_identical_signal5_zero(self):
        """When all verses have the same score, std=0 and signal 5 stays 0."""
        vss = [VerseScore(verse_id=f"{VID[:6]}{str(i).zfill(3)}", signal_1=0.5)
               for i in range(1, 4)]
        score_chapter(vss, CONFIG)
        for vs in vss:
            assert vs.signal_5 == 0.0
