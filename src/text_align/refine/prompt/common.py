"""Shared infrastructure for language-aware prompt assembly.

Contains the LanguagePromptConfig dataclass, the generic prompt assembly
logic, and token-formatting utilities.  No registry lives here — each
testament (nt/, ot/) owns its own registry.
"""

from dataclasses import dataclass, field

from text_align.burrito.source import Source
from text_align.migrate.models import MigrateTarget


# ---------------------------------------------------------------------------
# Language config
# ---------------------------------------------------------------------------

@dataclass
class LanguagePromptConfig:
    """All prompt content and assembly rules for one target language."""

    language_code: str
    base_block: str
    conditional_blocks: dict[str, str]
    block_order: list[str]
    forced_inclusions: dict[str, set[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------

def assemble_system_prompt(config: LanguagePromptConfig, phenomena: set[str]) -> str:
    """Assemble the system prompt from the base block plus relevant conditional blocks.

    Args:
        config:     The registered LanguagePromptConfig for the target language.
        phenomena:  Tags returned by a testament-specific detect_phenomena().
    """
    expanded: set[str] = set(phenomena)
    for tag, forced in config.forced_inclusions.items():
        if tag in expanded:
            expanded |= forced

    blocks = [config.base_block]

    if expanded:
        active = [t for t in config.block_order if t in expanded]
        notice = (
            "The following constructions were identified in this verse batch. "
            "Specific guidelines for each are included below: "
            + ", ".join(active) + "."
        )
        blocks.append(notice)

    for tag in config.block_order:
        if tag in expanded:
            blocks.append(config.conditional_blocks[tag])

    return "\n\n---\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Token maps: local sequential numbers ↔ full token IDs
# ---------------------------------------------------------------------------

def build_verse_token_maps(
    source_tokens: list[Source],
    target_tokens: list[MigrateTarget],
) -> tuple[dict[int, str], dict[int, str]]:
    """Build local-number → full-ID maps for one verse (1-based).

    Returns (source_map, target_map).
    """
    source_map = {i + 1: t.id for i, t in enumerate(source_tokens)}
    target_map = {i + 1: t.id for i, t in enumerate(target_tokens)}
    return source_map, target_map


def reverse_map_records(
    records: list[dict],
    source_map: dict[int, str],
    target_map: dict[int, str],
) -> tuple[list[dict], list[str]]:
    """Convert local integer token numbers in LLM records back to full token IDs.

    Returns (mapped_records, error_messages).
    """
    errors: list[str] = []
    mapped: list[dict] = []

    def _lookup(nums: list, id_map: dict[int, str], side: str, label: str) -> list[str]:
        result: list[str] = []
        for n in nums:
            try:
                key = int(n)
            except (TypeError, ValueError):
                errors.append(f"{label}: {side} value {n!r} is not an integer")
                continue
            full_id = id_map.get(key)
            if full_id is None:
                errors.append(
                    f"{label}: {side} token #{key} out of range "
                    f"(verse has {len(id_map)} {side} token(s))"
                )
                continue
            result.append(full_id)
        return result

    for i, rec in enumerate(records):
        label = f"record {i + 1}"
        new_rec = dict(rec)
        new_rec["source"] = _lookup(rec.get("source") or [], source_map, "source", label)
        new_rec["target"] = _lookup(rec.get("target") or [], target_map, "target", label)

        meta = rec.get("meta") or {}
        secondary = meta.get("secondary") or {}
        if secondary:
            sec_src = _lookup(secondary.get("source") or [], source_map, "secondary.source", label)
            sec_tgt = _lookup(secondary.get("target") or [], target_map, "secondary.target", label)
            new_secondary: dict = {}
            if sec_src:
                new_secondary["source"] = sec_src
            if sec_tgt:
                new_secondary["target"] = sec_tgt
            new_meta = {k: v for k, v in meta.items() if k != "secondary"}
            if new_secondary:
                new_meta["secondary"] = new_secondary
            new_rec["meta"] = new_meta

        mapped.append(new_rec)

    return mapped, errors


# ---------------------------------------------------------------------------
# Per-verse message formatting
# ---------------------------------------------------------------------------

def _format_source_token(num: int, token: Source) -> str:
    if token.morph:
        return f"  {num}  {token.text}  {token.morph}"
    # morph absent (OT/WLCM): use pos as tag proxy, gloss for meaning context
    tag = token.pos or ""
    gloss = token.gloss or ""
    if tag and gloss:
        return f"  {num}  {token.text}  {tag}  {gloss}"
    if tag or gloss:
        return f"  {num}  {token.text}  {tag or gloss}"
    return f"  {num}  {token.text}"


def format_verse_block(
    verse_id: str,
    source_tokens: list[Source],
    target_tokens: list[MigrateTarget],
    candidates: dict[str, list[dict]],
    target_language: str,
    source_corpus: str = "SBLGNT",
) -> tuple[str, dict[int, str], dict[int, str]]:
    """Format one verse block using local sequential token numbers.

    Returns (block_text, source_map, target_map).
    """
    source_map, target_map = build_verse_token_maps(source_tokens, target_tokens)
    source_inv = {v: k for k, v in source_map.items()}
    target_inv = {v: k for k, v in target_map.items()}

    lines: list[str] = []

    # Detect whether source tokens span multiple source verses (merged-verse case,
    # e.g. BSB 3JN 1:14 = SBLGNT 3JN 1:14-15).  Token IDs are BBCCCVVVWW…;
    # the 8-char prefix BBCCCVVV is the source verse BCV.
    first_sv = source_tokens[0].id[:8] if source_tokens else ""
    last_sv = source_tokens[-1].id[:8] if source_tokens else ""

    def _sv_label(vid: str) -> str:
        """Return a chapter:verse label, omitting chapter when same as first_sv."""
        ch, v = int(vid[2:5]), int(vid[5:8])
        return f"{ch}:{v}" if int(first_sv[2:5]) != ch else str(v)

    if first_sv and last_sv and first_sv != last_sv:
        lines.append(
            f"--- VERSE {verse_id} "
            f"(source spans {source_corpus} {_sv_label(first_sv)}–{_sv_label(last_sv)}) ---"
        )
    else:
        lines.append(f"--- VERSE {verse_id} ---")
    lines.append("")

    lines.append(f"SOURCE TOKENS ({source_corpus}):")
    prev_sv = ""
    for num, token in zip(range(1, len(source_tokens) + 1), source_tokens):
        cur_sv = token.id[:8]
        if prev_sv and cur_sv != prev_sv:
            lines.append(f"  -- verse {_sv_label(cur_sv)} --")
        lines.append(_format_source_token(num, token))
        prev_sv = cur_sv
    lines.append("")

    lines.append("TARGET TOKENS:")
    for num, t in zip(range(1, len(target_tokens) + 1), target_tokens):
        lines.append(f"  {num}  {t.text}")
    lines.append("")

    if not candidates:
        return "\n".join(lines), source_map, target_map

    lines.append("ALIGNMENT CANDIDATES:")
    for source_type, records in candidates.items():
        lines.append(f"\n[{source_type}]")
        for rec in records:
            src_nums = [
                str(source_inv[sid])
                for sid in rec.get("source", [])
                if sid in source_inv
            ]
            tgt_nums = [
                str(target_inv[tid])
                for tid in rec.get("target", [])
                if tid in target_inv
            ]
            lines.append(f"  source: [{' '.join(src_nums)}]  target: [{' '.join(tgt_nums)}]")

    return "\n".join(lines), source_map, target_map


def build_batch_message(
    verse_batch: list[tuple[str, list[Source], list[MigrateTarget], dict[str, list[dict]]]],
    target_language: str,
    source_corpus: str = "SBLGNT",
) -> tuple[str, dict[str, tuple[dict[int, str], dict[int, str]]]]:
    """Concatenate verse blocks for a batch into a single user message.

    Returns (message_str, all_maps) where all_maps maps verse_id →
    (source_map, target_map).
    """
    blocks: list[str] = []
    all_maps: dict[str, tuple[dict[int, str], dict[int, str]]] = {}

    for vid, src, tgt, cands in verse_batch:
        block, source_map, target_map = format_verse_block(
            vid, src, tgt, cands, target_language, source_corpus=source_corpus,
        )
        blocks.append(block)
        all_maps[vid] = (source_map, target_map)

    return "\n\n".join(blocks), all_maps
