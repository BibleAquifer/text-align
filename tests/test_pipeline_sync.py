"""Tests for text_align.pipeline_sync (token TSV split, pipeline.yaml lookup, alignment-map upsert)."""

from __future__ import annotations

from pathlib import Path

import pytest

from text_align.pipeline_sync import (
    MAP_COLUMNS,
    desired_map_row,
    find_aquifer_bible,
    split_token_tsv,
    sync_alignment_map,
    upsert_alignment_map,
)

HEADER = "id\tsource_verse\ttext\tskip_space_after\texclude\tid_range_end\tsource_verse_range_end\trequired\n"


def _row(book: int, n: int = 1) -> str:
    return f"{book:02d}001001{n:03d}\t{book:02d}001001\tw{book}\t\t\t\t\ty\n"


def _token(tmp: Path, books: list[int]) -> Path:
    p = tmp / "token_X.tsv"
    p.write_text(HEADER + "".join(_row(b) for b in books), encoding="utf-8", newline="")
    return p


# ---- split ----------------------------------------------------------------

def test_split_by_testament(tmp_path):
    tok = _token(tmp_path, [1, 39, 40, 66])
    out = tmp_path / "out"
    res = split_token_tsv(tok, out, "X")
    assert dict(res.files) == {"ot_X.tsv": "written", "nt_X.tsv": "written"}
    ot = (out / "ot_X.tsv").read_text().splitlines()
    nt = (out / "nt_X.tsv").read_text().splitlines()
    assert ot[0] == nt[0] == HEADER.strip()
    assert [r[:2] for r in ot[1:]] == ["01", "39"]
    assert [r[:2] for r in nt[1:]] == ["40", "66"]


def test_split_nt_only_writes_no_ot_file(tmp_path):
    tok = _token(tmp_path, [40, 41])
    out = tmp_path / "out"
    res = split_token_tsv(tok, out, "X")
    assert dict(res.files)["ot_X.tsv"] == "skipped-empty"
    assert not (out / "ot_X.tsv").exists()
    assert (out / "nt_X.tsv").exists()


def test_split_idempotent_and_conflict(tmp_path):
    tok = _token(tmp_path, [1, 40])
    out = tmp_path / "out"
    split_token_tsv(tok, out, "X")
    assert dict(split_token_tsv(tok, out, "X").files) == {"ot_X.tsv": "unchanged", "nt_X.tsv": "unchanged"}

    # an edit to the existing NT file is a conflict; nothing is written
    (out / "nt_X.tsv").write_text("edited\n")
    tok2 = _token(tmp_path, [1, 40, 41])
    res = split_token_tsv(tok2, out, "X")
    assert res.conflicts == ["nt_X.tsv"]
    assert (out / "nt_X.tsv").read_text() == "edited\n"
    assert len((out / "ot_X.tsv").read_text().splitlines()) == 2  # OT not rewritten either

    res = split_token_tsv(tok2, out, "X", force=True)
    assert dict(res.files)["nt_X.tsv"] == "overwritten"
    assert len((out / "nt_X.tsv").read_text().splitlines()) == 3


def test_split_normalizes_crlf_and_ignores_eol_in_compare(tmp_path):
    tok = tmp_path / "token_X.tsv"
    tok.write_bytes((HEADER + _row(1) + _row(40)).replace("\n", "\r\n").encode())
    out = tmp_path / "out"
    split_token_tsv(tok, out, "X")
    assert b"\r" not in (out / "nt_X.tsv").read_bytes()
    # an existing CRLF copy of identical content is not a conflict
    (out / "nt_X.tsv").write_bytes((HEADER + _row(40)).replace("\n", "\r\n").encode())
    assert dict(split_token_tsv(tok, out, "X").files)["nt_X.tsv"] == "unchanged"


def test_split_dry_run_writes_nothing(tmp_path):
    tok = _token(tmp_path, [1, 40])
    out = tmp_path / "out"
    split_token_tsv(tok, out, "X", dry_run=True)
    assert not out.exists()


def test_split_rejects_bad_header(tmp_path):
    p = tmp_path / "t.tsv"
    p.write_text("foo\tbar\n")
    with pytest.raises(ValueError):
        split_token_tsv(p, tmp_path / "out", "X")


# ---- pipeline.yaml lookup -------------------------------------------------

YAML = """
resources:
  Notes:
    type: resource
    abbreviation: "ABC"
  BibleOne:
    type: bible
    languages: ["swh"]
    abbreviation: "ONEN"
  DupSwh:
    type: bible
    languages: ["swh"]
    abbreviation: "DUP"
  DupEng:
    type: bible
    languages: ["eng"]
    abbreviation: "DUP"
  DupSwh2:
    type: bible
    languages: ["swh"]
    abbreviation: "DUP"
"""


