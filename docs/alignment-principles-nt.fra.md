# Alignment Principles — French (fra), New Testament

Guidelines used by `refine-alignment` when aligning Bible translations into French
against the Greek New Testament (SBLGNT) source.

Sections marked **[fra]** contain French-specific rules or examples. Unmarked
sections are shared with the English guidelines (`alignment-principles-nt.md` and
`prompt/nt/eng.py`).

This document was reverse-engineered from the existing `prompt/nt/fra.py` (written
directly without a corresponding markdown doc, unlike the por/spa/ind/hin configs).
NEGATION and the restrictive "ne…que" claim were subsequently checked at full-corpus
scale against LSG (1910, full NT) and cross-checked against AFBRT (modern; Mark plus a
few epistles), TOB10 (modern, full NT), and ULBFR (modern, full NT) — see the
Cross-translation methodology note near the end of this document for what that check
changed. The remaining sections (ARTICLES, PASSIVE VOICE, INFINITIVAL CONSTRUCTIONS,
ἵνα CLAUSES) were spot-checked but not corrected — see that same note for what was
confirmed versus left unverified.

Source files: `src/text_align/refine/prompt/nt/fra.py`, `src/text_align/refine/prompt/nt/eng.py`
Prose reference copy: `src/text_align/refine/prompt/nt/fra.prose.py` (not imported).

**Key differences from Portuguese/Spanish (por/spa) and English:**

- **NOT pro-drop** — the inverse default from Portuguese/Spanish: French grammatically
  requires a subject pronoun in nearly every finite clause (verb forms are often
  phonologically ambiguous). When no Greek pronoun is present, the French subject
  pronoun is secondary to the verb (this is the *normal* case, not the exception). When
  an explicit Greek pronoun (αὐτός, ἐγώ, σύ) is present, the French pronoun is primary
  to it.
