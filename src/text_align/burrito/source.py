"""Source token data model and reader."""

from collections import UserDict
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
import re
from typing import Any, Iterable
import unicodedata
from warnings import warn

from unicodecsv import DictReader, DictWriter

from biblelib.word import bcvwpid

from text_align import normalize_strongs, get_canonid
from .BaseToken import BaseToken

PREFIXRE = re.compile(r"^[no]")


def macula_prefixer(bcvwp: str) -> str:
    """Return a BCVWP reference with a canon prefix ('n' for NT, 'o' for OT)."""
    otcanonre = re.compile(r"^[0-3][0-9]")
    ntcanonre = re.compile(r"^[4-6][0-9]")
    notntcanonre = re.compile(r"^6[7-9]")
    if PREFIXRE.match(bcvwp):
        return bcvwp
    elif otcanonre.match(bcvwp):
        return "o" + bcvwp
    elif ntcanonre.match(bcvwp) and not notntcanonre.match(bcvwp):
        return "n" + bcvwp
    else:
        raise ValueError(f"Unable to add macula prefix to {bcvwp}")


def macula_unprefixer(bcvwp: str) -> str:
    """Drop a canon prefix ('n' or 'o') from a BCVWP string, if present."""
    return bcvwp[1:] if PREFIXRE.match(bcvwp) else bcvwp


@dataclass(order=True, repr=False)
class Source(BaseToken):
    """A source/manuscript token (SBLGNT or WLCM)."""

    strong: str = ""
    gloss: str = ""
    gloss2: str = ""
    lemma: str = ""
    pos: str = ""
    morph: str = ""
    required: bool = True
    _output_fields: tuple = (
        ("id", "id"),
        ("altId", "altId"),
        ("text", "text"),
        ("strong", "strongs"),
        ("gloss", "gloss"),
        ("gloss2", "gloss2"),
        ("lemma", "lemma"),
        ("pos", "pos"),
        ("morph", "morph"),
        ("required", "required"),
    )
    _input_fields: tuple = tuple(dict(_output_fields).keys())
    __hash__ = BaseToken.__hash__

    def __post_init__(self) -> None:
        def normalize(s: str) -> str:
            return unicodedata.normalize("NFKC", s)

        stdid = bcvwpid.BCVWPID(self.id)
        self.id = stdid.get_id()
        is_nt = 66 >= int(stdid.to_bid) >= 40
        if is_nt:
            self.altId = normalize(self.altId)
            self.text = normalize(self.text)
            self.lemma = normalize(self.lemma)
            if len(self.id) == 12:
                self.id = self.id[:11]
        if self.strong and self.strong != "H":
            if re.match(r"[AGH]", self.strong):
                prefix = self.strong[0]
            else:
                prefix = "G" if is_nt else "G"
                self.strong = prefix + self.strong
            try:
                self.strong = normalize_strongs(self.strong, prefix=prefix)
            except ValueError:
                warn(f"Failed to normalize Strong's '{self.strong}' in {self.id}")
        self.required = self.is_content

    @property
    def is_content(self) -> bool:
        """True if part of speech is content-bearing (noun, verb, adj, adv)."""
        return self.pos in {"noun", "verb", "adj", "adv"}

    def _is_pos(self, pos: str) -> bool:
        return self.pos == pos

    def is_noun(self) -> bool:
        return self._is_pos("noun")

    @property
    def maculaid(self) -> str:
        return macula_prefixer(self.id)

    @property
    def tokenid(self) -> str:
        return self.bare_id

    @staticmethod
    def fromjsondict(jdict: dict[str, Any]) -> "Source":
        newdict = jdict.copy()
        newdict["id"] = str(newdict["id"])
        if len(newdict["id"]) == 11:
            newdict["id"] = newdict["id"].zfill(12)
        newdict["altId"] = newdict["altId"].replace(chr(8206), "")
        newdict["text"] = newdict["text"].replace(chr(8206), "")
        sourceinst = Source(**newdict)
        if "required" in newdict and newdict["required"] != sourceinst.required:
            warn(f"Overwriting 'required' value {sourceinst.required} for {sourceinst.id}")
            sourceinst.required = newdict["required"]
        return sourceinst

    @property
    def _display(self) -> str:
        return f"{self.id}: {self.text}\t\t ({self.gloss}, {self.lemma}, {self.pos})"

    def display(self) -> None:
        print(self._display)

    def asdict(self, omittext: bool = False, essential: bool = False) -> dict[str, str]:
        fdict = dict(self._output_fields)
        outdict: dict[str, str] = {fdict[k]: getattr(self, k) for k in fdict}
        normid = bcvwpid.BCVWPID(outdict["id"])
        part_index = normid.canon_prefix != "n"
        outdict["id"] = normid.get_id(prefix=True, part_index=part_index)
        if omittext:
            outdict["altId"] = "--"
            outdict["text"] = "--"
        if essential:
            raise NotImplementedError("The essential parameter has been deprecated.")
        return outdict


