"""Rough $ cost estimation for retrying a set of verses via Gloo.

Not exact — this is a triage aid for the --include-suspect cost gate on
retry-alignment, not a billing reconciliation tool. Gloo-only: the primary
user of this tool accesses all cloud models through Gloo AI Studio, so there
is no rate source for other providers here. A non-Gloo provider (or a Gloo
model missing from the live catalog) means cost cannot be estimated.

Token counting uses tiktoken (cl100k_base) as a cross-model approximation —
it is not the actual tokenizer for Gemini/Claude/DeepSeek/etc., but for
English-dominant text it tracks real BPE tokenizers closely enough to be
useful, per multi-provider cost tools (e.g. LiteLLM) that use the same
fallback. It measures the *real* prompt text (via the same prompt-assembly
functions retry's actual resubmit path uses), not a rough word/char count, so
it captures per-verse prompt overhead accurately even where the underlying
tokenizer's absolute count would differ from Gemini's/Claude's own.

- Input tokens: counted against the real system+user prompt for the verse,
  built one verse at a time (the same shape as retry's individual resubmit
  path) — slightly overestimates vs. real multi-verse batching, which shares
  system-prompt overhead across verses in a batch. That's the safe direction
  for a spend gate.
- Output tokens: counted against the verse's *existing* alignment record
  JSON, since real output size can't be known without calling the LLM and a
  retry produces a similarly-shaped result. Floored at a minimum so a verse
  with sparse/no prior records doesn't estimate near-zero.

Rates: fetched live from Gloo's public, unauthenticated model catalog
(https://platform.ai.gloo.com/platform/v2/models), cached locally with a TTL
so a run doesn't require a network call every time, and falling back to a
stale cache (or "unknown") if the endpoint is unreachable.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from text_align.burrito.source import Source
from text_align.migrate.alignment_io import load_alignment_json

from .prompt import build_batch_message, build_system_prompt, detect_phenomena, infer_testament
from .source import collect_source_verse_range


_ENCODING_NAME = "cl100k_base"
_MIN_OUTPUT_TOKENS = 100
_GLOO_MODELS_URL = "https://platform.ai.gloo.com/platform/v2/models"

_encoding_cache: dict[str, Any] = {}


def _count_tokens(text: str) -> int:
    if _ENCODING_NAME not in _encoding_cache:
        import tiktoken
        _encoding_cache[_ENCODING_NAME] = tiktoken.get_encoding(_ENCODING_NAME)
    return len(_encoding_cache[_ENCODING_NAME].encode(text))


@dataclass
class CostEstimate:
    input_tokens: int
    output_tokens: int
    cost: float


def fetch_gloo_rates(
    cache_path: Path,
    max_age_hours: float = 24.0,
    timeout: float = 10.0,
) -> dict[str, dict[str, float]]:
    """Fetch current Gloo model pricing, keyed by model id (e.g. "gloo-deepseek-v4-pro").

    Uses a local JSON cache to avoid a network round-trip on every run. On any
    fetch failure (network error, non-200, malformed JSON), falls back to the
    stale cache if one exists, or {} if not — callers then report "cannot
    estimate" for gloo models rather than raising.
    """
    if cache_path.exists() and max_age_hours > 0:
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            age_hours = (time.time() - cached.get("fetched_at", 0)) / 3600
            if age_hours < max_age_hours:
                return cached.get("rates", {})
        except (json.JSONDecodeError, OSError):
            pass

    try:
        import requests
        resp = requests.get(_GLOO_MODELS_URL, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        rates: dict[str, dict[str, float]] = {}
        for entry in data.get("data", []):
            model_id = entry.get("id")
            pricing = entry.get("pricing") or {}
            in_rate = pricing.get("input", {}).get("rate_per_1m_tokens")
            out_rate = pricing.get("output", {}).get("rate_per_1m_tokens")
            if model_id and in_rate is not None and out_rate is not None:
                rates[model_id] = {
                    "input_per_1m": float(in_rate),
                    "output_per_1m": float(out_rate),
                }
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps({"fetched_at": time.time(), "rates": rates}, indent=2),
            encoding="utf-8",
        )
        return rates
    except Exception:
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding="utf-8")).get("rates", {})
            except (json.JSONDecodeError, OSError):
                pass
        return {}


def _load_records_by_verse(chapter_json_path: Path) -> dict[str, list[dict]]:
    data = load_alignment_json(chapter_json_path)
    groups = data.get("groups", [])
    if not groups:
        return {}
    by_verse: dict[str, list[dict]] = {}
    for rec in groups[0].get("records", []):
        tgt_ids = rec.get("target") or []
        src_ids = rec.get("source") or []
        vid = tgt_ids[0][:8] if tgt_ids else (src_ids[0][:8] if src_ids else None)
        if vid:
            by_verse.setdefault(vid, []).append(rec)
    return by_verse


def _estimate_tokens_for_verse(
    verse_id: str,
    source_verses: dict[str, list[Source]],
    target_verses: Any,
    target_language: str,
    corpus_id: str,
    existing_records: list[dict],
) -> tuple[int, int]:
    tgt_verse = target_verses.get(verse_id)
    tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
    if tgt_verse and tgt_verse.words:
        src_start = next(iter(tgt_verse.words.values())).source_verse
        src_end = tgt_verse.source_verse_range_end
        if src_end and src_end > src_start:
            src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
        else:
            src_tokens = source_verses.get(src_start, [])
    else:
        src_tokens = []

    verse_batch = [(verse_id, src_tokens, tgt_tokens, {})]
    testament = infer_testament(src_tokens)
    phenomena = detect_phenomena(src_tokens)
    system_msg = build_system_prompt(phenomena, target_language, testament=testament)
    user_msg, _ = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)
    input_tokens = _count_tokens(system_msg) + _count_tokens(user_msg)

    output_tokens = max(_MIN_OUTPUT_TOKENS, _count_tokens(json.dumps(existing_records)))

    return input_tokens, output_tokens


def estimate_retry_cost(
    verse_ids: list[str],
    chapter_paths: dict[str, Path],
    source_verses: dict[str, list[Source]],
    target_verses: Any,
    target_language: str,
    corpus_id: str,
    provider: str,
    model: str,
    gloo_rates: dict[str, dict[str, float]],
) -> CostEstimate | None:
    """Estimate total $ to retry verse_ids with provider/model, or None if the
    rate is unknown (non-Gloo provider, or model missing from the live catalog)."""
    if provider != "gloo":
        return None
    rate = gloo_rates.get(model)
    if not rate or rate.get("input_per_1m") is None or rate.get("output_per_1m") is None:
        return None
    input_rate, output_rate = rate["input_per_1m"], rate["output_per_1m"]

    records_cache: dict[str, dict[str, list[dict]]] = {}
    total_in = total_out = 0
    for vid in verse_ids:
        chapter_id = vid[:5]
        if chapter_id not in records_cache:
            path = chapter_paths.get(chapter_id)
            records_cache[chapter_id] = _load_records_by_verse(path) if path else {}
        existing = records_cache[chapter_id].get(vid, [])
        i, o = _estimate_tokens_for_verse(
            vid, source_verses, target_verses, target_language, corpus_id, existing,
        )
        total_in += i
        total_out += o

    cost = (total_in / 1_000_000) * input_rate + (total_out / 1_000_000) * output_rate
    return CostEstimate(input_tokens=total_in, output_tokens=total_out, cost=cost)
