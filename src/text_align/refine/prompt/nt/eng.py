"""English target-language prompt config for refine-alignment.

Imported by prompt/__init__.py to register the English config automatically.
Prose reference preserved in eng.prose.py.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language


# ---------------------------------------------------------------------------
# Prompt blocks
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

- Supplied subject pronoun — ἦλθεν → "he came": "came" primary; "he" secondary
- Auxiliary verb — ἐδίδασκεν → "was teaching": "teaching" primary; "was" secondary
- Infinitive marker — λαβεῖν → "to take": "take" primary; "to" secondary
- Indefinite article — ἄνθρωπος → "a man": "man" primary; "a" secondary
- Case-implied preposition — θεοῦ → "of God": "God" primary; "of" secondary (other words from different records are never secondary here)
- Case-implied preposition with article — τοῖς σάββασιν → "on the Sabbath":
  source=[τοῖς], target=["the"] — primary 1:1
  source=[σάββασιν], target=["on", "Sabbath"] — primary: "Sabbath"; secondary: "on"

- Periphrastic rendering — when a single Greek token is rendered by multiple English words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, compound nouns, or morphologically rich stems. Never NEQ a target word that expresses a component of the source word's meaning.
  κυριεύει → "exercises authority over": "exercises", "authority" primary; "over" secondary
  γινώσκουσιν (dative substantive participle) → "those who know": "know" primary; "those", "who" secondary
  καρποφορέω → "bear fruit": "bear", "fruit" both primary
  φιλαδελφία → "brotherly love": "brotherly", "love" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — always secondary to head when no English correspondent. See ARTICLES → Branch B.
Supplied copula ("is", "are", "was", "were") with no Greek εἶναι → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES

For every Greek article (POS T-*): does it have a direct English correspondent?
YES → Branch A (primary 1:1). NO → Branch B (secondary to head — never NEQ, never omitted).
A Greek article is NEVER NEQ and NEVER omitted — it never gets its own record; it is always secondary to the noun, adjective, participle, or proper name it modifies. A Greek article NEVER corresponds to a preposition.

### Branch A — article has an English correspondent

- → "the": 1:1 primary; noun/adjective/participle in its own record.
  ὁ λόγος → "the word":
    source=[ὁ], target=["the"] — primary 1:1
    source=[λόγος], target=["word"] — primary 1:1

- → possessive pronoun ("his", "her", "their", "its"): 1:1 primary — ONLY when no explicit Greek possessive pronoun (αὐτοῦ, αὐτῆς, αὐτῶν, μου, σου, ἡμῶν, etc.) present.
  τοὺς ὀφθαλμούς → "their eyes" (no explicit pronoun):
    source=[τούς], target=["their"] — primary 1:1
    source=[ὀφθαλμούς], target=["eyes"] — primary 1:1
  With explicit αὐτῶν: τοὺς ὀφθαλμοὺς αὐτῶν → "their eyes":
    source=[αὐτῶν], target=["their"] — primary 1:1
    source=[τούς, ὀφθαλμούς], target=["eyes"] — primary: "eyes"; secondary.source: [τούς]

- → "those"/"the one" (substantive participle): article → "those"/"the one" primary 1:1; "who" secondary to participle; case-implied preposition secondary to participle.
  τοῖς πιστεύουσιν → "to those who believe":
    source=[τοῖς], target=["those"] — primary 1:1
    source=[πιστεύουσιν], target=["who", "believe"] — primary: "believe"; secondary: "who"
    "to" → secondary to πιστεύουσιν (dative case-implied)

### Branch B — no English correspondent → secondary to head

Apply to each article independently; the head is always the word it grammatically modifies.
- Articular noun, no "the": source=[τήν, χεῖρα], target=["hand"] — primary: "hand"; secondary.source: [τήν]
- Attributive adjective: secondary to adjective (not noun), each article separately.
  τὴν γῆν τὴν καλήν → "good soil":
    source=[τήν, γῆν], target=["soil"] — primary: "soil"; secondary.source: [τήν]
    source=[τήν, καλήν], target=["good"] — primary: "good"; secondary.source: [τήN]
- Articular infinitive: secondary to infinitive. ἐν τῷ σπείρειν → "while sowing":
    source=[τῷ, σπείρειν], target=["sowing"] — primary: "sowing"; secondary.source: [τῷ]
- Article before proper name: always secondary — never NEQ.
  ὁ Ἰησοῦς → "Jesus": source=[ὁ, Ἰησοῦς], target=["Jesus"] — primary: "Jesus"; secondary.source: [ὁ]

### Anarthrous noun → "a/an"
source=[ἄνθρωπος], target=["a", "man"] — primary: "man"; secondary.target: ["a"]

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "so that": both primary).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  Wrong:  source=[καὶ, ἐγένετο], target=["Now","it","came","to","pass"], meta.is_idiom: true
  Better: source=[καὶ], target=["Now"] — primary 1:1
          source=[ἐγένετο], target=["it","came","to","pass"] — primary: "came"; secondary: "it", "to", "pass"

  μὴ γένοιτο — optative negation ("God forbid!" / "Certainly not!" / "By no means!"):
    When no token-level mapping is possible: is_idiom: true.
      source=[μή, γένοιτο], target=["God","forbid"] — is_idiom: true
    When the rendering allows granular alignment ("May it never be!"):
      source=[μή],      target=["never"]         — primary 1:1
      source=[γένοιτο], target=["may","it","be"] — primary: "be"; secondary: "may","it"\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE
Auxiliary + past participle: past participle primary; auxiliary ("was", "is", "has been") secondary.
Supplied subject pronoun absent from Greek: secondary (implied by verb's person/number/context).
Passive "it": secondary — contrast impersonal dummy "it" (see IMPERSONAL VERBS), which is NEQ.

γέγραπται → "it is written":
  source=[γέγραπται], target=["it", "is", "written"] — primary: "written"; secondary: "is", "it"\
"""