class SourceReader(UserDict):
    """Read a source TSV (SBLGNT.tsv or WLCM.tsv) into a dict keyed by token ID."""

    inmap = {v: k for k, v in Source._output_fields}
    canon: str = ""

    def __init__(self, tsvpath: Path, idheader: str = "id") -> None:
        super().__init__()
        self.tsvpath = tsvpath
        with self.tsvpath.open("rb") as f:
            reader = DictReader(f, delimiter="\t", quotechar="\x00")
            for row in reader:
                assert idheader in row, f"Missing ID header '{idheader}'"
                idrow = {("id" if k == idheader else k): v for k, v in row.items()} \
                    if idheader != "id" else row
                identifier = idrow["id"]
                deserialized = {self.inmap[k]: v for k, v in idrow.items() if k in self.inmap}
                if identifier in self:
                    warn(f"{identifier} is duplicated in {self.tsvpath}")
                srctoken = Source(**deserialized)
                self.data[srctoken.tokenid] = srctoken
        self.canon = get_canonid(list(self.data.keys())[0])

    def vocabulary(self, tokenattr: str = "text", lower: bool = False) -> list[str]:
        if lower:
            vocab = {getattr(t, tokenattr).lower() for t in self.values()}
        else:
            vocab = {getattr(t, tokenattr) for t in self.values()}
        return sorted(vocab)

    def write_tsv(self, outpath: Path, essential: bool = False) -> None:
        fields = list(dict(Source._output_fields).values())
        if essential:
            fields += ["exclude"]
        with outpath.open("wb") as f:
            writer = DictWriter(f, fieldnames=fields, delimiter="\t")
            writer.writeheader()
            for sourceinst in self.values():
                srcdict = sourceinst.asdict(essential=essential)
                srcdict["id"] = bcvwpid.BCVWPID(srcdict["id"]).get_id(
                    prefix=True, part_index=(self.canon == "ot")
                )
                writer.writerow(srcdict)

    def term_tokens(
        self, term: str, tokenattr: str = "text", lowercase: bool = False
    ) -> list[Source]:
        casedterm = term.lower() if lowercase else term
        return [
            token for token in self.values()
            if (tokattr := getattr(token, tokenattr))
            if (casedtokenattr := tokattr.lower() if lowercase else tokattr)
            if casedtokenattr == casedterm
        ]

    def _book_tokens(
        self, tokenattr: str = "text", lower: bool = False, is_content: bool = False
    ) -> dict[str, list[Source]]:
        def tokenattrfn(tok: Source) -> str:
            return getattr(tok, tokenattr).lower() if lower else getattr(tok, tokenattr)

        def to_bid(src: Source) -> str:
            return src.to_bcv()[:2]

        book_tokens: dict[str, list[Source]] = {
            k: list(g) for k, g in groupby(self.values(), to_bid)
        }
        if is_content:
            book_tokens = {
                bookid: [tok for tok in tokens if tok.is_content]
                for bookid, tokens in book_tokens.items()
            }
        return {
            bookid: [tokenattrfn(tok) for tok in tokens]
            for bookid, tokens in book_tokens.items()
        }

    def book_token_counts(self, lower: bool = False, is_content: bool = False) -> dict[str, int]:
        return {bookid: len(tokens) for bookid, tokens in
                self._book_tokens(lower=lower, is_content=is_content).items()}

    def book_type_counts(
        self, tokenattr: str = "text", lower: bool = False, is_content: bool = False
    ) -> dict[str, int]:
        return {bookid: len(set(tokenattrs)) for bookid, tokenattrs in
                self._book_tokens(tokenattr=tokenattr, lower=lower, is_content=is_content).items()}
