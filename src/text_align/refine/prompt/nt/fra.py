"""French target-language prompt config for refine-alignment.

Key differences from English (eng.py):
  BASE_BLOCK    — NOT pro-drop: subject pronouns required; absent Greek pronoun →
                  French pronoun secondary (inverse of Spanish/Portuguese).
                  Contracted forms du/des/au/aux (non-contracting stay two words).
                  Double-article attributive: first article → French article (Branch A);
                  second → secondary to adjective (Branch B). Partitive du/de la/des
                  secondary to noun (no Greek article token present).
  PASSIVE_BLOCK — reflexive passive (se + verb); "on" + active as passive equivalent.
  INFINITIVE_BLOCK — governed "de"/"à" secondary; gérondif for articular infinitive.
  HINA_BLOCK    — pour que/afin que + subjunctive; bare "que" + subjunctive; pour/afin de + infinitive.
  NEGATION_BLOCK — discontinuous ne…X structure; compound tokens; restrictive ne…que.

Prose reference preserved in fra.prose.py.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import (
    AUTOS_BLOCK,
    COMPARATIVE_BLOCK,
    CONDITIONAL_BLOCK,
    BLOCK_ORDER,
    FORCED_INCLUSIONS,
    IMPERSONAL_BLOCK,
    HOTI_BLOCK,
    PARTICIPLE_BLOCK,
    VERBAL_ASPECT_BLOCK,
)


# ---------------------------------------------------------------------------
# French-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied prepositions, morphologically-implied pronouns, and context-implied articles. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Create separate records whenever source tokens can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (implied pronoun, case preposition, modal helpers for verbal morphology ["could," "might," "would"], reinstated article) are secondary to the source token whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Greek token
secondary — exists only because of grammatical features in the Greek token's morphology (person, number, case, aspect, voice); no separate Greek word
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- Subject pronoun — French is NOT pro-drop. Verb forms are often phonologically ambiguous, so French grammatically requires a subject pronoun in nearly all finite clauses. When no Greek pronoun is present, the French subject pronoun is secondary to the verb. When an explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.) is present, the French pronoun is primary to that pronoun.
  ἦλθεν → "il vint" — "vint" primary; "il" secondary
  αὐτὸς ἦλθεν → "lui-même vint" — "vint" primary to ἦλθεν; "lui-même" primary to αὐτός

- Auxiliary verb — δεδίδαχεν → "a enseigné": "enseigné" primary; "a" secondary

- No infinitive marker — λαβεῖν → "prendre": primary alone. "pour"/"afin de" for purpose: see purpose infinitive rules.

- Indefinite article — ἄνθρωπος → "un homme": "homme" primary; "un" secondary

- Case-implied preposition — θεοῦ → "de Dieu": "Dieu" primary; "de" secondary (contracted form: see ARTICLES)

- Periphrastic rendering — when a single Greek token is rendered by multiple French words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, compound nouns, or morphologically rich stems. Never NEQ a target word that expresses a component of the source word's meaning.
  κυριεύει → "exerce son pouvoir sur": "exerce", "pouvoir" primary; "son", "sur" secondary
  γινώσκουσιν (dative substantive participle) → "à des gens qui connaissent": "connaissent" primary; "à", "des", "gens", "qui" secondary
  καρποφορέω → "porter du fruit": "porter", "fruit" primary; "du" secondary
  φιλαδελφία → "amour fraternel": "amour", "fraternel" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — always secondary to head when no French correspondent. See ARTICLES → Branch B.
Supplied copula ("est", "sont", "était", "étaient") with no Greek εἶναι → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES

For every Greek article (POS T-*): does it have a specific French word or contracted form as its direct correspondent?
YES → Branch A (primary 1:1). NO → Branch B (secondary to head — never NEQ, never omitted).
A Greek article is NEVER NEQ and NEVER omitted — it never gets its own record; it is always secondary to the noun, adjective, participle, or proper name it modifies. A Greek article NEVER corresponds to a preposition.

### Branch A — article has a French correspondent

- → "le/la/les": 1:1 primary; noun/adjective/participle in its own record.
  ὁ λόγος → "le Verbe":
    source=[ὁ],     target=["le"]    — primary 1:1
    source=[λόγος], target=["Verbe"] — primary 1:1

- → contracted preposition + article (du / des / au / aux only):
  French contracts de+le → du, de+les → des, à+le → au, à+les → aux. Non-contracting forms (de la, de l', à la, dans le/la, sur le/la, etc.) stay as separate words — the article aligns normally to its French correspondent or Branch B.
  Greek article only (case-implied preposition, no separate Greek preposition token):
  Contracted form is the article's correspondent; the "de/à" component is absorbed — no separate secondary.
    τοῦ λόγου → "du Verbe" (genitive, no separate Greek preposition):
      source=[τοῦ],   target=["du"]    — primary 1:1
      source=[λόγου], target=["Verbe"] — primary 1:1
  Greek preposition + article both present:
  Contracted form → primary to preposition; article is secondary.source.
    εἰς τὸν οὐρανόν → "au ciel":
      source=[εἰς, τόν], target=["au"]   — primary: εἰς; secondary.source: [τόν]
      source=[οὐρανόν],  target=["ciel"] — primary 1:1

- → possessive pronoun ("son/sa/ses", "leur/leurs", "mon/ma", "notre/nos"): 1:1 primary — ONLY when no explicit Greek possessive pronoun present.
  τοὺς ὀφθαλμούς → "ses yeux" (no explicit pronoun):
    source=[τούς],       target=["ses"]  — primary 1:1
    source=[ὀφθαλμούς], target=["yeux"] — primary 1:1
  With explicit αὐτῶν: τοὺς ὀφθαλμοὺς αὐτῶν → "leurs yeux":
    source=[αὐτῶν],            target=["leurs"] — primary 1:1
    source=[τούς, ὀφθαλμούς], target=["yeux"]  — primary: "yeux"; secondary.source: [τούς]

- → "ceux qui"/"celui qui" (substantive participle): article → "ceux"/"celui" primary 1:1; "qui" secondary to participle.
  τοῖς πιστεύουσιν → "à ceux qui croient":
    source=[τοῖς],        target=["ceux"]           — primary 1:1
    source=[πιστεύουσιν], target=["qui", "croient"] — primary: "croient"; secondary: "qui"
    "à" → secondary to πιστεύουσιν (dative case-implied)

### Branch B — no French correspondent → secondary to head

Apply to each article independently; the head is always the word it grammatically modifies.
French Bible translations (LS 1910 and modern) omit the article before proper names.

- Articular noun, no article: source=[τήν, χεῖρα], target=["main"] — primary: "main"; secondary.source: [τήν]
- Double-article attributive (τὴν γῆν τὴν καλήν): Greek uses two articles; French uses one. First article → French article (Branch A); second article → secondary to adjective (Branch B).
  τὴν γῆν τὴν καλήν → "la bonne terre":
    source=[τήν₁],        target=["la"]    — primary 1:1
    source=[γῆν],         target=["terre"] — primary 1:1
    source=[τήν₂, καλήν], target=["bonne"] — primary: "bonne"; secondary.source: [τήν₂]
- Articular infinitive: secondary to infinitive (or absorbed into "au"/"du" — see Branch A).
  τοῦ πιστεύειν → "de croire":
    source=[τοῦ, πιστεύειν], target=["de", "croire"] — primary: "croire"; secondary.source: [τοῦ]; secondary.target: ["de"]
- Article before proper name: ὁ Ἰησοῦς → "Jésus":
    source=[ὁ, Ἰησοῦς], target=["Jésus"] — primary: "Jésus"; secondary.source: [ὁ]

### Anarthrous noun → "un/une" or partitive

No Greek article token exists. Two cases:
- Count noun: "un/une" secondary. ἄνθρωπος → "un homme": source=[ἄνθρωπος], target=["un", "homme"] — primary: "homme"; secondary.target: ["un"]
- Partitive (mass/uncountable): du/de la/des secondary. Distinguish from contracted article: du/de la is partitive only when no Greek article token is present; otherwise align under Branch A.
  ἄρτον → "du pain" (anarthrous, partitive): source=[ἄρτον], target=["du", "pain"] — primary: "pain"; secondary.target: ["du"]

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "de sorte que": all three primary).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  καὶ ἐγένετο → "Et il arriva que":
    Wrong:  source=[καὶ, ἐγένετο], target=["Et","il","arriva","que"], meta.is_idiom: true
    Better: source=[καὶ], target=["Et"] — primary 1:1
            source=[ἐγένετο], target=["il","arriva","que"] — primary: "arriva"; secondary: "il", "que"

  μὴ γένοιτο — optative negation ("Loin de là !" / "Certes non !" / "À Dieu ne plaise !"):
    French translations typically render this as a fixed idiom with no token-level mapping — use is_idiom: true. Only prefer standard records if the translation is literal enough to allow granular alignment (μή → negation; γένοιτο → verb).
      source=[μή, γένοιτο], target=["Loin","de","là"] — is_idiom: true\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE
Auxiliary + past participle: past participle primary; auxiliary ("a été", "est") secondary.
Subject pronoun required by French grammar: secondary (person/number from Greek morphology, not a separate token).

### Reflexive passive (se + verb)
Main verb primary; "se/s'" secondary — voice is morphological in Greek, lexical in French.
  γέγραπται → "il s'accomplit":
    source=[γέγραπται], target=["il", "s'", "accomplit"] — primary: "accomplit"; secondary: "il", "s'"

### Impersonal "on" as passive equivalent
Greek passive rendered as "on" + active verb: main verb primary; "on" secondary — no separate Greek correspondent.
  ἐρρέθη → "on dit": source=[ἐρρέθη], target=["on", "dit"] — primary: "dit"; secondary: "on"

γέγραπται → "il est écrit":
  source=[γέγραπται], target=["il", "est", "écrit"] — primary: "écrit"; secondary: "est", "il"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Infinitive primary; no separate marker in French (unlike English "to").
  θέλω ἐλθεῖν → "je veux venir": source=[ἐλθεῖν], target=["venir"] — primary 1:1

### Governed infinitives with "de" or "à"
Many French verbs govern their infinitive complement with "de" (cesser de, permettre de) or "à" (commencer à, aider à). These prepositions are secondary to the infinitive — grammatical connectors with no separate Greek correspondent.
  ἤρξατο διδάσκειν → "commença à enseigner":
    source=[διδάσκειν], target=["à", "enseigner"] — primary: "enseigner"; secondary: "à"

### Purpose infinitive with "pour"/"afin de"
"pour"/"afin de" secondary to infinitive when purpose is already in the Greek verb; primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
  ἦλθεν σῴζειν → "il vint pour sauver":
    source=[σῴζειν], target=["pour", "sauver"] — primary: "sauver"; secondary: "pour"

### Articular infinitive → gérondif
When rendered as "en" + present participle: "en" primary to governing preposition; article secondary to participle.
  ἐν τῷ σπείρειν αὐτόν → "en semant":
    source=[ἐν],           target=["en"]    — primary
    source=[τῷ, σπείρειν], target=["semant"] — primary: "semant"; secondary.source: [τῷ]

### Indirect discourse
Supplied "que" → secondary to governing verb — not to the infinitive.
  λέγει αὐτὸν εἶναι → "dit qu'il est":
    source=[λέγει],  target=["dit"]
    source=[αὐτόν], target=["il"]
    source=[εἶναι], target=["que", "est"] — primary: "est"; secondary: "que"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- → "pour que"/"afin que" + subjunctive: all conjunction words primary to ἵνα. Subjunctive mood does not add a secondary token.
- → bare "que" + subjunctive (after verbs of wanting, commanding, permitting): "que" primary to ἵνα.
- → "pour"/"afin de" + infinitive (coreferential subjects): purpose-marking word(s) primary to ἵνα — not secondary to the infinitive.
- No correspondent → NEQ source (only when certain no element expresses purpose/result force).

  ἵνα σωθῇ → "pour qu'il soit sauvé":
    source=[ἵνα], target=["pour", "que"] — both primary

  θέλω ἵνα δῷς → "je veux que tu donnes":
    source=[ἵνα], target=["que"] — primary 1:1

  ἵνα σῴζῃ → "pour sauver":
    source=[ἵνα],   target=["pour"]   — primary (purpose marker)
    source=[σῴζῃ], target=["sauver"] — primary\
"""

