# Alignment Principles — Hindi (hin), Old Testament

Guidelines used by `refine-alignment` when aligning the Indian Revised Version Hindi
(IRVHin) against the Hebrew Old Testament (MACULA Hebrew / Westminster Leningrad Codex)
source.

Sections marked **[hin]** contain Hindi-specific rules or examples. Unmarked sections
follow the shared structural conventions of the English guidelines
(`alignment-principles-ot.md` and `prompt/ot/eng.py`).

**Draft status — spot-checked against `ot_IRVHin.tsv`, not yet cross-translation
verified or reviewed by a native speaker.** This document was seeded by carrying over
the Hindi-grammar findings already confirmed in `alignment-principles-nt.hin.md`
(cross-checked there against IRVHin, HSB, and OHCV for the New Testament) and
re-expressing them against Hebrew source structure instead of Greek. A first pass of
spot-checking against `WLCM.tsv` joined to `ot_IRVHin.tsv` (roughly 15 verses: Genesis
1–2, 3:1, 8:12, 8:21, 9:11, 11:30, 21:5, Joshua 1:1, Psalm 23:1, Isaiah 53:5) confirmed
most of the carried-over Hindi-grammar claims and surfaced two findings not present in
the NT document at all (the objective-genitive-with-light-verb rule for direct objects,
and reflexive अपना for subject-coreferent possessive suffixes). Sections below are
marked **CONFIRMED** (attested in the spot-check), **HYPOTHESIS** (carried over
unchecked), or **NEW** (found only in the OT spot-check). No full-corpus check and no
cross-translation check (against GST, GLT, or another Hindi OT) has been done yet — see
the Cross-translation methodology note at the end.

Source files (to be created): `src/text_align/refine/prompt/ot/hin.py`,
`src/text_align/refine/prompt/ot/eng.py`

**Key differences from OT English and OT Indonesian:**

- **CONFIRMED.** Like Indonesian, no native definite/indefinite article — but unlike
  Indonesian, Hindi has grammatical gender and a genitive postposition (का/की/के) that
  inflects for the gender/number/case of the *possessed* noun, not the possessor.
  Spot-check: real Hebrew construct chains (עֶבֶד יְהוָה "servant of the LORD" → यहोवा
  के दास; בִּן נוּן "son of Nun" → नून का पुत्र) render with का/की/के agreeing with the
  possessed noun, exactly as hypothesized (see CONSTRUCT CHAINS AND GENITIVE
  POSTPOSITION).
- **CONFIRMED.** Split-ergative case marking: ने marks a transitive subject in the
  perfective aspect, with no Hebrew trigger at all (Hebrew has no ergativity). Fired
  reliably in every checked verse with a perfective transitive subject (परमेश्वर ने
  सृष्टि की, आदम ने कहा, यहोवा ने...कहा). Secondary to the noun it marks, never NEQ
  (see ERGATIVE ने AND ACCUSATIVE/DATIVE को).
- **NEW finding, not in the NT document.** Direct objects of Hebrew verbs rendered as
  Hindi light verbs (सृष्टि करना "create," रचना करना "create/form," नाश करना "destroy")
  consistently take an objective genitive का/की on the light-verb noun rather than DOM
  को — confirmed 4+ times (Gen 1:1, 1:27, 9:11). This sharpens the NT document's
  "अपने लोगों का उद्धार करेगा"-style note (there illustrated with one example) into a
  systematic rule for this config: expect का/की, not को, whenever the direct object of
  a Hebrew transitive verb lands as the logical object of a light-verb noun.
- Finite verbs are almost always periphrastic (participle + copula) as the *default*
  paradigm, not optional style — directly relevant to how Hebrew's own periphrastic
  participle + הָיָה construction (§12.7 of the base OT document) renders: expect
  Hindi's own periphrasis to layer onto or replace Hebrew's, not necessarily to mirror
  it one-for-one. **HYPOTHESIS** — not isolated in the spot-check yet.
- **CONFIRMED (transfers cleanly).** Light verbs (noun + करना/होना/देना/रखना) are
  pervasive for Hebrew verbs exactly as for Greek — בָּרָא "create" → सृष्टि की / रचना
  की, both content words primary N:1 against the single Hebrew token. Vector verbs
  (V1 + bleached V2) not yet isolated in the spot-check but expected to hold the same
  way.
- Substantive participles: जो is expected to be the majority default for Hebrew
  substantive participles too (parallel to its NT behavior), with वाला reserved for
  lexicalized role-labels — but this needs checking against actual Hebrew participle
  constructions (§12.7 of the base document), which differ structurally from Greek
  articular participles. **HYPOTHESIS** — not isolated in the spot-check.
- **CONFIRMED for 2 of 8 strategies, both with strong evidence.** Hebrew's own passive
  stems (Niphal, Pual, Hophal — base document §12.4) do map onto the same
  multi-strategy inventory documented for Greek NT passives. Isaiah 53:5 alone attests
  Strategy 1 (periphrastic जाना: कुचला गया "was crushed," घायल किया गया "was wounded")
  and Strategy 3 (adjectival resultative: **चंगे हो जाएँ** for נִרְפָּא "healed" — the
  identical चंगा+होना mapping the NT document found for ἰαθήσεται, a strong
  cross-testament confirmation). Genesis 21:5's הִוָּלֶד ("was born") → उत्पन्न हुआ is
  also Strategy 3. Genesis 2:23's יִקָּרֵא ("shall be called") → नाम...होगा confirms
  Strategy 8 (naming/equational conversion, verb dropped entirely). The remaining five
  strategies are still HYPOTHESIS.
