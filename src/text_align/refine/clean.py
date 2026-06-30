"""Validate and repair chapter JSON alignment files in place.

Runs as a pre-pass before scoring so that scoring and render-alignment see
the same data.  The burrito Manager runs equivalent checks at render time;
by cleaning first, both pipelines agree.

Three-pass algorithm per chapter file:

  Pass 1 — per-record validity
    NOSOURCE / NOTARGET        empty source or target array
    MISSINGSOURCE              source token ID absent from corpus TSV
    MISSINGTARGETALL/SOME      target token ID absent from edition TSV

  Pass 2 — secondary-primary conflict repair
    SECONDARYCONFLICT          token is secondary in one record but primary in
                               another; the secondary reference is dropped.
                               If removing it empties the source array the
                               record is dropped (SECONDARYCONFLICT_DROP).

  Pass 3 — cross-record duplicate detection
    DUPLICATESOURCE            same source token in ≥2 records after repair
    DUPLICATETARGET            same target token in ≥2 records

Records flagged in pass 3 are all dropped (we cannot determine which is
correct; the verse is retried to produce a clean alignment).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from text_align.migrate.alignment_io import load_alignment_json, write_alignment_json


@dataclass
class CleanResult:
    """Summary of changes made to a single chapter file."""

    path: Path
    changed: bool = False
    dropped: int = 0    # total records removed
    repaired: int = 0   # records where secondary was trimmed but record kept
    reasons: dict[str, int] = field(default_factory=dict)

    def _tally(self, reason: str, n: int = 1) -> None:
        self.reasons[reason] = self.reasons.get(reason, 0) + n


def clean_chapter_file(
    path: Path,
    source_ids: frozenset[str],
    target_ids: frozenset[str] | None = None,
) -> CleanResult:
    """Validate and repair one chapter JSON file in place.

    source_ids: set of all valid source token IDs for this corpus.
    target_ids: set of all valid target token IDs, or None to skip target checks.

    Returns a CleanResult describing what changed.  The file is only rewritten
    when at least one record was dropped or repaired.
    """
    result = CleanResult(path=path)
    data = load_alignment_json(path)
    groups = data.get("groups", [])
    if not groups:
        return result

    group = groups[0]
    records: list[dict] = group.get("records", [])

    # ------------------------------------------------------------------
    # Pass 1: per-record structural validity
    # ------------------------------------------------------------------
    pass1: list[dict] = []
    for rec in records:
        src = rec.get("source") or []
        tgt = rec.get("target") or []
        if not src:
            result._tally("NOSOURCE"); result.dropped += 1; continue
        if not tgt:
            result._tally("NOTARGET"); result.dropped += 1; continue
        missing_src = [s for s in src if s not in source_ids]
        if missing_src:
            result._tally("MISSINGSOURCE"); result.dropped += 1; continue
        if target_ids is not None:
            missing_tgt = [t for t in tgt if t not in target_ids]
            if missing_tgt:
                reason = (
                    "MISSINGTARGETALL" if len(missing_tgt) == len(tgt)
                    else "MISSINGTARGETSOME"
                )
                result._tally(reason); result.dropped += 1; continue
        pass1.append(rec)

    # ------------------------------------------------------------------
    # Pass 2: secondary-primary conflict repair
    #
    # A token that is primary (non-secondary) in any record cannot also be
    # secondary in another record.  Build the full primary set first, then
    # strip conflicting secondaries.
    # ------------------------------------------------------------------
    primary_src: set[str] = set()
    for rec in pass1:
        sec_src: set[str] = set((rec.get("meta") or {}).get("secondary", {}).get("source") or [])
        for sid in (rec.get("source") or []):
            if sid not in sec_src:
                primary_src.add(sid)

    pass2: list[dict] = []
    for rec in pass1:
        meta = rec.get("meta") or {}
        sec = meta.get("secondary") or {}
        sec_src_list: list[str] = list(sec.get("source") or [])
        conflicts = [s for s in sec_src_list if s in primary_src]
        if not conflicts:
            pass2.append(rec)
            continue

        # Remove conflicting tokens from secondary.source and from source.
        new_sec_src = [s for s in sec_src_list if s not in conflicts]
        new_src = [s for s in (rec.get("source") or []) if s not in conflicts]
        if not new_src:
            result._tally("SECONDARYCONFLICT_DROP"); result.dropped += 1
            continue

        new_meta = {k: v for k, v in meta.items() if k != "secondary"}
        new_sec = {k: v for k, v in sec.items() if k != "source"}
        if new_sec_src:
            new_sec["source"] = new_sec_src
        if new_sec:
            new_meta["secondary"] = new_sec
        new_rec = {k: v for k, v in rec.items() if k not in ("source", "meta")}
        new_rec["source"] = new_src
        if new_meta:
            new_rec["meta"] = new_meta
        pass2.append(new_rec)
        result._tally("SECONDARYCONFLICT"); result.repaired += 1

    # ------------------------------------------------------------------
    # Pass 3: cross-record duplicate detection
    #
    # After conflict repair, any token still appearing in multiple records'
    # source/target arrays is a genuine duplicate.  Drop all offending records.
    # ------------------------------------------------------------------
    src_owners: dict[str, list[int]] = {}
    tgt_owners: dict[str, list[int]] = {}
    for i, rec in enumerate(pass2):
        for sid in (rec.get("source") or []):
            src_owners.setdefault(sid, []).append(i)
        for tid in (rec.get("target") or []):
            tgt_owners.setdefault(tid, []).append(i)

    bad: set[int] = set()
    n_dup_src = 0
    n_dup_tgt = 0
    for sid, idxs in src_owners.items():
        if len(idxs) > 1:
            n_dup_src += 1
            bad.update(idxs)
    for tid, idxs in tgt_owners.items():
        if len(idxs) > 1:
            n_dup_tgt += 1
            bad.update(idxs)
    if n_dup_src:
        result._tally("DUPLICATESOURCE", n_dup_src)
    if n_dup_tgt:
        result._tally("DUPLICATETARGET", n_dup_tgt)
    result.dropped += len(bad)

    final: list[dict] = [rec for i, rec in enumerate(pass2) if i not in bad]

    # ------------------------------------------------------------------
    # Write back only when something changed
    # ------------------------------------------------------------------
    result.changed = len(final) != len(records) or result.repaired > 0
    if result.changed:
        group["records"] = final
        write_alignment_json(data, path)

    return result


def run_clean_pass(
    chapter_files: list[Path],
    source_verses: dict,
    target_verses: dict | None = None,
) -> tuple[int, int, int]:
    """Run clean_chapter_file over all chapter files.

    Returns (files_changed, total_dropped, total_repaired).
    Callers are responsible for printing the summary.
    """
    source_ids: frozenset[str] = frozenset(
        t.id for tokens in source_verses.values() for t in tokens
    )
    target_ids: frozenset[str] | None = None
    if target_verses is not None:
        target_ids = frozenset(
            tok_id for verse in target_verses.values() for tok_id in verse.words
        )

    files_changed = total_dropped = total_repaired = 0
    for path in chapter_files:
        r = clean_chapter_file(path, source_ids, target_ids)
        if r.changed:
            files_changed += 1
            total_dropped += r.dropped
            total_repaired += r.repaired

    return files_changed, total_dropped, total_repaired
