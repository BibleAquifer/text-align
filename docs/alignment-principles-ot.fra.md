# Alignment Principles — French (fra), Old Testament

Guidelines used by `refine-alignment` when aligning Bible translations into French
against the Hebrew Old Testament (MACULA Hebrew / Westminster Leningrad Codex) source.

Sections marked **[fra]** contain French-specific rules or examples. Unmarked sections
follow the shared structural conventions of the English guidelines
(`alignment-principles-ot.md` and `prompt/ot/eng.py`).

This document was reverse-engineered from the existing `prompt/ot/fra.py` (written
directly without a corresponding markdown doc). NEGATION was subsequently checked at
full-corpus scale against LSG (1910, full OT) and cross-checked against TOB10 (modern,
full OT) — no modern French OT translation with Mark-equivalent coverage was available
the way AFBRT's Mark data is for the NT. See the Cross-translation methodology note near
the end of this document. The remaining sections (ARTICLES, CONSTRUCT CHAINS,
INSEPARABLE PREPOSITIONS) were spot-checked but not corrected.

Source files: `src/text_align/refine/prompt/ot/fra.py`, `src/text_align/refine/prompt/ot/eng.py`

**Key differences from OT Portuguese/Spanish (por.py/spa.py):**

- **NOT pro-drop** (the inverse default from Portuguese/Spanish): a supplied subject
  pronoun is normally present and normally secondary, since French grammatically
  requires one in nearly every finite clause, even where Hebrew encodes person/number
  only in the verb ending (waw-consecutive, etc.).
- **Gender-conditioned contraction** — a genuinely new axis of variation versus
  Spanish's fixed del/al: du/des/au/aux contract only for masculine/plural nouns; de
  la/à la stay two words for feminine singular.
- **Hebrew's own double-article attributive pattern** (הָאָרֶץ הַטּוֹבָה) parallels
  Greek's τὴν γῆν τὴν καλήν and gets the same first-article-primary/second-secondary
  treatment.
- **Geographic proper names keep the article** (le Jourdain, le Liban); **personal
  names drop it** (Jésus, David) — a place/person split, not a translator's-choice
  split the way it is in Portuguese.
- **No preposition+pronoun fusion at all** (avec moi, chez moi always stay two words) —
  simpler than both Portuguese and Spanish here.
- **Full ne…X discontinuous negation structure** (closer to OT English's discontiguous
  treatment than to Portuguese/Spanish's simplified contiguous version). **"point" is a
  dated (LSG/1910) alternative to "pas"** — 1,836 instances in LSG's OT vs. 133 in the
  modern TOB10, an even larger gap than the NT document's parallel finding; align it
  like "pas" but don't expect it from a modern translation. **"aucun(e)"** is a stable
  negative determiner alongside personne/rien/nul.
- **Gérondif** (en + present participle) for the temporal בְּ+infinitive construction;
  no personal infinitive; infinitive absolute still needs a secondary subject pronoun
  despite French's synthetic future, because French is not pro-drop.

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s)
are behind this translation word.

---

## HEBREW WORD-PART TOKENS

MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own
BCVWP ID. Common word-parts:

- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

Word-part present → align French correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main
token.

---

## TOKEN ROLES **[fra]**

- **primary** — direct lexical or semantic connection to the Hebrew token
- **secondary** — exists because of Hebrew grammar with no separate source token
  (construct relation, verbal morphology, merged definiteness)
- correspondence to a different Hebrew token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

**Common secondary cases:**

- **Subject pronoun** — French is NOT pro-drop. Verb forms are often phonologically
  ambiguous, so French grammatically requires a subject pronoun in nearly all finite
  clauses, even where Hebrew encodes person/number only in the verb ending
  (waw-consecutive, etc.). When no separate Hebrew pronoun token is present, the French
  subject pronoun is secondary to the verb — this is the normal case, not the
  exception (contrast Portuguese/Spanish, where a supplied pronoun is the less common
  case).
  Example: וַיֹּאמֶר → "et il dit": "et" primary (waw word-part); "dit" primary (verb
  token); "il" secondary.
  Example (explicit independent pronoun, rare, resumptive): הוּא אָמַר → "lui, il dit":
  "lui" primary to הוּא; "dit" primary to the verb; "il" still secondary (grammatically
  required regardless).

- **"de" from construct chain** — no preposition token; genitive by construct form.
  "de" secondary to the construct noun — UNLESS the absolute noun's own article
  word-part contracts with "de" (masculine/plural only; see CONSTRUCT CHAINS and
  ARTICLES).

