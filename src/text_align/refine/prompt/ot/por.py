"""Portuguese target-language prompt config for OT (Hebrew) refine-alignment.

Key differences from OT English (eng.py):
  BASE_BLOCK           — pro-drop subject pronouns; contracted preposition+article
                         forms (do/da/no/na/ao/à); Hebrew's already-merged
                         preposition+article word-part maps to a SINGLE contracted
                         Portuguese word (primary 1:1, no split) rather than
                         English's split "in"/"the" pattern; construct chain "de"
                         (contracted do/da when definite); no English-only "'s"
                         possessive branch.
  PRONOMINAL_SUFFIX_BLOCK — dele/dela vs. seu/sua ambiguity note; fused
                         preposition+pronoun words (nele, dele, comigo, consigo)
                         align both Hebrew word-parts primary to the one fused
                         Portuguese token.
  NEGATION_BLOCK       — Portuguese negation is normally contiguous (não + verb),
                         so the English discontiguous-verb caveat rarely applies.
  PARTICIPLE_BLOCK     — substantive participle → "o que"/"aquele que" pattern.
  INFINITIVE_BLOCK     — no "to" marker (bare infinitive primary); personal
                         infinitive endings absorb person/number (no secondary
                         expected); Portuguese synthetic future means infinitive
                         absolute has no auxiliary to secondary-mark.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language
from .eng import BLOCK_ORDER, FORCED_INCLUSIONS


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

Word-part present → align Portuguese correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Pro-drop subject pronoun — Portuguese encodes person/number in the verb ending. When no subject pronoun appears in the translation, none is expected (verb alone is primary). When a pronoun IS present for clarity (no separate Hebrew pronoun token) → secondary.
  וַיֹּאמֶר → "e disse" — "e" primary (waw word-part); "disse" primary (verb token); no secondary
  וַיֹּאמֶר → "e ele disse" (supplied for clarity) — "e", "disse" primary; "ele" secondary
- "de" from construct chain — no preposition token; genitive by construct form. "de" (or contracted "do"/"da" when the construct is definite) secondary to construct noun.
- Portuguese "o/a" when article merged — no article word-part; "o/a" secondary to noun token.
- Preposition+article merged (בַּ/לַ/כַּ) — Hebrew already fuses these into one token; the Portuguese contracted form (no/na/do/da) is the single direct correspondent: primary 1:1 to that one token, no split (contrast English, which must split "in"+"the" since it has no contracted word).
- Auxiliary verbs for participles ("estava sentado") — main verb primary; auxiliary secondary.

- Periphrastic rendering — when a single Hebrew token is rendered by multiple Portuguese words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, morphologically rich stems, or words whose Portuguese rendering distributes the meaning. Never NEQ a target word that expresses a component of the source word's meaning.
  מָשַׁל → "exerce domínio sobre": "exerce", "domínio" primary; "sobre" secondary
  שֹׁמֵר (substantive participle) → "aquele que guarda": "guarda" primary; "aquele", "que" secondary
  הוֹדוּ → "dar graças": "dar", "graças" both primary
  הֵיטִיב → "fazer bem": "fazer", "bem" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no Portuguese equivalent). Rare exception: when explicitly rendered "quanto a" or similar.
Supplied copula ("é", "são", "era", "eram") with no Hebrew verb token → NEQ target (verbless clause).
  יְהוָה אֱלֹהֵינוּ → "o SENHOR é o nosso Deus":
    source=[יְהוָה], target=["SENHOR"] — primary; "o" secondary (reinstated article)
    source=[אֱלֹהֵינוּ], target=["nosso", "Deus"] — primary: "Deus"; secondary: "nosso" (suffix), "o" (reinstated article)
    "é" → NEQ target
Waw conjunction + Portuguese asyndeton → waw word-part NEQ source.
Portuguese conjunction with no Hebrew conjunction token → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Create separate records whenever source tokens (or word-parts) can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.
Grammar-required translation words (pronominal suffix, construct-chain particle ["de"], modal helpers for verbal morphology ["poderia," "devesse," "teria"], implied article) are secondary to the source token or word-part whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
- Article word-part → "o/a/os/as": primary 1:1; noun gets its own record.
- Article word-part, no Portuguese "o/a/os/as": secondary to the noun in the noun's record.
- No article word-part, Portuguese "o/a/os/as" present: secondary to the noun token.
- Portuguese "um/uma": secondary to the noun (Hebrew has no indefinite article).
- Article before proper name (rare — mainly geographic, e.g. הַיַּרְדֵּן "the Jordan"): when Portuguese retains the article ("o Jordão"), primary 1:1; when Portuguese omits it (most personal names), secondary to the name.

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token.
- Construct noun → Portuguese head noun: primary. Portuguese "de" (or contracted "do"/"da" when the construct is definite) → secondary in construct noun's record.
  בֵּית יְהוָה → "casa do SENHOR":
    source=[בֵּית],  target=["casa", "do"] — primary: "casa"; secondary: "do" (contracted de+o, reflecting construct definiteness)
    source=[יְהוָה], target=["SENHOR"]      — primary 1:1
  Uncontracted: בֵּית יְהוָה → "casa de Javé": source=[בֵּית], target=["casa", "de"] — primary: "casa"; secondary: "de"
- Construct definiteness: Portuguese article/contraction before a construct noun (no article token) → secondary to that noun.

## INSEPARABLE PREPOSITIONS
Preposition word-part alone (no merged article) → Portuguese preposition (de/em/a/por): primary 1:1.
Preposition + merged article in the same token (בַּ/לַ/כַּ) → the Portuguese contracted form (no/na/do/da/ao/à) is the single direct correspondent: primary 1:1 to that one token, no split.
  בַּמֶּלֶךְ "no rei" (single merged Hebrew token):
    source=[bammelekId], target=["no", "rei"] — primary: "no" (contracted em+o, primary to whole merged token); "rei" primary 1:1

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "e"/"mas"/"então"/"assim"/"ora": primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever Portuguese word carries its force in context ("que", "porque", "pois", "porquanto"). Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — "que"/"o qual"/"onde"/etc. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source units are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES
Pronominal suffixes are separate word-part tokens (pos=suffix). Each suffix → Portuguese pronoun, primary 1:1.

- Possessive suffix on noun: suffix → possessive pronoun (primary); noun → head noun (primary). Either "seu/sua" or "dele/dela" is acceptable — align to whichever the translation uses; BP often prefers "dele/dela/deles/delas" for 3rd person to avoid ambiguity with formal "seu/sua" ("your").
  דְּבָרוֹ "sua palavra" / "a palavra dele": source=[davarPart], target=["palavra"] — primary; source=[sufPart], target=["sua"] or ["dele"] — primary

- Object suffix on verb: suffix → object pronoun, primary 1:1.
  שְׁמָרֵנוּ "ele nos guardou": source=[shamarPart], target=["guardou"] — primary; source=[nuPart], target=["nos"] — primary

- Suffix on preposition: suffix → governed pronoun, primary 1:1.
  אֵלָיו "a ele": source=[elPart], target=["a"] — primary; source=[sufPart], target=["ele"] — primary
  Fused preposition+pronoun (nele, dele, comigo, consigo): Portuguese fuses the two into one orthographic word. Both the preposition word-part and the suffix word-part align primary to that single fused target token (N:1) — do not attempt to split the fused word.
  בּוֹ "nele": source=[bePart, sufPart], target=["nele"] — both primary\
"""

