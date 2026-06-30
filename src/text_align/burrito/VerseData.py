"""Verse-level alignment data management."""

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pandas as pd

from .source import Source
from .target import Target


class DiffReason(Enum):
    """Reasons two VerseData instances differ."""

    DIFFLEN = "Different number of alignments"
    DIFFSOURCES = "Source selectors differ"
    DIFFTARGETS = "Target selectors differ"


@dataclass
class DiffRecord:
    """Data about a difference between two alignment sets at the same verse."""

    bcvid: str
    sources1: tuple[Source, ...]
    targets1: tuple[Target, ...]
    sources2: tuple[Source, ...]
    targets2: tuple[Target, ...]
    diffreason: DiffReason
    data: tuple = ()

    def __repr__(self) -> str:
        basestr = f"<DiffRecord ({self.bcvid}): '{self.diffreason.value}'"
        if self.data:
            basestr += ", " + repr(self.data)
        return basestr + ">"


@dataclass
class VerseData:
    """Alignments, sources, and targets for a single verse."""

    bcvid: str
    alignments: list[tuple[list[Source], list[Target]]]
    sources: list[Source]
    targets: list[Target]
    targets_included: tuple[Target, ...] = ()
    _typeattrs = ["sources", "targets"]

    def __post_init__(self) -> None:
        self.targets_included = tuple(tok for tok in self.targets if not tok.exclude)

    def __repr__(self) -> str:
        return f"<VerseData: {self.bcvid}>"

    def get_pairs(self, essential: bool = False) -> list[tuple[Source, Target]]:
        """Return pharaoh-style (source, target) token pairs."""
        if essential:
            return [(s, t) for src, trg in self.alignments for s in src if s.is_content for t in trg]
        return [(s, t) for src, trg in self.alignments for s in src for t in trg]

    def display(self, termsonly: bool = False) -> None:
        for sources, targets in self.alignments:
            print("------------")
            if termsonly:
                print(f"{[s.text for s in sources]}-{[t.text for t in targets]}")
            else:
                for src in sources:
                    print(f"Source: {src._display}")
                for trg in targets:
                    print(f"Target: {trg._display}")

    def table(self) -> None:
        for sources, targets in self.alignments:
            print(
                " ".join(s.text for s in sources),
                "\t",
                " ".join(t.text for t in targets),
            )

    def get_texts(
        self, typeattr: str = "targets", unique: bool = False, keepexcluded: bool = False
    ) -> list[str]:
        assert typeattr in self._typeattrs, f"typeattr should be one of {self._typeattrs}"
        tokens = getattr(self, typeattr)
        if typeattr == "targets" and not keepexcluded:
            tokens = self.targets_included
        if unique:
            cnt: Counter = Counter()
            texts: list[str] = []
            for item in tokens:
                itext = item.text
                texts.append(f"{itext}.{cnt[itext]}" if itext in cnt else itext)
                cnt[itext] = cnt[itext] + 1
        else:
            texts = [item.text for item in tokens]
        return texts

    def dataframe(
        self, hitmark: str = "-G-", missmark: str = "   ", srcattr: str = "text"
    ) -> pd.DataFrame:
        """Return a DataFrame showing alignment hits."""

        def get_mark(src: Source, trg: Target) -> str:
            return hitmark if src in aligned_target_sources.get(trg, {}) else missmark

        aligned_target_sources = {trg: alpair[0] for alpair in self.alignments for trg in alpair[1]}
        target_text = dict(zip(self.targets_included, self.get_texts(unique=True)))
        dfdata = {
            textdisplay: [get_mark(src, trg) for src in self.sources]
            for _ in enumerate(self.alignments)
            for trg, textdisplay in target_text.items()
        }
        return pd.DataFrame(dfdata, index=[getattr(src, srcattr) for src in self.sources])

    @staticmethod
    def _diff_pair(
        basedict: dict[str, str], pair: tuple
    ) -> Optional[DiffRecord]:
        if pair[0] != pair[1]:
            sources1, targets1 = pair[0]
            sources2, targets2 = pair[1]
            if sources1 != sources2:
                return DiffRecord(**basedict, diffreason=DiffReason.DIFFSOURCES, data=(sources1, sources2))
            if targets1 != targets2:
                return DiffRecord(**basedict, diffreason=DiffReason.DIFFTARGETS, data=(targets1, targets2))
        return None

    def diff(self, other: "VerseData") -> Optional[list[DiffRecord]]:
        assert isinstance(other, VerseData), "Can only compare two VerseData instances."
        basedict = {"bcvid": self.bcvid}
        if len(self.alignments) != len(other.alignments):
            return [DiffRecord(**basedict, diffreason=DiffReason.DIFFLEN,
                               sources1=(), targets1=(), sources2=(), targets2=())]
        diffs: list[DiffRecord] = []
        for pair in zip(self.alignments, other.alignments):
            result = self._diff_pair(basedict, pair)
            if result:
                diffs.append(result)
        return diffs
