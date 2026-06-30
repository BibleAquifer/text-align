"""Prose reference copy of the French NT prompt config — NOT imported.

Original French target-language prompt config for refine-alignment.

Key differences from English (eng.py):
  BASE_BLOCK
    TOKEN ROLES     — French is NOT pro-drop: subject pronouns are grammatically
                      required; when no Greek pronoun is present, the French subject
                      pronoun is secondary (inverse of Spanish/Portuguese).
    ARTICLES        — Branch A: contracted forms du/des/au/aux; possessive pronouns;
                      substantive participle → "ceux qui"/"celui qui".
                    — Branch B: proper-name rule (French Bible translations omit the
                      article before proper names); double-article attributive note.
                    — Anarthrous: partitive du/de la/des distinguished from
                      contracted article.
  PASSIVE_BLOCK     — adds reflexive passive (se + verb) and "on" as passive equivalent.
  INFINITIVE_BLOCK  — no separate infinitive marker; "de"/"à" governed infinitives;
                      "pour"/"afin de" for purpose; gérondif for articular infinitive.
  HINA_BLOCK        — pour que/afin que + subjunctive; pour/afin de + infinitive;
                      bare que + subjunctive.
  NEGATION_BLOCK    — full rewrite for discontinuous ne…pas structure; compound
                      negation tokens; restrictive ne…que ("only").

Blocks unchanged from English: IMPERSONAL, PARTICIPLE, COMPARATIVE, AUTOS, HOTI,
CONDITIONAL, VERBAL_ASPECT.
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

Every token in a record is either primary or secondary. For each French word, ask:

**Why does this word exist in the translation?**

- **It has a direct lexical or strong semantic connection to the Greek token** → it is
  **primary** in that token's record. A record may have multiple primary target tokens
  when the Greek token's meaning distributes across several French words — this is
  expected, not exceptional.
- **It exists because of grammar implied by the Greek token** (morphological
  person/number, case, aspect, mood, definiteness) with no separate Greek word of its
  own, and carries no independent lexical content → it is **secondary** in the same
  record.
- **It translates a different Greek token** → it belongs in a **separate record** for
  that token, not here.

One or more French words may all be primary to a single Greek token. The key
distinction: primary words exist because of the Greek token's **lexical and semantic
content**; secondary words exist only because of **grammatical features encoded in its
morphology** (person, number, case, aspect, voice) with no separate Greek word.

If a word could be primary to a different Greek token in the verse, give it its own
record instead.

Common secondary cases:

- **Supplied subject pronoun** — French is not a pro-drop language. Verb forms are
  often phonologically ambiguous (vient/viennent, mange/manges/mangent), so French
  grammatically requires the subject pronoun in nearly all finite constructions. When
  no Greek pronoun is present, the French subject pronoun is **secondary** to the Greek
  verb. When an explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.) is present, the French
  pronoun is **primary** to that pronoun.
  Example (no Greek pronoun): ἦλθεν → "il vint" — "vint" primary; "il" secondary
  Example (explicit αὐτός): αὐτὸς ἦλθεν → "lui-même vint" —
    "vint" primary to ἦλθεν; "lui-même" primary to αὐτός

- **Auxiliary verb** — δεδίδαχεν (perfect aspect) → "a enseigné":
  "enseigné" primary; "a" secondary (aspect encoded in morphology)

- **Infinitive marker** — λαβεῖν → "prendre": French has no separate infinitive marker
  (unlike English "to"); "prendre" is primary alone. When "pour" or "afin de" introduce
  a purpose infinitive, see purpose infinitive rules.

- **Indefinite article** — ἄνθρωπος (anarthrous) → "un homme":
  "homme" primary; "un" secondary (definiteness encoded in anarthrous form)

- **Case-implied preposition** — θεοῦ → "de Dieu":
  "Dieu" primary; "de" secondary (genitive case of θεοῦ, no separate Greek token).
  When "de" contracts with the article (→ "du"/"des"), see ARTICLES below.

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

**Greek articles (POS T-*) are never NEQ.** When an article has no French
correspondent, it is always secondary to its head noun or name. See ARTICLES → Branch B.

**Supplied copulas:** When a copula ("est", "sont", "était", "étaient") appears in the
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

Greek has a definite article (ὁ/ἡ/τό); French has both definite (le/la/les) and
indefinite (un/une). For every Greek article token (POS T-*), ask one question:

**Does this article have a specific French word or contracted form as its direct
correspondent?**

**YES → give it a primary 1:1 record for that word (see branch A below).**
**NO  → it is secondary to its head word. Never NEQ. Never omitted. Always secondary.**

**A Greek article is NEVER NEQ.** If the translation has no definite article,
or no available or appropriate possessive pronoun or reinstantiation
of a proper name, or no substantive participle rendered as "ceux qui"/"celui qui",
then the article is secondary to its head word. In this case, the article does not
get its own record; it is always secondary to the noun, adjective, participle,
or proper name it modifies.

**Critical prohibition: a Greek article NEVER corresponds to a preposition.**
French prepositions ("de", "en", "à", "par") that arise from a noun's case are
secondary to that noun — not to the article. The article is either a French article
or contracted form (branch A) or secondary to its head (branch B), regardless of case.

### Branch A — article has a French correspondent

- **→ "le/la/les":** 1:1 primary record for the article; noun/adjective/participle gets
  its own separate record.
  Example: ὁ λόγος → "le Verbe":
    source=[ὁ],     target=["le"]    — primary 1:1
    source=[λόγος], target=["Verbe"] — primary 1:1

- **→ contracted preposition + article (du/des/au/aux):**
  French fuses certain prepositions with the definite article: de + le → du,
  de + les → des, à + le → au, à + les → aux. Note: de + la, de + l', à + la, and
  à + l' do not contract and remain as two separate words. Two cases:

  *Greek article only (case-implied preposition, no separate Greek preposition token):*
  The contracted form is the article's correspondent. The "de/à" component is the
  case-implied preposition absorbed into the contraction — no separate secondary needed.
    Example: τοῦ λόγου → "du Verbe" (genitive; no separate preposition token in Greek):
      source=[τοῦ],   target=["du"]    — primary 1:1
      source=[λόγου], target=["Verbe"] — primary 1:1

  *Greek preposition + article both present as separate tokens:*
  The contracted form covers two Greek tokens. Align it to the preposition as primary;
  the article is secondary.source in the same record.
    Example: εἰς τὸν οὐρανόν → "au ciel":
      source=[εἰς, τόν], target=["au"]   — primary: εἰς; secondary.source: [τόν]
      source=[οὐρανόν],  target=["ciel"] — primary 1:1

  Non-contracting prepositions (dans le/la/les, sur le/la, avec le/la) remain as
  separate words; the article aligns to its French correspondent or Branch B as usual.

- **→ possessive pronoun ("son/sa/ses", "leur/leurs", "mon/ma/mes", "notre/nos", etc.):**
  1:1 primary — but ONLY when no explicit Greek possessive pronoun (αὐτοῦ, αὐτῆς,
  αὐτῶν, μου, σου, ἡμῶν, etc.) is present. Greek uses the article with body parts and
  personal relationships where French may supply a possessive.
  Example (no explicit pronoun): τοὺς ὀφθαλμούς → "ses yeux":
    source=[τούς],       target=["ses"]  — primary 1:1
    source=[ὀφθαλμούς], target=["yeux"] — primary 1:1
  Counter-example (explicit αὐτῶν present): τοὺς ὀφθαλμοὺς αὐτῶν → "leurs yeux":
    source=[αὐτῶν],             target=["leurs"] — primary 1:1 (pronoun takes "leurs")
    source=[τούς, ὀφθαλμούς],  target=["yeux"]  — primary: "yeux"; secondary.source: [τούς]

- **→ "ceux qui" / "celui qui" (substantive participle):** When an article + participle
  forms a noun phrase and French renders it with "ceux qui", "celui qui", etc., the
  article → "ceux"/"celui" (primary 1:1); "qui" is secondary to the participle. Any
  case-implied preposition is secondary to the participle.
  Example: τοῖς πιστεύουσιν → "à ceux qui croient":
    source=[τοῖς],        target=["ceux"]           — primary 1:1
    source=[πιστεύουσιν], target=["qui", "croient"]  — primary: "croient"; secondary: "qui"
    "à" → secondary to πιστεύουσιν (dative case-implied)

### Branch B — article has no French correspondent → secondary to its head

French Bible translations (LS 1910 and modern versions) do not use the definite article
before proper names. Apply independently to each article in the verse. The head is
always the word the article grammatically modifies:

- **Articular noun, no French article:** secondary to the noun.
  Example: τὴν χεῖρα → "main" (article absent in translation):
    source=[τήν, χεῖρα], target=["main"] — primary: "main"; secondary.source: [τήν]

- **Double-article attributive construction:** Greek double-article phrases
  (τὴν γῆν τὴν καλήν) use two articles; French uses one. The first article aligns to
  the single French article (Branch A); the second is secondary to the adjective.
  Example: τὴν γῆν τὴν καλήν → "la bonne terre":
    source=[τήν₁],        target=["la"]    — primary 1:1 (first article → definite article)
    source=[γῆν],         target=["terre"] — primary 1:1
    source=[τήν₂, καλήν], target=["bonne"] — primary: "bonne"; secondary.source: [τήν₂]

- **Articular infinitive:** secondary to the infinitive (or absorbed into "au"/"du"
  when à/de governs it — see contracted forms in Branch A).
  Example — τοῦ πιστεύειν → "de croire":
    source=[τοῦ, πιστεύειν], target=["de", "croire"]
      primary: "croire"; secondary.source: [τοῦ]; secondary.target: ["de"]
    ("de" is case-implied by the genitive article; no separate Greek preposition token)

- **Article before a proper name:** secondary to the name. Greek regularly uses the
  article with proper names (ὁ Ἰησοῦς, ὁ Paul); French Bible translations omit it.
  The article is never NEQ in this situation — it is always secondary to the name.
  Example: ὁ Ἰησοῦς → "Jésus":
    source=[ὁ, Ἰησοῦς], target=["Jésus"] — primary: "Jésus"; secondary.source: [ὁ]

### Anarthrous noun → French has "un/une" or a partitive article

No Greek article token exists. Two cases:

**Count noun:** include "un/une" as a secondary target in the noun's record.
  Example: ἄνθρωπος → "un homme":
    source=[ἄνθρωπος], target=["un", "homme"] — primary: "homme"; secondary.target: ["un"]

**Partitive (mass or uncountable noun):** French supplies a partitive article
  (du/de la/des) for nouns with a mass or partitive sense. This is secondary to the
  noun. Distinguish carefully from contracted articles: when a Greek article token is
  present (τοῦ, τῆς, etc.), "du/de la" aligns under Branch A; when no Greek article
  token exists, "du/de la/des" is partitive and secondary to the noun.
  Example: ἄρτον → "du pain" (anarthrous, partitive sense; no Greek article token):
    source=[ἄρτον], target=["du", "pain"] — primary: "pain"; secondary.target: ["du"]

## CONJUNCTIONS AND PARTICLES

When a conjunction or particle has a clear lexical correspondent in the translation,
align it. When multiple translation words together render a single conjunction or
particle, all of those translation words are primary to it (e.g. ὥστε → "de sorte que":
"de", "sorte", and "que" all primary). When the translation restructures and no
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
as primary tokens.

Example — καὶ ἐγένετο → "Et il arriva que":
  Wrong:  source=[καὶ, ἐγένετο], target=["Et","il","arriva","que"], meta.is_idiom: true
  Better: source=[καὶ], target=["Et"] — primary 1:1 (καὶ here marks a narrative transition)
          source=[ἐγένετο], target=["il","arriva","que"] — primary: "arriva"; secondary: "il", "que"\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

When a Greek passive verb is rendered with être + past participle ("a été envoyé",
"est écrit", "a été accompli"), the past participle is primary to the Greek verb.
The auxiliary ("a été", "est") is secondary — it exists because Greek encodes voice
morphologically rather than through a separate word.

A subject pronoun in the translation ("il est écrit", "elle a été envoyée") is secondary
— French grammatically requires the pronoun, but it exists because of the verb's person,
number, and discourse context, not a separate Greek token.

### Reflexive passive (se + verb)

French also expresses passive meaning with a reflexive marker: *se dit* ("it is said"),
*s'accomplit* ("it is fulfilled"). The main verb is primary; *se/s'* is secondary — it
exists because Greek encodes voice morphologically. Parallel to the auxiliary passive.
  Example — γέγραπται → "il s'accomplit":
    source=[γέγραπται], target=["il", "s'", "accomplit"]
      primary: "accomplit";  secondary: "il", "s'"

### Impersonal "on" as passive equivalent

French also renders Greek passives with "on" + active verb: *on lui dit* ("he was
told"), *on lui apporta* ("it was brought to him"). The main verb is primary; "on" is
secondary — it is a voice-rendering strategy with no separate Greek correspondent.
  Example — ἐρρέθη → "on dit":
    source=[ἐρρέθη], target=["on", "dit"]
      primary: "dit";  secondary: "on"

Translations differ in which passive strategy they prefer; apply the rule for whichever
construction the translator chose.

Example — γέγραπται → "il est écrit":
  source=[γέγραπται], target=["il", "est", "écrit"]
    primary: "écrit";  secondary: "est", "il"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

The Greek infinitive is a verbal noun. French renders it with an infinitive, often
governed by a preceding verb with "de" or "à", or introduced by "pour"/"afin de" for
purpose. French has no separate infinitive marker (unlike English "to").

### Complementary infinitive

After verbs of ability, necessity, or desire (pouvoir, vouloir, devoir, and similar),
the infinitive completes the main verb's meaning. The infinitive is primary; no
secondary marker is expected.

Example — θέλω ἐλθεῖν → "je veux venir":
  source=[ἐλθεῖν], target=["venir"] — primary 1:1

### Governed infinitives with "de" or "à"

Many French verbs govern their infinitive complement with "de" (cesser de, permettre de,
refuser de) or "à" (commencer à, aider à, hésiter à). These prepositions are secondary
to the infinitive — they are grammatical connectors with no separate Greek correspondent.

Example — ἤρξατο διδάσκειν → "commença à enseigner":
  source=[διδάσκειν], target=["à", "enseigner"]
    primary: "enseigner";  secondary: "à"

### Purpose infinitive with "pour" / "afin de"

When "pour" + infinitive or "afin de" + infinitive expresses purpose, the
purpose-marking word(s) are secondary to the infinitive — the purpose force is already
encoded in the Greek infinitive. If a Greek ἵνα or separate purpose particle is present,
"pour" or "afin de" is primary to that element; see ἵνα CLAUSES.

Example — ἦλθεν σῴζειν → "il vint pour sauver":
  source=[σῴζειν], target=["pour", "sauver"]
    primary: "sauver";  secondary: "pour"

### Articular infinitive

When a Greek infinitive is preceded by an article (τό, τῷ, τοῦ), the article marks
the infinitive's case function. French has no separate word for this article; it is
secondary to the infinitive (or absorbed into a contracted form — see ARTICLES).

When an articular infinitive is rendered as en + present participle (gérondif), "en"
corresponds to the governing preposition (ἐν, etc.); the article is secondary to the
participle.

Example — ἐν τῷ σπείρειν αὐτόν → "en semant":
  source=[ἐν],           target=["en"]     — primary (preposition)
  source=[τῷ, σπείρειν], target=["semant"]
    primary: "semant";  secondary.source: [τῷ]

### Indirect discourse

An infinitive in indirect discourse aligns to its translation correspondent. Supplied
conjunctions ("que") introducing the indirect statement are secondary to the governing
verb, not the infinitive.

Example — λέγει αὐτὸν εἶναι → "dit qu'il est":
  source=[λέγει],  target=["dit"]       — primary
  source=[αὐτόν], target=["il"]         — primary
  source=[εἶναι], target=["que", "est"]
    primary: "est" (infinitive → finite verb);  secondary: "que"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

ἵνα introduces purpose or result clauses. French regularly renders purpose and result
with the subjunctive mood, using conjunctions such as "pour que", "afin que", or bare
"que". How ἵνα is rendered determines how it aligns.

### ἵνα rendered as a purpose conjunction

When ἵνα is rendered as "pour que", "afin que", or similar (+ subjunctive), all words
of the conjunction are primary to ἵνα. The subjunctive ending in French carries mood
morphologically — no secondary token for the subjunctive form itself.

Example — ἵνα σωθῇ → "pour qu'il soit sauvé":
  source=[ἵνα], target=["pour", "que"] — both primary to ἵνα

### ἵνα rendered as bare "que" + subjunctive

After verbs of wanting, commanding, or permitting, ἵνα may be rendered as bare "que"
+ subjunctive. "que" is primary to ἵνα.

Example — θέλω ἵνα δῷς → "je veux que tu donnes":
  source=[ἵνα], target=["que"] — primary 1:1

### ἵνα rendered as "pour" / "afin de" + infinitive

When subjects are coreferential and ἵνα is rendered as "pour" + infinitive or "afin de"
+ infinitive, the purpose-marking word(s) are primary to ἵνα — not secondary to the
infinitive. The infinitive aligns to the Greek verb in the ἵνα clause normally.

Example — ἵνα σῴζῃ → "pour sauver" (infinitive rendering):
  source=[ἵνα],   target=["pour"]   — primary (purpose marker, not a governed infinitive)
  source=[σῴζῃ], target=["sauver"] — primary

### ἵνα with no explicit translation correspondent

When a translator absorbs ἵνα's force into the surrounding structure without a distinct
conjunction or purpose marker, ἵνα → NEQ source. Apply this only when you are
confident no translation element corresponds to ἵνα's purpose or result force.\
"""

