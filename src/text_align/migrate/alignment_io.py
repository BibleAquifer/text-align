"""Alignment JSON I/O utilities for alignment migration."""

import json
from pathlib import Path
from typing import Any

import regex as re


def load_alignment_json(path: Path) -> dict[str, Any]:
    """Load an alignment JSON file and return the parsed dict."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_alignment_json(alignment: dict[str, Any], path: Path) -> None:
    """Write alignment dict as JSON, one record per line, to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    json_string = json.dumps(alignment, ensure_ascii=False)
    # put "records" on its own line, then one record per line
    json_string = re.sub(r'"records"', r'\n"records"', json_string)
    # break between adjacent JSON objects (handles both old }}, and new }, separators)
    json_string = re.sub(r"(\}+), (\{)", r"\1,\n\2", json_string)
    path.write_text(json_string, encoding="utf-8")


def create_new_alignments(
    alignments: dict[str, Any],
    remap_target_ids: dict[str, str],
    corpus: str,
    edition: str,
    creator: str = "text-align",
) -> dict[str, Any]:
    """Build a new SB 0.4 alignment object by remapping target token IDs.

    *alignments* is the source alignment dict (parsed JSON); accepts both flat
    and SB 0.4 groups format.
    *remap_target_ids* maps old target IDs → new target IDs.
    *corpus* is the source corpus ID (e.g. ``"SBLGNT"`` or ``"WLCM"``).
    *edition* is the target edition ID (e.g. ``"NIrV"``).
    """
    # accept both flat and SB 0.4 groups input
    if "groups" in alignments:
        source_records = alignments["groups"][0]["records"]
    else:
        source_records = alignments["records"]

    used_new_targets: list[str] = []
    new_records: list[dict] = []

    for alignment in source_records:
        if not alignment.get("source") or not alignment.get("target"):
            continue
        remapped_ids: list[str] = []
        for target_id in alignment["target"]:
            if target_id in remap_target_ids:
                new_id = remap_target_ids[target_id]
                if new_id not in used_new_targets:
                    remapped_ids.append(new_id)
                    used_new_targets.append(new_id)
        target_ids = sorted(set(remapped_ids))
        if not target_ids:
            continue
        new_records.append({
            "source": alignment["source"],
            "target": target_ids,
        })

    return {
        "format": "alignment",
        "version": "0.4",
        "groups": [{
            "type": "translation",
            "meta": {"conformsTo": "0.4", "creator": creator},
            "documents": [
                {"docid": corpus, "scheme": "BCVWP"},
                {"docid": edition, "scheme": "BCVWP"},
            ],
            "roles": ["source", "target"],
            "records": new_records,
        }],
    }
