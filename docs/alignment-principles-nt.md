# Alignment Principles

*Working document — subject to revision and enhancement.*

---

## 1. Purpose and Scope

A **textual alignment** maps the word tokens of a Bible translation to the word tokens of the source text from which it was translated. Alignments in this project are always in the direction **translation → source**:

- **Source texts** (the alignment target): Greek New Testament (SBLGNT) and Hebrew Old Testament (Westminster Leningrad Codex as represented in the MACULA Hebrew syntactic annotation from Clear-Bible/Biblica)
- **Target translations**: any language, with a particular focus on minority languages

The goal is to provide linguistically faithful, maximally useful alignment data — not merely a mechanical mapping of tokens.

---

## 2. Core Principles

### 2.1 Generous Alignments

Alignments are intentionally **generous** rather than strictly literal. When a translation word exists *because of* a grammatical feature of the source (e.g., a preposition implied by a noun's case, a helping verb required by the target language's tense system), that word is included in the alignment record rather than left unaligned.

**Example (preposition from case):** In English "of the word" translating Greek λόγου (genitive noun), the preposition "of" exists because of the Greek case — it has no corresponding Greek word. A strict alignment would leave "of" unaligned; a generous alignment includes it in the same record as "word" → λόγου, with a secondary role (see §3).

**Example (preposition + article, no Greek article):** If the Greek is λόγου *without* the article τοῦ, but the translation reads "of the word," then *both* "of" and "the" are secondary tokens aligned to λόγου — "of" because of the genitive case, and "the" because it is a grammatically natural English rendering of a definite noun even when no separate Greek article token is present (see §6, Case 3).

**Limits of generous alignment:** Generous alignment means finding reasons to include a token — lexical, grammatical, or contextual. It does not mean forcing every token into some record. If no evident reason exists for a token's presence (it is not implied by grammar, not a lexical equivalent, and not contextually motivated), it is acceptable — and preferable — to mark it NEQ (if the absence of correspondence is certain) or leave it unrecorded (if undetermined). See §3.5.

**Surface form differences:** Morphological differences between source and target tokens — tense, voice, number, aspect — do not prevent alignment. A Greek historical present rendered as a past tense in English (see §9.1.2) is a valid alignment despite the tense difference. The question is whether there is lexical and semantic correspondence, not whether the surface forms match.

### 2.2 Alignment Direction

Alignments express the relationship **translation → source**. The source text is always Greek (NT) or Hebrew (OT). There is no reverse alignment direction in this data model.

### 2.3 Both OT and NT

All alignment principles apply across both testaments. Hebrew-specific rules (construct chains, definiteness, word-part identifiers) will require their own treatment, to be developed as a separate annex to this document.

---

## 3. Link Types: Primary and Secondary

Every token participating in an alignment record is classified as either **primary** or **secondary**.

### 3.1 Primary Links

A **primary** link connects a translation token to a source token with a direct lexical or semantic correspondence — the token is "there" because of what the source word *means*.

### 3.2 Secondary Links

A **secondary** link connects a translation token to a source token where the translation token exists *because of the grammar* of the source, not because of the source word's lexical content. Common secondary tokens include:

- Prepositions implied by a Greek or Hebrew noun's grammatical case
- English helping verbs required to render a Greek verbal form ("has been," "will have," "is being")
- English pronouns supplied from a Greek verb's person/number ending ("they" from a 3pl verb form)
- English articles ("the" or "a") when no separate article token exists in the source (see §6)
- Supplied subjects (pronoun or reinstated proper name) when no explicit source subject token is present — subject implied by the finite verb's person/number and discourse context (see §9.2.1, §9.2.2)
- Conjunctions and particles that do not have a direct lexical equivalent (rules TBD, §10)

### 3.3 Default Assumption

**All tokens in a record are assumed primary unless explicitly listed as secondary.** Secondary tokens are listed in the record's `meta.secondary` object (see §5.2). This minimizes overhead: only exceptions need to be marked.

**Every record must have at least one primary token on each side.** A valid alignment record requires a minimum of one primary source token and one primary target token. A record consisting entirely of secondary tokens on either side is not valid — if there is no primary correspondence, there is no alignment.

### 3.4 Practical Test for Primary vs Secondary

When determining whether a target token is primary or secondary, ask:

> **"What Greek (or Hebrew) word, in this context, is the reason this English word exists?"**

If a specific source token directly explains the English word's presence — lexically or semantically — that source token carries a **primary** link for that target token. If the English word exists because of grammar (case, person/number, verbal aspect, tense system) rather than a specific source word's meaning, it is **secondary**.

Multiple target tokens may each be primary to the same source token, and multiple source tokens may each carry primary links in the same record — the test is applied per token, not per record.

**Prefer explicit over implied alignment.** When a target token could either be aligned to an explicit source token *or* treated as grammatically implied (secondary), choose the explicit alignment. For example: φιλαδελφία → "brotherly love" — both "brotherly" and "love" are primary, each corresponding to a semantic component of the compound. If rendered "love of a brother or sister" — "love," "brother," and "sister" are primary; "of," "a," and "or" are secondary. Grammatical/implied alignment is a fallback only when no explicit token is available.

### 3.5 Alignment States

Every token in the source and target has one of three alignment states:

1. **Aligned** — the token participates in a record with a genuine correspondence (primary or secondary) to one or more tokens on the other side.

2. **NEQ (Non-Equivalent)** — the aligner has positively determined that the token has no correspondent on the other side. This is recorded by listing the token ID in the group's `meta.nonEquivalent` object (see §5.2.4). NEQ is a positive assertion of known non-equivalence.

3. **Unknown (not recorded)** — the alignment state has not been determined. The token simply does not appear in any record.

**NEQ is not the same as unknown.** A token left out of all records could mean "not yet aligned" or "genuinely uncertain." A NEQ record means "we have determined there is no correspondent." This distinction makes alignment data far more useful to downstream consumers.

Tokens that should be marked NEQ include: source tokens definitively untranslated (e.g. an untranslated conjunction), target tokens definitively supplied by the translator with no source correspondence (e.g. a dummy "it," a supplied copula, an apodotic "then"). See §5.2.4 and §9 for specific cases.