- **French "le/la/les" when article merged** — no article word-part; "le/la/les"
  secondary to the noun token.

- **Preposition+article merged** (בַּ/לַ/כַּ/מֵהַ) — contraction is gender-conditioned:
  masculine/plural nouns after לַ/מֵהַ produce a single fused French word
  (au/aux/du/des), primary 1:1 to the one Hebrew token, no split; feminine singular
  nouns after לַ/מֵהַ, and any gender after בַּ/כַּ, never contract in French ("à la",
  "dans le/la", "comme le/la") — split as in English (preposition primary, article
  secondary). See ARTICLES and INSEPARABLE PREPOSITIONS for detail.

- **Auxiliary verbs for participles** ("était assis") — main verb primary; auxiliary
  secondary.

- **Periphrastic rendering** — when a single Hebrew token is rendered by multiple
  French words, all words carrying lexical content are primary; purely grammatical
  connectors (prepositions, relativizers, determiners) are secondary to the same token.
  This includes any source word encoding multiple semantic components — compound
  verbs, morphologically rich stems, or words whose French rendering distributes the
  meaning. Never NEQ a target word that expresses a component of the source word's
  meaning.
  Examples: מָשַׁל → "exerce sa domination sur": "exerce", "domination" primary; "sa",
  "sur" secondary. שֹׁמֵר (substantive participle) → "celui qui garde": "garde"
  primary; "celui", "qui" secondary. הוֹדוּ → "rendre grâce": both primary. הֵיטִיב →
  "faire du bien": "faire", "bien" primary; "du" secondary (partitive).

---

## NEQ (NON-EQUIVALENT) **[fra]**

NEQ is a positive claim that no correspondence exists — never a fallback for
uncertainty. Unrecorded means correspondence was not determined (normal). NEQ records
must not include `meta.secondary`.

- Certain no correspondent → NEQ (source or target empty, `meta.rel: "NEQ"`).
- Uncertain → leave unrecorded.

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases
(marks definite direct objects; no French equivalent). Rare exception: when explicitly
rendered "quant à" or similar.

Supplied copula ("est", "sont", "était", "étaient") with no Hebrew verb token → NEQ
target (verbless clause).
Example: יְהוָה אֱלֹהֵינוּ → "le SEIGNEUR est notre Dieu": source=[יְהוָה],
target=["SEIGNEUR"] — primary; "le" secondary (reinstated article); source=[אֱלֹהֵינוּ],
target=["notre", "Dieu"] — primary: "Dieu"; secondary: "notre" (suffix); "est" → NEQ
target.

Waw conjunction + French asyndeton → waw word-part NEQ source.
French conjunction with no Hebrew conjunction token → NEQ target.

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent
alignment. Align on lexical/semantic correspondence.

---

## GRANULARITY **[fra]**

Prefer one record per source token — split rather than group. Create separate records
whenever source tokens (or word-parts) can each independently map to distinct target
tokens. Combine into N:M records only when tokens form an inseparable semantic unit
(idiom) or target words cannot be individually assigned to separate source tokens. When
in doubt, split.

Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a
failure.

Grammar-required translation words (pronominal suffix, construct-chain particle ["de"],
modal helpers for verbal morphology ["pourrait," "devrait," "aurait"], implied article,
required subject pronoun) are secondary to the source token or word-part whose grammar
requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

---

## ARTICLES **[fra]**

Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.

- **Article word-part → "le/la/les":** primary 1:1; noun gets its own record.
- **Article word-part, no French "le/la/les":** secondary to the noun in the noun's
  record.
- **No article word-part, French "le/la/les" present:** secondary to the noun token.
- **French "un/une":** secondary to the noun (Hebrew has no indefinite article).
  Partitive "du"/"de la"/"des" for anarthrous mass nouns: secondary to the noun.
  Example: לֶחֶם → "du pain" (anarthrous, partitive): source=[לֶחֶם], target=["du",
  "pain"] — primary: "pain"; secondary.target: ["du"].
- **Double-article attributive:** Hebrew marks an attributive adjective with its own
  article word-part, parallel to Greek's double article (הָאָרֶץ הַטּוֹבָה, lit.
  "the-land the-good"). French uses one article. First article (on the noun) → French
  article (Branch A, primary 1:1); second article (on the adjective) → secondary to
  the adjective.
  Example: הָאָרֶץ הַטּוֹבָה → "la bonne terre": source=[articlePart₁], target=["la"] —
  primary 1:1; source=[אָרֶץ], target=["terre"] — primary 1:1; source=[articlePart₂,
  טּוֹבָה], target=["bonne"] — primary: "bonne"; secondary.source: [articlePart₂].
