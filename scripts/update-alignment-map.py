#!/usr/bin/env python3
"""update-alignment-map.py -- Add/reconcile this edition's row in aquifer-pipeline's alignment map.

Edits <pipeline-root>/data/tsv/alignment-map-2025-12-08.tsv in the working tree
(never runs git there).  The Aquifer resource name is looked up in the
pipeline's pipeline.yaml by target_edition.  copy-from-gha.py runs this
automatically; use this script to run it on its own.

  * new row: alignment_path = exp/<ABBR>/LLM-REFINED
  * existing row: columns are corrected, except alignment_path, which is only
    changed when the current path doesn't exist under the Clear repo (a
    legacy path that exists, e.g. data/alignments/ONEN, is left alone)

Usage:
    python scripts/update-alignment-map.py --config ONEN
    python scripts/update-alignment-map.py --config BOKKPB --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from text_align.config import load_config
from text_align.pipeline_sync import DEFAULT_CLEAR_ROOT, DEFAULT_PIPELINE_ROOT, sync_alignment_map


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", required=True, metavar="NAME", help="Config name (configs/<NAME>.yaml)")
    p.add_argument("--clear-root", default=DEFAULT_CLEAR_ROOT, metavar="PATH")
    p.add_argument("--pipeline-root", default=DEFAULT_PIPELINE_ROOT, metavar="PATH",
                   help=f"aquifer-pipeline checkout (default: {DEFAULT_PIPELINE_ROOT})")
    p.add_argument("--dry-run", action="store_true", help="Report what would change without writing")
    args = p.parse_args()

    config = load_config(args.config)
    try:
        action, messages = sync_alignment_map(
            config, Path(args.pipeline_root), Path(args.clear_root), dry_run=args.dry_run
        )
    except (LookupError, FileNotFoundError, ValueError) as e:
        sys.exit(f"error: {e}")

    tag = "[dry-run] " if args.dry_run else ""
    print(f"update-alignment-map: {config.get('target_edition')}: {tag}{action}")
    for m in messages:
        print(f"  {m}")
    if action != "unchanged" and not args.dry_run:
        print(f"\nReview and commit in {Path(args.pipeline_root).expanduser()} yourself (no git was run).")


if __name__ == "__main__":
    main()