NEGATION_BLOCK = """\
## NEGATION

- לֹא/לוֹא → "não"/"nunca": primary 1:1.
- אַל (jussive/imperative) → "não": primary 1:1.
- אֵין/אַיִן (existential) → "não há"/"não existe"/"não é": all words primary 1:N.
  source=[einId], target=["não", "há"] — all primary
  Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "ele não é") → suffix word-part primary 1:1 (see PRONOMINAL SUFFIXES).

Portuguese negation is normally contiguous ("não sabe"), unlike English's discontiguous auxiliary+"not"+verb pattern ("does not know") — there is usually no separate auxiliary to secondary-mark.
  לֹא יֵדַע "ele não sabe":
    source=[loId],   target=["não"]  — primary 1:1
    source=[verbId], target=["sabe"] — primary 1:1 (no auxiliary; Portuguese present tense is synthetic)
  Rare periphrastic exception (compound tenses, e.g. "não tem sabido"): "não" stays in its own record; the verb record spans the periphrastic construction (auxiliary secondary, main verb primary), as in English.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival: align to Portuguese adjective or participial modifier — primary.
- Substantive with article word-part: article → Portuguese "o que"/"aquele que" primary 1:1; "que" secondary to participle.
  הַשֹּׁמֵר "aquele que guarda":
    source=[articlePart],  target=["aquele"]      — primary 1:1
    source=[participleId], target=["que", "guarda"] — primary: "guarda"; secondary: "que"
  Anarthrous substantive (no article token): all nominalizing elements ("o", "aquele", "que", "quem") secondary to participle.
- Verbal (predicative): Portuguese progressive auxiliary ("estava"/"está"/"estavam") secondary; main verbal element primary.
  יֹשֵׁב "estava sentado": source=[participleId], target=["estava", "sentado"] — primary: "sentado"; secondary: "estava"
- Periphrastic (participle + explicit הָיָה): הָיָה → Portuguese auxiliary, separate primary record; participle → main verb, primary.
  source=[hayahId],      target=["estava"]  — primary 1:1
  source=[participleId], target=["sentado"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
- Separate לְ word-part (pos=preposition): if purposive, לְ → "para" primary 1:1; infinitive → Portuguese verb primary. If purely complementary, Portuguese uses no marker — infinitive primary, לְ has no secondary correspondent.
- Merged לְ (no separate token): no separate marker expected (unlike English "to"); infinitive stands alone, primary.
  רָצָה לָלֶכֶת → "quis ir": source=[verbPart], target=["ir"] — primary 1:1 (no "to"-equivalent secondary)

### Purpose/temporal constructions (בְּ/לְ + infinitive)
Preposition word-part → Portuguese connector ("quando"/"ao"/"por"/"como"; contracted forms apply per ARTICLES/INSEPARABLE PREPOSITIONS): primary. Infinitive → main Portuguese verbal element: primary.
  בְּשָׁמְעוֹ "ao ouvir":
    source=[bePrepPart], target=["ao"]    — primary (contracted em+o)
    source=[verbPart],   target=["ouvir"] — primary (suffix subject may be absorbed by the personal infinitive ending — see PERSONAL INFINITIVE below — or rendered as a separate pronoun per PRONOMINAL SUFFIXES)

### Personal infinitive
Portuguese inflects the infinitive for person/number (ouvirmos, ouvirem, etc.). When a Hebrew infinitive construct carries a pronominal suffix marking its subject, a Portuguese personal-infinitive ending encodes the same information — no secondary token is expected for the ending itself.

### Infinitive absolute (cognate emphasis)
Infinitive absolute → Portuguese emphasis word ("certamente"/"decerto"/"deveras"): primary 1:1. Finite verb → main Portuguese verb: primary.
  מוֹת תָּמוּת → "certamente morrerás":
    source=[infAbsId], target=["certamente"] — primary 1:1
    source=[verbId],   target=["morrerás"]   — primary 1:1 (Portuguese future is synthetic — no auxiliary "shall"/"will" word to secondary-mark, unlike English)
  Absorbed without separate Portuguese word → infinitive absolute secondary to finite verb, or NEQ if definitively untranslated.\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PRONOMINAL_SUFFIX": PRONOMINAL_SUFFIX_BLOCK,
    "NEGATION":          NEGATION_BLOCK,
    "PARTICIPLE":        PARTICIPLE_BLOCK,
    "INFINITIVE":        INFINITIVE_BLOCK,
}

POR_OT_CONFIG = LanguagePromptConfig(
    language_code="por",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(POR_OT_CONFIG)