- **CONFIRMED.** नहीं/न/मत negation split by discourse function (not mood) carries over
  unchanged — both नहीं and न attested for indicative/future negation in the spot-check
  (मुझे कुछ घटी न होगी; यहोवा नहीं बरसाया). Hebrew's own "no longer" construction
  (לֹא...עוֹד) **is confirmed discontinuous** in 3 of 4 checked instances (फिर...न with
  material intervening — Gen 8:12, 8:21, 9:11×2), directly paralleling the NT
  document's οὐκέτι/μηκέτι finding and the OT Indonesian document's לֹא...עוֹד finding.
  See NEGATION.
- The -कर conjunctive participle (verb stem + कर, e.g. निकलकर "having gone out") —
  **HYPOTHESIS**, no clean instance isolated in the spot-check; still needs checking
  against Hebrew's waw-consecutive chain or infinitive construct.
- Hebrew word-part tokenization (MACULA splits prepositions, articles, waw, and
  pronominal suffixes into separate BCVWP tokens) has no Greek NT parallel. **NEW
  finding**: possessive pronominal suffixes render as ordinary free possessive pronouns
  (मेरा, उसकी) as hypothesized — *except* when the possessor is coreferential with the
  clause subject, where IRVHin uses the reflexive अपना/अपने instead (Gen 1:27
  בְּצַלְמוֹ → "अपने स्वरूप में," not "उसके स्वरूप में"). This reflexive-vs-ordinary
  distinction was not anticipated in the original draft or in the NT document — see
  PRONOMINAL SUFFIXES.

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

Word-part present → align Hindi correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main
token, per §6 of the base OT document.

---

## TOKEN ROLES **[hin]**

- **primary** — direct lexical or semantic connection to the Hebrew token
- **secondary** — exists only because of grammatical features of the Hebrew token
  (construct relation, verbal morphology, merged definiteness), or because Hindi's own
  grammar obligatorily requires a word with no separate Hebrew word behind it
- correspondence to a different Hebrew token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

**Common secondary cases (carried from the NT Hindi document — Hindi-grammar-level, not
Greek-specific):**

- **Subject pronoun** — Hindi verbs agree in gender/number but not richly in person;
  pro-drop is discourse-driven (topic continuity), not grammar-guaranteed. Supplied on a
  new/switched subject → secondary. Dropped for topic continuity → none expected.
  Expected to apply identically against Hebrew waw-consecutive narrative chains, which
  frequently switch or continue subjects clause by clause — needs checking.

- **Periphrastic finite verb (participle + copula)** — the default paradigm for present,
  imperfect, and several other tenses. Participle primary; copula secondary.
  Example (hypothesized, unchecked): a Hebrew participle rendered "करता है" — "करता"
  primary; "है" secondary.

- **Light verb (noun/adjective + करना/होना/देना/रखना)** — a Sanskrit/Persian/Arabic noun
  supplies the verbal slot for a Hebrew verb with no simple Hindi verbal root. Both words
  primary, N:1 against the single Hebrew token.

- **Vector/compound verb (V1 + V2)** — V1 primary; V2 secondary aspectual marker (देना,
  लेना, जाना, डालना, बैठना, etc.).

- **Conjunctive/perfective participle (verb stem + कर)** — primary alone; no supplied
  conjunction needed. Expected correspondent for Hebrew's own narrative chaining (waw-
  consecutive, or a circumstantial infinitive construct) — needs checking which Hebrew
  construction actually triggers it, since Hebrew has no direct participle parallel to
  the Greek aorist circumstantial participle that anchors this rule in the NT document.

- **No indefinite article** — bare noun is the default, matching Hebrew's own lack of an
  indefinite article. Only when एक ("one") is explicitly supplied for emphasis/
  specificity is it secondary.

- **Ergative ने** — marks the subject of a transitive verb in the perfective aspect. No
  Hebrew trigger at all (Hebrew has no split-ergative system) — secondary to the subject
  noun/pronoun, never NEQ. See ERGATIVE ने AND ACCUSATIVE/DATIVE को.

- **को** — dative (indirect object, or dative-experiencer subject) is case-implied,
  secondary to the noun; differential object marking (DOM) on a definite/animate direct
  object has no Hebrew trigger (Hebrew marks direct objects with אֶת regardless of
  definiteness/animacy — see the base document §13.4), still secondary to the noun, not
  NEQ. See ERGATIVE ने AND ACCUSATIVE/DATIVE को.

- **Genitive postposition का/की/के** — inflects for the gender/number/case of the
  possessed noun, not the possessor. Case-implied secondary to the possessed noun for an
  ordinary Hebrew construct-chain relationship where no explicit Hindi linking word is
  otherwise required; see CONSTRUCT CHAINS AND GENITIVE POSTPOSITION.

---

## NEQ (NON-EQUIVALENT) **[hin]**

NEQ = positive claim that no correspondence exists. Never use as fallback for
uncertainty. Unrecorded = correspondence not determined (normal). NEQ records must not
include `meta.secondary`.

- Certain no correspondent → NEQ (source or target empty, `meta.rel: "NEQ"`).
- Uncertain → leave unrecorded.

Supplied copula ("है"/"हूँ"/"हैं") with no Hebrew verb token → NEQ target (Hebrew verbless
clause, base document §12.1). Copula ellipsis after नहीं is common in predicate-nominal/
adjectival clauses — this is normal Hindi grammar, not a gap to fill; when both Hebrew
and Hindi omit the copula there is simply nothing to align.

ने and को-as-DOM are never NEQ even though neither has a Hebrew trigger — secondary to
the noun phrase they mark, since that noun phrase is itself the source anchor.

