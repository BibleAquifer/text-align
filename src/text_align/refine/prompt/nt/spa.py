"""Latin American Spanish target-language prompt config for refine-alignment.

Targets central and south American Spanish (not Castilian/continental).

Key differences from Portuguese (por.py):
  BASE_BLOCK    — same pro-drop rule; vos alongside tú regional note; ustedes for
                  2nd plural; only del/al contractions (not 8 Portuguese forms);
                  proper names always Branch B (LA Spanish omits article).
  PASSIVE_BLOCK — reflexive passive with Spanish examples.
  INFINITIVE_BLOCK — no personal infinitive; para rule kept.
  HINA_BLOCK    — para que + subjunctive with Spanish examples.

Prose reference preserved in spa.prose.py.
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
# Spanish-specific prompt blocks
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

- Pro-drop subject pronoun — Spanish encodes person/number in the verb ending. When no subject pronoun appears in the translation, none is expected (verb alone is primary). When a pronoun IS present without a corresponding Greek pronoun → secondary. When it corresponds to an explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.) → primary.
  Regional note: some Latin American translations use vos (Argentina, Central America) as 2nd person singular alongside tú; the rule is the same. 2nd person plural is ustedes (not vosotros).
  ἦλθεν → "vino" — "vino" primary; no secondary
  ἦλθεν → "él vino" (supplied for clarity) — "vino" primary; "él" secondary

- Auxiliary verb — ἐδίδασκεν → "estaba enseñando": "enseñando" primary; "estaba" secondary

- Indefinite article — ἄνθρωπος → "un hombre": "hombre" primary; "un" secondary

- Case-implied preposition — θεοῦ → "de Dios": "Dios" primary; "de" secondary (contracted form "del": see ARTICLES)

- Periphrastic rendering — when a single Greek token is rendered by multiple Spanish words, all words carrying lexical content are primary; purely grammatical connectors (prepositions, relativizers, determiners) are secondary to the same token. This includes any source word encoding multiple semantic components — compound verbs, compound nouns, or morphologically rich stems. Never NEQ a target word that expresses a component of the source word's meaning.
  κυριεύει → "ejerce dominio sobre": "ejerce", "dominio" primary; "sobre" secondary
  γινώσκουσιν (dative substantive participle) → "a los que conocen": "conocen" primary; "a", "los", "que" secondary
  καρποφορέω → "dar fruto": "dar", "fruto" both primary
  φιλαδελφία → "amor fraternal": "amor", "fraternal" both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — always secondary to head when no Spanish correspondent. See ARTICLES → Branch B.
Supplied copula ("es", "son", "era", "eran") with no Greek εἶναι → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES

For every Greek article (POS T-*): does it have a specific Spanish word or contracted form as its direct correspondent?
YES → Branch A (primary 1:1). NO → Branch B (secondary to head — never NEQ, never omitted).
A Greek article is NEVER NEQ and NEVER omitted — it never gets its own record; it is always secondary to the noun, adjective, participle, or proper name it modifies. A Greek article NEVER corresponds to a preposition.

### Branch A — article has a Spanish correspondent

- → "el/la/los/las": 1:1 primary; noun/adjective/participle in its own record.
  ὁ λόγος → "el Verbo":
    source=[ὁ],     target=["el"]    — primary 1:1
    source=[λόγος], target=["Verbo"] — primary 1:1

- → contracted form (del or al only — the only two Spanish contractions):
  Greek article only (case-implied preposition, no separate Greek preposition token):
  Contracted form is the article's correspondent; the "de/a" component is absorbed — no separate secondary.
    τοῦ λόγου → "del Verbo" (genitive, no separate Greek preposition):
      source=[τοῦ],   target=["del"]   — primary 1:1
      source=[λόγου], target=["Verbo"] — primary 1:1
  Greek preposition + article both present:
  Contracted form → primary to preposition; article is secondary.source.
    εἰς τόν κόσμον → "al mundo":
      source=[εἰς, τόν], target=["al"]    — primary: εἰς; secondary.source: [τόν]
      source=[κόσμον],   target=["mundo"] — primary 1:1

- → possessive pronoun ("su/sus", "mi/mis", "nuestro/a"): 1:1 primary — ONLY when no explicit Greek possessive pronoun present.
  τοὺς ὀφθαλμούς → "sus ojos" (no explicit pronoun):
    source=[τούς],       target=["sus"]  — primary 1:1
    source=[ὀφθαλμούς], target=["ojos"] — primary 1:1

- → "los que"/"el que" (substantive participle): article → "los"/"el" primary 1:1; "que" secondary to participle.
  τοῖς πιστεύουσιν → "a los que creen":
    source=[τοῖς],        target=["los"]          — primary 1:1
    source=[πιστεύουσιν], target=["que", "creen"] — primary: "creen"; secondary: "que"
    "a" → secondary to πιστεύουσιν (dative case-implied)

### Branch B — no Spanish correspondent → secondary to head

Apply to each article independently; the head is always the word it grammatically modifies.
Latin American Spanish Bible translations omit the definite article before proper names (Jesús, Pablo, Pedro). Greek articles before proper names are always secondary to the name — never NEQ.

- Articular noun, no article: source=[τήν, χεῖρα], target=["mano"] — primary: "mano"; secondary.source: [τήN]
- Attributive adjective: secondary to adjective (not noun), each article separately.
  τὴν γῆν τὴν καλήν → "buena tierra":
    source=[τήN, γῆν],   target=["tierra"] — primary: "tierra"; secondary.source: [τήN]
    source=[τήν, καλήν], target=["buena"]  — primary: "buena"; secondary.source: [τήν]
- Articular infinitive: secondary to infinitive (or absorbed into "al" — see Branch A).
  ἐν τῷ σπείρειν → "al sembrar":
    source=[ἐν, τῷ],    target=["al"]      — primary: ἐν; secondary.source: [τῷ]
    source=[σπείρειν],  target=["sembrar"] — primary 1:1
- Article before proper name: ὁ Ἰησοῦς → "Jesús":
    source=[ὁ, Ἰησοῦς], target=["Jesús"] — primary: "Jesús"; secondary.source: [ὁ]

### Anarthrous noun → "un/una"
source=[ἄνθρωπος], target=["un", "hombre"] — primary: "hombre"; secondary.target: ["un"]

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "de modo que": all three primary).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  μὴ γένοιτο — optative negation ("¡De ninguna manera!" / "¡Jamás!" / "¡En absoluto!"):
    When no token-level mapping is possible: is_idiom: true.
      source=[μή, γένοιτο], target=["De","ninguna","manera"] — is_idiom: true
    When the rendering permits, prefer granular alignment: μή → negation words; γένοιτο → verb "ser/estar".\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE
Auxiliary + past participle: past participle primary; auxiliary ("fue", "está", "ha sido") secondary.
Supplied subject pronoun absent from Greek: secondary. Pro-drop means this is uncommon in Spanish.
Passive "it": secondary — contrast impersonal dummy "it" (see IMPERSONAL VERBS), which is NEQ.

### Reflexive passive (se + verb)
Main verb primary; "se" secondary (voice is morphological in Greek, lexical in Spanish).
  γέγραπται → "se escribió":
    source=[γέγραπται], target=["se", "escribió"] — primary: "escribió"; secondary: "se"

γέγραπται → "está escrito":
  source=[γέγραπται], target=["está", "escrito"] — primary: "escrito"; secondary: "está"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Infinitive primary; no separate marker in Spanish (unlike English "to").
  θέλω ἐλθεῖν → "quiero venir": source=[ἐλθεῖν], target=["venir"] — primary 1:1

### Purpose infinitive with "para"
"para" carries purpose force → secondary to the infinitive when purpose is already in the Greek verb; primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
  ἦλθεν σῴζειν → "vino para salvar":
    source=[σῴζειν], target=["para", "salvar"] — primary: "salvar"; secondary: "para"

### Articular infinitive
Article secondary to infinitive (never NEQ); absorbed into "al" when applicable (see ARTICLES).
  ἐν τῷ σπείρειν αὐτόν → "al sembrar":
    source=[ἐν, τῷ],   target=["al"]      — primary: ἐν; secondary.source: [τῷ]
    source=[σπείρειν], target=["sembrar"] — primary 1:1

### Indirect discourse
Supplied "que" introducing indirect statement → secondary to governing verb — not to the infinitive.
  λέγει αὐτὸν εἶναι → "dice que él es":
    source=[λέγει],  target=["dice"]
    source=[αὐτόν], target=["él"]
    source=[εἶναι], target=["que", "es"] — primary: "es"; secondary: "que"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- → "para que"/"a fin de que" (purpose conjunction): conjunction primary; verbs/content words align normally. Subjunctive mood does not add a secondary token.
- → bare "para" + infinitive: "para" primary to ἵνα (not secondary to the infinitive).
- No correspondent → NEQ source (only when certain no element expresses purpose/result force).

  ἵνα σωθῇ → "para que sea salvo":
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

SPA_CONFIG = LanguagePromptConfig(
    language_code="spa",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(SPA_CONFIG)
