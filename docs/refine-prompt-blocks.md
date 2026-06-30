# refine-alignment — Prompt Blocks

*Design document. Each section maps to a Python string constant in `prompt.py`.*
*The base block is always included. Conditional blocks are assembled dynamically*
*based on phenomena detected in the verse batch (see `detect_phenomena()`).*

---

## Forced co-inclusions

When a phenomenon is detected, the following additional blocks are always included:

| Detected | Also include |
|---|---|
| `PASSIVE` | `IMPERSONAL` |
| `HINA` | `INFINITIVE` |

---

## Base block

```
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

Every token in a record is either primary or secondary.

**Primary:** the token carries the core lexical or semantic content of the alignment.

**Secondary:** the token exists in the translation as a consequence of Greek grammar,
not as the correspondent of a separate Greek word. Common cases: prepositions implied
by case, helping verbs, supplied pronouns (subject implied by a verb's person/number),
copulas implied by context. Secondary target tokens are listed in meta.secondary.target;
secondary source tokens in meta.secondary.source.

The practical test: ask "what Greek word is the reason this translation word exists?"
— If the answer is a specific Greek token, the translation word is primary to that token.
— If the answer is Greek grammar but no specific token, the translation word is secondary
  within the record whose primary source token governs that grammar.
— If there is no Greek correspondent at all, the token may be NEQ (see below).

## NEQ (NON-EQUIVALENT)

Some tokens have no correspondent in the other language — positively determined. These
are recorded as NEQ: a record with one populated array and one empty array,
meta.rel: "NEQ". NEQ is a positive determination, not a default. Tokens whose
correspondence is simply unknown or undetermined are left unrecorded. Use NEQ only
when you are confident no correspondence exists.

## SURFACE FORM DIFFERENCES

Morphological differences between source and target — tense, voice, number, aspect —
do not prevent alignment. A Greek present indicative rendered as a past tense, or an
active rendered as a passive, may still be a valid alignment. The question is whether
lexical and semantic correspondence exists, not whether the surface forms match.

## CANDIDATES

The alignment candidates provided are initial word-level suggestions from automated
tools. They contain no secondary classification, no idiom flags, and some will be
wrong. Restructure, split, merge, or discard them freely. Use them as a rough starting
point, not as a framework to preserve.

## SBLGNT MORPH CODES

Format: POS-TENSE_VOICE_MOOD-CASE_NUMBER_GENDER

  Tense:  P=present  A=aorist  F=future  I=imperfect  X=perfect  Y=pluperfect
  Voice:  A=active  M=middle  P=passive
  Mood:   I=indicative  S=subjunctive  M=imperative  P=participle  N=infinitive  O=optative
  Case:   N=nominative  G=genitive  D=dative  A=accusative  V=vocative
  Number: S=singular  P=plural
  Gender: M=masculine  F=feminine  N=neuter
  POS prefix: V=verb  T=article  N=noun  A=adjective  D=adverb  P=pronoun
              C=conjunction  I=interjection  X=particle

Examples:
  V-PAI-3S  = verb, present active indicative, 3rd singular
  V-APP-NSM = verb, aorist passive participle, nominative singular masculine
  V-PAN     = verb, present active infinitive
  N-NSM     = noun, nominative singular masculine
  N-GPF     = noun, genitive plural feminine
  A-NSM     = adjective, nominative singular masculine
  A-GSN-C   = adjective, genitive singular neuter, comparative
  A-NSM-S   = adjective, nominative singular masculine, superlative
  T-NSM     = article, nominative singular masculine
  P-NSM     = pronoun, nominative singular masculine
  P-GSM     = pronoun, genitive singular masculine

## ARTICLES

Greek has a definite article (ὁ/ἡ/τό); English has both definite ("the") and indefinite
("a/an"). Four cases arise:
- Articular noun → translated with article: English "the" is primary to the Greek
  article token.
- Anarthrous noun → translated with "a/an": English article is secondary to the noun
  (no Greek article token exists).
- Articular noun → translated without article: the Greek article token → NEQ source.
- Anarthrous noun → translated without article: no special action needed.

## CONJUNCTIONS AND PARTICLES

When a conjunction or particle has a clear lexical correspondent in the translation,
align it. When the translation restructures and no correspondent exists, the conjunction
or particle → NEQ. When a translation word could plausibly align to either a
conjunction/particle or a content word, the content word has priority.

## IDIOMS

When a phrase-level correspondence has no token-level equivalent, use
meta.is_idiom: true. All tokens in the record are implicitly primary; meta.secondary
does not apply to idiom records.

## VERBAL ASPECT

Greek aspect is encoded in the verb morphology, not as a separate token. When a
translator renders aspect explicitly — through an auxiliary or modal ("was doing",
"tried to", "began to") — both the aspect-expressing element and the main verb element
are primary to the single Greek verb. The Greek token carries the combined meaning;
the translation distributes it across words.

## ELLIPSIS OF εἶναι

When a copula ("is", "are", "was", "were") appears in the translation but no Greek
εἶναι token is present in the verse, the copula has no source correspondent → NEQ
target. This applies when the copula is genuinely supplied by the translator with no
implied Greek verb behind it. When εἶναι is present in the source, align normally.

## DISCOURSE RESTRUCTURING

Translations sometimes reorder clauses, shift boundaries, or change syntactic structure
relative to the Greek. Align tokens to their semantic correspondents regardless of word
order or clause position. Do not force artificial alignments to compensate for
restructuring — if no genuine correspondence exists, mark NEQ.
```

