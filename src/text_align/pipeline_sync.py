"""Helpers for moving data between text-align and BN-Content/aquifer-pipeline.

Two directions:

* **In** — ``create-bible`` writes one kathairo token TSV per Bible
  (``output/{lang}/{ABBR}/token/token_{ABBR}.tsv``).  The alignment code wants
  it split by testament as ``ot_{ABBR}.tsv`` / ``nt_{ABBR}.tsv``
  (:func:`split_token_tsv`).
* **Out** — once alignments exist, the pipeline needs a row in
  ``data/tsv/alignment-map-2025-12-08.tsv`` (:func:`upsert_alignment_map`).

The Aquifer resource name (the map's ``aquifer_bible`` column) is looked up in
the pipeline's ``pipeline.yaml`` by edition abbreviation
(:func:`find_aquifer_bible`).

This module only reads/writes files; it never runs git and never imports
``aquifer_pipeline``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_PIPELINE_ROOT = "~/git/BN-Content/aquifer-pipeline"
DEFAULT_CLEAR_ROOT = "~/git/Clear-Bible"

# The pipeline hard-codes both of these (import_alignments.py).
ALIGNMENT_MAP_RELPATH = Path("data") / "tsv" / "alignment-map-2025-12-08.tsv"
PIPELINE_SUFFIX = "LLM-REFINED"

GITHUB_ORG = "Clear-Bible"
NT_SOURCE = "SBLGNT"
OT_SOURCE = "WLCM"

MAP_COLUMNS = [
    "aquifer_bible", "biblica_abbr", "language", "github_org", "alignment_repo",
    "alignment_path", "target_path", "nt_source", "ot_source",
]

OT_BOOKS = range(1, 40)
NT_BOOKS = range(40, 67)


# ---------------------------------------------------------------------------
# pipeline.yaml lookup
# ---------------------------------------------------------------------------

def find_aquifer_bible(pipeline_yaml: Path, abbreviation: str, language: str | None = None) -> str:
    """Return the ``pipeline.yaml`` resource key for a Bible edition.

    Matches ``type: bible`` entries whose ``abbreviation`` equals *abbreviation*.
    If several match, *language* (checked against each entry's ``languages``)
    disambiguates.  Raises :class:`LookupError` on no match or ambiguity.
    """
    data = yaml.safe_load(Path(pipeline_yaml).read_text(encoding="utf-8")) or {}
    resources: dict[str, Any] = data.get("resources") or {}
    matches = [
        name for name, entry in resources.items()
        if isinstance(entry, dict)
        and entry.get("type") == "bible"
        and entry.get("abbreviation") == abbreviation
    ]
    if len(matches) > 1 and language:
        matches = [m for m in matches if language in (resources[m].get("languages") or [])]
    if not matches:
        raise LookupError(
            f"no Bible with abbreviation {abbreviation!r} in {pipeline_yaml}; "
            "add the resource to pipeline.yaml first"
        )
    if len(matches) > 1:
        raise LookupError(
            f"abbreviation {abbreviation!r} is ambiguous in {pipeline_yaml}: {', '.join(matches)}"
        )
    return matches[0]


def check_bible_metadata(pipeline_root: Path, language: str, abbreviation: str) -> str | None:
    """Return a warning if ``bible_metadata.yaml`` disagrees on the abbreviation."""
    meta = Path(pipeline_root) / "data" / "bibles" / language / abbreviation / "bible_metadata.yaml"
    if not meta.exists():
        return None
    data = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
    found = data.get("abbreviation")
    if found and found != abbreviation:
        return f"{meta} says abbreviation {found!r}, config says {abbreviation!r}"
    return None


# ---------------------------------------------------------------------------
# Token TSV split
# ---------------------------------------------------------------------------

@dataclass
class SplitResult:
    # (filename, status) where status is one of: written, unchanged, overwritten, conflict, skipped-empty
    files: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def conflicts(self) -> list[str]:
        return [n for n, s in self.files if s == "conflict"]


def _book_of(line: str) -> int | None:
    first = line.split("\t", 1)[0]
    try:
        return int(first[:2])
    except ValueError:
        return None


def split_token_tsv(
    token_path: Path,
    out_dir: Path,
    abbreviation: str,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> SplitResult:
    """Split a kathairo token TSV into ``ot_{abbr}.tsv`` and ``nt_{abbr}.tsv``.

    Rows are passed through unchanged except that line endings are normalized
    to LF (the pipeline writes CRLF; the Clear repos hold LF) and the header is
    repeated in each file.  Existing files are compared ignoring line endings.
    A testament with no rows (e.g. an NT-only Bible) gets no file.  An existing
    file with identical content is left alone; one with different content is a
    conflict unless *force* is set.  Nothing is written if any conflict exists
    and *force* is False.
    """
    token_path = Path(token_path)
    with token_path.open("r", encoding="utf-8", newline="") as f:
        lines = f.read().splitlines(keepends=True)
    if not lines or not lines[0].startswith("id\t"):
        raise ValueError(f"{token_path}: first line is not a kathairo token header (expected 'id\\t...')")

    lines = [ln.rstrip("\r\n") + "\n" for ln in lines]
    header, rows = lines[0], lines[1:]
    result = SplitResult()
    buckets: dict[str, list[str]] = {"ot": [], "nt": []}
    stray = 0
    for row in rows:
        if not row.strip():
            continue
        book = _book_of(row)
        if book in OT_BOOKS:
            buckets["ot"].append(row)
        elif book in NT_BOOKS:
            buckets["nt"].append(row)
        else:
            stray += 1
    if stray:
        result.warnings.append(f"{stray} row(s) with a book number outside 01-66 were dropped")

    out_dir = Path(out_dir)
    pending: list[tuple[Path, str, str]] = []  # (path, content, status)
    for canon in ("ot", "nt"):
        name = f"{canon}_{abbreviation}.tsv"
        if not buckets[canon]:
            result.files.append((name, "skipped-empty"))
            continue
        content = header + "".join(buckets[canon])
        dest = out_dir / name
        if dest.exists():
            if dest.read_bytes().replace(b"\r\n", b"\n") == content.encode("utf-8"):
                result.files.append((name, "unchanged"))
                continue
            status = "overwritten" if force else "conflict"
        else:
            status = "written"
        result.files.append((name, status))
        pending.append((dest, content, status))

    if result.conflicts or dry_run:
        return result
    out_dir.mkdir(parents=True, exist_ok=True)
    for dest, content, _ in pending:
        with dest.open("w", encoding="utf-8", newline="") as f:
            f.write(content)
    return result


# ---------------------------------------------------------------------------
# Alignment map upsert
# ---------------------------------------------------------------------------

def desired_map_row(config: dict[str, Any], aquifer_bible: str) -> dict[str, str]:
    """Build the alignment-map row implied by a text-align config."""
    lang = config["target_language"]
    edition = config["target_edition"]
    biblica_lang = config.get("biblica_language") or lang
    return {
        "aquifer_bible": aquifer_bible,
        "biblica_abbr": edition,
        "language": lang,
        "github_org": GITHUB_ORG,
        "alignment_repo": f"alignments-{biblica_lang}",
        "alignment_path": f"exp/{edition}/{PIPELINE_SUFFIX}",
        "target_path": f"data/targets/{edition}",
        "nt_source": NT_SOURCE,
        "ot_source": OT_SOURCE,
    }


def upsert_alignment_map(
    map_path: Path,
    desired: dict[str, str],
    clear_root: Path,
    *,
    dry_run: bool = False,
) -> tuple[str, list[str]]:
    """Add or reconcile one row of the alignment map.  Returns (action, messages).

    *action* is ``added``, ``updated`` or ``unchanged``.  For an existing row
    every column is brought in line with *desired* except ``alignment_path``:
    that is only corrected when the current path does not exist under the Clear
    repo.  A path that does exist (e.g. a legacy ``data/alignments/ONEN``
    holding Biblica's v0.3 alignment) is left alone, since changing it would
    change what the pipeline imports.
    """
    map_path = Path(map_path)
    with map_path.open("r", encoding="utf-8", newline="") as f:
        text = f.read()
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    if not lines or lines[0].split("\t") != MAP_COLUMNS:
        raise ValueError(f"{map_path}: unexpected header (expected columns {MAP_COLUMNS})")

    messages: list[str] = []
    repo_dir = Path(clear_root).expanduser() / desired["alignment_repo"]

    idx = next(
        (i for i, ln in enumerate(lines[1:], 1) if ln.split("\t", 1)[0] == desired["aquifer_bible"]),
        None,
    )

    if idx is None:
        lines.append("\t".join(desired[c] for c in MAP_COLUMNS))
        action = "added"
        messages.append(f"add row {desired['aquifer_bible']} ({desired['biblica_abbr']})")
    else:
        fields = lines[idx].split("\t")
        if len(fields) != len(MAP_COLUMNS):
            raise ValueError(
                f"{map_path}: row {desired['aquifer_bible']} has {len(fields)} fields, "
                f"expected {len(MAP_COLUMNS)} (missing/extra tab?); fix it by hand"
            )
        current = dict(zip(MAP_COLUMNS, fields))
        changed = False
        for col in MAP_COLUMNS:
            if current[col] == desired[col]:
                continue
            if col == "alignment_path":
                if (repo_dir / current[col]).exists():
                    messages.append(
                        f"keep alignment_path {current[col]!r} (exists; differs from "
                        f"{desired[col]!r}) -- left alone"
                    )
                    continue
            messages.append(f"{col}: {current[col]!r} -> {desired[col]!r}")
            current[col] = desired[col]
            changed = True
        if changed:
            lines[idx] = "\t".join(current[c] for c in MAP_COLUMNS)
            action = "updated"
        else:
            action = "unchanged"

    if action != "unchanged" and not dry_run:
        with map_path.open("w", encoding="utf-8", newline="") as f:
            f.write(eol.join(lines) + eol)
    return action, messages


def sync_alignment_map(
    config: dict[str, Any],
    pipeline_root: Path,
    clear_root: Path,
    *,
    dry_run: bool = False,
) -> tuple[str, list[str]]:
    """Resolve the Aquifer name from ``pipeline.yaml`` and upsert the map row.

    Returns (action, messages) including any warnings.  Raises
    :class:`LookupError` / :class:`FileNotFoundError` / :class:`ValueError`
    for problems the caller should report.
    """
    pipeline_root = Path(pipeline_root).expanduser()
    clear_root = Path(clear_root).expanduser()
    lang, edition = config.get("target_language"), config.get("target_edition")
    if not lang or not edition:
        raise ValueError("config must define target_language and target_edition")

    messages: list[str] = []
    suffix = config.get("alignment_suffix") or PIPELINE_SUFFIX
    if suffix != PIPELINE_SUFFIX:
        messages.append(
            f"warning: alignment_suffix is {suffix!r} but the pipeline only reads "
            f"exp/<abbr>/{PIPELINE_SUFFIX}; it will not find this output"
        )

    pipeline_yaml = pipeline_root / "pipeline.yaml"
    map_path = pipeline_root / ALIGNMENT_MAP_RELPATH
    for p in (pipeline_yaml, map_path):
        if not p.exists():
            raise FileNotFoundError(f"not found: {p}")

    aquifer_bible = find_aquifer_bible(pipeline_yaml, edition, lang)
    meta_warn = check_bible_metadata(pipeline_root, lang, edition)
    if meta_warn:
        messages.append(f"warning: {meta_warn}")

    desired = desired_map_row(config, aquifer_bible)
    action, msgs = upsert_alignment_map(map_path, desired, clear_root, dry_run=dry_run)
    messages.extend(msgs)

    out_dir = clear_root / desired["alignment_repo"] / desired["alignment_path"]
    if not out_dir.exists():
        messages.append(f"warning: {out_dir} does not exist yet")
    return action, messages
