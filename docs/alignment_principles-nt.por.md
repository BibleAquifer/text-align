# Alignment Principles — Portuguese (por)

Guidelines used by `refine-alignment` when aligning Bible translations into Portuguese
against the Greek New Testament (SBLGNT) source.

Sections marked **[por]** contain Portuguese-specific rules or examples. Unmarked
sections are shared with the English guidelines (`alignment-principles-nt.md` and
`prompt/eng.py`).

Source files: `src/text_align/refine/prompt/por.py`, `src/text_align/refine/prompt/eng.py`

---

## ALIGNMENT DIRECTION **[por]**

Alignments map translation → source. Each record associates one or more target tokens
with one or more source tokens. The direction matters: you are asking what Greek word(s)
are behind each translation word, not the reverse.

---

## ALIGNMENT PHILOSOPHY **[por]**

Alignments are generous. When a translation word exists because of Greek grammar — a
preposition implied by a noun's case, a pronoun implied by a verb's person and number,
an article implied by context — it belongs in an alignment record. The goal is to
account for as many tokens as the Greek justifies, not to restrict alignment to strict
lexical equivalents.

---

## TOKEN ROLES **[por]**

Every token in a record is either primary or secondary. For each Portuguese word, ask:

**Why does this word exist in the translation?**

- **It has a direct lexical or strong semantic connection to the Greek token** → it is
  **primary** in that token's record. A record may have multiple primary target tokens
  when the Greek token's meaning distributes across several Portuguese words — this is
  expected, not exceptional.
- **It exists because of grammar implied by the Greek token** (morphological
  person/number, case, aspect, mood, definiteness) with no separate Greek word of its
  own, and carries no independent lexical content → it is **secondary** in the same
  record.
- **It translates a different Greek token** → it belongs in a **separate record** for
  that token, not here.

One or more Portuguese words may all be primary to a single Greek token. The key
distinction: primary words exist because of the Greek token's **lexical and semantic
content**; secondary words exist only because of **grammatical features encoded in its
morphology** (person, number, case, aspect, voice) with no separate Greek word.

If a word could be primary to a different Greek token in the verse, give it its own
record instead.

Common secondary cases:

- **Supplied subject pronoun** — Portuguese is a pro-drop language. Subject pronouns
  are regularly absent because person and number are encoded in the verb ending. When
  the translation has no explicit subject pronoun, none is expected — the verb form
  alone is primary to the Greek verb. Do not supply a secondary token that is not in
  the text.
  When a subject pronoun IS present and has no corresponding Greek pronoun, it is
  secondary (supplied for stylistic emphasis or clarity). When it corresponds to an
  explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.), it is primary to that pronoun.
  Example (no pronoun — most common): ἦλθεν → veio — "veio" primary; no secondary token
  Example (supplied for clarity, no Greek pronoun): ἦλθεν → ele veio — "veio" primary;
    "ele" secondary

- **Auxiliary verb** — ἐδίδασκεν (imperfect) → "estava ensinando":
  "ensinando" primary; "estava" secondary (aspect in morphology)

- **Infinitive marker** — λαβεῖν → "tomar": typically no separate marker in Portuguese;
  "tomar" primary alone. When "para" introduces the infinitive, see purpose infinitive
  rules.

- **Indefinite article** — ἄνθρωπος (anarthrous) → "um homem":
  "homem" primary; "um" secondary (definiteness encoded in anarthrous form)

- **Case-implied preposition** — θεοῦ → "de Deus":
  "Deus" primary; "de" secondary (genitive case of θεοῦ, no separate Greek token).
  When "de" is contracted with the article (→ "do"/"da"), see ARTICLES below.

**Structural constraints:**

Every record must have at least one primary token on each populated side. A token cannot
be the only token on its side and also be marked secondary.

Each target token ID must appear in exactly one record per verse. Do not assign the same
target token to two records, even as secondary in one and primary in another.

---

## NEQ (NON-EQUIVALENT) **[por]**

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