Hebrew direct object marker (אֶת/אֵת) with no Hindi correspondent → NEQ source (the
standard, expected outcome — parallel to OT Indonesian's treatment).

A parenthetical cross-reference (e.g. "(यहूदा 1:1)") → NEQ target. (IRVHin appends these
in both testaments; carried over from the NT document's config.)

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent
alignment. Align on lexical/semantic correspondence, not surface form.

---

## GRANULARITY **[hin]**

Prefer one record per source token — split rather than group. Create separate records
whenever source tokens (or word-parts) can each independently map to distinct target
tokens. Combine into N:M records only when tokens form an inseparable semantic unit
(idiom, light verb, vector verb) or target words cannot be individually assigned to
separate source tokens. When in doubt, split.

Grammar-required translation words (periphrastic copula, ergative ने, DOM को, vector
verb, reinstated demonstrative) are secondary to the source token or word-part whose
grammar requires them — not NEQ.

---

## ARTICLES **[hin]**

Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.

**DEFAULT → Branch B — CONFIRMED.** No separate word at all — the noun stands bare,
article secondary to the noun's own record, no target word required. Spot-checked
across every articular noun in Genesis 1:1, 2:23, and 3:1 with no exceptions: הַשָּׁמַיִם
→ आकाश, הָאָרֶץ → पृथ्वी, הָאִשָּׁה → स्त्री, הַגָּן → वाटिका — all bare, no यह/वह
supplied. This is a small, single-chapter sample, but it is unanimous and matches both
the NT Hindi document's and OT Indonesian's findings. One exception was noted but not
yet resolved: הָאָדָם ("the man") in Genesis 2:23 is rendered "आदम" (the proper name
"Adam") rather than a generic "the man" — a translator convention supplying a proper
name for a common noun+article, distinct from the ordinary Branch A/B choice. Flagged
as an open question below rather than folded into either branch.

**MINORITY case → Branch A:** यह (proximal, "this") or वह (distal, "that") supplied,
primary 1:1, noun in its own record — typically a second/later mention. **Not yet
isolated in the spot-check** — no Branch A instance was found in the sample checked so
far (only Branch B and the आदम exception above).

**Check for an explicit Hebrew demonstrative pronoun before assuming यह/वह is Branch A
for the article itself.** OT Hebrew commonly follows an articular noun with a separate
demonstrative-pronoun word (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) to form "that/this X" (הָאִישׁ
הַהוּא, lit. "the man, the that-one" = "that man") — a real, distinct Hebrew token. When
IRVHin's यह/वह corresponds to one of these demonstrative-pronoun tokens, align it primary
1:1 to THAT token, not to the article (which stays Branch B secondary on the noun). OT
Indonesian found this distinction mattered a great deal (53.5% itu/ini co-occurrence rate
vs. NT's 22%, tracking the demonstrative-pronoun's own frequency, not a shift in the
article's own Branch A/B split) — expect the same pattern for Hindi. **Still HYPOTHESIS**:
a targeted search for the exact הַ...הַהוּא/הַהִיא construction did not turn up a match
in this pass (see Open questions); Genesis 2:11–19's various הוּא instances found instead
turned out to be predicative "it is..." usages (e.g. "यह वही है जो..." for פִּישׁוֹן...
הוּא הַסֹּבֵב, "this is the one that flows around..."), not the "that man" demonstrative-
after-article pattern. A dedicated search is still needed.

### Branch A — article has a distinct Hindi correspondent

- Example (repeated/anaphoric mention, no separate Hebrew demonstrative — the article
  itself is the only source of यह/वह): הָאָרֶץ → "वह पृथ्वी" (hypothesized):
  source=[articlePart], target=["वह"] — primary 1:1; source=[אָרֶץ], target=["पृथ्वी"] —
  primary 1:1.
- Example (explicit Hebrew demonstrative present): הָאִישׁ הַהוּא → "वह मनुष्य"
  (hypothesized): source=[articlePart] — no target correspondent (Branch B, secondary to
  the noun); source=[אִישׁ], target=["मनुष्य"] — primary 1:1; source=[הוּא],
  target=["वह"] — primary 1:1 (the demonstrative pronoun, not the article, is वह's real
  correspondent).

### Branch B — no distinct Hindi correspondent → secondary, no target word

- Articular noun, bare in Hindi: source=[articlePart, אָרֶץ], target=["पृथ्वी"] —
  primary: "पृथ्वी"; secondary.source: [articlePart].
- Construct-chain absolute noun with article: का/की/के-marked Hindi construction already
  carries the construct-chain semantics; the article stays secondary with no separate
  word (see CONSTRUCT CHAINS AND GENITIVE POSTPOSITION).

### Anarthrous noun

No Hebrew article token exists, and Hindi has no indefinite article by default — bare
noun, no secondary needed unless एक is explicitly supplied.

---

## CONSTRUCT CHAINS AND GENITIVE POSTPOSITION का/की/के **[hin]**

A Hebrew construct chain expresses a genitive-like relationship by word order and a
change in the construct noun's form — no preposition token is inserted (base document
§11). Hindi renders this with the genitive postposition का/की/के, which — unlike
English "of" or French "de" — inflects for the gender, number, and case of the
**possessed** noun (the noun that precedes का/की/के in Hindi word order, which is
typically the construct noun's Hindi equivalent), not the possessor. This is the same
mechanism documented in the NT Hindi document for Greek genitives; the trigger here is
the Hebrew construct relationship instead of Greek's genitive case.

**CONFIRMED** against two real construct chains in Joshua 1:1:

- עֶבֶד יְהוָה "servant of the LORD" → "यहोवा **के** दास": के agrees with masculine दास
  ("servant"), not with यहोवा. के secondary to the possessed noun (दास); no separate
  Hebrew preposition token exists for it to be primary to.
  source=[עֶבֶד], target=["दास"] — primary: "दास"; secondary: "के";
  source=[יְהוָה], target=["यहोवा"] — primary 1:1.
- בִּן נוּן "son of Nun" → "नून **का** पुत्र": का agrees with masculine पुत्र ("son").
  source=[בִּן], target=["पुत्र"] — primary: "पुत्र"; secondary: "का";
  source=[נוּן], target=["नून"] — primary 1:1.

**Objective genitive with a light verb — NEW finding, not documented for Greek in this
form.** When a Hebrew transitive verb is rendered as a Hindi light verb (noun + करना),
the logical direct object of that verb takes का/की on the light-verb noun, exactly
parallel to the ordinary construct-chain treatment above, even though there is no
Hebrew construct relationship or preposition involved at all — the sole Hebrew trigger
is the direct-object relationship (often אֶת-marked) to the verb being rendered as a
light verb. Confirmed 4+ times:

- Genesis 1:1: אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ (direct objects of בָּרָא "created") →
  "आकाश और पृथ्वी **की** सृष्टि की" (lit. "did creation of heaven and earth"): की marks
  both as the objective genitive of सृष्टि ("creation," the light-verb noun); אֵת → NEQ
  source (per the general DOM-marker rule, not rendered by की at all — की's source
  anchor is the light-verb-object relationship, not אֶת itself).
- Genesis 1:27 (×2): אֶת־הָאָדָם (object of בָּרָא) → "मनुष्य **की** रचना की"; זָכָר
  וּנְקֵבָה (object of בָּרָא again) → "मनुष्यों **की** सृष्टि की".
- Genesis 9:11: הָאָרֶץ (object of לְשַׁחֵת, an infinitive rendered as a light verb) →
  "पृथ्वी **का** नाश करने के लिये" — का marks पृथ्वी as objective genitive of नाश
  ("destruction").

This sharpens what the NT Hindi document illustrated with a single example ("अपने
लोगों **का**...उद्धार करेगा," GENITIVE POSTPOSITION का/की/के in that document) into a
systematic rule for this config: **expect का/की, not DOM को, whenever the direct object
of a Hebrew verb lands as the logical object of a light-verb noun.** Treat the object
noun as secondary (marked by का/की) to the light-verb noun, which is itself primary in
the light-verb record (see TOKEN ROLES and LIGHT AND VECTOR VERBS).

**Construct chains of three or more links:** align each link individually, per §11.5 of
the base document; each का/की/के is secondary to the construct noun it follows.
**HYPOTHESIS** — no 3+-link chain was checked in this pass.

**Construct definiteness:** the Hebrew article word-part on the absolute (genitive) noun
stays secondary per ARTICLES Branch B — Hindi's का/की/के construction already signals
the relationship, so no extra word is needed even when the article marks the whole chain
as definite. **HYPOTHESIS** — not directly isolated, though consistent with the
confirmed Branch B default.

**Still needs checking:** whether IRVHin ever uses bare noun-noun juxtaposition (parallel
to Indonesian's construct-chain strategy) instead of का/की/के for any construct chains —
not observed in this pass (both checked instances used का/के).

---

## INSEPARABLE PREPOSITIONS **[hin]**

Preposition word-part → Hindi preposition/postposition (में, को, से, के साथ, जैसा, etc.):
primary 1:1. Merged article in the same token has no separate Hindi correspondent
(Hindi has no article) beyond the ordinary Branch B treatment.

Example (hypothesized): בַּשָּׁמַיִם "in the heavens" (single merged token, article
absorbed) → "स्वर्ग में": source=[bashamayimId], target=["स्वर्ग", "में"] — primary:
"स्वर्ग", "में".

מִן ("from") independent word → "से" primary 1:1; attached prefix מִ/מִּ follows the
same rules as other inseparable prepositions.

---

## PRONOMINAL SUFFIXES **[hin]**

Hebrew pronominal suffixes are separate word-part tokens (pos=suffix) when MACULA
provides them. Unlike Indonesian's fused clitics (-ku/-mu/-nya), Hindi possessive/object
pronouns are ordinarily free-standing words (मेरा, तेरा, उसका, हमारा, etc.) rather than
attaching to the noun/verb/preposition as a bound morpheme. **CONFIRMED**: Psalm 23:1's
רֹעִי ("my shepherd") → "मेरा चरवाहा" and Genesis 2:23's עֲצָמַי ("my bones") → "मेरी
हड्डियों" both render the suffix as a free possessive pronoun agreeing with the
possessed noun's gender (मेरा masc./मेरी fem.), confirming the expected non-fusion
pattern differs from OT Indonesian.

- **Possessive suffix on noun** — suffix word-part present → primary 1:1, suffix →
  Hindi possessive pronoun (मेरा/तेरा/उसका/हमारा/तुम्हारा/उनका, agreeing in gender/number
  with the possessed noun per the same का/की/के agreement pattern as CONSTRUCT CHAINS).
  Example (confirmed, Ps 23:1): יְהוָה רֹעִ- י "the LORD [is] my shepherd" → "यहोवा मेरा
  चरवाहा है": source=[רֹעִ], target=["चरवाहा"] — primary 1:1; source=[suffix־י],
  target=["मेरा"] — primary 1:1 (है is a separately-supplied copula, NEQ — see NEQ).
  Suffix token absent (single token): the Hindi possessive pronoun is primary to the
  containing noun token.

- **Reflexive अपना/अपने when the possessor is coreferential with the clause subject —
  NEW finding, not anticipated in the original draft or the NT document.** When the
  noun bearing the pronominal suffix is itself an argument of a verb whose subject is
  the same referent as the suffix, IRVHin substitutes the reflexive अपना/अपने/अपनी for
  the ordinary possessive (उसका/उसकी/उसके), rather than defaulting to the third-person
  possessive the suffix's own person/number would otherwise predict.
  Example (confirmed, Gen 1:27): בְּצַלְמוֹ "in his own image" (the referent — God — is
  also the subject of the clause's verb, יִּבְרָא "created") → "**अपने** स्वरूप में,"
  not "उसके स्वरूप में." source=[צֶלֶם], target=["स्वरूप"] — primary 1:1;
  source=[suffix־וֹ], target=["अपने"] — primary 1:1. Treat अपना/अपने/अपनी exactly like
  an ordinary possessive suffix rendering (primary 1:1 to the suffix word-part) — the
  reflexive/non-reflexive choice is a Hindi-grammar detail that does not change which
  Hebrew token is the correspondent, only which Hindi lexeme surfaces. Needs checking
  whether this applies equally to suffixes on verbs and prepositions, not just nouns.

- **Object suffix on verb** — suffix word-part present → primary 1:1, suffix → Hindi
  object pronoun (मुझे/तुझे/उसे/हमें/तुम्हें/उन्हें) or a DOM-को-marked noun phrase.
  Example (hypothesized): שְׁמָרֵנוּ "he kept us" → "उसने हमें रखा"-type construction:
  source=[shamarPart], target=["रखा"] — primary 1:1; source=[nuPart], target=["हमें"] —
  primary 1:1.

- **Suffix on preposition** — suffix word-part present → primary 1:1 to the Hindi
  pronoun object of the postposition. Example (hypothesized): אֵלָיו "to him" → "उसकी
  ओर"/"उसके पास"-type construction: source=[elPart], target=["ओर"/"पास"] — primary;
  source=[sufPart], target=["उसकी"/"उसके"] — primary.

---

## CONJUNCTIONS AND PARTICLES **[hin]**

Align content words first; conjunctions and particles are residual.

- Waw word-part (pos=conjunction) → "और"/"परन्तु"/"तब"/"तो"/"इसलिये": primary 1:1.
  Asyndeton → NEQ source.
- כִּי — polyfunctional (causal, content-clause, conditional, temporal, emphatic,
  recitative — base document §13.2); align to whichever Hindi word carries its force in
  context ("क्योंकि", "कि", "यदि", "जब"). Recitative כִּי rendered with only punctuation
  → NEQ source.
- אֲשֶׁר/שֶׁ — relative/subordinate marker (base document §13.3); expected default
  correspondent जो, parallel to its NT role. Absorbed without correspondent → NEQ
  source.

---

## IDIOMS **[hin]**

`meta.is_idiom: true` when phrase-level correspondence has no token-level equivalent.
All tokens implicitly primary; `meta.secondary` does not apply.

Last resort — prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom
marking whenever the construction is a recognized light or vector verb rather than a
genuinely non-compositional phrase. Function-word-only source records are never idioms.

Hebrew idiom examples from the base document (נָשָׂא פָּנִים "show favoritism," חָרָה אַף
"be angry," שָׂם לֵב "pay attention") are expected to render as single Hindi light-verb
or fixed expressions rather than word-for-word — needs checking against actual IRVHin
renderings.

---

## ERGATIVE ने AND ACCUSATIVE/DATIVE को **[hin]**

Hindi has split ergativity: transitive verbs in the perfective aspect require the
subject to carry ने. This has **no trigger in Hebrew at all** — Hebrew has no
ergativity, and this is purely a requirement of Hindi's own verb-agreement system,
exactly as it has no Greek trigger in the NT document.

**CONFIRMED, strongly.** ने fired in every checked verse with a perfective-transitive
subject: Genesis 1:1 परमेश्वर **ने** सृष्टि की, Genesis 2:23 आदम **ने** कहा, Joshua 1:1
यहोवा **ने**...कहा, Genesis 8:21/9:11 यहोवा **ने**/मैं. **ने is always secondary to the
subject noun/pronoun it marks — never NEQ.**

को has the same functions documented in the NT Hindi document:

- **Dative** (indirect object) — often corresponds to a Hebrew לְ-marked indirect
  object; case-implied secondary to the noun. **HYPOTHESIS** — not directly isolated in
  this pass.
- **Differential object marking (DOM)** on a definite/animate direct object — no Hebrew
  correspondent (Hebrew marks direct objects with אֶת regardless of definiteness/
  animacy); still secondary to the noun, not NEQ. **Not observed as को in this pass** —
  every direct-object case checked (Genesis 1:1, 1:27, 9:11) instead took the objective-
  genitive-का/की pattern documented under CONSTRUCT CHAINS AND GENITIVE POSTPOSITION,
  because the corresponding Hebrew verb was rendered as a Hindi light verb. को-as-DOM
  may still occur when the Hebrew verb is rendered with an ordinary (non-light) Hindi
  verb instead — this needs a targeted check on a verse where that is the case.

**Interaction with אֶת:** a Hebrew direct object already marked with אֶת and rendered in
Hindi with DOM-को produces two separate grammar-internal markers side by side (one
Hebrew, one Hindi) with no correspondence to each other — אֶת → NEQ source; को →
secondary to the noun, per their respective independent rules. Do not treat को as the
Hindi correspondent of אֶת. **Confirmed for the की/का case** (Genesis 1:1's two אֵת
tokens are unaligned/NEQ while की marks the light-verb objective genitive) — the को
case specifically remains unchecked.

---

## NEGATION **[hin]**

**CONFIRMED overall** — carries over from the NT document largely unchanged, as expected
for pure Hindi grammar:

- **नहीं** — default, general-purpose negator, usable with almost any Hebrew-sourced
  verb form. Confirmed: Genesis 2:5 כִּי לֹא הִמְטִיר → "यहोवा...**नहीं** बरसाया"
  (indicative past). Copula ellipsis after नहीं in predicate-nominal/adjectival clauses
  is common — not a gap to fill.
- **न** — interchangeable literary variant of नहीं for ordinary negation. Confirmed with
  both future/modal (Ps 23:1 לֹא אֶחְסָר "I shall not want" → "मुझे कुछ घटी **न** होगी")
  and imperative-flavored (Gen 3:1 לֹא תֹאכְלוּ "you shall not eat" → "**न** खाना")
  contexts — matches the NT document's finding that the split is not conditioned by
  mood. Also the dedicated correlative form for "neither...nor" lists — **not isolated
  in this pass**; needs checking whether Hebrew has a comparably explicit correlative-
  negation construction or whether it is expressed more freely (e.g. repeated לֹא
  across parallel cola in poetry, per the base document's parallelism guidance, §15).
- **मत** — ordinary colloquial prohibitive. **Not isolated in this pass** — no imperative
  אַל-negation instance was checked. Caution: homographic with an unrelated noun मत
  ("opinion") — disambiguate by syntactic position.

**Simple negation (לֹא)** → नहीं/न, per the base document's simple-negation treatment
(§13.5). **CONFIRMED** — see examples above.

**Existential negation (אֵין) — HYPOTHESIS REVISED.** The original draft guessed a fixed
"नहीं है"/"नहीं हैं" expression, parallel to Indonesian's fixed "tidak ada" idiom. The
spot-check does not support a single fixed idiom: IRVHin instead uses a flexible नहीं/न
+ tense-agreeing था/हुआ construction, matching whatever tense the surrounding narrative
is in, still landing as a 1:N record against אֵין per the base document's general אֵין
guidance (§13.5) rather than Indonesian's single fixed phrase:
- Genesis 2:5: וְאָדָם אַיִן לַעֲבֹד "and there was no man to work" → "भूमि पर खेती करने
  के लिये मनुष्य भी **नहीं था**" — नहीं + था (past copula), both primary to אַיִן (1:N).
- Genesis 11:30: אֵין לָהּ וָלָד "she had no child" → "उसके सन्तान **न हुई**" — न + हुई
  ("became/happened"), both primary to אֵין (1:N); לָהּ ("to her") → "उसके," primary to
  the suffix.

**Emphatic negation (οὐ μή's absence in Hebrew):** Hebrew has no single construction
directly parallel to Greek οὐ μή; strong negation in Hebrew is typically expressed
through infinitive absolute + negated finite verb, or through reinforcing adverbs. If
IRVHin renders these with the same reinforcement strategies documented for Greek οὐ μή
(कभी/कदापि + न/नहीं, अनन्तकाल तक + न, किसी रीति से + न, or bare न/नहीं with no
reinforcement), treat identically — needs checking against actual OT emphatic-negation
constructions.

### Compound / discontinuous negation — CONFIRMED

The NT document and OT Indonesian both found a "no longer" construction (Greek
οὐκέτι/μηκέτι; Hebrew לֹא...עוֹד) that is discontinuous in the target language more
often than a naive contiguity assumption would predict (OT Indonesian: ~70% of 222
Hebrew לֹא...עוֹד verses render with the verb/modal intervening between "tidak" and
"lagi," not the contiguous "tidak lagi"). **Confirmed for Hindi** in 3 of 4 checked
instances (out of 217 verses in the full WLCM corpus containing both לֹא and עוֹד — not
yet checked at that scale, but the spot-check result is unanimous enough to treat this
as solid pending a full count):

- Genesis 8:12: וְלֹא־יָסְפָה שׁוּב אֵלָיו עוֹד → "वह उसके पास **फिर** कभी लौटकर **न**
  आई" — फिर separated from न by कभी लौटकर.
- Genesis 8:21 (first instance): לֹא אֹסִף...עוֹד → "मैं **फिर** कभी भूमि को श्राप **न**
  दूँगा" — फिर separated from न by भूमि को श्राप.
- Genesis 9:11 (both instances): וְלֹא יִכָּרֵת...עוֹד and וְלֹא יִהְיֶה...עוֹד → "**फिर**
  जल-प्रलय से नाश **न** होंगे" and "**फिर** जल-प्रलय **न** होगा" — फिर separated from न
  by intervening material in both.
- The one contiguous exception (Genesis 8:21, second instance): לֹא אֹסִף עוֹד → "**फिर**
  कभी **न** मारूँगा" — फिर, कभी, and न all cluster together immediately before the verb,
  showing contiguity is a real minority option, not that the discontinuous pattern is
  absolute.

Both words are primary to their respective Hebrew tokens (לֹא → नहीं/न, עוֹד → फिर)
regardless of adjacency in the Hindi text.

**False-friend trap — जब तक...न ("until...not"):** confirmed in the NT document (78
IRVHin verses) as having no Greek source correspondent when the ἕως/ἄχρι clause carries
no negative particle of its own. Hebrew has a directly parallel construction (עַד
"until" + negated clause, base document §13.1) — this trap is expected to recur
identically in the OT: the न in जब तक...न would be NEQ target when the Hebrew עַד clause
itself carries no negation. **HYPOTHESIS** — not checked against an actual OT "until"
construction in this pass.

---

## PASSIVE VOICE **[hin]**

Hebrew passive stems (Niphal, Pual, Hophal — base document §12.4) are expected to map
onto the same multi-strategy inventory the NT document confirmed for Greek passives,
since the strategies themselves are properties of Hindi, not of the source language.
**3 of 8 strategies are now confirmed** with real Hebrew passive-stem examples,
including one striking cross-testament match:

1. **True periphrastic passive (participle/vector-compound + जाना) — CONFIRMED.**
   Isaiah 53:5: מְחֹלָל (Pual, "pierced") → "**घायल किया गया**" (घायल primary + किया
   गया secondary, a light-verb passive: घायल करना "to wound" + जाना); מְדֻכָּא (Pual,
   "crushed") → "**कुचला गया**" (कुचला primary, participle; गया secondary). Both from a
   single verse, both clean instances of participle/light-verb-noun primary + जाना
   secondary.
2. **Stative-perfect (participle + copula, no जाना)** — confirmed in the NT document as
   narrowly specific to the "it is written" citation formula (γέγραπται → लिखा है). The
   OT has its own recurring "it is written" formula (כָּתוּב) — **not isolated in this
   pass** (a targeted search for כָּתוּב did not return a match with the query used;
   needs retry with a corrected search).
3. **Adjectival/nominal resultative (adjective + होना/बनना) — CONFIRMED, with a notable
   cross-testament match.** Isaiah 53:5: נִרְפָּא (Niphal, "healed") → "**चंगे हो
   जाएँ**" — the identical चंगा+होना mapping the NT document found for ἰαθήσεται
   (Matthew-type "will be healed"). Two independent testaments, two independent source
   languages, same Hindi lexical strategy for "healed" — strong evidence this mapping
   is a stable feature of IRVHin's lexicon, not coincidence. Genesis 21:5: הִוָּלֶד
   (Niphal, "was born") → "**उत्पन्न हुआ**" (उत्पन्न "arisen/produced" + हुआ "became") —
   a second confirmed instance of the same strategy.
4. **Dedicated intransitive/unaccusative verb** — Hindi's own transitive/intransitive
   verb pairs (खोलना/खुलना, etc.) absorbing a passive with no voice marking. **Not
   isolated in this pass.**
5. **Light-verb/noun+होना idiomatic construction** — for passives of experience,
   relation, and communication. **Not isolated in this pass** (distinct from the
   light-verb+जाना pattern confirmed under Strategy 1 above, which has जाना as an
   overt passive marker; this strategy specifically lacks जाना).
6. **Bare resultative participle (+ हुआ/हुई/हुए, no finite copula)**. **Not isolated in
   this pass** — though see the उत्पन्न हुआ example under Strategy 3, which is close
   but does have हुआ functioning as a finite verb, not a bare attributive participle.
7. **Active-voice conversion** — a full voice flip. **Not isolated in this pass.**
8. **Naming/equational conversion — CONFIRMED.** Genesis 2:23: יִקָּרֵא ("she shall be
   called") → "**इसका नाम नारी होगा**" ("her name will be woman/nari") — the passive
   verb is dropped entirely in favor of a naming/equational sentence, exactly
   parallel to the NT document's Revelation 19:13 example (उसका नाम...है for
   κέκληται).

**Theological/divine passive:** Hebrew sometimes uses the passive to imply divine
agency without naming God (base document §12.4). When IRVHin makes the divine agent
explicit with no Hebrew token for "परमेश्वर," that supplied noun is NEQ target — parallel
to the base document's general supplied-proper-name rule, not a Hindi-specific
mechanism. **HYPOTHESIS** — not checked in this pass.

---

## PARTICIPIAL CONSTRUCTIONS **[hin]**

Hebrew participles (base document §12.7) serve adjectival, substantive/nominal, and
verbal/predicative (continuous) functions — structurally different from Greek's
article+participle substantive construction, so this section needs more careful
adaptation than most.

- **Adjectival participle** — aligns to Hindi adjective or participial modifier,
  primary.
- **Substantive (nominal) participle** — expected default जो + finite verb/relative
  clause, parallel to its NT role, when the Hebrew article word-part is present
  (הַשֹּׁמֵר "the one who keeps"). वाला reserved for participles that compress into a
  stable, lexicalized agent-noun or role label, parallel to its NT restriction. Needs
  checking whether Hebrew's article-marked substantive participle behaves the same way
  a Greek articular participle does for this purpose, since Hebrew's article is a
  distinct word-part token rather than a fused morpheme.
- **Verbal (predicative) participle — continuous/progressive** — participle primary;
  Hindi progressive auxiliary (है/था/थी) secondary. Parallel to base document's יֹשֵׁב
  example.
- **Participle + הָיָה (periphrastic construction)** — when הָיָה is explicit, it aligns
  as a primary record to the Hindi auxiliary (था/थी/थे); the participle aligns to the
  main verbal element, also primary. Two separate primary records, per the base
  document's treatment. This is expected to interact with Hindi's own periphrastic
  default (participle + copula is *always* the ordinary way to form these tenses in
  Hindi, not an optional stylistic choice) — when both Hebrew and Hindi use periphrasis
  independently, expect a 2-record structure (Hebrew participle + Hebrew הָיָה, each
  primary to its own Hindi correspondent) rather than collapsing into one.

---

## INFINITIVAL CONSTRUCTIONS **[hin]**

Hindi has a true infinitive (verb stem + ना: करना, आना, जाना).

### Infinitive construct with לְ

לְ + infinitive construct (base document §12.5): when לְ is a separate word-part token,
it aligns to a Hindi purpose/purpose-adjacent marker (के लिये, को) as primary, parallel
to the NT document's purpose-infinitive treatment; the infinitive itself aligns to the
bare Hindi infinitive, also primary — unlike Greek, where the NT document treats "to" as
secondary, Hebrew's לְ is an explicit lexical morpheme (base document §12.5 explicitly
contrasts this with Greek's secondary "to"), so expect के लिये/को to be **primary** to
the לְ word-part when both are present, not secondary to the infinitive.

**CONFIRMED** — के लिये is the attested default in both checked instances, matching the
NT document's finding that के लिये (not को) is the translation-independent default:

- Genesis 2:5: לַעֲבֹד אֶת־הָאֲדָמָה ("to work the ground") → "भूमि पर खेती **करने के
  लिये**" — लְ → के लिये, primary; the infinitive (עָבַד) → करने, primary (करने itself
  is the light-verb component of खेती करना "to farm").
- Genesis 9:11: לְשַׁחֵת הָאָרֶץ ("to destroy the earth") → "पृथ्वी का नाश **करने के
  लिये**" — לְ → के लिये, primary; the infinitive (שָׁחַת) → करने, primary (करने is again
  the light-verb component of नाश करना "to destroy"; पृथ्वी का is the objective genitive
  of नाश per CONSTRUCT CHAINS AND GENITIVE POSTPOSITION, not related to לְ at all).

Both instances happen to involve a light-verb infinitive (करने के लिये rather than a
single-word infinitive) — worth noting that this may be the more common pattern for
Hebrew infinitive constructs specifically, since Hebrew infinitive constructs so often
correspond to abstract-noun-headed Hindi light verbs (खेती, नाश) rather than simple
verbal roots. Needs checking against a Hebrew infinitive construct rendered with a
simple (non-light-verb) Hindi infinitive to see whether के लिये still applies the same
way.

**Infinitive construct as verbal noun** (בְּ + infinitive → "when/while/in ...-ing," base
document §12.5): the infinitive aligns to the Hindi main verbal element; the preposition
word-part aligns to the Hindi temporal/logical connector (जब, जैसे ही, में) as primary.

### Infinitive absolute (cognate emphasis)

Hebrew's infinitive absolute + cognate finite verb for emphasis (מוֹת תָּמוּת "you shall
surely die," base document §12.6) is expected to render with a Hindi emphasis adverb
(अवश्य/निश्चय/ज़रूर) — infinitive absolute primary to the adverb; finite verb primary to
the main Hindi verb, per the base document's two-primary-record treatment. If the
translation absorbs the emphasis into a strong modal without a separate word, the
infinitive absolute may be secondary to the finite verb, or NEQ if definitively
untranslated.

---

## Cross-translation methodology note

**Single-translation spot-check performed; full-corpus and cross-translation checks
still pending.** A first pass joined `WLCM.tsv` (Hebrew source) to `ot_IRVHin.tsv` by
verse and inspected roughly 15 verses (Genesis 1:1, 1:27, 2:5, 2:23, 3:1, 8:12, 8:21,
9:11, 11:30, 21:5; Joshua 1:1; Psalm 23:1; Isaiah 53:5), chosen to cover articles,
construct chains, pronominal suffixes, ergative ने, negation, existentials, and passive
voice. This confirmed most carried-over NT-document findings and surfaced two genuinely
new findings not present in the NT document at all: the objective-genitive-का/की rule
for light-verb direct objects, and the reflexive अपना/अपने rule for subject-coreferent
possessive suffixes.

Unlike the NT Hindi document (cross-checked against IRVHin, HSB, and OHCV) and the OT
Indonesian document (checked at full-corpus scale against TBI, all 23,213 verses), this
pass is neither full-corpus nor cross-translation. Two other Hindi OT translations exist
in the repo with partial coverage — `alignments-hin/data/targets/GST/ot_GST.tsv`
(45,069 lines) and `alignments-hin/data/targets/GLT/ot_GLT.tsv` (32,719 lines), both
well short of IRVHin's 682,689-line full OT — and could serve the same cross-checking
role HSB/OHCV played for the NT document, but neither has been consulted yet.

What held up unchanged from the NT document: ergative ने, नहीं/न negation split by
discourse function (not mood), light-verb N:1 treatment, the general shape of the
passive-voice strategy inventory, article Branch B default, के लिये as the purpose-
infinitive default, and (via the לֹא...עוֹד parallel) discontinuous "no longer" negation.

What is new to the OT document specifically: the objective-genitive-का/की rule for
light-verb direct objects (not encountered in the NT document because Greek direct
objects don't interact with a construct-chain-like relationship the way Hebrew's אֶת-
marked objects of light-verb-rendered transitives do), and the reflexive अपना/अपने
rule for coreferent possessive suffixes (not surfaced in the NT document's spot-check
verses, though it may well apply there too and simply wasn't checked).

What was checked and produced a genuinely unresolved result: the הַ...הַהוּא/הַהִיא
demonstrative-after-article construction (ARTICLES Branch A) — the search strategy used
(exact match on הַהוּא/הַהִיא as tokens) returned zero hits, while a broader search for
הוּא as a pronoun turned up only predicative "it is..." usages unrelated to the
demonstrative-doubling construction OT Indonesian found productive. Either IRVHin
tokenizes or renders this construction differently than expected, or the sample simply
didn't contain an instance — needs a differently-targeted search.

## Open questions for native-speaker and TSV-data review

- **Highest priority — needs retry:** a search for the OT "it is written" formula
  (כָּתוּב) to check whether the NT document's stative-perfect (participle + copula, no
  जाना) exception recurs for this recurring OT citation formula. The initial query
  string didn't match; a corrected search is needed.
- **Highest priority — needs retry:** find an actual instance of the
  הָאִישׁ הַהוּא / הָאִשָּׁה הַהִיא ("that man" / "that woman") demonstrative-after-
  article construction to confirm or disconfirm the ARTICLES Branch A hypothesis and
  the demonstrative-vs-article distinction OT Indonesian found productive.
- Does DOM-को ever appear for a Hebrew direct object when the corresponding Hebrew verb
  is rendered with an ordinary (non-light-verb) Hindi verb, rather than always taking
  the objective-genitive-का/की pattern found so far? All checked instances happened to
  involve light-verb renderings.
- Does the reflexive अपना/अपने rule for subject-coreferent possessive suffixes extend to
  suffixes on verbs and prepositions, not just nouns? Only a noun-suffix instance
  (בְּצַלְמוֹ) was checked.
- Does IRVHin's construct-chain rendering ever use bare noun-noun juxtaposition (the
  Indonesian strategy) instead of का/की/के? Not observed in the two instances checked,
  both of which used का/के.
- Do the remaining five NT-confirmed passive-voice strategies (2 stative-perfect, 4
  intransitive/unaccusative pairs, 5 light-verb+होना without जाना, 6 bare resultative
  participle, 7 active-voice conversion) actually recur for Hebrew Niphal/Pual/Hophal
  verbs? Only strategies 1, 3, and 8 were confirmed in this pass.
- Does जो/वाला substantive-participle behavior hold for Hebrew articular participles
  the same way it does for Greek articular participles, given the different underlying
  tokenization (Hebrew article is a distinct word-part token, not a fused morpheme)? Not
  checked at all in this pass.
- Does the जब तक...न false-friend trap (confirmed in the NT document) recur identically
  for Hebrew עַד ("until") constructions? Not checked in this pass.
- Would checking against GST or GLT (the two other Hindi OT translations with partial
  coverage in this repo) confirm these findings are general Hindi strategies rather than
  IRVHin-specific choices, the way HSB/OHCV did for the NT document?
- This document has not been reviewed by a native Hindi speaker, matching the NT
  document's draft status.
