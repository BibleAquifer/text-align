#!/usr/bin/env python3
"""split-token-tsv.py -- Split an aquifer-pipeline kathairo token TSV by testament.

`create-bible` (aquifer-pipeline) writes one token TSV per Bible:

    <pipeline-root>/output/<lang>/<ABBR>/token/token_<ABBR>.tsv

The alignment code wants it split into ot_<ABBR>.tsv and nt_<ABBR>.tsv (header
kept, rows untouched), placed where copy-to-gha.py already looks:

    <clear-root>/alignments-<biblica_lang>/data/targets/<ABBR>/

A testament with no rows (e.g. an NT-only Bible) gets no file.  Idempotent:
identical existing files are left alone; differing ones need --force.

Usage:
    python scripts/split-token-tsv.py --config BOKKPB
    python scripts/split-token-tsv.py --config BOKKPB --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from text_align.config import load_config
from text_align.pipeline_sync import DEFAULT_CLEAR_ROOT, DEFAULT_PIPELINE_ROOT, split_token_tsv


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", required=True, metavar="NAME", help="Config name (configs/<NAME>.yaml)")
    p.add_argument("--clear-root", default=DEFAULT_CLEAR_ROOT, metavar="PATH")
    p.add_argument("--pipeline-root", default=DEFAULT_PIPELINE_ROOT, metavar="PATH",
                   help=f"aquifer-pipeline checkout (default: {DEFAULT_PIPELINE_ROOT})")
    p.add_argument("--force", action="store_true", help="Overwrite existing files whose content differs")
    p.add_argument("--dry-run", action="store_true", help="Report what would happen without writing")
    args = p.parse_args()

    config = load_config(args.config)
    lang = config.get("target_language")
    edition = config.get("target_edition")
    if not lang or not edition:
        sys.exit(f"error: config {args.config} must define target_language and target_edition")
    biblica_lang = config.get("biblica_language") or lang

    token = Path(args.pipeline_root).expanduser() / "output" / lang / edition / "token" / f"token_{edition}.tsv"
    out_dir = Path(args.clear_root).expanduser() / f"alignments-{biblica_lang}" / "data" / "targets" / edition
    if not token.exists():
        sys.exit(f"error: token TSV not found: {token}\n  Run create-bible for {edition} first.")

    print(f"split-token-tsv: {lang}/{edition}")
    print(f"  {token}\n  -> {out_dir}")
    result = split_token_tsv(token, out_dir, edition, force=args.force, dry_run=args.dry_run)
    tag = "[dry-run] " if args.dry_run else ""
    for name, status in result.files:
        print(f"  {tag}{status:<13} {name}")
    for w in result.warnings:
        print(f"  warning: {w}")
    if result.conflicts:
        sys.exit(
            f"error: existing file(s) differ: {', '.join(result.conflicts)}\n"
            "  Nothing written. Re-run with --force to overwrite."
        )


if __name__ == "__main__":
    main()
