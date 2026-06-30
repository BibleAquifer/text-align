"""Base class for Source and Target tokens."""

from dataclasses import dataclass
import re

from biblelib.word import bcvwpid


@dataclass(order=True)
class BaseToken:
    """Common structure for source and target tokens."""

    # Word identifier in BBCCCVVVWWWP format
    id: str
    # Surface form
    text: str
    altId: str = ""
    aligned: bool = False
    text_unique: str = ""
    _truthyre = re.compile("(?i)(y|true)$")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def bcv(self) -> str:
        """Return the BCV-format verse reference for this token."""
        return str(bcvwpid.to_bcv(self.id))

    def to_bcv(self) -> str:
        """Return the BCV-format verse reference (callable variant)."""
        return str(self.bcv)

    @property
    def idtext(self) -> tuple[str, str]:
        """Return a tuple of (id, text)."""
        return (self.id, self.text)

    @property
    def bare_id(self) -> str:
        """Return the ID minus any canon prefix (n/o)."""
        return self.id[1:] if self.id[0].isalpha() else self.id

    @property
    def isempty(self) -> bool:
        """True if token text is the empty string."""
        return self.text == ""

    def _truthy_asbool(self, value: bool | str) -> bool:
        """Return a bool for truthy string/bool values."""
        return bool(self._truthyre.match(value))


def asbool(value: bool | str) -> str:
    """Return 'y' or 'n' for a boolean value."""
    return "y" if bool(value) else "n"


def bare_id(identifier: str) -> str:
    """Strip any canon prefix (n/o) from a BCVWPID identifier."""
    assert bcvwpid.is_bcvwpid(identifier), f"'{identifier}' does not look like a valid BCVWPID."
    return identifier[1:] if identifier[0].isalpha() else identifier
