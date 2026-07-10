"""Tests for refine/gloo_usage_log.py — empirical token-usage log for cost estimation."""

from pathlib import Path

from text_align.refine.gloo_usage_log import append_usage, load_usage_ratio, model_family

# ---------------------------------------------------------------------------
# model_family
# ---------------------------------------------------------------------------


def test_model_family_gloo_prefixed():
    assert model_family("gloo-google-gemini-3.1-pro") == "gemini"
    assert model_family("gloo-google-gemini-2.5-flash") == "gemini"
    assert model_family("gloo-google-gemma-4-26b") == "gemma"
    assert model_family("gloo-anthropic-claude-opus-4.7") == "claude"
    assert model_family("gloo-anthropic-claude-sonnet-4.5") == "claude"
    assert model_family("gloo-deepseek-v4-pro") == "deepseek"
    assert model_family("gloo-deepseek-r1-0528") == "deepseek"
    assert model_family("gloo-openai-gpt-4.1-mini") == "gpt"
    assert model_family("gloo-openai-gpt-oss-120b") == "gpt"
    assert model_family("gloo-qwen-3.7-plus") == "qwen"
    assert model_family("gloo-kimi-k2-thinking") == "kimi"
    assert model_family("gloo-meta-llama-4-maverick") == "meta"
    assert model_family("gloo-minimax-m3") == "minimax"
    assert model_family("gloo-mistral-large-3") == "mistral"
    assert model_family("gloo-mistral-ministral-14b") == "mistral"
    assert model_family("gloo-xiaomi-mimo-v2.5") == "xiaomi"
    assert model_family("gloo-z-ai-glm-5.2") == "z"


def test_model_family_native_provider_strings():
    # No "gloo-" prefix at all — first token is already the family.
    assert model_family("claude-sonnet-4-6") == "claude"
    assert model_family("gpt-5.4-mini") == "gpt"
    assert model_family("gemini-2.0-flash-001") == "gemini"


def test_model_family_openrouter_slash_format():
    assert model_family("deepseek/deepseek-v4-pro") == "deepseek"
    assert model_family("qwen/qwen3-235b-a22b") == "qwen"


def test_model_family_unknown_falls_back_to_other():
    assert model_family("") == "other"
    assert model_family("gloo") == "other"


# ---------------------------------------------------------------------------
# append_usage / load_usage_ratio
# ---------------------------------------------------------------------------


def test_append_usage_writes_exact_model_file(tmp_path: Path):
    append_usage("gloo-google-gemini-3.1-pro", 1000, 2000, base_dir=tmp_path)
    expected = tmp_path / "gemini" / "gloo-google-gemini-3.1-pro.jsonl"
    assert expected.exists()
    assert '"prompt_tokens": 1000' in expected.read_text(encoding="utf-8")


def test_append_usage_skips_missing_token_counts(tmp_path: Path):
    append_usage("gloo-google-gemini-3.1-pro", None, 2000, base_dir=tmp_path)
    append_usage("gloo-google-gemini-3.1-pro", 1000, None, base_dir=tmp_path)
    append_usage("gloo-google-gemini-3.1-pro", 0, 0, base_dir=tmp_path)
    assert not (tmp_path / "gemini" / "gloo-google-gemini-3.1-pro.jsonl").exists()


def test_load_usage_ratio_exact_model_hit(tmp_path: Path):
    append_usage("gloo-google-gemini-3.1-pro", 1000, 2000, base_dir=tmp_path)
    append_usage("gloo-google-gemini-3.1-pro", 2000, 3000, base_dir=tmp_path)
    ratio = load_usage_ratio("gloo-google-gemini-3.1-pro", base_dir=tmp_path)
    assert ratio == (2000 + 3000) / (1000 + 2000)


def test_load_usage_ratio_falls_back_to_family(tmp_path: Path):
    # A sibling Gemini model has data; the exact model being queried does not.
    append_usage("gloo-google-gemini-2.5-flash", 1000, 4000, base_dir=tmp_path)
    ratio = load_usage_ratio("gloo-google-gemini-3.1-pro", base_dir=tmp_path)
    assert ratio == 4.0


def test_load_usage_ratio_family_fallback_aggregates_all_family_files(tmp_path: Path):
    append_usage("gloo-google-gemini-2.5-flash", 1000, 1000, base_dir=tmp_path)
    append_usage("gloo-google-gemini-3.5-flash", 1000, 3000, base_dir=tmp_path)
    ratio = load_usage_ratio("gloo-google-gemini-3.1-pro", base_dir=tmp_path)
    assert ratio == (1000 + 3000) / (1000 + 1000)


def test_load_usage_ratio_no_data_returns_none(tmp_path: Path):
    assert load_usage_ratio("gloo-google-gemini-3.1-pro", base_dir=tmp_path) is None


def test_load_usage_ratio_different_family_not_mixed_in(tmp_path: Path):
    append_usage("gloo-deepseek-v4-pro", 1000, 5000, base_dir=tmp_path)
    assert load_usage_ratio("gloo-google-gemini-3.1-pro", base_dir=tmp_path) is None
