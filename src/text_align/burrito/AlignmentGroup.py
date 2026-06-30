"""Data model for Scripture Burrito alignment records and groups.

Implements the Scripture Burrito Alignment Specification v0.4:
https://github.com/bible-technology/alignment-spec/blob/main/spec.md
"""

from dataclasses import dataclass, field, fields
import datetime as dt
from functools import total_ordering
from itertools import groupby
from typing import Any, Optional

from biblelib.word import bcvwpid

from text_align import SourceidEnum
from .AlignmentType import TranslationType
from .source import macula_prefixer


@dataclass
class Document:
    """Data for an alignment document reference."""

    docid: str
    scheme: str = "BCVWP"
    sourceid: Optional[SourceidEnum] = None

    def __post_init__(self) -> None:
        try:
            self.sourceid = SourceidEnum(self.docid)
        except ValueError:
            self.sourceid = None
            if self.scheme == "BCVWP":
                self.scheme = "BCVW"

    def asdict(self) -> dict[str, Any]:
        return {"docid": self.docid, "scheme": self.scheme}


@dataclass(order=True)
class AlignmentReference:
    """A reference to one or more tokens in a document."""

    document: Document
    selectors: list[str]

    def __post_init__(self) -> None:
        self.selectors = sorted(self.selectors)

    def __repr__(self) -> str:
        return f"<{self.docid}: {self.selectors}>"

    @property
    def docid(self) -> str:
        return self.document.docid

    @property
    def scheme(self) -> str:
        return self.document.scheme

    @property
    def incomplete(self) -> bool:
        return any(sel == "MISSING" for sel in self.selectors)

    def asdict(self, hoist: bool = True) -> dict[str, Any]:
        refdict: dict[str, Any] = {"selectors": self.selectors}
        if not hoist:
            refdict.update({"docid": self.docid, "scheme": self.scheme})
        return refdict


@dataclass
class Metadata:
    """Metadata for an alignment group or record.

    All fields are optional; creator and created are strongly recommended.
    """

    conformsTo: str = ""
    contributor: str = ""
    created: Optional[dt.datetime] = None
    creator: str = ""
    coverage: str = ""
    description: str = ""
    id: str = ""
    is_idiom: bool = False
    note: str = ""
    origin: str = ""
    secondary: dict = field(default_factory=dict)
    status: str = ""
    _fieldnames: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self._fieldnames = tuple(
            sorted(f.name for f in fields(self) if f.name != "_fieldnames")
        )

    def __repr__(self) -> str:
        attrstr = " ".join(
            f"{f}={repr(fattr)}" for f in self._fieldnames if (fattr := getattr(self, f))
        )
        return f"Metadata({attrstr})"

    def asdict(self) -> dict[str, Any]:
        return {f: fattr for f in sorted(self._fieldnames) if (fattr := getattr(self, f))}


@dataclass
@total_ordering
class AlignmentRecord:
    """A single alignment record."""

    meta: Metadata
    references: dict[str, AlignmentReference]
    type: TranslationType = field(default_factory=TranslationType)

    def __post_init__(self) -> None:
        for role in self.roles:
            assert role in self.references, f"role missing from references: {role}"
        assert len(self.roles) == len(self.references), "different numbers of roles and references"

    def __repr__(self) -> str:
        return f"<AlignmentRecord: {repr(self.references)}>"

    def __hash__(self) -> int:
        return hash(self.identifier)

    def __eq__(self, other) -> bool:
        assert isinstance(other, AlignmentRecord), f"Not an AlignmentRecord: {other}"
        return self.source_selectors[0] == other.source_selectors[0]

    def __lt__(self, other) -> bool:
        assert isinstance(other, AlignmentRecord), f"Not an AlignmentRecord: {other}"
        return self.source_selectors[0] < other.source_selectors[0]

    @property
    def identifier(self) -> str:
        return self.meta.id

    @property
    def roles(self) -> tuple[str, str]:
        return self.type.roles

    def get_selectors(self, role: str) -> list[str]:
        assert role in self.roles, f"Invalid role: {role}"
        return self.references[role].selectors

    @property
    def source_selectors(self) -> list[str]:
        return self.get_selectors("source")

    @property
    def target_selectors(self) -> list[str]:
        return self.get_selectors("target")

    @property
    def source_bcv(self) -> str:
        if self.source_selectors:
            return [bcvwpid.to_bcv(sel) for sel in self.source_selectors][0]
        return ""

    @property
    def incomplete(self) -> bool:
        return any(ref.incomplete for ref in self.references.values())

    def asdict(
        self,
        positional: bool = False,
        withmeta: bool = True,
        withmaculaprefix: bool = False,
    ) -> dict[str, Any]:
        recdict: dict[str, Any] = {}
        if positional:
            if not withmaculaprefix:
                raise NotImplementedError("Positional without maculaprefix is not yet supported.")
            recdict["references"] = self.references.items()
        else:
            sourcerefs = self.references["source"].selectors
            if withmaculaprefix:
                sourcerefs = [macula_prefixer(s) for s in sourcerefs]
            recdict["source"] = sourcerefs
            recdict["target"] = self.references["target"].selectors
        if withmeta:
            recdict["meta"] = self.meta.asdict()
        return {k: recdict[k] for k in sorted(recdict)}


