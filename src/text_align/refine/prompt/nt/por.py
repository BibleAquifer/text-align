"""Portuguese target-language prompt config for refine-alignment.

Key differences from English (eng.py):
  BASE_BLOCK    — pro-drop subject pronouns; contracted preposition+article forms
                  (do/da/no/na/ao/à/pelo/pela); conditional proper-name article (BP
                  retains article before proper names).
  PASSIVE_BLOCK — adds reflexive passive (se + verb).
  INFINITIVE_BLOCK — adds personal infinitive note; no "to" marker.
  HINA_BLOCK    — para que/a fim de que + subjunctive examples.

Prose reference preserved in por.prose.py.
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
    NEGATION_BLOCK,
    HOTI_BLOCK,
    PARTICIPLE_BLOCK,
    VERBAL_ASPECT_BLOCK,
)


# ---------------------------------------------------------------------------
# Portuguese-specific prompt blocks
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

- Pro-drop subject pronoun — Portuguese encodes person/number in the verb ending. When no subject pronoun appears in the translation, none is expected (verb alone is primary). When a pronoun IS present without a corresponding Greek pronoun → secondary. When it corresponds to an explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.) → primary.
  ἦλθεν → "veio" — "veio" primary; no secondary
  ἦλθεν → "ele veio" (supplied for clarity) — "veio" primary; "ele" secondary

- Auxiliary verb — ἐδίδασκεν → "estava ensinando": "ensinando" primary; "estava" secondary

- Indefinite article — ἄνθρωπος → "um homem": "homem" primary; "um" secondary

- Case-implied preposition — θεοῦ → "de Deus": "Deus" primary; "de" secondary (contracted form: see ARTICLES)

- Periphrastic rendering — when a single Greek token is rendered by multiple Portuguese words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, compound nouns, or morphologically rich stems. Never NEQ a target word that expresses a component of the source word's meaning.
  κυριεύει → "exerce domínio sobre": "exerce", "domínio" primary; "sobre" secondary
  γινώσκουσιν (dative substantive participle) → "aos que conhecem": "conhecem" primary; "aos", "que" secondary
  καρποφορέω → "dar fruto": "dar", "fruto" both primary
  φιλαδελφία → "amor fraternal": "amor", "fraternal" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — always secondary to head when no Portuguese correspondent. See ARTICLES → Branch B.
Supplied copula ("é", "são", "era", "eram") with no Greek εἶναι → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES

For every Greek article (POS T-*): does it have a specific Portuguese word or contracted form as its direct correspondent?
YES → Branch A (primary 1:1). NO → Branch B (secondary to head — never NEQ, never omitted).
A Greek article is NEVER NEQ and NEVER omitted — it never gets its own record; it is always secondary to the noun, adjective, participle, or proper name it modifies. A Greek article NEVER corresponds to a preposition.

### Branch A — article has a Portuguese correspondent

- → "o/a/os/as": 1:1 primary; noun/adjective/participle in its own record.
  ὁ λόγος → "o Verbo":
    source=[ὁ],     target=["o"]     — primary 1:1
    source=[λόγος], target=["Verbo"] — primary 1:1

- → contracted preposition + article (do/da/no/na/ao/à/pelo/pela):
  Greek article only (case-implied preposition, no separate Greek preposition token):
  Contracted form is the article's correspondent; the "de/em/a/por" component is absorbed — no separate secondary.
    τοῦ λόγου → "do Verbo" (genitive, no separate Greek preposition):
      source=[τοῦ],   target=["do"]    — primary 1:1
      source=[λόγου], target=["Verbo"] — primary 1:1
  Greek preposition + article both present:
  Contracted form → primary to preposition; article is secondary.source.
    ἐν τῷ ναῷ → "no templo":
      source=[ἐν, τῷ], target=["no"]     — primary: ἐν; secondary.source: [τῷ]
      source=[ναῷ],    target=["templo"] — primary 1:1

- → possessive pronoun ("seu/sua/seus/suas", "meu", "nosso"): 1:1 primary — ONLY when no explicit Greek possessive pronoun present.
  τοὺς ὀφθαλμούς → "seus olhos" (no explicit pronoun):
    source=[τούς],       target=["seus"]  — primary 1:1
    source=[ὀφθαλμούς], target=["olhos"] — primary 1:1

- → "os que"/"aquele que" (substantive participle): article → "os"/"aquele" primary 1:1; "que" secondary to participle.
  τοῖς πιστεύουσιν → "aos que creem":
    source=[τοῖς],        target=["aos"]           — primary 1:1 (contracted ao + article)
    source=[πιστεύουσιν], target=["que", "creem"]  — primary: "creem"; secondary: "que"

- → article before proper name (Brazilian Portuguese retains article): 1:1 primary when present; apply Branch B when absent.
  ὁ Ἰησοῦς → "o Jesus":
    source=[ὁ],       target=["o"]     — primary 1:1
    source=[Ἰησοῦς], target=["Jesus"] — primary 1:1
  ὁ Ἰησοῦς → "Jesus" (translation omits article):
    source=[ὁ, Ἰησοῦς], target=["Jesus"] — primary: "Jesus"; secondary.source: [ὁ]

### Branch B — no Portuguese correspondent → secondary to head

Apply to each article independently; the head is always the word it grammatically modifies.
- Articular noun, no article: source=[τήν, χεῖρα], target=["mão"] — primary: "mão"; secondary.source: [τήν]
- Attributive adjective: secondary to adjective (not noun), each article separately.
  τὴν γῆν τὴν καλήν → "boa terra":
    source=[τήν, γῆν],   target=["terra"] — primary: "terra"; secondary.source: [τήν]
    source=[τήN, καλήν], target=["boa"]   — primary: "boa"; secondary.source: [τήN]
- Articular infinitive: secondary to infinitive. ἐν τῷ σπείρειν → "ao semear":
    source=[ἐν, τῷ],    target=["ao"]     — primary: ἐν; secondary.source: [τῷ]
    source=[σπείρειν],  target=["semear"] — primary 1:1

### Anarthrous noun → "um/uma"
source=[ἄνθρωπος], target=["um", "homem"] — primary: "homem"; secondary.target: ["um"]

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "de modo que": all three primary).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  μὴ γένοιτο — optative negation ("De modo algum!" / "Nunca!" / "Longe disso!"):
    When no token-level mapping is possible: is_idiom: true.
      source=[μή, γένοιτο], target=["De","modo","algum"] — is_idiom: true
    When the rendering permits, prefer granular alignment: μή → negation words; γένοιτο → verb "ser/estar".\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE
Auxiliary + past participle: past participle primary; auxiliary ("foi", "está", "tem sido") secondary.
Supplied subject pronoun absent from Greek: secondary. Pro-drop means this is uncommon in Portuguese.
Passive "it": secondary — contrast impersonal dummy "it" (see IMPERSONAL VERBS), which is NEQ.

### Reflexive passive (se + verb)
Main verb primary; "se" secondary (voice is morphological in Greek, lexical in Portuguese).
  γέγραπται → "se escreveu":
    source=[γέγραπται], target=["se", "escreveu"] — primary: "escreveu"; secondary: "se"

γέγραπται → "está escrito":
  source=[γέγραπται], target=["está", "escrito"] — primary: "escrito"; secondary: "está"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Infinitive primary; no separate marker in Portuguese (unlike English "to").
  θέλω ἐλθεῖν → "quero vir": source=[ἐλθεῖν], target=["vir"] — primary 1:1

### Purpose infinitive with "para"
"para" carries purpose force → secondary to the infinitive when purpose is already in the Greek verb; primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
  ἦλθεν σῴζειν → "veio para salvar":
    source=[σῴζειν], target=["para", "salvar"] — primary: "salvar"; secondary: "para"

### Articular infinitive
Article secondary to infinitive (never NEQ); absorbed into contracted form when applicable (see ARTICLES).
  ἐν τῷ σπείρειν αὐτόν → "ao semear ele":
    source=[ἐν, τῷ],   target=["ao"]     — primary: ἐν; secondary.source: [τῷ]
    source=[αὐτόν],    target=["ele"]    — primary
    source=[σπείρειν], target=["semear"] — primary 1:1

### Personal infinitive
Portuguese inflects the infinitive for person/number (fazermos, fazerem, etc.). These endings encode the same information as Greek verb endings; no secondary token is expected.

### Indirect discourse
Supplied "que" introducing indirect statement → secondary to governing verb — not to the infinitive.
  λέγει αὐτὸν εἶναι → "diz que ele é":
    source=[λέγει],  target=["diz"]
    source=[αὐτόν], target=["ele"]
    source=[εἶναι], target=["que", "é"] — primary: "é"; secondary: "que"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- → "para que"/"a fim de que" (purpose conjunction): conjunction primary; verbs/content words align normally. Subjunctive mood does not add a secondary token.
- → bare "para" + infinitive: "para" primary to ἵνα (not secondary to the infinitive).
- No correspondent → NEQ source (only when certain no element expresses purpose/result force).

  ἵνα σωθῇ → "para que seja salvo":
    source=[ἵνα], target=["para", "que"] — both primary

  ἵνα σῴζῃ → "para salvar":
    source=[ἵνα],   target=["para"]   — primary (purpose marker)
    source=[σῴζῃ], target=["salvar"] — primary\
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

POR_CONFIG = LanguagePromptConfig(
    language_code="por",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(POR_CONFIG)