- **Article before a proper name:** geographic names keep the French article (le
  Jourdain, le Liban) — primary 1:1 when the Hebrew article word-part is present.
  Personal names drop it (Jésus, David) — secondary to the name, never NEQ.

---

## CONSTRUCT CHAINS **[fra]**

A construct chain expresses genitive by word order and construct form — no preposition
token.

- Construct noun → French head noun: primary. French "de" → secondary in the construct
  noun's record — UNLESS the absolute noun carries its own Hebrew article word-part AND
  is masculine/plural, in which case the contraction ("du"/"des") is assigned entirely
  to that article token's own record (Branch A above), and no secondary is added to the
  construct noun's record.
  Example (no article, proper name): בֵּית דָּוִד → "maison de David": source=[בֵּית],
  target=["maison", "de"] — primary: "maison"; secondary: "de"; source=[דָּוִד],
  target=["David"] — primary 1:1.
  Example (absolute noun's own article, masculine — contracts): בֶּן־הַמֶּלֶךְ → "fils du
  roi": source=[בֶּן], target=["fils"] — primary 1:1 (no "de" secondary needed);
  source=[articlePart], target=["du"] — primary 1:1 (contraction absorbs the implied
  "de"); source=[מֶּלֶךְ], target=["roi"] — primary 1:1.
  Example (absolute noun's own article, feminine — no contraction): בַּת הָעִיר → "fille
  de la ville": source=[בַּת], target=["fille", "de"] — primary: "fille"; secondary:
  "de" (no contraction absorbs it here); source=[articlePart], target=["la"] — primary
  1:1; source=[עִיר], target=["ville"] — primary 1:1.
- Construct definiteness: French article/contraction before a construct noun (no
  article token) → secondary to that noun.

---

## INSEPARABLE PREPOSITIONS **[fra]**

Preposition word-part alone (no merged article) → French preposition (de/à/comme/dans):
primary 1:1.

Preposition + merged article in the same token — contraction is gender-conditioned:

- לַ / מֵהַ (le/min + article) before a masculine/plural noun → single French word
  ("au"/"aux"/"du"/"des"), primary 1:1 to the one merged token, no split.
- לַ / מֵהַ before a feminine singular noun → "à la"/"de la" (no contraction): split —
  preposition primary, article secondary.
- בַּ / כַּ (be/ke + article) → never contract in French regardless of gender ("dans
  le/la", "comme le/la"): always split — preposition primary, article secondary.

Example (masculine, single merged token): לַמֶּלֶךְ → "au roi": source=[lammelekId],
target=["au", "roi"] — primary: "au" (contracted à+le), "roi".
Example (feminine, single merged token, no contraction): לַמַּלְכָּה → "à la reine":
source=[lammalkahId], target=["à", "la", "reine"] — primary: "à", "reine";
secondary.target: ["la"].
Example (never contracts): בַּבַּיִת → "dans la maison": source=[babbayitId],
target=["dans", "la", "maison"] — primary: "dans", "maison"; secondary.target: ["la"].

---

## CONJUNCTIONS AND PARTICLES **[fra]**

Align content words first; conjunctions and particles are residual.

- Waw word-part (pos=conjunction) → "et"/"mais"/"alors"/"donc"/"or": primary. Asyndeton
  → NEQ source.
- כִּי — polyfunctional; align to whichever French word carries its force in context
  ("que", "car", "parce que"). Introducing direct speech with only punctuation → NEQ
  source.
- אֲשֶׁר/שֶׁ — "qui"/"que"/"où"/etc. Absorbed without correspondent → NEQ source.

---

## IDIOMS **[fra]**

`meta.is_idiom: true` when phrase-level correspondence has no token-level equivalent.
All tokens implicitly primary; `meta.secondary` does not apply.

Last resort — always prefer standard records, even with loose primary matches. Use idiom
only when no plausible token-level decomposition exists. Function-word-only source units
are never idioms — they have individual correspondences or NEQ determinations.

---

## PRONOMINAL SUFFIXES **[fra]**

Pronominal suffixes are separate word-part tokens (pos=suffix). Each suffix → French
pronoun, primary 1:1.

- **Possessive suffix on noun:** suffix → possessive pronoun (primary); noun → head
  noun (primary).
  Example: דְּבָרוֹ → "sa parole": source=[davarPart], target=["parole"] — primary;
  source=[sufPart], target=["sa"] — primary.

- **Object suffix on verb:** suffix → object pronoun, primary 1:1. The verb record also
  carries its own required subject pronoun as secondary (French is not pro-drop — see
  TOKEN ROLES).
  Example: שְׁמָרֵנוּ → "il nous a gardés": source=[shamarPart], target=["il", "a",
  "gardés"] — primary: "gardés"; secondary: "il", "a"; source=[nuPart], target=["nous"]
  — primary.

- **Suffix on preposition:** suffix → governed pronoun, primary 1:1. Unlike
  Portuguese/Spanish, French never fuses a preposition with the following pronoun (avec
  moi, chez moi, sur moi always stay two words) — every case aligns as a plain 1:1 pair.
  Example: אֵלָיו → "à lui": source=[elPart], target=["à"] — primary; source=[sufPart],
  target=["lui"] — primary.

---

## NEGATION **[fra]**

### Standard French negation (ne…X)

French negation is a discontinuous two-part structure: **ne** (pre-verbal) + a
post-verbal negative word (**pas**, **jamais**, **plus**, **rien**, etc.). Together they
correspond to a single Hebrew negation word-part (לֹא, אַל).

**"point" is a dated alternative to "pas"** — checked against LSG (1910) and TOB10
(modern), both full OT: LSG uses "point" 1,836 times vs. TOB10's 133, an even sharper
gap than the parallel NT finding (see the sibling NT document). Treat "point" exactly
like "pas" — primary/secondary roles unchanged — but recognize it as a marker of LSG's
dated register, not general French.

- "ne" is **primary** to the Hebrew negation word-part; the post-verbal word (pas,
  plus, jamais, rien, etc.) is **secondary** in the same record — required by French
  grammar but not a separate Hebrew correspondent. Never NEQ the post-verbal word.
- The negated verb gets its own record with auxiliaries and the required subject
  pronoun; **do not include "ne" or "pas" in the verb record**.
- The verb record is discontiguous: "ne" precedes and "pas" follows the verb, but both
  stay in the negation record.

Example: לֹא יֵדַע → "il ne sait pas": source=[loId], target=["ne", "pas"] — primary:
"ne"; secondary.target: ["pas"]; source=[verbId], target=["il", "sait"] — primary:
"sait"; secondary: "il".

### אַל (jussive/imperative negation)

Same ne…X structure: "ne" primary; post-verbal word secondary.
Example: אַל תִּירָא → "ne crains pas": source=[alId], target=["ne", "pas"] — primary:
"ne"; secondary.target: ["pas"]; source=[verbId], target=["crains"] — primary 1:1.

### אֵין / אַיִן (existential negation)

Fixed idiomatic expression — no single word bears the negation alone: all words primary
1:N.
Example: source=[einId], target=["il", "n'y", "a", "pas"] — all primary.
Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ "il n'est pas") → suffix word-part primary
1:1 (see PRONOMINAL SUFFIXES).

### Restrictive "ne…que" (= "only")

When Hebrew רַק/אַךְ ("only") → "ne…que", both "ne" and "que" are **primary** to the
Hebrew word for "only" — do not treat "ne" here as a negation particle.
Example: source=[raqId], target=["ne", "que"] — both primary.

---

## PARTICIPIAL CONSTRUCTIONS **[fra]**

- **Adjectival:** align to French adjective or participial modifier — primary.

- **Substantive with article word-part:** article → French "celui qui"/"ceux qui"
  primary 1:1; "qui" secondary to the participle.
  Example: הַשֹּׁמֵר → "celui qui garde": source=[articlePart], target=["celui"] —
  primary 1:1; source=[participleId], target=["qui", "garde"] — primary: "garde";
  secondary: "qui".
  Anarthrous substantive (no article token): all nominalizing elements ("celui",
  "qui") secondary to the participle.

- **Verbal (predicative):** French auxiliary ("était"/"est"/"étaient") secondary; main
  verbal element primary.
  Example: יֹשֵׁב → "était assis": source=[participleId], target=["était", "assis"] —
  primary: "assis"; secondary: "était".

- **Periphrastic (participle + explicit הָיָה):** הָיָה → French auxiliary, separate
  primary record; participle → main verb, primary.
  source=[hayahId], target=["était"] — primary 1:1; source=[participleId],
  target=["assis"] — primary 1:1.

---

## INFINITIVAL CONSTRUCTIONS **[fra]**

### Infinitive construct with לְ

Separate לְ word-part (pos=preposition): if purposive, לְ → "pour"/"afin de" primary
1:1; infinitive → French verb primary. If purely complementary, the infinitive is
primary alone — no separate correspondent for לְ (unlike English "to").
Example: רָצָה לָלֶכֶת → "voulut partir": source=[verbPart], target=["partir"] — primary
1:1 (no "to"-equivalent secondary).

Governed infinitive: many French verbs govern their infinitive complement with "de" or
"à" (cessa de, commença à) with no Hebrew correspondent — secondary to the infinitive.
Example: הֵחֵל לְדַבֵּר → "commença à parler": source=[verbPart], target=["à", "parler"]
— primary: "parler"; secondary: "à".

### Purpose/temporal constructions (בְּ/לְ + infinitive)

Temporal (בְּ + infinitive, "when/while X-ing"): French renders this with the
**gérondif** (en + present participle). "en" primary to the preposition word-part;
infinitive → French present participle, primary.
Example: בְּשָׁמְעוֹ → "en entendant": source=[bePrepPart], target=["en"] — primary;
source=[verbPart], target=["entendant"] — primary (the gérondif does not inflect for
person — a suffix-marked subject typically has no separate French correspondent here).

Purpose (לְ + infinitive, "in order to"): לְ → "pour"/"afin de" primary 1:1; infinitive
primary.
Example: לָתֵת → "pour donner": source=[verbPart], target=["pour", "donner"] — both
primary (purpose marker + infinitive).

### No personal infinitive

Like Spanish, French infinitives (and the gérondif) do not inflect for person/number.
When a Hebrew infinitive construct carries a pronominal suffix marking its subject,
French has no ending to carry it: if the translation supplies an explicit pronoun,
align it as a normal suffix correspondent (see PRONOMINAL SUFFIXES); if it supplies
none, leave the suffix unrecorded — not NEQ.

### Infinitive absolute (cognate emphasis)

Infinitive absolute → French emphasis word ("certainement"/"assurément"): primary 1:1.
Finite verb → main French verb: primary.
Example: מוֹת תָּמוּת → "certainement tu mourras": source=[infAbsId],
target=["certainement"] — primary 1:1; source=[verbId], target=["tu", "mourras"] —
primary: "mourras"; secondary: "tu" (required subject pronoun — French is not
pro-drop, so this stays secondary even though French, like Portuguese/Spanish, has a
synthetic future with no auxiliary "shall"/"will" to mark).
Absorbed without separate French word → infinitive absolute secondary to finite verb,
or NEQ if definitively untranslated.

---

## Cross-translation methodology note

NEGATION was re-checked at full-corpus scale (WLCM.tsv joined to each target's TSV by
verse: 5,161 לֹא/לוֹא instances, 732 אַל, 793 אֵין-family) against LSG (1910, full OT)
and cross-checked against TOB10 (modern, full OT) — the only two complete French OT
translations available in this repo. Unlike the NT document, no modern French OT with
AFBRT-equivalent (deliberately-current, purpose-built) coverage exists to check
against, so this pass leans more heavily on the LSG-vs-TOB10 contrast alone.

What held up unchanged: the construct-chain "de" requirement (French "de" outnumbers
Hebrew's מִן-family preposition 4.7:1 — French genuinely needs a supplied linking word,
confirming the document's contrast with Indonesian's bare-juxtaposition pattern).

What changed: "point" was identified as a dated (LSG-era) alternative to "pas" — 1,836
OT instances in LSG vs. 133 in TOB10, an even sharper gap than the sibling NT document's
parallel finding (460 vs. ~1) — previously undocumented. "aucun(e)" was added as a
stable negative determiner, present at similar rates in both LSG and TOB10 (322 vs.
275) — not a translation-age effect the way "point" is.

What was checked and NOT changed: the gender-conditioned contraction claim (masculine
du/au vs. feminine de la/à la after לַ/מֵהַ) was spot-checked by cross-referencing
WLCM's noun-gender morph codes against LSG text, but the verse-level frequency method
could not isolate a clean signal — masculine and feminine cases showed nearly identical
raw "au"/"du" co-occurrence rates (41% vs. 37%), which is almost certainly noise from
unrelated contracted forms elsewhere in long OT verses rather than evidence against the
claim. This describes settled French grammar (contraction is obligatory and
gender-determined, not a translation-style choice), so it was left as-is.

## Open questions for native-speaker review

- ARTICLES, CONSTRUCT CHAINS, and INSEPARABLE PREPOSITIONS were spot-checked only
  (examples pulled during the negation pass), not independently re-derived at
  full-corpus scale. A future pass could apply the same discipline to the
  geographic-vs-personal-name article split and the double-article attributive pattern
  (הָאָרֶץ הַטּוֹבָה).
- If a modern, complete French OT translation becomes available (TOB10 is the only one
  currently in this repo), re-run the "point"/"aucun" checks against it for a second
  cross-translation data point beyond LSG-vs-TOB10.
