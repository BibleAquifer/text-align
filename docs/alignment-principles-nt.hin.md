# Alignment Principles — Hindi (hin), New Testament

Guidelines used by `refine-alignment` when aligning the Indian Revised Version Hindi
(IRVHin) against the Greek New Testament (SBLGNT) source.

Sections marked **[hin]** contain Hindi-specific rules or examples. Unmarked sections
are shared with the English guidelines (`alignment-principles-nt.md` and
`prompt/nt/eng.py`).

Examples are grounded in IRVHin and checked against the actual target TSV
(`nt_IRVHin.tsv`: John 1:1, John 3:16, Matthew 1:21, Mark 1:2–9) rather than
constructed from general knowledge alone. The major structural sections (negation,
ἵνα clauses, passive voice, substantive participles) were additionally cross-checked
against three other Hindi NT translations — HSB (`data/targets/HSB/nt_HSB.tsv`), OHCV
(`data/targets/OHCV/OHCV_hindi_20240610.tsv`), and GLT
(`data/targets/GLT/nt_GLT.tsv`, unfoldingWord Gateway Literal Translation Hindi, partial
NT coverage) — to separate general Hindi grammar from IRVHin's individual stylistic
choices, and a full-corpus (not just anchor-verse) frequency-count pass was run against
IRVHin alone to check whether "majority/default/most common" claims actually hold at
scale; see the Cross-translation methodology note near the end of this document for
what both checks changed.

Source files (to be created): `src/text_align/refine/prompt/nt/hin.py`,
`src/text_align/refine/prompt/nt/eng.py`

**Draft status:** this document has not yet been reviewed by a native Hindi speaker.
Portuguese, Spanish, and French configs were validated this way before being trusted in
production; Hindi should follow the same path before `hin.py` is written and used for
real alignment runs.

**Key differences from the Romance-language and Indonesian configs:**

- No articles at all (like Indonesian), but Hindi has grammatical gender, case-marking
  postpositions, and a productive genitive postposition (का/की/के) that inflects to
  agree with the *possessed* noun — none of which Indonesian has.
- Split-ergative case marking: the postposition ने appears on transitive subjects only
  in perfective aspect, with no source-language trigger at all — it is purely a target-
  grammar requirement (see ERGATIVE ने AND ACCUSATIVE/DATIVE को).
- को marks the dative (indirect object, "to/for," including a dative-experiencer
  subject construction attested in Acts 15:22 that maps cleanly to a genuine Greek
  dative) or, on a definite/animate direct object, differential object marking (DOM,
  no Greek trigger at all). Only the DOM use is purely grammar-internal to Hindi.
- Finite verbs are almost always periphrastic: participle (agreeing in gender/number)
  + copula (agreeing in person) is the ordinary way to form present, imperfect, and
  most other paradigms — not an optional stylistic choice the way Portuguese
  "estava fazendo" is. Treat the participle as primary and the copula as secondary by
  default, the same pattern as Portuguese/Spanish auxiliary passives, but expect it far
  more often.
- Compound ("light") verbs are pervasive: a Sanskrit/Persian/Arabic-derived noun +
  करना ("do")/होना ("be")/देना ("give") supplies most abstract verbal meanings
  (उद्धार करना "to save," प्रचार करना "to preach," प्रेम रखना "to love"). Treat as
  N:1 against the single Greek verb, all content words primary.
- Vector ("compound") verbs — V1 (main verb stem) + V2 (a semantically bleached second
  verb marking completion, suddenness, or benefit, e.g. दे दिया "gave" = दे + दिया) —
  are a distinct phenomenon from light verbs: V1 is primary, V2 is secondary aspectual
  marking, parallel to VERBAL ASPECT in the base guidelines.
- Substantive participles have (at least) four attested strategies, checked
  systematically against all 1,339 SBLGNT article+participle sequences and
  cross-checked against HSB and OHCV to guard against IRVHin-specific overfitting:
  जो + finite verb (secondary जो, the same role as yang/qui/que/che elsewhere) covers
  both generic and specific referents alike and was originally described as "the true
  majority default" over वाला — **a fresh 25-verse corpus-scale re-sample found जो and
  वाला running almost exactly even (8 instances each)**, so treat the two as roughly
  co-equal in frequency, not जो-dominant, though जो still reads as more general-purpose
  while वाला/वाली/वाले (a productive agentive nominalizer — 473 of 7,957 IRVHin NT verses
  contain it) is reserved for participles that compress into a stable, lexicalized
  agent-noun/role label ("सतानेवाले" persecutors, "रहनेवाले" dwellers — both robustly
  confirmed across all three translations); a plain, already-lexicalized noun (पाठक
  "reader," किसान "farmer") often bypasses the जो/वाला choice entirely, especially in
  HSB and OHCV; and a bare participial adjective or ordinary finite clause with no
  marker at all is a real minority option. **The cross-translation check overturned one
  claim from an earlier draft**: "आनेवाला" as a stable formulaic epithet for "the coming
  one" does NOT hold up — OHCV never uses it (always जो+plain verb instead), and even
  IRVHin/HSB apply it inconsistently to the same recurring Greek phrase. See
  PARTICIPIAL CONSTRUCTIONS for the full breakdown, including which formulaic
  renderings *do* hold up robustly (जो जय पाए in Revelation) versus which turned out to
  be single-translation quirks.
- The perfective/conjunctive participle (verb stem + कर, e.g. निकलकर "having gone out,"
  झुककर "having bowed," आकर "having come") maps directly and cleanly onto Greek
  circumstantial (temporal/causal) aorist participles — no supplied conjunction is
  needed the way English/Portuguese need "after"/"depois de," because -कर already
  carries "having done X" inherently.
