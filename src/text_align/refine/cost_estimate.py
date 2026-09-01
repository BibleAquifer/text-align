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
- Output tokens: when real usage history exists for the model (see
  `gloo_usage_log.py`), estimated as input_tokens × the model's empirical
  completion/prompt ratio — this captures reasoning/thinking tokens that
  Gemini/Claude models routed through Gloo generate by default (billed as
  completion tokens) and that no static heuristic can predict without real
  data. Falls back to a same-family ratio, then finally to counting the
  verse's *existing* alignment record JSON (floored at a minimum) if there's
  no usage history at all yet for the model or its family — that proxy is
  then scaled by `_NO_DATA_OUTPUT_MULTIPLIER` (default 6x) since the raw
  proxy is known to undercount reasoning/thinking-heavy models badly.

Rates: fetched live from Gloo's public, unauthenticated model catalog
(https://platform.ai.gloo.com/platform/v2/models), cached locally with a TTL
so a run doesn't require a network call every time, and falling back to a
stale cache (or "unknown") if the endpoint is unreachable.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from text_align.burrito.source import Source
from text_align.migrate.alignment_io import load_alignment_json

from text_align import ROOT

from .gloo_usage_log import load_usage_ratio
from .prompt import build_batch_message, build_system_prompt, detect_phenomena, infer_testament
from .source import collect_source_verse_range


_ENCODING_NAME = "cl100k_base"
_MIN_OUTPUT_TOKENS = 100
_GLOO_MODELS_URL = "https://platform.ai.gloo.com/platform/v2/models"

# Applied to the existing-JSON-size fallback proxy when a model (and its
# family) has no logged usage history yet (see gloo_usage_log.py). The
# unmultiplied proxy measures the *shape* of a prior alignment result, not
# real generation size, and undercounts for any model that does
# reasoning/thinking by default. Calibrated against real completion/prompt
# ratios observed for gloo-deepseek-v4-pro (~2.27) and
# gloo-google-gemini-3.1-pro (~1.20, 13 samples) — this is a placeholder
# margin for models with no history at all, not a calibrated value for any
# specific model; it stops applying the moment real usage data exists for
# the model or its family.
_NO_DATA_OUTPUT_MULTIPLIER = 2.0

# Shared cache path — score-alignment and retry-alignment both read/write this
# same file, so a rate fetch by either tool warms the cache for the other.
DEFAULT_GLOO_RATES_CACHE = ROOT / ".cache" / "gloo_rates.json"

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
        key = os.environ.get("GLOO_API_KEY", "")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        resp = requests.get(_GLOO_MODELS_URL, headers=headers, timeout=timeout)
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
    model: str,
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

    ratio = load_usage_ratio(model)
    if ratio is not None:
        output_tokens = max(_MIN_OUTPUT_TOKENS, round(input_tokens * ratio))
    else:
        proxy_tokens = _count_tokens(json.dumps(existing_records))
        output_tokens = max(_MIN_OUTPUT_TOKENS, round(proxy_tokens * _NO_DATA_OUTPUT_MULTIPLIER))

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
            vid, source_verses, target_verses, target_language, corpus_id, existing, model,
        )
        total_in += i
        total_out += o

    cost = (total_in / 1_000_000) * input_rate + (total_out / 1_000_000) * output_rate
    return CostEstimate(input_tokens=total_in, output_tokens=total_out, cost=cost)
