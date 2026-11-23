import json
from pathlib import Path

from text_align.migrate.alignment_io import create_new_alignments, load_source_alignment


def _chapter(path: Path, records, neq=None):
    meta = {"conformsTo": "0.4"}
    if neq:
        meta["nonEquivalent"] = neq
    path.write_text(json.dumps({"format": "alignment", "version": "0.4",
                                "groups": [{"meta": meta, "records": records}]}))


def test_prefers_v04_chapter_files_and_merges_neq(tmp_path):
    v04, v03 = tmp_path / "v04", tmp_path / "v03"
    v04.mkdir(); v03.mkdir()
    _chapter(v04 / "SBLGNT-ONEN-40-001-manual.json",
             [{"source": ["40001001001"], "target": ["40001001001"]}],
             neq={"source": ["40001001002"], "target": ["40001001009"]})
    _chapter(v04 / "SBLGNT-ONEN-40-002-manual.json",
             [{"source": ["40002001001"], "target": ["40002001001"]}],
             neq={"source": ["40002001002"], "target": []})
    (v04 / "SBLGNT-ONEN-40-001-manual.retries.json").write_text("{}")
    (v03 / "SBLGNT-ONEN-manual.json").write_text(json.dumps({"records": []}))

    data, desc = load_source_alignment("SBLGNT", "ONEN", v04, v03)
    group = data["groups"][0]
    assert "0.4" in desc and "2 chapter files" in desc
    assert len(group["records"]) == 2
    assert group["meta"]["nonEquivalent"] == {
        "source": ["40001001002", "40002001002"], "target": ["40001001009"]}


def test_falls_back_to_v03_then_none(tmp_path):
    v04, v03 = tmp_path / "v04", tmp_path / "v03"
    v03.mkdir()
    (v03 / "SBLGNT-ONEN-manual.json").write_text(
        json.dumps({"records": [{"source": ["n40001001001"], "target": ["40001001001"]}]}))
    data, desc = load_source_alignment("SBLGNT", "ONEN", v04, v03)
    assert "0.3 fallback" in desc and len(data["records"]) == 1
    assert load_source_alignment("WLCM", "ONEN", v04, v03) is None


def test_create_new_alignments_keeps_meta_and_neq_for_v04():
    src = {"groups": [{"meta": {"nonEquivalent": {"source": ["s2"], "target": ["t9", "t8"]}},
                       "records": [
                           {"source": ["s1", "s3"], "target": ["t1"],
                            "meta": {"secondary": {"source": ["s3"]}}},
                           {"source": ["s4"], "target": ["t7"]},  # t7 not in remap
                       ]}]}
    out = create_new_alignments(src, {"t1": "u1", "t9": "u9"}, "SBLGNT", "ONMM")
    group = out["groups"][0]
    assert group["records"] == [{"source": ["s1", "s3"], "target": ["u1"],
                                 "meta": {"secondary": {"source": ["s3"]}}}]
    assert group["meta"]["nonEquivalent"] == {"source": ["s2"], "target": ["u9"]}


def test_create_new_alignments_v03_drops_meta():
    src = {"records": [{"source": ["n1"], "target": ["t1"],
                        "meta": {"id": "x", "origin": "manual"}}]}
    out = create_new_alignments(src, {"t1": "u1"}, "SBLGNT", "ONMM")
    assert out["groups"][0]["records"] == [{"source": ["n1"], "target": ["u1"]}]
    assert "nonEquivalent" not in out["groups"][0]["meta"]
