"""Utilities for working with Strong's numbers."""

import re


def normalize_strongs(strongs: str | int, prefix: str = "", strict: bool = False) -> str:
    """Return a normalized Strong's id."""
    _strongsre: re.Pattern = re.compile(r"[AGH]?\d{1,4}[a-d]?")
    _badsuffixre: re.Pattern = re.compile(r"[e-z]$")
    specials: dict[str, str] = {
        "1537+4053": "G4053b",
        "5228+1537+4053": "G4053c",
        "1417+3461": "G3461b",
    }
    # some WLCM values have vertical bars like "1886j|2050b"; use the part after the bar
    if isinstance(strongs, str) and "|" in strongs:
        strongs = strongs.split("|")[-1]
    # uW KeyTerms data: some like G29620 — last digit is always zero
    if isinstance(strongs, str) and strongs.startswith("G") and len(strongs) == 6:
        if strongs.endswith("0"):
            strongs = strongs[:-1]
    # Macula Hebrew has trailing j, z
    if isinstance(strongs, str) and _badsuffixre.search(strongs):
        strongs = strongs[:-1]
    # special cases for SBLGNT data
    if strongs in specials:
        normed = specials[str(strongs)]
    # Macula Hebrew has some empty values: allow these if not strict
    elif strict and (strongs == "H"):
        raise ValueError("Strong's code must not be empty")
    elif isinstance(strongs, int):
        normed = f"{prefix}{strongs:0>4}"
    elif _strongsre.fullmatch(strongs):
        if re.match(r"[AGH]", strongs):
            firstchar = strongs[0]
            if prefix:
                if firstchar != prefix:
                    print(f"Overwriting prefix parameter {prefix} for {strongs}")
            else:
                prefix = firstchar
        base = re.sub(r"\D", "", strongs)
        suffix = strongs[-1] if re.search("[a-d]$", strongs) else ""
        assert prefix, f"prefix must be specified: {strongs}"
        normed = f"{prefix}{base:0>4}{suffix}"
    else:
        raise ValueError(f"Invalid Strong's code: {strongs}")
    return normed
