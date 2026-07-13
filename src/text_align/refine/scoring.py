"""Alignment quality scoring for retry gating.

Computes a per-verse penalty score (0–1, higher = worse) from five signals:

  1. Weighted source-token coverage  (unaligned content words penalised more)
  2. Translation content-word coverage  (target gaps, requires target TSV)
  3. NEQ overuse  (NEQ rate above a per-language baseline)
  4. Token smearing  (N:M records where both sides are multi-primary, no idiom flag)
  5. Per-verse deviation from chapter mean  (second pass)

Verses with composite > config.retry_threshold are flagged needs_retry=True.

A separate, unconditional check (not part of the composite, like article_neq and
the semantic-similarity check) flags any verse where a source token tagged with
an ACAI entity (person/place/group/etc.) is neither aligned nor NEQ'd — see
acai_unaligned_count on VerseScore.

A further unconditional, *informational-only* check (does NOT set needs_retry,
unlike article_neq/semantic_low_sim/acai_unaligned) flags candidate 1:N
over-grouping ("smearing"): a single content-bearing source token (noun/verb/
adj) whose record claims 3+ primary target tokens, sitting next to a source
token (word position ±1) that is itself content-bearing/referential and is
genuinely unaligned (not NEQ'd, not covered by any record). This complements
signal 4, which only catches smearing when *both* sides of a record have
multiple independent primaries — a single wide-span record with one clean
source token slips past it. See smear_1toN_count / find_smear_1toN_records.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from text_align.burrito.source import Source
from text_align.migrate.alignment_io import load_alignment_json

from .scoring_stopwords import stopwords_for_lang
from .source import collect_source_verse_range
from .util import _chapter_id_from_path


# ---------------------------------------------------------------------------
# POS weights for signal 1
# ---------------------------------------------------------------------------

_POS_WEIGHTS: dict[str, float] = {
    "verb": 1.0,
    "noun": 1.0,
    "adj":  0.8,
    "adv":  0.8,
    "pron": 0.5,
    "prep": 0.4,
    "conj": 0.2,
    "part": 0.2,
    "ptcl": 0.2,
    "art":  0.1,
    "det":  0.1,
    "intj": 0.3,
    "num":  0.7,
}
_DEFAULT_WEIGHT = 0.6

# Source-side POS codes that are bound morphemes: they travel with a head word
# and should not be counted as independent primaries when detecting smearing.
# Prepositions are intentionally absent — prep+noun combos should be split.
_BOUND_SRC_POS: frozenset[str] = frozenset({
    "det",          # NT article (ὁ, ἡ, τό)
    "art",          # alias kept for safety
    "conj",         # NT conjunction
    "ptcl",         # NT particle
    "conjunction",  # OT conjunction
    "particle",     # OT particle
    "suffix",       # OT pronominal suffix (bound to host)
})

# Source-side POS codes treated as "content-bearing" for the smear_1toN check
# (the record's own single source token must be one of these to be a candidate).
_CONTENT_SRC_POS: frozenset[str] = frozenset({"noun", "verb", "adj", "adjective"})

# Source-side POS codes for the *neighbor* token: referential/content-bearing
# enough that its being left genuinely unaligned next to a wide-span record is
# meaningful. Bound morphemes (articles, conjunctions, prepositions) are
# routinely untranslated or absorbed and would make this check noisy if
# included — see conversation history / calibration against French and
# Portuguese reviewed corpora.
_MEANINGFUL_NEIGHBOR_POS: frozenset[str] = frozenset({
    "noun", "verb", "adj", "adjective", "pron", "num", "adv",
})


def _pos_weight(token: Source) -> float:
    return _POS_WEIGHTS.get(token.pos, _DEFAULT_WEIGHT)


# ---------------------------------------------------------------------------
# BCVWP word-position helpers (for adjacency check in signal 4)
# ---------------------------------------------------------------------------

def _word_pos(token_id: str) -> int:
    """Extract the word-position integer from a BCVWP token ID.

    Works for both NT (11-char: BB CCC VVV WWW) and OT (12-char: BB CCC VVV WWW P).
    Word position occupies characters 8–10 (0-indexed).
    """
    return int(token_id[8:11])


def _is_adjacent(token_ids: list[str]) -> bool:
    """True if all token IDs form a consecutive run by word position."""
    if len(token_ids) <= 1:
        return True
    positions = [_word_pos(tid) for tid in token_ids]
    return max(positions) - min(positions) == len(positions) - 1


def _neighbor_id(token_id: str, delta: int) -> str:
    """BCVWP ID for the source token one word-position before/after token_id.

    Preserves any trailing sub-word suffix (OT morph IDs) after the 3-digit
    word position at characters 8-10.
    """
    return f"{token_id[:8]}{_word_pos(token_id) + delta:03d}{token_id[11:]}"


def find_smear_1toN_records(
    records: list[dict],
    src_by_id: dict[str, Source],
    verse_neq_src: set[str],
    aligned_src: set[str],
) -> list[dict]:
    """Find records where one content-POS source token claims a wide primary
    target span next to a genuinely unaligned, meaningful-POS source neighbor.

    Informational-only over-grouping candidate detector (see module docstring).
    Returns a list of {"record": rec, "source_id": sid, "neighbor_id": nid}
    dicts, one per flagged record (at most one neighbor recorded per record,
    even if both sides qualify).
    """
    flagged: list[dict] = []
    for rec in records:
        src_ids = rec.get("source") or []
        tgt_ids = rec.get("target") or []
        sec = rec.get("meta", {}).get("secondary", {})
        sec_src = set(sec.get("source", []))
        sec_tgt = set(sec.get("target", []))
        prim_src = [s for s in src_ids if s not in sec_src]
        prim_tgt = [t for t in tgt_ids if t not in sec_tgt]
        if len(prim_src) != 1 or len(prim_tgt) < 3:
            continue
        sid = prim_src[0]
        src_tok = src_by_id.get(sid)
        if src_tok is None or src_tok.pos not in _CONTENT_SRC_POS:
            continue
        for delta in (-1, 1):
            nid = _neighbor_id(sid, delta)
            nbr_tok = src_by_id.get(nid)
            if nbr_tok is None or nbr_tok.pos not in _MEANINGFUL_NEIGHBOR_POS:
                continue
            if nid in verse_neq_src or nid in aligned_src:
                continue
            flagged.append({"record": rec, "source_id": sid, "neighbor_id": nid})
            break
    return flagged


# ---------------------------------------------------------------------------
# Configuration and result types
# ---------------------------------------------------------------------------

# Testament-aware fallback defaults for signal 3 (NEQ overuse), used when no
# explicit --neq-baseline / neq_baseline override is given. Measured empirically
# across eng/fra/por/spa editions: OT (Hebrew) alignments carry a genuinely higher
# natural NEQ rate than NT (Greek), roughly 2.2-2.6x, driven by construct chains,
# the accusative particle, pronominal suffixes, and waw-consecutive constructions
# with no target counterpart. Actual per-edition rates vary several-fold beyond
# this split based on translation style (e.g. RV09's literalism vs. a dynamic
# translation), so these are starting points, not a substitute for per-edition
# tuning via --neq-baseline / neq_baseline in the edition's YAML config.
NEQ_BASELINE_DEFAULTS: dict[str, float] = {"nt": 0.07, "ot": 0.16}


def default_neq_baseline(corpus: str | None) -> float:
    """Testament-aware fallback for ScoringConfig.neq_baseline.

    Falls back to the NT default when corpus is None/unrecognized.
    """
    return NEQ_BASELINE_DEFAULTS.get(corpus or "nt", NEQ_BASELINE_DEFAULTS["nt"])


def resolve_neq_baseline(args: Any) -> float:
    """Resolve the effective neq_baseline from CLI/YAML args for this run.

    Precedence: --neq-baseline-{nt,ot} (corpus-specific) > --neq-baseline
    (generic, same value for either testament) > testament-aware default.
    A single edition YAML config covers both --corpus nt and --corpus ot
    invocations, so the corpus-specific keys let one config file supply
    different values per testament.
    """
    corpus = getattr(args, "corpus", None)
    specific = getattr(args, f"neq_baseline_{corpus}", None) if corpus else None
    if specific is not None:
        return specific
    generic = getattr(args, "neq_baseline", None)
    if generic is not None:
        return generic
    return default_neq_baseline(corpus)


@dataclass
class ScoringConfig:
    # Signal weights (must sum to 1.0)
    w1: float = 0.25   # weighted source coverage
    w2: float = 0.20   # translation content coverage
    w3: float = 0.15   # NEQ overuse
    w4: float = 0.40   # token smearing
    w5: float = 0.00   # per-verse deviation (informational only; 0 = no retry influence)
    # Signal 3: NEQ baseline rate (expected natural NEQ rate for this corpus/lang)
    neq_baseline: float = 0.10
    # Signal 4: adjacency boost for same-verse consecutive-token smearing
    adjacency_multiplier: float = 1.5
    # Signal 4: standalone retry gate — forces needs_retry regardless of composite
    smear_forced_retry_threshold: float = 0.22
    # Signal 5: standard deviation multiplier for the outlier threshold
    deviation_k: float = 1.5
    # Retry gate
    retry_threshold: float = 0.25
    # Optional semantic similarity check (separate flag, not part of composite)
    semantic_model: str | None = None
    semantic_threshold: float = 0.35


@dataclass
class VerseScore:
    verse_id: str
    signal_1: float = 0.0
    signal_2: float = 0.0
    signal_3: float = 0.0
    signal_4: float = 0.0
    signal_5: float = 0.0
    composite: float = 0.0
    structural_errors: int = 0
    article_neq_count: int = 0
    semantic_low_sim_count: int = 0
    acai_unaligned_count: int = 0
    smear_1toN_count: int = 0
    smear_1toN_max_delta: float | None = None
    needs_retry: bool = False
    # Raw candidates from find_smear_1toN_records(), consumed by the optional
    # semantic-delta ranking pass (apply_smear_delta_scores). Not written to
    # the score-alignment TSV.
    smear_1toN_flagged: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core scoring functions
# ---------------------------------------------------------------------------

def score_verse(
    verse_id: str,
    records: list[dict],
    verse_neq_src: set[str],
    verse_neq_tgt: set[str],
    src_tokens: list[Source],
    tgt_token_ids: set[str],
    tgt_text_by_id: dict[str, str] | None,
    lang: str,
    config: ScoringConfig,
    acai_src_ids: set[str] | None = None,
) -> VerseScore:
    """Compute signals 1–4 for a single verse.

    Signal 5 (per-verse deviation) requires chapter context and is filled in
    by score_chapter() in the second pass.

    Args:
        verse_id:      8-char verse ID (BSB for OT, SBLGNT/BSB for NT).
        records:       Alignment records belonging to this verse.
        verse_neq_src: NEQ source token IDs for this verse (pre-filtered by caller).
        verse_neq_tgt: NEQ target token IDs for this verse (pre-filtered by caller).
        src_tokens:    Source tokens for this verse (from source TSV).
        tgt_token_ids: Target token IDs in this verse (from target TSV).
        tgt_text_by_id: token_id → lowercase word text; None skips signal 2.
        lang:          ISO 639-3 language code for stop-word lookup.
        config:        Scoring weights and thresholds.
        acai_src_ids:  Corpus-wide set of source token IDs tagged with an ACAI
                       entity (from build_word_entity_map()); None skips the check.
    """
    vs = VerseScore(verse_id=verse_id)

    # Definite articles in NEQ are always a mistake: articles must be primary
    # to "the"/pronoun/reinstated proper noun, or secondary to their head.
    src_by_id: dict[str, Source] = {t.id: t for t in src_tokens}
    vs.article_neq_count = sum(
        1 for sid in verse_neq_src
        if src_by_id.get(sid) is not None and src_by_id[sid].pos in {"art", "det"}
    )

    # -----------------------------------------------------------------------
    # Tier 1 — structural validity check (count errors, skip invalid records)
    # -----------------------------------------------------------------------
    valid_records: list[dict] = []
    for rec in records:
        src_ids = rec.get("source") or []
        tgt_ids = rec.get("target") or []
        sec = rec.get("meta", {}).get("secondary", {})
        sec_src = set(sec.get("source", []))
        sec_tgt = set(sec.get("target", []))

        is_invalid = (
            (src_ids and set(src_ids) <= sec_src) or  # all source are secondary
            (tgt_ids and set(tgt_ids) <= sec_tgt) or  # all target are secondary
            (not src_ids and not tgt_ids)              # both sides empty
        )
        if is_invalid:
            vs.structural_errors += 1
        else:
            valid_records.append(rec)

    # Sets of aligned token IDs
    aligned_src = {sid for rec in valid_records for sid in (rec.get("source") or [])}
    aligned_tgt = {tid for rec in valid_records for tid in (rec.get("target") or [])}

    # -----------------------------------------------------------------------
    # ACAI entity coverage — unconditional check, not part of the composite.
    # A source token tagged with an ACAI entity (person/place/group/etc.) that
    # is neither aligned nor NEQ'd is always a mistake.
    # -----------------------------------------------------------------------
    if acai_src_ids:
        verse_acai_ids = acai_src_ids & {t.id for t in src_tokens}
        vs.acai_unaligned_count = len(verse_acai_ids - aligned_src - verse_neq_src)

    # -----------------------------------------------------------------------
    # 1:N over-grouping candidates — unconditional, informational-only (does
    # not affect needs_retry). See module docstring and find_smear_1toN_records.
    # -----------------------------------------------------------------------
    vs.smear_1toN_flagged = find_smear_1toN_records(valid_records, src_by_id, verse_neq_src, aligned_src)
    vs.smear_1toN_count = len(vs.smear_1toN_flagged)

    # -----------------------------------------------------------------------
    # Signal 1 — weighted source coverage
    # -----------------------------------------------------------------------
    covered_src = aligned_src | verse_neq_src
    total_w = sum(_pos_weight(t) for t in src_tokens)
    uncov_w = sum(_pos_weight(t) for t in src_tokens if t.id not in covered_src)
    vs.signal_1 = uncov_w / total_w if total_w > 0 else 0.0

    # -----------------------------------------------------------------------
    # Signal 2 — translation content-word coverage (requires target TSV)
    # -----------------------------------------------------------------------
    if tgt_text_by_id is not None and tgt_token_ids:
        stopwords = stopwords_for_lang(lang)
        content_ids = {tid for tid in tgt_token_ids
                       if tgt_text_by_id.get(tid, "").lower() not in stopwords}
        covered_tgt = aligned_tgt | verse_neq_tgt
        unaligned_content = content_ids - covered_tgt
        vs.signal_2 = len(unaligned_content) / len(content_ids) if content_ids else 0.0

    # -----------------------------------------------------------------------
    # Signal 3 — NEQ overuse
    # -----------------------------------------------------------------------
    total_src = len(src_tokens)
    if total_src > 0 and config.neq_baseline < 1.0:
        raw_neq = len(verse_neq_src) / total_src
        vs.signal_3 = max(0.0, raw_neq - config.neq_baseline) / (1.0 - config.neq_baseline)

    # -----------------------------------------------------------------------
    # Signal 4 — token smearing (N:M non-idiom records with multi-primary both sides)
    # -----------------------------------------------------------------------
    smear_mass = 0.0
    total_mass = 0.0
    for rec in valid_records:
        src_ids = rec.get("source") or []
        tgt_ids = rec.get("target") or []
        if not src_ids or not tgt_ids:
            continue
        sec = rec.get("meta", {}).get("secondary", {})
        sec_src_set = set(sec.get("source", []))
        p_tgt = len(tgt_ids) - len(sec.get("target", []))
        is_idiom = bool(rec.get("meta", {}).get("is_idiom"))
        total_mass += len(src_ids) * len(tgt_ids)
        # Count only primary source tokens that are independent content units.
        # Articles, conjunctions, particles, and suffixes travel with a head
        # word and don't constitute a separate alignment record on their own,
        # so grouping them with their head is not smearing.
        primary_src_ids = [sid for sid in src_ids if sid not in sec_src_set]
        independent_p_src = sum(
            1 for sid in primary_src_ids
            if src_by_id.get(sid) is None
            or src_by_id[sid].pos not in _BOUND_SRC_POS
        )
        if independent_p_src > 1 and p_tgt > 1 and not is_idiom:
            mass = float(independent_p_src * p_tgt)
            if _is_adjacent(src_ids) and _is_adjacent(tgt_ids):
                mass *= config.adjacency_multiplier
            smear_mass += mass
    vs.signal_4 = smear_mass / total_mass if total_mass > 0 else 0.0

    return vs


def score_chapter(verse_scores: list[VerseScore], config: ScoringConfig) -> list[VerseScore]:
    """Second pass: compute signal 5 (deviation), final composite, and needs_retry flag.

    Mutates the VerseScore objects in place and returns the same list.
    """
    if not verse_scores:
        return verse_scores

    # Composite of signals 1–4 for each verse
    for vs in verse_scores:
        vs.composite = (
            config.w1 * vs.signal_1
            + config.w2 * vs.signal_2
            + config.w3 * vs.signal_3
            + config.w4 * vs.signal_4
        )

    # Signal 5: per-verse deviation from chapter mean
    composites = [vs.composite for vs in verse_scores]
    if len(composites) > 1:
        mean = sum(composites) / len(composites)
        std = math.sqrt(sum((c - mean) ** 2 for c in composites) / len(composites))
        threshold = mean + config.deviation_k * std
        for vs in verse_scores:
            if std > 0:
                vs.signal_5 = max(0.0, (vs.composite - threshold) / std)
            # else signal_5 stays 0.0

    # Final composite including signal 5, then set retry flag
    for vs in verse_scores:
        vs.composite = (
            config.w1 * vs.signal_1
            + config.w2 * vs.signal_2
            + config.w3 * vs.signal_3
            + config.w4 * vs.signal_4
            + config.w5 * vs.signal_5
        )
        vs.needs_retry = (
            vs.composite > config.retry_threshold
            or vs.article_neq_count > 0
            or vs.signal_4 > config.smear_forced_retry_threshold
            or vs.acai_unaligned_count > 0
        )

    return verse_scores


def find_suspect_verses(
    verse_scores: list[VerseScore],
    already_flagged: set[str],
    k: float,
) -> tuple[list[VerseScore], float]:
    """Verses whose composite exceeds a corpus-wide mean + k*stddev bar but are
    not already flagged (needs_retry, coverage-flagged, or otherwise excluded
    by the caller via already_flagged). Statistics are computed across all of
    verse_scores, so callers should pass every verse scored in the run, not a
    pre-filtered subset.

    Returns (suspects sorted by verse_id, the computed bar) — the bar is
    returned so callers can report it even when there are zero suspects.
    """
    if len(verse_scores) < 2:
        return [], (verse_scores[0].composite if verse_scores else 0.0)

    composites = [vs.composite for vs in verse_scores]
    mean = statistics.mean(composites)
    std = statistics.pstdev(composites)
    bar = mean + k * std

    suspects = [
        vs for vs in verse_scores
        if vs.verse_id not in already_flagged and vs.composite > bar
    ]
    suspects.sort(key=lambda vs: vs.verse_id)
    return suspects, bar


def score_chapter_file(
    chapter_json_path: Path,
    source_verses: dict[str, list[Source]],
    lang: str,
    config: ScoringConfig,
    target_verses: Any | None = None,
    record_details: list | None = None,
    acai_src_ids: set[str] | None = None,
) -> list[VerseScore]:
    """Score all verses in a chapter JSON file.

    Args:
        chapter_json_path: Path to a chapter alignment JSON file.
        source_verses:     BCV ID → list[Source] from load_source_verses().
        lang:              ISO 639-3 target language code.
        config:            Scoring configuration.
        target_verses:     BCV ID → MigrateVerse from process_usfm_tsv(), or None.
                           When None, signal 2 is skipped (scores 0.0).
        acai_src_ids:      Corpus-wide set of source token IDs tagged with an
                           ACAI entity (from build_word_entity_map()), or None
                           to skip the ACAI-unaligned check.
    """
    data = load_alignment_json(chapter_json_path)
    groups = data.get("groups", [])
    if not groups:
        return []

    group = groups[0]
    records: list[dict] = group.get("records", [])
    neq_meta = group.get("meta", {}).get("nonEquivalent", {})
    neq_source: set[str] = set(neq_meta.get("source", []))
    neq_target: set[str] = set(neq_meta.get("target", []))

    # Group records by verse.  When target_verses is available (handles OT
    # versification shifts), index by target token prefix (BSB verse ID) so the
    # keys match what the rest of the retry pipeline uses.  Fall back to source
    # token prefix (WLCM / SBLGNT) only when no target TSV is provided.
    records_by_verse: dict[str, list[dict]] = {}
    for rec in records:
        src_ids = rec.get("source") or []
        tgt_ids = rec.get("target") or []
        if target_verses is not None and tgt_ids:
            vid = tgt_ids[0][:8]
        elif src_ids:
            vid = src_ids[0][:8]
        elif tgt_ids:
            vid = tgt_ids[0][:8]
        else:
            continue
        records_by_verse.setdefault(vid, []).append(rec)

    chapter_id = _chapter_id_from_path(chapter_json_path)
    verse_scores: list[VerseScore] = []
    chapter_tgt_text: dict[str, str] = {}

    # When target_verses is available, iterate BSB verse IDs so OT versification
    # shifts (e.g. Jonah 2: WLCM 32002001 = BSB 1:17) don't bleed across chapters.
    if target_verses is not None:
        chapter_verse_ids = sorted(v for v in target_verses if v[:5] == chapter_id)
    else:
        chapter_verse_ids = sorted(v for v in source_verses if v[:5] == chapter_id)

    for verse_id in chapter_verse_ids:
        tgt_token_ids: set[str] = set()
        tgt_text_by_id: dict[str, str] | None = None
        verse_neq_src: set[str]
        verse_neq_tgt: set[str]

        if target_verses is not None:
            tgt_verse = target_verses.get(verse_id)
            if tgt_verse and tgt_verse.words:
                tgt_token_ids = set(tgt_verse.words.keys())
                tgt_text_by_id = {
                    tok_id: tok.text.lower()
                    for tok_id, tok in tgt_verse.words.items()
                }
                chapter_tgt_text.update(tgt_text_by_id)
                src_start = next(iter(tgt_verse.words.values())).source_verse
                src_end = tgt_verse.source_verse_range_end
                if src_end and src_end > src_start:
                    src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                    verse_neq_src = {sid for sid in neq_source if src_start <= sid[:8] <= src_end}
                else:
                    src_tokens = source_verses.get(src_start, [])
                    verse_neq_src = {sid for sid in neq_source if sid[:8] == src_start}
            else:
                src_tokens = source_verses.get(verse_id, [])
                verse_neq_src = {sid for sid in neq_source if sid[:8] == verse_id}
            verse_neq_tgt = {tid for tid in neq_target if tid[:8] == verse_id}
        else:
            src_tokens = source_verses.get(verse_id, [])
            verse_neq_src = {sid for sid in neq_source if sid[:8] == verse_id}
            verse_neq_tgt = {tid for tid in neq_target if tid[:8] == verse_id}

        verse_records = records_by_verse.get(verse_id, [])

        vs = score_verse(
            verse_id=verse_id,
            records=verse_records,
            verse_neq_src=verse_neq_src,
            verse_neq_tgt=verse_neq_tgt,
            src_tokens=src_tokens,
            tgt_token_ids=tgt_token_ids,
            tgt_text_by_id=tgt_text_by_id,
            lang=lang,
            config=config,
            acai_src_ids=acai_src_ids,
        )
        verse_scores.append(vs)

    verse_scores = score_chapter(verse_scores, config)

    if config.semantic_model:
        from .semantic import apply_semantic_scores, apply_smear_delta_scores
        chapter_src_by_id = {
            t.id: t
            for vid, tokens in source_verses.items()
            if vid[:5] == chapter_id
            for t in tokens
        }
        apply_semantic_scores(
            verse_scores,
            records_by_verse,
            chapter_src_by_id,
            chapter_tgt_text,
            config.semantic_model,
            config.semantic_threshold,
            chapter_id=chapter_id,
            record_details=record_details,
        )
        apply_smear_delta_scores(
            verse_scores,
            chapter_src_by_id,
            chapter_tgt_text,
            config.semantic_model,
        )

    return verse_scores