**Greek articles (POS T-*) are never NEQ.** When an article has no Portuguese
correspondent, it is always secondary to its head noun or name. See ARTICLES → Branch B.

**Supplied copulas:** When a copula ("é", "são", "era", "eram") appears in the
translation but no Greek εἶναι token is present in the verse, the copula →
NEQ target (Greek uses verbless clauses; the translator supplied the copula).

---

## SURFACE FORM DIFFERENCES

Morphological differences between source and target — tense, voice, number, aspect —
do not prevent alignment. A Greek present indicative rendered as a past tense, or an
active rendered as a passive, may still be a valid alignment. The question is whether
lexical and semantic correspondence exists, not whether the surface forms match.

---

## CANDIDATES

The alignment candidates provided are initial word-level suggestions from automated
tools. They contain no secondary classification, no idiom flags, and some will be
wrong. Restructure, split, merge, or discard them freely. Use them as a rough starting
point, not as a framework to preserve. Align to semantic correspondents regardless of
word order or clause position.

---

## ARTICLES **[por]**

Greek has a definite article (ὁ/ἡ/τό); Portuguese has both definite (o/a/os/as) and
indefinite (um/uma/uns/umas). For every Greek article token (POS T-*), ask one question:

**Does this article have a specific Portuguese word or contracted form as its direct
correspondent?**

**YES → give it a primary 1:1 record for that word (see branch A below).**
**NO  → it is secondary to its head word. Never NEQ. Never omitted. Always secondary.**

**Critical prohibition: a Greek article NEVER corresponds to a preposition.**
Portuguese prepositions ("de", "em", "a", "por") that arise from a noun's case are
secondary to that noun — not to the article. The article is either a Portuguese article
or contracted form (branch A) or secondary to its head (branch B), regardless of case.

### Branch A — article has a Portuguese correspondent

- **→ "o/a/os/as":** 1:1 primary record for the article; noun/adjective/participle gets
  its own separate record.
  Example: ὁ λόγος → "o Verbo":
    source=[ὁ],     target=["o"]     — primary 1:1
    source=[λόγος], target=["Verbo"] — primary 1:1

- **→ contracted preposition + article (do/da/no/na/ao/à/pelo/pela, etc.):**
  Portuguese fuses certain prepositions with the article into a single token. Two cases:

  *Greek article only (case-implied preposition, no separate Greek preposition token):*
  The contracted form is the article's correspondent. The "de/em/a" component is the
  case-implied preposition absorbed into the contraction — no separate secondary needed.
    Example: τοῦ λόγου → "do Verbo" (genitive; no separate preposition token in Greek):
      source=[τοῦ],    target=["do"]    — primary 1:1
      source=[λόγου],  target=["Verbo"] — primary 1:1

  *Greek preposition + article both present as separate tokens:*
  The contracted form covers two Greek tokens. Align it to the preposition as primary;
  the article is secondary.source in the same record.
    Example: ἐν τῷ ναῷ → "no templo":
      source=[ἐν, τῷ], target=["no"]     — primary: ἐν; secondary.source: [τῷ]
      source=[ναῷ],     target=["templo"] — primary 1:1

- **→ possessive pronoun ("seu/sua/seus/suas", "meu", "nosso", etc.):** 1:1 primary —
  but ONLY when no explicit Greek possessive pronoun is present. Greek uses the article
  with body parts and personal relationships where Portuguese may supply a possessive.
  Example (no explicit pronoun): τοὺς ὀφθαλμούς → "seus olhos":
    source=[τούς],       target=["seus"] — primary 1:1
    source=[ὀφθαλμούς], target=["olhos"] — primary 1:1

- **→ "os que" / "aquele que" (substantive participle):** When an article + participle
  forms a noun phrase and Portuguese renders it with "os que", "aquele que", etc., the
  article → "os"/"aquele" (primary 1:1); "que" is secondary to the participle.
  Example: τοῖς πιστεύουσιν → "aos que creem":
    source=[τοῖς],         target=["aos"]  — primary 1:1 (contracted ao + article)
    source=[πιστεύουσιν],  target=["que", "creem"] — primary: "creem"; secondary: "que"

