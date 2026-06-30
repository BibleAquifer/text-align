"""Per-project YAML config loader for text-align CLI tools.

Usage in a CLI tool's parse_args():

    from text_align.config import load_config_from_args, require

    def parse_args():
        config_defaults = load_config_from_args(output_suffix="SIM-MIGRATED")

        p = argparse.ArgumentParser(...)
        p.add_argument("--config", metavar="NAME",
                       help="Load defaults from configs/<NAME>.yaml")
        p.add_argument("--source-edition", default=None, ...)
        # ... no required=True on config-eligible args ...

        p.set_defaults(**config_defaults)
        args = p.parse_args()

        require(args, "source_edition", "target_edition", ...)
        return args

Config files live in configs/<name>.yaml in the repo root.
Invoke with --config bonbv (extension assumed; .yaml appended automatically).

Path derivation
---------------
If a config sets ``alignments_root`` plus the identity keys
(``source_language``, ``source_edition``, ``target_language``/``alignment_lang``,
``target_edition``/``alignment_edition``), any path key that is *not* explicitly
provided is derived automatically:

    source_tsv_dir       → <root>/alignments-<src_lang>/data/targets/<src_ed>
    source_alignment_dir → <root>/alignments-<src_lang>/data/alignments/<src_ed>
    target_tsv_dir       → <root>/alignments-<trg_lang>/data/targets/<trg_ed>
    targets_dir          → <root>/alignments-<trg_lang>/data/targets/<trg_ed>
    lang_data_path       → <root>/alignments-<trg_lang>/data
    output_dir           → <root>/alignments-<trg_lang>/exp/<trg_ed>/<output_suffix>
                           (or <root>/alignments-<trg_lang>/<output_suffix> when
                            output_in_exp=False, used by render-alignment)
    alignment_dir        → <root>/alignments-<trg_lang>/exp/<trg_ed>/<alignment_suffix>
                           (only derived when ``alignment_suffix`` is set in the YAML;
                            used by render-alignment to point at a specific exp subdir)

Two additional paths are derived unconditionally from the repo root (``ROOT``),
regardless of ``alignments_root``.  They assume all repos share a common git-root
parent (``ROOT.parent.parent``):

    acai_data_dir → <git-root>/BibleAquifer/ACAI
    trabina_dir   → <git-root>/BN-Content/trabina/data/weighted

Set either key to ``null`` in the YAML to suppress the default (e.g. to disable
ACAI annotations in render-alignment when the sibling repo is absent).

Explicit values in the YAML always override derived ones.
"""

import argparse
import os
from pathlib import Path
from typing import Any

import yaml

from text_align import ROOT

CONFIGS_DIR = ROOT / "configs"

# Keys ending with these suffixes are auto-converted str → Path
_PATH_SUFFIXES = ("_dir", "_path", "_file", "_root")


def load_config(name: str) -> dict[str, Any]:
    """Load ``configs/<name>.yaml`` and return a dict of argument defaults.

    The ``.yaml`` extension is optional — it is appended if absent.
    String values whose key ends in ``_dir``, ``_path``, ``_file``, or
    ``_root`` are automatically converted to :class:`~pathlib.Path` objects.
    """
    stem = name
    for ext in (".yaml", ".yml"):
        if stem.endswith(ext):
            stem = stem[: -len(ext)]
            break
    path = CONFIGS_DIR / f"{stem}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path}\n"
            f"Config files should be YAML files in {CONFIGS_DIR}/"
        )
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}
    # Normalize hyphens to underscores so YAML keys match argparse dest names.
    # e.g. from-scratch: true → from_scratch: true (both forms accepted).
    return {
        k.replace("-", "_"): (
            Path(os.path.expandvars(v)).expanduser()
            if isinstance(v, str) and any(k.endswith(s) for s in _PATH_SUFFIXES)
            else v
        )
        for k, v in data.items()
    }


