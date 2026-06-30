#!/usr/bin/env python3
"""copy-from-gha.py -- Copy GHA alignment results back to the Clear alignments repo.

After a GHA alignment run (align-nt or align-ot) completes:
  1. git pull   (to get GHA-committed JSON files into this repo)
  2. Run this script

Copies:
  ./data/alignments/alignments-<lang>/exp/<edition>/<alignment_suffix>/*.json
    -> <clear_root>/alignments-<lang>/exp/<edition>/<alignment_suffix>/

  ./data/alignments/alignments-<lang>/viz/<edition>/   (if present)
    -> <clear_root>/alignments-<lang>/viz/<edition>/

Then patches the config YAML so alignments_root points back to <clear_root>,
and removes the edition-specific staged data from ./data/alignments/:
  alignments-<lang>/data/targets/<edition>/
  alignments-<lang>/exp/<edition>/
  alignments-<lang>/viz/<edition>/   (if present)

The alignment_suffix is read from the config YAML; defaults to LLM-REFINED.

Usage:
    python scripts/copy-from-gha.py --config JFA11
    python scripts/copy-from-gha.py --config OENGB --dry-run
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
    clear_root_str = args.clear_root  # raw (unexpanded) form — written back to YAML

    src_json_dir = (
        _REPO_ROOT / "data" / "alignments"
        / f"alignments-{lang}" / "exp" / edition / suffix
    )
    dest_json_dir = clear_root / f"alignments-{lang}" / "exp" / edition / suffix

    src_viz_dir = (
        _REPO_ROOT / "data" / "alignments"
        / f"alignments-{lang}" / "viz" / edition
    )
    dest_viz_dir = clear_root / f"alignments-{lang}" / "viz" / edition

    tag = "[dry-run] " if args.dry_run else ""
    print(f"copy-from-gha: {lang}/{edition}  suffix={suffix}")
    print()

    # --- Alignment JSON files ---
    if not src_json_dir.exists():
        sys.exit(
            f"error: source alignment dir not found: {src_json_dir}\n"
            "  Did you git pull first?"
        )

    jsons = sorted(src_json_dir.glob("*.json"))
    if not jsons:
        sys.exit(
            f"error: no JSON files found in {src_json_dir}\n"
            "  Did you git pull first?"
        )

    print(f"  alignment JSON ({len(jsons)} files):")
    print(f"    {src_json_dir}")
    print(f"    -> {dest_json_dir}")

    if not args.dry_run:
        dest_json_dir.mkdir(parents=True, exist_ok=True)

    for f in jsons:
        print(f"  {tag}copy  {f.name}")
        if not args.dry_run:
            shutil.copy2(f, dest_json_dir / f.name)

    print(f"\n  {len(jsons)} file(s) copied")
    print()

    # --- Viz ---
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

    # --- YAML patch ---
    config_path = CONFIGS_DIR / f"{args.config}.yaml"
    _patch_yaml(config_path, clear_root_str, args.dry_run)

    # --- Cleanup staged data ---
    staged_root = _REPO_ROOT / "data" / "alignments" / f"alignments-{lang}"
    cleanup_dirs = [
        staged_root / "data" / "targets" / edition,
        staged_root / "exp" / edition,
        staged_root / "viz" / edition,
    ]
    print()
    print("  cleanup staged data:")
    for d in cleanup_dirs:
        if d.exists():
            print(f"  {tag}rm -r  {d.relative_to(_REPO_ROOT)}")
            if not args.dry_run:
                shutil.rmtree(d)
        else:
            print(f"  (not present: {d.relative_to(_REPO_ROOT)})")

    print()
    if args.dry_run:
        print("Dry run complete -- no files written.")
    else:
        print("Done.")
        print()
        print("Next steps (in Clear repo):")
        print(f"  cd {clear_root / f'alignments-{lang}'}")
        print(f"  git add exp/{edition}/{suffix}/")
        if has_viz:
            print(f"  git add viz/{edition}/")
        print(f"  git commit -m 'feat: GHA alignment results -- {lang}/{edition}'")
        print( "  git push")
        print()
        print("Next steps (in text-align repo):")
        print(f"  git add -A")
        print(f"  git commit -m 'chore: restore alignments_root and remove staged data for {args.config}'")


if __name__ == "__main__":
    main()
