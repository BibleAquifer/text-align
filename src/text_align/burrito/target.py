"""Target/translation token data model and reader."""

from collections import UserDict, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional
from warnings import warn

from unicodecsv import DictReader, DictWriter
import regex

from biblelib.word import bcvwpid

from .BaseToken import BaseToken, asbool
from .util import groupby_bcv


@dataclass(order=True, repr=False)
class Target(BaseToken):
    """A translation target token."""

    source_verse: str = ""
    skip_space_after: bool = False
    exclude: bool = False
    required: bool = True
    transType: str = ""
    isPunc: bool = False
    isPrimary: bool = False
    msId: str = ""
    _boolean_fields: tuple = ("skip_space_after", "exclude", "required", "isPunc", "isPrimary")
    _input_fields: tuple = (
        ("id", "id"),
        ("altId", "altId"),
        ("text", "text"),
        ("source_verse", "source_verse"),
        ("skip_space_after", "skip_space_after"),
        ("exclude", "exclude"),
        ("transType", "transType"),
        ("isPunc", "isPunc"),
        ("isPrimary", "isPrimary"),
    )
    _output_fields: tuple = ("id", "text", "source_verse", "skip_space_after", "exclude")
    _punctre = regex.compile(r"\p{P}")
    __hash__ = BaseToken.__hash__

    def __post_init__(self) -> None:
        if not self.source_verse:
            self.source_verse = self.bcv
        for f in self._boolean_fields:
            fval = getattr(self, f)
            if isinstance(fval, str):
                setattr(self, f, self._truthy_asbool(fval))

    @staticmethod
    def fromjsondict(jdict: dict[str, Any]) -> "Target":
        newdict = jdict.copy()
        newdict["id"] = str(newdict["id"])
        if len(newdict["id"]) == 10:
            newdict["id"] = "0" + newdict["id"]
        return Target(**newdict)

    @property
    def same_source_verse(self) -> bool:
        return self.bcv == self.source_verse

    @property
    def _display(self) -> str:
        return f"{self.id}: {self.text}\t\t ({self.transType!r}, {self.isPunc}, {self.isPrimary})"

    @property
    def ispunc_token(self) -> bool:
        return bool(self._punctre.fullmatch(self.text))

    def display(self) -> None:
        print(self._display)

    def asdict(
        self,
        fields: tuple = _output_fields,
        omitfalse: bool = True,
        omittext: bool = False,
    ) -> dict[str, str]:
        outdict = {k: getattr(self, k) for k in fields}
        for f in fields:
            if f in self._boolean_fields:
                outdict[f] = "" if (omitfalse and not outdict[f]) else asbool(outdict[f])
        if omittext:
            for omitfield in ["altId", "text"]:
                if omitfield in fields:
                    outdict[omitfield] = "--"
        return outdict


class TargetReader(UserDict):
    """Read a target TSV into a dict keyed by token ID."""

    inmap = {v: k for k, v in Target._input_fields}

    def __init__(
        self,
        tsvpath: Path,
        idheader: str = "id",
        keepwordpart: bool = False,
        detect_punc: bool = False,
        strict: bool = False,
    ) -> None:
        super().__init__()
        self.tsvpath = tsvpath
        assert self.tsvpath.exists(), (
            f"No such path as {tsvpath}:\n"
            "pattern is targets/<targetid>/<canon>_<targetid>.tsv"
        )
        self.identifier = self.tsvpath.stem
        self.badtokens = {}
        with self.tsvpath.open("rb") as f:
            reader = DictReader(f, delimiter="\t", quotechar="\x00")
            for row in reader:
                assert idheader in row, f"TargetReader: missing ID header '{idheader}'"
                idrow = {("id" if k == idheader else k): v for k, v in row.items()} \
                    if idheader != "id" else row
                identifier = idrow["id"]
                if len(identifier) == 12 and not keepwordpart:
                    identifier = idrow["id"] = idrow["id"][0:11]
                deserialized = {self.inmap[k]: v for k, v in idrow.items() if k in self.inmap}
                if identifier in self:
                    warn(f"{identifier} is duplicated in {self.tsvpath}")
                token = Target(**deserialized)
                if detect_punc:
                    token.isPunc = token.ispunc_token
                self.data[identifier] = token
                if self.data[identifier].isempty:
                    if strict:
                        warn(f"Empty text for target token {identifier}")
                    self.badtokens[identifier] = self.data[identifier]
        if self.badtokens:
            print(
                f"{self.identifier} has {len(self.badtokens)} target tokens with empty text: "
                "see self.badtokens."
            )

    def add_isPunc(self) -> None:
        for tok in self.values():
            tok.isPunc = tok.ispunc_token

    @staticmethod
    def write_tsv(
        tokenlist: list[Target],
        outpath: Path,
        excludefn: Optional[Callable] = None,
        fields: tuple[str, ...] = ("id", "source_verse", "text", "skip_space_after", "exclude"),
    ) -> None:
        if excludefn and "exclude" not in fields:
            fields = fields + ("exclude",)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with outpath.open("wb") as f:
            writer = DictWriter(f, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            for targetinst in tokenlist:
                trgdict = targetinst.asdict(fields=fields)
                trgdict["id"] = bcvwpid.BCVWPID(trgdict["id"]).get_id(
                    prefix=False, part_index=False
                )
                if excludefn:
                    trgdict["exclude"] = excludefn(targetinst)
                writer.writerow(trgdict)

    def write_vref(self, outpath: Path) -> None:
        with outpath.open("w") as f:
            self.bcv = groupby_bcv(list(self.values()), bcvfn=lambda t: t.bcv)
            for bcv in self.bcv:
                f.write(f"{bcv}\n")

    def term_tokens(
        self, term: str, tokenattr: str = "text", lowercase: bool = False
    ) -> list[Target]:
        casedterm = term.lower() if lowercase else term
        return [
            token for token in self.values()
            if (tokattr := getattr(token, tokenattr))
            if (casedtokenattr := tokattr.lower() if lowercase else tokattr)
            if casedtokenattr == casedterm
        ]

    def get_source_bcvs(self) -> dict[str, list[Target]]:
        source_bcvs: dict[str, list[Target]] = defaultdict(list)
        for trg in self.data.values():
            source_bcvs[trg.source_verse].append(trg)
        return source_bcvs
