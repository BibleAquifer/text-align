"""Prose reference copy of the OT English prompt config — NOT imported.

Original English target-language prompt config for OT (Hebrew) refine-alignment."""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language


# ---------------------------------------------------------------------------
# Prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Hebrew source
text (MACULA Hebrew / Westminster Leningrad Codex).

## ALIGNMENT DIRECTION

Alignments map translation → source. Each record associates one or more target tokens
with one or more source tokens. The direction matters: you are asking what Hebrew word(s)
or word-part(s) are behind each translation word, not the reverse.

## HEBREW WORD-PART TOKENS

Hebrew source tokens may be individual morphological components of a single written word.
MACULA Hebrew splits prefixed elements into separate word-part tokens, each with its own
BCVWP ID. Common splits:

- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

**Word-part token present** → independent alignment unit; its English correspondent is
**primary** to it. **No word-part token** (morpheme merged into the main token) → English
correspondent is **primary** to the main token. This principle governs all sections below.

## ALIGNMENT PHILOSOPHY

Alignments are generous. When a translation word exists because of Hebrew grammar — a
preposition implied by a construct relationship, a subject pronoun implied by a verb's
person/gender/number ending, an article encoded as a prefix — it belongs in an alignment
record. The goal is to align as clearly and generously as possible.

Generous alignment sometimes means leaving tokens unaligned or marking them NEQ. Do not
force tokens into records when no genuine correspondence exists. Both are deliberate,
legitimate outcomes — not failures.

## TOKEN ROLES

Every token in a record is either primary or secondary. For each English word, ask:

**Why does this word exist in the translation?**

- **It has a direct lexical or semantic connection to the Hebrew token** → **primary**.
- **It exists because of Hebrew grammar with no separate source token** (construct
  relationship, verbal morphology, definiteness from a merged article) → **secondary**.
- **It translates a different Hebrew token** → separate record for that token.

Common secondary cases:

- **Supplied subject pronoun** — no independent Hebrew pronoun token; person/gender/
  number is encoded in the verb ending.
  Example: וַיֹּאמֶר "and he said" → "and" primary (waw word-part); "said" primary
  (verb token); "he" secondary to the verb (no separate pronoun token).

- **"of" from a construct chain** — no preposition token; genitive expressed by
  construct form.
  Example: בֵּית יְהוָה "house of the LORD" → "of" secondary to בֵּית.

- **English "the" when the article is merged** — article (הַ) has no separate word-part
  token; "the" is secondary to the noun token.

- **English article-driven preposition merges** — when an inseparable preposition is
  merged with the article into one token (בַּ/לַ/כַּ), the English preposition is
  primary and "the" is secondary, both to that single token.

- **Auxiliary verbs** for Hebrew participles ("was sitting", "is going") — main verb
  element primary; auxiliary secondary.

**Structural constraints:**

Every record must have at least one primary token on each populated side.
Each target token ID must appear in exactly one record per verse.

## NEQ (NON-EQUIVALENT)

For each token without an obvious alignment, ask:

**Am I certain this token has no correspondent anywhere in the translation of this verse?**

- **YES, certain** → NEQ: a record with the token in one array and the other array
  empty, plus `meta.rel: "NEQ"`.
- **Uncertain / cannot determine** → leave the token **unrecorded**.

Do not use NEQ as a fallback for uncertainty. NEQ is a positive claim.
NEQ records must not include meta.secondary.

**Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source** in virtually all
cases. It marks definite direct objects but has no English equivalent. The rare exception:
when a translator explicitly renders it with "as for," "namely," or similar.

**Supplied copula ("is", "are", "was", "were") with no Hebrew verb token → NEQ target.**
Hebrew verbless clauses require a copula in English that the translator supplies; no
Hebrew token corresponds to it.

Example: יְהוָה אֱלֹהֵינוּ (Deut 6:4) → "the LORD is our God"
  source=[יְהוָה],    target=["LORD"] — primary
  source=[אֱלֹהֵינוּ], target=["our", "God"] — "God" primary; "our" secondary (suffix)
  "is" → NEQ target

**Waw conjunction (וְ/וַ) + English asyndeton** — waw word-part token → NEQ source.
**Translator-supplied English conjunction with no Hebrew conjunction token** → NEQ target.

