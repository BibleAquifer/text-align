#!/usr/bin/env python3
"""copy-to-gha.py -- Stage translation TSVs into text-align repo for a GHA alignment run.

Copies all TSV files for the target edition from the Clear alignments repo into
./data/alignments/alignments-<lang>/data/targets/<edition>/, then patches the
config YAML so alignments_root points to ./data/alignments.

If exp/<edition>/<alignment_suffix>/ exists in the Clear repo, its JSON files are
also staged (enables incremental GHA runs). If viz/<edition>/ exists, it is staged too.

The alignment_suffix is read from the config YAML; defaults to LLM-REFINED.

After running this script:
  1. git add data/alignments/alignments-<lang>/ configs/<edition>.yaml
  2. git commit && git push
  3. Trigger the GHA align-nt workflow with config=<edition> lang=<lang>

Usage:
    python scripts/copy-to-gha.py --config JFA11
    python scripts/copy-to-gha.py --config OENGB --dry-run
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src"))

from text_align.config import CONFIGS_DIR, load_config

_DEFAULT_SUFFIX = "LLM-REFINED"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--config", required=True, metavar="NAME",
                   help="Config name, e.g. JFA11 (reads configs/<NAME>.yaml)")
    p.add_argument("--clear-root", default="~/git/Clear-Bible", metavar="PATH",
                   help="Root of the Clear alignments repos (default: ~/git/Clear-Bible)")
    p.add_argument("--dry-run", action="store_true",
                   help="Print actions without copying files or patching YAML")
    return p.parse_args()


def _patch_yaml(config_path: Path, new_value: str, dry_run: bool) -> None:
    content = config_path.read_text(encoding="utf-8")
    old_line = next(
        (ln for ln in content.splitlines() if ln.startswith("alignments_root:")), None
    )
    if old_line is None:
        print(f"  warning: no alignments_root line in {config_path.name} -- not patched")
        return
    new_content = re.sub(
        r"^alignments_root:.*", f"alignments_root: {new_value}", content, flags=re.MULTILINE
    )
    print(f"  patch {config_path.name}:")
    print(f"    was: {old_line}")
    print(f"    now: alignments_root: {new_value}")
    if not dry_run:
        config_path.write_text(new_content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    lang = config.get("target_language")
    edition = config.get("target_edition")
    suffix = config.get("alignment_suffix") or _DEFAULT_SUFFIX
    if not lang or not edition:
        sys.exit(f"error: config {args.config} must define target_language and target_edition")

    clear_root = Path(args.clear_root).expanduser()
    staged_root = _REPO_ROOT / "data" / "alignments" / f"alignments-{lang}"

    src_tsv_dir = clear_root / f"alignments-{lang}" / "data" / "targets" / edition
    dest_tsv_dir = staged_root / "data" / "targets" / edition

    src_exp_dir = clear_root / f"alignments-{lang}" / "exp" / edition / suffix
    dest_exp_dir = staged_root / "exp" / edition / suffix

    src_viz_dir = clear_root / f"alignments-{lang}" / "viz" / edition
    dest_viz_dir = staged_root / "viz" / edition

    if not src_tsv_dir.exists():
        sys.exit(f"error: source targets dir not found: {src_tsv_dir}")

    tsvs = sorted(src_tsv_dir.glob("*.tsv"))
    if not tsvs:
        sys.exit(f"error: no TSV files found in {src_tsv_dir}")

    tag = "[dry-run] " if args.dry_run else ""
    print(f"copy-to-gha: {lang}/{edition}  suffix={suffix}")
    print()

    # --- TSV target files ---
    print(f"  targets ({len(tsvs)} TSV files):")
    print(f"    {src_tsv_dir}")
    print(f"    -> {dest_tsv_dir}")

    if not args.dry_run:
        dest_tsv_dir.mkdir(parents=True, exist_ok=True)

    for tsv in tsvs:
        print(f"  {tag}copy  {tsv.name}")
        if not args.dry_run:
            shutil.copy2(tsv, dest_tsv_dir / tsv.name)

    print(f"\n  {len(tsvs)} file(s) copied")
    print()

    # --- Exp alignment JSONs (optional) ---
    jsons = sorted(src_exp_dir.glob("*.json")) if src_exp_dir.exists() else []
    if jsons:
        print(f"  exp alignment JSON ({len(jsons)} files):")
        print(f"    {src_exp_dir}")
        print(f"    -> {dest_exp_dir}")
        if not args.dry_run:
            dest_exp_dir.mkdir(parents=True, exist_ok=True)
        for f in jsons:
            print(f"  {tag}copy  {f.name}")
            if not args.dry_run:
                shutil.copy2(f, dest_exp_dir / f.name)
        print(f"\n  {len(jsons)} file(s) copied")
    else:
        print(f"  exp: {src_exp_dir} not found or empty -- skipping")
    print()

    # --- Viz (optional) ---
    has_viz = src_viz_dir.exists() and any(src_viz_dir.iterdir())
    if has_viz:
        print(f"  viz:")
        print(f"    {src_viz_dir}")
        print(f"    -> {dest_viz_dir}")
        if not args.dry_run:
            shutil.copytree(src_viz_dir, dest_viz_dir, dirs_exist_ok=True)
            print("  viz copied")
        else:
            print(f"  {tag}copytree viz")
    else:
        print(f"  viz: {src_viz_dir} not found or empty -- skipping")
    print()

    config_path = CONFIGS_DIR / f"{args.config}.yaml"
    _patch_yaml(config_path, "./data/alignments", args.dry_run)

    print()
    if args.dry_run:
        print("Dry run complete -- no files written.")
    else:
        print("Done.")
        print()
        print("Next steps:")
        print(f"  git add data/alignments/alignments-{lang}/")
        print(f"  git add configs/{args.config}.yaml")
        print(f"  git commit -m 'chore: stage {lang}/{edition} data for GHA alignment'")
        print( "  git push")
        print(f"  # Trigger GHA align-nt or align-ot workflow: config={args.config}  lang={lang}")


if __name__ == "__main__":
    main()