- Negation has three particles, but the split is by *discourse function*, not mood:
  नहीं is the default/common negator across virtually all moods and tenses and very
  frequently co-occurs with an elided copula in predicate-nominal clauses; न is not
  restricted to subjunctive contexts (it is attested with plain indicative past,
  future, and modal forms) but is the dedicated, near-obligatory form for correlative
  "neither...nor" lists (न...न...), where it aligns 1:1 with each Greek οὐδέ/οὔτε in the
  list; मत is the true colloquial prohibitive ("मत डरना," "मत करना" — do not fear/do").
  See NEGATION for attested examples of all three.
- Passive voice has at least eight distinct strategies, checked systematically against
  a stratified sample of all 3,014 SBLGNT passive-voice verb forms: true periphrastic
  passive (participle/vector-compound + जाना, e.g. "दिया जाता है") is actually the
  single most common strategy, not one option among equals; a narrow stative-perfect
  exception (participle + copula, no जाना) is confirmed specific to the recurring "it
  is written" formula (लिखा है) rather than a general perfect-passive rule; a
  previously undocumented adjectival-resultative strategy (adjective + होना/बनना,
  e.g. "पूरा होना" for be fulfilled) turned out to be genuinely common; Hindi's own
  transitive/intransitive verb pairs (खोलना/खुलना) absorb many passives with no voice
  marking at all; light-verb/noun+होना idioms handle passives of experience and
  communication; and active-voice conversion (बपतिस्मा लिया "took baptism" = "was
  baptized") remains common beyond baptism verbs specifically. See PASSIVE VOICE for
  the full breakdown — check which strategy a given verse uses rather than assuming.

`AUTOS` and `HOTI` blocks are expected to import largely unchanged from `eng.py` with
example substitution only, now with a first corpus pass behind them (see the Shared
sections below) — `HOTI` is fully confirmed; `AUTOS`'s ordinary pronoun majority use is
confirmed but its intensive/reflexive sub-case is still an open gap. `COMPARATIVE` and
`CONDITIONAL`, previously assumed to transfer unchanged, turned out to need real
Hindi-specific rules once corpus-checked (से as the comparative standard-marker; a
केवल+relative exceptive strategy and a कि...है कि नहीं indirect-question strategy for
conditionals) — see the COMPARATIVE AND SUPERLATIVE and CONDITIONAL sections. Native-
speaker review should still confirm all four.

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Greek word(s) are behind this
translation word.

---

## ALIGNMENT PHILOSOPHY **[hin]**

Alignments are generous: include case-implied postpositions, morphologically-implied
pronouns, and grammar-required copulas or vector verbs. Do not restrict to strict
lexical equivalents.

Prefer one record per source token — split rather than group. Create separate records
whenever source tokens can each independently map to distinct target tokens. Combine
into N:M records only when tokens form an inseparable semantic unit (idiom, light verb,
vector verb) or target words cannot be individually assigned to separate source tokens.
When in doubt, split.

Grammar-required translation words (periphrastic copula, ergative ने, DOM को, vector
verb, reinstated demonstrative) are secondary to the source token whose grammar
requires them — not NEQ. NEQ is for words with no source-language grammatical anchor at
all, including postpositions that arise purely from Hindi's own verbal or case system
with no Greek trigger (see ERGATIVE ने AND ACCUSATIVE/DATIVE को).

---

## TOKEN ROLES **[hin]**

- **primary** — direct lexical or semantic connection to the Greek token
- **secondary** — exists only because of grammatical features in the Greek token's
  morphology (person, number, case, aspect, voice), or because Hindi's own grammar
  obligatorily requires a word with no separate Greek word behind it
- correspondence to a different Greek token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

**Common secondary cases:**

- **Subject pronoun** — Hindi verbs agree in gender and number but not richly in person
  the way Greek/Spanish/Portuguese verbs do (present/past participles mark gender and
  number only; only a few forms, like the copula है/हूँ/हैं, mark person). This means a
  dropped subject pronoun is *not* fully recoverable from verb morphology the way it is
  in Portuguese or Spanish — Hindi pro-drop is discourse-driven (topic continuity)
  rather than grammar-guaranteed. A pronoun is typically supplied when a clause
  introduces or switches to a new subject, and dropped when a coordinate clause
  continues the same topic.
  Example (Mark 1:6, topic continuity — no repeated subject): "यूहन्ना...वस्त्र पहने...
  रहता था और...खाया करता था" ("John wore...and ate...") — the second clause has no
  repeated यूहन्ना or subject pronoun; none is expected.
  Example (supplied, new subject): ἦλθεν → "वह आया" — "आया" primary; "वह" secondary.

- **Periphrastic finite verb (participle + copula)** — the ordinary way to form present,
  imperfect, and several other Hindi tenses is participle (agreeing in gender/number)
  + copula (agreeing in person), e.g. भेजता हूँ ("I am sending" — Mark 1:2), लिखा है
  ("is written" — Mark 1:2). This is closer to how Portuguese/Spanish/French mark the
  imperfect (estava fazendo, était en train de) than to a single Greek-style inflected
  verb, but unlike those languages it is not optional stylistic periphrasis — it is the
  unmarked, default paradigm. The participle carries the lexical content and is
  **primary**; the copula is **secondary**.
  Example (Mark 1:2): ἀποστέλλω → "भेजता हूँ": source=[ἀποστέλλω], target=["भेजता", "हूँ"]
  — primary: "भेजता"; secondary: "हूँ".

- **Light verb (noun/adjective + करना/होना/देना)** — many Greek verbs with no simple
  Hindi verbal root are rendered as a Sanskrit/Persian/Arabic-derived noun + a light
  verb supplying tense/agreement. The noun carries the lexical content and is
  **primary**; so is the light verb when it is the sole rendering of the Greek verb —
  treat the whole construction as an N:1 record against the single Greek token, both
  Hindi words primary (parallel to French/Portuguese analytic renderings, not to the
  auxiliary-secondary pattern above, because there is no separate Greek word for the
  light verb to be secondary to).
  Example (Matt 1:21): σώσει → "उद्धार करेगा": source=[σώσει], target=["उद्धार", "करेगा"]
  — both primary.
  Example (Mark 1:4): κηρύσσων → "प्रचार करता": both primary.

- **Vector/compound verb (V1 + V2)** — a distinct phenomenon from light verbs: V1 is
  the main verb carrying lexical content; V2 is a semantically bleached second verb
  (देना, जाना, लेना, डालना, बैठना, etc.) marking aspect (completion, suddenness,
  benefit/detriment) with no independent lexical content of its own in this use. V1 is
  **primary**; V2 is **secondary**, parallel to VERBAL ASPECT in the base guidelines.
  Example (John 3:16): ἔδωκεν → "दे दिया": source=[ἔδωκεν], target=["दे", "दिया"] —
  primary: "दे"; secondary: "दिया" (दिया here marks completive aspect, not a second
  "giving" event).

- **Conjunctive/perfective participle (verb stem + कर)** — renders Greek circumstantial
  (temporal/causal) participles directly; the -कर form itself already carries "having
  done X," so no separate conjunction is supplied or needed. Primary alone.
  Example (Mark 1:5): the participle rendered "निकलकर" ("having gone out") — primary,
  no secondary conjunction.

- **No infinitive marker beyond the verb's own -ना ending** — करना, आना, etc. are the
  citation/infinitive forms already; no separate marker word exists the way English has
  "to." Primary alone when functioning as a bare infinitive.

- **No indefinite article** — a bare noun is the default. Only when the translation
  supplies एक ("one") for emphasis or specificity is it secondary.
  Example (Mark 1:3): φωνή → "एक...शब्द" ("a voice"): source=[φωνή], target=["एक", "शब्द"]
  — primary: "शब्द"; secondary: "एक".
  Contrast: most anarthrous Greek nouns have no एक at all in the Hindi and need no
  secondary token.

---

## NEQ (NON-EQUIVALENT) **[hin]**

NEQ is a positive claim that no correspondence exists — never a fallback for
uncertainty. Unrecorded means correspondence was not determined (normal). NEQ records
must not include `meta.secondary`.

- Certain no correspondent → NEQ (source or target empty, `meta.rel: "NEQ"`).
- Uncertain → leave unrecorded.

Supplied copula with no Greek εἶναι token → NEQ target. Note Hindi can also *elide* its
own copula in some negative predicate-nominal clauses (Mark 1:7, "मैं इस योग्य [हूँ]"
rendered without हूँ) — when both Greek and Hindi omit the copula, there is simply
nothing to align; this is not a special case requiring its own rule.

Ergative ने and DOM/dative को are grammar-internal to Hindi's own case system (see
ERGATIVE ने AND ACCUSATIVE/DATIVE को) — they are **secondary** to the noun they mark,
not NEQ, even when no Greek case or preposition motivates them. NEQ is reserved for
target words with no plausible source anchor at all — ने/को virtually always have one
(the noun phrase itself).

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, and aspect differences do not prevent alignment. Align on
lexical/semantic correspondence, not surface form.

---

## CANDIDATES

The alignment candidates provided are initial automated word-level suggestions with no
secondary classification, no idiom flags, and some errors. Restructure, split, merge, or
discard them freely. Word order does not constrain alignment — Hindi is SOV with
postpositions, so Hindi and Greek token order diverge substantially more than
English/Romance-language word order does.

---

## DEFINITENESS AND ARTICLES **[hin]**

Hindi has no definite or indefinite article. For every Greek article (POS T-*), ask:
does the translation supply a distinct correspondent (a demonstrative, or a generic head
noun for a substantive participle)?

**DEFAULT → no separate word at all:** the noun stands bare; the article is secondary to
the noun's own record with no target word required. This is the majority case.

**MINORITY case → demonstrative supplied:** यह (proximal, "this") or वह (distal, "that,"
also the ordinary 3rd-person pronoun) sometimes renders an anaphoric Greek article —
primary 1:1, noun in its own record.

**Corpus-scale check**: a stratified sample (6 verses/book × 27 books, 418 article
tokens out of SBLGNT's 19,796 total) put attributive demonstrative-for-article at ≤7.7%
(restricted to the oblique attributive forms इस/उस/इन/उन, which typically premodify a
noun) — i.e. bare-noun is the correspondent for ≥92% of articles, solid quantitative
support for "the majority case" above. **Methodological caveat**: वह/वे are also the
ordinary 3rd-person pronoun with no relation to any article, so word-counting alone
can't cleanly separate demonstrative-for-article uses from plain pronoun uses — treat
this as an upper-bound estimate, not a precise percentage.

### Article rendered as a demonstrative

Example (first mention, no demonstrative): ὁ λόγος → "वचन" (John 1:1) — no
correspondent (article absorbed, no target word); source=[ὁ, λόγος], target=["वचन"] —
primary: "वचन"; secondary.source: [ὁ].

### Substantive participle — generic head noun + जो

Example: τοῖς πιστεύουσιν-type construction rendered "जो...विश्वास करे" (John 3:16
pattern, "जो कोई...विश्वास करे" — "whoever believes"): जो is the relativizer, secondary
to the participle/verb it introduces; कोई ("someone/anyone") supplies the head when no
explicit generic noun like "लोग" ("people") is present — secondary as well, parallel to
Indonesian's bare "yang" case (no separate head-noun word needed).

### Article before a proper name

Hindi never uses one. ὁ Ἰησοῦς → "यीशु": source=[ὁ, Ἰησοῦς], target=["यीशु"] — primary:
"यीशु"; secondary.source: [ὁ].

### Anarthrous noun

No Greek article token exists, and Hindi has no indefinite article by default — bare
noun, no secondary needed unless एक is explicitly supplied (see TOKEN ROLES).

---

## GENITIVE POSTPOSITION का/की/के **[hin]**

Hindi's genitive/possessive postposition inflects for the gender, number, and case of
the **possessed** noun (the noun that follows), not the possessor — का (masc. sg.
direct), की (fem. sg./pl.), के (masc. pl./oblique, and the fixed form before most
compound postpositions). This is structurally similar to French's du/de la/des or
Portuguese's do/da in that a single morpheme carries both a relational and an agreement
function, but the agreement target (the following noun) is different from either.

**Ordinary possessive/genitive** (Mark 1:2): यशायाह भविष्यद्वक्ता **की** पुस्तक ("the
book of Isaiah the prophet") — की agrees with the feminine पुस्तक ("book"), not with the
masculine भविष्यद्वक्ता ("prophet") it follows. का/की/के renders a Greek genitive case
with no separate Greek preposition token — **secondary** to the possessed noun, the same
practical treatment as Portuguese "de"/Spanish "de" for case-implied genitives.
Example: source=[भविष्यद्वक्ता's genitive-triggering noun, पुस्तक], target=["की",
"पुस्तक"] — primary: "पुस्तक"; secondary: "की".

**Objective genitive with a light verb** (Matt 1:21): अपने लोगों **का**...उद्धार करेगा
("he will save his people," literally "will do the salvation of his people") — का marks
the logical object of the light-verb construction उद्धार करना. Treat का as secondary to
उद्धार ("salvation," the noun half of the light verb), which is itself primary in the
light-verb record (see TOKEN ROLES).

**Compound postpositions built on के** — के लिये ("for," "for the sake of"), के साथ
("with"), के बाद ("after"), के सामने ("in front of," "before"), के पास ("near," "with,"
possession), के ऊपर ("above/on") and similar two-word postpositions use the fixed के form
regardless of the following noun's gender — के here is not doing independent agreement
work, and the whole compound aligns as a single functional unit to whatever Greek
preposition/case governs it.
Example (John 1:1): μετά (implicit in the dative construction rendered) → "**के साथ**"
("with" — "the Word was with God"): both के and साथ are secondary to परमेश्वर ("God"),
or primary to an explicit Greek preposition if one governs the phrase; ग्रीक genitive/
dative case with no separate preposition token → both secondary to the noun.
Example (Mark 1:2): εἰς + genitive-type purpose sense rendered "तेरे **लिये**" ("for you"):
लिये secondary to the pronoun it governs, or primary to an explicit purpose-marking Greek
element if present — apply the same practical test used for ἵνα/purpose infinitives
elsewhere (§ἵνα CLAUSES).

---

## ERGATIVE ने AND ACCUSATIVE/DATIVE को **[hin]**

Hindi has split ergativity: transitive verbs in the perfective aspect (simple past and
related forms) require the subject to carry the postposition ने. This has **no trigger
in Greek at all** — it does not correspond to any Greek case, voice, or aspect marking;
it is purely a requirement of Hindi's own verb-agreement system.

**ने is always secondary to the subject noun/pronoun it marks — never NEQ.** Treat it
exactly like a case-implied preposition, except that "the case" originates entirely in
Hindi grammar rather than in the Greek source.

**Corpus scale**: ने appears in 1,597 of 7,959 NT verses (20%), 1,757 tokens total — a
15-verse random sample confirmed the postposed-immediately-after-the-subject pattern
with no counter-example. को is far more frequent (2,690 tokens), consistent with its
four overloaded functions below versus ने's single function; splitting को's raw count
by function would need real token alignment, not word-counting, to do reliably.

Example (John 3:16): θεός (subject of ἠγάπησεν, a Greek finite verb with no separate
ergative-triggering morphology) → "परमेश्वर ने": source=[θεός], target=["परमेश्वर", "ने"]
— primary: "परमेश्वर"; secondary: "ने".

को has four distinct functions; only one is fully grammar-internal to Hindi with no
Greek trigger at all:

- **Dative** (indirect object, "to"/"for"): often corresponds to a Greek dative case or
  πρός/εἰς-type preposition — treat as a case-implied postposition, secondary to the
  noun, parallel to θεῷ → "to God" in the base guidelines.
- **Dative-experiencer subject**: a small closed class of Hindi verbs (अच्छा लगना
  "seem good/please," ज़रूरत होना "need," मिलना in some senses "obtain/receive") puts
  the logical subject in को rather than the ergative or plain nominative. This
  frequently corresponds directly to a genuine Greek dative construction and should be
  treated the same as ordinary dative — secondary to the noun, primary content mapped
  normally. Example (Acts 15:22): ἔδοξε τοῖς ἀποστόλοις-type construction → "प्रेरितों
  और प्राचीनों **को** अच्छा लगा" ("it seemed good to the apostles and elders"): को
  secondary to प्रेरितों/प्राचीनों, case-implied from the Greek dative, exactly as with
  θεῷ.
- **Differential object marking (DOM)** on a definite or animate direct object: no Greek
  correspondent at all (Greek marks the direct object with the accusative case
  regardless of definiteness/animacy) — still secondary to the noun it marks, not NEQ,
  because the noun phrase itself is the source anchor.
- **Purpose-infinitive marker** (करने को): attested in IRVHin (John 10:31 "पथराव करने
  को," Rev 8:6 "फूँकने को"), but cross-checking HSB and OHCV on the same verses shows
  both prefer के लिये instead ("पथराव करने के लिये") — को-as-purpose-marker is a real
  possibility in Hindi but IRVHin's individual choice here, not the translation-
  independent default. के लिये is the safer default assumption. See ἵνα CLAUSES.

Example (Mark 1:2, DOM): "मैं अपने दूत **को**...भेजता हूँ" ("I am sending my messenger"
— अपोστέλλω τὸν ἄγγελόν μου, a plain Greek accusative direct object): source=[ἄγγελόν],
target=["दूत", "को"] — primary: "दूत"; secondary: "को" (को here is DOM, not case-implied
from any distinct Greek marking, but still a grammatical requirement of the Hindi noun
phrase and therefore secondary, not NEQ).

---

## CONJUNCTIONS AND PARTICLES **[hin]**

- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

कि deserves special note: it functions both as a content-clause/purpose complementizer
("...ऐसा प्रेम रखा **कि** जो कोई...विश्वास करे..." — John 3:16, introducing a result/
purpose clause) and, distinctly, to introduce direct or reported speech, parallel to
ὅτι's dual function (see ὅτι below). Apply the same disambiguation test.

**Stability varies sharply by particle**, checked against a fresh cross-book sample:
γάρ → क्योंकि ("because") and ἀλλά → परन्तु/पर ("but") are both near-categorical 1:1
defaults (6/6 in each sample). **δέ is genuinely variable** — the same particle surfaces
as और, परन्तु, तो, or अब depending on context, and is sometimes absorbed into the
surrounding clause's connective sense with no separately identifiable word at all. Expect
the real NEQ-vs-correspondent judgment calls to concentrate on δέ, not γάρ/ἀλλά.

---

## IDIOMS **[hin]**

`meta.is_idiom: true` when phrase-level correspondence has no token-level equivalent.
All tokens implicitly primary; `meta.secondary` does not apply.

Last resort — always prefer standard records, even with loose primary matches, and
prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom marking whenever the
construction is a recognized light or vector verb rather than a genuinely
non-compositional phrase. Function-word-only source records (POS C-*, X-*,
prepositions) are never idioms.

μὴ γένοιτο — checked against all 13 SBLGNT occurrences (Romans/1 Corinthians/Galatians).
**12 of 13 render identically as "कदापि नहीं!"** ("by no means!"), a fixed idiom with no
token-level correspondence to μή or γένοιτο individually — `is_idiom: true`, both Greek
words primary. The one outlier, Gal 6:14, uses "ऐसा न हो" instead — the same idiom
already documented under NEGATION/ἵνα CLAUSES for negative-purpose clauses, so treat it
identically there rather than as a separate μὴ γένοιτο-specific rendering.

---

## PASSIVE VOICE **[hin]**

Checked systematically: all 3,014 SBLGNT passive-voice verb forms were enumerated
(`morph[3]=='P'`), and a 50-verse stratified sample of finite indicative passives across
Matthew, Mark, Luke, John, Acts, Romans, 1 Corinthians, Hebrews, and Revelation was
cross-checked against IRVHin, then **re-checked against HSB and OHCV** to separate
genuine cross-translation Hindi strategies from IRVHin-specific choices. Most of what
follows held up well — the true periphrastic passive, the stative-perfect exception for
"it is written," and the intransitive-verb-pair strategy are all confirmed, sometimes
with word-for-word identical renderings across all three translations. One example
(§7 below) did not hold up and has been corrected. **The earlier three-strategy picture
in this document undersold the real range** — IRVHin uses at least eight distinct
strategies.

**A follow-up corpus check qualifies the "single most common strategy" claim**: a fresh
33-instance sample deliberately drawn from books the original 50-verse sample barely
touched (Luke, John, Acts, 2 Corinthians, Galatians, Ephesians, Philippians, James,
1–2 Peter, Jude) found Strategy 3 (adjectival/nominal resultative) and Strategy 5
(light-verb + होना) as the *largest* categories there, not Strategy 1. The pattern looks
**genre-conditioned**: Strategy 1 (periphrastic जाना) dominates in narrative/concrete-verb
contexts (Gospels, Acts, 1 Corinthians — where the original sample concentrated), while
Strategy 3/5 dominate in doctrinal/exhortation epistles with abstract-quality predicates
(Ephesians, Philippians, James, Peter, Jude). Treat "which strategy is most common" as a
question to ask per genre, not a fixed corpus-wide ranking — identify which strategy is
in play verse by verse before assigning primary/secondary roles either way.

**Methodological caveat**: the `morph[3]=='P'` filter used to enumerate the 3,014
passive-voice forms also catches deponent middle/passive-form verbs (γίνομαι,
ἐνυπνιάζομαι, ὑπεραίρομαι, and John 13:4's middle ἐγείρω) that are not real semantic
passives. These don't test translation strategy the way genuine passives do and should
be excluded (or separately tagged) in any further sampling from this set.

### 1. True periphrastic passive (participle/vector-compound + जाना) — the default for ordinary transitive verbs

The largest single category in the sample (roughly 20 of 50 verses), spanning every
tense and mood, simple verbs, causatives, light verbs, and vector-compounds alike:
"प्रचार किया **जाएगा**" (will be proclaimed, Matt 24:14), "पकड़वाया **जाता है**" (is
betrayed, causative stem, Mark 14:21), "क्षमा किए **गए हैं**" (have been forgiven, light
verb, John 20:23), "मोल लिये **गए हो**" (have been bought, light verb, 1 Cor 6:20; 7:23),
"गवाही दी **गई है**" (it is testified, light verb, Heb 7:17), "उठाए **जाएँगे**" (will be
raised, 1 Cor 15:52), "मार डाले **गए**" (were killed, vector-compound, Rev 19:21).
Participle/light-verb-noun **primary**; जाना (in whatever tense/mood, plus any perfect
है layered on top, e.g. "ठहराया जा **चुका है**") **secondary**.

### 2. Stative-perfect (participle + copula, no जाना at all) — narrower than it first appeared

Confirmed stable and specific to the recurring "it is written" scripture-citation
formula: γέγραπται → "लिखा **है**," attested identically in Mark 1:2, John 8:17, and
Mark 14:21 within the very same verse that also contains a true periphrastic passive
(पकड़वाया जाता है) — proving this is a lexically-anchored exception for this one formula,
not a general "perfect passive" rule. **This is one of the strongest findings in the
whole document**: HSB and OHCV both render "लिखा है" identically for all of Mark 1:2,
Mark 14:21, and John 8:17 (three-way word-for-word agreement across independent
translations is rare — treat this mapping as safe to rely on). Do not extend this
pattern to other perfect passives by default — most (उठाए जाएँगे, गवाही दी गई है,
दिखाया गया था) use जाना. Participle **primary**; copula **secondary**, exactly as the
ordinary periphrastic finite-verb pattern (TOKEN ROLES).

### 3. Adjectival/nominal resultative (adjective + होना/बनना "become") — a genuinely common strategy, previously undocumented here

For passives describing a change of state or quality, IRVHin regularly converts the
Greek passive verb into a Hindi adjective + होना/बनना ("become"), with no verbal passive
marking anywhere in the clause: "**चंगा** हो जाएगा" (will be healed, Matt 8:8), "**अंधेरा**
हो जाएगा" (will be darkened, Mark 13:24), "**इकट्ठे** हुए/होकर" (were/having gathered
together, Mark 2:2, 6:30 — a stable lexicalized mapping for συνάγω-passive), "**पूरे**/
**परिपूर्ण** होना" (be fulfilled/completed — attested four separate times across Luke
1:23, Acts 13:52, Romans 8:4, and Revelation 17:17, an unusually stable cross-book
mapping for πληρόω/τελέω-passive), "**मूर्ख** बन गए" (became foolish, Rom 1:22),
"**तितर-बितर** हो गए" (were scattered, Acts 5:37), "**अचम्भित**/**चकित**" हुए (were
amazed, Acts 3:10). Treat the adjective as **primary** (it carries the lexical content
the Greek passive verb expresses) and होना/बनना as **secondary** — parallel to a light
verb, not to a case-implied postposition, since there is no noun-phrase argument
structure requiring it independently. **Confirmed cross-translation**: all three
translations use adjective+होना for Matt 8:8 and Luke 2:23/1:23-type "fulfilled"
passives — but expect the specific adjective to vary (IRVHin चंगा vs. HSB/OHCV स्वस्थ
for "healed"; IRVHin/HSB पूरा vs. OHCV's abstract-noun variant पूर्ति for "fulfilled,"
Rev 17:17). The **structural strategy** (state predicate + होना) is what is
translation-independent, not the specific lexical item.

**A third auxiliary, ठहरना ("be held/considered to be"), joins होना/बनना for
declarative/legal-verdict passives** — confirmed independently three times: Luke 2:23
(κληθήσεται → "पवित्र ठहरेगा," "will be called/considered holy"), James 2:24 (δικαιοῦται
→ "धर्मी ठहरता है," "is justified"), James 2:25 (δικαιωθεῖσα → "धार्मिक न ठहरी," "was
[not] justified"). Same primary/secondary treatment as होना/बनना — the state-word is
primary, ठहरना secondary.

### 4. Dedicated intransitive/unaccusative verb — no voice marking at all

Hindi has lexicalized transitive/intransitive verb pairs the way English has "open
(something)" / "(something) opens": खोलना/**खुलना** (open, Matt 27:52 "कब्रें **खुल**
गईं" — word-for-word identical across IRVHin, HSB, and OHCV, the strongest possible
cross-translation confirmation), सुखाना/**सूखना** (wither, Mark 9:18 "**सूखता** जाता
है"), रोकना/**रुकना** (hinder/stop, Rom 1:13 "**रुका** रहा"), उजाड़ना/**उजड़ना**
(devastate, Rev 18:19 "**उजड़** गया"), उठाना/**उठना** (raise/rise, John 13:4 "**उठ**कर"),
and जन्मना (be born, inherently intransitive; HSB and IRVHin both use जन्मना for Luke
2:11, though OHCV recasts as active "जन्म लिया," जन्म लेना, still avoiding any passive
marker). The Greek passive verb corresponds to the single Hindi intransitive verb,
**primary** alone — no secondary auxiliary is needed or present, since there is no
periphrasis at all.

### 5. Light-verb / noun + होना idiomatic construction — for passives of experience, relation, and communication

Overlaps with LIGHT AND VECTOR VERBS but deserves its own note here: passives of
experiential/relational/communicative verbs are frequently nominalized and paired with
होना ("happen to/occur") rather than rendered with any passive-specific marking:
"**चर्चा** हो रही है" (is being talked about/proclaimed, Rom 1:8), "**महिमा** इसी से
होती है" (glory comes about/is glorified, John 15:8), "तुम पर **दया** हुई" (mercy came
upon you/you were shown mercy, Rom 11:30), "**जाँच** आत्मिक रीति से होती है"
(examination happens spiritually/is discerned, 1 Cor 2:14), "तुम्हारे वश में **हैं**"
(are in your control/are subjected, Luke 10:20), "**दिखाई** दिया" (appeared, literally
"gave visibility" — an experiencer-को idiom, 1 Cor 15:7, parallel to को अच्छा लगना in
ERGATIVE ने AND ACCUSATIVE/DATIVE को). The noun is **primary**; होना/देना is
**secondary**, same treatment as an ordinary light verb. **Note the ὁράω-passive
("appear") case specifically diverges by translation**: IRVHin and HSB both use
दिखाई देना for 1 Cor 15:7, but OHCV instead uses **प्रकट होना** ("become manifest,"
Strategy 3's adjectival-resultative pattern) for the same verse — both are valid
"appear" renderings, but they are structurally different strategies (idiom-experiencer
vs. adjectival-resultative), so check which one a given translation actually uses
rather than assuming दिखाई देना.

### 6. Bare resultative participle (+ हुआ/हुई/हुए, no finite copula) as an attributive adjective

A participle-of-होना (हुआ/हुई/हुए) attaches directly to its head noun with no separate
finite copula at all, functioning as a pure attributive modifier rather than a
predicate: "बलि की **हुई**" (having been sacrificed, 1 Cor 8:7), "नगर...बसा **हुआ** था"
(the city was situated/settled, Luke 4:29 — पूर्ण finite था here supports it, but the
हुआ itself carries the resultative sense, distinct from the participle+है predicate
pattern in Strategy 2). Same treatment as the bare-adjective participle pattern
documented in PARTICIPIAL CONSTRUCTIONS: the content participle is **primary**, the
हुआ/हुई/हुए component is **secondary** when it is separable from the main lexical verb.

### 7. Active-voice conversion — real, but check per verse; do not over-generalize from one example

Full voice flip, recasting the passive event as an active clause. **Correction:** this
document originally used Matt 11:27 ("**मेरे पिता ने** मुझे सब कुछ **सौंपा है**," "my
Father has entrusted me with everything," for an agentful passive with an explicit
ὑπὸ-phrase) as the flagship example. Cross-checking HSB and OHCV on that same verse
shows this was overfit to IRVHin: both other translations instead **keep the passive**
with an explicit द्वारा-agent phrase ("मेरे पिता **के द्वारा**...**सौंपा गया है**" — a
plain instance of Strategy 1 with an agent phrase added, not voice conversion at all).
Only IRVHin fully flips to active for this particular verse.

The strategy is still real, just better evidenced elsewhere: "**बपतिस्मा लिया**" (took
baptism = "was baptized," Mark 1:5) is **confirmed identically or near-identically
across all three translations** ("बपतिस्मा लेने लगे" HSB, "बपतिस्मा ले रहे थे" OHCV —
all three use the active light-verb, none uses a passive here), a much more solid
anchor example. "**मान लिया**" (accepted/agreed, for "were persuaded," Acts 17:4) is
confirmed in two of three (IRVHin, HSB); OHCV paraphrases further ("आश्वस्त होकर...सहमत
हो गए," a double adjectival-resultative construction, Strategy 3) rather than using
मानना, but stays broadly active either way.

**Practical takeaway:** active-voice conversion is a genuine, recurring strategy — but
confirm it against more than one translation before treating a specific verse's
active rendering as "the" Hindi strategy for that passive, since a passive-with-
द्वारा-agent-phrase (Strategy 1) is always an available, and sometimes preferred,
alternative. The whole active verb complex aligns to the single Greek passive verb —
both words primary when it is a light-verb pattern (TOKEN ROLES), with voice conversion
noted per SURFACE FORM DIFFERENCES. Any newly supplied subject with a genuine Greek
ὑπό-agent phrase behind it is primary to that agent noun, not NEQ, since the
correspondence is real even though the grammatical role (subject vs. agent adjunct)
changed.

### 8. Naming/equational conversion

Passives of naming (κέκληται, ὀνομάζομαι-type) sometimes convert entirely to a
possessive-copular naming sentence with no verb corresponding to "is called" at all:
"उसका नाम '**परमेश्वर का वचन**' **है**" ("his name is 'the Word of God,'" for κέκληται,
Rev 19:13) — contrast the "called X" epithet pattern in PARTICIPIAL CONSTRUCTIONS
(शमौन जो जेलोतेस **कहलाता है**), which does keep a verb (कहलाना, a lexicalized
middle/passive-equivalent). **Cross-checked**: for Rev 19:13 specifically, IRVHin and
OHCV both drop the verb (नाम...है), while HSB alone keeps कहलाना — so the pure
naming/equational conversion is actually the majority choice here, not a minor
alternative to कहलाना as an earlier draft implied. Both are valid; check which one a
given verse uses rather than assuming.

---

## LIGHT AND VECTOR VERBS **[hin]**

See TOKEN ROLES for the primary/secondary split. Two distinct phenomena, easily
confused:

- **Light verb** (noun/adjective + करना/होना/देना/रखना supplying the verbal slot for a
  borrowed or nominal lexeme): both words primary, N:1 against the single Greek verb.
  उद्धार करना (save), प्रचार करना (preach), प्रेम रखना (love, John 3:16 "प्रेम रखा").
- **Vector verb** (V1 main verb + V2 aspectual auxiliary from a small closed set —
  देना, लेना, जाना, डालना, बैठना, पड़ना): V1 primary, V2 secondary. दे दिया (John 3:16),
  खा लिया-type "ate up," आ गया-type "arrived" (completive).
- **खाना as a light-verb support verb** — beyond its literal "eat" sense, खाना also
  supplies the verbal slot for a small set of experiential/relational idioms, confirmed
  independently twice against GLT (`data/targets/GLT/nt_GLT.tsv`): "ठोकर खाता है"
  (stumbles, 1 Cor 8:13) and "भय खाता है" (fears, 1 John 4:18). Treat like करना/होना/
  देना/रखना — the noun (ठोकर, भय) is primary, खाना secondary, N:1 against the Greek verb.

The practical test: is the second element a Sanskrit/Persian/Arabic noun's supporting
verb with no aspectual nuance of its own (light verb, both primary), or a semantically
bleached native verb adding completive/benefactive/sudden nuance to a fully verbal V1
(vector verb, V2 secondary)?

**Corpus scale**: light-verb nouns are far more pervasive than the handful of examples
above suggest — NT-wide occurrence counts include विश्वास 471, प्रेम 250, आज्ञा 209,
राज्य 189, प्रार्थना 134, विनती 120, उद्धार 98, प्रचार 80, क्षमा 80, चंगा 64. This is a
high-frequency, structural pattern in IRVHin, not an occasional idiom — expect it
constantly, not just in the handful of illustrated verses.

---

## INFINITIVAL CONSTRUCTIONS **[hin]**

Hindi has a true infinitive (verb stem + ना: करना, आना, जाना), unlike Indonesian, which
has none.

### Complementary infinitive

After a modal or matrix verb, the bare infinitive is primary; no additional marker word
is needed. Example: θέλω ἐλθεῖν-type construction → "आना चाहता हूँ" ("want to come") —
"आना" primary; "चाहता हूँ" aligns to the matrix verb in its own record.

### Purpose infinitive with के लिये or को

के लिये ("for," "in order to") governing an oblique infinitive (करने के लिये, "in order
to do") carries purpose force — primary to an explicit ἵνα-type Greek purpose marker
when present, or secondary to the infinitive when the purpose sense is already carried
by the Greek verb alone. Apply the same test as Portuguese "para"/Indonesian "untuk."
को can also mark a purpose infinitive (करने को, John 10:31 "पथराव करने को," Rev 8:6
"फूँकने को") — a real but IRVHin-leaning choice; HSB and OHCV both use के लिये on the
same verses. **A 4th translation, GLT, uses neither on this verse** — "यहूदियों ने फिर
से पत्थर उठा लिए **कि** उसे पत्थरवाह **करें**," a finite कि-clause with no purpose-
infinitive construction at all — so treat के लिये as the safer default among the
postposition strategies specifically, not as a translation-independent universal; a
finite कि-clause is a live fourth option (see ἵνα CLAUSES). Apply the same primary/
secondary test either way.
See ἵνα CLAUSES for the fuller breakdown of purpose-clause strategies.

### Indirect discourse

Supplied कि introducing an indirect statement is secondary to the governing verb of
speech/perception, not to the embedded verb.

---

## ἵνα CLAUSES **[hin]**

Checked against all 663 SBLGNT ἵνα occurrences, with a 54-verse stratified sample across
Matthew, Mark, Luke, John, Acts, Romans, 1 Corinthians, 2 Corinthians, and Revelation.
**Cross-checked against two other Hindi NT translations** (HSB — Hindi Standard Bible,
`data/targets/HSB/nt_HSB.tsv`; OHCV — Open Hindi Contemporary Version,
`data/targets/OHCV/OHCV_hindi_20240610.tsv`) to guard against overfitting the whole
document to IRVHin's specific stylistic choices. Result: कि dominates and के लिये +
infinitive is solid across those three translations; two of the other renderings
originally documented here turned out to be IRVHin-specific rather than general Hindi
strategies — see the corrections below. **A spot-check against a 4th translation, GLT
(`data/targets/GLT/nt_GLT.tsv`), shows के लिये + infinitive is not translation-universal
either** — see the के लिये + oblique infinitive entry below.

- **कि** — the default, general-purpose marker, covering purpose, result, *and* plain
  content clauses ("said that...," "wanted that...") without distinction. By far the
  most common rendering, confirmed identically across IRVHin, HSB, and OHCV in every
  verse checked. Example (John 3:16 pattern): "...प्रेम रखा **कि** जो कोई..."
  conjunction primary; verbs/content words align normally.
- **ताकि** — a more explicit "in order that" marker. **Correction:** an earlier version
  of this document claimed ताकि clusters in the epistles; that does not hold up.
  Checking the same verse across translations shows ताकि is often just IRVHin's
  individual word choice where HSB and OHCV both use plain कि instead (Luke 22:30: IRV
  "ताकि," HSB and OHCV both "कि"). Treat कि/ताकि/जिससे as **free stylistic variants of
  the same conjunction, translator-dependent**, not as markers of different Greek
  constructions or genres — do not expect consistency across translations for which one
  appears on a given verse.
- **इसलिए...कि** — a correlative construction where इसलिए ("for this [reason]")
  anticipates the purpose and कि introduces it. **Confirmed robustly**: identical
  इसलिए...कि wording across IRVHin, HSB, and OHCV for Mark 4:21 (translations rarely
  agree word-for-word, so this is a strong signal); **a 4th translation, GLT, also uses
  इसलिए/इसीलिए...कि twice in this same verse** — now confirmed across four independent
  translations, the strongest cross-translation signal in this document. Treat as a
  single primary unit against ἵνα, both words primary.
- **के लिये + oblique infinitive** — a common purpose-infinitive strategy, confirmed
  across IRVHin, HSB, and OHCV for John 6:38 ("पूरी करने के लिये," identical in IRVHin
  and HSB, near-identical in OHCV) and John 10:31 (all three use के लिये here, see को
  correction below): के लिये primary to ἵνα, not secondary to the infinitive. **Not
  translation-universal, though**: GLT renders both of these same verses with a finite
  कि-clause instead of an infinitive at all — John 6:38 "मैं...इसलिए नहीं उतरा हूँ, कि
  अपनी इच्छा को पूरा करूँ" (no के लिये, no infinitive), John 10:31 "...कि उसे पत्थरवाह
  करें." Treat के लिये as the safer default *among the postposition+infinitive
  strategies*, not as the single Hindi-wide answer — a plain finite कि-clause (see कि
  above) is a live fourth option some translations prefer outright.
- **को + oblique infinitive** — **correction:** originally documented as a second
  purpose-infinitive marker (John 10:31 "पथराव करने को"). Checking HSB and OHCV on the
  same verse shows both use "पथराव करने **के लिये**" instead — को here was IRVHin's
  individual choice, not a shared strategy. को *can* mark a purpose infinitive in
  Hindi generally, but के लिये is the safer default among the postposition strategies
  when a translation's practice is unknown; do not expect को on this function elsewhere
  without checking.
- **जिससे** ("by which") — **correction:** originally documented as a marker reserved
  for a secondary/consequential purpose clause layered onto a primary one. Checking the
  same verse (Rom 15:16) across translations disproves the "reserved" framing: HSB uses
  ताकि and OHCV uses कि for the exact same clause IRVHin marks with जिससे. जिससे is just
  one more free variant in the कि/ताकि/जिससे set (see the ताकि correction above), not a
  dedicated grammatical category.

**Negative purpose (ἵνα μή / μήποτε-type "lest")** has a dedicated idiom in the more
literal translations: "**ऐसा न हो कि**" or the shortened "**न हो कि**," confirmed
identically in IRVHin and HSB across Matt 7:6, Luke 14:29, Acts 27:42, and 1 Cor 8:13.
**OHCV frequently drops this idiom** in favor of a bare कि/यदि + negated verb with no
"ऐसा न हो" framing at all (Acts 27:42: IRV/HSB "ऐसा न हो कि," OHCV "कि...न जाए" bare) —
a real translation-style difference (OHCV is the more dynamic/paraphrase-style
translation of the three), not evidence the idiom is optional within a single
translation's own practice. When the idiom is present, both particles (ἵνα + μή) are
primary to it as a single unit, parallel to the emphatic-negation treatment in
NEGATION; when absent, treat the plain negator as the correspondent instead.

No correspondent → NEQ source (only when certain no element expresses purpose/result
force; occasionally the whole purpose/result clause is instead recast as an
independent coordinated main clause with no subordinating marker at all — worth
double-checking against the Greek before defaulting to NEQ in that case).

---

## NEGATION **[hin]**

Confirmed against a broad read of IRVHin (John 1, Romans 1 and 8, and spot checks
across Matthew/Mark/Acts): the नहीं/न split is **not** conditioned by mood the way an
earlier draft of this document assumed. Both particles are attested with plain
indicative forms, including future ("क्यों **न** देगा" — Rom 8:32, "will he not give")
and modal/compound verbs ("**न** कर सकी" — Rom 8:3, "could not do"; "**न** रख छोड़ा" —
Rom 8:32, "did not withhold"). The real split is by **discourse function**:

**Full-corpus token counts (all 27 books each particle appears in): नहीं = 1,611, न =
1,747, मत = 72.** न is not a minor variant of नहीं by frequency — it is in fact
marginally *more* common. Of न's occurrences, roughly 59% are single-न verses (plain
ordinary negation, not a correlative list) and roughly 41% are in verses with 2+ न
tokens (the correlative-list pattern). **Treat नहीं and न as co-equal in raw frequency,
just split across more distinct functions** (plain negator, correlative list,
negative-purpose, emphatic-negation reinforcement — न covers all four; नहीं is
essentially limited to the first) — न is not "the rarer/secondary particle," it simply
does more jobs.

- **नहीं** — the default, general-purpose negator, usable with almost any verb form.
  Typically immediately precedes the finite verb complex (contiguous, unlike French's
  discontinuous ne…pas).
  Example: John 1:10, ἔγνω (negated) → "**नहीं** पहचाना" ("did not recognize"): "नहीं"
  primary 1:1; "पहचाना" primary in its own record.

  **Copula ellipsis after नहीं is a real, recurring IRVHin pattern, but check each
  translation rather than assuming it's Hindi-general.** Predicate-nominal and
  predicate-adjectival clauses in IRVHin regularly drop है/हूँ/हैं when नहीं is present:
  John 1:47 "इसमें कपट **नहीं** [है]," John 1:27 "खोलने के योग्य **नहीं** [हूँ]," Rom 8:1
  "दण्ड की आज्ञा **नहीं** [है]," Rom 8:9 "उसका जन **नहीं** [है]," Rom 8:12 "कर्जदार
  **नहीं** [हैं]." **A 4th translation, GLT, keeps है explicit in both John 1:27 and John
  1:47** ("मैं इतना योग्य भी नहीं **हूँ**"; "जिसमें कोई छल नहीं **है**") — the two verses
  cited above as the flagship illustration — so ellipsis-after-नहीं should be treated as
  a genuine but translation/register-dependent stylistic option, not a default to expect
  across editions. The elided copula, when it does occur and the Greek has an explicit
  εἶναι token, is NEQ per the base copula-ellipsis rule; the ellipsis itself needs no
  special marking. (Even within IRVHin the copula is not always dropped — Rom 8:18
  "कुछ भी नहीं **हैं**" keeps it — so check each verse rather than assuming ellipsis.)

- **न** — has two distinct attested uses, neither conditioned by subjunctive mood:
  1. **Interchangeable literary variant of नहीं** for ordinary negation, confirmed by a
     near-identical clause repeated twice in John 1 with different particles: John 1:31
     "मैं तो उसे पहचानता **न** था" vs. John 1:33 "मैं तो उसे पहचानता **नहीं** था" (both
     "I did not recognize him"). Treat identically to नहीं when it is not part of a
     correlative list.
  2. **The dedicated correlative form for "neither...nor" lists**, aligning **1:1 to each
     Greek οὐδέ/οὔτε** in the list — this is the strongest, most useful correspondence
     for alignment purposes. John 1:13: "**न** तो लहू से, **न** शरीर की इच्छा से, **न**
     मनुष्य की इच्छा से" (οὐκ ἐξ αἱμάτων, οὐδὲ ἐκ θελήματος σαρκός, οὐδὲ ἐκ θελήματος
     ἀνδρός). Rom 8:38–39 has a ten-item list this way ("**न** मृत्यु, **न** जीवन, **न**
     स्वर्गदूत...और **न** कोई और सृष्टि"), each न aligning 1:1 to its corresponding Greek
     οὔτε.
  3. Also appears in negative-purpose clauses ("ऐसा **न** हो कि वे...रौंदें" — Matt 7:6,
     "lest they trample," a μήποτε-type construction) and occasionally in literary
     imperative prohibition ("पवित्र वस्तु कुत्तों को **न** दो" — Matt 7:6, "do not give").

- **मत** — the ordinary colloquial prohibitive, paired with an imperative or the -ना
  infinitive form: "**मत** डर"/"**मत** डरना" (do not fear — Matt 1:20, 10:26, 10:28),
  "**मत** करना" (do not do — Matt 23:3), "दोष **मत** लगाओ" (do not judge — Matt 7:1).
  Primary 1:1 to the Greek prohibitive (μή + imperative or aorist subjunctive).
  **Caution:** मत is homographic with an unrelated noun मत ("opinion, view, vote" — Matt
  23:15 "अपने मत में लाने"); disambiguate by syntactic position (preverbal particle vs.
  object noun), not by string match alone.

### Compound negation

अभी तक confirmed as part of "not yet" constructions and कभी नहीं ("never," lit.
"ever not," John 1:18 "किसी ने **कभी नहीं** देखा" — "no one has ever seen") and फिर
कभी ("again/ever again") are both attested with reasonable frequency across the corpus
(13 and 12 verses respectively in a full-NT scan). Align all content words as primary to
the single Greek compound-negation token (οὐδέποτε, οὐκέτι, οὔπω), per the base
guidelines' general pattern (§9.7.2 in `alignment-principles-nt.md`).

### Emphatic negation (οὐ μή)

Checked against all 85 οὐ μή occurrences in SBLGNT (`data/sources/SBLGNT.tsv`) and a
spread of the corresponding IRVHin verses across Matthew, Mark, John, Hebrews, and
Revelation. **IRVHin has no single dedicated emphatic-negation construction** — it uses
one of at least five reinforcement strategies layered onto ordinary न/नहीं, chosen for
the specific semantic flavor of the emphasis, or sometimes no reinforcement at all:

- **कभी / कदापि ("ever") + न or नहीं** — the most common strategy, for a "never"
  reading. Matt 5:20 "प्रवेश करने **न** पाओगे" ("shall by no means enter"), Matt 24:35 /
  Mark 13:31 (identical synoptic-parallel wording) "मेरे शब्द **कभी न** टलेंगे" ("my
  words will never pass away"), John 6:37 "मैं **कभी न** निकालूँगा" ("I will never cast
  out"), John 10:28 "वे **कभी नाश नहीं** होंगी" ("they will never perish" — नहीं here,
  not न, confirming the two particles are freely interchangeable in this slot too).
  **Correction:** an earlier draft claimed Revelation favors the more literary/formal
  कदापि over कभी, based on Rev 18:14 "**फिर कदापि न** मिलेंगे." Checking HSB on the same
  verse disproves the genre claim — HSB uses the ordinary "अब फिर कभी नहीं मिलेंगी"
  there, and separately uses कदापि in *Matthew* (24:35: "मेरे वचन **कदापि** न टलेंगे,"
  where IRVHin instead has कभी). कदापि is a real, recurring literary synonym for कभी,
  but it is not tied to any particular book or genre — treat कभी/कदापि as free
  stylistic variants throughout, the same conclusion reached for कि/ताकि/जिससे in
  ἵνα CLAUSES.
- **अनन्तकाल तक ("for eternity/forever") + न** — a distinct, more durative-sounding
  strategy that clusters specifically in John's "whoever believes/drinks..." formula
  sayings: John 4:14 "**अनन्तकाल तक** प्यासा **न** होगा" ("will never be thirsty
  again"), John 8:51 "**अनन्तकाल तक** मृत्यु को **न** देखेगा" ("will never see death"),
  John 8:52 (same pericope, same phrasing), John 11:26 "**अनन्तकाल तक न** मरेगा" ("will
  never die"). **Cross-checked and confirmed**: HSB independently uses अनंतकाल तक on
  all four of these same verses (sometimes stacking it with कभी for extra emphasis,
  "अनंतकाल तक कभी नहीं मरेगा," John 11:26) — two independent literal translations
  converging on the identical durative marker for this Johannine formula is a real,
  reliable signal, not an IRVHin idiosyncrasy. OHCV, however, restructures away from it
  every time (John 11:26 "उसकी मृत्यु कभी न होगी," no अनंतकाल तक at all) — expect this
  marker specifically in more literal/formal translations, not dynamic ones.
- **किसी रीति से / किसी प्रकार से ("in any way, by any means") + न** — a modal rather
  than temporal reinforcement, closer to English "by no means." Rev 21:27 "किसी रीति
  से प्रवेश **न** करेगा" ("will by no means enter"). **Correction:** this is real (OHCV
  independently uses "किसी भी रीति से" for Matt 5:20, a different verse), but checking
  HSB and OHCV on Rev 21:27 itself shows neither uses it there — both instead restructure
  the whole verse as a correlative negated-subject list ("**न** कोई अपवित्र वस्तु और
  **न ही** घृणित...वस्तु," "neither anything impure nor anything detestable...") rather
  than reinforcing the verb. So किसी (भी) रीति से is a real, attested Hindi strategy for
  emphatic negation, but it was IRVHin's specific choice for Rev 21:27 — do not assume
  it is the standard rendering for that verse across translations.
- **निश्चय ही ("certainly/surely") + negator** — not attested in IRVHin/HSB/OHCV, but a
  consistent house-style pattern in a 4th translation, GLT: stacked on top of नहीं or
  अनन्तकाल तक in essentially every οὐ μή instance checked (John 6:37, 8:51, 8:52, 10:28,
  11:26). Five independent verses converging on the same reinforcement word within one
  translation is a real, recurring strategy for that edition — check whether the
  translation in use follows this pattern rather than assuming it applies universally.
- **Bare न or नहीं, no reinforcement at all** — attested within the very same verse as
  a reinforced instance, showing reinforcement is a translator choice, not a rule: John
  10:28's second clause ("कोई उन्हें मेरे हाथ से छीन **न** लेगा," "no one will snatch
  them out of my hand") has no reinforcement, immediately following the कभी नहीं
  clause earlier in the same verse.

**Alignment treatment:** both Greek particles (οὐ + μή) are primary in a single record
against whatever Hindi words carry the emphasis — the negator (न/नहीं) plus any
reinforcing word (कभी/कदापि/अनन्तकाल तक/किसी रीति से/निश्चय ही) when present. When no
reinforcement is present, both particles are still primary to the ordinary negator
alone — the absolute force is understood from context, and this is a legitimate,
attested translation choice, not a gap to fill in.

**False-friend trap — जब तक...न ("until...not"):** Hindi idiomatically expresses "until
X happens" as "जब तक X **न** हो" (literally "as long as X does not happen, then...") —
confirmed in 78 IRVHin verses. This न has **no Greek source correspondent** when the
Greek ἕως/ἄχρι clause carries no negative particle of its own — it is purely a
target-grammar requirement of the "until" frame and should be NEQ target, not aligned to
any Greek particle. Critically, several οὐ μή verses contain *both* this idiomatic न
*and* a separate, genuine οὐ μή rendering in the same sentence — do not conflate them.
Matt 5:18: "जब तक आकाश और पृथ्वी टल **न** जाएँ" (idiomatic "until," न → NEQ target) "तब
तक...**नहीं** टलेगा" (the actual οὐ μὴ παρέλθῃ rendering, नहीं primary). Matt 5:26: "जब
तक तू पाई-पाई चुका **न** दे" (idiomatic "until," न → NEQ target) "तब तक वहाँ से
छूटने **न** पाएगा" (the actual οὐ μὴ ἐξέλθῃς rendering, न primary). In both verses the
Greek ἕως clause itself carries no negation — only the emphatic main clause does.

**Cross-checked**: HSB uses the identical जब तक...न idiom in both verses (न jaeँ, न de)
— confirmed as a real, shared literal-translation strategy, not an IRVHin one-off.
OHCV, however, **avoids the trap entirely** by restructuring Matt 5:18 as a positive
"as long as X exists" clause ("जब तक आकाश और पृथ्वी **अस्तित्व में हैं**," no negation
at all in the temporal clause) — a good illustration that this false-friend trap is
specific to translations that keep the literal "until...not" calque; a more dynamic
translation may sidestep it structurally. Check which style of translation you are
working with before assuming the trap applies.

---

## PARTICIPIAL CONSTRUCTIONS **[hin]**

### Adverbial (circumstantial) — the -कर conjunctive participle

The verb stem + कर suffix (निकलकर "having gone out," झुककर "having bowed," आकर "having
come" — all attested in Mark 1:2–9) renders a Greek circumstantial (typically aorist)
participle directly, primary alone. Because -कर already means "having done X," no
supplied conjunction is needed the way English needs "after" or Portuguese needs "depois
de" — this is a cleaner match to the Greek construction than most target languages get.

Example (Mark 1:5): a circumstantial participle rendered "निकलकर" ("having gone out") —
primary 1:1, no secondary conjunction.

If the translation instead supplies an explicit conjunction alongside a non-कर verb form
(e.g. "जब...तो"), treat the conjunction as secondary to the verb, per the general pattern
in the base guidelines.

### Genitive absolute

Align each element to its correspondent; any supplied conjunction/adverb is secondary to
the participle; supplied subject is secondary if introducing/switching subject (see
TOKEN ROLES).

### Substantive — जो pattern vs. वाला pattern vs. bare-noun pattern

Checked systematically: every SBLGNT `article + participle` sequence (1,339 instances
total, `morph[4]=='P'`) was enumerated, and a stratified 48-verse sample spanning
Matthew, Mark, Luke, John, Acts, Romans, 1 Corinthians, and Revelation was cross-checked
against IRVHin, **then re-checked against HSB and OHCV specifically to test whether the
जो/वाला split generalizes or is an IRVHin artifact.** One major claim did not survive
this check and has been corrected below (the "coming one" epithet); the rest held up
reasonably well, with OHCV showing a distinct, translation-wide preference worth
flagging on its own.

**जो + finite verb is a highly productive strategy**, used for both generic and specific
referents alike, including cases that look as generic as anything gets: "जिसके कान हों
वह सुन ले" (ὁ ἔχων ὦτα, "he who has ears, let him hear," Matt 13:9 — identical जो-based
wording in all three translations) and Paul's "जो किसी दिन को मानता है...जो खाता
है...जो नहीं खाता" (Rom 14:6 — three generic-conditional participles, all जो in all
three translations, none वाला). **Correction — not clearly the "majority default" over
वाला**: an earlier version of this document called जो "the true majority default." A
fresh, non-overlapping 25-verse sample (across Thessalonians, 1 Cor, Acts, Matthew,
Mark, Luke, John, Galatians, Philippians, Hebrews, James, 2 Peter, Revelation) found जो
and वाला running almost exactly even, 8 instances each. Treat the two as roughly
co-equal, general-purpose strategies rather than जो-as-default/वाला-as-exception — जो
still covers a broader range of referent types (including the generic/conditional cases
above, which वाला rarely takes), but "majority" overstated the actual balance.

**वाला is used when the participle compresses cleanly into a single stable, lexicalized
agent-noun or role label.** The strongest, most reliable confirmations — identical or
near-identical वाला across all three translations — are role/occupation labels:
"**सतानेवालों**" (persecutors, Rom 12:14), "**रहनेवाले**" (dwellers/inhabitants, Rev
13:8), "**चाहनेवाले**/**दौड़नेवाले**/**दया करनेवाले**" (the one who wills/runs/shows
mercy, Rom 9:16, confirmed in IRVHin and HSB; OHCV drops the participial construction
entirely for an abstract-noun paraphrase here, its general tendency — see below).

**Correction — "the coming one" is not a stable cross-translation epithet.** An earlier
draft of this document treated "**आनेवाला**" as a fixed formulaic rendering of ὁ
ἐρχόμενος across Matt 3:11, Mark 1:7, John 1:15/27/30, and Rev 22:7. Checking all five
verses across all three translations disproves this: **OHCV never uses वाला for this
motif in any of the five instances** — it consistently uses जो + a plain present/future
verb instead ("वह, जो मेरे बाद आ रहे हैं," "who is coming after me"), sometimes with a
supplied head noun ("एक ऐसा व्यक्ति आएगा, जो...," "such a person will come, who...").
IRVHin and HSB each use वाला in only 3 of the 5 instances, and not even the *same*
three — both freely alternate between वाला and जो+plain-verb for this exact same
recurring Greek phrase within their own text. **Do not treat वाला as the expected or
default rendering for "the coming one" or any other single recurring epithet without
checking the specific translation in hand** — this is squarely a translation-style
effect, not a fixed feature of the Hindi language or the Bible-translation tradition as
a whole.

**A specific individual can still get वाला** — "**पकड़वानेवाले**" (the betrayer, Judas,
Matt 26:25) is confirmed in IRVHin and HSB (both specific, not generic — directly
contradicting a specific/generic split), but OHCV instead uses जो + relative clause
("यहूदाह...जो...धोखा कर रहा था"). So even वाला's most solid category (a specific named
individual acting as a stable narrative role) shows one of three translations departing
from it — 2-of-3 agreement is still meaningful signal, just not universal.

**A fourth strategy: a plain, already-lexicalized noun, bypassing जो/वाला entirely.**
Where Hindi already has an ordinary noun for a role, HSB and OHCV often prefer it over
either participial strategy, even when IRVHin constructs a वाला-participle: Mark 13:14's
parenthetical aside "let the reader understand" is "**पढ़नेवाला** समझ ले" in IRVHin but
"**पाठक** समझ ले" (पाठक, "reader," a plain noun) in both HSB and OHCV; Matt 13:18's "the
sower's parable" is "**बोनेवाले** का दृष्टान्त" in IRVHin and HSB but "**किसान** का
दृष्टान्त" (किसान, "farmer") in OHCV. Check whether a natural lexicalized noun exists
for the role before assuming a participial construction is required at all.

**वाला does not track genericity** — it tracks whether Hindi has (or a specific
translator reached for) a ready single-word agentive compound for that verb, and this
varies by translation. Light-verb-based participles (जय पाना "to overcome," प्रेम रखना
"to love") more often resist वाला-compounding and get जो instead, even in a recurring
formulaic refrain: Revelation's "he who overcomes" is rendered "**जो** जय पाए," and this
one *is* robustly confirmed across all three translations for Rev 3:21 (IRVHin, HSB,
and OHCV all use जो विजयी/जय पाए, never a वाला compound) — a genuinely stable
cross-translation finding, unlike the "coming one" case above. **The practical
takeaway: check each specific recurring phrase against more than one translation before
trusting a formulaic rendering — some hold up (जो जय पाए, सतानेवाले, रहनेवाले), others
turn out to be one translation's individual choice (आनेवाला, पकड़वानेवाला, पढ़नेवाला).**

**A general translation-style pattern worth naming:** across every case checked, OHCV
(the more dynamic/paraphrase-style of the three) shows a consistent pull away from both
जो-with-complex-clause and वाला-participles, toward either a plain lexicalized noun
(पाठक, किसान), an appositive gloss (अर्थात्, for John Mark's "who is called Mark"), or a
fuller paraphrase that drops the participial structure altogether (Rom 9:16's "the one
who wills...runs...shows mercy" triad becomes "यह मनुष्य की इच्छा...पर नहीं...परमेश्वर
की कृपादृष्टि पर निर्भर है," no participles at all). If working from a more literal
translation, expect जो/वाला choices to be more literal-source-shaped and more internally
variable verse-to-verse; if working from a dynamic translation, expect more restructuring
away from participial forms generally.

जो + finite verb — secondary जो, the Hindi counterpart to Indonesian "yang" and
French/Spanish/Portuguese "qui/que." Any generic head noun explicitly supplied ("कोई,"
"व्यक्ति," "लोग") is likewise secondary unless a distinct Greek article token
independently earns it a primary link (see DEFINITENESS AND ARTICLES).

Example (John 3:16 pattern): ὁ πιστεύων-type substantive participle → "जो...विश्वास
करे" ("whoever believes"): source=[participle], target=["जो", "विश्वास", "करे"] —
primary: "विश्वास", "करे" (light verb, both primary per LIGHT AND VECTOR VERBS);
secondary: "जो".

वाला/वाली/वाले — treat verb-stem + वाला as one fused record, both primary (parallel to
the fused-clitic treatment used in Indonesian, though the underlying mechanism differs)
— no separate secondary token is needed the way जो requires one. This pattern also
extends to non-human/abstract heads, not just human agents: "**आनेवाला** क्रोध" (the
coming wrath, Matt 3:7).

Example: ὁ βαπτίζων-type construction → "बपतिस्मा देनेवाला": source=[participle],
target=["देनेवाला"] — primary (the light-verb noun बपतिस्मा gets its own separate
record per LIGHT AND VECTOR VERBS).

**A third, minority strategy: no जो/वाला at all.** Some articular participles are
rendered as an ordinary finite-verb clause with the article's substantive force simply
absorbed into normal sentence syntax (Luke 16:15 "अपने आपको धर्मी ठहराते हो" for οἱ
δικαιοῦντες, "you who justify yourselves" — rendered as a plain second-person verb, no
relativizer at all), or as a bare participial adjective directly modifying its head
noun with neither जो nor वाला (John 5:35 "**जलता और चमकता हुआ** दीपक," "a burning and
shining lamp"; John 6:12 "**बचे हुए** टुकड़े," "leftover/remaining pieces" for τὰ
περισσεύσαντα). Both of these still align cleanly at the token level — the participle's
Hindi correspondent is primary either way — but expect this bare-adjective option to
show up, particularly for attributive (not substantive) participle uses.

### Discourse particle adjacent to a participle

A conjunction/particle near a participle with no correspondent → NEQ source, only when
certain no element in the surrounding clause carries its force.

---

## COMPARATIVE AND SUPERLATIVE **[hin]**

Previously a placeholder assumed to parallel Portuguese's analytic "mais + base"
pattern with no real Hindi-specific investigation. A first corpus pass (12 of 300
SBLGNT comparative-adjective forms, `morph` A-*-C, sampled against IRVHin) shows the
load-bearing element is **से**, a postposition marking the standard of comparison
("than X") — secondary to the noun/pronoun it governs, parallel to how genitive-case
postpositions are treated elsewhere in this document:

- **X से + बड़ा/अधिक/दृढ़-type adjective** — the dominant analytic pattern: "भविष्यद्वक्ता
  **से** भी बड़े" (Matt 11:9/Luke 7:26, "greater than a prophet"), "अपने **से** किसी बड़े"
  (Heb 6:16, "someone greater than himself"), "उस**से**...बड़ा" (1 John 4:4). से secondary
  to the noun it marks; the comparative adjective is primary, both words primary to the
  comparative-morphology-bearing Greek adjective as a whole.
- **X से + बढ़कर** (participial, "exceeding X") — a second live pattern, corpus-confirmed
  independently in IRVHin itself (से बढ़कर, 27 occurrences NT-wide) and in GLT (Mark 1:7
  "वह मुझ से **बढ़कर** शक्तिशाली है," "he is mightier than I"). से अधिक (analytic) is more
  frequent overall (30 occurrences) but से बढ़कर is not a minor variant — treat both as
  live options and check which a given verse/translation uses; same primary/secondary
  split (से secondary to the noun; बढ़कर/अधिक carries the comparative sense alongside the
  adjective, both primary).

Superlatives were not separately investigated in this pass — flag as still open.

## CONDITIONAL **[hin]**

Previously a placeholder assuming यदि/अगर...तो parallels εἰ/ἐάν...(apodosis) with no
Hindi-specific investigation. A first corpus pass (12 of 833 εἰ/ἐάν instances) confirms
the basic structure but surfaces two real Hindi-specific wrinkles:

- **यदि...तो (ordinary real/hypothetical conditional)** — the dominant pattern,
  confirming the base assumption: यदि (or अगर) marks the protasis, तो the apodosis.
  तो is NEQ when supplied with no Greek apodotic particle correspondent, or primary if
  one exists (ἄρα, οὖν in apodosis position) — apply the same test as other
  supplied-conjunction cases in this document.
- **Exceptive εἰ μή → केवल + relative clause**, not a literal "if not": 1 John 5:5
  "संसार पर जय पानेवाला कौन है? **केवल** वह **जिसका** विश्वास है..." ("who overcomes the
  world? Only the one who believes..."). केवल ("only") and the जिसका-relative jointly
  correspond to εἰ μή — treat as a unit primary to εἰ μή, not as εἰ (NEQ/secondary) + μή
  (negation) separately.
- **Indirect-question εἰ ("whether") → कि...है कि नहीं**: Mark 3:2 "देखें कि वह सब्त के
  दिन चंगा करता है **कि नहीं**" ("[they watched] whether he would heal on the Sabbath").
  This is a distinct function from the ordinary conditional and should not be forced
  into the यदि...तो template — कि नहीं ("or not") as a unit corresponds to the
  indirect-question εἰ.

## Shared sections (expected to import largely unchanged from English)

Pending native-speaker review, the following blocks are not expected to need
Hindi-specific mechanics beyond example substitution — Hindi's grammar for these
constructions parallels English/Portuguese closely:

- **αὐτός (AUTOS)** — third-person pronoun uses render via वह/उसने/उसका/उसे etc.
  following the ordinary case-marking rules above (ने/को/का as applicable); intensive
  use ("himself") via स्वयं/खुद; reflexive similarly. **A 10-instance corpus sample
  confirms the ordinary third-person-pronoun majority use** (उसके, उसका, उसे, तुम्हारा,
  etc. inflecting normally, no complication found) — but the sample happened not to
  catch any intensive or reflexive instance, so that specific sub-case remains an
  actual gap, not just an unconfirmed assumption. Confirm with native speaker.
- **ὅτι (HOTI)** — कि serves both the conjunction and (with punctuation/quotation marks)
  recitativum functions, directly parallel to ὅτι. **Confirmed at corpus scale** (12 of
  1,294 ὅτι instances sampled): कि dominates both functions with no separate dedicated
  recitativum marker found. See CONJUNCTIONS AND PARTICLES above for the disambiguation
  test.

---

## Register: confirmed by corpus scan **[hin]**

IRVHin's vocabulary is a genuine blend, not uniformly Sanskritized (shuddh Hindi): common
nouns skew toward the everyday Hindustani/Persian-Urdu layer (गवाही "testimony/witnessing"
appears 118 times in the NT vs. साक्षी, the Sanskrit tatsama equivalent, only 5 times),
while abstract theological and doctrinal vocabulary is heavily Sanskrit tatsama,
especially in the epistles. A side-by-side read of John 1 (narrative) against Romans 1
and 8 (doctrinal) shows a real density difference: Romans is saturated with tatsama
compounds largely absent from John's narrative register (अभक्ति, अधर्म, धार्मिकता,
अविनाशी, नाशवान, सृष्टि, स्वतंत्र, आध्यात्मिक, दासत्व, प्रतीक्षा — none of these appear in
John 1). **Practical implication:** expect the semantic-similarity scorer
(`refine/semantic.py`, LaBSE) to behave differently by genre — epistle vocabulary is more
likely to be underrepresented in LaBSE's Hindi training data than Gospel-narrative
vocabulary. If `score-alignment` shows a genre-correlated pattern in `semantic_low_sim`
counts (systematically worse in Romans/Hebrews/epistles than in the Gospels), that is
this register effect, not a real alignment-quality problem — worth calibrating
`--semantic-threshold` per corpus section rather than assuming one global value, or
flagging it for the native-speaker reviewer rather than auto-retrying.

## Cross-translation methodology note

Everything in NEGATION, ἵνα CLAUSES, PASSIVE VOICE, and PARTICIPIAL CONSTRUCTIONS was
originally derived from IRVHin alone, then deliberately re-checked against two other
Hindi NT translations — HSB (`data/targets/HSB/nt_HSB.tsv`) and OHCV
(`data/targets/OHCV/OHCV_hindi_20240610.tsv`) — specifically to catch claims that were
really just IRVHin's individual stylistic choices dressed up as general Hindi grammar.
That check changed real conclusions, not just added caveats: the "coming one" वाला
epithet and the Matt 11:27 active-voice-conversion example were both overfit to IRVHin
and have been corrected; ताकि/जिससे were reclassified from "distinct purpose markers"
to "free stylistic variants of कि"; को-as-purpose-infinitive-marker and किसी रीति से
were downgraded from "a strategy" to "an attested but translation-specific choice."
Meanwhile other findings (लिखा है for γέγραπται, खुलना for ἀνοίγω-passive, बपतिस्मा
लेना for baptism, इसलिए...कि, जो जय पाए in Revelation, सतानेवाले/रहनेवाले) came back
*more* confident, having survived word-for-word or near-word-for-word agreement across
independent translations. **If this document is extended to a fourth phenomenon not yet
covered, apply the same discipline**: derive from IRVHin, then check at least one other
translation on the same verses before writing a claim as general Hindi grammar rather
than "this is what IRVHin does here."

**A 4th translation, GLT** (`data/targets/GLT/nt_GLT.tsv`, unfoldingWord Gateway Literal
Translation Hindi), was spot-checked broadly across every major section above.
Coverage caveat: GLT's TSV covers only Mark, Luke, John, 1–2 Corinthians, and the
shorter epistles — it has no Matthew, Acts, Romans, Galatians, Hebrews, or Revelation,
so several of this document's anchor verses could not be re-checked against it. Where
GLT was checkable, it mostly reinforced the three-way findings above (ने ergative,
न...न...न correlative, अनन्तकाल तक, इसलिए...कि now confirmed across all four), but it
broke two claims that had been called "robust across all three translations" — के लिये
+ infinitive for ἵνα (John 6:38, John 10:31: GLT uses a finite कि-clause instead) and
copula ellipsis after नहीं as the expected default (John 1:27, 1:47: GLT keeps है) —
both now corrected above to scope the claim to the three translations actually checked.
It also surfaced two additions (खाना as a light-verb support verb, निश्चय ही as an
emphatic-negation reinforcement) and several single-instance observations not yet
folded into the document proper — see the open questions below.

**A subsequent, IRVHin-only corpus-scale re-verification pass** (not translation-count
comparison this time, but full-corpus joins/counts against SBLGNT.tsv, to check claims
against real frequency data rather than a handful of anchor verses) covered every
section of this document. It resolved the COMPARATIVE gap (से बढ़कर confirmed as
IRVHin-native, 27 occurrences, not GLT-specific) and wrote real content for COMPARATIVE
and CONDITIONAL for the first time; it softened two "majority/dominant" claims that
frequency counts didn't support as strongly as stated (न vs. नहीं: 1,747 vs. 1,611
tokens, not नहीं-dominant; जो vs. वाला: 8-8 in a fresh 25-verse sample, not जो-dominant);
it qualified passive Strategy 1's "single most common" claim as genre-conditioned rather
than a flat ranking; and it added a third passive auxiliary (ठहरना), a δέ-variability
note, and resolved the μὴ γένοιτο idiom placeholder with real data (12/13 SBLGNT
instances → कदापि नहीं). **The lesson for any future extension of this document**: even
claims backed by a real cross-translation check can still overstate frequency/dominance
if the underlying sample was small — a corpus-scale count is worth running before
calling something "the default" or "the most common," not just before generalizing
across translations.

## Open questions for native-speaker review

- Confirm whether को-as-DOM is applied consistently enough across IRVHin, HSB, and OHCV
  to rely on the secondary-not-NEQ rule without verse-by-verse judgment calls.
- The जो-vs-वाला split has now been checked against a 48-verse stratified sample across
  eight books and cross-checked against two further translations (see PARTICIPIAL
  CONSTRUCTIONS) — the remaining open question is finer-grained: for the small set of
  role-labels that DO hold up across all three translations (सतानेवाले, रहनेवाले, जो जय
  पाए), is there a reliable *predictive* rule for which verbs join that stable set, or
  is it genuinely lexeme-by-lexeme convention that a native speaker would need to
  confirm case by case?
- Confirm the semantic-scorer register effect described earlier once real
  score-alignment runs are available for an IRVHin epistle chapter.
- **Resolved by the follow-up corpus-scale pass** (previously listed here as
  single-instance GLT observations): the COMPARATIVE gap is resolved — से बढ़कर turned
  out to be an IRVHin-native pattern (27 corpus-wide occurrences), not GLT-specific, and
  both COMPARATIVE AND SUPERLATIVE and CONDITIONAL now have real sections above instead
  of being unchecked eng.py-import placeholders. ठहरना as a passive-naming auxiliary is
  also resolved — a 2nd corpus pass independently found it twice more (James 2:24,
  2:25), now documented as a 3rd Strategy-3 auxiliary in PASSIVE VOICE.
- **Still open, single-instance, needs a native speaker or a further targeted look**:
  (1) John 3:16's Greek has both ὥστε (result) and ἵνα (purpose); GLT is the only one of
  the four translations to mark them with two distinct Hindi conjunctions (कि for ὥστε,
  ताकि for ἵνα) rather than collapsing both under one कि — worth checking whether this
  generalizes as a useful disambiguation signal. (2) A possible ने-drop inconsistency:
  Mark 1:5's plural subject before a perfective transitive verb has no ने ("यरूशलेम के
  सब रहनेवाले...उससे बपतिस्मा लिया"), while Mark 1:9's singular subject in the identical
  construction does ("उसने...बपतिस्मा लिया") — may be a genuine grammatical wrinkle
  (register, or ergative marking sensitivity to the specific verb/subject type) rather
  than free variation; needs a native speaker's opinion rather than being written into
  ERGATIVE ने as a rule.
- **New from the wider corpus-scale re-verification pass**: (3) AUTOS's intensive/
  reflexive sub-case (स्वयं/खुद) remains genuinely unchecked against real text — the
  corpus sample that confirmed the ordinary-pronoun majority use happened not to catch
  any intensive/reflexive instance. (4) COMPARATIVE's superlative constructions were not
  investigated in the corpus pass that resolved the comparative side — still open.
  (5) Splitting को's 2,690 raw NT-wide tokens by function (dative / DOM / experiencer /
  purpose-infinitive) would need real token-level alignment data, not word-counting, to
  do reliably — flagged for whenever enough scored IRVHin alignment data exists to check
  against. (6) ही/तो/भी are pervasive Hindi discourse particles with weak/variable Greek
  triggers (γε, emphatic καί, topic-shift) that CONJUNCTIONS AND PARTICLES doesn't cover
  at all — a real gap, not yet investigated at corpus scale.
