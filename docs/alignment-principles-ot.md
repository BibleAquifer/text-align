# Alignment Principles — Old Testament (Hebrew)

*Working document — subject to revision and enhancement.*

---

## 1. Purpose and Scope

A **textual alignment** maps the word tokens of a Bible translation to the word tokens of the source text from which it was translated. Alignments in this project are always in the direction **translation → source**:

- **Source text** (the alignment target): Hebrew Old Testament as represented in the Westminster Leningrad Codex, tokenized and annotated in the MACULA Hebrew syntactic dataset (Clear-Bible/Biblica). Aramaic sections (Daniel 2:4b–7:28; Ezra 4:8–6:18; 7:12–26; Jeremiah 10:11) use the same principles unless otherwise noted.
- **Target translations**: any language, with a particular focus on minority languages.

The goal is to provide linguistically faithful, maximally useful alignment data — not merely a mechanical mapping of tokens.

This document covers alignment principles for the Old Testament (Hebrew source). For Greek New Testament alignment, see `alignment-principles-nt.md`. The core philosophy (§§2–5) is identical across both documents; Hebrew-specific token structure and grammatical constructions begin at §6.

---

## 2. Core Principles

### 2.1 Generous Alignments

Alignments are intentionally **generous** rather than strictly literal. When a translation word exists *because of* a grammatical feature of the source — a preposition expressed through a construct relationship, an English copula required by a verbless clause, a possessive pronoun implied by a noun suffix — that word is included in the alignment record rather than left unaligned.

**Example (construct chain):** Hebrew בֵּית יְהוָה "house of the LORD" — the English preposition "of" is expressed through the construct relationship between the two nouns, not by a separate Hebrew preposition token. A generous alignment includes "of" as a secondary token in the record for בֵּית.

**Example (inseparable preposition, split token):** Hebrew לַמֶּלֶךְ "to the king" encodes preposition (לְ), article (הַ), and noun (מֶּלֶךְ) in a single word form. When MACULA provides separate word-part tokens for each morpheme, each maps individually to its English correspondent. When the entire form is one token, English "to," "the," and "king" collectively align to it (with "the" secondary; see §7).

**Limits of generous alignment:** Generous alignment means finding reasons to include a token — lexical, grammatical, or contextual. The goal is to align as clearly and generously as possible, which sometimes means leaving tokens unaligned or marking them NEQ ("Non-Equivalent"; see definition in §3.5). It does not mean forcing every token into some record. Leaving a token unrecorded (state: unknown) and marking it NEQ (state: positively no correspondent) are both legitimate, deliberate outcomes — not failures of alignment. If no evident reason exists for a token's presence, marking it NEQ or leaving it unrecorded is preferable to manufacturing a link. See §3.5.

**Surface form differences:** Morphological differences between source and target tokens — tense, voice, number, aspect, stem — do not prevent alignment. The question is whether there is lexical and semantic correspondence, not whether the surface forms match.

### 2.2 Alignment Direction

Alignments express the relationship **translation → source**. The source text is always Hebrew (OT) or Aramaic (for the Aramaic sections listed in §1). There is no reverse alignment direction in this data model.

### 2.3 Both OT and NT

All core alignment principles apply across both testaments. This document addresses Hebrew-specific constructions. For Greek-specific constructions, see `alignment-principles-nt.md`.

---

## 3. Link Types: Primary and Secondary

Every token participating in an alignment record is classified as either **primary** or **secondary**.

### 3.1 Primary Links

A **primary** link connects a translation token to a source token with a direct lexical or semantic correspondence — the token is "there" because of what the source word *means* or what morpheme *does* as an explicit lexical element.

### 3.2 Secondary Links

A **secondary** link connects a translation token to a source token where the translation token exists *because of the grammar* of the source, not because of the source word's lexical content. Common secondary tokens in Hebrew alignment include:

- English prepositions implied by a construct-chain relationship ("of," "belonging to") when no separate preposition token is present (§11.1)
- English articles ("the" or "a") when the Hebrew article is not a separate word-part token (§7)
- English copula ("is," "are," "was," "were") in Hebrew verbless clauses where no Hebrew verb token is present (§12.1)
- English subject pronouns supplied from a finite verb's person/gender/number morphology, when no explicit pronoun token is present (§12.2)
- Conjunctions and connectors added by the translator in rendering clause-level Hebrew structure (§13.1)
- English "to" before an infinitive construct when the Hebrew לְ is not a separate word-part token (§12.4)

### 3.3 Default Assumption

**All tokens in a record are assumed primary unless explicitly listed as secondary.** Secondary tokens are listed in the record's `meta.secondary` object (see §5.2). This minimizes overhead: only exceptions need to be marked.

**Every record must have at least one primary token on each side.** A valid alignment record requires a minimum of one primary source token and one primary target token. A record consisting entirely of secondary tokens on either side is not valid — if there is no primary correspondence, there is no alignment.

### 3.4 Practical Test for Primary vs Secondary

When determining whether a target token is primary or secondary, ask:

> **"What Hebrew word or word-part token, in this context, is the reason this English word exists?"**

If a specific source token directly explains the English word's presence — lexically or semantically — that source token carries a **primary** link for that target token. If the English word exists because of grammatical structure (a construct relationship, verbal person/gender/number, a verbless clause) rather than an explicit source token's meaning, it is **secondary**.

**Prefer explicit over implied alignment.** When a target token could either be aligned to an explicit source token *or* treated as grammatically implied (secondary), choose the explicit alignment. Grammatical/implied alignment is a fallback only when no explicit token is available. The availability of Hebrew word-part tokens for morphemes like inseparable prepositions, pronominal suffixes, and the article means that many elements that would be secondary in other languages can be aligned explicitly as primary in Hebrew.