- **→ article before a proper name (when Portuguese retains it):** Portuguese, especially
  Brazilian Portuguese, frequently retains the definite article with proper names
  (o Jesus, o Paulo, o Pedro) — unlike English. When the translation has the article,
  align 1:1 primary. When the translation omits it, apply Branch B.
  Example (article present): ὁ Ἰησοῦς → "o Jesus":
    source=[ὁ],       target=["o"]     — primary 1:1
    source=[Ἰησοῦς], target=["Jesus"] — primary 1:1
  Example (article absent): ὁ Ἰησοῦς → "Jesus" (translation omits article):
    source=[ὁ, Ἰησοῦς], target=["Jesus"] — primary: "Jesus"; secondary.source: [ὁ]

### Branch B — article has no Portuguese correspondent → secondary to its head

Apply independently to each article in the verse. The head is always the word the
article grammatically modifies:

- **Articular noun, no Portuguese article:** secondary to the noun.
  Example: τὴν χεῖρα → "mão":
    source=[τήν, χεῖρα], target=["mão"] — primary: "mão"; secondary.source: [τήν]

- **Attributive adjective:** secondary to the adjective (not the noun), applied to
  each article separately.
  Example: τὴν γῆν τὴν καλήν → "boa terra":
    source=[τήν, γῆν],   target=["terra"] — primary: "terra"; secondary.source: [τήN]
    source=[τήν, καλήν], target=["boa"]   — primary: "boa"; secondary.source: [τήν]

- **Articular infinitive:** secondary to the infinitive.
  Example: ἐν τῷ σπείρειν → "ao semear":
    source=[ἐν, τῷ], target=["ao"] — primary: ἐν; secondary.source: [τῷ]
    (see contracted forms in Branch A — "ao" covers ἐν + τῷ)

- **Article before a proper name with no Portuguese correspondent:** secondary to the
  name. When Portuguese omits the article that Greek has, the Greek article is always
  secondary to the name — never NEQ.
  Example: ὁ Ἰησοῦς → "Jesus" (article absent in this translation):
    source=[ὁ, Ἰησοῦς], target=["Jesus"] — primary: "Jesus"; secondary.source: [ὁ]

### Anarthrous noun → Portuguese has "um/uma"

No Greek article token exists; include "um/uma" as a secondary target in the noun's
record.
  Example: ἄνθρωπος → "um homem":
    source=[ἄνθρωπος], target=["um", "homem"] — primary: "homem"; secondary.target: ["um"]

---

## CONJUNCTIONS AND PARTICLES **[por]**

When a conjunction or particle has a clear lexical correspondent in the translation,
align it. When multiple translation words together render a single conjunction or
particle, all of those translation words are primary to it (e.g. ὥστε → "de modo que":
"de", "modo", and "que" all primary). When the translation restructures and no
correspondent exists, the conjunction or particle → NEQ. When a translation word could
plausibly align to either a conjunction/particle or a content word, the content word
has priority.

---

## IDIOMS **[por]**

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

---

## PASSIVE VOICE **[por]**

When a Greek passive verb is rendered with an auxiliary + past participle ("foi enviado",
"está escrito", "foi cumprido"), the past participle is primary to the Greek verb.
The auxiliary ("foi", "está", "tem sido") is secondary — it exists because Greek encodes
voice morphologically rather than through a separate word.

A subject pronoun supplied in the translation but absent from the Greek ("foi escrito",
"ele foi enviado") is secondary — the subject is implied by the verb's person, number,
and discourse context. Because Portuguese is pro-drop, an explicit subject pronoun in a
passive is rarer and more likely to be emphatic; still classify it as secondary when no
separate Greek pronoun is present.

### Reflexive passive (se + verb) **[por]**

