"""English target-language prompt config for OT (Hebrew) refine-alignment.

Prose reference preserved in eng.prose.py.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language


# ---------------------------------------------------------------------------
# Prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Hebrew source
text (MACULA Hebrew / Westminster Leningrad Codex).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s) are behind this translation word.

## HEBREW WORD-PART TOKENS
MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own BCVWP ID. Common word-parts:
- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

Word-part present → align English correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Supplied subject pronoun — no Hebrew pronoun token; person/gender/number encoded in verb ending.
  וַיֹּאמֶר → "and he said": "and" primary (waw word-part); "said" primary (verb token); "he" secondary
- "of" from construct chain — no preposition token; genitive by construct form. "of" secondary to construct noun.
- English "the" when article merged — no article word-part; "the" secondary to noun token.
- Preposition+article merged (בַּ/לַ/כַּ) — English preposition primary; "the" secondary, both to that merged token.
- Auxiliary verbs for participles ("was sitting") — main verb primary; auxiliary secondary.

- Periphrastic rendering — when a single Hebrew token is rendered by multiple English words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, morphologically rich stems, or words whose English rendering distributes the meaning. Never NEQ a target word that expresses a component of the source word's meaning.
  מָשַׁל → "exercises dominion over": "exercises", "dominion" primary; "over" secondary
  שֹׁמֵר (substantive participle) → "the one who keeps": "keeps" primary; "the", "one", "who" secondary
  הוֹדוּ → "give thanks": "give", "thanks" both primary
  הֵיטִיב → "do good": "do", "good" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no English equivalent). Rare exception: when explicitly rendered "as for" or "namely".
Supplied copula ("is", "are", "was", "were") with no Hebrew verb token → NEQ target (verbless clause).
  יְהוָה אֱלֹהֵינוּ → "the LORD is our God":
    source=[יְהוָה], target=["LORD"] — primary
    source=[אֱלֹהֵינוּ], target=["our", "God"] — primary: "God"; secondary: "our" (suffix)
    "is" → NEQ target
Waw conjunction + English asyndeton → waw word-part NEQ source.
English conjunction with no Hebrew conjunction token → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Create separate records whenever source tokens (or word-parts) can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.
Grammar-required translation words (pronominal suffix, construct-chain particle ["of"], modal helpers for verbal morphology ["could," "might," "would"], implied article) are secondary to the source token or word-part whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
- Article word-part → "the": primary 1:1; noun gets its own record.
- Article word-part, no English "the": secondary to the noun in the noun's record.
- No article word-part, English "the" present: "the" secondary to the noun token.
- English "a"/"an": secondary to the noun (Hebrew has no indefinite article).

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token.
- Construct noun → English head noun: primary. English "of" → secondary in construct noun's record.
  בֵּית יְהוָה → "house of the LORD":
    source=[בֵּית],  target=["house", "of"] — primary: "house"; secondary: "of"
    source=[יְהוָה], target=["LORD"]         — primary 1:1
- English possessive "'s": no secondary; each noun aligns to its English counterpart.
  בֵּית יְהוָה → "the LORD's house": source=[יְהוָה], target=["LORD's"] — primary; source=[בֵּית], target=["house"] — primary
- Construct definiteness: English "the" before a construct noun (no article token) → secondary to that noun.

## INSEPARABLE PREPOSITIONS
Preposition word-part → English preposition: primary. Merged article in same token → English "the": secondary, both to that token.
  בַּמֶּלֶךְ "in the king" (single merged token):
    source=[bammelekId], target=["in", "the", "king"] — primary: "in", "king"; secondary.target: ["the"]

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "and"/"but"/"then"/"so"/"now": primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever English word carries its force in context. Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — "who"/"which"/"that"/"where"/etc. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source units are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES
Pronominal suffixes are separate word-part tokens (pos=suffix). Each suffix → English pronoun, primary 1:1.

- Possessive suffix on noun: suffix → possessive pronoun (primary); noun → head noun (primary).
  דְּבָרוֹ "his word": source=[davarPart], target=["word"] — primary; source=[sufPart], target=["his"] — primary

- Object suffix on verb: suffix → object pronoun, primary 1:1.
  שְׁמָרֵנוּ "he kept us": source=[shamarPart], target=["kept"] — primary; source=[nuPart], target=["us"] — primary

- Suffix on preposition: suffix → governed pronoun, primary 1:1.
  אֵלָיו "to him": source=[elPart], target=["to"] — primary; source=[sufPart], target=["him"] — primary\
"""

NEGATION_BLOCK = """\
## NEGATION

- לֹא/לוֹא → "not"/"no"/"never": primary 1:1.
- אַל (jussive/imperative) → "not"/"do not"/"let…not": primary 1:1.
- אֵין/אַיִן (existential) → "there is no"/"are no"/"is not": all words primary 1:N.
  source=[einId], target=["there", "is", "no"] — all primary
  Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "he is not") → suffix word-part primary 1:1 (see PRONOMINAL SUFFIXES).

Discontiguous verb: when a negation particle is present, "not" belongs in the negation record. The verb record spans non-adjacent tokens (auxiliary + main verb with "not" interleaved in English) — do not include "not" as secondary in the verb record.
  לֹא יֵדַע "he does not know":
    source=[loId],   target=["not"]          — primary 1:1
    source=[verbId], target=["does", "know"] — primary: "know"; secondary: "does"\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival: align to English adjective or participial modifier — primary.
- Substantive with article word-part: article → English relativizer ("the one"/"he who"/"those who") primary 1:1; relative pronouns ("who", "that") secondary to participle.
  הַשֹּׁמֵר "the one who keeps":
    source=[articlePart],  target=["the", "one"]   — primary 1:1
    source=[participleId], target=["who", "keeps"] — primary: "keeps"; secondary: "who"
  Anarthrous substantive (no article token): all nominalizing elements ("the", "one", "who", "whoever") secondary to participle.
- Verbal (predicative): English progressives ("is"/"was"/"are"/"were") secondary; main verbal element primary.
  יֹשֵׁב "was sitting": source=[participleId], target=["was", "sitting"] — primary: "sitting"; secondary: "was"
- Periphrastic (participle + explicit הָיָה): הָיָה → English auxiliary, separate primary record; participle → main verb, primary.
  source=[hayahId],      target=["was"]     — primary 1:1
  source=[participleId], target=["sitting"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
- Separate לְ word-part (pos=preposition): לְ → "to" primary 1:1; infinitive → English verb primary.
- Merged לְ (no separate token): "to" primary to the infinitive token.

### Purpose/temporal constructions (בְּ/לְ + infinitive)
Preposition word-part → English connector ("to"/"when"/"while"/"by"/"as"): primary. Infinitive → main English verbal element: primary.
  בְּשָׁמְעוֹ "when he heard":
    source=[bePrepPart], target=["when"]  — primary
    source=[verbPart],   target=["heard"] — primary (suffix → "he", see PRONOMINAL SUFFIXES)

### Infinitive absolute (cognate emphasis)
Infinitive absolute → English emphasis word ("surely"/"certainly"/"indeed"): primary 1:1. Finite verb → main English verb: primary.
  מוֹת תָּמוּת → "you shall surely die":
    source=[infAbsId], target=["surely"] — primary 1:1
    source=[verbId],   target=["die"]    — primary (auxiliary "shall" secondary)
  Absorbed without separate English word → infinitive absolute secondary to finite verb, or NEQ if definitively untranslated.\
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

register_ot_language(ENG_OT_CONFIG)
