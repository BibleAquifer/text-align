"""Code for working with alignment data in Scripture Burrito format."""

from text_align import ROOT, DATAPATH, SRCPATH

from .AlignmentGroup import (
    Document,
    Metadata,
    AlignmentReference,
    AlignmentRecord,
    AlignmentGroup,
    TopLevelGroups,
)
from .AlignmentSet import AlignmentSet
from .AlignmentType import TranslationType
from .alignments import AlignmentsReader, write_alignment_group
from .BadRecord import BadRecord, Reason
from .BaseToken import BaseToken, asbool, bare_id
from .manager import Manager
from .source import macula_prefixer, macula_unprefixer, Source, SourceReader
from .target import Target, TargetReader
from .util import groupby_bcv
from .VerseData import VerseData


__all__ = [
    "ROOT",
    "DATAPATH",
    "SRCPATH",
    # AlignmentGroup
    "Document",
    "Metadata",
    "AlignmentReference",
    "AlignmentRecord",
    "AlignmentGroup",
    "TopLevelGroups",
    # AlignmentSet
    "AlignmentSet",
    # AlignmentType
    "TranslationType",
    # BadRecord
    "BadRecord",
    "Reason",
    # BaseToken
    "BaseToken",
    "asbool",
    "bare_id",
    # alignments
    "AlignmentsReader",
    "write_alignment_group",
    # manager
    "Manager",
    # source
    "macula_prefixer",
    "macula_unprefixer",
    "Source",
    "SourceReader",
    # target
    "Target",
    "TargetReader",
    # util
    "groupby_bcv",
    # VerseData
    "VerseData",
]
