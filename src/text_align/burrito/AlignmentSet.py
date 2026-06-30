"""Manage the file paths for a source+target alignment set."""

from dataclasses import dataclass
from pathlib import Path
import re

from text_align import ROOT, SOURCES, SourceidEnum


@dataclass
class AlignmentSet:
    """Manage file paths for an alignment set.

    sourcedatapath defaults to the repo's own data/sources/ directory,
    where SBLGNT.tsv and WLCM.tsv are stored.
    """

    sourceid: str
    targetid: str
    targetlanguage: str
    sourcedatapath: Path = SOURCES
    langdatapath: Path = Path()
    alternateid: str = "manual"
    reponame: str = ""
    alignmentpath_override: Path | None = None
    # computed in __post_init__
    sourcepath: Path = Path()
    targetpath: Path = Path()
    alignmentpath: Path = Path()
    tomlpath: Path = Path()

    def __post_init__(self) -> None:
        for idattr in ["sourceid", "targetid"]:
            idstr = getattr(self, idattr)
            if not re.fullmatch(r"\w+", idstr, flags=re.ASCII):
                raise ValueError(f"Invalid {idattr}: {idstr}")
        _ = SourceidEnum(self.sourceid)
        if self.alternateid and not re.fullmatch(r"\w+", self.alternateid, flags=re.ASCII):
            raise ValueError(f"Invalid alternateid: {self.alternateid}")
        self.sourcepath = self.sourcedatapath / f"{self.sourceid}.tsv"
        self.targetpath = (
            self.langdatapath / f"targets/{self.targetid}/{self.canon}_{self.targetid}.tsv"
        )
        assert self.targetpath.exists(), f"No such target TSV: {self.targetpath}"
        if self.alignmentpath_override is not None:
            self.alignmentpath = self.alignmentpath_override
        else:
            self.alignmentpath = (
                self.langdatapath / f"alignments/{self.targetid}/{self.identifier}.json"
            )
            assert self.alignmentpath.exists(), f"No such alignment file: {self.alignmentpath}"
        self.tomlpath = self.langdatapath / f"alignments/{self.targetid}/{self.identifier}.toml"

    def __repr__(self) -> str:
        return f"<AlignmentSet: {self.targetlanguage}, {self.identifier}>"

    def __hash__(self) -> int:
        return hash(self.sourceid + self.targetid + self.alternateid)

    @property
    def identifier(self) -> str:
        """Return a hyphen-delimited identifier string."""
        base = f"{self.sourceid}-{self.targetid}"
        if self.alternateid:
            base += f"-{self.alternateid}"
        return base

    @property
    def canon(self) -> str:
        """Return 'nt', 'ot', or 'X' for the source canon."""
        return SourceidEnum.get_canon(self.sourceid)

    @property
    def displaystr(self) -> str:
        return (
            f"\n        - sourcepath: {self.sourcepath}"
            f"\n        - targetpath: {self.targetpath}"
            f"\n        - alignmentpath: {self.alignmentpath}"
            f"\n        - tomlpath: {self.tomlpath}"
        )

    def comparable(self, other: "AlignmentSet") -> bool:
        assert isinstance(other, AlignmentSet), "Comparison must be to another AlignmentSet."
        for attr in ["sourceid", "targetlanguage"]:
            if getattr(self, attr) != getattr(other, attr):
                print(f"Different values for {attr}: {getattr(self, attr)} vs {getattr(other, attr)}")
                return False
        return True

    def check_files(self) -> bool:
        for pathattr in ["sourcepath", "targetpath", "alignmentpath", "tomlpath"]:
            pathval = getattr(self, pathattr)
            if not pathval.exists():
                raise ValueError(f"Missing {pathattr}: {pathval}")
        return True