def test_find_aquifer_bible(tmp_path):
    y = tmp_path / "pipeline.yaml"
    y.write_text(YAML)
    assert find_aquifer_bible(y, "ONEN", "swh") == "BibleOne"
    assert find_aquifer_bible(y, "ONEN") == "BibleOne"
    with pytest.raises(LookupError, match="no Bible"):
        find_aquifer_bible(y, "ABC")  # non-bible resource is ignored
    with pytest.raises(LookupError, match="no Bible"):
        find_aquifer_bible(y, "NOPE")
    with pytest.raises(LookupError, match="ambiguous"):
        find_aquifer_bible(y, "DUP", "swh")
    assert find_aquifer_bible(y, "DUP", "eng") == "DupEng"


# ---- map upsert -----------------------------------------------------------

def _map(tmp: Path, rows: list[list[str]]) -> Path:
    p = tmp / "map.tsv"
    p.write_text("\n".join("\t".join(r) for r in [MAP_COLUMNS, *rows]) + "\n")
    return p


CFG = {"target_language": "zht", "biblica_language": "cmn", "target_edition": "BOCCB2023T"}


def test_upsert_adds_row(tmp_path):
    m = _map(tmp_path, [])
    d = desired_map_row(CFG, "BiblicaOpenChineseContemporary2023Traditional")
    action, _ = upsert_alignment_map(m, d, tmp_path / "clear")
    assert action == "added"
    last = m.read_text().splitlines()[-1].split("\t")
    assert len(last) == 9
    assert last[MAP_COLUMNS.index("alignment_repo")] == "alignments-cmn"
    assert last[MAP_COLUMNS.index("alignment_path")] == "exp/BOCCB2023T/LLM-REFINED"
    # second run is a no-op
    before = m.read_bytes()
    action, _ = upsert_alignment_map(m, d, tmp_path / "clear")
    assert action == "unchanged" and m.read_bytes() == before


def test_upsert_fixes_nonexistent_alignment_path(tmp_path):
    d = desired_map_row(CFG, "B")
    old = [d[c] for c in MAP_COLUMNS]
    old[MAP_COLUMNS.index("alignment_path")] = "data/alignments/BOCCB2023T"
    m = _map(tmp_path, [old])
    action, msgs = upsert_alignment_map(m, d, tmp_path / "clear")  # path doesn't exist
    assert action == "updated"
    assert m.read_text().splitlines()[1].split("\t")[5] == "exp/BOCCB2023T/LLM-REFINED"


def test_upsert_keeps_existing_legacy_path(tmp_path):
    clear = tmp_path / "clear"
    (clear / "alignments-cmn" / "data/alignments/BOCCB2023T").mkdir(parents=True)
    d = desired_map_row(CFG, "B")
    old = [d[c] for c in MAP_COLUMNS]
    old[MAP_COLUMNS.index("alignment_path")] = "data/alignments/BOCCB2023T"
    old[MAP_COLUMNS.index("nt_source")] = "WRONG"
    m = _map(tmp_path, [old])
    action, msgs = upsert_alignment_map(m, d, clear)
    row = m.read_text().splitlines()[1].split("\t")
    assert action == "updated"  # nt_source corrected
    assert row[MAP_COLUMNS.index("nt_source")] == "SBLGNT"
    assert row[MAP_COLUMNS.index("alignment_path")] == "data/alignments/BOCCB2023T"  # kept
    assert any("left alone" in x for x in msgs)


def test_upsert_refuses_malformed_row(tmp_path):
    d = desired_map_row(CFG, "B")
    bad = [d[c] for c in MAP_COLUMNS]
    bad = bad[:5] + [bad[5] + bad[6]] + bad[7:]  # a missing tab
    m = _map(tmp_path, [bad])
    with pytest.raises(ValueError, match="fields"):
        upsert_alignment_map(m, d, tmp_path / "clear")


def test_upsert_preserves_crlf(tmp_path):
    m = tmp_path / "map.tsv"
    m.write_bytes(("\t".join(MAP_COLUMNS) + "\r\n").encode())
    upsert_alignment_map(m, desired_map_row(CFG, "B"), tmp_path / "clear")
    data = m.read_bytes()
    assert b"\r\n" in data and b"\n" not in data.replace(b"\r\n", b"")


def test_sync_alignment_map_end_to_end(tmp_path):
    root = tmp_path / "pipe"
    (root / "data" / "tsv").mkdir(parents=True)
    (root / "pipeline.yaml").write_text(YAML)
    (root / "data" / "tsv" / "alignment-map-2025-12-08.tsv").write_text("\t".join(MAP_COLUMNS) + "\n")
    cfg = {"target_language": "swh", "target_edition": "ONEN", "alignment_suffix": "OTHER"}
    action, msgs = sync_alignment_map(cfg, root, tmp_path / "clear")
    assert action == "added"
    assert any("alignment_suffix" in m for m in msgs)  # suffix mismatch warned
    assert any("does not exist yet" in m for m in msgs)
    assert "BibleOne\tONEN\tswh" in (root / "data/tsv/alignment-map-2025-12-08.tsv").read_text()