NEGATION_BLOCK = """\
## NEGATION

### Standard French negation structure

French negation is a discontinuous two-part structure: **ne** (placed before the verb
or auxiliary) + a post-verbal negative word (**pas**, **jamais**, **plus**, **rien**,
etc.). Together they correspond to a single Greek negation particle (οὐ, οὐκ, οὐχ, μή).

**"ne"** is **primary** to the Greek negation particle — it is the etymological negator
and the direct correspondent of the Greek particle. The post-verbal word (**pas**, etc.)
is **secondary** in the same record: French grammar requires it, but it has no separate
Greek source token and carries no independent lexical content beyond marking the negation
already expressed by "ne" and the Greek particle. Never NEQ the post-verbal word.

The negated verb aligns to its French correspondent (main verb + auxiliaries) without
"ne" or "pas". The verb record is **discontiguous**: "ne" precedes the verb and "pas"
follows it, but both stay in the negation record — do not include either in the verb
record.

In compound tenses ("il ne l'a pas vu"), "ne" and "pas" are themselves discontiguous
across the auxiliary and object clitic; both remain in the negation record.

Example — οὐκ ἔρχεται → "il ne vient pas":
  source=[οὐκ],     target=["ne", "pas"]  — primary: "ne"; secondary.target: ["pas"]
  source=[ἔρχεται], target=["il", "vient"]
    primary: "vient";  secondary: "il"
    (discontiguous — "ne" and "pas" bracket "vient" but belong to the negation record)

### Emphatic negation

οὐ μή + subjunctive expresses strong emphatic negation. French renders it as
"ne…jamais", "ne…point", or similar. Here there are **two** Greek source tokens, which
justifies **two** primary French targets: both "ne" and the post-verbal word are primary.
This differs from simple negation (one source token) where the post-verbal word is
secondary.

Example — οὐ μή + subjunctive verb → "ne…jamais [verb]":
  source=[οὐ, μή],  target=["ne", "jamais"] — both particles, both words primary
  source=[verb],    target=["il", "[verb]"]
    primary: main verb;  secondary: "il"

### Compound negation tokens

Some Greek forms are single tokens encoding negation together with another element.
Because there is only one source token, align "ne" as primary and the post-verbal
word as secondary — the same pattern as simple negation:

- οὐκέτι/μηκέτι ("no longer") → "ne…plus": "ne" primary; "plus" secondary
- οὔπω/μήπω ("not yet") → "ne…pas encore": "ne" primary; "pas", "encore" secondary
- οὐδέ/μηδέ ("and not", "neither", "nor") → "ni" (primary) or "et ne…pas"
  ("ne" primary, "pas" secondary)
- οὔτε ("neither…nor", correlative) → "ni"
- οὐδείς/μηδείς ("nobody", "no one", "nothing") → "personne"/"rien"/"nul" — primary

Example — οὐκέτι → "ne…plus":
  source=[οὐκέτι], target=["ne", "plus"] — primary: "ne"; secondary.target: ["plus"]

### Negation with negative pronouns

When a clause contains both a negative pronoun (οὐδείς → "personne", "nul";
μηδείς → "rien") and a separate negation particle, French double negation is emphatic
(as in Greek), not canceling. The negative pronoun is primary to its Greek token; "ne"
before the verb is retained but "pas" is typically omitted when a strong post-verbal
negative word is already present.

### Restrictive "ne…que" (= "only")

"Ne…que" in French is a restriction marker, not a true negation. When Greek μόνον,
μόνος, or another restrictive expression → "ne…que", both "ne" and "que" are **primary**
to the Greek word for "only". Do not classify "ne" here as a negation particle — the
construction carries restrictive, not negative, force.

Example — μόνον → "ne…que":
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

# register_nt_language(FRA_CONFIG)  # not active — prose reference only