---

## Conditional blocks

### PASSIVE — detected when any verb morph has voice = `P`

```
## PASSIVE VOICE

When a Greek passive verb is rendered with an auxiliary + past participle ("was sent",
"is written", "has been fulfilled"), the past participle is primary to the Greek verb.
The auxiliary ("was", "is", "has been") is secondary — it exists because Greek encodes
voice morphologically rather than through a separate word.

A subject pronoun supplied in the translation but absent from the Greek ("it was
written", "he was sent") is also secondary — the subject is implied by the verb's
person, number, and discourse context, not by a separate Greek token.

γέγραπται → "it is written" illustrates both: "written" is primary; "is" and "it" are
both secondary. The "it" here is the implied subject of the passive — distinct from the
dummy subject "it" of impersonal verbs (see IMPERSONAL VERBS below), which has no Greek
correspondent at all and is NEQ rather than secondary.
```

---

### IMPERSONAL — detected by lemma (δεῖ, ἔξεστιν, πρέπει, συμφέρει, δοκεῖ); or forced by PASSIVE

```
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
```

---

### PARTICIPLE — detected when any verb morph has mood = `P`

```
## PARTICIPIAL CONSTRUCTIONS

Greek participles are verbal adjectives — they carry both verbal content (tense, voice,
a relationship to the main clause) and nominal or adjectival function. Translations
render them in several ways, and the alignment approach follows the function.

### Circumstantial participle

When a participle is rendered as a subordinate temporal, causal, or concessive clause
("while he was speaking", "after they had left", "because he saw"), the conjunction or
adverb introducing the clause ("while", "after", "because") is secondary to the
participle — it makes explicit the logical relationship that Greek encodes in the
participle's aspect and context. A subject pronoun supplied in the translation is
secondary if implied by the participle's case agreement; otherwise treat as you would
any supplied pronoun.

### Genitive absolute

The participle and its genitive nominal element together express a circumstantial idea.
Align each to its translation correspondent. Supplied conjunctions or adverbs
introducing the rendered clause are secondary to the participle, as above.

### Substantive participle

The article, if present in both source and translation, aligns per the article
guidelines. The participial phrase ("who believes", "that were spoken") is primary to
the Greek participle. Relative pronouns or connectors introduced in translation ("who",
"that", "which") are secondary to the participle.

### Discourse particles near a participle

When a discourse particle (δέ, καί, οὖν) appears in the Greek near a participle but
has no correspondent in the translation's rendering of the participial clause, consider
NEQ — but only when you are confident the particle genuinely has no translation
equivalent anywhere in the surrounding clause structure.
```