@dataclass
class AlignmentGroup:
    """A full set of alignment records for a source+target pair."""

    documents: tuple[Document, Document]
    meta: Metadata
    records: list[AlignmentRecord]
    roles: tuple[str, str] = ("source", "target")
    sourcedocid: str = ""
    canon: str = ""
    _type: str = ""
    _hoist_docid: bool = True

    def __post_init__(self) -> None:
        typeset = {rec.type.type for rec in self.records if self.records}
        assert len(typeset) == 1, f"Multiple AlignmentRecord types found: {typeset}"
        self._type = typeset.pop()
        assert len(self.documents) == len(self.roles), (
            f"Must have same number of documents and roles: {self.documents}, {self.roles}"
        )
        sourcedocid = self.documents[0].sourceid or self.documents[1].sourceid
        assert sourcedocid, (
            f"Neither {self.documents[0].docid} nor {self.documents[1].docid} are recognized "
            "source texts: check SourceidEnum for completeness."
        )
        self.canon = sourcedocid.canon
        self.sourcedocid = sourcedocid.value

    def __repr__(self) -> str:
        docids = tuple(doc.asdict()["docid"] for doc in self.documents)
        return f"<AlignmentGroup{docids}: {len(self.records)} records>"

    def asdict(self, hoist: bool = True) -> dict[str, Any]:
        return {
            "meta": self.meta.asdict(),
            "type": self._type,
            "records": [rec.asdict(positional=False, withmeta=False) for rec in self.records],
        }

    def verserecords(self) -> dict[str, list[AlignmentRecord]]:
        """Return a dict mapping source BCV references to their alignment records."""
        return {k: list(g) for k, g in groupby(self.records, lambda r: r.source_bcv)}


@dataclass
class TopLevelGroups:
    """A pair of AlignmentGroups (one OT, one NT)."""

    groups: tuple[AlignmentGroup, AlignmentGroup]
    format: str = "alignment"
    version: str = "0.4"
    sourcedocids: tuple[str, str] = ()
    targetdocid: str = ""

    def __post_init__(self) -> None:
        assert len(self.groups) == 2, "There must be exactly two groups."
        assert self.groups[0].roles == self.groups[1].roles, (
            f"Roles must match: {self.groups[0].roles}, {self.groups[1].roles}"
        )
        assert self.groups[0].meta.conformsTo == self.groups[1].meta.conformsTo, (
            f"meta.conformsTo values must match: "
            f"{self.groups[0].meta.conformsTo}, {self.groups[1].meta.conformsTo}"
        )
        targetdocids = list(
            {group.documents[group.roles.index("target")].docid for group in self.groups}
        )
        assert len(targetdocids) == 1, f"OT and NT target docids must match: {targetdocids}"
        self.targetdocid = targetdocids[0]
        assert {self.groups[0].canon, self.groups[1].canon} == {"ot", "nt"}, (
            "Both OT and NT canons are required."
        )
        self.sourcedocids = (self.groups[0].sourcedocid, self.groups[1].sourcedocid)

    def __repr__(self) -> str:
        return f"<TopLevelGroups({self.targetdocid}): {self.sourcedocids}>"

    def asdict(self, hoist: bool = True) -> dict[str, Any]:
        return {
            "format": self.format,
            "version": self.version,
            "groups": [self.groups[0].asdict(hoist=hoist), self.groups[1].asdict(hoist=hoist)],
        }
