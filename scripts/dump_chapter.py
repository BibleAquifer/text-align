#!/usr/bin/env python3
"""Dump one chapter of a generated alignment in a compact, reviewable form.

Usage:
    poetry run python scripts/dump_chapter.py --config CUV --corpus nt --chapter 56002
    poetry run python scripts/dump_chapter.py --config CUV --corpus nt --chapter 56002 --verses 1-5
    poetry run python scripts/dump_chapter.py --config CUV --corpus nt --prompt
    poetry run python scripts/dump_chapter.py --config CUV --corpus nt --prompt-block PASSIVE_VOICE

Per verse prints the source and target token streams, then every record as
`source -> target`, with secondary tokens marked `*`, followed by NEQ'd tokens
and anything left unaligned. Read-only; never writes.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from text_align import ROOT
from text_align.config import derive_paths, load_config

_CORPUS_ID = {"nt": "SBLGNT", "ot": "WLCM"}
_PUNCT = set("，。；、：？！「」『』－,.;:?!\"'()[]—-–…·“”‘’")


def _read_tsv(path: Path, text_col: int) -> dict[str, str]:
    out: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        rows = csv.reader(f, delimiter="\t")
        next(rows, None)
        for r in rows:
            if len(r) > text_col:
                out[r[0]] = r[text_col]
    return out


def _parse_verses(spec: str | None) -> set[int] | None:
    if not spec:
        return None
    lo, _, hi = spec.partition("-")
    return set(range(int(lo), int(hi or lo) + 1))


def _show_prompt(lang: str, corpus: str, block_tags: list[str] | None) -> None:
    import text_align.refine.prompt  # noqa: F401 — triggers language registration
    if corpus == "nt":
        from text_align.refine.prompt.nt.core import get_nt_language_config as get_cfg
    else:
        from text_align.refine.prompt.ot.core import get_ot_language_config as get_cfg
    cfg = get_cfg(lang)
    if block_tags:
        for t in block_tags:
            if t not in cfg.conditional_blocks:
                sys.exit(f"unknown block {t!r}; available: {', '.join(cfg.block_order)}")
            print(f"## [{t}]\n{cfg.conditional_blocks[t]}\n")
        return
    print(cfg.base_block)
    print("\n## Conditional blocks available (use --prompt-block TAG):")
    print(", ".join(cfg.block_order))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--corpus", required=True, choices=["nt", "ot"])
    ap.add_argument("--chapter", help="BBCCC, e.g. 56002")
    ap.add_argument("--verses", help="N or N-M within the chapter")
    ap.add_argument("--prompt", action="store_true", help="print the language's base prompt block and conditional-block tags")
    ap.add_argument("--prompt-block", nargs="+", metavar="TAG", help="print the named conditional prompt block(s)")
    args = ap.parse_args()

    cfg = derive_paths(load_config(args.config))
    lang, edition = cfg["target_language"], cfg["target_edition"]

    if args.prompt or args.prompt_block:
        _show_prompt(lang, args.corpus, args.prompt_block)
        return
    if not args.chapter:
        ap.error("--chapter is required unless --prompt/--prompt-block is given")

    cid = _CORPUS_ID[args.corpus]
    bb, ccc = args.chapter[:2], args.chapter[2:5]
    path = Path(cfg["alignment_dir"]) / f"{cid}-{edition}-{bb}-{ccc}-manual.json"
    if not path.exists():
        sys.exit(f"alignment file not found: {path}")
    group = json.loads(path.read_text(encoding="utf-8"))["groups"][0]
    neq = group.get("meta", {}).get("nonEquivalent", {})
    neq_src, neq_tgt = set(neq.get("source", [])), set(neq.get("target", []))

    src_text = {k[1:]: v for k, v in _read_tsv(ROOT / "data" / "sources" / f"{cid}.tsv", 2).items()
                if k[1:].startswith(args.chapter)}
    src_gloss = {k[1:]: v for k, v in _read_tsv(ROOT / "data" / "sources" / f"{cid}.tsv", 4).items()
                 if k[1:].startswith(args.chapter)}
    tgt_file = Path(cfg["target_tsv_dir"]) / f"{args.corpus}_{edition}.tsv"
    tgt_text = {k: v for k, v in _read_tsv(tgt_file, 2).items() if k.startswith(args.chapter)}

    want = _parse_verses(args.verses)
    verses = sorted({k[5:8] for k in tgt_text})
    print(f"# {args.config} {cid} {args.chapter}  llm={group.get('meta', {}).get('llm')}  "
          f"retry_llm={group.get('meta', {}).get('retry_llm')}")
    print("# legend: * secondary   [idiom]   NEQ listed per verse\n")

    aligned_tgt = {t for r in group["records"] for t in r["target"]} | neq_tgt
    aligned_src = {s for r in group["records"] for s in r["source"]} | neq_src

    for v in verses:
        if want and int(v) not in want:
            continue
        p = f"{args.chapter}{v}"
        print(f"== {int(v)} | " + "".join(t for k, t in tgt_text.items() if k.startswith(p)))
        verse_src = [k for k in src_text if k.startswith(p)]
        # OT versification can differ; only trust source-verse membership when ids match.
        print("   SRC: " + " ".join(f"{src_text[k]}[{src_gloss[k]}]" for k in verse_src))
        for r in group["records"]:
            if not any(x.startswith(p) for x in r["target"] or r["source"]):
                continue
            sec = r.get("meta", {}).get("secondary", {})
            s = " ".join(src_text.get(x, "?") + ("*" if x in sec.get("source", []) else "") for x in r["source"])
            t = " ".join(tgt_text.get(x, "?") + ("*" if x in sec.get("target", []) else "") for x in r["target"])
            print(f"   {s} -> {t}{'  [idiom]' if r.get('meta', {}).get('is_idiom') else ''}")
        ns = [src_text[x] for x in neq_src if x.startswith(p) and x in src_text]
        nt = [tgt_text[x] for x in neq_tgt if x.startswith(p) and x in tgt_text]
        if ns or nt:
            print(f"   NEQ  src={ns} tgt={nt}")
        us = [src_text[k] for k in verse_src if k not in aligned_src]
        ut = [t for k, t in tgt_text.items() if k.startswith(p) and k not in aligned_tgt and t not in _PUNCT]
        if us or ut:
            print(f"   UNALIGNED  src={us} tgt={ut}")
        print()


if __name__ == "__main__":
    main()