Multiple target tokens may each be primary to the same source token, and multiple source tokens may each carry primary links in the same record — the test is applied per token, not per record.

### 3.5 Alignment States

Every token in the source and target has one of three alignment states:

1. **Aligned** — the token participates in a record with a genuine correspondence (primary or secondary) to one or more tokens on the other side.

2. **NEQ (Non-Equivalent)** — the aligner has positively determined that the token has no correspondent on the other side. This is recorded by listing the token ID in the group's `meta.nonEquivalent` object (see §5.2.4). NEQ is a positive assertion of known non-equivalence.

3. **Unknown (not recorded)** — the alignment state has not been determined. The token simply does not appear in any record.

**NEQ is not the same as unknown.** A token left out of all records could mean "not yet aligned" or "genuinely uncertain." A NEQ record means "we have determined there is no correspondent." This distinction makes alignment data far more useful to downstream consumers.

Tokens that should be marked NEQ include: the direct object marker אֶת when untranslated (§13.2); conjunctions and particles definitively not rendered; supplied English words definitively without a source correspondent (e.g., a supplied copula, an apodotic "then," a context-derived proper name). See §§5.2.4 and 12–13 for specific cases.

### 3.6 Multiple Primaries

A single record may have multiple primary tokens on either or both sides:

- **Multiple primary target tokens, single source:** "word of mouth" → פֶּה (lit. "mouth") — both English words may be primary to the single Hebrew token
- **Multiple primary source tokens, single target:** a single translation word rendering two closely bound Hebrew words (construct + head noun rendered as a single English word)
- **Multiple primary on both sides:** idiomatic constructions where phrase-level correspondence is real but word-level mapping distributes across multiple tokens on each side

---

## 4. Discontiguous Tokens

The tokens in an alignment record need not be adjacent in the text. The Scripture Burrito alignment spec explicitly supports non-contiguous reference units.

**Hebrew word-internal discontiguity:** MACULA Hebrew splits morphologically complex words into word-part tokens. A single Hebrew word may yield two or more BCVWP part-tokens (preposition, article, noun; or noun, pronominal suffix) that land in different alignment records. These word-part records are consecutive by BCVWP ID but their English correspondents may be separated by other tokens in the translation.

**Example:** שְׁמָרֵנוּ "he kept us" — verb word-part (P1) aligns to "kept"; suffix word-part (P2) aligns to "us." In an English clause like "the LORD has kept us safe," the "us" may not immediately follow "kept." Both records are correct; document token IDs in document order.