## SURFACE FORM DIFFERENCES

Morphological differences — tense, voice, number, aspect, verbal stem (binyan) — do not
prevent alignment. The question is whether lexical and semantic correspondence exists.

## ARTICLES

The Hebrew definite article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle,
gloss="the"). Never NEQ.

- **Article word-part → "the":** primary 1:1. Noun gets its own record.
- **Article word-part, no English "the":** secondary to the noun in the noun's record.
- **No article word-part, English "the" present:** "the" is secondary to the noun token.
- **English "a"/"an":** secondary to the noun (Hebrew has no indefinite article).

## CONSTRUCT CHAINS

A construct chain expresses a genitive relationship through word order and the construct
form of the first noun — no preposition token. English renders it with "of" or a
possessive.

- Construct noun → English head noun: **primary** record.
- English **"of"**: **secondary** target token in the construct noun's record (no
  preposition token exists for it).
  Example: בֵּית יְהוָה → "house of the LORD":
    source=[בֵּית], target=["house", "of"] — primary: "house"; secondary: "of"
    source=[יְהוָה], target=["LORD"] — primary 1:1

- English **possessive ("'s")**: no secondary needed; construct noun → English head;
  genitive noun → English possessor.
  Example: בֵּית יְהוָה → "the LORD's house":
    source=[יְהוָה],  target=["LORD's"] — primary 1:1
    source=[בֵּית],   target=["house"]  — primary 1:1

- **Construct definiteness**: a construct noun is definite when the following noun is
  definite, but carries no article prefix. English "the" before the construct noun is
  secondary to that construct noun (no article token exists for it).

## INSEPARABLE PREPOSITIONS

Align the English preposition **primary** to the preposition word-part when present, or
to the noun token when merged. English "the" from a merged article is **secondary** to
that same token.

Example — single-token בַּמֶּלֶךְ "in the king":
  source=[bammelekId], target=["in", "the", "king"]
    primary: "in", "king";  secondary.target: ["the"]

## CONJUNCTIONS AND PARTICLES

Align content words first; conjunctions and particles are residual. When a conjunction
or particle has a clear English correspondent, align it primary 1:1.

The waw word-part token (pos=conjunction) is extremely common. Align it to its English
rendering ("and", "but", "then", "so", "now") as primary. When the translation uses
asyndeton, waw → NEQ source.

כִּי is polyfunctional. Match whichever English word carries כִּי's force in context.
כִּי introducing direct speech with only punctuation → NEQ source.

אֲשֶׁר/שֶׁ relative and subordinate particle → "who", "which", "that", "where", etc.
When absorbed into clause structure without a correspondent → NEQ source.

## IDIOMS

When a phrase-level correspondence has no token-level equivalent, use
meta.is_idiom: true. All tokens in the record are implicitly primary; meta.secondary
does not apply to idiom records.

Idiom is a last resort. Always prefer standard records. Function-word-only source units
are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Hebrew pronominal suffixes are separate word-part tokens in MACULA (pos=suffix). Each
suffix token is a **primary** source token for the English pronoun it expresses.

### Possessive suffix on a noun

Suffix → English possessive pronoun, primary 1:1. Noun → English head noun, primary 1:1.

Example — דְּבָרוֹ "his word" (word-parts: דָּבָר noun, וֹ 3ms suffix):
  source=[davarPartId], target=["word"] — primary
  source=[sufPartId],   target=["his"]  — primary

### Object suffix on a verb

Suffix → English object pronoun, primary 1:1.

Example — שְׁמָרֵנוּ "he kept us" (word-parts: שָׁמַר verb, נוּ 1cp suffix):
  source=[shamarPartId], target=["kept"] — primary
  source=[nuPartId],     target=["us"]   — primary

### Suffix on a preposition

Suffix → English pronoun governed by the preposition, primary 1:1.

Example — אֵלָיו "to him" (word-parts: אֵל prep, יו 3ms suffix):
  source=[elPartId],  target=["to"]  — primary
  source=[sufPartId], target=["him"] — primary\
"""

NEGATION_BLOCK = """\
## NEGATION

### Standard negation (לֹא, לוֹא)

Align to "not", "no", "never" — **primary** 1:1.

### Jussive/imperative negation (אַל)

Align to "not", "do not", "let … not" — **primary** 1:1.

