"""Latin American Spanish target-language prompt config for OT (Hebrew) refine-alignment.

Targets central and south American Spanish (not Castilian/continental).

Key differences from OT Portuguese (por.py):
  BASE_BLOCK           — same pro-drop rule with vos/tú/ustedes regional note;
                         only del/al contractions (not 8 Portuguese forms) —
                         so Hebrew's merged preposition+article token only
                         collapses to a single Spanish word for לַ ("al") and
                         מֵהַ ("del"); בַּ/כַּ have no Spanish contraction and
                         must split like English (preposition primary, article
                         secondary). Proper names always Branch B (Spanish
                         omits the article, no conditional retention like
                         Portuguese).
  PRONOMINAL_SUFFIX_BLOCK — no dele/dela-style ambiguity; suffix+preposition
                         fusion is narrower than Portuguese (only "con" fuses:
                         conmigo/contigo/consigo); other prepositions stay two
                         words and align as plain 1:1 pairs.
  INFINITIVE_BLOCK     — no personal infinitive (Spanish infinitives don't
                         inflect for person); "al" + infinitive is a fixed
                         idiomatic temporal marker, not decomposed.
  NEGATION_BLOCK, PARTICIPLE_BLOCK — same contiguous-negation and "el que"/
                         "los que" substantive-participle pattern as
                         Portuguese, translated.
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

Word-part present → align Spanish correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Pro-drop subject pronoun — Spanish encodes person/number in the verb ending. When no subject pronoun appears in the translation, none is expected (verb alone is primary). When a pronoun IS present for clarity (no separate Hebrew pronoun token) → secondary.
  Regional note: some Latin American translations use vos (Argentina, Central America) as 2nd person singular alongside tú; the rule is the same. 2nd person plural is ustedes (not vosotros).
  וַיֹּאמֶר → "y dijo" — "y" primary (waw word-part); "dijo" primary (verb token); no secondary
  וַיֹּאמֶר → "y él dijo" (supplied for clarity) — "y", "dijo" primary; "él" secondary
- "de" from construct chain — no preposition token; genitive by construct form. "de" secondary to construct noun. Contraction to "del" only arises when the absolute noun carries its own Hebrew article word-part (see CONSTRUCT CHAINS).
- Spanish "el/la" when article merged — no article word-part; "el/la" secondary to noun token.
- Preposition+article merged (בַּ/לַ/כַּ/מֵהַ) — Hebrew fuses these into one token. Spanish only contracts "de+el→del" and "a+el→al": לַ and מֵהַ → single Spanish word, primary 1:1 to the one token, no split. בַּ and כַּ have no Spanish contraction ("en el", "como el" stay two words) — split as in English: preposition primary, article secondary.
- Auxiliary verbs for participles ("estaba sentado") — main verb primary; auxiliary secondary.

- Periphrastic rendering — when a single Hebrew token is rendered by multiple Spanish words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, morphologically rich stems, or words whose Spanish rendering distributes the meaning. Never NEQ a target word that expresses a component of the source word's meaning.
  מָשַׁל → "ejerce dominio sobre": "ejerce", "dominio" primary; "sobre" secondary
  שֹׁמֵר (substantive participle) → "el que guarda": "guarda" primary; "el", "que" secondary
  הוֹדוּ → "dar gracias": "dar", "gracias" both primary
  הֵיטִיב → "hacer bien": "hacer", "bien" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no Spanish equivalent). Rare exception: when explicitly rendered "en cuanto a" or similar.
Supplied copula ("es", "son", "era", "eran") with no Hebrew verb token → NEQ target (verbless clause).
  יְהוָה אֱלֹהֵינוּ → "el SEÑOR es nuestro Dios":
    source=[יְהוָה], target=["SEÑOR"] — primary; "el" secondary (reinstated article)
    source=[אֱלֹהֵינוּ], target=["nuestro", "Dios"] — primary: "Dios"; secondary: "nuestro" (suffix)
    "es" → NEQ target
Waw conjunction + Spanish asyndeton → waw word-part NEQ source.
Spanish conjunction with no Hebrew conjunction token → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Create separate records whenever source tokens (or word-parts) can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.
Grammar-required translation words (pronominal suffix, construct-chain particle ["de"], modal helpers for verbal morphology ["podría," "debiera," "habría"], implied article) are secondary to the source token or word-part whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
- Article word-part → "el/la/los/las": primary 1:1; noun gets its own record.
- Article word-part, no Spanish "el/la/los/las": secondary to the noun in the noun's record.
- No article word-part, Spanish "el/la/los/las" present: secondary to the noun token.
- Spanish "un/una": secondary to the noun (Hebrew has no indefinite article).
- Article before proper name: Latin American Spanish Bible translations omit the definite article before proper names (Jesús, David, Jerusalén). Hebrew articles before proper names (rare — mainly geographic) are always secondary to the name — never NEQ, and never primary (no Branch A alternative for Spanish, unlike Portuguese).

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token.
- Construct noun → Spanish head noun: primary. Spanish "de" → secondary in construct noun's record — UNLESS the absolute noun carries its own Hebrew article word-part, in which case the contraction "del" is assigned entirely to that article token's own record (Branch A above), and no secondary is added to the construct noun's record (the fused word already carries both meanings).
  בֵּית דָּוִד → "casa de David" (no article — proper name):
    source=[בֵּית], target=["casa", "de"] — primary: "casa"; secondary: "de"
    source=[דָּוִד], target=["David"] — primary 1:1
  בֶּן־הַמֶּלֶךְ → "hijo del rey" (absolute noun has its own article word-part):
    source=[בֶּן],          target=["hijo"] — primary 1:1 (no "de" secondary needed)
    source=[articlePart],  target=["del"]  — primary 1:1 (Branch A article rule; contraction absorbs the implied "de")
    source=[מֶּלֶךְ],        target=["rey"]  — primary 1:1
- Construct definiteness: Spanish article/contraction before a construct noun (no article token) → secondary to that noun.

## INSEPARABLE PREPOSITIONS
Preposition word-part alone (no merged article) → Spanish preposition (de/a/como/en): primary 1:1.
Preposition + merged article in the same token: only "de+el→del" and "a+el→al" contract in Spanish.
- לַ / מֵהַ (le/min + article) → single Spanish word ("al"/"del"), primary 1:1 to the one merged token, no split.
- בַּ / כַּ (be/ke + article) → no Spanish contraction ("en el", "como el" stay two words): split as in English — preposition primary, article secondary.
  לַמֶּלֶךְ "al rey" (single merged Hebrew token): source=[lammelekId], target=["al", "rey"] — primary: "al" (contracted a+el, primary to whole merged token); "rey" primary 1:1
  בַּמֶּלֶךְ "en el rey" (single merged Hebrew token, no Spanish contraction): source=[bammelekId], target=["en", "el", "rey"] — primary: "en", "rey"; secondary.target: ["el"]

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "y"/"pero"/"entonces"/"así"/"ahora": primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever Spanish word carries its force in context ("que", "porque", "pues"). Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — "que"/"el cual"/"donde"/etc. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source units are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES
Pronominal suffixes are separate word-part tokens (pos=suffix). Each suffix → Spanish pronoun, primary 1:1.

- Possessive suffix on noun: suffix → possessive pronoun (primary); noun → head noun (primary).
  דְּבָרוֹ "su palabra": source=[davarPart], target=["palabra"] — primary; source=[sufPart], target=["su"] — primary

- Object suffix on verb: suffix → object pronoun, primary 1:1.
  שְׁמָרֵנוּ "él nos guardó": source=[shamarPart], target=["guardó"] — primary; source=[nuPart], target=["nos"] — primary

- Suffix on preposition: suffix → governed pronoun, primary 1:1. Unlike Portuguese, most Spanish prepositions do NOT fuse with the following pronoun — they stay two words and align as plain 1:1 pairs.
  אֵלָיו "a él": source=[elPart], target=["a"] — primary; source=[sufPart], target=["él"] — primary
  Exception — "con" fuses irregularly (conmigo/contigo/consigo): both the preposition word-part and the suffix word-part align primary to that single fused target token (N:1).
  עִמִּי "conmigo": source=[imPart, sufPart], target=["conmigo"] — both primary\
"""