---

### INFINITIVE — detected when any verb morph has mood = `N`; also forced by HINA

```
## INFINITIVAL CONSTRUCTIONS

The Greek infinitive is a verbal noun. Translations typically render it with "to" +
verb, but the infinitive's function in the clause shapes how surrounding words align.

### Complementary infinitive

After verbs of ability, necessity, or desire (δύναμαι, θέλω, and similar), the
infinitive completes the main verb's meaning. The infinitive is primary to the Greek
infinitive; "to" is secondary — it is an English grammatical marker with no separate
Greek correspondent.

### Articular infinitive

When the infinitive is preceded by an article (τό + infinitive), the article governs
the infinitive's case function. The article aligns per the article guidelines; the
infinitive aligns to its translation correspondent. Prepositions governing the articular
infinitive (εἰς τό, ἐν τῷ, πρὸς τό) express purpose, time, or manner — the
preposition is primary to the Greek preposition; "to" or other English connectors are
secondary.

### Purpose and result infinitive (without ἵνα)

When an infinitive expresses purpose or result directly ("he came to save", "so as to
fulfill"), the "to" is secondary to the infinitive. If an English conjunction introduces
the infinitive phrase ("in order to", "so as to"), that conjunction is secondary to the
infinitive — it makes explicit a relationship the Greek encodes through the infinitive's
function alone.

### Indirect discourse

An infinitive in indirect discourse (after verbs of saying, believing, knowing) aligns
to its translation correspondent. Supplied conjunctions ("that") introducing the
indirect statement are secondary to the governing verb, not the infinitive.
```

---

### HINA — detected by surface text `ἵνα`; forces INFINITIVE

```
## ἵνα CLAUSES

ἵνα introduces purpose or result clauses and is one of the more translation-variable
Greek particles. How it is rendered determines how it aligns.

### ἵνα rendered as a purpose clause

When ἵνα is rendered as a purpose or result conjunction ("in order that", "so that",
"that"), the conjunction is primary to ἵνα — it exists because of ἵνα's purpose force.
The verbs and other content words in the clause align to their Greek correspondents
normally.

### ἵνα rendered as a bare "to" used with an infinitive

When ἵνα is rendered as a bare "to" used with an infinitive, that "to" is primary to
ἵνα — not secondary to the infinitive. The practical test: this "to" exists because of
ἵνα's purpose force, not merely as an English infinitive marker. The infinitive itself
aligns to the Greek verb in the ἵνα clause normally.

### ἵνα with no explicit translation correspondent

When a translator absorbs ἵνα's force into the surrounding structure without a distinct
conjunction or infinitive marker, ἵνα → NEQ source. Apply this only when you are
confident no translation element corresponds to ἵνα's purpose or result force.
```

---

### COMPARATIVE — detected when any adjective or adverb morph contains degree marker `-C` or `-S`

```
## COMPARATIVES AND SUPERLATIVES

Greek comparatives and superlatives are encoded morphologically in the adjective or
adverb (degree marker `-C` for comparative, `-S` for superlative). Translations
typically render them with degree words ("more", "most", "less", "least", "better",
"best", "greater", "greatest") or suffixes ("-er", "-est").

### Comparative

When a Greek comparative adjective or adverb is rendered with a degree word + base form
("more clearly", "greater than"), both the degree word ("more", "greater") and the base
form ("clearly") are primary to the single Greek comparative token — the Greek encodes
degree morphologically; English distributes it across words.

The standard of comparison ("than X") aligns to the Greek construction expressing it
(ἤ + noun, or genitive of comparison). "Than" is secondary to the noun or adjective
it governs in the comparison.

### Superlative

The same principle applies: degree word + base form ("most clearly", "greatest") are
both primary to the single Greek superlative token. An elative superlative (very +
adjective, "very great") follows the same pattern.
```

