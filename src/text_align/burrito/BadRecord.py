"""Support for logging errors in alignment records."""

from dataclasses import dataclass
from enum import Enum

from .AlignmentGroup import AlignmentRecord


class Reason(Enum):
    """Reasons why an alignment record is considered bad."""

    ALIGNEDEXCLUDE = "An excluded token is aligned"
    DUPLICATESOURCE = "Source selector is included in multiple records"
    DUPLICATETARGET = "Target selector is included in multiple records"
    EMPTYSOURCE = "Empty string in source selectors"
    EMPTYTARGET = "Empty string in target selectors"
    MISSINGSOURCE = "Token reference is missing from sourceitems"
    MISSINGTARGETSOME = "Some token references are missing from targetitems"
    MISSINGTARGETALL = "All token references are missing from targetitems"
    NOSOURCE = "No source selectors"
    NOTARGET = "No target selectors"
    UNKNOWN = "Uncategorized error"


@dataclass
class BadRecord:
    """Container for data about a malformed alignment record."""

    identifier: str
    record: AlignmentRecord
    reason: Reason
    data: tuple = ()

    def __repr__(self) -> str:
        basestr = f"<BadRecord ({self.identifier}): '{self.reason.value}'"
        if self.data:
            basestr += ", " + repr(self.data)
        return basestr + ">"

    @property
    def display(self) -> str:
        basestr = f"{self.identifier!r}: {self.reason.name}."
        if self.reason == Reason.ALIGNEDEXCLUDE:
            basestr += f" Targets: {self.record.target_selectors}"
        elif self.reason in (Reason.DUPLICATESOURCE, Reason.DUPLICATETARGET):
            basestr += f" Duplicates: {self.data}"
        elif self.reason in (
            Reason.EMPTYSOURCE, Reason.EMPTYTARGET, Reason.NOSOURCE, Reason.NOTARGET,
        ):
            basestr += f" {self.data}"
        elif self.reason in (Reason.MISSINGTARGETALL, Reason.MISSINGTARGETSOME):
            basestr += f" Sources: {self.record.source_selectors}, Missing targets: {self.data}"
        elif self.reason == Reason.MISSINGSOURCE:
            basestr += f" Missing sources: {self.data}, targets: {self.record.target_selectors}"
        else:
            basestr += (
                f" Sources: {self.record.source_selectors}, "
                f"targets: {self.record.target_selectors}"
            )
        return basestr
