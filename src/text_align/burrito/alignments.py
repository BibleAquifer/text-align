"""Read and write alignment data in Scripture Burrito format."""

from collections import defaultdict
from dataclasses import fields as dataclass_fields
import json
from pathlib import Path
from typing import Any, Optional, TextIO

from .AlignmentGroup import Document, Metadata, AlignmentGroup, AlignmentReference, AlignmentRecord
from .AlignmentSet import AlignmentSet
from .AlignmentType import TranslationType
from .BadRecord import BadRecord, Reason
from .source import SourceReader, macula_unprefixer
from .target import TargetReader


def bad_reason(
    arec: AlignmentRecord, sourceitems: SourceReader, targetitems: TargetReader
) -> Optional[BadRecord]:
    """Return a BadRecord if the alignment record is malformed, else None."""
    arecdict = arec.asdict(withmaculaprefix=False)
    badrecdict = {"identifier": arec.identifier, "record": arec}
    if not arecdict["source"]:
        return BadRecord(**badrecdict, reason=Reason.NOSOURCE)
    elif "" in arecdict["source"]:
        return BadRecord(**badrecdict, reason=Reason.EMPTYSOURCE)
    elif not arecdict["target"]:
        return BadRecord(**badrecdict, reason=Reason.NOTARGET)
    elif "" in arecdict["target"]:
        return BadRecord(**badrecdict, reason=Reason.EMPTYTARGET)
    elif any(sel not in sourceitems for sel in arecdict["source"]):
        missing = [sel for sel in arecdict["source"] if sel not in sourceitems]
        return BadRecord(**badrecdict, reason=Reason.MISSINGSOURCE, data=missing)
    elif any(sel not in targetitems for sel in arecdict["target"]):
        missing = [sel for sel in arecdict["target"] if sel not in targetitems]
        if set(arecdict["target"]).symmetric_difference(set(missing)):
            return BadRecord(**badrecdict, reason=Reason.MISSINGTARGETSOME, data=missing)
        else:
            return BadRecord(**badrecdict, reason=Reason.MISSINGTARGETALL, data=missing)
    elif any(targetitems[sel].exclude for sel in arecdict["target"]):
        excluded = [sel for sel in arecdict["target"] if targetitems[sel].exclude]
        return BadRecord(**badrecdict, reason=Reason.ALIGNEDEXCLUDE, data=excluded)
    return None


