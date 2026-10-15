"""Shared utilities for refine-alignment tools."""

from __future__ import annotations

from pathlib import Path


def _chapter_id_from_path(path: Path) -> str:
    """Extract BBCCC chapter ID from a filename like SBLGNT-OENGB-66-007-manual.json."""
    parts = path.stem.split("-")
    return parts[-3] + parts[-2]


def _parse_id_list(value, width: int) -> frozenset[str]:
    """Parse a comma-separated string (or YAML list) of IDs, zero-padded to width."""
    if not value:
        return frozenset()
    items = value.split(",") if isinstance(value, str) else value
    return frozenset(str(i).strip().zfill(width) for i in items if str(i).strip())


# Canonical corpus ID for each corpus key used throughout the refine pipeline.
# "nt" → Greek NT source (SBLGNT); "ot" → Hebrew OT source (WLCM).
_CORPUS_ID: dict[str, str] = {"nt": "SBLGNT", "ot": "WLCM"}
_CORPUS_TESTAMENT: dict[str, str] = {v: k for k, v in _CORPUS_ID.items()}
