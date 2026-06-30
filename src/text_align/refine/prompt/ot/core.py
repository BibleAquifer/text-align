"""OT registry and Hebrew phenomenon detection for refine-alignment.

Detection notes
---------------
The WLCM.tsv morph field is always empty; detection relies on the pos and
gloss fields:

  pos == "suffix"                      → PRONOMINAL_SUFFIX  (pronominal suffix word-part)
  pos == "particle" + text in neg set  → NEGATION
  pos == "verb" + gloss ends "-ing"    → PARTICIPLE         (participial gloss convention)
  pos == "verb" + gloss starts "to "   → INFINITIVE         (infinitive construct / absolute)
"""

from text_align.burrito.source import Source
from text_align.refine.prompt.common import LanguagePromptConfig


_OT_REGISTRY: dict[str, LanguagePromptConfig] = {}


def register_ot_language(config: LanguagePromptConfig) -> None:
    _OT_REGISTRY[config.language_code] = config


def get_ot_language_config(language_code: str) -> LanguagePromptConfig:
    if language_code in _OT_REGISTRY:
        return _OT_REGISTRY[language_code]
    fallback = _OT_REGISTRY.get("eng")
    if fallback is None:
        raise KeyError(
            f"No OT prompt config registered for '{language_code}' and no 'eng' fallback."
        )
    return fallback


# ---------------------------------------------------------------------------
# Phenomenon detection (Hebrew OT source tokens)
# ---------------------------------------------------------------------------

_HEBREW_NEGATION: frozenset[str] = frozenset({
    "לֹא", "לֹּא", "לוֹא",          # standard negation
    "אַל",                              # jussive / imperative negation
    "אֵין", "אַיִן", "אֵינֶנּוּ",     # existential negation
    "בַּל", "בְּלִי", "בְּלֵי",       # poetic negation
})


def detect_phenomena(source_tokens: list[Source]) -> set[str]:
    """Scan Hebrew OT source token fields and return phenomenon tags."""
    tags: set[str] = set()

    for t in source_tokens:
        pos = t.pos or ""
        text = t.text or ""
        gloss = (t.gloss or "").strip()

        if pos == "suffix":
            tags.add("PRONOMINAL_SUFFIX")

        if pos == "particle" and text in _HEBREW_NEGATION:
            tags.add("NEGATION")

        if pos == "verb":
            if gloss.endswith("ing"):
                tags.add("PARTICIPLE")
            if gloss.startswith("to "):
                tags.add("INFINITIVE")

    return tags
