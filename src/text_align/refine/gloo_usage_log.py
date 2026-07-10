"""Empirical per-model token-usage log used to calibrate retry cost estimates.

Every real Gloo call that returns a `usage` object (see `_call_gloo` in
`llm.py`) appends one line to `data/token_usage/{family}/{model}.jsonl`:
{"model": ..., "prompt_tokens": ..., "completion_tokens": ...}. This tree is
git-tracked (unlike `.cache/`) so that GHA runs — which start from a fresh
checkout — see the same historical data a local dev machine has
accumulated; nothing is computed or synced specially for GHA, it just reads
whatever is checked out on `main`.

Layout: one file per exact model, grouped into a directory per family (see
`model_family`) so an exact-model lookup is a single direct file read, and a
family-wide fallback is a glob over that model's family directory — no
family needs to be re-derived from filenames, since the directory itself
already partitions by family by construction.

`load_usage_ratio` computes completion_tokens / prompt_tokens (summed
across all matching samples, not averaged-of-ratios, so a few huge-verse
calls don't get outvoted by many tiny ones) for a specific model, falling
back to every sample in that model's family directory when the exact model
has no logged samples yet.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from text_align import ROOT

TOKEN_USAGE_DIR = ROOT / "data" / "token_usage"

# Tokens stripped when deriving a model's family from its name (see
# model_family). Covers known provider-name segments seen in Gloo model IDs
# (gloo-google-gemini-3.1-pro, gloo-anthropic-claude-opus-4.7, ...) and bare
# native-provider model strings (which have no prefix to strip at all, so
# this set doesn't need to grow for those).
_KNOWN_PROVIDER_TOKENS = {"gloo", "google", "anthropic", "openai"}

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def model_family(model: str) -> str:
    """Derive a coarse grouping key from a model string.

    Splits on '-' and '/' (the two separators seen across Gloo model IDs
    and OpenRouter "vendor/model-slug" strings), strips known provider-name
    tokens, and returns the first token left over. Requires no maintenance
    as new model *families* appear (only for genuinely new provider-name
    tokens that aren't also the family name, e.g. "meta" for Llama).
    """
    for tok in re.split(r"[-/]", model.lower()):
        if tok and tok not in _KNOWN_PROVIDER_TOKENS:
            return tok
    return "other"


def _sanitize_filename(name: str) -> str:
    return _UNSAFE_FILENAME_CHARS.sub("_", name)


def _model_path(model: str, base_dir: Path) -> Path:
    family = model_family(model)
    return base_dir / family / f"{_sanitize_filename(model)}.jsonl"


def append_usage(
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    base_dir: Path = TOKEN_USAGE_DIR,
) -> None:
    if not prompt_tokens or not completion_tokens:
        return
    path = _model_path(model, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }) + "\n")


def _load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _ratio(records: list[dict]) -> float | None:
    total_in = sum(r.get("prompt_tokens", 0) for r in records)
    total_out = sum(r.get("completion_tokens", 0) for r in records)
    if total_in <= 0:
        return None
    return total_out / total_in


def load_usage_ratio(model: str, base_dir: Path = TOKEN_USAGE_DIR) -> float | None:
    """completion/prompt token ratio for `model`, from real logged calls.

    Tries the exact model's own file first; if it doesn't exist or has no
    usable data, falls back to every sample in that model's family
    directory. Returns None if there's no data at all — for the model or
    its family — meaning the caller should fall back to its own
    non-empirical estimate.
    """
    exact_path = _model_path(model, base_dir)
    ratio = _ratio(_load_records(exact_path))
    if ratio is not None:
        return ratio

    family_dir = exact_path.parent
    if not family_dir.is_dir():
        return None
    family_records: list[dict] = []
    for path in family_dir.glob("*.jsonl"):
        family_records.extend(_load_records(path))
    return _ratio(family_records)
