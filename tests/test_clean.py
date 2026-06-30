"""Tests for refine/clean.py — three-pass alignment file cleaner."""

import json
from pathlib import Path

import pytest

from text_align.refine.clean import clean_chapter_file

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOURCE_IDS = frozenset({"40001001001", "40001001002", "40001001003"})
TARGET_IDS = frozenset({"40001001001", "40001001002", "40001001003"})


def _write_chapter(
    tmp_path: Path,
    records: list[dict],
    group_meta: dict | None = None,
) -> Path:
    path = tmp_path / "SBLGNT-TST-40-001-manual.json"
    group: dict = {"records": records}
    if group_meta:
        group["meta"] = group_meta
    path.write_text(json.dumps({"groups": [group]}), encoding="utf-8")
    return path


def _rec(src: list, tgt: list, meta: dict | None = None) -> dict:
    r: dict = {"source": src, "target": tgt}
    if meta:
        r["meta"] = meta
    return r


def _read_records(path: Path) -> list[dict]:
    return json.loads(path.read_text())["groups"][0]["records"]


# ---------------------------------------------------------------------------
# Pass 1 — structural validity
# ---------------------------------------------------------------------------

class TestPass1:
    def test_nosource_dropped(self, tmp_path):
        path = _write_chapter(tmp_path, [_rec([], ["40001001001"])])
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 1
        assert result.reasons.get("NOSOURCE") == 1
        assert result.changed

    def test_notarget_dropped(self, tmp_path):
        path = _write_chapter(tmp_path, [_rec(["40001001001"], [])])
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 1
        assert result.reasons.get("NOTARGET") == 1

    def test_missing_source_token_dropped(self, tmp_path):
        path = _write_chapter(tmp_path, [_rec(["40001001099"], ["40001001001"])])
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 1
        assert result.reasons.get("MISSINGSOURCE") == 1

    def test_missing_all_target_tokens_dropped(self, tmp_path):
        path = _write_chapter(tmp_path, [_rec(["40001001001"], ["40001001099"])])
        result = clean_chapter_file(path, SOURCE_IDS, TARGET_IDS)
        assert result.dropped == 1
        assert result.reasons.get("MISSINGTARGETALL") == 1

    def test_missing_some_target_tokens_dropped(self, tmp_path):
        path = _write_chapter(
            tmp_path,
            [_rec(["40001001001"], ["40001001001", "40001001099"])],
        )
        result = clean_chapter_file(path, SOURCE_IDS, TARGET_IDS)
        assert result.dropped == 1
        assert result.reasons.get("MISSINGTARGETSOME") == 1

    def test_target_check_skipped_when_no_target_ids(self, tmp_path):
        # A target token absent from TARGET_IDS should NOT be flagged when
        # target_ids is not passed.
        path = _write_chapter(tmp_path, [_rec(["40001001001"], ["40001001099"])])
        result = clean_chapter_file(path, SOURCE_IDS)  # no target_ids
        assert result.dropped == 0
        assert not result.changed

    def test_valid_record_unchanged(self, tmp_path):
        path = _write_chapter(tmp_path, [_rec(["40001001001"], ["40001001001"])])
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 0
        assert not result.changed

    def test_multiple_records_only_bad_ones_dropped(self, tmp_path):
        records = [
            _rec(["40001001001"], ["40001001001"]),  # good
            _rec([], ["40001001002"]),               # NOSOURCE
            _rec(["40001001002"], ["40001001002"]),  # good
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 1
        assert len(_read_records(path)) == 2


# ---------------------------------------------------------------------------
# Pass 2 — secondary-primary conflict repair
# ---------------------------------------------------------------------------

class TestPass2:
    def test_conflicting_secondary_removed_from_record(self, tmp_path):
        """A token primary in rec A but secondary in rec B is removed from B's source."""
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(
                ["40001001002", "40001001001"],
                ["40001001002"],
                meta={"secondary": {"source": ["40001001001"]}},
            ),
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.repaired == 1
        assert result.dropped == 0
        recs = _read_records(path)
        assert "40001001001" not in recs[1]["source"]

    def test_conflict_repair_preserves_other_secondary(self, tmp_path):
        """Repairing a conflict should leave unrelated secondary tokens intact."""
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(
                ["40001001002", "40001001001", "40001001003"],
                ["40001001002"],
                meta={"secondary": {"source": ["40001001001", "40001001003"]}},
            ),
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.repaired == 1
        recs = _read_records(path)
        assert "40001001001" not in recs[1]["source"]
        assert "40001001003" in recs[1]["source"]

    def test_conflict_drop_when_source_emptied(self, tmp_path):
        """If removing the conflicting token empties source, the record is dropped."""
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(
                ["40001001001"],
                ["40001001002"],
                meta={"secondary": {"source": ["40001001001"]}},
            ),
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 1
        assert result.reasons.get("SECONDARYCONFLICT_DROP") == 1
        assert len(_read_records(path)) == 1


# ---------------------------------------------------------------------------
# Pass 3 — cross-record duplicate detection
# ---------------------------------------------------------------------------

class TestPass3:
    def test_duplicate_source_both_records_dropped(self, tmp_path):
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(["40001001001"], ["40001001002"]),
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 2
        assert result.reasons.get("DUPLICATESOURCE") == 1
        assert _read_records(path) == []

    def test_duplicate_target_both_records_dropped(self, tmp_path):
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(["40001001002"], ["40001001001"]),
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 2
        assert result.reasons.get("DUPLICATETARGET") == 1
        assert _read_records(path) == []

    def test_non_duplicate_record_unaffected(self, tmp_path):
        records = [
            _rec(["40001001001"], ["40001001001"]),
            _rec(["40001001002"], ["40001001002"]),
            _rec(["40001001002"], ["40001001003"]),  # dup source with above
        ]
        path = _write_chapter(tmp_path, records)
        result = clean_chapter_file(path, SOURCE_IDS)
        assert result.dropped == 2
        recs = _read_records(path)
        assert len(recs) == 1
        assert recs[0]["source"] == ["40001001001"]


# ---------------------------------------------------------------------------
# Empty / no-groups edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_groups_returns_unchanged(self, tmp_path):
        path = tmp_path / "SBLGNT-TST-40-001-manual.json"
        path.write_text(json.dumps({"groups": []}), encoding="utf-8")
        result = clean_chapter_file(path, SOURCE_IDS)
        assert not result.changed
        assert result.dropped == 0

    def test_empty_records_list_unchanged(self, tmp_path):
        path = _write_chapter(tmp_path, [])
        result = clean_chapter_file(path, SOURCE_IDS)
        assert not result.changed
