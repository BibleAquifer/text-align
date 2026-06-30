"""Utilities for burrito alignment data."""

from itertools import groupby
from typing import Any, Callable

from .BaseToken import BaseToken


def groupby_bcv(values: list[Any], bcvfn: Callable = BaseToken.to_bcv) -> dict[str, list[Any]]:
    """Group a list of tokens into a dict keyed by BCV reference."""
    return {k: list(g) for k, g in groupby(values, bcvfn)}


def groupby_bc(values: list[str | BaseToken]) -> dict[str, list[Any]]:
    """Group a list of tokens into a dict keyed by book+chapter."""

    def _to_bc(token: BaseToken) -> str:
        if isinstance(token, BaseToken):
            return token.id[:5]
        elif isinstance(token, str):
            return token[:5]
        else:
            raise ValueError(f"Invalid type for {token}")

    return {k: list(g) for k, g in groupby(values, _to_bc)}


def groupby_bcid(values: list[str]) -> dict[str, list[Any]]:
    """Group a list of token ID strings into a dict keyed by book+chapter."""
    return {k: list(g) for k, g in groupby(values, lambda tokenid: tokenid[:5])}


def filter_by_bcv(
    items: list[Any],
    startbcv: str,
    endbcv: str,
    key: Callable = lambda x: x,
) -> list[Any]:
    """Return a subset of items between startbcv and endbcv (inclusive).

    key is applied to each element to obtain a BCV string for comparison.
    Items must be in canonical order.
    """
    partial: list[Any] = []
    collecting = False
    for item in items:
        itembcv = key(item)
        if itembcv == startbcv:
            collecting = True
        if collecting:
            partial.append(item)
        if itembcv == endbcv:
            collecting = False
            break
    if not partial:
        raise ValueError(f"No records: didn't find startbcv {startbcv}")
    if collecting:
        lastbcv = key(items[-1])
        if endbcv != lastbcv:
            raise ValueError(f"Did not stop collecting: check endbcv {endbcv}")
    return partial
