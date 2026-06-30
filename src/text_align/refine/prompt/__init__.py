"""System prompt assembly and per-verse message formatting for refine-alignment.

Language configs are registered on import. The testament is auto-derived from
the source token IDs (book numbers 01-39 = OT, 40-66 = NT).
"""

from typing import Literal

from text_align.burrito.source import Source
from text_align.migrate.models import MigrateTarget

from .common import (
    LanguagePromptConfig,
    assemble_system_prompt,
    build_batch_message as _build_batch_message,
    build_verse_token_maps,
    format_verse_block as _format_verse_block,
    reverse_map_records,
)
from .nt.core import (
    detect_phenomena as _detect_phenomena_nt,
    get_nt_language_config,
    register_nt_language,
)
from .ot.core import (
    detect_phenomena as _detect_phenomena_ot,
    get_ot_language_config,
    register_ot_language,
)
from . import nt as _nt  # noqa: F401 — registers NT language configs
from . import ot as _ot  # noqa: F401 — registers OT language configs

Testament = Literal["nt", "ot"]


def infer_testament(source_tokens: list[Source]) -> Testament:
    """Derive testament from source token IDs (book 01-39 = OT, 40-66 = NT)."""
    if not source_tokens:
        return "nt"
    return "nt" if int(source_tokens[0].id[:2]) >= 40 else "ot"


def detect_phenomena(source_tokens: list[Source]) -> set[str]:
    """Detect alignment phenomena; testament is inferred from token IDs."""
    if infer_testament(source_tokens) == "nt":
        return _detect_phenomena_nt(source_tokens)
    return _detect_phenomena_ot(source_tokens)


def build_system_prompt(
    phenomena: set[str],
    target_language: str = "eng",
    testament: Testament = "nt",
) -> str:
    """Assemble the system prompt for the given language and testament."""
    if testament == "nt":
        config = get_nt_language_config(target_language)
    else:
        config = get_ot_language_config(target_language)
    return assemble_system_prompt(config, phenomena)


def format_verse_block(
    verse_id: str,
    source_tokens: list[Source],
    target_tokens: list[MigrateTarget],
    candidates: dict[str, list[dict]],
    target_language: str,
    source_corpus: str = "SBLGNT",
) -> tuple[str, dict[int, str], dict[int, str]]:
    return _format_verse_block(
        verse_id, source_tokens, target_tokens, candidates,
        target_language, source_corpus=source_corpus,
    )


def build_batch_message(
    verse_batch: list[tuple[str, list[Source], list[MigrateTarget], dict[str, list[dict]]]],
    target_language: str,
    source_corpus: str = "SBLGNT",
) -> tuple[str, dict[str, tuple[dict[int, str], dict[int, str]]]]:
    return _build_batch_message(verse_batch, target_language, source_corpus=source_corpus)


__all__ = [
    "LanguagePromptConfig",
    "Testament",
    "build_batch_message",
    "build_system_prompt",
    "build_verse_token_maps",
    "detect_phenomena",
    "format_verse_block",
    "get_nt_language_config",
    "get_ot_language_config",
    "infer_testament",
    "register_nt_language",
    "register_ot_language",
    "reverse_map_records",
]