class AlignmentsReader:
    """Read alignment data from a Scripture Burrito JSON file."""

    scheme = "BCVWP"
    altype: TranslationType = TranslationType()

    def __init__(
        self,
        alignmentset: AlignmentSet,
        keeptargetwordpart: bool = False,
        keepbadrecords: bool = False,
        keeprejected: bool = False,
        _preloaded_data: Optional[dict] = None,
    ) -> None:
        self.alignmentset = alignmentset
        self.keeptargetwordpart = keeptargetwordpart
        self.keepbadrecords = keepbadrecords
        self.sourcedoc = Document(docid=self.alignmentset.sourceid, scheme=self.scheme)
        self.targetdoc = Document(docid=self.alignmentset.targetid, scheme=self.scheme)
        self.badrecords: Optional[dict[str, list[BadRecord]]] = defaultdict(list)
        self.rejected: dict[str, AlignmentRecord] = {}
        self.neq_source: frozenset[str] = frozenset()
        self.neq_target: frozenset[str] = frozenset()
        self.group_meta: dict = {}
        self.per_chapter_meta: dict[str, dict] = {}  # BB-CCC → group meta; set by from_chapter_files
        self.alignmentgroup: AlignmentGroup = self.read_alignments(
            keeprejected=keeprejected, data=_preloaded_data
        )

    def _targetid(self, targetid: str) -> str:
        if not self.keeptargetwordpart and len(targetid) == 12:
            return targetid[:11]
        return targetid

    def _make_record(self, alrec: dict[str, Any]) -> Optional[AlignmentRecord]:
        metadatadict = dict(alrec.get("meta") or {})
        # upgrade: 0.2.1 renamed 'process' to 'origin'
        if "process" in metadatadict:
            metadatadict["origin"] = metadatadict["process"]
            del metadatadict["process"]
        metadatadict.setdefault("status", "created")
        # filter to known Metadata fields to avoid TypeError on SB 0.4 extension keys
        known_fields = {f.name for f in dataclass_fields(Metadata) if f.name != "_fieldnames"}
        metadatadict = {k: v for k, v in metadatadict.items() if k in known_fields}
        meta = Metadata(**metadatadict)
        if not alrec.get("source"):
            print(f"No source selectors for {meta.id or '(unknown)'}: dropping record.")
            return None
        alrec["source"] = [macula_unprefixer(src) for src in alrec["source"]]
        # SB 0.4 records have no per-record id; synthesize from first source selector
        if not meta.id:
            meta.id = alrec["source"][0]
        sourceref = AlignmentReference(document=self.sourcedoc, selectors=alrec["source"])
        trgselectors = [self._targetid(tid) for tid in alrec["target"]]
        targetref = AlignmentReference(document=self.targetdoc, selectors=trgselectors)
        return AlignmentRecord(
            meta=meta, references={"source": sourceref, "target": targetref}, type=self.altype
        )

    @classmethod
    def from_chapter_files(
        cls,
        paths: list[Path],
        alignmentset: AlignmentSet,
        keeptargetwordpart: bool = False,
        keepbadrecords: bool = False,
        keeprejected: bool = False,
    ) -> "AlignmentsReader":
        """Create an AlignmentsReader by merging records from multiple chapter JSON files.

        Each file is expected to be an SB 0.4 alignment JSON covering one chapter.
        NEQ sets and records are merged across all files.  ``group_meta`` is taken
        from the first file (alphabetically) and shared across all chapters.
        """
        merged_records: list[dict] = []
        merged_neq_source: list[str] = []
        merged_neq_target: list[str] = []
        first_meta: Optional[dict] = None
        last_group: dict = {}
        per_chapter_meta: dict[str, dict] = {}

        for path in sorted(paths):
            with path.open("rb") as f:
                raw = json.load(f)
            group = raw["groups"][0] if "groups" in raw else raw
            last_group = group
            file_meta = dict(group.get("meta", {}))
            if first_meta is None:
                first_meta = file_meta
            # Derive BB-CCC chapter key from filename stem (e.g. WLCM-OENGB-66-007-manual → 66-007)
            parts = path.stem.split("-")
            if len(parts) >= 3:
                chapter_key = f"{parts[-3]}-{parts[-2]}"
                per_chapter_meta[chapter_key] = file_meta
            neq = group.get("meta", {}).get("nonEquivalent", {})
            merged_neq_source.extend(neq.get("source", []))
            merged_neq_target.extend(neq.get("target", []))
            merged_records.extend(group.get("records", []))

        merged_meta: dict = dict(first_meta or {})
        if merged_neq_source or merged_neq_target:
            non_equiv: dict = {}
            if merged_neq_source:
                non_equiv["source"] = merged_neq_source
            if merged_neq_target:
                non_equiv["target"] = merged_neq_target
            merged_meta["nonEquivalent"] = non_equiv
        elif "nonEquivalent" in merged_meta:
            del merged_meta["nonEquivalent"]

        merged_data: dict = {
            "format": "alignment",
            "version": "0.4",
            "groups": [{
                "type": "translation",
                "meta": merged_meta,
                "documents": last_group.get("documents", []),
                "roles": last_group.get("roles", ["source", "target"]),
                "records": merged_records,
            }],
        }

        reader = cls(
            alignmentset=alignmentset,
            keeptargetwordpart=keeptargetwordpart,
            keepbadrecords=keepbadrecords,
            keeprejected=keeprejected,
            _preloaded_data=merged_data,
        )
        reader.per_chapter_meta = per_chapter_meta
        return reader

    def read_alignments(self, keeprejected: bool = False, data: Optional[dict] = None) -> AlignmentGroup:
        if data is None:
            with self.alignmentset.alignmentpath.open("rb") as f:
                data = json.load(f)
        if isinstance(data, list):
            raise ValueError(
                f"{self.alignmentset.alignmentpath} should be an object, not a list."
            )
        # Handle SB 0.4 groups wrapper; extract group-level NEQ sets
        if "groups" in data:
            agroupdict = data["groups"][0]
            neq = agroupdict["meta"].get("nonEquivalent", {})
            self.neq_source = frozenset(neq.get("source", []))
            self.neq_target = frozenset(neq.get("target", []))
        else:
            agroupdict = data
        self.group_meta = dict(agroupdict.get("meta", {}))
        known_fields = {f.name for f in dataclass_fields(Metadata) if f.name != "_fieldnames"}
        raw_meta = {k: v for k, v in agroupdict["meta"].items() if k in known_fields}
        meta = Metadata(**raw_meta)
        assert agroupdict["type"] == self.altype.type, (
            f"Unexpected alignment type: {agroupdict['type']}"
        )
        records: list[AlignmentRecord] = [
            record
            for alrec in agroupdict["records"]
            if (record := self._make_record(alrec))
        ]
        self.rejected = {
            recid: rec for rec in records
            if rec.meta.status == "rejected"
            if (recid := rec.meta.id)
        }
        if not keeprejected:
            records = [rec for rec in records if rec.meta.id not in self.rejected]
            if self.rejected:
                print(f"Dropping {len(self.rejected)} rejected records")
        return AlignmentGroup(
            documents=(self.sourcedoc, self.targetdoc),
            meta=meta,
            records=sorted(records),
            roles=records[0].roles,
        )

    def _clean_corpus(self, records: dict[str, AlignmentRecord]) -> None:
        def _flag_dupes(dupedict: dict[str, list[AlignmentRecord]], reason: Reason) -> None:
            for firstbad, duped_records in dupedict.items():
                for rec in duped_records:
                    recid = rec.identifier
                    self.badrecords[recid].append(
                        BadRecord(identifier=recid, record=rec, reason=reason, data=firstbad)
                    )

        sourceselectors: dict[str, list[AlignmentRecord]] = defaultdict(list)
        targetselectors: dict[str, list[AlignmentRecord]] = defaultdict(list)
        for rec in records.values():
            for srcsel in rec.source_selectors:
                sourceselectors[srcsel].append(rec)
            for trgsel in rec.target_selectors:
                targetselectors[trgsel].append(rec)
        _flag_dupes(
            {s: r for s, r in sourceselectors.items() if len(r) > 1}, Reason.DUPLICATESOURCE
        )
        _flag_dupes(
            {t: r for t, r in targetselectors.items() if len(r) > 1}, Reason.DUPLICATETARGET
        )

    def clean_alignments(self, sourceitems: SourceReader, targetitems: TargetReader) -> None:
        alrecdict = {arec.meta.id: arec for arec in self.alignmentgroup.records}
        for recid, arec in alrecdict.items():
            if badrec := bad_reason(arec, sourceitems, targetitems):
                self.badrecords[recid].append(badrec)
        self._clean_corpus(alrecdict)
        if self.badrecords:
            keepmsg = "Keeping" if self.keepbadrecords else "Dropping"
            print(f"{keepmsg} {len(self.badrecords)} bad alignment records.")
            for reason in Reason:
                rcount = sum(
                    1 for mallist in self.badrecords.values()
                    for mal in mallist if mal.reason == reason
                )
                if rcount:
                    print(f"{reason.value}\t{rcount}")
        if not self.keepbadrecords:
            self.alignmentgroup.records = [
                rec for recid, rec in alrecdict.items() if recid not in self.badrecords
            ]

    def filter_books(self, keep: tuple = ()) -> AlignmentGroup:
        filtered = [
            rec for rec in self.alignmentgroup.records
            if (bcv := rec.source_bcv) and bcv[:2] in keep
        ]
        return AlignmentGroup(
            documents=self.alignmentgroup.documents,
            meta=self.alignmentgroup.meta,
            records=filtered,
        )


def write_alignment_group(group: AlignmentGroup, f: TextIO, hoist: bool = True) -> None:
    """Write an AlignmentGroup as Scripture Burrito JSON, one record per line."""

    def _write_documents(out: TextIO, documents: tuple[Document, Document]) -> None:
        out.write(' "documents": [\n')
        out.write("    " + json.dumps(documents[0].asdict()) + ",\n")
        out.write("    " + json.dumps(documents[1].asdict()) + "\n")
        out.write(" ],\n")

    def _write_meta(out: TextIO, meta: Metadata) -> None:
        out.write(' "meta": ' + json.dumps(meta.asdict()) + ",\n")

    f.write("{\n")
    _write_documents(f, group.documents)
    _write_meta(f, group.meta)
    f.write(f' "roles": {json.dumps(group.roles)},\n')
    f.write(f' "type": "{group._type}",\n "records": [\n ')
    for arec in group.records[:-1]:
        json.dump(arec.asdict(), f)
        f.write(",\n ")
    json.dump(group.records[-1].asdict(), f)
    f.write("\n ]}")
