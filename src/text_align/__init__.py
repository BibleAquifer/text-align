"""Tools for creating and improving Bible text alignments."""

from enum import Enum
from pathlib import Path
import re

from .strongs import normalize_strongs

ROOT = Path(__file__).parent.parent.parent
DATAPATH = ROOT / "data"
SRCPATH = ROOT / "src"

SOURCES = DATAPATH / "sources"
TARGETS = DATAPATH / "targets"
ALIGNMENTS = DATAPATH / "alignments"


class SourceidEnum(str, Enum):
    """Valid source text identifiers."""

    BHB = "BHB"
    BGNT = "BGNT"
    NA27 = "NA27"
    NA28 = "NA28"
    SBLGNT = "SBLGNT"
    UGNT = "UGNT"
    UHB = "UHB"
    WLC = "WLC"
    WLCM = "WLCM"

    @property
    def canon(self) -> str:
        """Return 'ot' or 'nt' for the canon."""
        if self.value in {"BHB", "UHB", "WLC", "WLCM"}:
            return "ot"
        elif self.value in {"BGNT", "NA27", "NA28", "SBLGNT", "UGNT"}:
            return "nt"
        else:
            raise ValueError(f"Unknown canon for SourceidEnum: {self.value}")

    @staticmethod
    def get_canon(sourceid: str) -> str:
        """Return a canon string for recognized sources, else 'X'."""
        try:
            return SourceidEnum(sourceid).canon
        except ValueError:
            return "X"


def get_canonid(bcv: str) -> str:
    """Return 'nt' or 'ot' for a BCVish string.

    Works for book, chapter, verse, and full BCVWPID identifiers.
    """
    otcanonre = re.compile(r"^[0-3][0-9]")
    ntcanonre = re.compile(r"^[4-6][0-9]")
    notntcanonre = re.compile(r"^6[7-9]")
    if otcanonre.match(bcv):
        return "ot"
    elif ntcanonre.match(bcv) and not notntcanonre.match(bcv):
        return "nt"
    else:
        raise ValueError(f"Invalid BCVish id value: {bcv}")


CANONIDS: set[str] = {"nt", "ot", "protestant"}

__all__ = [
    "ROOT",
    "DATAPATH",
    "SRCPATH",
    "SOURCES",
    "TARGETS",
    "ALIGNMENTS",
    "CANONIDS",
    "SourceidEnum",
    "get_canonid",
    "normalize_strongs",
]
