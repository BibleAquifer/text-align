"""Alignment type definitions."""

from dataclasses import dataclass
from typing import Union


@dataclass
class _AlignmentType:
    """Base class for alignment types and roles."""

    type: str
    roles: tuple[str, ...] = tuple([])

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: roles={self.roles}>"


@dataclass
class RelatedType(_AlignmentType):
    type: str = "related"


@dataclass
class DirectedType(_AlignmentType):
    type: str = "directed"
    roles: tuple[str, str] = tuple(["from", "to"])


@dataclass
class TranslationType(_AlignmentType):
    type: str = "translation"
    roles: tuple[str, str] = tuple(["source", "target"])


@dataclass
class AnaphoraType(_AlignmentType):
    type: str = "anaphora"
    roles: tuple[str, str] = tuple(["antecedent", "anaphor"])


AlignmentTypes = Union[RelatedType, DirectedType, TranslationType, AnaphoraType]