IMPERSONAL_BLOCK = """\
## IMPERSONAL VERBS
Verbs with no real subject (δεῖ, ἔξεστιν, πρέπει, συμφέρει, δοκεῖ): dummy "it" → NEQ target.
Complementary infinitive aligns normally; "to" secondary. Impersonal verb aligns normally.
Contrast: passive "it" secondary (implied subject); impersonal "it" NEQ (no subject at all).

δεῖ → "it is necessary": source=[δεῖ], target=["is", "necessary"] — both primary; "it" → NEQ
Or: source=[δεῖ], target=["must"] — primary\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adverbial (circumstantial)
Introductory conjunction/adverb secondary; supplied subject pronoun secondary.
  source=[ἀκούσας], target=["when", "he", "heard"] — primary: "heard"; secondary: "when", "he"

### Genitive absolute
Align each element to its correspondent. Introduced conjunctions/adverbs secondary to participle.
  source=[αὐτοῦ], target=["he"] — primary
  source=[λαλοῦντος], target=["while", "was", "speaking"] — primary: "speaking"; secondary: "while", "was"

### Substantive
Apply ARTICLES rules to article. Relative pronouns ("who", "that", "which") secondary to participle.
  source=[πιστεύων], target=["whoever", "believes"] — primary: "believes"; secondary: "whoever"

### Discourse particle adjacent to participle
δέ/καί/οὖν near participle with no correspondent → NEQ source (only when certain).\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Infinitive primary; "to" secondary.
  source=[ἐλθεῖν], target=["to", "come"] — primary: "come"; secondary: "to"

### Articular infinitive
Article secondary to infinitive (never NEQ). Governing prepositions (εἰς τό, ἐν τῷ, πρὸς τό) primary. Aspect auxiliaries secondary.
  ἐν τῷ σπείρειν αὐτόν → "as he was sowing":
    source=[ἐν], target=["as"] — primary
    source=[αὐτόν], target=["he"] — primary
    source=[τῷ, σπείρειν], target=["was", "sowing"] — primary: "sowing"; secondary.source: [τῷ]; secondary.target: ["was"]

### Purpose/result infinitive (without ἵνα)
"to" secondary; purpose conjunctions ("in order to", "so as to") secondary.
  source=[σῴζειν], target=["to", "save"] — primary: "save"; secondary: "to"

### Indirect discourse
Supplied "that" secondary to governing verb — not to the infinitive.
  λέγει αὐτὸν εἶναι → "says that he is":
    source=[λέγει], target=["says"]; source=[αὐτόν], target=["he"]
    source=[εἶναι], target=["that", "is"] — primary: "is"; secondary: "that"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- Purpose/result conjunction ("in order that", "so that", "that"): conjunction primary; verbs/content words align normally.
- Bare "to" (purpose infinitive rendering): "to" primary to ἵνα — not secondary to the infinitive.
- No correspondent → NEQ source.

  source=[ἵνα], target=["that"] — primary 1:1
  source=[ἵνα], target=["to"] — primary (purpose marker); source=[σῴζῃ], target=["save"] — primary\
"""

