"""Semantic similarity scoring for alignment records using sentence-transformers.

Optional post-hoc signal: for each alignment record, embed the English glosses of
primary source tokens and the text of primary target tokens, then compute cosine
similarity.  Records below a configurable threshold contribute to a verse-level
semantic_low_sim_count flag.

Source-side text: gloss2 (bare core meaning) is the primary form; gloss is the
alternate.  When a record's primary tokens include any token where gloss2 differs
from gloss after normalisation, both forms are encoded and the higher similarity is
used, reducing false positives caused by overly terse gloss2 entries.  OT gloss2
punctuation is normalised: dots ("he.created" → "he created"), tildes (context-
elision markers), and asterisks are replaced with spaces.

The model is lazy-loaded and cached at the module level so repeated calls within
a session only pay the load cost once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from text_align.burrito.source import Source

_MODEL_CACHE: dict[str, Any] = {}

_CONTENT_POS: frozenset[str] = frozenset({"noun", "verb", "adj", "adjective"})


def _load_model(model_name: str) -> Any:
    if model_name not in _MODEL_CACHE:
        from sentence_transformers import SentenceTransformer
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name)
    return _MODEL_CACHE[model_name]


def _normalize_gloss_text(raw: str) -> str:
    """Normalise raw gloss text for embedding.

    Lowercases, replaces dots (OT word-join markers), tildes (context-elision
    markers), and asterisks with spaces; collapses runs of whitespace; strips ends.
    Target token text is already lowercased, so lowercasing here keeps both sides
    symmetric and avoids case-driven similarity penalties on proper nouns.
    """
    raw = raw.lower().replace(".", " ").replace("~", " ").replace("*", " ")
    return " ".join(raw.split())


def _resolve_gloss(token: Source) -> str:
    """Return primary gloss text: gloss2 if set, else gloss, normalised."""
    raw = token.gloss2 if token.gloss2 else token.gloss
    return _normalize_gloss_text(raw)


def _primary_src_text(
    src_ids: list[str],
    secondary_src: set[str],
    src_by_id: dict[str, Source],
) -> str:
    """Join primary gloss texts of primary (non-secondary) source tokens."""
    parts = [
        _resolve_gloss(src_by_id[sid])
        for sid in src_ids
        if sid not in secondary_src and sid in src_by_id
    ]
    return " ".join(p for p in parts if p)


def _alt_primary_src_text(
    src_ids: list[str],
    secondary_src: set[str],
    src_by_id: dict[str, Source],
) -> str | None:
    """Return alternate source text using gloss for all tokens, or None if identical to primary.

    The alternate is only useful when at least one primary token has a gloss2 that
    differs from its gloss after normalisation.  Returns None when the texts would
    be identical, avoiding redundant encoding.
    """
    primary_parts: list[str] = []
    alt_parts: list[str] = []
    has_alt = False
    for sid in src_ids:
        if sid in secondary_src or sid not in src_by_id:
            continue
        tok = src_by_id[sid]
        prim = _resolve_gloss(tok)
        alt = _normalize_gloss_text(tok.gloss) if tok.gloss else ""
        primary_parts.append(prim)
        alt_parts.append(alt if alt else prim)
        if alt and alt != prim:
            has_alt = True
    if not has_alt:
        return None
    alt_text = " ".join(p for p in alt_parts if p)
    primary_text = " ".join(p for p in primary_parts if p)
    return alt_text if alt_text != primary_text else None


def _primary_tgt_text(
    tgt_ids: list[str],
    secondary_tgt: set[str],
    tgt_text_by_id: dict[str, str],
) -> str:
    """Join texts of primary (non-secondary) target tokens."""
    parts = [
        tgt_text_by_id[tid]
        for tid in tgt_ids
        if tid not in secondary_tgt and tid in tgt_text_by_id
    ]
    return " ".join(p for p in parts if p)


def apply_semantic_scores(
    verse_scores: list,  # list[VerseScore]; typed as list to avoid circular import
    records_by_verse: dict[str, list[dict]],
    src_by_id: dict[str, Source],
    tgt_text_by_id: dict[str, str],
    model_name: str,
    threshold: float,
    chapter_id: str = "",
    record_details: list | None = None,
) -> None:
    """Score alignment records by semantic similarity and update VerseScore objects.

    For each record with primary tokens on both sides, embeds the resolved gloss of
    primary source tokens and the text of primary target tokens, then computes cosine
    similarity.  When a record's primary tokens include any gloss2/gloss pair that
    differ after normalisation, both source forms are encoded and the higher similarity
    is used to reduce false positives.  All unique source texts and all target texts
    across the chapter are encoded in two batch calls for efficiency.

    Increments semantic_low_sim_count on any verse where at least one record falls
    below threshold, and sets needs_retry=True on those verses.

    Prints a one-line summary to stderr showing pair count, similarity stats, and
    flagged record count (useful for threshold calibration).

    Mutates VerseScore objects in place; returns nothing.
    """
    import sys

    pairs: list[tuple[str, str]] = []      # (primary_src_text, tgt_text)
    pair_alt_src: list[str | None] = []    # alternate src text, or None when identical
    pair_verse_ids: list[str] = []
    pair_meta: list[dict] = []             # parallel to pairs; populated only when record_details provided

    for vs in verse_scores:
        for rec in records_by_verse.get(vs.verse_id, []):
            src_ids = rec.get("source") or []
            tgt_ids = rec.get("target") or []
            if not src_ids or not tgt_ids:
                continue
            if rec.get("meta", {}).get("is_idiom"):
                continue
            sec = rec.get("meta", {}).get("secondary", {})
            secondary_src = set(sec.get("source", []))
            secondary_tgt = set(sec.get("target", []))

            primary_src_tokens = [
                src_by_id[sid]
                for sid in src_ids
                if sid not in secondary_src and sid in src_by_id
            ]
            if not any(t.pos in _CONTENT_POS for t in primary_src_tokens):
                continue

            src_text = _primary_src_text(src_ids, secondary_src, src_by_id)
            alt_text = _alt_primary_src_text(src_ids, secondary_src, src_by_id)
            tgt_text = _primary_tgt_text(tgt_ids, secondary_tgt, tgt_text_by_id)

            if src_text and tgt_text:
                pairs.append((src_text, tgt_text))
                pair_alt_src.append(alt_text)
                pair_verse_ids.append(vs.verse_id)
                if record_details is not None:
                    primary_tgt_ids = [tid for tid in tgt_ids if tid not in secondary_tgt]
                    pair_meta.append({
                        "verse_id":      vs.verse_id,
                        "src_ids":       " ".join(sid for sid in src_ids if sid not in secondary_src),
                        "src_lemmas":    " ".join(t.lemma for t in primary_src_tokens if t.lemma),
                        "src_gloss":     src_text,
                        "src_gloss_alt": alt_text or "",
                        "tgt_ids":       " ".join(primary_tgt_ids),
                        "tgt_text":      tgt_text,
                        "similarity":    None,
                        "below_threshold": None,
                    })

    if not pairs:
        label = f"[{chapter_id}] " if chapter_id else ""
        print(f"  Semantic {label}0 pairs found — check --target-tsv-dir", file=sys.stderr)
        return

    # Encode all unique source texts in one batch (primary + non-None alternates).
    # Insertion-order dict gives stable indexing without sorting.
    src_text_to_idx: dict[str, int] = {}
    for i, (src_text, _) in enumerate(pairs):
        if src_text not in src_text_to_idx:
            src_text_to_idx[src_text] = len(src_text_to_idx)
        alt = pair_alt_src[i]
        if alt and alt not in src_text_to_idx:
            src_text_to_idx[alt] = len(src_text_to_idx)

    model = _load_model(model_name)
    src_embs = model.encode(
        list(src_text_to_idx.keys()),
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    tgt_embs = model.encode(
        [p[1] for p in pairs],
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    sims: list[float] = []
    for i, (src_text, _) in enumerate(pairs):
        sim = float((src_embs[src_text_to_idx[src_text]] * tgt_embs[i]).sum())
        alt = pair_alt_src[i]
        if alt:
            sim_alt = float((src_embs[src_text_to_idx[alt]] * tgt_embs[i]).sum())
            sim = max(sim, sim_alt)
        sims.append(sim)

    low_sim_by_verse: dict[str, int] = {}
    for verse_id, sim in zip(pair_verse_ids, sims):
        if sim < threshold:
            low_sim_by_verse[verse_id] = low_sim_by_verse.get(verse_id, 0) + 1

    if record_details is not None:
        for meta, sim in zip(pair_meta, sims):
            meta["similarity"] = f"{sim:.4f}"
            meta["below_threshold"] = sim < threshold
        record_details.extend(pair_meta)

    flagged_records = sum(low_sim_by_verse.values())
    label = f"[{chapter_id}] " if chapter_id else ""
    print(
        f"  Semantic {label}{len(pairs)} pairs, "
        f"sim min={min(sims):.3f} mean={sum(sims)/len(sims):.3f} max={max(sims):.3f}, "
        f"{flagged_records} record(s) below {threshold:.2f}",
        file=sys.stderr,
    )

    verse_by_id = {vs.verse_id: vs for vs in verse_scores}
    for verse_id, count in low_sim_by_verse.items():
        if verse_id in verse_by_id:
            vs = verse_by_id[verse_id]
            vs.semantic_low_sim_count = count
            vs.needs_retry = True