- **Contracted forms limited to du/des/au/aux** (de+le→du, de+les→des, à+le→au,
  à+les→aux). Non-contracting forms (de la, de l', à la, dans le/la, sur le/la, etc.)
  stay as two separate words.
- **Double-article attributive** (τὴν γῆν τὴν καλήν): Greek repeats the article before
  an attributive adjective; French uses one. First article → French article (Branch A);
  second article → secondary to the adjective (Branch B).
- **Partitive du/de la/des** for anarthrous mass nouns — secondary to the noun, distinct
  from the contracted-article case (partitive only applies when no Greek article token
  is present).
- **Reflexive passive** (se + verb) and **impersonal "on"** as passive equivalents —
  both real strategies alongside the auxiliary+past-participle passive.
- **Discontinuous ne…X negation** — a genuinely different structure from every other
  language config in this codebase: "ne" (pre-verbal) is primary to the Greek negation
  particle, and the post-verbal word (pas/jamais/plus/rien) is secondary in the *same*
  record, not the verb's record. The verb record itself never includes "ne" or "pas".
- **μόνον/μόνος overwhelmingly renders as "seul(ement)"** (simple adverb/adjective,
  primary 1:1, no negation machinery at all) — checked against all 111 SBLGNT μόνος
  instances across LSG/TOB10/ULBFR: "seul(ement)" alone accounts for 75–84% of
  renderings in every translation checked. **Restrictive "ne…que"** (= "only") is a
  real but minority pattern (3–5%) — when it does appear, both "ne" and "que" are
  primary to the Greek word for "only," and it is a distinct construction from
  negation.
- **"point" is a dated (LSG/1910) alternative to "pas"** — 460 instances in LSG NT vs.
  ~1 in the modern AFBRT sample; align it exactly like "pas" (secondary, same role)
  when it appears, but don't expect it in modern translations.
- **"aucun(e)"** is a common, stable negative determiner for οὐδείς/μηδείς alongside
  personne/rien/nul, not tied to translation age.
- **Governed infinitive prepositions** ("de"/"à") — many French verbs govern their
  infinitive complement with a preposition that has no Greek correspondent (cesser de,
  commencer à) — secondary to the infinitive.
- **Gérondif** (en + present participle) for the articular/temporal infinitive
  construction (ἐν τῷ + infinitive), parallel to Indonesian's "ketika"/"saat" finite-
  clause strategy but structurally a nonfinite gérondif rather than a finite clause.

`AUTOS`, `COMPARATIVE`, `CONDITIONAL`, `HOTI`, `IMPERSONAL`, `PARTICIPLE`, and
`VERBAL_ASPECT` blocks are imported unchanged from `eng.py` — no French-specific
mechanics were found for these constructions. See `alignment-principles-nt.md` for
those sections.

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Greek word(s) are behind this
translation word.

---

## ALIGNMENT PHILOSOPHY

Alignments are generous: include case-implied prepositions, morphologically-implied
pronouns, and context-implied articles. Do not restrict to strict lexical equivalents.

Prefer one record per source token — split rather than group. Create separate records
whenever source tokens can each independently map to distinct target tokens. Combine
into N:M records only when tokens form an inseparable semantic unit (idiom) or target
words cannot be individually assigned to separate source tokens. When in doubt, split.

Grammar-required translation words (implied pronoun, case preposition, modal helpers
["could," "might," "would"], reinstated article) are secondary to the source token whose
grammar requires them — not NEQ. NEQ is for words with no source-language grammatical
anchor.

---

## TOKEN ROLES **[fra]**

- **primary** — direct lexical or semantic connection to the Greek token
- **secondary** — exists only because of grammatical features in the Greek token's
  morphology (person, number, case, aspect, voice); no separate Greek word
- correspondence to a different Greek token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

**Common secondary cases:**

- **Subject pronoun** — French is NOT pro-drop. Verb forms are often phonologically
  ambiguous, so French grammatically requires a subject pronoun in nearly all finite
  clauses. When no Greek pronoun is present, the French subject pronoun is secondary to
  the verb. When an explicit Greek pronoun (αὐτός, ἐγώ, σύ, etc.) is present, the French
  pronoun is primary to that pronoun.
  Example: ἦλθεν → "il vint": "vint" primary; "il" secondary.
  Example (explicit pronoun): αὐτὸς ἦλθεν → "lui-même vint": "vint" primary to ἦλθεν;
  "lui-même" primary to αὐτός.

- **Auxiliary verb** — δεδίδαχεν → "a enseigné": "enseigné" primary; "a" secondary.

- **No infinitive marker** — λαβεῖν → "prendre": primary alone. "pour"/"afin de" for
  purpose: see purpose infinitive rules.

- **Indefinite article** — ἄνθρωπος → "un homme": "homme" primary; "un" secondary.

- **Case-implied preposition** — θεοῦ → "de Dieu": "Dieu" primary; "de" secondary
  (contracted form: see ARTICLES).

- **Periphrastic rendering** — when a single Greek token is rendered by multiple French
  words, all words carrying lexical content are primary; purely grammatical connectors
  (prepositions, relativizers, determiners) are secondary to the same token. This
  includes any source word encoding multiple semantic components — compound verbs,
  compound nouns, or morphologically rich stems. Never NEQ a target word that expresses
  a component of the source word's meaning.
  Examples: κυριεύει → "exerce son pouvoir sur": "exerce", "pouvoir" primary; "son",
  "sur" secondary. γινώσκουσιν (dative substantive participle) → "à des gens qui
  connaissent": "connaissent" primary; "à", "des", "gens", "qui" secondary. καρποφορέω
  → "porter du fruit": "porter", "fruit" primary; "du" secondary. φιλαδελφία → "amour
  fraternel": both primary.

---

## NEQ (NON-EQUIVALENT) **[fra]**

NEQ is a positive claim that no correspondence exists — never a fallback for
uncertainty. Unrecorded means correspondence was not determined (normal). NEQ records
must not include `meta.secondary`.

- Certain no correspondent → NEQ (source or target empty, `meta.rel: "NEQ"`).
- Uncertain → leave unrecorded.

Greek articles (POS T-*) are **never** NEQ — always secondary to the head when there is
no French correspondent. See ARTICLES → Branch B.

Supplied copula ("est", "sont", "était", "étaient") with no Greek εἶναι token → NEQ
target.

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, and aspect differences do not prevent alignment. Align on
lexical/semantic correspondence, not surface form.

---

## CANDIDATES

The alignment candidates provided are initial automated word-level suggestions with no
secondary classification, no idiom flags, and some errors. Restructure, split, merge, or
discard them freely. Word order does not constrain alignment.

---

## ARTICLES **[fra]**

For every Greek article (POS T-*): does it have a specific French word or contracted
form as its direct correspondent?

**YES → Branch A** (primary 1:1). **NO → Branch B** (secondary to head — never NEQ,
never omitted).

A Greek article is NEVER NEQ and NEVER omitted; it never gets its own record — it is
always secondary to the noun, adjective, participle, or proper name it modifies. A Greek
article NEVER corresponds to a preposition.

### Branch A — article has a French correspondent

- **→ "le/la/les":** 1:1 primary; noun/adjective/participle in its own record.
  Example: ὁ λόγος → "le Verbe": source=[ὁ], target=["le"] — primary 1:1; source=[λόγος],
  target=["Verbe"] — primary 1:1.

- **→ contracted preposition + article (du / des / au / aux only):** French contracts
  de+le → du, de+les → des, à+le → au, à+les → aux. Non-contracting forms (de la, de l',
  à la, dans le/la, sur le/la, etc.) stay as separate words — the article aligns
  normally to its French correspondent or Branch B.
  Greek article only (case-implied preposition, no separate Greek preposition token):
  the contracted form is the article's correspondent; the "de/à" component is absorbed
  — no separate secondary.
  Example: τοῦ λόγου → "du Verbe" (genitive, no separate Greek preposition):
  source=[τοῦ], target=["du"] — primary 1:1; source=[λόγου], target=["Verbe"] — primary
  1:1.
  Greek preposition + article both present: the contracted form is primary to the
  preposition; the article is secondary.source.
  Example: εἰς τὸν οὐρανόν → "au ciel": source=[εἰς, τόν], target=["au"] — primary: εἰς;
  secondary.source: [τόν]; source=[οὐρανόν], target=["ciel"] — primary 1:1.

- **→ possessive pronoun** ("son/sa/ses", "leur/leurs", "mon/ma", "notre/nos"): 1:1
  primary — ONLY when no explicit Greek possessive pronoun is present.
  Example (no explicit pronoun): τοὺς ὀφθαλμούς → "ses yeux": source=[τούς],
  target=["ses"] — primary 1:1; source=[ὀφθαλμούς], target=["yeux"] — primary 1:1.
  Example (explicit αὐτῶν): τοὺς ὀφθαλμοὺς αὐτῶν → "leurs yeux": source=[αὐτῶν],
  target=["leurs"] — primary 1:1; source=[τούς, ὀφθαλμούς], target=["yeux"] — primary:
  "yeux"; secondary.source: [τούς].

- **→ "ceux qui"/"celui qui" (substantive participle):** article → "ceux"/"celui"
  primary 1:1; "qui" secondary to the participle.
  Example: τοῖς πιστεύουσιν → "à ceux qui croient": source=[τοῖς], target=["ceux"] —
  primary 1:1; source=[πιστεύουσιν], target=["qui", "croient"] — primary: "croient";
  secondary: "qui"; "à" secondary to πιστεύουσιν (dative case-implied).

### Branch B — no French correspondent → secondary to head

Apply to each article independently; the head is always the word it grammatically
modifies. French Bible translations (LS 1910 and modern) omit the article before proper
names.

- **Articular noun, no article:** source=[τήν, χεῖρα], target=["main"] — primary:
  "main"; secondary.source: [τήν].

- **Double-article attributive** (τὴν γῆν τὴν καλήν): Greek uses two articles; French
  uses one. First article → French article (Branch A); second article → secondary to
  the adjective (Branch B).
  Example: τὴν γῆν τὴν καλήν → "la bonne terre": source=[τήν₁], target=["la"] — primary
  1:1; source=[γῆν], target=["terre"] — primary 1:1; source=[τήν₂, καλήν],
  target=["bonne"] — primary: "bonne"; secondary.source: [τήν₂].

- **Articular infinitive:** secondary to the infinitive (or absorbed into "au"/"du" —
  see Branch A).
  Example: τοῦ πιστεύειν → "de croire": source=[τοῦ, πιστεύειν], target=["de", "croire"]
  — primary: "croire"; secondary.source: [τοῦ]; secondary.target: ["de"].

- **Article before a proper name:** ὁ Ἰησοῦς → "Jésus": source=[ὁ, Ἰησοῦς],
  target=["Jésus"] — primary: "Jésus"; secondary.source: [ὁ].

### Anarthrous noun → "un/une" or partitive

No Greek article token exists. Two cases:

- **Count noun:** "un/une" secondary. ἄνθρωπος → "un homme": source=[ἄνθρωπος],
  target=["un", "homme"] — primary: "homme"; secondary.target: ["un"].
- **Partitive (mass/uncountable):** du/de la/des secondary. Distinguish from the
  contracted article: du/de la is partitive only when no Greek article token is
  present; otherwise align under Branch A.
  Example: ἄρτον → "du pain" (anarthrous, partitive): source=[ἄρτον], target=["du",
  "pain"] — primary: "pain"; secondary.target: ["du"].

---

## CONJUNCTIONS AND PARTICLES **[fra]**

- Clear correspondent → primary. Multiple words rendering one: all primary
  (ὥστε → "de sorte que": all three primary).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

---

## IDIOMS **[fra]**

`meta.is_idiom: true` when phrase-level correspondence has no token-level equivalent.
All tokens implicitly primary; `meta.secondary` does not apply.

Last resort — always prefer standard records, even with loose primary matches. Use idiom
only when no plausible token-level decomposition exists. Function-word-only source
records (POS C-*, X-*, prepositions) are never idioms.

Example: καὶ ἐγένετο → "Et il arriva que":
Wrong: source=[καί, ἐγένετο], target=["Et","il","arriva","que"], `is_idiom: true`.
Better: source=[καί], target=["Et"] — primary 1:1; source=[ἐγένετο],
target=["il","arriva","que"] — primary: "arriva"; secondary: "il", "que".

Example: μὴ γένοιτο — optative negation ("Loin de là !" / "Certes non !" / "À Dieu ne
plaise !"). French translations typically render this as a fixed idiom with no
token-level mapping — use `is_idiom: true`. Only prefer standard records if the
translation is literal enough to allow granular alignment (μή → negation; γένοιτο →
verb).
source=[μή, γένοιτο], target=["Loin","de","là"] — `is_idiom: true`.

---

## PASSIVE VOICE **[fra]**

Auxiliary + past participle: past participle primary; auxiliary ("a été", "est")
secondary. Subject pronoun required by French grammar: secondary (person/number from
Greek morphology, not a separate token).

### Reflexive passive (se + verb)

Main verb primary; "se/s'" secondary — voice is morphological in Greek, lexical in
French.
Example: γέγραπται → "il s'accomplit": source=[γέγραπται], target=["il", "s'",
"accomplit"] — primary: "accomplit"; secondary: "il", "s'".

### Impersonal "on" as passive equivalent

Greek passive rendered as "on" + active verb: main verb primary; "on" secondary — no
separate Greek correspondent.
Example: ἐρρέθη → "on dit": source=[ἐρρέθη], target=["on", "dit"] — primary: "dit";
secondary: "on".

Example (auxiliary passive): γέγραπται → "il est écrit": source=[γέγραπται],
target=["il", "est", "écrit"] — primary: "écrit"; secondary: "est", "il".

---

## INFINITIVAL CONSTRUCTIONS **[fra]**

### Complementary infinitive

Infinitive primary; no separate marker in French (unlike English "to").
Example: θέλω ἐλθεῖν → "je veux venir": source=[ἐλθεῖν], target=["venir"] — primary 1:1.

### Governed infinitives with "de" or "à"

Many French verbs govern their infinitive complement with "de" (cesser de, permettre de)
or "à" (commencer à, aider à). These prepositions are secondary to the infinitive —
grammatical connectors with no separate Greek correspondent.
Example: ἤρξατο διδάσκειν → "commença à enseigner": source=[διδάσκειν], target=["à",
"enseigner"] — primary: "enseigner"; secondary: "à".

### Purpose infinitive with "pour"/"afin de"

"pour"/"afin de" secondary to the infinitive when purpose is already in the Greek verb;
primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
Example: ἦλθεν σῴζειν → "il vint pour sauver": source=[σῴζειν], target=["pour",
"sauver"] — primary: "sauver"; secondary: "pour".

### Articular infinitive → gérondif

When rendered as "en" + present participle: "en" primary to the governing preposition;
article secondary to the participle.
Example: ἐν τῷ σπείρειν αὐτόν → "en semant": source=[ἐν], target=["en"] — primary;
source=[τῷ, σπείρειν], target=["semant"] — primary: "semant"; secondary.source: [τῷ].

### Indirect discourse

Supplied "que" → secondary to the governing verb — not to the infinitive.
Example: λέγει αὐτὸν εἶναι → "dit qu'il est": source=[λέγει], target=["dit"];
source=[αὐτόν], target=["il"]; source=[εἶναι], target=["que", "est"] — primary: "est";
secondary: "que".

---

## ἵνα CLAUSES **[fra]**

- → "pour que"/"afin que" + subjunctive: all conjunction words primary to ἵνα.
  Subjunctive mood does not add a secondary token.
- → bare "que" + subjunctive (after verbs of wanting, commanding, permitting): "que"
  primary to ἵνα.
- → "pour"/"afin de" + infinitive (coreferential subjects): purpose-marking word(s)
  primary to ἵνα — not secondary to the infinitive.
- No correspondent → NEQ source (only when certain no element expresses purpose/result
  force).

Example: ἵνα σωθῇ → "pour qu'il soit sauvé": source=[ἵνα], target=["pour", "que"] — both
primary.
Example: θέλω ἵνα δῷς → "je veux que tu donnes": source=[ἵνα], target=["que"] — primary
1:1.
Example: ἵνα σῴζῃ → "pour sauver": source=[ἵνα], target=["pour"] — primary (purpose
marker); source=[σῴζῃ], target=["sauver"] — primary.

---

## NEGATION **[fra]**

### Standard French negation (ne…X)

French negation is a discontinuous two-part structure: **ne** (pre-verbal) + a
post-verbal negative word (**pas**, **jamais**, **plus**, **rien**, etc.). Together they
correspond to a single Greek negation particle (οὐ, οὐκ, οὐχ, μή).

**"point" is a dated alternative to "pas"** — checked across LSG (1910), TOB10, ULBFR,
and AFBRT: LSG uses "point" 460 times in the NT; the modern AFBRT sample (Mark plus a
few epistles) uses it essentially once; TOB10 and ULBFR fall in between (50 and 131).
Treat "point" exactly like "pas" — primary/secondary roles unchanged — but don't expect
it from a modern translation, and don't be surprised to see it heavily in LSG.

- "ne" is **primary** to the Greek negation particle; the post-verbal word (pas, plus,
  jamais, rien, etc.) is **secondary** in the same record — required by French grammar
  but not a separate Greek correspondent. Never NEQ the post-verbal word.
- The negated verb gets its own record with auxiliaries and subject pronoun; **do not
  include "ne" or "pas" in the verb record**.
- The verb record is discontiguous: "ne" precedes and "pas" follows the verb, but both
  stay in the negation record.
- In compound tenses ("il ne l'a pas vu"), "ne" and "pas" are discontiguous across the
  auxiliary and object clitic — both remain in the negation record.

Example: οὐκ ἔρχεται → "il ne vient pas": source=[οὐκ], target=["ne", "pas"] — primary:
"ne"; secondary.target: ["pas"]; source=[ἔρχεται], target=["il", "vient"] — primary:
"vient"; secondary: "il".

### Emphatic negation (οὐ μή)

Both Greek particles + both French words primary in a single record (two source tokens
justify two primary targets).
Example: οὐ μή + subjunctive → "ne…jamais [verb]": source=[οὐ, μή], target=["ne",
"jamais"] — both particles, both words primary.

### Compound negation tokens (single Greek token → "ne" primary, post-verbal word secondary)

- οὐκέτι/μηκέτι ("no longer") → "ne…plus": "ne" primary; "plus" secondary.
- οὔπω/μήπω ("not yet") → "ne…pas encore": "ne" primary; "pas", "encore" secondary.
- οὐδέ/μηδέ ("and not"/"neither"/"nor") → "ni" (primary) or "et ne…pas" ("ne" primary,
  "pas" secondary).
- οὔτε ("neither…nor") → "ni".
- οὐδείς/μηδείς ("nobody"/"no one"/"nothing") → "personne"/"rien"/"nul"/"aucun(e)" —
  primary. "aucun(e)" is a common, stable alternative to personne/rien/nul, checked
  across LSG/TOB10/ULBFR at similar rates (~112–168 instances per translation) — not
  a translation-age effect the way "point" is.
  Example: source=[οὐκέτι], target=["ne", "plus"] — primary: "ne"; secondary.target:
  ["plus"].

### Negation with negative pronouns

Negative pronoun (οὐδείς → "personne"/"nul"/"aucun", μηδείς → "rien"/"aucun") primary
to its Greek token. "ne" before the verb is retained; "pas" is typically omitted when a
strong post-verbal negative is already present.

### μόνον/μόνος: "seul(ement)" is the default, "ne…que" is a minority variant

**This corrects the document's original framing**, which presented "ne…que" as the
standard rendering for μόνον/μόνος. Checked against all 111 SBLGNT μόνος instances:

| Rendering | LSG | TOB10 | ULBFR |
|---|---|---|---|
| "seul(ement)" alone | 93 (84%) | 85 (77%) | 88 (79%) |
| "ne…que" alone | 3 (3%) | 4 (4%) | 6 (5%) |
| both together | 6 | 5 | 2 |
| neither (free rendering) | 9 | 17 | 15 |

**Default → "seul(ement)" as a simple adverb/adjective, primary 1:1, no negation
machinery at all.** This is not a negation construction — μόνον/μόνος is a positive
lexical item ("only/alone") and "seul(ement)" is its direct lexical correspondent.
Example: σὺ μόνος → "toi seul": source=[μόνος], target=["seul"] — primary 1:1.
Example: αὐτῷ μόνῳ λατρεύσεις → "tu le serviras lui seul": source=[μόνῳ],
target=["seul"] — primary 1:1 (governing verb and pronoun align separately).

**Minority variant → "ne…que" (restrictive, = "only")**, when the translation does use
it: both "ne" and "que" are **primary** to μόνον/μόνος — this is a distinct restrictive
construction, not a true negation, so do not treat "ne" here as a negation particle.
Example: οὐκ εἶδον εἰ μὴ τὸν Ἰησοῦν μόνον → "ils ne virent que Jésus seul": here both
strategies co-occur — source=[μόνον], target=["ne", "que", "seul"] — all three primary
(the translation doubles up for emphasis; treat each word as primary to the one Greek
token when they co-occur like this).

---

## Shared sections (imported unchanged from English)

The following blocks have no French-specific mechanics and are imported unchanged from
`prompt/nt/eng.py`. See `alignment-principles-nt.md` for full detail:

- **αὐτός (AUTOS)** — intensive, reflexive, third-person pronoun uses.
- **COMPARATIVES AND SUPERLATIVES**
- **CONDITIONAL CONSTRUCTIONS**
- **ὅτι (HOTI)** — conjunction vs. quotation-marker (recitativum) uses.
- **IMPERSONAL VERBS**
- **PARTICIPIAL CONSTRUCTIONS**
- **VERBAL ASPECT**

---

## Cross-translation methodology note

NEGATION was re-checked at full-corpus scale (SBLGNT.tsv joined to each target's TSV by
verse: 15,774 finite verbs, 2,642 οὐ/μή instances, 111 μόνος instances, compound
negation particles) against LSG (1910, full NT) and cross-checked against three modern
translations — AFBRT (Mark plus a few epistles; the modern Aquifer reference text this
config exists for), TOB10 (full NT), and ULBFR (full NT) — rather than the general-
knowledge claims the original `fra.py` draft was built from.

What held up unchanged: the discontinuous ne…X structure itself (checked via an overall
"ne" frequency proxy against the full SBLGNT οὐ/μή count — order-of-magnitude
consistent); auxiliary passive as the dominant passive strategy over reflexive "se" and
impersonal "on" (γέγραπται → "il est écrit" in 14/15 sampled instances); the
construct-chain-requires-"de" pattern (French "de" outnumbers Hebrew's מִן-family
preposition 4.7:1 in the OT, confirming French needs a supplied linking word — the
opposite of Indonesian's bare juxtaposition); non-pro-drop / required subject pronoun.

What changed: (1) μόνον/μόνος was reclassified from "renders as ne…que" (the document's
original framing) to "renders as seul(ement) in ~80% of cases, ne…que in ~4%" — a real
correction, not a caveat, cross-confirmed across three translations of different eras
and register. (2) "point" was identified as a dated (LSG-era) alternative to "pas" —
460 NT instances in LSG vs. ~1 in the modern AFBRT sample (1836 vs. 133 in the OT,
checked in the sibling OT document) — previously undocumented, and directly relevant
given LSG (1910) is one of only two data sources this codebase currently has for
French. (3) "aucun(e)" was added as a stable negative determiner for οὐδείς/μηδείς,
present at similar rates across all three translations checked (not a translation-age
effect).

What was checked and NOT changed, despite being tempting to "fix": the OT document's
gender-conditioned contraction claim (masculine/plural du/au vs. feminine de la/à la)
was spot-checked but the verse-level text-frequency method used elsewhere in this pass
could not isolate a clean signal (too much unrelated "au"/"du" elsewhere in long
verses). This claim describes settled French grammar (contraction is obligatory and
gender-determined, not a translation-style choice the way "point" or "seul" vs. "ne…que"
are), so it was left as-is rather than force a corpus check unsuited to it.

## Open questions for native-speaker review

- Confirm the "point" register note doesn't need finer-grained treatment — e.g.
  whether TOB10's intermediate rate (50/NT) reflects deliberate archaizing style in
  specific books rather than a uniform modern-vs-1910 split.
- The ARTICLES, PASSIVE VOICE, and INFINITIVAL CONSTRUCTIONS sections were spot-checked
  (a handful of examples pulled during the negation/μόνος pass) but not independently
  re-derived at full-corpus scale the way NEGATION was. A future pass could apply the
  same discipline to double-article attributive ordering, gérondif usage for the
  articular/temporal infinitive, and governed "de"/"à" infinitive prepositions.
