"""Manager: read and organise all burrito alignment data for an AlignmentSet."""

from collections import UserDict

from .AlignmentGroup import AlignmentGroup, AlignmentRecord
from .AlignmentSet import AlignmentSet
from .BadRecord import BadRecord
from .VerseData import VerseData
from .alignments import AlignmentsReader
from .source import Source, SourceReader
from .target import Target, TargetReader
from .util import groupby_bcv


class Manager(UserDict):
    """Read Burrito alignment data and organise it by BCV.

    self is a dict of BCV identifiers → VerseData instances.
    """

    tokentypeattrs: set[str] = {"source", "target"}

    def __init__(
        self,
        alignmentset: AlignmentSet,
        creator: str = "text-align",
        keeptargetwordpart: bool = False,
        keepbadrecords: bool = False,
        preloaded_reader: AlignmentsReader | None = None,
    ) -> None:
        super().__init__()
        self.keeptargetwordpart = keeptargetwordpart
        self.keepbadrecords = keepbadrecords
        self.alignmentset = alignmentset
        print(self.alignmentset.displaystr)
        self.sourceitems: SourceReader = self.read_sources()
        self.targetitems: TargetReader = self.read_targets()
        self.bcv = {
            "sources": groupby_bcv(list(self.sourceitems.values())),
            "targets": groupby_bcv(list(self.targetitems.values())),
            "target_sourceverses": groupby_bcv(
                list(self.targetitems.values()), bcvfn=lambda t: t.source_verse
            ),
        }
        if preloaded_reader is not None:
            self.alignmentsreader = preloaded_reader
        else:
            self.alignmentsreader = AlignmentsReader(
                alignmentset=alignmentset,
                keeptargetwordpart=self.keeptargetwordpart,
                keepbadrecords=self.keepbadrecords,
            )
        self.alignmentsreader.clean_alignments(self.sourceitems, self.targetitems)
        self.bcv["records"] = groupby_bcv(
            list(self.alignmentsreader.alignmentgroup.records), lambda r: r.source_bcv
        )
        self.data = self.bcv["versedata"] = {
            bcvid: self.make_versedata(bcvid, self.bcv["records"])
            for bcvid in self.bcv["records"]
        }
        self.check_integrity()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {len(self)} keys>"

    def read_sources(self) -> SourceReader:
        return SourceReader(self.alignmentset.sourcepath)

    def read_targets(self) -> TargetReader:
        return TargetReader(self.alignmentset.targetpath, keepwordpart=self.keeptargetwordpart)

    def make_versedata(
        self, bcvid: str, verserecords: dict[str, list[AlignmentRecord]]
    ) -> VerseData:
        alpairs = [
            (ardict["source"], ardict["target"])
            for ar in verserecords[bcvid]
            if (ardict := ar.asdict(withmaculaprefix=False))
        ]
        alinstpairs = [
            (sourceinst, targetinst)
            for sources, targets in alpairs
            if (sourceinst := [self.sourceitems[tok] for tok in sources if tok in self.sourceitems])
            if (targetinst := [self.targetitems[tok] for tok in targets if tok in self.targetitems])
        ]
        return VerseData(
            bcvid=bcvid,
            alignments=alinstpairs,
            sources=self.bcv["sources"].get(bcvid, []),
            targets=self.bcv["targets"].get(bcvid, []),
        )

    def display_record(self, alrec: AlignmentRecord) -> None:
        print(f"{alrec.meta.id} ------------")
        for src in alrec.source_selectors:
            print(f"Source: {self.sourceitems[src]._display if src else 'None'}")
        for trg in alrec.target_selectors:
            print(f"Target: {self.targetitems[trg]._display if trg else 'None'}")

    def check_integrity(self) -> None:
        if len(self.bcv["records"]) != len(self.bcv["versedata"]):
            print(
                f"{len(self.bcv['records'])} BCV records != "
                f"{len(self.bcv['versedata'])} VerseData instances."
            )
        if len(self.bcv["sources"]) < len(self.bcv["records"]):
            print(
                f"{len(self.bcv['sources'])} BCV sources < "
                f"{len(self.bcv['records'])} records."
            )

    def token_alignments(
        self, term: str, role: str = "source", tokenattr: str = "text", lowercase: bool = False
    ) -> list[Source | Target]:
        itemreader = self.sourceitems if role == "source" else self.targetitems
        tokendict = {
            token.id: token
            for token in itemreader.term_tokens(term, tokenattr=tokenattr, lowercase=lowercase)
        }
        selectorset = set(tokendict)
        selectorattr = "source_selectors" if role == "source" else "target_selectors"
        return [
            rec for rec in self.alignmentsreader.alignmentgroup.records
            if selectorset.intersection(getattr(rec, selectorattr))
        ]
