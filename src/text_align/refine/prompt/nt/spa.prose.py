"""Prose reference copy of the Latin American Spanish NT prompt config — NOT imported.

Original Latin American Spanish target-language prompt config for refine-alignment.

Targets central and south American Spanish (not Castilian/continental).

Key differences from Portuguese (por.py):
  BASE_BLOCK
    TOKEN ROLES     — same pro-drop rule; notes vos alongside tú for regional
                      translations; ustedes (not vosotros) for 2nd person plural.
    ARTICLES        — Branch A: contracted forms limited to del (de+el) and
                      al (a+el) only — simpler than Portuguese.
                    — Branch B: proper-name rule is the default (LA Spanish
                      Bible translations generally omit the article before
                      proper names, unlike Brazilian Portuguese).
  PASSIVE_BLOCK     — reflexive passive with Spanish examples.
  INFINITIVE_BLOCK  — no personal infinitive (Spanish lacks it); para rule kept.
  HINA_BLOCK        — para que + subjunctive with Spanish examples.

Blocks unchanged from English: IMPERSONAL, PARTICIPLE, COMPARATIVE, AUTOS, HOTI,
CONDITIONAL, NEGATION, VERBAL_ASPECT.
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

Alignments map translation → source. Each record associates one or more target tokens
with one or more source tokens. The direction matters: you are asking what Greek word(s)
are behind each translation word, not the reverse.

## ALIGNMENT PHILOSOPHY

Alignments are generous. When a translation word exists because of Greek grammar — a
preposition implied by a noun's case, a pronoun implied by a verb's person and number,
an article implied by context — it belongs in an alignment record. The goal is to
account for as many tokens as the Greek justifies, not to restrict alignment to strict
lexical equivalents.

## TOKEN ROLES

Every token in a record is either primary or secondary. For each Spanish word, ask:

**Why does this word exist in the translation?**

- **It has a direct lexical or strong semantic connection to the Greek token** → it is
  **primary** in that token's record. A record may have multiple primary target tokens
  when the Greek token's meaning distributes across several Spanish words — this is
  expected, not exceptional.
- **It exists because of grammar implied by the Greek token** (morphological
  person/number, case, aspect, mood, definiteness) with no separate Greek word of its
  own, and carries no independent lexical content → it is **secondary** in the same
  record.
- **It translates a different Greek token** → it belongs in a **separate record** for
  that token, not here.

One or more Spanish words may all be primary to a single Greek token. The key
distinction: primary words exist because of the Greek token's **lexical and semantic
content**; secondary words exist only because of **grammatical features encoded in its
morphology** (person, number, case, aspect, voice) with no separate Greek word.

If a word could be primary to a different Greek token in the verse, give it its own
record instead.

Common secondary cases:

- **Supplied subject pronoun** — Spanish is a pro-drop language. Subject pronouns are
  regularly absent because person and number are encoded in the verb ending. When the
  translation has no explicit subject pronoun, none is expected — the verb form alone
  is primary to the Greek verb. Do not supply a secondary token that is not in the text.
  When a subject pronoun IS present and has no corresponding Greek pronoun, it is
  secondary (supplied for stylistic emphasis or clarity). When it corresponds to an
  explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.), it is primary to that pronoun.
  Example (no pronoun — most common): ἦλθεν → vino — "vino" primary; no secondary token
  Example (supplied for clarity, no Greek pronoun): ἦλθεν → él vino — "vino" primary;
    "él" secondary
  Note: some Latin American translations use vos (Argentina, Central America) as the
  second person singular instead of tú; the alignment rules are the same for both forms.
  For second person plural, Latin American Spanish uses ustedes (not vosotros).

- **Auxiliary verb** — ἐδίδασκεν (imperfect) → "estaba enseñando":
  "enseñando" primary; "estaba" secondary (aspect in morphology)

- **Infinitive marker** — λαβεῖν → "tomar": typically no separate marker in Spanish;
  "tomar" primary alone. When "para" introduces the infinitive, see purpose infinitive
  rules.

- **Indefinite article** — ἄνθρωπος (anarthrous) → "un hombre":
  "hombre" primary; "un" secondary (definiteness encoded in anarthrous form)

- **Case-implied preposition** — θεοῦ → "de Dios":
  "Dios" primary; "de" secondary (genitive case of θεοῦ, no separate Greek token).
  When "de" + "el" contracts to "del", see ARTICLES below.

**Structural constraints:**

Every record must have at least one primary token on each populated side. A token cannot
be the only token on its side and also be marked secondary.

Each target token ID must appear in exactly one record per verse. Do not assign the same
target token to two records, even as secondary in one and primary in another.

## NEQ (NON-EQUIVALENT)

For each token without an obvious alignment, ask:

**Am I certain this token has no correspondent anywhere in the translation of this verse?**

- **YES, certain** → NEQ: a record with the token in one array and the other array
  empty, plus `meta.rel: "NEQ"`.
- **Uncertain / cannot determine** → leave the token **unrecorded**. Do not use NEQ
  as a fallback for difficulty or uncertainty.

Unrecorded tokens are normal — they mean the correspondence was not determined.
NEQ tokens make a positive claim that no correspondence exists. Using NEQ when you
are merely unsure corrupts the data.

NEQ records must not include meta.secondary. A token is either non-equivalent (NEQ)
or has a primary/secondary relationship with another token — never both.

**Greek articles (POS T-*) are never NEQ.** When an article has no Spanish
correspondent, it is always secondary to its head noun or name. See ARTICLES → Branch B.

**Supplied copulas:** When a copula ("es", "son", "era", "eran") appears in the
translation but no Greek εἶναι token is present in the verse, the copula →
NEQ target (Greek uses verbless clauses; the translator supplied the copula).

## SURFACE FORM DIFFERENCES

Morphological differences between source and target — tense, voice, number, aspect —
do not prevent alignment. A Greek present indicative rendered as a past tense, or an
active rendered as a passive, may still be a valid alignment. The question is whether
lexical and semantic correspondence exists, not whether the surface forms match.

## CANDIDATES

The alignment candidates provided are initial word-level suggestions from automated
tools. They contain no secondary classification, no idiom flags, and some will be
wrong. Restructure, split, merge, or discard them freely. Use them as a rough starting
point, not as a framework to preserve. Align to semantic correspondents regardless of
word order or clause position.

## ARTICLES

Greek has a definite article (ὁ/ἡ/τό); Spanish has both definite (el/la/los/las) and
indefinite (un/una/unos/unas). For every Greek article token (POS T-*), ask one question:

**Does this article have a specific Spanish word or contracted form as its direct
correspondent?**

**YES → give it a primary 1:1 record for that word (see branch A below).**
**NO  → it is secondary to its head word. Never NEQ. Never omitted. Always secondary.**

**A Greek article is NEVER NEQ.** If the translation has no definite or indefinite article, 
or no available or appropriate possessive pronoun or reinstantiation 
of a proper name, or no substantive participle rendered with "los que"/"el que",
then the article is secondary to its head word. In this case, the article does not 
get its own record; it is always secondary to the noun, adjective, participle, 
or proper name it modifies.

**Critical prohibition: a Greek article NEVER corresponds to a preposition.**
Spanish prepositions ("de", "en", "a", "por") that arise from a noun's case are
secondary to that noun — not to the article. The article is either a Spanish article
or contracted form (branch A) or secondary to its head (branch B), regardless of case.

### Branch A — article has a Spanish correspondent

- **→ "el/la/los/las":** 1:1 primary record for the article; noun/adjective/participle
  gets its own separate record.
  Example: ὁ λόγος → "el Verbo":
    source=[ὁ],     target=["el"]    — primary 1:1
    source=[λόγος], target=["Verbo"] — primary 1:1

- **→ contracted form (del or al):**
  Spanish contracts "de" + "el" → "del" and "a" + "el" → "al". These are the only two
  contractions; "de la", "en el", etc. remain as separate words. Two cases:

  *Greek article only (case-implied preposition, no separate Greek preposition token):*
  The contracted form is the article's correspondent. The "de/a" component is the
  case-implied preposition absorbed into the contraction — no separate secondary needed.
    Example: τοῦ λόγου → "del Verbo" (genitive; no separate preposition token in Greek):
      source=[τοῦ],    target=["del"]   — primary 1:1
      source=[λόγου],  target=["Verbo"] — primary 1:1

  *Greek preposition + article both present as separate tokens:*
  The contracted form covers two Greek tokens. Align it to the preposition as primary;
  the article is secondary.source in the same record.
    Example: εἰς τόν κόσμον → "al mundo":
      source=[εἰς, τόν], target=["al"]    — primary: εἰς; secondary.source: [τόν]
      source=[κόσμον],   target=["mundo"] — primary 1:1

- **→ possessive pronoun ("su/sus", "mi/mis", "nuestro/a", etc.):** 1:1 primary —
  but ONLY when no explicit Greek possessive pronoun is present. Greek uses the article
  with body parts and personal relationships where Spanish may supply a possessive.
  Example (no explicit pronoun): τοὺς ὀφθαλμούς → "sus ojos":
    source=[τούς],       target=["sus"]  — primary 1:1
    source=[ὀφθαλμούς], target=["ojos"] — primary 1:1

- **→ "los que" / "el que" (substantive participle):** When an article + participle
  forms a noun phrase and Spanish renders it with "los que", "el que", etc., the
  article → "los"/"el" (primary 1:1); "que" is secondary to the participle.
  Example: τοῖς πιστεύουσιν → "a los que creen":
    source=[τοῖς],         target=["los"]          — primary 1:1
    source=[πιστεύουσιν],  target=["que", "creen"] — primary: "creen"; secondary: "que"
    "a" → secondary to πιστεύουσιν (dative case-implied)

### Branch B — article has no Spanish correspondent → secondary to its head

Latin American Spanish Bible translations generally omit the definite article before
proper names (Jesús, Pablo, Pedro), unlike English where Greek articles before proper
names are also absent. The default rule applies: Greek articles before proper names are
secondary to the name.

Apply independently to each article in the verse. The head is always the word the
article grammatically modifies:

- **Articular noun, no Spanish article:** secondary to the noun.
  Example: τὴν χεῖρα → "mano":
    source=[τήν, χεῖρα], target=["mano"] — primary: "mano"; secondary.source: [τήN]

- **Attributive adjective:** secondary to the adjective (not the noun), applied to
  each article separately.
  Example: τὴν γῆν τὴν καλήν → "buena tierra":
    source=[τήN, γῆν],   target=["tierra"] — primary: "tierra"; secondary.source: [τήν]
    source=[τήν, καλήν], target=["buena"]  — primary: "buena"; secondary.source: [τήν]

- **Articular infinitive:** secondary to the infinitive (or absorbed into "al" — see
  contracted forms in Branch A).
  Example: ἐν τῷ σπείρειν → "al sembrar":
    source=[ἐν, τῷ], target=["al"]     — primary: ἐν; secondary.source: [τῷ]
    source=[σπείρειν], target=["sembrar"] — primary 1:1

- **Article before a proper name:** secondary to the name. Greek regularly uses the
  article with proper names (ὁ Ἰησοῦς, ὁ Παῦλος); Spanish Bible translations omit it.
  The article is never NEQ in this situation — it is always secondary to the name.
  Example: ὁ Ἰησοῦς → "Jesús":
    source=[ὁ, Ἰησοῦς], target=["Jesús"] — primary: "Jesús"; secondary.source: [ὁ]

### Anarthrous noun → Spanish has "un/una"

No Greek article token exists; include "un/una" as a secondary target in the noun's
record.
  Example: ἄνθρωπος → "un hombre":
    source=[ἄνθρωπος], target=["un", "hombre"] — primary: "hombre"; secondary.target: ["un"]

## CONJUNCTIONS AND PARTICLES

When a conjunction or particle has a clear lexical correspondent in the translation,
align it. When multiple translation words together render a single conjunction or
particle, all of those translation words are primary to it (e.g. ὥστε → "de modo que":
"de", "modo", and "que" all primary). When the translation restructures and no
correspondent exists, the conjunction or particle → NEQ. When a translation word could
plausibly align to either a conjunction/particle or a content word, the content word
has priority.

## IDIOMS

When a phrase-level correspondence has no token-level equivalent, use
meta.is_idiom: true. All tokens in the record are implicitly primary; meta.secondary
does not apply to idiom records.

**Idiom is a last resort.** Always prefer splitting a phrase into standard non-idiom
records before reaching for meta.is_idiom. If you can find a reasonable primary
correspondence for individual tokens — even if the match is loose — use standard records.
Use idiom only when no plausible token-level decomposition exists.

**Function-word records are never idioms.** When the source side of a record consists
entirely of conjunctions (POS C-*), particles (POS X-*), or prepositions — even when
aligning to multiple target tokens — do not mark it as an idiom. These function words
are semantically flexible and need not match their literal glosses to be primary
alignments. Instead, produce a standard record with the translation correspondent(s)
as primary tokens.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

When a Greek passive verb is rendered with an auxiliary + past participle ("fue enviado",
"está escrito", "ha sido cumplido"), the past participle is primary to the Greek verb.
The auxiliary ("fue", "está", "ha sido") is secondary — it exists because Greek encodes
voice morphologically rather than through a separate word.

A subject pronoun supplied in the translation but absent from the Greek is secondary —
the subject is implied by the verb's person, number, and discourse context. Because
Spanish is pro-drop, an explicit subject pronoun in a passive construction is uncommon;
when present without a separate Greek pronoun, it is secondary.

### Reflexive passive (se + verb)

Spanish also expresses passive with a reflexive marker: *se escribió* ("it was
written"), *se cumplió* ("it was fulfilled"), *se vendió* ("it was sold"). The main
verb is primary to the Greek passive verb; *se* is secondary — it exists because Greek
encodes voice morphologically. This is parallel to the auxiliary passive: voice is
conveyed morphologically in Greek and lexically in Spanish.
  Example — γέγραπται → "se escribió":
    source=[γέγραπται], target=["se", "escribió"]
      primary: "escribió";  secondary: "se"

Example — γέγραπται → "está escrito":
  source=[γέγραπται], target=["está", "escrito"]
    primary: "escrito";  secondary: "está"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

The Greek infinitive is a verbal noun. Spanish renders it with an infinitive, often
introduced by "para" (purpose) or governed by a preceding verb or noun.

### Complementary infinitive

After verbs of ability, necessity, or desire (poder, querer, and similar), the
infinitive completes the main verb's meaning. The infinitive is primary; no separate
infinitive marker exists in Spanish (unlike English "to"), so no secondary marker is
expected unless "para" is present.

Example — θέλω ἐλθεῖν → "quiero venir":
  source=[ἐλθεῖν], target=["venir"] — primary 1:1

### Purpose infinitive with "para"

When "para" + infinitive expresses purpose, "para" carries the purpose force. When a
Greek ἵνα or purpose infinitive is present, "para" is primary to that element; see
ἵνα CLAUSES. When the purpose force is already in the Greek infinitive with no separate
ἵνα, "para" is secondary to the infinitive.

Example — ἦλθεν σῴζειν → "vino para salvar":
  source=[σῴζειν], target=["para", "salvar"]
    primary: "salvar";  secondary: "para"

### Articular infinitive

When a Greek infinitive is preceded by an article (τό, τῷ, τοῦ), the article marks
the infinitive's case function. Spanish has no separate word for this article, so it
is secondary to the infinitive (or absorbed into "al" — see ARTICLES).

Example — ἐν τῷ σπείρειν αὐτόν → "al sembrar":
  source=[ἐν, τῷ], target=["al"]      — primary: ἐν; secondary.source: [τῷ]
  source=[σπείρειν], target=["sembrar"] — primary 1:1

### Indirect discourse

An infinitive in indirect discourse aligns to its translation correspondent. Supplied
conjunctions ("que") introducing the indirect statement are secondary to the governing
verb, not the infinitive.

Example — λέγει αὐτὸν εἶναι → "dice que él es":
  source=[λέγει],  target=["dice"]      — primary
  source=[αὐτόν], target=["él"]         — primary
  source=[εἶναι], target=["que", "es"]
    primary: "es" (infinitive → finite verb);  secondary: "que"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

ἵνα introduces purpose or result clauses. Spanish regularly renders purpose and result
with the subjunctive mood, using conjunctions such as "para que", "a fin de que", or
"que". How ἵνα is rendered determines how it aligns.

### ἵνα rendered as a purpose conjunction

When ἵνα is rendered as "para que", "a fin de que", or similar, the conjunction is
primary to ἵνα — it exists because of ἵνα's purpose force. The verbs and other content
words in the clause align to their Greek correspondents normally.
The subjunctive verb form in Spanish does not add a secondary token — the subjunctive
ending carries mood morphologically, just as Greek does.

### ἵνα rendered as "para" + infinitive

When ἵνα is rendered as bare "para" + infinitive, "para" is primary to ἵνα — not
secondary to the infinitive. The infinitive aligns to the Greek verb in the clause
normally.

### ἵνα with no explicit translation correspondent

When a translator absorbs ἵνα's force into the surrounding structure without a distinct
conjunction or purpose marker, ἵνα → NEQ source. Apply this only when you are
confident no translation element corresponds to ἵνα's purpose or result force.

Example — ἵνα σωθῇ → "para que sea salvo":
  source=[ἵνα], target=["para", "que"] — both primary to ἵνα

Example — ἵνα σῴζῃ → "para salvar" (infinitive rendering):
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

# register_nt_language(SPA_CONFIG)  # not active — prose reference only
