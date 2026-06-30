"""Stopword utilities shared by migrate and align tools."""

from stopwordsiso import stopwords as iso_stopwords
from nltk.corpus import stopwords as nltk_stopwords


# ISO 639-3 → stopwordsiso (ISO 639-1) language code map
STOPWORDS_LANGUAGE_MAP: dict[str, str] = {
    "eng": "en",
    "spa": "es",
    "ger": "de",
    "fra": "fr",
    "arb": "ar",
    "ind": "id",
    "rus": "ru",
    "por": "pt",
    "lin": "ln",
    "swh": "sw",
}

# ISO 639-3 → NLTK corpus name map (NLTK has fewer languages)
NLTK_LANGUAGE_MAP: dict[str, str] = {
    "eng": "english",
    "spa": "spanish",
    "ger": "german",
    "fra": "french",
    "por": "portuguese",
    "ind": "indonesian",
    "rus": "russian",
    "arb": "arabic",
    "lin": "lingala",
    "swh": "swahili",
}


def load_stopwordsiso_stopwords(language: str) -> set[str]:
    """Return stopwords for *language* (ISO 639-3) from stopwordsiso, or empty set."""
    if language in STOPWORDS_LANGUAGE_MAP:
        return set(iso_stopwords(STOPWORDS_LANGUAGE_MAP[language]))
    return set()


def load_nltk_stopwords(language: str) -> set[str]:
    """Return stopwords for *language* (ISO 639-3) from NLTK, or empty set."""
    if language in NLTK_LANGUAGE_MAP:
        try:
            return set(nltk_stopwords.words(NLTK_LANGUAGE_MAP[language]))
        except OSError:
            return set()
    return set()