### 3.6 Multiple Primaries

A single record may have multiple primary tokens on either or both sides:

- **Multiple primary target tokens, single source:** "most excellent" → κράτιστε (Luke 1:3) — both English words are primary; neither is a grammatical helper
- **Multiple primary source tokens, single target:** a single translation word rendering two closely bound Greek words
- **Multiple secondary with single primary:** "that have been fulfilled" → πεπληροφορημένων (Luke 1:1) — "fulfilled" is primary; "that," "have," and "been" are secondary helpers

---

## 4. Discontiguous Tokens

The tokens in an alignment record need not be adjacent in the text. The Scripture Burrito alignment spec explicitly supports non-contiguous reference units.

**Example:** "of \[the\] word" → λόγου, where "the" in the middle belongs to a *different* alignment record (aligning with the Greek article). The record for λόγου contains "of" and "word" as non-adjacent target token IDs, with "of" marked secondary.

When representing discontiguous tokens, serialize token IDs in document order.

---

## 5. Data Format

### 5.1 Base Format

Alignments use the [Scripture Burrito alignment specification](https://github.com/bible-technology/alignment-spec/blob/main/spec.md) (currently v0.4) as the base format. The top-level structure is:

```json
{
  "format": "alignment",
  "version": "0.4",
  "groups": [ ... ]
}
```

Each group contains:

```json
{
  "type": "translation",
  "meta": { "creator": "...", "conformsTo": "0.4" },
  "documents": [
    { "scheme": "BCVWP", "docid": "SBLGNT" },
    { "scheme": "BCVWP", "docid": "<edition>" }
  ],
  "roles": ["source", "target"],
  "records": [ ... ]
}
```

Each record:

```json
{
  "source": ["<source_token_id>", ...],
  "target": ["<target_token_id>", ...],
  "meta": { ... }
}
```

### 5.2 Extensions to the Base Format

The SB spec defines `meta` as explicitly open and extensible. All extensions are additive and placed in `meta` at the record level; they do not break spec conformance.

#### 5.2.1 Secondary tokens

```json
"meta": {
  "secondary": {
    "source": ["<source_token_id>"],
    "target": ["<target_token_id>", "<target_token_id>"]
  }
}
```

- `meta.secondary.source`: list of source token IDs in this record that are secondary
- `meta.secondary.target`: list of target token IDs in this record that are secondary
- Absence of `meta.secondary` (or either subkey) means all tokens on that side are primary

#### 5.2.2 Idioms

```json
"meta": {
  "is_idiom": true
}
```

- `meta.is_idiom`: marks the record as an idiomatic phrase-to-phrase alignment
- All tokens in an idiom record are implicitly primary at the phrase level
- `meta.secondary` is not applicable on idiom records

#### 5.2.3 Record metadata (existing, carried forward)

```json
"meta": {
  "id": "400040030001.1",
  "origin": "manual",
  "status": "created"
}
```

#### 5.2.4 Non-Equivalent tokens (NEQ)

NEQ token IDs are stored in the group's `meta` object (which the SB spec leaves explicitly open), keeping all `records` entries as genuine correspondences and maintaining spec compliance.

```json
{
  "type": "translation",
  "meta": {
    "creator": "text-align",
    "conformsTo": "0.4",
    "nonEquivalent": {
      "source": ["<source_token_id>", "..."],
      "target": ["<target_token_id>", "..."]
    }
  },
  "documents": [ ... ],
  "roles": ["source", "target"],
  "records": [ /* genuine correspondences only */ ]
}
```

- `meta.nonEquivalent.source`: source token IDs definitively untranslated (e.g. ὅτι recitative, an untranslated conjunction)
- `meta.nonEquivalent.target`: target token IDs definitively supplied with no source correspondent (e.g. a dummy "it," a supplied copula, an apodotic "then")
- BCVWP token IDs encode book/chapter/verse, so no per-verse scoping is needed within the lists
- Either subkey may be absent if there are no NEQ tokens on that side
- NEQ is distinct from leaving a token out of all records (unknown state). See §3.5.

### 5.3 Token ID Scheme

Token IDs use the BCVWP scheme: an 11–12 character string encoding book, chapter, verse, word, and (for Hebrew) word-part. Example: `410040030011` = Mark 4:3, word 1.

---

## 6. Article Alignment Guidelines

### 6.1 Greek Definite Article (ὁ/ἡ/τό and declined forms)

**Baseline — all Greek tokens present (e.g., ἐκ τοῦ λόγου → "of the word"):**
When a preposition, article, and noun are all present in the Greek, each English word maps individually to its Greek counterpart as a **primary** link — typically three separate one-to-one records: ἐκ → "of", τοῦ → "the", λόγου → "word". Nothing is secondary; every English word has a direct Greek correspondent. The cases below address situations where one or more Greek tokens are *absent*.

**Case 1 — English "the" is present in the translation:**
Align "the" directly with the corresponding Greek article token. Both the article token and the "the" token are **primary**.

**Case 2 — Greek article is present but English "the" is absent:**
The Greek article is **secondary** to its noun. Include the article token in the noun's alignment record as a secondary source token.

*Exceptions — the Greek article receives its own alignment record with a **primary** link when it is rendered as:*
- An English **pronoun** (substantival use of the article)
- An English **proper name or place name**

**Case 3 — English "the" is present, no Greek article token:**
When a Greek noun is definite by context but carries no separate article token, and the translation supplies "the," the English "the" is **secondary** to the noun. Include it in the noun's alignment record as a secondary target token. If a case-driven preposition is also present (e.g., "of the word" → λόγου), both the preposition and "the" are secondary tokens in the same record.

**Case 4 — English "a" is present, no Greek article:**
Greek has no indefinite article. English "a" is grammatically supplied. "a" is **secondary** to the noun it modifies; include it in the noun's alignment record as a secondary target token.

### 6.2 Examples

All Greek tokens present (ἐκ τοῦ λόγου → "of the word") — three separate primary records:
```json
{ "source": ["grkEkId"],    "target": ["engOfId"]   }
{ "source": ["grkTouId"],   "target": ["engTheId"]  }
{ "source": ["grkLogouId"], "target": ["engWordId"] }
```

Greek article present, "the" present in English:
```json
{ "source": ["grkArticleId"], "target": ["engTheId"] }
```

Greek article present, no "the" in English (article secondary to noun):
```json
{
  "source": ["grkArticleId", "grkNounId"],
  "target": ["engNounId"],
  "meta": { "secondary": { "source": ["grkArticleId"] } }
}
```

English "the" present, no Greek article ("the" secondary to noun):
```json
{
  "source": ["grkNounId"],
  "target": ["engTheId", "engNounId"],
  "meta": { "secondary": { "target": ["engTheId"] } }
}
```

English "of the word" → λόγου (no article; both "of" and "the" secondary):
```json
{
  "source": ["grkNounId"],
  "target": ["engOfId", "engTheId", "engNounId"],
  "meta": { "secondary": { "target": ["engOfId", "engTheId"] } }
}
```

English "a" present, no Greek article ("a" secondary to noun):
```json
{
  "source": ["grkNounId"],
  "target": ["engAId", "engNounId"],
  "meta": { "secondary": { "target": ["engAId"] } }
}
```

### 6.3 Substantival Article Constructions

The Greek article can nominalize adjectives, infinitives, and prepositional phrases. Each construction follows the general article guidelines with the additions below.

**Article + adjective** (ὁ ἀγαθός → "the good one" / "the good man"):
- Article → "the" — **primary**
- Adjective → "good one" / "good man" — the supplied nominal ("one," "man") is **secondary** to the adjective; the adjective carries the lexical content

**Articular infinitive** (τὸ πιστεύειν):

When rendered as a single word or compact phrase without an explicit article ("believing," "faith"): τό is **secondary** to the infinitive — same as Case 3 in §6.1.

When rendered with explicit nominalization ("the act of believing"): two records reflecting the nominalizing and verbal roles separately.
- τό → "the act": "the" **primary**, "act" **secondary** (τό nominalizes the infinitive; "act" is the English nominalizer it supplies)
- πιστεύειν → "of believing": "believing" **primary**, "of" **secondary** (grammatical connector, same pattern as case-driven prepositions)

**Article + prepositional phrase** (τὸ ἐν σοί → "what is in you"):
Individual token mappings are available, so align them rather than treating the construction as an idiom.
- τό → "what" — **primary**
- ἐν → "in" — **primary**
- σοί → "you" — **primary**
- Supplied copula ("is") → **NEQ** (no source token; not implied by any single Greek word — see §9.1.5)

---

## 7. Idioms

An **idiom** is a multi-token expression in the source (or target, or both) whose meaning is not compositional — the phrase as a whole corresponds to the phrase as a whole, but the individual tokens do not map to each other in any reliable way.

Idiom records:
- May have any number of source and target tokens
- All tokens are implicitly **primary** at the phrase level
- Are marked with `meta.is_idiom: true`
- Do **not** use `meta.secondary`

**Examples:**

- Matt 1:18 — ἐν γαστρὶ ἔχουσα → "pregnant" / "with child." Literally "in womb having" — the individual tokens (preposition, noun, participle) do not map to "pregnant" in any meaningful way. The phrase as a whole corresponds to the English expression as a whole.

- μὴ γένοιτο → "May it never be!" / "God forbid!" / "By no means!" — a fixed Pauline expression. The individual tokens (negation particle + optative of γίνομαι) do not map reliably to any specific English words. The phrase as a whole maps to the English expression as a whole.

**Prefer smaller alignment units.** `meta.is_idiom` is a last resort — use it only when word-level mapping genuinely breaks down and would be misleading, not merely when mappings are counterintuitive or involve unexpected polarity or form shifts. Where individual token mappings are workable, even if surprising, prefer them over a larger phrasal idiom record.

**Function words are never idioms.** A source unit consisting entirely of conjunctions, particles, or prepositions (e.g. καὶ ἐγένετο) is never an idiom record. These elements have individual token-level correspondences or NEQ determinations; they must be aligned (or marked NEQ) individually. If no word-level mapping is workable, the correct outcome is NEQ — not `meta.is_idiom: true`.

**Frequency varies by translation type.** More literal translations tend to preserve word-level correspondence, so idiom records will be rare. More dynamic or paraphrase translations restructure content more heavily, and genuine idiom records will be correspondingly more frequent. In both cases `meta.is_idiom` remains a last resort — the threshold does not change, only how often that threshold is reached.

---

## 8. Mounce Reverse Interlinear Reference Cases

The following cases are drawn from the *Mounce Reverse Interlinear* (IRU) alignment layout guidelines and serve as concrete reference points for the alignment data model. In the IRU, alignment is communicated via typographic conventions (arrows, brackets, italics); below each is translated into data model terms.

> **Note:** Further specifications from Mounce or other sources regarding the Greek definite article, conjunctions, and particles are forthcoming and will supplement this section.

### 8.1 Multiple English Words → Single Greek Word (N:1)

One alignment record, multiple target tokens, single source token. The primary token is the one carrying the core lexical content; all others are secondary.

| Situation | Example | Secondary token(s) |
|---|---|---|
| Infinitive requires "to" | "to live" → μένειν | "to" |
| Compound lexical meaning | "atoning sacrifice" → ἱλασμός | none — both primary |
| Helping verbs for Greek tense | "is made complete" → τετελείωται | "is," "made" |
| Subject pronoun from verb ending | "they went out" → ἐξῆλθαν | "they" |
| "this/there is/was" expressions | "There was" → ἐγένετο | "There" |
| Case-driven preposition | "of God" → θεοῦ (genitive) | "of" |
| Case-driven preposition | "of the word" → λόγου | "of" |

### 8.2 Single English Word → Multiple Greek Words (1:N)

One alignment record, multiple source tokens, single target token. Common when a Greek article + noun together are rendered by a single English word or phrase.

| Situation | Example | Notes |
|---|---|---|
| Article + noun → English noun | "sins" → ⌈τὰς ἁμαρτίας⌉ | Article secondary in source |
| Prepositional phrase → English word | "pregnant" → ⌈ἐν γαστρί⌉ | Idiom or phrase-level primary |

### 8.3 Discontiguous English Words → Single Greek Word

One alignment record, non-adjacent target token IDs, single source token. Target IDs listed in document order.

| Situation | Example |
|---|---|
| Interrupted phrase | "Do \[not\] love" → ἀγαπᾶτε, where "not" belongs to a separate record |
| Separated helpers | "of \[the\] word" → λόγου, where "the" is in a separate article record |

### 8.4 Supplied Words with No Greek Equivalent

English translations regularly supply words not present in the Greek. These follow the generous alignment principle — include them in the nearest appropriate record as secondary tokens. When a supplied word cannot be linked to any source token (even as secondary), it is **NEQ**.

| Supplied word type | Treatment |
|---|---|
| Personal pronoun from verb ending | Secondary target token linked to the verb |
| Specific noun supplied from context ("Jesus replied") | **NEQ** — noun derives from discourse context, not a token |
| Generic noun ("person," "one") supplied from verb | Secondary target token linked to the verb |
| Helping verbs (is, can, will, have, do, may) | Secondary target tokens linked to the main verb |
| Case-implied prepositions (of, to, for, on) | Secondary target tokens linked to the noun |
| Dummy subject "it" (impersonal verbs — see §9.1.4) | **NEQ** |
| Supplied copula with no Greek εἶναι (see §9.1.5) | **NEQ** |

### 8.5 Greek Words with No English Equivalent

Greek sometimes includes words (especially indirect objects, articles, particles) that English omits. These appear as secondary source tokens in the nearest noun/verb record — or, when no corresponding record exists and the omission is definitive, as a **NEQ** source-side record (see §5.2.4).

### 8.6 Untranslatable / Idiomatic Constructions

When there is no reliable word-level correspondence between source and target tokens (Greek idioms, restructured syntax), use an idiom record (`meta.is_idiom: true`). Do not attempt word-level mapping within the record.

---

## 9. Grammatical Construction Cases

The following guidelines address specific Greek grammatical constructions that commonly require careful alignment decisions.

### 9.1 Finite Verb Constructions

#### 9.1.1 Passive Voice Constructions

Greek passive verbs are rendered in English with a "be" auxiliary + past participle. The "be" auxiliary is **secondary** to the participle (main verbal element), following the same pattern as other compound verbal renderings (§8.1).

**Simple passive:**
- ἐγράφη → "was written" — "written" primary, "was" secondary
- γέγραπται → "has been written" — "written" primary, "has been" secondary; or "it is written" — "written" primary, "it" and "is" both secondary ("it" is the implied subject of the passive, treated as secondary like other supplied pronouns — contrast the impersonal "it" of §9.1.4 which is NEQ)

**Passive with explicit agent** (ὑπό + genitive): ὑπό → "by" — primary 1:1. Agent noun → English agent — primary. Passive verb → English passive construction as above.

Example — Mark 1:9, ἐβαπτίσθη ὑπὸ Ἰωάννου → "was baptized by John":

| Source | Target | Note |
|---|---|---|
| ἐβαπτίσθη | "was baptized" | "baptized" primary; "was" secondary |
| ὑπό | "by" | primary 1:1 |
| Ἰωάννου | "John" | primary |

**Voice conversion** (passive → active or vice versa): translators sometimes convert voice for naturalness. The alignment is still valid — surface form differences including voice do not prevent alignment (§2.1).

**Divine passive (theological passive):** Greek uses the passive to imply God as agent without stating it explicitly. When a translation makes the divine agent explicit by supplying "God" or converting to active:
- Supplied "God" with no Greek token → **NEQ** (§8.4 — context-supplied proper noun)
- The passive verb aligns normally to its English correspondent

Example — Matt 5:4, αὐτοὶ παρακληθήσονται:
- Literal: "they will be comforted" — παρακληθήσονται → "will be comforted" ("comforted" primary, "will be" secondary)
- Dynamic: "God will comfort them" — παρακληθήσονται → "will comfort" ("will" secondary, "comfort" primary); "God" → **NEQ**

#### 9.1.2 Historical Present

Greek uses the present tense to narrate past events for vividness. English translations typically render it as a simple past. The tense difference does not affect alignment — the link is valid and primary.

This follows directly from the surface-form principle (§2.1): morphological differences between source and target do not prevent alignment. No additional alignment guidelines are required for the historical present beyond those already in place.

#### 9.1.3 Verbal Aspect — Iterative, Conative, and Ingressive Renderings

Greek verbal aspect is encoded morphologically, not by a separate token. When translators render the aspect explicitly in English through auxiliaries or modal expressions, the aspect-expressing element and the main verbal element are both **primary** to the single Greek verb — the Greek token carries the combined meaning; English distributes it across words. This is the reverse of the adverb + verb → single Greek verb case (§9.4.2).

**Iterative / habitual imperfect** — repeated or habitual action:
- ἔλεγεν → "he would say" — "would" and "say" both primary
- ἔλεγεν → "he kept saying" — "kept" and "saying" both primary
- ἔλεγεν → "he used to say" — "used" and "say" both primary; "to" secondary

**Conative imperfect** — attempted but uncompleted action. When rendered with "tried to": "tried" and the main verb are both **primary**; "to" secondary.

Example — Mark 15:23 (NASB), ἐδίδουν αὐτῷ ἐσμυρνισμένον οἶνον → "they tried to give Him wine mixed with myrrh":

| Source | Target | Note |
|---|---|---|
| ἐδίδουν | "tried to give" | "tried" and "give" primary; "to" secondary |
| αὐτῷ | "Him" | primary; "to" secondary per dative case |
| ἐσμυρνισμένον οἶνον | "wine mixed with myrrh" | "wine" and "myrrh" primary; "mixed with" secondary |

**Ingressive aorist** — the onset or beginning of an action. When the translation makes the ingressive force explicit with "began to": "began" and the main verb are both **primary**; "to" secondary.

This differs from explicit ἄρχομαι + infinitive, where ἄρχομαι is its own source token that aligns to "began" / "started" directly, and the infinitive aligns separately.

#### 9.1.4 Impersonal Verbs

Impersonal verbs (δεῖ, ἔξεστιν, δοκεῖ, etc.) take no expressed subject in Greek. English renderings often supply "it" as a dummy subject and a copula.

- Impersonal verb → English equivalent ("must," "is necessary," "is lawful," "seems") — **primary**
- English "it" → **NEQ** (no Greek token)
- English copula ("is") → **NEQ** per §9.1.5
- Complementary infinitive → per §8.4

Example — δεῖ αὐτὸν ἐλθεῖν → "it is necessary for him to come" / "he must come":
- δεῖ → "is necessary" or "must" — **primary**
- "it" → **NEQ**
- αὐτόν → "him" / "he" — **primary**
- ἐλθεῖν → "come" — **primary**; "to" **secondary** per §8.4

#### 9.1.5 Ellipsis of εἶναι (Supplied Copula)

Greek frequently omits the copula in nominal sentences — predicate nouns and predicate adjectives often appear with no εἶναι/εἰμί form. English requires an explicit copula. The general guideline:

**Supplied copula** ("is," "are," "was," "were," "am") with no corresponding Greek token → **NEQ**. The copula is required by English grammar but is not implied by any single Greek word; it reflects the predicative structure of the sentence as a whole.

- ὁ θεὸς ἀγάπη (1 John 4:8) → "God is love": "is" → **NEQ**
- τὸ ἐν σοί (cf. §6.3) → "what is in you": "is" → **NEQ**

**When εἶναι is explicitly present**, ellipsis does not apply — handle per the relevant construction (periphrastic §9.2.1, articular infinitive §6.3, modal e.g. δεῖ εἶναι → "must be" as two separate primary records).

**Future and other inflected forms** (ἔσται → "will be"): not ellipsis — ἔσται → "will be" with "will" secondary and "be" primary.

### 9.2 Participial Constructions

#### 9.2.1 Circumstantial Participles

A circumstantial participle modifies the main verb by expressing time, manner, means, cause, condition, or concession. It has no explicit subject token — the subject is shared with or implied from the main clause.

**Subordinating conjunction or connective "and"** added to express the circumstantial relationship → **secondary** to the participle.

- ἀπελθὼν εἶπεν → "After he went away, he said": "after" secondary to ἀπελθών; "he" secondary to εἶπεν
- ἀπελθὼν εἶπεν → "he went away and said": "and" secondary to ἀπελθών; "he" secondary to εἶπεν

**Supplied subject** (pronoun or reinstated proper name) → **secondary** to the finite/main verb, based on that verb's person/number and the contextually active referent. The subject is implied by the finite verb, not by the participle.

- If an explicit article is present on the participle, see §9.2.3 (Substantive Participles).

Example — Luke 3:11, ἀποκριθεὶς δὲ ἔλεγεν αὐτοῖς → "And he answered and said to them":

| Source | Target | Note |
|---|---|---|
| δέ | "And" | primary |
| ἀποκριθείς | "answered and" | "and" secondary |
| ἔλεγεν | "he … said" | "he" secondary — from verb's person/number |
| αὐτοῖς | "to them" | "to" secondary |

Alternative rendering "Answering, he said to them" (δέ untranslated): δέ → **NEQ**; ἀποκριθείς → "Answering" (primary); ἔλεγεν → "he said" ("he" secondary); αὐτοῖς → "to them" ("to" secondary).

**Redundant/pleonastic participle** (εἶπεν λέγων → "he said"): both the participle and the finite verb are **primary** source tokens in a single record; supplied pronoun is **secondary**.

```json
{
  "source": ["eipenId", "legonId"],
  "target": ["heId", "saidId"],
  "meta": { "secondary": { "target": ["heId"] } }
}
```

**Periphrastic construction** (εἶναι form + participle → compound English tense): two separate primary records.
- The εἶναι form → English auxiliary ("was," "had been," "is being") — **primary**
- The participle → English main verbal element ("going," "written," "saying") — **primary**

#### 9.2.2 Genitive Absolute

A genitive absolute is a participial phrase with its own subject in the genitive case, syntactically independent from the main clause. The subject is an **explicit** genitive noun or pronoun — a real source token.

**Genitive subject** → English subject of the subordinate clause: **primary** (explicit token, not grammatically implied).

**Genitive participle** → English verbal element: **primary**. Subordinating conjunction ("while," "when," "after") and helping verbs → **secondary**, same as circumstantial participles.

**If the genitive subject is untranslated**: implied subject falls back to **secondary** alignment with the nearest finite verb.

Example — ταῦτα αὐτοῦ λαλοῦντος → "while he was saying these things":

| Source | Target | Note |
|---|---|---|
| αὐτοῦ | "he" | primary — explicit genitive subject |
| λαλοῦντος | "was saying" | "was" and "while" secondary |
| ταῦτα | "these things" | primary |

#### 9.2.3 Substantive Participles

A substantive participle functions as a noun. Alignment depends on whether a definite article is present.

**Articular substantive participle** (ὁ πιστεύων → "he who believes"):
- Article → English relativizer ("who," "the one," "those who") — **primary**
- Participle → English verbal element ("believes") — **primary**
- English head pronoun ("he," "those") → **secondary** to the finite verb of the clause (grammatically implied subject)

**Anarthrous substantive participle** (πιστεύων → "the one who believes" / "whoever believes"):
- No article token available; single record
- Core verbal element ("believes") → **primary** to the participle
- All English nominalizing elements ("the," "one," "who," "whoever") → **secondary** to the participle (fallback — no explicit token available)
- If the English rendering is a single lexicalized noun ("believers"), that noun is **primary** with no secondary tokens needed

### 9.3 Infinitival Constructions

#### 9.3.1 Infinitives

"to" before an infinitive is secondary to the infinitive verb in most constructions (§8.1, §8.4). The cases below address constructions where additional alignment decisions arise.

**Complementary infinitive** (after δεῖ, θέλω, δύναμαι, etc.): covered in §9.1.4. The infinitive is primary; "to" is secondary.

**Purpose infinitive — bare Greek infinitive of purpose → English "to" + infinitive:** the infinitive verb is primary; "to" is secondary (no ἵνα token present to claim it). "In order to" similarly: "in order" and "to" are both secondary to the infinitive.

**Purpose clause — ἵνα rendered as bare "to" + infinitive:** when ἵνα is rendered as a bare "to" before an infinitive (see §9.3.2), "to" is **primary** to ἵνα — not secondary to the infinitive. The practical test: this "to" exists because of ἵνα's purpose force, not merely as an infinitive marker.

**Accusative + infinitive indirect discourse:** Greek uses an accusative noun/pronoun + infinitive to express indirect discourse after verbs of speaking, knowing, and thinking. English renders this as a finite "that" clause.
- Accusative subject → English subject of the subordinate clause — **primary**
- Infinitive → English finite verb in the subordinate clause — **primary** (voice/tense adjustment per §2.1)
- Supplied "that" → **secondary** to the infinitive (no Greek word corresponds to it; it is the English complementizer for the indirect discourse structure)

Example — Mark 8:27, τίνα με λέγουσιν οἱ ἄνθρωποι εἶναι → "Who do people say I am?":

| Source | Target | Note |
|---|---|---|
| τίνα | "Who" | primary |
| λέγουσιν | "say" | primary |
| οἱ ἄνθρωποι | "people" | primary |
| με | "I" | primary — accusative subject rendered as nominative in English |
| εἶναι | "am" | primary — infinitive rendered as finite verb in English question structure |

#### 9.3.2 ἵνα and Purpose/Result Clauses

ἵνα + subjunctive is the primary Greek marker of purpose and result. The alignment follows what the translator did with it.

**ἵνα → "that":** primary 1:1.

**ἵνα → "so that":** "so" and "that" together are both **primary** to ἵνα — both words exist because of ἵνα.

**ἵνα → "in order that" / "in order to" + infinitive:** all words of the English purpose phrase are **primary** to ἵνα. When rendered "in order to" + infinitive, "to" belongs with ἵνα (primary), not with the infinitive verb as secondary — the practical test: this "to" exists because of ἵνα's purpose force.

**ἵνα → bare "to" + infinitive:** "to" is **primary** to ἵνα; the subjunctive verb → English infinitive verb, primary.

Example — Luke 4:3, εἰπὲ τῷ λίθῳ τούτῳ ἵνα γένηται ἄρτος → "tell this stone to become bread":

| Source | Target | Note |
|---|---|---|
| εἰπέ | "tell" | primary |
| τῷ λίθῳ | "stone" | "stone" primary; τῷ secondary per §6.1 Case 2 |
| τούτῳ | "this" | primary |
| ἵνα | "to" | primary — purpose marker |
| γένηται | "become" | primary |
| ἄρτος | "bread" | primary |

**ἵνα with no corresponding English purpose marker** (purpose expressed through clause structure or word order): ἵνα → **NEQ**.

**ὥστε** (result clauses) follows the same pattern: ὥστε → "so that," "with the result that," "that," or bare "to" + infinitive. Apply the same principles as ἵνα above.

### 9.4 Adjectives and Adverbs

#### 9.4.1 Comparative and Superlative Forms

Comparatives and superlatives follow directly from existing principles; examples are included here for clarity.

**Synthetic comparative** (Greek comparative suffix → English "-er" or suppletive form): primary 1:1.
- μείζων → "greater"; κρείσσων → "better"; πλείων → "more"

**Analytic comparative** (μᾶλλον + adjective → "more [adj]"): two separate primary records.
- μᾶλλον → "more" — **primary**
- adjective → English adjective — **primary**

**Superlative** (Greek superlative form → English "-est" or "first/last/least"): primary 1:1.
- πρῶτος → "first"; ἔσχατος → "last"; ἐλάχιστος → "least"

**Elative superlative** (superlative form used as intensive → "very [adj]" / "most [adj]"): single record; both the intensifier and the adjective are **primary** to the superlative form — the superlative morphology licenses both English words.
- ἁγιώτατος → "most holy": "most" and "holy" both **primary**

**English "more"/"most" with no Greek comparative token**: **NEQ** — this should rarely arise in a well-formed translation.

#### 9.4.2 Adverbs and Compound Verbs

**Explicit Greek adverb → English adverb:** primary 1:1. Syntactic position may differ between source and target without affecting alignment.

- εὐθύς / εὐθέως → "immediately," "at once" — primary 1:1
- ταχέως → "quickly" — primary 1:1

**Greek verb + adverb → single English verb (lexical capture):** when the translator renders a Greek verb + adverb combination with a single English verb capturing the combined meaning (e.g., ταχέως + motion verb → "hurried"), both the Greek verb and the Greek adverb are **primary** source tokens in a single record against the English verb. The English word exists because of both.

```json
{ "source": ["verbId", "adverbId"], "target": ["engVerbId"] }
```

**Compound Greek verb → English phrasal verb:** Greek compound verbs with a prepositional prefix frequently correspond to English phrasal verbs (verb + adverbial particle). Both English elements are **primary** to the single Greek token. When the English uses a single lexicalized verb instead, that verb is primary 1:1.

- ἐξέρχομαι → "come out" / "go out" — "come"/"go" and "out" both primary; or "exit" — single primary
- εἰσέρχομαι → "go in" / "come in" — both primary; or "enter" — single primary
- καταβαίνω → "come down" — both primary; or "descend" — single primary

**Compound verb with redundant explicit preposition:** Greek frequently reinforces a compound verb's prepositional prefix with an explicit same-root prepositional phrase (εἰσέρχομαι εἰς, ἐξέρχομαι ἐκ, ἀναβαίνω εἰς, etc.). The explicit preposition and the prefix encode the same directional semantics; the English must distribute against both source tokens.

**Principle:** the explicit preposition token has first claim on whatever English preposition or particle corresponds to it (§3.4 — prefer explicit over implied). The compound verb aligns to the remaining English verbal elements.

**John 16:28** — ἐξῆλθον ἐκ τοῦ πατρός — two translation strategies:

NASB/KJV "came forth from the Father":

| Source | Target | Note |
|---|---|---|
| ἐξῆλθον | "came forth" | both primary — verb root + directional particle |
| ἐκ | "from" | primary 1:1 |
| τοῦ | "the" | per §6.1 Case 1 |
| πατρός | "Father" | primary |

NIV/ESV "came from the Father":

| Source | Target | Note |
|---|---|---|
| ἐξῆλθον | "came" | primary — prefix absorbed; ἐκ has already claimed "from" |
| ἐκ | "from" | primary 1:1 |
| τοῦ | "the" | per §6.1 Case 1 |
| πατρός | "Father" | primary |

The explicit ἐκ claims "from" in both renderings. What changes is whether the ἐξ- prefix finds an English correspondent ("forth") or is absorbed into the verb.

**Mark 1:26** — ἐξῆλθεν ἐξ αὐτοῦ — all major translations: "came out of him"

| Source | Target | Note |
|---|---|---|
| ἐξῆλθεν | "came out" | both primary — verb root + directional particle |
| ἐξ | "of" | primary 1:1 — ἐξ expresses separation/source; "of" in "out of" carries that relationship |
| αὐτοῦ | "him" | primary |

Here the clean distribution is universal: "out" belongs to the compound verb, "of" to the explicit preposition.

**When no English particle is available** (translation uses a single lexical verb such as "entered" or "descended"), the explicit preposition has no English correspondent to claim and is **secondary** to the compound verb.

### 9.5 Pronouns

#### 9.5.1 αὐτός — Pronoun, Intensive, and "Same"

αὐτός has three alignment-relevant uses, all handled by the practical test (§3.4).

**Third-person pronoun** ("he," "she," "him," "her," "it," "them"): primary 1:1.

**Intensive** ("himself," "herself," "themselves," "the very"): αὐτός → English intensifier — **primary**. The noun it intensifies gets its own separate primary record.
- αὐτὸς ὁ Ἰησοῦς → "Jesus himself": αὐτός → "himself" (primary); Ἰησοῦς → "Jesus" (primary); ὁ secondary per §6.1 Case 2

**"Same"** (αὐτὸς λόγος → "the same word"): αὐτός → "same" — **primary**; noun → its English equivalent in a separate primary record.

### 9.6 Prepositions

#### 9.6.1 Prepositional Phrases

**Explicit Greek preposition** (ἐν, εἰς, ἐκ, πρός, etc.) → English preposition: **primary** 1:1 record. Standard prepositional phrases (ἐν τῇ ὁδῷ → "in the road") yield three separate records — preposition, article, and noun each get their own record. The preposition is not grouped with its object.

**Case-driven English preposition** (no Greek preposition token — genitive "of," dative "to/for"): **secondary** to the noun. See also §6 and §8.4.

**Multi-word English compound preposition** rendering a single Greek preposition (ἀντί → "in place of," κατά → "in accordance with"): single record; principal preposition word **primary**, grammatical filler words **secondary**.

**Greek prepositional phrase → single English adverb or preposition** (ἐν ταχεῖ → "quickly," ἐν μέσῳ → "among"): not an idiom. Single record; the content noun is **primary**, the Greek preposition is a **secondary** source token.

```json
{
  "source": ["enId", "tacheiId"],
  "target": ["quicklyId"],
  "meta": { "secondary": { "source": ["enId"] } }
}
```

**"to" before an infinitive** → **secondary** to the infinitive. See §8.4.

### 9.7 Conjunctions, Particles, and Discourse Markers

#### 9.7.1 Conjunctions and Particles

Conjunctions (καί, δέ, γάρ, οὖν, ἀλλά, etc.) and particles (μέν, γε, οὖν, ἄρα, etc.) are handled pragmatically. Align content words first; conjunctions and particles are residual — assessed after the main lexical correspondences are settled.

**Tier 1 — obvious direct associations.** When a Greek conjunction or particle has a clear English correspondent in context, encode it directly as a primary 1:1 link. Do not overthink evident associations:

| Greek | Typical English rendering |
|---|---|
| καί | "and," "also," "even" |
| δέ | "but," "and," "now" |
| γάρ | "for" (explanatory) |
| οὖν | "therefore," "so," "then" |
| ἀλλά | "but," "rather" |

**Tier 2 — non-obvious cases.** When the clause-to-clause transition does not map cleanly — particularly in dynamic translations — assess the leftover tokens (not yet in any record) on both sides after content words are settled. Then determine whether a justifiable link exists or whether the item should be marked NEQ. Both outcomes are valid and require the same quality of judgment.

**The alignment threshold.** There is an intuitive threshold between "justifiable" and "not justifiable" that cannot be reduced to a formula. The guiding question is: *does this link reflect a genuine correspondence, or would it mislead more than it helps?* Neither aligning nor not aligning is a default — both are deliberate decisions.

**Asyndeton cases:**
- Greek asyndeton + translator-supplied English conjunction → English conjunction → **NEQ** (no source token)
- Greek conjunction + English asyndeton → Greek conjunction → **NEQ**

**Competing claims.** When a target word could plausibly align to either a conjunction/particle *or* a content word, the content word has priority. Conjunctions and particles are generally the *less likely* alignment option when there are competing choices. For example, a clause beginning with "After" where the Greek has a temporal circumstantial participle and δέ: "After" belongs with the participle (§9.2.1); δέ → **NEQ**.

**Stacked conjunctions** (e.g. ἀλλὰ μενοῦνγε καί, Phil 3:8 — sometimes parsed as ἀλλά + μέν + οὖν + γε + καί): apply the overall guiding principles to whatever the translation provides and distribute against leftover bits where justifiable. `meta.is_idiom` is available as a last resort when the combination is genuinely non-compositional, but the pragmatic approach applies first.

**NEQ is valid.** For conjunctions and particles especially, a NEQ determination is a legitimate and often correct outcome. Forcing an alignment where none is clearly justified produces misleading data.

#### 9.7.2 Negation and Emphatic Negation

**Simple negation** (οὐ, οὐκ, οὐχ, μή) → "not," "no": **primary** 1:1 record.

**Discontiguous verb alignment with intervening negation:** when a negation particle is present, its English correspondent ("not") belongs in the negation record — not as a secondary token in the verb record. Because English places "not" between the auxiliary and the main verb, the verb record is typically **discontiguous**: the auxiliary and main verb are non-adjacent target token IDs (listed in document order), with the negation record interleaved between them. This is expected and correct.

Example — John 4:2, Ἰησοῦς αὐτὸς οὐκ ἐβάπτιζεν → "Jesus himself was not baptizing":

| Source | Target | Note |
|---|---|---|
| Ἰησοῦς | "Jesus" | primary |
| αὐτός | "himself" | primary |
| οὐκ | "not" | primary 1:1 |
| ἐβάπτιζεν | "was … baptizing" | "baptizing" primary; "was" secondary — discontiguous target ("not" intervenes) |

**Emphatic negation** (οὐ μή + subjunctive → "will never," "certainly not," "by no means"): both particles are **primary** source tokens in a single record against the English emphatic expression. English auxiliaries ("will") are **secondary** to the main verb, not part of the negation record.

**Compound negation tokens** — some Greek negation forms are single tokens encoding negation together with another element. All English words in the rendered phrase are **primary** to that single token:

| Greek token | Typical rendering | Note |
|---|---|---|
| οὐδέ / μηδέ | "and not," "neither," "nor" | All words primary |
| οὐκέτι / μηκέτι | "no longer," "no more" | All words primary |
| οὔπω / μήπω | "not yet" | All words primary |
| οὔτε | "neither … nor" (correlative) | Align to "neither" or "nor" as applicable |

**Double negative with οὐδείς/μηδείς** (e.g. οὐδείς … οὐ μή → "nobody will ever"): accept the counterintuitive link. Greek double negation is emphatic, not canceling; the translation absorbs the extra negation into English "ever." The polarity shift is real but the mapping is clean — alignment documents what the translation did, not semantic equivalence.

- οὐδείς → "nobody" / "no one" — **primary**
- οὐ + μή → "ever" — both **primary** in a single record
- "will" → **secondary** to the main verb

This follows the general guideline of preferring smaller alignment units (§7): the individual token mappings are workable even though they are counterintuitive, so an idiom record is not warranted.

#### 9.7.3 ὅτι — Causal, Content Clause, and Recitative

ὅτι has three uses with distinct alignment outcomes.

**Causal** ("because," "for"): primary 1:1 — ὅτι → "because" / "for."

**Content clause / indirect discourse** ("that" — "he said that…"): primary 1:1 — ὅτι → "that."

**Recitative** (introduces direct speech): the translation renders it with quotation marks, a colon, or a dash — no corresponding word token. ὅτι → **NEQ**.

The alignment decision follows what the translator did: if "that" is present, align to it; if only punctuation introduces the quotation, ὅτι → **NEQ**.

> **Note:** Some alignment schemas permit aligning a source token to target punctuation. This project does not. Punctuation is not a valid alignment target; ὅτι recitative is NEQ when the translation uses only punctuation to introduce the quotation.

#### 9.7.4 Conditional Sentences

Conditional sentences in Greek follow a protasis ("if" clause) + apodosis ("then" clause) structure. Four classical types are distinguished by mood and tense; for alignment purposes the distinctions matter less than the token-level correspondences.

**Condition marker** εἰ / ἐάν → "if": **primary** 1:1.

**Translator-supplied "then"** in the apodosis: Greek frequently omits an explicit apodotic marker. When the translation supplies "then" (or "so") with no corresponding Greek token, it is **NEQ**.

Everything else in a conditional sentence follows existing guidelines: supplied pronouns, helping verbs, conjunctions, and particles are handled per §9.2.1, §9.7.1, and §8.4.

> For a detailed analysis of conditional structures in the Greek NT, including clause typing and annotation, see the [Clear-Bible nt-conditionals](https://github.com/Clear-Bible/nt-conditionals) repository, particularly the `/docs` folder.

### 9.8 Discourse-Level

#### 9.8.1 Discourse Restructuring and Manual Alignment Strategy

**Discourse restructuring** — Greek frequently strings clauses participially or with καί where English uses subordination, punctuation, or paragraph breaks, and vice versa. Syntactic restructuring between source and target does not change the alignment task. Tokens still align to their correspondents via the practical test (§3.4) regardless of how sentence structure differs. The restructuring is the translator's work; the aligner's job is to find token-level correspondences despite it.

- Do not mark tokens NEQ merely because the syntax was restructured — the correspondence may still be present
- Do not force artificial alignments to compensate for restructuring — if no genuine correspondence exists, mark it NEQ
- Conjunctions and particles added or dropped as part of restructuring follow §9.7.1

**Manual alignment strategy for complex verses** — when manually aligning a complicated verse, start from the beginning and work forward token by token. If you reach a point where the alignment is unclear or ambiguous, move to the end of the verse and work backwards. This bidirectional approach frequently clarifies the sticky or ambiguous spots in the middle and makes alignment decisions more evident.

---

## 10. Pending Specifications

The following areas require further specification before alignment work on them can proceed consistently:

- **Hebrew-specific rules** — construct chains, definiteness via prefix ה, word-part identifiers (BCVWP part field), pronominal suffixes

---

## 11. Workflow Overview

Alignments are produced through a two-stage process:

### Stage 1 — Automated Alignment

Initial alignments are generated by one or more automated methods:

- **Diff-based migration** (`diff-migrate`): given an existing aligned translation and a similar/related unaligned text, use text-diff to migrate alignments across identical or near-identical token sequences
- **Similarity-based migration** (`sim-migrate`): use multilingual sentence embeddings (LaBSE or SONAR-200) to match tokens across translations, enabling cross-language migration
- **Entity alignment** (`acai-align`): use ACAI person/place/entity data to align named entities across source and translation

Stage 1 produces initial 1:1 or simple N:N records. Secondary classification and idiom flagging are not expected at this stage.

### Stage 2 — Linguistically-Informed Refinement

Automated alignments are refined through linguistically-informed prompting (LLM-assisted) to:

- Resolve primary/secondary relationships
- Identify and flag idiomatic constructions
- Handle discontiguous token cases
- Apply the article, conjunction, and particle guidelines (§6, §9.7.1)
- Expand 1:1 links to appropriate N:N links where the grammar requires it