### Existential negation (אֵין, אַיִן)

"there is no / are no / is not" — **primary**, often 1:N.

Example — אֵין → "there is no":
  source=[einId], target=["there", "is", "no"] — all three primary to אֵין

Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "he is not") are separate word-part tokens
— align suffix → "he"/"it"/etc. primary 1:1 (see PRONOMINAL SUFFIXES).

### Discontiguous verb with intervening negation

When a negation particle is present, "not" belongs in the negation record. The verb
record is often **discontiguous**: the auxiliary and main verb are non-adjacent target
tokens, with "not" interleaved in English. Do not include "not" as secondary in the
verb record.

Example — לֹא יֵדַע "he does not know":
  source=[loId],    target=["not"]          — primary 1:1
  source=[verbId],  target=["does", "know"] — primary: "know"; secondary: "does"
  ("not" intervenes in English but belongs to the negation record; verb record is
  discontiguous)\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adjectival participle

Align to the English adjective or participial modifier — **primary**.

### Substantive (nominal) participle

When a Hebrew article word-part (pos=particle, gloss="the") is present, align the
article → English relativizer ("the one", "he who", "those who") per the ARTICLES rule.
Relative pronouns ("who", "that") introduced in English are secondary to the participle.

Example: הַשֹּׁמֵר "the one who keeps":
  source=[articlePartId], target=["the", "one"] — primary 1:1 (article → "the one")
  source=[participleId],  target=["who", "keeps"] — primary: "keeps"; secondary: "who"

Anarthrous substantive (no article token): all English nominalizing elements ("the",
"one", "who", "whoever") are secondary to the participle.

### Verbal (predicative) participle

English progressive auxiliaries ("is", "was", "are", "were") are **secondary**; the
main verbal element is **primary**.

Example: יֹשֵׁב "was sitting":
  source=[participleId], target=["was", "sitting"]
    primary: "sitting";  secondary: "was"

### Periphrastic construction (participle + explicit הָיָה)

Align הָיָה → English auxiliary as a separate **primary** record. The participle →
English main verbal element, primary.

  source=[hayahId],      target=["was"]     — primary 1:1
  source=[participleId], target=["sitting"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ

When לְ is a **separate word-part token** (pos=preposition), align it to English "to" —
**primary** 1:1. The infinitive aligns to the English verb — primary.

When לְ is **merged** (no separate token), English "to" is **primary** to the infinitive
token.

### Purpose and temporal constructions with בְּ/לְ + infinitive

When an inseparable preposition + infinitive expresses purpose or temporal relationship:
- Preposition word-part → English connector ("to", "when", "while", "by", "as") —
  **primary** if it has its own token.
- Infinitive → main English verbal element — **primary**.

Example — בְּשָׁמְעוֹ "when he heard" (inseparable בְּ as word-part):
  source=[bePrepPartId], target=["when"]   — primary
  source=[verbPartId],   target=["heard"]  — primary (suffix → "he", see PRONOMINAL SUFFIXES)

### Infinitive absolute (cognate emphasis)

Align the infinitive absolute to the English emphasis word ("surely", "certainly",
"indeed") — **primary** 1:1. The finite verb aligns to the main English verb — primary.

Example — מוֹת תָּמוּת → "you shall surely die":
  source=[infAbsId], target=["surely"] — primary 1:1
  source=[verbId],   target=["die"]    — primary  (auxiliary "shall" secondary to verb)

When the translation absorbs the emphasis without a separate word, the infinitive
absolute may be secondary to the finite verb, or NEQ if definitively untranslated.\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

BLOCK_ORDER = [
    "PRONOMINAL_SUFFIX",
    "NEGATION",
    "PARTICIPLE",
    "INFINITIVE",
]

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PRONOMINAL_SUFFIX": PRONOMINAL_SUFFIX_BLOCK,
    "NEGATION":          NEGATION_BLOCK,
    "PARTICIPLE":        PARTICIPLE_BLOCK,
    "INFINITIVE":        INFINITIVE_BLOCK,
}

FORCED_INCLUSIONS: dict[str, set[str]] = {}

ENG_OT_CONFIG = LanguagePromptConfig(
    language_code="eng",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

# register_ot_language(ENG_OT_CONFIG)  # not active — prose reference only
