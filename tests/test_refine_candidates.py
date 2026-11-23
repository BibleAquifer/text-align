import json

from text_align.burrito.source import Source
from text_align.migrate.models import MigrateTarget
from text_align.refine.prompt.common import CANDIDATE_INSTRUCTION, build_batch_message
from text_align.refine.refine import load_candidate_records

SRC = [Source(id=i, text=f"s{n}") for n, i in enumerate(
    ["400010010011", "400010010021", "400010010031", "400010010041", "400010010051"], 1)]
S = [t.id for t in SRC]  # Source normalizes ids
T = ["40001001001", "40001001002", "40001001003", "40001001004"]


def _write(tmp_path):
    path = tmp_path / "SBLGNT-ONMM-manual.json"
    path.write_text(json.dumps({"groups": [{
        "meta": {"nonEquivalent": {"source": [S[4]], "target": [T[3]]}},
        "records": [
            {"source": [S[0]], "target": [T[0]]},
            {"source": [S[1], S[2]], "target": [T[1]], "meta": {"secondary": {"source": [S[2]]}}},
        ]}]}))
    return path


def test_loader_keeps_meta_and_attaches_neq(tmp_path):
    verses = load_candidate_records(_write(tmp_path))
    recs = next(iter(verses.values()))
    assert recs[1]["meta"] == {"secondary": {"source": [S[2]]}}
    neq = recs[-1]
    assert neq["meta"] == {"rel": "NEQ"} and neq["source"] == [S[4]] and neq["target"] == [T[3]]


def test_block_marks_secondary_neq_and_no_candidate(tmp_path):
    verses = load_candidate_records(_write(tmp_path))
    cands = {"DIFF-MIGRATED": next(iter(verses.values()))}
    src = SRC
    tgt = [MigrateTarget(id=i, source_verse="40001001", text=f"t{n}") for n, i in enumerate(T, 1)]
    msg, _ = build_batch_message([("40001001", src, tgt, cands)], "swh")
    print(msg)
    assert msg.startswith(CANDIDATE_INSTRUCTION)
    assert "source: [2 3*]  target: [2]" in msg
    assert "NEQ  source: [5]  target: [4]" in msg
    tail = msg.split("\nNO CANDIDATE:")[1]
    assert "source: [4]" in tail and "target: [3]" in tail
    no_cand = build_batch_message([("40001001", src, tgt, {})], "swh")[0]
    assert "CANDIDATE" not in no_cand


def test_load_candidates_selects_chapters_and_falls_back_to_single_file(tmp_path):
    from text_align.refine.refine import load_candidates

    def chapter(name, src, tgt):
        (tmp_path / name).write_text(json.dumps({"groups": [{"meta": {}, "records": [
            {"source": [src], "target": [tgt]}]}]}))

    chapter("SBLGNT-ONMM-40-001-manual.json", "400010010011", "40001001001")
    chapter("SBLGNT-ONMM-40-002-manual.json", "400020010011", "40002001001")
    recs, desc = load_candidates(tmp_path, "SBLGNT", "ONMM", {"40002"})
    assert list(recs) == ["40002001"] and "1 of 2" in desc
    assert len(load_candidates(tmp_path, "SBLGNT", "ONMM", None)[0]) == 2
    assert load_candidates(tmp_path / "missing", "SBLGNT", "ONMM") is None

    single = tmp_path / "single"
    single.mkdir()
    (single / "SBLGNT-ONMM-manual.json").write_text(json.dumps({"records": [
        {"source": ["n40001001001"], "target": ["40001001001"]}]}))
    assert len(load_candidates(single, "SBLGNT", "ONMM", {"40001"})[0]) == 1