NEGATION_BLOCK = """\
## NEGATION

- לֹא/לוֹא → "no"/"nunca": primary 1:1.
- אַל (jussive/imperative) → "no": primary 1:1.
- אֵין/אַיִן (existential) → "no hay"/"no existe"/"no es": all words primary 1:N.
  source=[einId], target=["no", "hay"] — all primary
  Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "él no es") → suffix word-part primary 1:1 (see PRONOMINAL SUFFIXES).

Spanish negation is normally contiguous ("no sabe"), unlike English's discontiguous auxiliary+"not"+verb pattern ("does not know") — there is usually no separate auxiliary to secondary-mark.
  לֹא יֵדַע "él no sabe":
    source=[loId],   target=["no"]   — primary 1:1
    source=[verbId], target=["sabe"] — primary 1:1 (no auxiliary; Spanish present tense is synthetic)
  Rare periphrastic exception (compound tenses, e.g. "no ha sabido"): "no" stays in its own record; the verb record spans the periphrastic construction (auxiliary secondary, main verb primary), as in English.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival: align to Spanish adjective or participial modifier — primary.
- Substantive with article word-part: article → Spanish "el que"/"los que" primary 1:1; "que" secondary to participle.
  הַשֹּׁמֵר "el que guarda":
    source=[articlePart],  target=["el"]           — primary 1:1
    source=[participleId], target=["que", "guarda"] — primary: "guarda"; secondary: "que"
  Anarthrous substantive (no article token): all nominalizing elements ("el", "que", "quien") secondary to participle.
- Verbal (predicative): Spanish progressive auxiliary ("estaba"/"está"/"estaban") secondary; main verbal element primary.
  יֹשֵׁב "estaba sentado": source=[participleId], target=["estaba", "sentado"] — primary: "sentado"; secondary: "estaba"
- Periphrastic (participle + explicit הָיָה): הָיָה → Spanish auxiliary, separate primary record; participle → main verb, primary.
  source=[hayahId],      target=["estaba"] — primary 1:1
  source=[participleId], target=["sentado"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
- Separate לְ word-part (pos=preposition): if purposive, לְ → "para" primary 1:1; infinitive → Spanish verb primary. If purely complementary, Spanish uses no marker — infinitive primary, no separate correspondent for לְ (unlike English "to").
  רָצָה לָלֶכֶת → "quiso ir": source=[verbPart], target=["ir"] — primary 1:1 (no "to"-equivalent secondary)

### Purpose/temporal constructions (בְּ/לְ + infinitive)
"al" + infinitive is a fixed Spanish idiom for "upon/when X-ing," regardless of which Hebrew preposition is present — treat "al" as a single primary marker, not decomposed into "a"+"el". Infinitive → main Spanish verbal element: primary.
  בְּשָׁמְעוֹ "al oír":
    source=[bePrepPart], target=["al"]   — primary (fixed idiomatic marker)
    source=[verbPart],   target=["oír"] — primary (suffix subject typically has no separate Spanish correspondent — see PERSONAL INFINITIVE below)

### No personal infinitive
Unlike Portuguese, Spanish infinitives do not inflect for person/number. When a Hebrew infinitive construct carries a pronominal suffix marking its subject, Spanish has no ending to carry that information: if the translation supplies an explicit subject pronoun, align it as a normal suffix correspondent (see PRONOMINAL SUFFIXES); if it supplies none, leave the suffix unrecorded — not NEQ.

### Infinitive absolute (cognate emphasis)
Infinitive absolute → Spanish emphasis phrase ("ciertamente"/"de cierto"/"en verdad"): primary 1:1. Finite verb → main Spanish verb: primary.
  מוֹת תָּמוּת → "de cierto morirás":
    source=[infAbsId], target=["de", "cierto"] — both primary
    source=[verbId],   target=["morirás"]      — primary 1:1 (Spanish future is synthetic — no auxiliary "shall"/"will" word to secondary-mark, unlike English)
  Absorbed without separate Spanish word → infinitive absolute secondary to finite verb, or NEQ if definitively untranslated.\
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

SPA_OT_CONFIG = LanguagePromptConfig(
    language_code="spa",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(SPA_OT_CONFIG)