Portuguese also expresses passive with a reflexive marker: *se escreveu* ("it was
written"), *se vendeu* ("it was sold"), *se cumpriu* ("it was fulfilled"). The main
verb is primary to the Greek passive verb; *se* is secondary — it exists because Greek
encodes voice morphologically. This is parallel to the auxiliary passive: voice is
conveyed morphologically in Greek and lexically in Portuguese.
  Example — γέγραπται → "se escreveu":
    source=[γέγραπται], target=["se", "escreveu"]
      primary: "escreveu";  secondary: "se"

The "it" of a passive supplied subject is secondary in the auxiliary construction, not
NEQ — contrast the dummy "it" of impersonal verbs (see IMPERSONAL VERBS below), which
has no Greek correspondent at all and is NEQ. Portuguese pro-drop means this supplied
"it" often simply does not appear.

Example — γέγραπται → "está escrito":
  source=[γέγραπται], target=["está", "escrito"]
    primary: "escrito";  secondary: "está"

---

## IMPERSONAL VERBS

Some Greek verbs are used impersonally — they have no real subject, only a grammatical
placeholder. Common examples: δεῖ ("it is necessary"), ἔξεστιν ("it is
lawful/permitted"), πρέπει ("it is fitting"), συμφέρει ("it is better/profitable"),
δοκεῖ ("it seems").

When these are rendered with a dummy subject "it" in the translation, that "it" has no
Greek correspondent — there is no implied subject behind it, only a grammatical
convention of English. The dummy "it" → NEQ target.

The complementary infinitive that typically follows (δεῖ + infinitive, "it is necessary
to do") is a separate alignment: the infinitive is primary to the Greek infinitive; "to"
is secondary. The impersonal verb itself aligns to its translation equivalent in the
normal way.

Contrast with the passive supplied subject (see PASSIVE VOICE above): a passive supplied
"it" is secondary because it represents the implied grammatical subject of the verb. An
impersonal "it" is NEQ because no subject — implied or otherwise — exists in the Greek.

Example — δεῖ → "it is necessary":
  source=[δεῖ], target=["is", "necessary"] — "is" and "necessary" both primary to δεῖ
  "it" → NEQ target (no Greek correspondent; no subject is implied)

  Or rendered compactly:
  source=[δεῖ], target=["must"] — primary

---

## PARTICIPIAL CONSTRUCTIONS

Greek participles are verbal adjectives. First identify the participle's syntactic role,
then apply the rule for that role.

**What syntactic function is the participle serving?**

### Adverbial (circumstantial)

The participle modifies the main verb, expressing time, cause, concession, or manner.
The translation renders it as a subordinate clause introduced by a conjunction or adverb
("quando", "enquanto", "depois de", "porque", "embora").

The introductory conjunction/adverb is **secondary** to the participle — it makes
explicit the logical relationship Greek encodes in the participle's aspect and context.
A supplied subject pronoun is secondary if implied by the participle's case agreement.

  source=[ἀκούσας], target=["quando", "ouviu"]
    primary: "ouviu";  secondary: "quando"

### Genitive absolute

The participle and its genitive nominal element together express a circumstantial idea
external to the main clause. Align each element to its translation correspondent.
Supplied conjunctions or adverbs introducing the rendered clause are secondary to the
participle.

### Substantive

The participle functions as a noun phrase. Apply ARTICLES rules to the article if
present (→ "os"/"aquele" if Portuguese has it; secondary to participle otherwise).
Relative pronouns or connectors ("que") introduced in Portuguese are secondary to the
participle.

  source=[πιστεύων], target=["quem", "crê"]
    primary: "crê";  secondary: "quem"

### Discourse particle adjacent to a participle

When δέ, καί, οὖν or similar appears near a participle but has no correspondent in the
participle's rendering, consider NEQ — only when confident the particle has no
translation equivalent anywhere in the surrounding clause.

---

## INFINITIVAL CONSTRUCTIONS **[por]**

The Greek infinitive is a verbal noun. Portuguese renders it with an infinitive, often
introduced by "para" (purpose) or "de/a" (governed by a preceding verb or noun).

### Complementary infinitive

After verbs of ability, necessity, or desire (poder, querer, and similar), the
infinitive completes the main verb's meaning. The infinitive is primary; no separate
infinitive marker exists in Portuguese (unlike English "to"), so no secondary marker
is expected unless "para" is present.

Example — θέλω ἐλθεῖν → "quero vir":
  source=[ἐλθεῖν], target=["vir"] — primary 1:1

### Purpose infinitive with "para"

When "para" + infinitive expresses purpose, "para" is the correspondent of the purpose
relationship (not secondary to the infinitive). If a Greek ἵνα or purpose infinitive
is present, "para" is primary to that element; see ἵνα CLAUSES.

Example — ἦλθεν σῴζειν → "veio para salvar":
  source=[σῴζειν], target=["para", "salvar"]
    primary: "salvar";  secondary: "para"
  (here "para" is secondary to the infinitive — the purpose force is already in σῴζειν)

### Articular infinitive

When a Greek infinitive is preceded by an article (τό, τῷ, τοῦ), the article marks
the infinitive's case function. Portuguese has no separate word for this article, so it
is secondary to the infinitive (or absorbed into a contracted form — see ARTICLES).

Example — ἐν τῷ σπείρειν αὐτόν → "ao semear":
  source=[ἐν, τῷ], target=["ao"]     — primary: ἐν; secondary.source: [τῷ]
  source=[αὐτόν],  target=["ele"]    — primary (if pronoun is present in translation)
  source=[σπείρειν], target=["semear"] — primary 1:1

### Personal infinitive **[por]**

Portuguese has a personal infinitive — an infinitive with person/number endings
(fazermos, fazerem, etc.). These endings carry the same grammatical information as
Greek verb endings: no secondary token is expected for the person/number information
since it is encoded in the infinitive's morphology, not in a separate word.

### Indirect discourse

An infinitive in indirect discourse aligns to its translation correspondent. Supplied
conjunctions ("que") introducing the indirect statement are secondary to the governing
verb, not the infinitive.

Example — λέγει αὐτὸν εἶναι → "diz que ele é":
  source=[λέγει],  target=["diz"]       — primary
  source=[αὐτόν], target=["ele"]        — primary
  source=[εἶναι], target=["que", "é"]
    primary: "é" (infinitive → finite verb);  secondary: "que"

---

## ἵνα CLAUSES **[por]**

ἵνα introduces purpose or result clauses. Portuguese regularly renders purpose and
result with the subjunctive mood, using conjunctions such as "para que", "a fim de
que", or "que". How ἵνα is rendered determines how it aligns.

### ἵνα rendered as a purpose conjunction

When ἵνα is rendered as "para que", "a fim de que", or similar, the conjunction is
primary to ἵνα — it exists because of ἵνα's purpose force. The verbs and other content
words in the clause align to their Greek correspondents normally.
The subjunctive verb form in Portuguese does not add a secondary token — the subjunctive
ending carries mood morphologically, just as Greek does.

### ἵνα rendered as "para" + infinitive

When ἵνα is rendered as bare "para" + infinitive, "para" is primary to ἵνα — not
secondary to the infinitive. The infinitive aligns to the Greek verb in the clause
normally.

### ἵνα with no explicit translation correspondent

When a translator absorbs ἵνα's force into the surrounding structure without a distinct
conjunction or purpose marker, ἵνα → NEQ source. Apply this only when you are
confident no translation element corresponds to ἵνα's purpose or result force.

Example — ἵνα σωθῇ → "para que seja salvo":
  source=[ἵνα], target=["para", "que"] — both primary to ἵνα

Example — ἵνα σῴζῃ → "para salvar" (infinitive rendering):
  source=[ἵνα],   target=["para"]  — primary (purpose marker)
  source=[σῴζῃ], target=["salvar"] — primary

---

## COMPARATIVES AND SUPERLATIVES

Greek comparatives and superlatives are encoded morphologically in the adjective or
adverb (degree marker `-C` for comparative, `-S` for superlative). Translations
typically render them with degree words ("mais", "o mais", "menos", "melhor", "maior")
or suffixes.

### Comparative

When a Greek comparative adjective or adverb is rendered with a degree word + base form
("mais claramente", "maior do que"), both the degree word ("mais", "maior") and the base
form ("claramente") are primary to the single Greek comparative token — the Greek encodes
degree morphologically; Portuguese distributes it across words.

The standard of comparison ("do que X") aligns to the Greek construction expressing it
(ἤ + noun, or genitive of comparison). "do que" is secondary to the noun or adjective
it governs in the comparison.

### Superlative

The same principle applies: degree word + base form ("mais claramente", "o maior") are
both primary to the single Greek superlative token. An elative superlative (muito +
adjective) follows the same pattern.

Example — μείζων → "maior":
  source=[μείζων], target=["maior"] — primary 1:1

Example — ἁγιώτατος → "santíssimo" or "mui santo":
  source=[ἁγιώτατος], target=["santíssimo"] — primary 1:1
  source=[ἁγιώτατος], target=["mui", "santo"] — both primary

---

## αὐτός

First identify the grammatical function αὐτός is serving in the clause:

**What is αὐτός doing here?**

### Intensive (attributive position — adds emphasis to a noun or pronoun)

αὐτός stands beside a noun/pronoun to emphasize it ("o próprio homem", "o próprio
Jesus"). Align to the intensive pronoun; the noun it modifies gets its own record.

  source=[αὐτός],   target=["próprio"] — primary 1:1
  source=[Ἰησοῦς], target=["Jesus"]   — primary 1:1 (separate record)

### Reflexive (object refers back to the subject)

αὐτός functions as a reflexive pronoun. Align to the reflexive in translation
("a si mesmo", "a si mesma", "a eles mesmos").

  source=[αὐτόν], target=["a", "si", "mesmo"] — all primary

### Third-person pronoun (most common use)

αὐτός serves as a simple third-person pronoun. Align to the corresponding pronoun
("ele", "ela", "o/a", "lhe", "deles/delas"). When the translation substitutes
a proper name for clarity, the name is primary to αὐτός; any additionally supplied
subject pronoun is secondary.

  source=[αὐτόν], target=["o"]     — primary 1:1
  source=[αὐτοῦ], target=["Jesus"] — primary (name substituted for pronoun)

### No translation correspondent

αὐτός is absorbed into surrounding structure or stylistically omitted → NEQ source,
but only when confident no translation element corresponds to it.

---

## ὅτι

ὅτι serves two distinct functions in Greek, and its alignment depends on which it
is performing.

### ὅτι as conjunction ("que", "porque", "pois")

When ὅτι introduces indirect discourse or a causal clause, its translation
correspondent ("que", "porque", "pois") is primary to ὅτι. When the translation
omits the conjunction and moves directly into the indirect statement or clause,
ὅτι → NEQ source.

### ὅτι as quotation marker (recitativum)

When ὅτι introduces direct speech (ὅτι recitativum), it functions as a quotation
marker with no translation equivalent — Portuguese uses punctuation (a colon or
quotation marks) rather than a word. In this use ὅτι → NEQ source.

### Distinguishing the two

The function is usually clear from context: ὅτι recitativum follows a verb of saying
or asking and introduces direct speech; ὅτι as conjunction introduces an indirect
statement or a causal clause. When the distinction is genuinely ambiguous, prefer the
conjunction reading and align if a correspondent exists.

Example — ὅτι (conjunction) → "que":
  source=[ὅτι], target=["que"] — primary 1:1

Example — ὅτι (recitativum) → quotation marks only:
  source=[ὅτι] → NEQ source

---

## CONDITIONAL CONSTRUCTIONS

Greek conditionals are introduced by εἰ (simple or contrary-to-fact) or ἐάν (with
subjunctive, more probable). The alignment of the conditional elements follows the
general conjunction guidelines, but several features of conditional sentences are
worth noting.

### The conditional particle

εἰ and ἐάν typically correspond to "se" in translation, but translators render
conditional force in many ways — "a menos que", "mesmo que", "se", "quando", and others.
Look for the translation element that carries the conditional or hypothetical force
of the clause and align to that. When you are confident no translation element
corresponds to the conditional particle's force, NEQ source is appropriate.

### Apodosis markers

Greek sometimes introduces the apodosis (the "then" clause) with a particle (τότε,
ἄρα, οὖν) or leaves it unmarked. When the translation supplies "então" with no Greek
correspondent, "então" → NEQ target. When a Greek apodosis particle is present, align
it to its translation correspondent if one exists.

### Contrary-to-fact conditions

εἰ with indicative in past tense (contrary-to-fact) may be rendered with modal
constructions ("teria", "poderia ter") in the apodosis. Those auxiliaries are
primary to the Greek verb they render — Greek encodes counterfactuality through mood
and tense rather than separate modal words; Portuguese distributes that meaning across
words.

### Everything else

Supplied pronouns, helping verbs, conjunctions, and particles within the protasis and
apodosis follow the general guidelines for those constructions.

Example — εἰ → "se":
  source=[εἰ], target=["se"] — primary 1:1

Example — contrary-to-fact apodosis verb → "teria conhecido":
  source=[verb], target=["teria", "conhecido"]
    both primary — Greek encodes counterfactuality through mood and tense;
    Portuguese distributes that meaning across auxiliary + main verb

---

## NEGATION

### Simple negation

Greek negation particles (οὐ, οὐκ, οὐχ, μή and related forms) are discrete tokens
separate from the verb they negate. Look for the Portuguese "não" and align it
directly to the negation particle as a **primary** 1:1 record.

The negated verb aligns to its Portuguese correspondent — main verb and auxiliaries —
**without** including "não." Because Portuguese typically places "não" before the verb,
the verb record may be **discontiguous** when auxiliaries intervene between "não" and
the main verb. This discontiguous verb record is expected and correct.

Do not include "não" as a secondary token within the verb record. It has its own
source token and belongs in its own record.

Example — οὐκ ἔρχεται → "não está vindo":
  source=[οὐκ],      target=["não"]             — primary 1:1
  source=[ἔρχεται], target=["está", "vindo"]
    primary: "vindo";  secondary: "está"

### Emphatic negation

οὐ μή + subjunctive expresses strong emphatic negation. Translations render it as
"nunca", "de modo algum", "jamais", or similar. Both particles are **primary** in a
single record against the emphatic Portuguese expression.

Example — οὐ μή + subjunctive verb → "nunca [verb]":
  source=[οὐ, μή],  target=["nunca"]          — both particles primary
  source=[verb],    target=["[verb]"]          — primary

### Compound negation tokens

Some Greek forms are single tokens encoding negation together with another element.
All Portuguese words in the rendered phrase are **primary** to the single Greek token:

- οὐδέ / μηδέ ("nem") — single token aligns to full phrase
- οὐκέτι / μηκέτι ("não mais", "já não") — single token aligns to full phrase
- οὔπω / μήπω ("ainda não") — single token aligns to full phrase

Example — οὐκέτι → "não mais":
  source=[οὐκέτι], target=["não", "mais"] — both primary

### Negation with negative pronouns

When a clause contains both a negative pronoun (οὐδείς → "ninguém", "nada";
μηδείς → "ninguém", "nada") and emphatic negation (οὐ μή), Greek double negation
is emphatic, not canceling. Portuguese typically resolves this into a single strong
negation.

- οὐδείς / μηδείς → "ninguém" / "nada" — primary
- οὐ + μή combined force → absorbed into the negative pronoun or adverb
- Main verb auxiliaries → secondary to the verb, not part of the negation record

---

## VERBAL ASPECT

Greek aspect is encoded in the verb morphology, not as a separate token. When a
translator renders aspect explicitly — through an auxiliary or modal ("estava fazendo",
"tentou", "começou a") — both the aspect-expressing element and the main verb element
are primary to the single Greek verb. The Greek token carries the combined meaning;
the translation distributes it across words.