**Cross-verse or long-range discontiguity** may also occur in poetry and highly restructured translations. Serialize all token IDs in document order regardless of span.

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
    { "scheme": "BCVWP", "docid": "MACULA-Hebrew" },
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
  "id": "010010010011.1",
  "origin": "manual",
  "status": "created"
}
```

#### 5.2.4 Non-Equivalent tokens (NEQ)

NEQ token IDs are stored in the group's `meta` object, keeping all `records` entries as genuine correspondences:

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

- `meta.nonEquivalent.source`: source token IDs definitively untranslated (e.g., אֶת direct-object marker, an untranslated conjunction)
- `meta.nonEquivalent.target`: target token IDs definitively supplied with no source correspondent (e.g., a supplied copula, a context-derived proper name, an apodotic "then")
- BCVWP token IDs encode book/chapter/verse, so no per-verse scoping is needed within the lists
- Either subkey may be absent if there are no NEQ tokens on that side

### 5.3 Token ID Scheme

Token IDs use the BCVWP scheme. Hebrew tokens use a 12-character form:

```
BB CCC VVV WWW P
01 001 001 001 1  =  Genesis 1:1, word 1, part 1
```

- **BB**: 2-digit book number (01 = Genesis … 39 = Malachi)
- **CCC**: 3-digit chapter number, zero-padded
- **VVV**: 3-digit verse number, zero-padded
- **WWW**: 3-digit word number within the verse, zero-padded
- **P**: word-part number within the word (1, 2, 3, …); see §6

---

## 6. Hebrew Word Structure and Word-Part Tokens

### 6.1 Overview of MACULA Hebrew Tokenization

MACULA Hebrew tokenizes at the **word-part** level for morphologically complex words. Hebrew frequently attaches multiple morphemes to a single orthographic word; MACULA typically provides each morpheme as a distinct word-part token with its own BCVWP part number. Common splits:

| Element | Example word | Parts |
|---|---|---|
| Waw conjunction prefix (וְ/וַ/וּ/וּ) | וּמֶלֶךְ | P1 = וּ (conj), P2 = מֶלֶךְ (noun) |
| Inseparable preposition (בְּ/לְ/כְּ) | בְּבֵיתוֹ | P1 = בְּ (prep), P2 = בֵּית (noun), P3 = וֹ (suffix) |
| Definite article (הַ/הָ/הֶ) | הַמֶּלֶךְ | P1 = הַ (art), P2 = מֶּלֶךְ (noun) |
| Preposition + article (בַּ/לַ/כַּ) | לַמֶּלֶךְ | P1 = לְ (prep), P2 = הַ (art), P3 = מֶּלֶךְ (noun) |
| Pronominal suffix on noun | דְּבָרוֹ | P1 = דָּבָר (noun), P2 = וֹ (3ms "his") |
| Pronominal suffix on verb | שְׁמָרֵנוּ | P1 = שָׁמַר (verb), P2 = נוּ (1cp "us") |
| Pronominal suffix on preposition | אֵלָיו | P1 = אֵל (prep), P2 = יו (3ms "him") |
| Interrogative prefix (הֲ/הַ/הֶ) | הֲיֵדַעְתָּ | P1 = הֲ (interrog), P2 = יֵדַעְתָּ (verb) |

**When word-part tokens are present** (separate BCVWP IDs), each part aligns independently to its English correspondent as described in §§7–13.

**When the entire word is a single token** (no splits), all English words corresponding to morphological components of that word collectively align to the single token, with primary/secondary distinctions applied per §§7–13. The general principle: morphemes with clear lexical content (prepositions, pronominal suffixes, content nouns, verbal roots) are **primary** to the single token; the pure definiteness-marking article when folded in is **secondary**.

### 6.2 Verifying Token Boundaries

Because word-part splits are determined by the MACULA tokenization, always verify the actual token IDs present in the source data before assigning alignments. Do not assume a morphological element has its own token — confirm whether a separate BCVWP word-part ID exists for it.

---

## 7. Hebrew Definiteness and the Article

### 7.1 The Hebrew Definite Article (הַ/הָ/הֶ)

The Hebrew definite article is always a prefix attached to the following word. MACULA Hebrew typically provides it as a distinct word-part token.

**Article word-part token present:** align the article word-part token to English "the" as a **primary** 1:1 record.

```json
{ "source": ["hebArticlePartId"], "target": ["engTheId"] }
```

**Article word-part token absent (folded into single token):** English "the" is a **secondary** target token in the noun's record.

```json
{
  "source": ["hebNounId"],
  "target": ["engTheId", "engNounId"],
  "meta": { "secondary": { "target": ["engTheId"] } }
}
```

**English "the" absent, Hebrew article word-part present:** the article word-part token is a **secondary** source token in the noun's record.

```json
{
  "source": ["hebArticlePartId", "hebNounId"],
  "target": ["engNounId"],
  "meta": { "secondary": { "source": ["hebArticlePartId"] } }
}
```

*Exceptions — the article word-part token receives its own **primary** record when it is rendered as:*
- An English **pronoun** (substantival use, e.g., הַצַּדִּיק → "the righteous one" / "he who is righteous": article → "he" or "the one" — primary)
- An English **relative pronoun or relativizer** in a substantival construction (§10.3)

**English "a" / "an" (no Hebrew article):** Hebrew has no indefinite article. English "a"/"an" is **secondary** to the noun it modifies.

```json
{
  "source": ["hebNounId"],
  "target": ["aId", "engNounId"],
  "meta": { "secondary": { "target": ["aId"] } }
}
```

### 7.2 Definiteness by Construct Chain

A noun in construct state is definite when the following genitive noun is definite, even though the construct noun carries no article prefix. When the translation renders this definiteness with English "the," that "the" is **secondary** to the construct noun (there is no article token for it).

*Example:* בֵּית יְהוָה "the house of the LORD" — בֵּית is definite by construct relationship with the proper noun יְהוָה, but bears no article prefix. English "the" before "house" is secondary to the בֵּית token.

```json
{
  "source": ["beitId"],
  "target": ["theId", "houseId", "ofId"],
  "meta": { "secondary": { "target": ["theId", "ofId"] } }
}
{ "source": ["yhwhId"], "target": ["lordId"] }
```

### 7.3 Definiteness via Pronominal Suffix

A noun with a pronominal suffix is definite. The English rendering typically uses a possessive pronoun ("his house"), not "the." No secondary "the" arises. See §9 for pronominal suffix alignment.

### 7.4 Summary: Article Alignment Cases

| Situation | Treatment |
|---|---|
| Article word-part token present, English "the" present | Primary 1:1: article → "the" |
| Article word-part token present, English "the" absent | Article word-part is secondary source token in noun record |
| Article token absent, English "the" present | English "the" is secondary target token in noun record |
| Article token absent, construct definiteness supplies "the" | Same as above — "the" secondary to construct noun |
| No Hebrew article, English "a"/"an" supplied | English "a"/"an" secondary to noun |

---

## 8. Inseparable Prepositions

### 8.1 Overview

Hebrew has four inseparable (prefixed) prepositions: בְּ ("in," "at," "by," "with," "through"), לְ ("to," "for," "of," belonging to"), כְּ ("as," "like," "according to"), and מִ/מִּ ("from," "out of," "more than," "because of"). These attach as prefixes; MACULA Hebrew typically provides them as separate word-part tokens.

### 8.2 Inseparable Preposition Word-Part Token Present

When MACULA provides a distinct word-part token for the preposition, align it to the English preposition as a **primary** record.

*Example:* לַמֶּלֶךְ "to the king" — word-parts: לְ (P1), הַ (P2), מֶּלֶךְ (P3):

```json
{ "source": ["lePart1Id"],    "target": ["toId"]   }
{ "source": ["haPart2Id"],    "target": ["theId"]  }
{ "source": ["melekPart3Id"], "target": ["kingId"] }
```

### 8.3 Inseparable Preposition Folded into Single Token

When the prefixed form is a single token (no word-part split), the English preposition is **primary** to that token (the preposition is an explicit lexical morpheme of the source word, not merely a grammatically implied feature). The article, if folded in, generates a secondary English "the."

*Example:* single-token בַּמֶּלֶךְ "in the king":

```json
{
  "source": ["bammelekId"],
  "target": ["inId", "theId", "kingId"],
  "meta": { "secondary": { "target": ["theId"] } }
}
```

*Example:* single-token לְמֶלֶךְ "to a king" (no article):

```json
{
  "source": ["lemelekId"],
  "target": ["toId", "aId", "kingId"],
  "meta": { "secondary": { "target": ["aId"] } }
}
```

### 8.4 מִן Preposition

מִן "from" appears in two forms:

- **Attached prefix** מִ/מִּ: follows the same rules as §8.2–8.3.
- **Independent word** מִן: **primary** 1:1 record with the English preposition.

### 8.5 Polysemous Prepositions

Hebrew prepositions are highly polysemous. בְּ alone may render as "in," "at," "on," "by," "with," "through," "by means of," "because of," etc. The alignment pairs whichever English rendering the translator chose with the Hebrew preposition token or word-part, as a primary record. When the translation uses a multi-word English expression ("by means of," "in accordance with," "as a result of"):

- The semantically central preposition word is **primary** to the Hebrew preposition token.
- Grammatical filler words of the English expression are **secondary**.

*Example:* בְּ → "by means of": "by" primary; "means" and "of" secondary.

---

## 9. Pronominal Suffixes

### 9.1 Pronominal Suffixes on Nouns (Possession)

Hebrew pronominal suffixes on nouns express possession. MACULA typically provides them as a distinct word-part token.

**Suffix word-part token present:** primary 1:1, suffix → English possessive pronoun.

*Example:* דְּבָרוֹ "his word" — P1 = דָּבָר, P2 = וֹ (3ms):

```json
{ "source": ["davarPart1Id"], "target": ["wordId"] }
{ "source": ["sufPart2Id"],   "target": ["hisId"]  }
```

**Suffix token absent (single token):** the English possessive pronoun is **primary** to the containing noun token (the suffix is an explicit morpheme, not a purely grammatical implication).

```json
{ "source": ["dvarohId"], "target": ["hisId", "wordId"] }
```

### 9.2 Pronominal Suffixes on Verbs (Direct Object)

Hebrew pronominal suffixes on verbs express the direct object. MACULA typically provides them as a distinct word-part token.

*Example:* שְׁמָרֵנוּ "he kept us" — P1 = שָׁמַר, P2 = נוּ (1cp object):

```json
{ "source": ["shamarPart1Id"], "target": ["keptId"] }
{ "source": ["nuPart2Id"],     "target": ["usId"]   }
```

**Suffix token absent:** the English object pronoun is **primary** to the verb token.

### 9.3 Pronominal Suffixes on Prepositions

Hebrew prepositions with pronominal suffixes form fused prepositional + pronominal words (אֵלָיו "to him," עָלֵינוּ "upon us," מֵהֶם "from them"). MACULA typically provides the preposition and suffix as separate word-part tokens.

*Example:* אֵלָיו "to him" — P1 = אֵל (prep), P2 = יו (3ms):

```json
{ "source": ["elPart1Id"],  "target": ["toId"]  }
{ "source": ["sufPart2Id"], "target": ["himId"] }
```

**Single token (no split):** both "to" and "him" are **primary** to the single token (each corresponds to an explicit morpheme).

```json
{ "source": ["elayvId"], "target": ["toId", "himId"] }
```

### 9.4 First- and Second-Person Pronominal Suffixes

The same rules apply regardless of person. When a suffix is present:
- Noun suffix → possessive pronoun ("my," "your," "our," etc.)
- Verb suffix → object pronoun ("me," "you," "us," etc.)
- Preposition suffix → object pronoun after the preposition

---

## 10. Conjunction Waw

### 10.1 Waw as a Word-Part Token

The conjunction וְ/וַ/וּ ("and," "but," "then," "now," "so") is the most frequent element in the Hebrew Bible. It prefixes virtually every word class. MACULA Hebrew typically provides it as a distinct word-part token (P1) on the word it prefixes.

**Waw word-part token present:** primary 1:1, waw → its English rendering.

```json
{ "source": ["wawPart1Id"], "target": ["andId"] }
```

### 10.2 Waw-Consecutive (Wayyiqtol and Weqatal)

Waw-consecutive forms (וַיִּקְרָא, וְקָרָא) encode narrative sequencing or logical consequence. In MACULA, the waw prefix is typically a separate word-part token.

**Rendered as "and" / "then" / "so":** primary 1:1.
**Rendered as a bare sentence with no connective (asyndeton):** waw word-part → **NEQ**.
**Temporal subordination expressed by the translation ("when X, then Y"):** if "when" is supplied with no waw correspondent, it is **secondary** to the verb that carries the temporal relationship; waw → its own record or NEQ as appropriate.

### 10.3 Waw Folded into Single Token

When waw is not a separate word-part token, English "and"/"but" is **primary** to the containing word token — the conjunction is an explicit morpheme, not a grammatically implied feature.

### 10.4 NEQ and Asyndeton

**Hebrew waw + English asyndeton:** the waw word-part → **NEQ**.
**Hebrew asyndeton + English supplied conjunction:** the English conjunction → **NEQ**.

These are direct parallels to the Greek καί / asyndeton rules in `alignment-principles-nt.md §9.7.1`.

---

## 11. Construct Chains (סְמִיכוּת)

### 11.1 What Is a Construct Chain

A **construct chain** is a genitive-like relationship in Hebrew expressed purely by word order and a change in the construct noun's form — no preposition token is inserted. The construct noun (nomen regens) immediately precedes the genitive noun (nomen rectum). English typically renders this with "of" or a possessive:

- דְּבַר יְהוָה → "word of the LORD" / "the LORD's word"
- בֵּית יִשְׂרָאֵל → "house of Israel"
- עֵץ הַדַּעַת → "tree of the knowledge [of good and evil]"

### 11.2 Alignment of the Construct Noun

The construct noun aligns to the English head noun as a **primary** record.

### 11.3 English "of" from the Construct Relationship

When English uses "of" to render a construct chain, that "of" is **secondary** to the construct noun — there is no separate Hebrew preposition token; the relationship is expressed by the construct form.

```json
{
  "source": ["devarId"],
  "target": ["wordId", "ofId"],
  "meta": { "secondary": { "target": ["ofId"] } }
}
{ "source": ["yhwhId"], "target": ["lordId"] }
```

### 11.4 English Possessive ("'s") from the Construct Relationship

When English renders the construct with a possessive apostrophe ("the LORD's word"), align the construct noun to the English head noun and the genitive noun to the English possessor. No "of" appears; no secondary marker is needed.

```json
{ "source": ["yhwhId"],  "target": ["lordsId"] }
{ "source": ["devarId"], "target": ["wordId"]  }
```

### 11.5 Construct Chains of Three or More Links

Hebrew construct chains may extend across three or more nouns (e.g., דִּבְרֵי סֵפֶר הַתּוֹרָה "words of the book of the law"). Align each link individually following §11.2–11.4. Each 'of' is secondary to the construct noun it follows.

### 11.6 Adjectives in Construct Position

Hebrew adjectives occasionally appear in construct-like relationships. Apply the same secondary-"of" rule when English uses "of" to express the relationship.

---

## 12. Verbal Constructions

### 12.1 Verbless Clauses (Supplied Copula)

Hebrew frequently omits the copula in nominal sentences — predicate nouns and predicate adjectives appear with no form of הָיָה. English requires an explicit copula.

**Supplied copula** ("is," "are," "was," "were," "am") with no corresponding Hebrew verb token → **NEQ**. The copula is required by English grammar but is not implied by any single Hebrew word; it reflects the predicative structure of the sentence as a whole.

- טוֹב הָאוֹר (Gen 1:4) → "the light was good": "was" → **NEQ**
- יְהוָה אֱלֹהֵינוּ (Deut 6:4) → "the LORD is our God": "is" → **NEQ**

**When הָיָה is explicitly present**, this does not apply — align the verb token normally.

**Future and other inflected forms** (יִהְיֶה → "will be"): not ellipsis — יִהְיֶה → "will be" with "will" secondary (aspect marker) and "be" primary.

### 12.2 Supplied Subject Pronouns

Hebrew finite verbs encode person, gender, and number morphologically. Translations frequently supply an explicit subject pronoun for the verbal subject ("he," "she," "they," "I") when no independent Hebrew pronoun token is present.

**Supplied subject pronoun with no corresponding Hebrew pronoun token:** the pronoun is **secondary** to the finite verb token.

*Example:* וַיֹּאמֶר "and he said" — waw-word-part → "and" (primary); verb → "said" (primary); "he" → **secondary** to the verb.

```json
{ "source": ["wawPartId"],  "target": ["andId"]  }
{
  "source": ["verbId"],
  "target": ["heId", "saidId"],
  "meta": { "secondary": { "target": ["heId"] } }
}
```

**Explicit Hebrew pronoun present** (הוּא, הִיא, הֵם, אֲנִי, etc.): the pronoun aligns as a separate **primary** record to the English subject pronoun.

**Emphasis with explicit pronoun:** when the Hebrew has both an explicit pronoun and a verb (הוּא אָמַר "he himself said"), the independent pronoun carries an emphatic sense. Align: הוּא → "he" (primary, emphasis); verb → "said" (primary).

### 12.3 Verbal Stems (Binyanim)

Hebrew verbs inflect in seven primary stems (Qal, Niphal, Piel, Pual, Hiphil, Hophal, Hithpael) and several rare stems. Stem-driven meaning differences are captured in the translation's lexical choice, not by separate tokens. The same alignment rules apply regardless of stem.

**Passive stems (Niphal, Pual, Hophal) → English passive:** follow the same pattern as §12.4.

**Causative stems (Hiphil, Hithpael) → English causative or transitive rendering:** both English verbal elements are primary to the Hebrew verb token when the translation uses a multi-word causative expression ("caused to fall," "made to hear"). If a single lexical verb captures the meaning ("toppled," "proclaimed"), that single verb is the primary record.

**Intensive stems (Piel) → English intensive adverb + verb or single verb:** same principle — if the translation distributes the intensive meaning across multiple words, all are primary; if a single word captures it, that word is the primary record.

### 12.4 Passive Voice Constructions

Hebrew passives (Niphal, Pual, Hophal) are rendered in English with a "be" auxiliary + past participle.

- The past participle (main verbal element) is **primary** to the Hebrew verb token.
- The "be" auxiliary is **secondary** to the Hebrew verb token.

*Example:* נִכְתַּב "was written" — "written" primary; "was" secondary.

*Example:* נִשְׁמַע "has been heard" — "heard" primary; "has been" secondary.

**Passive with explicit agent:** when the translation makes an agent explicit (often with "by"), the agent noun aligns as primary to its Hebrew source token. No Hebrew agent may be present (theological passive; see below).

**Theological/divine passive:** Hebrew sometimes uses the passive to imply divine agency without naming God. When a translation makes the divine agent explicit:
- Supplied "God" with no Hebrew token → **NEQ** (context-supplied proper noun)
- The passive verb aligns normally as above

### 12.5 Infinitive Construct

The Hebrew infinitive construct (שְׁמֹר, לִכְתֹּב) is used as a verbal noun and in a variety of constructions. It typically carries the inseparable preposition לְ.

**לְ + infinitive construct:** when לְ is a separate word-part token, it aligns to English "to" as **primary** (§8.2). When לְ is not a separate token, English "to" is **primary** to the infinitive token (the לְ is an explicit morpheme, not a purely grammatical implication — contrast §3.2's secondary "to" for Greek).

**Purpose infinitive** (לִ + infinitive expressing purpose → "in order to," "to"): apply the lexical correspondence test. If "in order" has no separate Hebrew token corresponding to it, "in order" and "to" are both secondary to the infinitive token; or "to" is primary to the לְ word-part token and "in order" is secondary to the infinitive.

**Infinitive construct as verbal noun** (בְּ + infinitive → "when … -ing," "while …-ing," "in … -ing"): the infinitive token aligns to the main verbal element of the English expression. The preposition word-part aligns to the English temporal or logical connector ("when," "while," "in," "by") as primary.

### 12.6 Infinitive Absolute

The Hebrew infinitive absolute (שָׁמוֹר, כָּתוֹב) is used in two main constructions:

**Cognate accusative (emphasis):** the infinitive absolute precedes or follows a cognate finite verb to express emphasis or certainty: מוֹת תָּמוּת "you shall surely die." The infinitive absolute token aligns to the English emphasis word(s) ("surely," "certainly," "indeed"). The finite verb aligns to the main English verb. Both are **primary** records.

```json
{ "source": ["infAbsId"], "target": ["surelyId"]  }
{ "source": ["verbId"],   "target": ["dieId"]      }
```

If the translation absorbs the emphasis into the main verb without a separate English word (e.g., a strong modal: "you will certainly die" where "certainly" is not present), the infinitive absolute may be secondary to the finite verb — or NEQ if it is definitively untranslated.

**Infinitive absolute as imperative substitute:** in poetry and legal texts, the infinitive absolute may stand in for a finite verb or imperative. Align to the English rendering as a primary record; supplied subject pronoun is secondary if no pronoun token is present.

**Stacked verbal constructions:** when a translator renders the emphasis with a compound English phrase ("die you shall die," "dying you shall die"), both English verbal elements are primary to their respective source tokens.

### 12.7 Participle Constructions

Hebrew participles (active and passive) serve as adjectives, nouns, and continuous/progressive verbal predicates.

**Adjectival participle:** aligns to the English adjective or participial phrase — **primary**.

**Substantive (nominal) participle:** aligns to the English noun or noun phrase. When a Hebrew article word-part is present (הַשֹּׁמֵר "the one who keeps"), the article → English relativizer ("the one," "he who") per §7.1.

**Verbal (predicative) participle — continuous/progressive:** the Hebrew participle aligns to the English main verbal element. English progressive auxiliaries ("is," "was," "are," "were") are **secondary** to the participle.

*Example:* יֹשֵׁב "was sitting / is sitting" — "sitting" primary; "was"/"is" secondary.

**Participle + הָיָה (periphrastic construction):** when הָיָה is explicit, it aligns as a **primary** record to the English auxiliary ("was," "were," "had been"). The participle aligns to the English main verbal element. Two separate primary records.

---

## 13. Particles and Discourse Markers

### 13.1 Hebrew Conjunctions and Particles — General Approach

Hebrew has a rich inventory of conjunctions and particles. Align content words first; conjunctions and particles are residual — assessed after the main lexical correspondences are settled.

**Tier 1 — obvious direct associations.** When a conjunction or particle has a clear English correspondent in context, encode it directly as a primary 1:1 link:

| Hebrew | Common English rendering |
|---|---|
| וְ/וַ (waw) | "and," "but," "then," "so," "now" |
| כִּי | "because," "for," "that," "when," "if," "indeed" |
| אֲשֶׁר / שֶׁ | "who," "which," "that," "where," "when" |
| אִם | "if," "whether," "when," "though" |
| לָכֵן | "therefore," "so," "thus" |
| אַחַר / אַחֲרֵי | "after," "afterward" |
| כַּאֲשֶׁר | "as," "when," "just as" |
| פֶּן | "lest," "so that … not" |
| עַד | "until," "as far as" |

**Tier 2 — non-obvious cases.** When a conjunction or particle does not map cleanly to a specific English word, assess leftover tokens on both sides after content words are settled. Either a justifiable link exists or NEQ is the correct outcome. Both are valid.

**NEQ is valid.** For conjunctions and particles especially, a NEQ determination is a legitimate and often correct outcome. Forcing an alignment where none is clearly justified produces misleading data.

### 13.2 כִּי — Causal, Content, Conditional, Temporal, Emphatic, and Recitative

כִּי is among the most polyfunctional particles in Biblical Hebrew. The alignment follows what the translator did:

**Causal** ("because," "for"): primary 1:1.
**Content / object clause** ("that" — "he knew that…"): primary 1:1.
**Conditional** ("if," "when"): primary 1:1.
**Temporal** ("when," "as soon as"): primary 1:1.
**Adversative / concessive** ("but," "except," "although"): primary 1:1.
**Emphatic / asseverative** ("indeed," "surely," "certainly"): primary 1:1 when a corresponding word is present; **NEQ** when the translation absorbs the emphasis into the clause structure without a separate word.
**Recitative** (introduces direct speech): when the translation renders it with only quotation marks, a colon, or a dash — no corresponding word token — כִּי → **NEQ**.

> **Note:** Some alignment schemas permit aligning a source token to target punctuation. This project does not. Punctuation is not a valid alignment target; כִּי recitative is NEQ when the translation uses only punctuation to introduce the quotation.

### 13.3 אֲשֶׁר / שֶׁ — Relative and Subordinate Marker

אֲשֶׁר (and its clitic form שֶׁ) functions as a relative pronoun, a subordinating conjunction, and a complementizer.

**Relative clause** → "who," "which," "that," "whose," "whom": primary 1:1.
**Complementizer** ("that" — "he saw that…"): primary 1:1.
**Temporal / locative** ("where," "when"): primary 1:1.
**Untranslated** (absorbed into English clause structure without a word): **NEQ**.

### 13.4 Direct Object Marker (אֶת/אֵת)

The particle אֶת marks definite direct objects. It has no English equivalent and is typically untranslated.

**אֶת untranslated → NEQ.** This is the normal and expected outcome.

*Exception:* When a translator renders אֶת with an explicit topicalizing word ("as for," "namely," "even") — typically in emphatic or contrastive contexts — align אֶת to that word as a primary record.

### 13.5 Negation

**Simple negation** (לֹא, לֹו → "not," "no," "will not," "did not"): **primary** 1:1 record.

**Jussive/imperative negation** (אַל → "do not," "let … not"): **primary** 1:1 record.

**Existential negation** (אֵין, אֵינֶנּוּ, אַיִן → "there is no," "is not," "are not," "has no"):
- אֵין → the English existential negative expression — **primary** (often a 1:N mapping: אֵין → "there is no," with "is" and "no" both primary to אֵין; or אֵין → "is not," with both words primary).
- Pronominal suffixes on אֵין (אֵינֶנּוּ "he is not") → English subject pronoun — follow §9.2.

**Poetic/rare negation** (בַּל, בְּלִי, בְּלֵי → "not," "without," "no"): primary 1:1.

**Discontiguous verb with intervening negation:** when a negation particle is present, its English correspondent belongs in the negation record — not as secondary in the verb record. The verb record may be **discontiguous** (auxiliary and main verb non-adjacent, with the negation interleaved). This is expected and correct.

*Example:* לֹא אֵדַע "I do not know" — where English is "I do not know":

| Source | Target | Note |
|---|---|---|
| (verb subject) | "I" | secondary to verb (§12.2) |
| לֹא | "not" | primary 1:1 |
| אֵדַע | "do … know" | "know" primary; "do" secondary (added for English syntax) — discontiguous target |

### 13.6 Interrogative Prefix (הֲ/הַ/הֶ)

The interrogative prefix converts a statement into a yes/no question. MACULA typically provides it as a separate word-part token.

**Interrogative word-part token present, translation renders with an explicit question word or particle:** primary 1:1 to the English interrogative marker ("Is it that…," "Do you…" etc.). When English questions are formed purely by inversion (no explicit question particle), the interrogative prefix → **NEQ**.

**Single-token form (no split):** apply the same logic. If an English question marker exists, it is primary to the containing word token. If not, the interrogative sense is absorbed into English question syntax → **NEQ** for any reconstructed interrogative element.

### 13.7 Emphatic Particles

| Hebrew particle | Common function | Alignment |
|---|---|---|
| גַּם / גַּם … גַּם | "also," "even," "both … and" | Primary 1:1 to English equivalent |
| אַף / אַף כִּי | "also," "even," "how much more" | Primary 1:1 |
| רַק | "only," "but," "however" | Primary 1:1 |
| אַךְ | "surely," "only," "but" | Primary 1:1 |
| הִנֵּה / הֵן | "behold," "look," "see," "here is" | Primary 1:1 to English rendering; NEQ when the interjection is untranslated |
| נָא | Entreaty particle ("please," "pray"): primary 1:1 when translated; NEQ when untranslated | |

### 13.8 Conditional Sentences

**Condition marker** אִם / אִם … אִם → "if" / "whether … or": **primary** 1:1.
**כִּי conditional** → "if": **primary** 1:1 (§13.2).
**Translator-supplied "then"** in the apodosis: Hebrew often omits an explicit apodotic marker. When the translation supplies "then" with no corresponding Hebrew token, it is **NEQ**.

Everything else in a conditional sentence follows existing guidelines for supplied pronouns, helping verbs, and particles.

### 13.9 Temporal and Causal Constructions with בְּ + Infinitive Construct

Hebrew uses בְּ + infinitive construct to express temporal or causal relationships: "when X," "as X," "while X." The preposition word-part token aligns to the temporal connector ("when," "as," "while"); the infinitive aligns to the main verbal element. If the preposition is not a separate token, the temporal connector is primary to the infinitive token.

---

## 14. Idioms

An **idiom** is a multi-token expression in the source (or target, or both) whose meaning is not compositional — the phrase as a whole corresponds to the phrase as a whole, but the individual tokens do not map to each other in any reliable way.

Idiom records:
- May have any number of source and target tokens
- All tokens are implicitly **primary** at the phrase level
- Are marked with `meta.is_idiom: true`
- Do **not** use `meta.secondary`

**Hebrew idiom examples:**

- נָשָׂא פָּנִים → "to show favoritism / partiality" (lit. "lift up the face"). The individual tokens (verb "lift," noun "face") do not map to "favoritism" in any reliable word-level way. The phrase as a whole corresponds to the English expression.

- חָרָה אַף → "to be angry / furious" (lit. "the nose burned" — idiomatic for anger). The burning-nose idiom is non-compositional.

- הִכָּה בְּחֶרֶב → "to put to the sword" / "to kill with the sword": when rendered literally, individual tokens map; when rendered idiomatically ("put to the sword"), the idiom record is appropriate.

- שָׂם לֵב → "to pay attention" / "take to heart" (lit. "put heart"): the idiom as a whole maps to the English expression.

**Prefer smaller alignment units.** `meta.is_idiom` is a last resort — use it only when word-level mapping genuinely breaks down, not merely when mappings are counterintuitive or involve unexpected polarity or form shifts.

**Function words are never idioms.** A source unit consisting entirely of conjunctions, particles, or prepositions is never an idiom record. These elements have individual token-level correspondences or NEQ determinations; they must be aligned (or marked NEQ) individually.

**Frequency varies by translation type.** More literal translations preserve word-level correspondence more often; idiom records will be rarer. Dynamic or paraphrase translations restructure content more heavily and will use idiom records more frequently. The threshold does not change — only how often it is reached.

---

## 15. Hebrew Poetry and Parallelism

### 15.1 Parallelism Structure

Hebrew poetry is organized around **parallelism** — two or more lines (cola) that stand in synonymous, antithetic, or synthetic relationship. Parallelism affects alignment in the following ways:

**Each colon aligns independently.** Do not force one-to-one mapping between parallel cola. The second (or third) colon may repeat the first with different vocabulary, expand it, or contrast it. Each token in each colon aligns to its own best English correspondent in its own translation colon.

**Synonymous parallelism:** when two Hebrew words in parallel cola correspond to different English words meaning roughly the same thing, each aligns independently to its own English word. Do not merge parallel cola into a single record.

**Antithetic parallelism:** contrasting ideas in parallel cola are treated the same way — each token aligns in its own colon's record.

**Incomplete parallelism (gapping):** when the second colon omits a verb that is implied from the first ("gapping"), the omitted verb may have a corresponding English word in the translation's second colon. Align that English word as a secondary token in the first verb's record — the first colon's verb carries the correspondence for both.

### 15.2 Poetic Vocabulary and Rare Words

Hebrew poetry uses a richer and sometimes archaic vocabulary. Surface form differences (rare lexical choices, archaic morphology) do not prevent alignment. Apply the practical test (§3.4) as in prose.

### 15.3 Chiasm and Inverted Parallelism

Hebrew poetry sometimes inverts word order across parallel cola (A-B / B-A chiasm). Discontiguous token IDs may result. Serialize in document order; the alignment records are still correct.

---

## 16. Mounce Reverse Interlinear Reference Cases (Adapted for Hebrew)

The following cases parallel the NT reference cases and serve as concrete alignment examples in Hebrew.

### 16.1 Multiple English Words → Single Hebrew Token (N:1)

One alignment record, multiple target tokens, single source token. The primary token(s) carry the core lexical content; all grammatical helpers are secondary.

| Situation | Example | Secondary token(s) |
|---|---|---|
| Infinitive requires "to" (לְ not separate) | "to live" → לִחְיוֹת (single token) | "to" |
| Copula in verbless clause | "God is good" → טוֹב אֱלֹהִים | "is" → NEQ |
| Subject pronoun from verb ending | "he said" → אָמַר | "he" |
| Construct chain "of" | "house of God" → בֵּית הָאֱלֹהִים | "of" |
| Compound lexical meaning | "lovingkindness" → חֶסֶד | none — one primary |

### 16.2 Single English Word → Multiple Hebrew Tokens (1:N)

One alignment record, multiple source tokens, single target token. Common when a Hebrew construct chain or idiom is rendered by a single English word.

| Situation | Example | Notes |
|---|---|---|
| Construct chain → English compound | "battleground" → שְׂדֵה הַמִּלְחָמָה | Idiom or phrase-level primary |
| Article + noun → English noun | "king" → הַמֶּלֶךְ (single English, two source word-parts) | Article secondary in source |

### 16.3 Supplied Words with No Hebrew Equivalent

Hebrew translations regularly supply words not present in the source. Include them in the nearest appropriate record as secondary tokens. When a supplied word cannot be linked to any source token (even as secondary), it is **NEQ**.

| Supplied word type | Treatment |
|---|---|
| Subject pronoun from verb ending | Secondary target token linked to the verb |
| Supplied copula (verbless clause) | **NEQ** |
| Supplied "then" in apodosis | **NEQ** |
| Supplied proper name from context ("God did X") | **NEQ** — contextually derived, not a token |
| "the" from construct definiteness | Secondary target token linked to construct noun |
| Preposition "of" from construct chain | Secondary target token linked to construct noun |
| English progressive auxiliary ("was," "were") with Hebrew participle | Secondary to participle token |

### 16.4 Hebrew Tokens with No English Equivalent

Hebrew sometimes includes elements that English omits entirely.

| Hebrew element | Treatment |
|---|---|
| אֶת direct object marker | **NEQ** (standard) |
| כִּי recitative | **NEQ** |
| Waw conjunction + English asyndeton | **NEQ** |
| Infinitive absolute (emphasis absorbed) | Secondary to finite verb, or **NEQ** if definitively untranslated |
| Interrogative הֲ absorbed into question syntax | **NEQ** |

---

## 17. Discourse-Level

### 17.1 Discourse Restructuring

Hebrew narrative frequently strings clauses with waw-consecutive where English uses subordination, temporal clauses, or paragraph structure. Syntactic restructuring does not change the alignment task — tokens still align to their correspondents via the practical test (§3.4) regardless of structural differences.

- Do not mark tokens NEQ merely because the syntax was restructured
- Do not force artificial alignments to compensate for restructuring
- Conjunctions added or dropped as part of restructuring follow §10 and §13.1

### 17.2 Manual Alignment Strategy for Complex Verses

When manually aligning a complicated verse, start from the beginning and work forward token by token. If alignment becomes unclear or ambiguous in the middle, move to the end of the verse and work backward. This bidirectional approach frequently clarifies ambiguous stretches.

---

## 18. Pending Specifications

The following areas require further development before alignment work on them can proceed consistently:

- **Aramaic-specific constructions** — the Aramaic sections of Daniel and Ezra share many features with Hebrew but have distinct vocabulary, morphology, and some syntactic differences; a dedicated annex will supplement this document
- **Accents and cantillation** — occasional impact on word boundary interpretation; TBD
- **Poetic meter and acrostic structures** — no impact on token-level alignment, but relevant context for evaluating alignment quality in poetry

---

## 19. Workflow Overview

Alignments are produced through a two-stage process.

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
- Apply the article, conjunction, particle, and construct-chain guidelines (§§7–13)
- Apply Hebrew word-part token distinctions correctly (§6)
- Expand 1:1 links to appropriate N:N links where the grammar requires it
