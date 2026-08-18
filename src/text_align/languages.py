"""Right-to-left language registry (ISO 639-3), shared by render-alignment and
compare-alignment for auto-detecting RTL layout from a target-language code.

Mirrors the ``is_rtl=True`` entries in BN-Content's ``aquifer_pipeline.languages``
registry, copied locally rather than taken as a cross-repo dependency.
"""

from __future__ import annotations

RTL_LANGUAGES: frozenset[str] = frozenset({
    "arb",  # Arabic
    "apd",  # Sudanese Arabic
    "fas",  # Farsi (Persian)
    "heb",  # Hebrew
    "arc",  # Aramaic
})


def is_rtl_language(code: str | None) -> bool:
    """Return True if the given ISO 639-3 code is a known right-to-left language."""
    return code in RTL_LANGUAGES
