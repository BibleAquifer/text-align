"""NT registry and Greek phenomenon detection for refine-alignment."""

from text_align.burrito.source import Source
from text_align.refine.prompt.common import LanguagePromptConfig


_NT_REGISTRY: dict[str, LanguagePromptConfig] = {}


def register_nt_language(config: LanguagePromptConfig) -> None:
    _NT_REGISTRY[config.language_code] = config


def get_nt_language_config(language_code: str) -> LanguagePromptConfig:
    if language_code in _NT_REGISTRY:
        return _NT_REGISTRY[language_code]
    fallback = _NT_REGISTRY.get("eng")
    if fallback is None:
        raise KeyError(
            f"No NT prompt config registered for '{language_code}' and no 'eng' fallback."
        )
    return fallback


# ---------------------------------------------------------------------------
# Phenomenon detection (Greek NT source tokens)
# ---------------------------------------------------------------------------

_IMPERSONAL_FORMS: frozenset[str] = frozenset({
    "δεῖ", "ἔξεστιν", "ἔξεστι", "πρέπει", "συμφέρει", "δοκεῖ",
})

_NEGATION_FORMS: frozenset[str] = frozenset({
    "οὐ", "οὐκ", "οὐχ", "οὐχί",
    "μή", "μήτε",
    "οὐδέ", "μηδέ",
    "οὐκέτι", "μηκέτι",
    "οὔπω", "μήπω",
    "οὔτε",
})


def detect_phenomena(source_tokens: list[Source]) -> set[str]:
    """Scan Greek NT source token fields and return phenomenon tags."""
    tags: set[str] = set()

    for t in source_tokens:
        morph = t.morph or ""
        text = t.text or ""
        lemma = t.lemma or ""

        if t.pos == "verb" and "-" in morph:
            tam = morph.split("-")[1]
            if len(tam) >= 3:
                voice = tam[-2]
                mood = tam[-1]
                if voice == "P":
                    tags.add("PASSIVE")
                if mood == "P":
                    tags.add("PARTICIPLE")
                if mood == "N":
                    tags.add("INFINITIVE")
                if tam[0] in "IXY":
                    tags.add("VERBAL_ASPECT")

        if t.pos in ("adj", "adv"):
            if morph.endswith("-C") or morph.endswith("-S"):
                tags.add("COMPARATIVE")

        if text == "ἵνα":
            tags.add("HINA")
        if text in ("εἰ", "ἐάν"):
            tags.add("CONDITIONAL")
        if text == "ὅτι":
            tags.add("HOTI")
        if lemma == "αὐτός" or text in (
            "αὐτός", "αὐτοῦ", "αὐτῷ", "αὐτόν",
            "αὐτή", "αὐτῆς", "αὐτῇ", "αὐτήν",
            "αὐτό", "αὐτοί", "αὐτῶν", "αὐτοῖς",
            "αὐτούς", "αὐταί", "αὐτάς",
        ):
            tags.add("AUTOS")
        if text in _IMPERSONAL_FORMS:
            tags.add("IMPERSONAL")
        if text in _NEGATION_FORMS:
            tags.add("NEGATION")

    return tags