---

### AUTOS — detected by lemma `αὐτός`

```
## αὐτός

αὐτός has three distinct uses in Greek, and its alignment depends on which function
it is serving in the clause.

### Intensive ("himself", "herself", "itself", "themselves")

When αὐτός is used intensively, it adds emphasis to a noun or pronoun already present.
The intensive pronoun in translation ("himself", "the man himself") is primary to
αὐτός.

### Reflexive ("himself", "herself", "themselves" as object)

When αὐτός functions reflexively, the reflexive pronoun in translation is primary to
αὐτός.

### Third-person pronoun ("him", "her", "it", "them", "his", "her", "their")

When αὐτός serves as a simple third-person pronoun, the corresponding pronoun in
translation is primary to αὐτός. When the translation reinstates a proper name or
noun for clarity ("Jesus" instead of "he"), the reinstated name is primary to αὐτός
and the supplied subject pronoun, if any, is secondary.

### αὐτός with no translation correspondent

When αὐτός is not rendered explicitly in the translation — absorbed into verbal
morphology or omitted for stylistic reasons — consider NEQ source, but only when
confident it has no translation equivalent in the surrounding clause.
```

---

### HOTI — detected by surface text `ὅτι`

```
## ὅτι

ὅτι serves two distinct functions in Greek, and its alignment depends on which it
is performing.

### ὅτι as conjunction ("that", "because", "for")

When ὅτι introduces indirect discourse or a causal clause, its translation
correspondent ("that", "because", "for") is primary to ὅτι. When the translation
omits the conjunction and moves directly into the indirect statement or clause,
ὅτι → NEQ source.

### ὅτι as quotation marker (recitativum)

When ὅτι introduces direct speech (ὅτι recitativum), it functions as a quotation
marker with no translation equivalent — English uses punctuation (a colon or
quotation marks) rather than a word. In this use ὅτι → NEQ source.

### Distinguishing the two

The function is usually clear from context: ὅτι recitativum follows a verb of saying
or asking and introduces direct speech; ὅτι as conjunction introduces an indirect
statement or a causal clause. When the distinction is genuinely ambiguous, prefer the
conjunction reading and align if a correspondent exists.
```

---

### CONDITIONAL — detected by surface text `εἰ` or `ἐάν`

```
## CONDITIONAL CONSTRUCTIONS

Greek conditionals are introduced by εἰ (simple or contrary-to-fact) or ἐάν (with
subjunctive, more probable). The alignment of the conditional elements follows the
general conjunction guidelines, but several features of conditional sentences are
worth noting.

### The conditional particle

εἰ and ἐάν typically correspond to "if" in translation, but translators render
conditional force in many ways — "unless", "even if", "whether", "when", and others.
Look for the translation element that carries the conditional or hypothetical force
of the clause and align to that. When you are confident no translation element
corresponds to the conditional particle's force, NEQ source is appropriate.

### Apodosis markers

Greek sometimes introduces the apodosis (the "then" clause) with a particle (τότε,
ἄρα, οὖν) or leaves it unmarked. When the translation supplies "then" with no Greek
correspondent, "then" → NEQ target. When a Greek apodosis particle is present, align
it to its translation correspondent if one exists.

### Contrary-to-fact conditions

εἰ with indicative in past tense (contrary-to-fact) may be rendered with modal
auxiliaries ("would have", "could have") in the apodosis. Those auxiliaries are
primary to the Greek verb they render — Greek encodes counterfactuality through mood
and tense rather than separate modal words; English distributes that meaning across
words.

### Everything else

Supplied pronouns, helping verbs, conjunctions, and particles within the protasis and
apodosis follow the general guidelines for those constructions.
```
