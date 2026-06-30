"""Minimal per-language stopword sets for alignment quality scoring (Signal 2).

Loads data from stopwordsiso and intersects with a small curated core of
unambiguously function words per language. Falls back to an empty frozenset
for languages without coverage — the safe direction is to penalise gaps
rather than hide them by over-suppressing content words.
"""

from __future__ import annotations

import functools

# Curated cores: words that are unambiguously function words in every context.
# Words like "say", "go", "come", "make" are intentionally excluded even
# though they appear in some stopword packages.

_CORE: dict[str, frozenset[str]] = {
    "eng": frozenset({
        "a", "an", "the",
        "and", "but", "or", "nor",
        "of", "to", "in", "on", "at", "by", "with", "from", "as", "into",
        "it", "its",
        "is", "are", "was", "were", "be", "been", "being",
        "do", "does", "did",
        "not",
    }),
    "por": frozenset({
        "a", "as", "o", "os",
        "e", "mas", "ou", "nem",
        "de", "do", "da", "dos", "das",
        "em", "no", "na", "nos", "nas",
        "ao", "à", "aos", "às",
        "por", "pelo", "pela", "pelos", "pelas",
        "para", "com", "sem",
        "um", "uma", "uns", "umas",
        "se", "que",
        "não",
        "é", "são", "era", "eram", "foi", "foram", "ser", "sido", "sendo",
    }),
    "spa": frozenset({
        "el", "la", "los", "las",
        "y", "e", "pero", "sino", "o", "u", "ni",
        "de", "del", "a", "al", "en", "con", "por", "para", "sin",
        "un", "una", "unos", "unas",
        "se", "que",
        "no",
        "es", "son", "era", "eran", "fue", "fueron", "ser", "sido", "siendo",
    }),
    "fra": frozenset({
        "le", "la", "les", "l",
        "et", "mais", "ou", "ni",
        "de", "du", "des", "d",
        "en", "à", "au", "aux", "par", "pour", "avec", "sans",
        "un", "une", "des",
        "se", "que", "qu",
        "ne", "pas",
        "est", "sont", "était", "étaient", "être", "été", "étant",
    }),
}

# ISO 639-3 → ISO 639-1 for stopwordsiso
_ISO3_TO_ISO1: dict[str, str] = {
    "eng": "en",
    "por": "pt",
    "spa": "es",
    "fra": "fr",
    "ara": "ar",
    "zho": "zh",
    "hin": "hi",
    "guj": "gu",
    "nep": "ne",
    "swa": "sw",
}

@functools.lru_cache(maxsize=None)
def stopwords_for_lang(lang_iso3: str) -> frozenset[str]:
    """Return a minimal stopword frozenset for the given ISO 639-3 code.

    Intersects the curated core with stopwordsiso data so only words that
    appear in both are kept. Languages with no curated core or no package
    coverage return an empty frozenset.
    """
    core = _CORE.get(lang_iso3, frozenset())
    iso1 = _ISO3_TO_ISO1.get(lang_iso3)

    if core and iso1:
        try:
            from stopwordsiso import stopwords as _sw
            pkg = frozenset(w.lower() for w in _sw(iso1))
            return core & pkg
        except Exception:
            return core
    return frozenset()
