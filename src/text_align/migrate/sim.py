"""sim-migrate: migrate alignments using multilingual sentence-transformer similarity.

Supports two model families:
* ``sentence-transformers/LaBSE`` (default) — broad language coverage via
  SentenceTransformer; produces a full similarity matrix for each verse.
* ``cointegrated/SONAR_200_text_encoder`` — token-by-token cosine similarity
  via M2M100Encoder; useful for languages not covered by LaBSE (e.g. Lingala).

CLI entry point: ``sim-migrate``
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import regex as re

from text_align.config import load_config_from_args, require
from text_align.stopwords import load_nltk_stopwords, load_stopwordsiso_stopwords

from .alignment_io import create_new_alignments, load_alignment_json, write_alignment_json
from .models import MigrateTarget
from .tsv import dump_verse_text, get_wordlist, process_usfm_tsv


# ---------------------------------------------------------------------------
# Similarity helpers — LaBSE
# ---------------------------------------------------------------------------

def locate_similar_words(similarities: Any) -> list[dict]:
    """Return src_idx/trg_idx/similarity records from a LaBSE similarity matrix."""
    results = []
    for src_idx, row in enumerate(similarities):
        best_score = float(row.max())
        best_trg = int(row.argmax())
        results.append({"src_idx": src_idx, "trg_idx": best_trg, "similarity": best_score})
    return results


# ---------------------------------------------------------------------------
# Similarity helpers — SONAR_200
# ---------------------------------------------------------------------------

def encode_embeddings(texts: list[str], tokenizer: Any, encoder: Any,
                      lang: str = "eng_Latn", norm: bool = False) -> Any:
    """Encode *texts* with SONAR mean-pooled embeddings."""
    import torch
    tokenizer.src_lang = lang
    with torch.inference_mode():
        batch = tokenizer(texts, return_tensors="pt", padding=True)
        seq_embs = encoder(**batch).last_hidden_state
        mask = batch.attention_mask
        mean_emb = (seq_embs * mask.unsqueeze(-1)).sum(1) / mask.unsqueeze(-1).sum(1)
        if norm:
            mean_emb = torch.nn.functional.normalize(mean_emb)
    return mean_emb


# module-level embedding caches (speed up repeated single-word encodings)
_src_cache: dict[str, Any] = {}
_trg_cache: dict[str, Any] = {}


def locate_similar_words_sonar(
    source_tokens: list[MigrateTarget],
    source_language: str,
    target_tokens: list[MigrateTarget],
    target_language: str,
    tokenizer: Any,
    encoder: Any,
) -> list[dict]:
    """Return similarity records using SONAR, caching embeddings by token text."""
    import torch
    results = []
    used_trg_idx: list[int] = []
    for src_idx, src_tok in enumerate(source_tokens):
        if src_tok.text not in _src_cache:
            _src_cache[src_tok.text] = encode_embeddings(
                [src_tok.text], tokenizer, encoder, lang=f"{source_language}_Latn"
            )
        src_emb = _src_cache[src_tok.text]
        best_score = 0.0
        best_trg = 0
        for trg_idx, trg_tok in enumerate(target_tokens):
            if trg_idx in used_trg_idx:
                continue
            if trg_tok.text not in _trg_cache:
                _trg_cache[trg_tok.text] = encode_embeddings(
                    [trg_tok.text], tokenizer, encoder, lang=f"{target_language}_Latn"
                )
            trg_emb = _trg_cache[trg_tok.text]
            score = float(torch.cosine_similarity(src_emb, trg_emb).item())
            if score > best_score:
                best_score = score
                best_trg = trg_idx
        used_trg_idx.append(best_trg)
        results.append({"src_idx": src_idx, "trg_idx": best_trg, "similarity": best_score})
    return results


# ---------------------------------------------------------------------------
# Remap building
# ---------------------------------------------------------------------------

def map_similar_words(
    similar_words: list[dict],
    remap: dict[str, str],
    source_tokens: list[MigrateTarget],
    target_tokens: list[MigrateTarget],
    source_stop_words: set[str],
    target_stop_words: set[str],
    remove_stopwords: bool = True,
    max_word_distance: int = 8,
    min_similarity: float = 0.7,
) -> dict[str, str]:
    """Merge *similar_words* matches into *remap*, applying distance/similarity filters."""
    for sw in similar_words:
        src_tok = source_tokens[sw["src_idx"]]
        trg_tok = target_tokens[sw["trg_idx"]]
        if remove_stopwords:
            if src_tok.text.lower() in source_stop_words:
                continue
            if trg_tok.text.lower() in target_stop_words:
                continue
        dist = abs(sw["src_idx"] - sw["trg_idx"])
        sim = sw["similarity"]
        if (dist < max_word_distance and sim >= min_similarity) or sim >= 0.9:
            remap[src_tok.id] = trg_tok.id
    return remap


def build_remap(
    source_verses: dict,
    target_verses: dict,
    model_name: str,
    source_language: str,
    target_language: str,
    remove_stopwords: bool = True,
    max_word_distance: int = 8,
    min_similarity: float = 0.7,
) -> dict[str, str]:
    """Build a source-token-ID → target-token-ID remap via sentence similarity."""
    is_labse = bool(re.search(r"LaBSE", model_name))
    is_sonar = bool(re.search(r"SONAR_200", model_name))

    if is_labse:
        from sentence_transformers import SentenceTransformer
        sim_model = SentenceTransformer(model_name)
        encoder = tokenizer = None
    elif is_sonar:
        import torch  # noqa: F401
        from transformers import AutoTokenizer
        from transformers.models.m2m_100.modeling_m2m_100 import M2M100Encoder
        sim_model = None
        encoder = M2M100Encoder.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        raise ValueError(f"Unknown similarity model: {model_name}")

    source_stop_words = load_nltk_stopwords(source_language)
    target_stop_words = load_stopwordsiso_stopwords(target_language)

    remap: dict[str, str] = {}
    for verse_id, target_verse in target_verses.items():
        if verse_id not in source_verses:
            print(f"Verse {verse_id} not in source TSV, skipping")
            continue

        source_tokens = list(source_verses[verse_id].words.values())
        target_tokens = list(target_verse.words.values())
        source_text = dump_verse_text(source_tokens)
        target_text = dump_verse_text(target_tokens)

        if source_text == target_text and len(source_tokens) == len(target_tokens):
            for src, trg in zip(source_tokens, target_tokens):
                remap[src.id] = trg.id
            continue

        if is_labse:
            assert sim_model is not None
            matrix = sim_model.similarity(
                sim_model.encode(get_wordlist(source_tokens)),
                sim_model.encode(get_wordlist(target_tokens)),
            )
            similar_words = locate_similar_words(matrix)
        else:
            assert encoder is not None and tokenizer is not None
            similar_words = locate_similar_words_sonar(
                source_tokens, source_language,
                target_tokens, target_language,
                tokenizer, encoder,
            )

        remap = map_similar_words(
            similar_words, remap,
            source_tokens, target_tokens,
            source_stop_words, target_stop_words,
            remove_stopwords=remove_stopwords,
            max_word_distance=max_word_distance,
            min_similarity=min_similarity,
        )

    return remap


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="SIM-MIGRATED")

    p = argparse.ArgumentParser(
        description=(
            "Migrate alignments from a reference translation to a similar translation "
            "using multilingual word-level similarity (LaBSE or SONAR_200)."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--source-edition", default=None,
                   help="Source (reference) edition ID, e.g. NIV11")
    p.add_argument("--target-edition", default=None,
                   help="Target (unaligned) edition ID, e.g. BONBV")
    p.add_argument("--source-language", default=None,
                   help="ISO 639-3 language code for the source edition, e.g. eng")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code for the target edition, e.g. spa")
    p.add_argument("--source-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<source>.tsv and nt_<source>.tsv")
    p.add_argument("--target-tsv-dir", default=None, type=Path,
                   help="Directory containing ot_<target>.tsv and nt_<target>.tsv")
    p.add_argument("--source-alignment-dir", default=None, type=Path,
                   help="Directory containing source alignment JSON files")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory to write migrated alignment JSON files")
    p.add_argument("--ot-corpus", default="WLCM",
                   help="OT source corpus ID (default: WLCM)")
    p.add_argument("--nt-corpus", default="SBLGNT",
                   help="NT source corpus ID (default: SBLGNT)")
    p.add_argument("--model", default="sentence-transformers/LaBSE",
                   help="Similarity model name (default: sentence-transformers/LaBSE)")
    p.add_argument("--max-word-distance", type=int, default=8,
                   help="Max index distance to accept a match (default: 8)")
    p.add_argument("--min-similarity", type=float, default=0.7,
                   help="Minimum similarity threshold (default: 0.7)")
    p.add_argument("--no-stopword-filter", dest="remove_stopwords",
                   action="store_false", default=True,
                   help="Disable stopword filtering (default: filtering is ON)")
    p.add_argument("--creator", default="text-align",
                   help="Creator string written into alignment meta (default: text-align)")
    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "source_edition", "target_edition", "source_language", "target_language",
            "source_tsv_dir", "target_tsv_dir", "source_alignment_dir", "output_dir")
    return args


def main() -> None:
    args = parse_args()

    print("Loading source TSV ...")
    source_verses = process_usfm_tsv(args.source_tsv_dir, args.source_edition)
    print("Loading target TSV ...")
    target_verses = process_usfm_tsv(args.target_tsv_dir, args.target_edition)

    print(f"Building remap with {args.model} ...")
    remap = build_remap(
        source_verses, target_verses,
        model_name=args.model,
        source_language=args.source_language,
        target_language=args.target_language,
        remove_stopwords=args.remove_stopwords,
        max_word_distance=args.max_word_distance,
        min_similarity=args.min_similarity,
    )
    print(f"Remap contains {len(remap)} token ID mappings.")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for corpus in (args.ot_corpus, args.nt_corpus):
        src_path = args.source_alignment_dir / f"{corpus}-{args.source_edition}-manual.json"
        if not src_path.exists():
            print(f"Source alignment not found, skipping: {src_path}")
            continue
        print(f"Migrating {src_path.name} ...")
        src_alignments = load_alignment_json(src_path)
        new_alignments = create_new_alignments(
            src_alignments, remap, corpus, args.target_edition, creator=args.creator
        )
        out_path = args.output_dir / f"{corpus}-{args.target_edition}-manual.json"
        write_alignment_json(new_alignments, out_path)
        print(f"  → {out_path}  ({len(new_alignments['groups'][0]['records'])} records)")


if __name__ == "__main__":
    main()
