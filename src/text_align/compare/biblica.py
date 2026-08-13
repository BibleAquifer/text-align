"""Load Biblica's Scripture Burrito 0.3 reference alignment data for comparison.

Biblica's ``alignments-{lang}`` repos mirror this project's directory layout
(``data/targets/{edition}/``, ``data/alignments/{edition}/``), so the existing
``AlignmentSet``/``AlignmentsReader`` classes read their files with no
adaptation: ``AlignmentsReader._make_record`` already calls
``macula_unprefixer`` on every source selector (Biblica keeps the canon
prefix we drop), and ``AlignmentsReader.read_alignments`` already handles a
flat (no ``groups`` wrapper) top-level JSON shape, which is exactly SB 0.3.
"""

from pathlib import Path

from text_align.burrito.AlignmentSet import AlignmentSet
from text_align.burrito.alignments import AlignmentsReader
from text_align.migrate.models import MigrateVerse
from text_align.migrate.tsv import process_usfm_tsv


def biblica_lang_data_path(clear_root: Path | str, lang_dir: str) -> Path:
    """Return the ``data/`` directory for a Biblica ``alignments-{lang}`` repo."""
    return Path(clear_root).expanduser() / f"alignments-{lang_dir}" / "data"


def resolve_biblica_reference_file(
    lang_data_path: Path,
    sourceid: str,
    targetid: str,
    override: str | None = None,
) -> Path:
    """Return the path to Biblica's reference alignment JSON.

    Defaults to ``{sourceid}-{targetid}-manual.json`` (the pattern documented
    by Biblica's own ``.toml`` sidecar files). *override* may be a bare
    filename (resolved under the standard ``alignments/{targetid}/`` dir) or
    a full path, since the right reference file varies by translation.
    """
    if override:
        override_path = Path(override)
        if not override_path.is_absolute() and override_path.parent == Path("."):
            return lang_data_path / "alignments" / targetid / override_path
        return override_path
    return lang_data_path / "alignments" / targetid / f"{sourceid}-{targetid}-manual.json"


def load_biblica_reader(
    clear_root: Path | str,
    lang_dir: str,
    sourceid: str,
    targetid: str,
    target_language: str,
    override: str | None = None,
) -> AlignmentsReader:
    """Load Biblica's reference alignment for *sourceid* -> *targetid* as an AlignmentsReader."""
    lang_data_path = biblica_lang_data_path(clear_root, lang_dir)
    reference_path = resolve_biblica_reference_file(lang_data_path, sourceid, targetid, override)
    if not reference_path.exists():
        raise FileNotFoundError(f"Biblica reference alignment not found: {reference_path}")
    alignmentset = AlignmentSet(
        sourceid=sourceid,
        targetid=targetid,
        targetlanguage=target_language,
        langdatapath=lang_data_path,
        alignmentpath_override=reference_path,
    )
    return AlignmentsReader(alignmentset=alignmentset)


def load_biblica_target_verses(
    clear_root: Path | str,
    lang_dir: str,
    targetid: str,
) -> dict[str, MigrateVerse]:
    """Load Biblica's own target TSVs (independent of ours), for id reconciliation and display."""
    targets_dir = biblica_lang_data_path(clear_root, lang_dir) / "targets" / targetid
    return process_usfm_tsv(targets_dir, targetid)
