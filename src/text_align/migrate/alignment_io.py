"""Alignment JSON I/O utilities for alignment migration."""

import json
from pathlib import Path
from typing import Any

import regex as re


def load_alignment_json(path: Path) -> dict[str, Any]:
    """Load an alignment JSON file and return the parsed dict."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_source_alignment(
    corpus: str,
    edition: str,
    v04_dir: Path | None,
    v03_dir: Path | None,
) -> tuple[dict[str, Any], str] | None:
    """Load the source alignment for *corpus*/*edition*, preferring SB 0.4.

    Order:
    1. SB 0.4 chapter files ``{corpus}-{edition}-BB-CCC-manual.json`` in *v04_dir*
       (``*.retries.json`` sidecars never match), merged into one SB 0.4 dict
       with ``meta.nonEquivalent`` combined across chapters.
    2. The single SB 0.3 (or corpus-level 0.4) file ``{corpus}-{edition}-manual.json``
       in *v03_dir*.

    Returns ``(alignment_dict, description)`` or ``None`` when neither exists.
    """
    if v04_dir is not None and v04_dir.is_dir():
        paths = sorted(v04_dir.glob(f"{corpus}-{edition}-??-???-manual.json"))
        if paths:
            records: list[dict] = []
            neq_source: list[str] = []
            neq_target: list[str] = []
            for path in paths:
                group = load_alignment_json(path)["groups"][0]
                records.extend(group.get("records", []))
                neq = group.get("meta", {}).get("nonEquivalent", {})
                neq_source.extend(neq.get("source", []))
                neq_target.extend(neq.get("target", []))
            meta: dict[str, Any] = {}
            if neq_source or neq_target:
                meta["nonEquivalent"] = {"source": neq_source, "target": neq_target}
            merged = {"groups": [{"meta": meta, "records": records}]}
            return merged, f"SB 0.4, {len(paths)} chapter files from {v04_dir}"

    if v03_dir is not None:
        path = v03_dir / f"{corpus}-{edition}-manual.json"
        if path.exists():
            return load_alignment_json(path), f"SB 0.3 fallback, {path}"
    return None


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
    # accept both flat and SB 0.4 groups input; record meta (primary/secondary,
    # idiom, ...) and group nonEquivalent are only carried over from groups input
    is_v04 = "groups" in alignments
    if is_v04:
        source_records = alignments["groups"][0]["records"]
        source_neq = alignments["groups"][0].get("meta", {}).get("nonEquivalent", {})
    else:
        source_records = alignments["records"]
        source_neq = {}

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
        new_record: dict[str, Any] = {
            "source": alignment["source"],
            "target": target_ids,
        }
        if is_v04 and alignment.get("meta"):
            new_record["meta"] = alignment["meta"]
        new_records.append(new_record)

    group_meta: dict[str, Any] = {"conformsTo": "0.4", "creator": creator}
    neq_source = list(source_neq.get("source", []))
    neq_target = sorted({remap_target_ids[t] for t in source_neq.get("target", [])
                         if t in remap_target_ids})
    if neq_source or neq_target:
        group_meta["nonEquivalent"] = {"source": neq_source, "target": neq_target}

    return {
        "format": "alignment",
        "version": "0.4",
        "groups": [{
            "type": "translation",
            "meta": group_meta,
            "documents": [
                {"docid": corpus, "scheme": "BCVWP"},
                {"docid": edition, "scheme": "BCVWP"},
            ],
            "roles": ["source", "target"],
            "records": new_records,
        }],
    }