COMPARATIVE_BLOCK = """\
## COMPARATIVES AND SUPERLATIVES
Greek encodes degree morphologically; English distributes across words. Degree word + base form both primary to the single Greek token. Elative superlative ("very + adj") same pattern.
"Than" in standard of comparison: secondary to the noun/adjective it governs.

  μείζων → "greater": source=[μείζων], target=["greater"] — primary 1:1
  ἁγιώτατος → "most holy": source=[ἁγιώτατος], target=["most", "holy"] — both primary\
"""

AUTOS_BLOCK = """\
## αὐτός

- Intensive (attributive, emphasizes noun/pronoun) → "himself"/"herself"/etc.: primary 1:1; modified noun its own record.
- Reflexive (object refers back to subject) → reflexive pronoun: primary 1:1.
- Third-person pronoun → "him"/"her"/"it"/"them"/"his"/"her"/"their": primary 1:1.
  Translation substitutes proper name: name primary; additionally supplied subject pronoun secondary.
- No correspondent → NEQ source (only when certain).

  source=[αὐτόν], target=["him"] — primary 1:1
  source=[αὐτοῦ], target=["Jesus"] — primary (name substituted)\
"""

HOTI_BLOCK = """\
## ὅτι

- Conjunction ("that", "because", "for"): correspondent primary; no correspondent → NEQ source.
- Recitativum (introduces direct speech after verb of saying/asking): → NEQ source.
- Genuinely ambiguous: prefer conjunction reading.

  source=[ὅτι], target=["that"] — primary 1:1
  source=[ὅτι] → NEQ source (recitativum)\
"""

CONDITIONAL_BLOCK = """\
## CONDITIONAL CONSTRUCTIONS

- εἰ/ἐάν → conditional equivalent ("if", "unless", "whether", "when", etc.): primary. No correspondent → NEQ.
- Supplied "then" (apodosis, no Greek particle) → NEQ target.
- Greek apodosis particle (τότε, ἄρα, οὖν) with correspondent → primary.
- Contrary-to-fact apodosis modals ("would have", "could have"): all primary to the Greek verb.

  source=[εἰ], target=["if"] — primary 1:1
  source=[verb], target=["would", "have", "known"] — all three primary\
"""

NEGATION_BLOCK = """\
## NEGATION

### Simple negation
οὐ/οὐκ/οὐχ/μή → "not"/"no": primary 1:1. Verb record is discontiguous (auxiliary + main verb; "not" in its own record — do not include "not" as secondary in the verb record).

  source=[οὐκ], target=["not"] — primary 1:1
  source=[ἔρχεται], target=["is", "coming"] — primary: "coming"; secondary: "is"

### Emphatic negation
οὐ μή + subjunctive: both particles primary against the emphatic expression. "will" in verb record as secondary.
  source=[οὐ, μή], target=["never"] — both primary

### Compound negation tokens (single Greek token → all English words primary)
- οὐδέ/μηδέ — "and not"/"neither"/"nor"
- οὐκέτι/μηκέτι — "no longer"/"no more"
- οὔπω/μήπω — "not yet"
- οὔτε — "neither…nor" (correlative)
  source=[οὐκέτι], target=["no", "longer"] — both primary

### Negation with negative pronouns
οὐδείς/μηδείς → "nobody"/"no one"/"nothing": primary.
With οὐ μή: double negation emphatic; English "ever"/"at all" — both οὐ and μή primary in one record.\
"""

VERBAL_ASPECT_BLOCK = """\
## VERBAL ASPECT
When a translator renders aspect explicitly (auxiliary/modal: "was doing", "tried to", "began to"), both the aspect element and the main verb are primary to the single Greek verb.\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

BLOCK_ORDER = [
    "PASSIVE",
    "IMPERSONAL",
    "PARTICIPLE",
    "INFINITIVE",
    "HINA",
    "COMPARATIVE",
    "AUTOS",
    "HOTI",
    "CONDITIONAL",
    "NEGATION",
    "VERBAL_ASPECT",
]

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

FORCED_INCLUSIONS: dict[str, set[str]] = {
    "PASSIVE": {"IMPERSONAL"},
    "HINA":    {"INFINITIVE"},
}

ENG_CONFIG = LanguagePromptConfig(
    language_code="eng",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(ENG_CONFIG)
