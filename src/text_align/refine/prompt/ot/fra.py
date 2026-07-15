"""French target-language prompt config for OT (Hebrew) refine-alignment.

Examples checked against LSG (1910, full OT) and cross-checked against
TOB10 (modern, full OT) — see docs/alignment-principles-ot.fra.md's
Cross-translation methodology note.

Key differences from OT Portuguese/Spanish (por.py/spa.py):
  BASE_BLOCK           — NOT pro-drop (inverse default from Portuguese/Spanish):
                         a supplied subject pronoun is normally present and
                         normally secondary, since French grammatically
                         requires one in nearly every finite clause. Contracted
                         forms are gender-conditioned (du/des/au/aux only for
                         masculine/plural nouns; de la/à la stay two words for
                         feminine singular) — a genuinely new axis of variation
                         versus Spanish's fixed del/al. Hebrew's own
                         double-article attributive pattern (הָאָרֶץ הַטּוֹבָה)
                         parallels Greek's τὴν γῆν τὴν καλήν and gets the same
                         first-article-primary/second-secondary treatment.
                         Geographic proper names keep the article (le Jourdain);
                         personal names drop it (Jésus) — a place/person split,
                         not a translator's-choice split like Portuguese.
  PRONOMINAL_SUFFIX_BLOCK — no preposition+pronoun fusion at all (avec moi,
                         chez moi always stay two words) — simpler than both
                         Portuguese and Spanish here.
  NEGATION_BLOCK       — full ne…X discontinuous structure (closer to OT
                         English's discontiguous treatment than to Portuguese/
                         Spanish's simplified contiguous version). "point" is
                         a dated LSG-era alternative to "pas" (1,836 OT
                         instances in LSG vs. 133 in modern TOB10) — align
                         like "pas" but don't expect it from modern
                         translations. "aucun(e)" is a stable alternative to
                         personne/rien/nul.
  INFINITIVE_BLOCK     — gérondif (en + present participle) for the temporal
                         בְּ+infinitive construction; no personal infinitive;
                         infinitive absolute still needs a secondary subject
                         pronoun despite French's synthetic future, because
                         French is not pro-drop.
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

Word-part present → align French correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Subject pronoun — French is NOT pro-drop. Verb forms are often phonologically ambiguous, so French grammatically requires a subject pronoun in nearly all finite clauses, even where Hebrew encodes person/number only in the verb ending (waw-consecutive, etc.). When no separate Hebrew pronoun token is present, the French subject pronoun is secondary to the verb — this is the normal case, not the exception (contrast Portuguese/Spanish, where a supplied pronoun is the less common case).
  וַיֹּאמֶר → "et il dit" — "et" primary (waw word-part); "dit" primary (verb token); "il" secondary
  Explicit independent pronoun (rare, resumptive): הוּא אָמַר → "lui, il dit" — "lui" primary to הוּא; "dit" primary to the verb; "il" still secondary (grammatically required regardless).
- "de" from construct chain — no preposition token; genitive by construct form. "de" secondary to construct noun — UNLESS the absolute noun's own article word-part contracts with "de" (masculine/plural only; see CONSTRUCT CHAINS and ARTICLES).
- French "le/la/les" when article merged — no article word-part; "le/la/les" secondary to noun token.
- Preposition+article merged (בַּ/לַ/כַּ/מֵהַ) — contraction is gender-conditioned: masculine/plural nouns after לַ/מֵהַ produce a single fused French word (au/aux/du/des), primary 1:1 to the one Hebrew token, no split; feminine singular nouns after לַ/מֵהַ, and any gender after בַּ/כַּ, never contract in French ("à la", "dans le/la", "comme le/la") — split as in English (preposition primary, article secondary). See ARTICLES and INSEPARABLE PREPOSITIONS for detail.
- Auxiliary verbs for participles ("était assis") — main verb primary; auxiliary secondary.

- Periphrastic rendering — when a single Hebrew token is rendered by multiple French words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, morphologically rich stems, or words whose French rendering distributes the meaning. Never NEQ a target word that expresses a component of the source word's meaning.
  מָשַׁל → "exerce sa domination sur": "exerce", "domination" primary; "sa", "sur" secondary
  שֹׁמֵר (substantive participle) → "celui qui garde": "garde" primary; "celui", "qui" secondary
  הוֹדוּ → "rendre grâce": "rendre", "grâce" both primary
  הֵיטִיב → "faire du bien": "faire", "bien" primary; "du" secondary (partitive)

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no French equivalent). Rare exception: when explicitly rendered "quant à" or similar.
Supplied copula ("est", "sont", "était", "étaient") with no Hebrew verb token → NEQ target (verbless clause).
  יְהוָה אֱלֹהֵינוּ → "le SEIGNEUR est notre Dieu":
    source=[יְהוָה], target=["SEIGNEUR"] — primary; "le" secondary (reinstated article)
    source=[אֱלֹהֵינוּ], target=["notre", "Dieu"] — primary: "Dieu"; secondary: "notre" (suffix)
    "est" → NEQ target
Waw conjunction + French asyndeton → waw word-part NEQ source.
French conjunction with no Hebrew conjunction token → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Create separate records whenever source tokens (or word-parts) can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.
Grammar-required translation words (pronominal suffix, construct-chain particle ["de"], modal helpers for verbal morphology ["pourrait," "devrait," "aurait"], implied article, required subject pronoun) are secondary to the source token or word-part whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
- Article word-part → "le/la/les": primary 1:1; noun gets its own record.
- Article word-part, no French "le/la/les": secondary to the noun in the noun's record.
- No article word-part, French "le/la/les" present: secondary to the noun token.
- French "un/une": secondary to the noun (Hebrew has no indefinite article). Partitive "du"/"de la"/"des" for anarthrous mass nouns: secondary to the noun.
  לֶחֶם "du pain" (anarthrous, partitive): source=[לֶחֶם], target=["du", "pain"] — primary: "pain"; secondary.target: ["du"]
- Double-article attributive: Hebrew marks an attributive adjective with its own article word-part, parallel to Greek's double article (הָאָרֶץ הַטּוֹבָה, lit. "the-land the-good"). French uses one article. First article (on the noun) → French article (Branch A, primary 1:1); second article (on the adjective) → secondary to the adjective.
  הָאָרֶץ הַטּוֹבָה → "la bonne terre":
    source=[articlePart₁], target=["la"]    — primary 1:1
    source=[אָרֶץ],         target=["terre"] — primary 1:1
    source=[articlePart₂, טּוֹבָה], target=["bonne"] — primary: "bonne"; secondary.source: [articlePart₂]
- Article before proper name: geographic names keep the French article (le Jourdain, le Liban) — primary 1:1 when the Hebrew article word-part is present. Personal names drop it (Jésus, David) — secondary to the name, never NEQ.

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token.
- Construct noun → French head noun: primary. French "de" → secondary in construct noun's record — UNLESS the absolute noun carries its own Hebrew article word-part AND is masculine/plural, in which case the contraction ("du"/"des") is assigned entirely to that article token's own record (Branch A above), and no secondary is added to the construct noun's record.
  בֵּית דָּוִד → "maison de David" (no article — proper name):
    source=[בֵּית], target=["maison", "de"] — primary: "maison"; secondary: "de"
    source=[דָּוִד], target=["David"] — primary 1:1
  בֶּן־הַמֶּלֶךְ → "fils du roi" (absolute noun has its own article word-part, masculine — contracts):
    source=[בֶּן],          target=["fils"] — primary 1:1 (no "de" secondary needed)
    source=[articlePart],  target=["du"]   — primary 1:1 (contraction absorbs the implied "de")
    source=[מֶּלֶךְ],        target=["roi"]  — primary 1:1
  בַּת הָעִיר → "fille de la ville" (absolute noun has its own article word-part, feminine — no contraction):
    source=[בַּת],          target=["fille", "de"] — primary: "fille"; secondary: "de" (no contraction absorbs it here)
    source=[articlePart],  target=["la"]           — primary 1:1
    source=[עִיר],          target=["ville"]        — primary 1:1
- Construct definiteness: French article/contraction before a construct noun (no article token) → secondary to that noun.

## INSEPARABLE PREPOSITIONS
Preposition word-part alone (no merged article) → French preposition (de/à/comme/dans): primary 1:1.
Preposition + merged article in the same token — contraction is gender-conditioned:
- לַ / מֵהַ (le/min + article) before a masculine/plural noun → single French word ("au"/"aux"/"du"/"des"), primary 1:1 to the one merged token, no split.
- לַ / מֵהַ before a feminine singular noun → "à la"/"de la" (no contraction): split — preposition primary, article secondary.
- בַּ / כַּ (be/ke + article) → never contract in French regardless of gender ("dans le/la", "comme le/la"): always split — preposition primary, article secondary.
  לַמֶּלֶךְ "au roi" (masculine, single merged token): source=[lammelekId], target=["au", "roi"] — primary: "au" (contracted à+le), "roi"
  לַמַּלְכָּה "à la reine" (feminine, single merged token, no contraction): source=[lammalkahId], target=["à", "la", "reine"] — primary: "à", "reine"; secondary.target: ["la"]
  בַּבַּיִת "dans la maison" (never contracts): source=[babbayitId], target=["dans", "la", "maison"] — primary: "dans", "maison"; secondary.target: ["la"]

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "et"/"mais"/"alors"/"donc"/"or": primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever French word carries its force in context ("que", "car", "parce que"). Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — "qui"/"que"/"où"/etc. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source units are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES
Pronominal suffixes are separate word-part tokens (pos=suffix). Each suffix → French pronoun, primary 1:1.

- Possessive suffix on noun: suffix → possessive pronoun (primary); noun → head noun (primary).
  דְּבָרוֹ "sa parole": source=[davarPart], target=["parole"] — primary; source=[sufPart], target=["sa"] — primary

- Object suffix on verb: suffix → object pronoun, primary 1:1. The verb record also carries its own required subject pronoun as secondary (French is not pro-drop — see BASE_BLOCK).
  שְׁמָרֵנוּ "il nous a gardés": source=[shamarPart], target=["il", "a", "gardés"] — primary: "gardés"; secondary: "il", "a"; source=[nuPart], target=["nous"] — primary

- Suffix on preposition: suffix → governed pronoun, primary 1:1. Unlike Portuguese/Spanish, French never fuses a preposition with the following pronoun (avec moi, chez moi, sur moi always stay two words) — every case aligns as a plain 1:1 pair.
  אֵלָיו "à lui": source=[elPart], target=["à"] — primary; source=[sufPart], target=["lui"] — primary\
"""