NEGATION_BLOCK = """\
## NEGATION

### Standard French negation (ne…X)
French negation is a discontinuous two-part structure: **ne** (pre-verbal) + a post-verbal negative word (**pas**, **jamais**, **plus**, **rien**, etc.). Together they correspond to a single Greek negation particle (οὐ, οὐκ, οὐχ, μή).

- "ne" is **primary** to the Greek negation particle; the post-verbal word (**pas**, **plus**, **jamais**, **rien**, etc.) is **secondary** in the same record — required by French grammar but not a separate Greek correspondent. Never NEQ the post-verbal word.
- The negated verb gets its own record with auxiliaries and subject pronoun; **do not include "ne" or "pas" in the verb record**.
- The verb record is discontiguous: "ne" precedes and "pas" follows the verb, but both stay in the negation record.
- In compound tenses ("il ne l'a pas vu"), "ne" and "pas" are discontiguous across the auxiliary and object clitic — both remain in the negation record.

  οὐκ ἔρχεται → "il ne vient pas":
    source=[οὐκ],     target=["ne", "pas"]  — primary: "ne"; secondary.target: ["pas"]
    source=[ἔρχεται], target=["il", "vient"] — primary: "vient"; secondary: "il"

### Emphatic negation (οὐ μή)
Both Greek particles + both French words primary in a single record (two source tokens justify two primary targets).
  οὐ μή + subjunctive → "ne…jamais [verb]":
    source=[οὐ, μή], target=["ne", "jamais"] — both particles, both words primary

### Compound negation tokens (single Greek token → "ne" primary, post-verbal word secondary)
- οὐκέτι/μηκέτι ("no longer") → "ne…plus": "ne" primary; "plus" secondary
- οὔπω/μήπω ("not yet") → "ne…pas encore": "ne" primary; "pas", "encore" secondary
- οὐδέ/μηδέ ("and not"/"neither"/"nor") → "ni" (primary) or "et ne…pas" ("ne" primary, "pas" secondary)
- οὔτε ("neither…nor") → "ni"
- οὐδείς/μηδείς ("nobody"/"no one"/"nothing") → "personne"/"rien"/"nul" — primary
  source=[οὐκέτι], target=["ne", "plus"] — primary: "ne"; secondary.target: ["plus"]

### Negation with negative pronouns
Negative pronoun (οὐδείς → "personne"/"nul", μηδείς → "rien") primary to its Greek token. "ne" before the verb is retained; "pas" is typically omitted when a strong post-verbal negative is already present.

### Restrictive "ne…que" (= "only") — not a true negation
When Greek μόνον/μόνος → "ne…que", both "ne" and "que" are **primary** to the Greek word for "only". Do not treat "ne" here as a negation particle — the construction is restrictive, not negative.
  source=[μόνον], target=["ne", "que"] — both primary\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PASSIVE":        PASSIVE_BLOCK,
    "IMPERSONAL":     IMPERSONAL_BLOCK,
    "PARTICIPLE":     PARTICIPLE_BLOCK,
    "INFINITIVE":     INFINITIVE_BLOCK,
    "HINA":           HINA_BLOCK,
    "COMPARATIVE":    COMPARATIVE_BLOCK,
    "AUTOS":          AUTOS_BLOCK,
    "HOTI":           HOTI_BLOCK,
    "CONDITIONAL":    CONDITIONAL_BLOCK,
    "NEGATION":       NEGATION_BLOCK,
    "VERBAL_ASPECT":  VERBAL_ASPECT_BLOCK,
}

FRA_CONFIG = LanguagePromptConfig(
    language_code="fra",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(FRA_CONFIG)