def derive_paths(
    config: dict[str, Any],
    output_suffix: str = "MIGRATED",
    output_in_exp: bool = True,
) -> dict[str, Any]:
    """Fill in missing path keys derived from ``alignments_root`` + identity values.

    Only fills keys that are absent from *config*; explicit values are never
    overwritten.  Returns a new dict (does not mutate *config*).

    *output_suffix* is the final component of the derived ``output_dir``:
    - ``"DIFF-MIGRATED"`` for diff-migrate
    - ``"SIM-MIGRATED"``  for sim-migrate
    - ``"ACAI"``          for acai-align
    - ``"viz"``           for render-alignment (with ``output_in_exp=False``)

    When *output_in_exp* is True (default):
        output_dir → <root>/alignments-<trg_lang>/exp/<trg_ed>/<output_suffix>
    When False:
        output_dir → <root>/alignments-<trg_lang>/<output_suffix>

    ACAI and trabina default paths are always derived relative to the repo root
    (``ROOT``).  Set to ``null`` in the YAML to disable (e.g. to suppress ACAI
    annotations in render-alignment):
        acai_data_dir → <git-root>/BibleAquifer/ACAI
        trabina_dir   → <git-root>/BN-Content/trabina/data/weighted
    where ``<git-root>`` is two levels above the repo root (``ROOT.parent.parent``).
    """
    result = dict(config)

    # Derive ACAI / trabina paths from the shared git-root sibling layout.
    # Only fills keys absent from the YAML; set to null to suppress.
    _git_root = ROOT.parent.parent
    result.setdefault("acai_data_dir", _git_root / "BibleAquifer" / "ACAI")
    result.setdefault("trabina_dir",   _git_root / "BN-Content" / "trabina" / "data" / "weighted")

    root = config.get("alignments_root")
    if not root:
        return result

    root = Path(root)

    src_lang = config.get("source_language")
    src_ed   = config.get("source_edition")
    # render-alignment uses alignment_lang / alignment_edition instead of
    # target_language / target_edition — resolve both and write both back so
    # set_defaults works regardless of which key the YAML uses.
    trg_lang = config.get("target_language") or config.get("alignment_lang")
    trg_ed   = config.get("target_edition")  or config.get("alignment_edition")
    if trg_lang:
        result.setdefault("alignment_lang", trg_lang)
        result.setdefault("target_language", trg_lang)
    if trg_ed:
        result.setdefault("alignment_edition", trg_ed)
        result.setdefault("target_edition", trg_ed)

    if src_lang and src_ed:
        src_repo = root / f"alignments-{src_lang}"
        result.setdefault("source_tsv_dir",       src_repo / "data" / "targets"   / src_ed)
        result.setdefault("source_alignment_dir",  src_repo / "data" / "alignments" / src_ed)

    if trg_lang and trg_ed:
        trg_repo = root / f"alignments-{trg_lang}"
        result.setdefault("target_tsv_dir",  trg_repo / "data" / "targets" / trg_ed)
        result.setdefault("targets_dir",     trg_repo / "data" / "targets" / trg_ed)
        result.setdefault("lang_data_path",  trg_repo / "data")
        if output_in_exp:
            result.setdefault("output_dir", trg_repo / "exp" / trg_ed / output_suffix)
        else:
            result.setdefault("output_dir", trg_repo / output_suffix)
        alignment_suffix = config.get("alignment_suffix")
        if alignment_suffix:
            result.setdefault("alignment_dir", trg_repo / "exp" / trg_ed / alignment_suffix)

    return result


def load_config_from_args(
    argv: list[str] | None = None,
    output_suffix: str = "MIGRATED",
    output_in_exp: bool = True,
) -> dict[str, Any]:
    """Extract ``--config`` from *argv* (or ``sys.argv``), load the YAML, and
    derive any missing paths.

    Returns an empty dict if ``--config`` was not supplied.
    Uses a minimal pre-parser so the main parser still sees all original args.
    """
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--config", default=None)
    pre_args, _ = pre.parse_known_args(argv)
    if pre_args.config:
        raw = load_config(pre_args.config)
        return derive_paths(raw, output_suffix=output_suffix, output_in_exp=output_in_exp)
    return {}


def require(args: argparse.Namespace, *fields: str) -> None:
    """Raise :exc:`SystemExit` if any of *fields* are ``None`` on *args*.

    Produces an error message naming both the CLI flag and ``--config``
    as valid ways to supply the missing value.
    """
    missing = [
        f"--{f.replace('_', '-')}"
        for f in fields
        if getattr(args, f, None) is None
    ]
    if missing:
        raise SystemExit(
            "error: the following arguments are required "
            "(supply on the command line or via --config):\n  "
            + "\n  ".join(missing)
        )