NEGATION_BLOCK = """\
## NEGATION

### Standard French negation (ne…X)
Discontinuous: **ne** (pre-verbal) + a post-verbal negative word (**pas**, **jamais**, **plus**, **rien**, **point** — dated/LSG-style variant of "pas", same treatment) correspond to one Hebrew negation word-part (לֹא, אַל). "aucun(e)" is a stable alternative to personne/rien/nul for negative-pronoun contexts.

- "ne" is **primary** to the Hebrew negation word-part; the post-verbal word (pas, plus, jamais, rien, point, etc.) is **secondary** in the same record — required by French grammar but not a separate Hebrew correspondent. Never NEQ the post-verbal word.
- The negated verb gets its own record with auxiliaries and the required subject pronoun; **do not include "ne" or "pas" in the verb record**.
- The verb record is discontiguous: "ne" precedes and "pas" follows the verb, but both stay in the negation record.

  לֹא יֵדַע → "il ne sait pas":
    source=[loId],   target=["ne", "pas"]  — primary: "ne"; secondary.target: ["pas"]
    source=[verbId], target=["il", "sait"] — primary: "sait"; secondary: "il"

### אַל (jussive/imperative negation)
Same ne…X structure: "ne" primary; post-verbal word secondary.
  אַל תִּירָא → "ne crains pas": source=[alId], target=["ne", "pas"] — primary: "ne"; secondary.target: ["pas"]; source=[verbId], target=["crains"] — primary 1:1

### אֵין / אַיִן (existential negation)
Fixed idiomatic expression — no single word bears the negation alone: all words primary 1:N.
  source=[einId], target=["il", "n'y", "a", "pas"] — all primary
  Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "il n'est pas") → suffix word-part primary 1:1 (see PRONOMINAL SUFFIXES).

### Restrictive "ne…que" (= "only")
When Hebrew רַק/אַךְ ("only") → "ne…que", both "ne" and "que" are **primary** to the Hebrew word for "only" — do not treat "ne" here as a negation particle.
  source=[raqId], target=["ne", "que"] — both primary\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival: align to French adjective or participial modifier — primary.
- Substantive with article word-part: article → French "celui qui"/"ceux qui" primary 1:1; "qui" secondary to participle.
  הַשֹּׁמֵר "celui qui garde":
    source=[articlePart],  target=["celui"]         — primary 1:1
    source=[participleId], target=["qui", "garde"]  — primary: "garde"; secondary: "qui"
  Anarthrous substantive (no article token): all nominalizing elements ("celui", "qui") secondary to participle.
- Verbal (predicative): French auxiliary ("était"/"est"/"étaient") secondary; main verbal element primary.
  יֹשֵׁב "était assis": source=[participleId], target=["était", "assis"] — primary: "assis"; secondary: "était"
- Periphrastic (participle + explicit הָיָה): הָיָה → French auxiliary, separate primary record; participle → main verb, primary.
  source=[hayahId],      target=["était"] — primary 1:1
  source=[participleId], target=["assis"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
- Separate לְ word-part (pos=preposition): if purposive, לְ → "pour"/"afin de" primary 1:1; infinitive → French verb primary. If purely complementary, infinitive is primary alone — no separate correspondent for לְ (unlike English "to").
  רָצָה לָלֶכֶת → "voulut partir": source=[verbPart], target=["partir"] — primary 1:1 (no "to"-equivalent secondary)
- Governed infinitive: many French verbs govern their infinitive complement with "de" or "à" (cessa de, commença à) with no Hebrew correspondent — secondary to the infinitive.
  הֵחֵל לְדַבֵּר → "commença à parler": source=[verbPart], target=["à", "parler"] — primary: "parler"; secondary: "à"

### Purpose/temporal constructions (בְּ/לְ + infinitive)
Temporal (בְּ + infinitive, "when/while X-ing"): French renders this with the **gérondif** (en + present participle). "en" primary to the preposition word-part; infinitive → French present participle, primary.
  בְּשָׁמְעוֹ "en entendant": source=[bePrepPart], target=["en"] — primary; source=[verbPart], target=["entendant"] — primary (the gérondif does not inflect for person — a suffix-marked subject typically has no separate French correspondent here)
Purpose (לְ + infinitive, "in order to"): לְ → "pour"/"afin de" primary 1:1; infinitive primary.
  לָתֵת "pour donner": source=[verbPart], target=["pour", "donner"] — both primary (purpose marker + infinitive)

### No personal infinitive
Like Spanish, French infinitives (and the gérondif) do not inflect for person/number. When a Hebrew infinitive construct carries a pronominal suffix marking its subject, French has no ending to carry it: if the translation supplies an explicit pronoun, align it as a normal suffix correspondent (see PRONOMINAL SUFFIXES); if it supplies none, leave the suffix unrecorded — not NEQ.

### Infinitive absolute (cognate emphasis)
Infinitive absolute → French emphasis word ("certainement"/"assurément"): primary 1:1. Finite verb → main French verb: primary.
  מוֹת תָּמוּת → "certainement tu mourras":
    source=[infAbsId], target=["certainement"] — primary 1:1
    source=[verbId],   target=["tu", "mourras"] — primary: "mourras"; secondary: "tu" (required subject pronoun — French is not pro-drop, so this stays secondary even though French, like Portuguese/Spanish, has a synthetic future with no auxiliary "shall"/"will" to mark)
  Absorbed without separate French word → infinitive absolute secondary to finite verb, or NEQ if definitively untranslated.\
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

FRA_OT_CONFIG = LanguagePromptConfig(
    language_code="fra",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(FRA_OT_CONFIG)
