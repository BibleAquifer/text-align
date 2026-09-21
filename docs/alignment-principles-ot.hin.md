# Alignment Principles — Hindi (hin), Old Testament

Guidelines used by `refine-alignment` when aligning the Indian Revised Version Hindi
(IRVHin) against the Hebrew Old Testament (MACULA Hebrew / Westminster Leningrad Codex)
source.

Sections marked **[hin]** contain Hindi-specific rules or examples. Unmarked sections
follow the shared structural conventions of the English guidelines
(`alignment-principles-ot.md` and `prompt/ot/eng.py`).

**Draft status — corpus-scale checked against `ot_IRVHin.tsv` and cross-translation
checked against OHCV and GLT (partial OT coverage); not yet reviewed by a native
speaker.** This document was originally seeded by carrying over the Hindi-grammar
findings already confirmed in `alignment-principles-nt.hin.md` (cross-checked there
against IRVHin, HSB, and OHCV for the New Testament) and re-expressing them against
Hebrew source structure instead of Greek. An initial ~15-verse spot-check (Genesis 1–2,
3:1, 8:12, 8:21, 9:11, 11:30, 21:5, Joshua 1:1, Psalm 23:1, Isaiah 53:5) confirmed most
of the carried-over claims and surfaced two OT-specific findings (the objective-
genitive-with-light-verb rule for direct objects, and reflexive अपना for subject-
coreferent possessive suffixes). **A follow-up two-part verification pass** then (1)
cross-checked the doc's claims against OHCV (full OT coverage) and GLT (partial OT
coverage — only Ruth, Ezra, Nehemiah, Esther, Obadiah, Jonah; GST was deliberately
excluded), and (2) ran full-corpus-scale checks against WLCM.tsv+IRVHin for sections
that were previously untested hypotheses (participles, infinitives, pronominal-suffix
generalization, idioms, conjunctions) or backed by only a handful of examples
(negation, passive voice, articles, construct chains). This resolved both of the
document's previously flagged "highest priority" open questions (the כָּתוּב "it is
written" formula and the הָאִישׁ הַהוּא demonstrative-after-article construction), and
**overturned one claim outright**: the objective-genitive-का/की rule turned out to be
IRVHin's own lexical choice, not a general Hindi-OT strategy (OHCV uses ordinary
DOM-को on the same direct objects). Sections below are marked **CONFIRMED** (attested
against real text), **HYPOTHESIS** (still carried over unchecked), or **NEW** (found
only in this document's own research). See the Cross-translation methodology note near
the end for the full breakdown of what both passes changed.

Source files (to be created): `src/text_align/refine/prompt/ot/hin.py`,
`src/text_align/refine/prompt/ot/eng.py`

**Key differences from OT English and OT Indonesian:**

- **CONFIRMED at corpus scale (21/21 clean instances, 56,980 construct-state nouns in
  WLCM).** Like Indonesian, no native definite/indefinite article — but unlike
  Indonesian, Hindi has grammatical gender and a genitive postposition (का/की/के) that
  inflects for the gender/number/case of the *possessed* noun, not the possessor.
  Real Hebrew construct chains (עֶבֶד יְהוָה "servant of the LORD" → यहोवा के दास; בִּן
  נוּן "son of Nun" → नून का पुत्र) render with का/की/के agreeing with the possessed
  noun, exactly as hypothesized, with no bare noun-noun juxtaposition counter-example
  found in a moderate sample (see CONSTRUCT CHAINS AND GENITIVE POSTPOSITION). **New
  refinement**: के (not का) is used when the possessed noun is mid-chain, followed by
  an appositive name/title (नून **के** पुत्र यहोशू, "Joshua son of Nun") — confirmed
  2-translation (Joshua 1:1 and Ruth 1:1 independently show the same pattern).
- **CONFIRMED.** Split-ergative case marking: ने marks a transitive subject in the
  perfective aspect, with no Hebrew trigger at all (Hebrew has no ergativity). Fired
  reliably in every checked verse with a perfective transitive subject (परमेश्वर ने
  सृष्टि की, आदम ने कहा, यहोवा ने...कहा). Secondary to the noun it marks, never NEQ
  (see ERGATIVE ने AND ACCUSATIVE/DATIVE को).
- **Correction — IRVHin-specific, not a general Hindi-OT strategy.** An earlier draft
  claimed direct objects of Hebrew verbs rendered as Hindi light verbs (सृष्टि करना
  "create," रचना करना "create/form," नाश करना "destroy") consistently take an objective
  genitive का/की on the light-verb noun rather than DOM को, confirmed 4+ times within
  IRVHin (Gen 1:1, 1:27, 9:11). **Cross-checking OHCV on the same verses disproves the
  "general Hindi-OT strategy" framing**: OHCV instead uses an ordinary verb + DOM-को
  for the identical direct objects (Gen 1:1: "आकाश एवं पृथ्वी **को** रचा," not "की
  सृष्टि की"), and even uses को *alongside* a light-verb rendering in one case (Gen
  9:11: "पृथ्वी **को**...नाश करूंगा"). This also answers the doc's own open question
  (does DOM-को ever appear when the Hebrew verb is rendered with an ordinary or
  light verb?) — yes, in another translation. Treat का/की-on-light-verb-object as a
  real, confirmed IRVHin pattern, but check को first in any other Hindi OT edition
  rather than assuming का/की transfers.
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
- **CONFIRMED at corpus scale (1,479 article+participle pairs in WLCM; 40-verse
  sample).** Substantive participles: जो dominates (~55%), वाला is a smaller but real
  strategy (~10%), and a "neither" bucket — bare lexicalized noun or plain finite
  clause with no relativizer — is larger than the NT document found (~32%), suggesting
  OT narrative more often bypasses जो/वाला entirely for a plain noun or finite clause.
  See PARTICIPIAL CONSTRUCTIONS.
- **CONFIRMED for 7 of 8 strategies (up from 2), following a 33-instance fresh sample
  across 10 books beyond Genesis/Isaiah.** Hebrew's own passive stems (Niphal, Pual,
  Hophal — base document §12.4) map onto the same multi-strategy inventory documented
  for Greek NT passives. Isaiah 53:5 alone attests Strategy 1 (periphrastic जाना:
  कुचला गया "was crushed," घायल किया गया "was wounded") and Strategy 3 (adjectival
  resultative: **चंगे हो जाएँ** for נִרְפָּא "healed" — the identical चंगा+होना mapping
  the NT document found for ἰαθήσεται, now a 3-way cross-testament/cross-translation
  match after OHCV independently confirmed it). Genesis 21:5's הִוָּלֶד ("was born") →
  उत्पन्न हुआ is also Strategy 3. Genesis 2:23's יִקָּרֵא ("shall be called") →
  नाम...होगा confirms Strategy 8, though this is translation-dependent (OHCV instead
  keeps a periphrastic passive verb there, "नाम दिया जायेगा," Strategy 1 — parallel to
  the NT document's κέκληται finding). The follow-up corpus pass newly confirmed
  Strategy 4 (Judg 10:7 "न मिला"), Strategy 5 (Exod 22:9 "चोट खाए," Deut 33:13
  "आशीष पाए" — पाना is a newly documented light-verb auxiliary alongside होना/देना/
  बनना/खाना), Strategy 6 (Lev 7:9 "पके हुए"), and a plausible Strategy 7 instance
  (Lev 5:23). Only Strategy 2 needed a refinement rather than a flat confirmation — see
  below. **Methodological caveat**: at least one Niphal (Judg 21:5 שָׁבַע "swore," a
  deponent reflexive-middle rendered actively) is not a real semantic passive — the
  same deponent-verb caution the NT document's passive-voice pass flagged.
- **The "it is written" (כָּתוּב) open question is resolved, with a refinement.**
  Searching by lemma/morph (not exact surface string) found 103 corpus instances
  splitting into two context-conditioned patterns: the rhetorical citation formula
  ("is it not written in the book of...," 1 Kings 22:39/46, 2 Kings 1:18, 2 Chron
  9:29/35:27) uses **bare participle+है/हैं** ("लिखा है"/"लिखे हैं") — an exact match to
  the NT document's γέγραπται→लिखा है Strategy 2 exception. The "written on tablets/
  scroll" physical-inscription sense (Exod 31:18, 32:15, Deut 9:10, Esth 6:2, Neh 8:14,
  Jer 17:1) instead uses **participle+हुआ+copula** ("लिखा हुआ था/है/मिला"), closer to
  Strategy 6. Both are real, context-conditioned variants of the same lexical root —
  treat as two sub-patterns of Strategy 2/6, not one fixed rule.
- **CONFIRMED, with an OT-specific correction.** नहीं/न/मत negation split by discourse
  function (not mood) carries over unchanged — both नहीं and न attested for
  indicative/future negation (मुझे कुछ घटी न होगी; यहोवा नहीं बरसाया). **Correction**:
  the NT document found नहीं and न roughly co-equal in raw frequency; the OT does NOT
  show the same balance — full-corpus counts are नहीं = 2,334, न = 5,128, मत = 189, so
  **न outnumbers नहीं more than 2:1 in the OT**, likely driven by poetry's (Psalms,
  Proverbs, Isaiah) heavier use of parallelism-style negation. Do not assume the NT's
  near-parity carries over; treat न as the more frequent particle here. Hebrew's own
  "no longer" construction (לֹא...עוֹד) **is confirmed discontinuous** in roughly 82%
  of a fresh 25-verse sample (231 corpus-wide candidate verses; फिर...न with material
  intervening — Gen 8:12, 8:21, 9:11×2, among others), directly paralleling the NT
  document's οὐκέτι/μηκέτι finding and the OT Indonesian document's לֹא...עוֹד finding.
  A new lexical variant, आगे को, was also found alongside फिर in this slot (Lev 27:20,
  Gen 35:10). See NEGATION.
- **CONFIRMED, resolved.** The -कर conjunctive participle (verb stem + कर, e.g. निकलकर
  "having gone out") — a corpus check (1,778 candidate verses, 18 inspected across
  Genesis, Judges, 1–2 Samuel, 1–2 Kings) found a near-exceptionless trigger: **Hebrew's
  wayyiqtol (waw-consecutive) narrative chain**. IRVHin systematically converbializes
  all-but-the-last verb of a Hebrew narrative verb sequence into -कर, keeping only the
  final verb finite (1 Sam 9:18 וַ יִּגַּשׁ...וַ יֹּאמֶר "he approached...and said" →
  "जाकर कहने लगा"; 2 Sam 14:31's three-verb chain, arose/came/said, → "उठा,
  और...जाकर...पूछने लगा," first finite, second -कर, third finite). No infinitive-
  construct-circumstantial instances turned up — the trigger is the narrative chain,
  not the infinitive construct.
- Hebrew word-part tokenization (MACULA splits prepositions, articles, waw, and
  pronominal suffixes into separate BCVWP tokens) has no Greek NT parallel. **NEW
  finding, now generalized beyond one example.** Possessive pronominal suffixes render
  as ordinary free possessive pronouns (मेरा, उसकी) as hypothesized — *except* when the
  possessor is coreferential with the clause subject, where IRVHin uses the reflexive
  अपना/अपने instead (Gen 1:27 בְּצַלְמוֹ → "अपने स्वरूप में," not "उसके स्वरूप में"). A
  corpus pass confirmed this well beyond the single original example — noun+suffix
  (death formula, "hardened heart" idiom), true **verb-suffix** (18/18 clean, → अपने
  को/अपने लिये), and preposition-suffix (real, अपने/अपनी, but frequently absorbed into
  a vector verb with no separate reflexive word at all) — and surfaced a genuinely new,
  previously undocumented strategy: **आप (ही)**, a distinct intensive/agentive
  reflexive for the "by/of one's own agency" sense rather than possession (Gen 22:8
  "परमेश्वर...आप ही करेगा," "he himself will provide"; Gen 22:16 "मैं अपनी ही यह शपथ
  खाता हूँ," stacking अपनी + ही). See PRONOMINAL SUFFIXES.

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

**DEFAULT → Branch B — CONFIRMED**, though the corpus-scale check found the simple
whole-verse यह/वह-presence method too noisy to trust for a precise percentage (the same
वह/वे pronoun-homonymy confound the NT document flagged — वह/वे are also the ordinary
3rd-person pronoun, unrelated to any article). Spot-checked across every articular noun
in Genesis 1:1, 2:23, and 3:1 with no exceptions: הַשָּׁמַיִם → आकाश, הָאָרֶץ → पृथ्वी,
הָאִשָּׁה → स्त्री, הַגָּן → वाटिका — all bare, no यह/वह supplied. This unanimous small
sample matches both the NT Hindi document's and OT Indonesian's findings; treat Branch B
as the confirmed default, with a precise ratio still out of reach without token-level
alignment data. One exception was noted but not yet resolved: הָאָדָם ("the man") in
Genesis 2:23 is rendered "आदम" (the proper name "Adam") rather than a generic "the
man" — confirmed not IRVHin-specific (OHCV also opens with "आदम ने कहा" for the same
verse) — a translator convention supplying a proper name for a common noun+article,
distinct from the ordinary Branch A/B choice. Flagged as an open question below rather
than folded into either branch.

**MINORITY case → Branch A:** यह (proximal, "this") or वह (distal, "that") supplied,
primary 1:1, noun in its own record — typically a second/later mention.

**Check for an explicit Hebrew demonstrative pronoun before assuming यह/वह is Branch A
for the article itself.** OT Hebrew commonly follows an articular noun with a separate
demonstrative-pronoun word (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) to form "that/this X" (הָאִישׁ
הַהוּא, lit. "the man, the that-one" = "that man") — a real, distinct Hebrew token. When
IRVHin's यह/वह corresponds to one of these demonstrative-pronoun tokens, align it primary
1:1 to THAT token, not to the article (which stays Branch B secondary on the noun). OT
Indonesian found this distinction mattered a great deal (53.5% itu/ini co-occurrence rate
vs. NT's 22%, tracking the demonstrative-pronoun's own frequency, not a shift in the
article's own Branch A/B split) — expect the same pattern for Hindi.

**CONFIRMED, resolved.** The original targeted search for the exact הַ...הַהוּא/הַהִיא
token spelling found nothing, but a broader search (article token followed within 3
tokens by a standalone הוּא/הִיא/זֶה/זֹאת pronoun, not requiring a fused spelling) found
2,503 candidate corpus-wide matches, with clean genuine attributive instances confirming
the construction is real and productive: Gen 1:12/10:11 הָאָרֶץ הַהִוא ("that land") →
"उस देश"; Gen 7:1/7:11/7:13 הַ...הַזֶּה ("this day/time") → "उसी दिन"/"इस समय"; Gen
12:7 הָאָרֶץ הַזֹּאת ("this land") → "यह देश." Many of the 2,503 matches are instead the
already-documented predicative "X is the one that..." pattern (a real, distinct
construction) — both exist in the corpus; disambiguate by whether the pronoun sits
inside a noun phrase (attributive, Branch A trigger) or functions as the clause's own
predicate (predicative, unrelated to this rule).

### Branch A — article has a distinct Hindi correspondent

- Example (repeated/anaphoric mention, no separate Hebrew demonstrative — the article
  itself is the only source of यह/वह): הָאָרֶץ → "वह पृथ्वी" (hypothesized):
  source=[articlePart], target=["वह"] — primary 1:1; source=[אָרֶץ], target=["पृथ्वी"] —
  primary 1:1.
- Example (confirmed, Gen 1:12/10:11): הָאָרֶץ הַהִוא → "उस देश" ("that land"):
  source=[articlePart] — no target correspondent (Branch B, secondary to the noun);
  source=[אֶרֶץ], target=["देश"] — primary 1:1; source=[הִוא], target=["उस"] — primary
  1:1 (the demonstrative pronoun, not the article, is उस's real correspondent).
- Example (confirmed, Gen 12:7): הָאָרֶץ הַזֹּאת → "यह देश" ("this land"): same pattern,
  source=[זֹּאת], target=["यह"] — primary 1:1.

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

**CONFIRMED at corpus scale.** 56,980 construct-state nouns identified in WLCM
(`morph` ending in construct-state marker); a 21-instance sample across Genesis, Exodus,
Joshua, 1 Samuel, Psalms, Proverbs, and Isaiah showed का/की/के consistently marking the
relationship in every instance (पिता के चेहरे, वेदी के सींगों, अभिषेक का तेल, प्रजा का
वर्ष, etc.) — no counter-example found. The two original Joshua 1:1 examples:

- עֶבֶד יְהוָה "servant of the LORD" → "यहोवा **के** दास": के agrees with masculine दास
  ("servant"), not with यहोवा. के secondary to the possessed noun (दास); no separate
  Hebrew preposition token exists for it to be primary to.
  source=[עֶבֶד], target=["दास"] — primary: "दास"; secondary: "के";
  source=[יְהוָה], target=["यहोवा"] — primary 1:1.
- בִּן נוּן "son of Nun" → "नून **का** पुत्र": का agrees with masculine पुत्र ("son").
  source=[בִּן], target=["पुत्र"] — primary: "पुत्र"; secondary: "का";
  source=[נוּן], target=["नून"] — primary 1:1.

**Refinement — के vs. का depends on chain position, not just possessed-noun gender.**
Cross-checking OHCV on the same Joshua 1:1 construction ("नून **के** पुत्र यहोशू") and
GLT's independent Ruth 1:1 ("यहूदा **के** बैतलहम **का** एक पुरुष") both show the same
pattern: **के** is used when the possessed noun is mid-chain, immediately followed by
an appositive name/title (नून **के** पुत्र यहोशू — "Joshua, son of Nun," another name
follows), while bare **का/की** applies when the possessed noun is chain-final with
nothing else following. This is a genuine 2-translation-confirmed refinement to the
plain agreement rule above, not a contradiction of it — का/की/के still agree with the
possessed noun's gender/number/case; के's mid-chain appearance is an additional,
position-sensitive layer on top.

**Objective genitive with a light verb — CORRECTION, IRVHin-specific, not a general
Hindi-OT strategy.** An earlier draft claimed: when a Hebrew transitive verb is
rendered as a Hindi light verb (noun + करना), the logical direct object of that verb
takes का/की on the light-verb noun, exactly parallel to the ordinary construct-chain
treatment above, even though there is no Hebrew construct relationship or preposition
involved at all — confirmed 4+ times within IRVHin:

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

**Cross-checking OHCV on these same verses disproves the "general Hindi-OT strategy"
framing.** OHCV instead renders the same direct objects with an ordinary verb + DOM-को:
Genesis 1:1 → "परमेश्वर ने आकाश एवं पृथ्वी **को** रचा" (ordinary verb रचा + को, not
light verb + की). Genesis 9:11 is even more telling: OHCV *does* use a light-verb
rendering here (नाश करना) but still marks the object with **को**, not का — "पृथ्वी
**को**...नाश करूंगा." This also directly answers the open question below the ERGATIVE
ने AND ACCUSATIVE/DATIVE को section (does DOM-को ever appear when the Hebrew verb is
rendered as a light verb?): **yes**, in another translation — का/की-on-light-verb-
object is not even guaranteed to exclude को the way the original rule assumed. Treat
IRVHin's का/की pattern as a real, confirmed IRVHin-specific choice (4+ instances within
IRVHin itself), but check को first when working with any other Hindi OT edition rather
than assuming का/की transfers as a general Hindi strategy. Treat the object noun as
secondary (marked by का/की, when IRVHin's pattern is in play) to the light-verb noun,
which is itself primary in the light-verb record (see TOKEN ROLES and LIGHT AND VECTOR
VERBS).

**Construct chains of three or more links — CONFIRMED, with two refinements.** A
targeted search found 2,384 sequences of 2 consecutive construct-state nouns followed
by a third noun (genuine 3-word/2-link chains). The core rule holds cleanly: 2 Kings
18:33 יַד מֶלֶךְ אַשּׁוּר ("hand of king of Assyria") → "**अश्शूर के राजा के हाथ से**" —
two के postpositions chained, each secondary to the noun it follows and agreeing with
its gender (के→राजा, के→हाथ, both masculine), exactly per §11.5 of the base document.
No counter-example to the agreement rule was found. Two refinements:
- **בְּנֵי ("sons/children of") X routinely collapses an apparent 3-link chain into a
  single Hindi demonym/gentilic noun + one postposition**, not a spelled-out
  2-postposition chain: עֲדַת בְּנֵי יִשְׂרָאֵל ("community of sons of Israel") →
  "इस्राएलियों की...मण्डली" (Israelites + की + community — 1 postposition, not 2);
  מַחֲנֵה בְנֵי־דָן ("camp of sons of Dan") → "दानियों की छावनी" (Danites + की + camp).
- The idiomatic "all the days of the life of X" chain (כָּל יְמֵי חַיֵּי X) collapses the
  same way, consistently rendering "X की कुल आयु" ("X's total lifespan") rather than a
  literal 3-link chain.

Both collapses are lexicalization effects, not evidence the agreement rule breaks
down — Hebrew's 3+-link chains frequently surface with fewer links in Hindi because a
recurring "sons of X"/idiom pattern has its own established Hindi rendering, not
because का/की/के stops agreeing correctly.

**Construct definiteness:** the Hebrew article word-part on the absolute (genitive) noun
stays secondary per ARTICLES Branch B — Hindi's का/की/के construction already signals
the relationship, so no extra word is needed even when the article marks the whole chain
as definite. **HYPOTHESIS** — not directly isolated, though consistent with the
confirmed Branch B default.

**Still needs checking:** whether IRVHin ever uses bare noun-noun juxtaposition (parallel
to Indonesian's construct-chain strategy) instead of का/की/के for any construct chains —
not observed in the 21-instance corpus-scale sample either (tentative, not exhaustive).

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
  Hebrew token is the correspondent, only which Hindi lexeme surfaces.

  **CONFIRMED well beyond the single original example** by a corpus pass on two other
  recurring idioms: the "gathered to his people" death formula (אֶל עַמָּיו, 22 corpus
  instances) renders "अपने लोगों में जा मिला" in essentially every sampled instance
  (9/9 clean hits, never उसके लोगों); the "hardened his/their heart" idiom (אֶת־לִבּוֹ,
  object of a verb whose subject is the same referent) likewise takes अपने ("अपने मन
  को कठोर किया").

  **RESOLVED — verb-suffix and preposition-suffix reflexives, previously the doc's
  last open question on this topic.** A targeted search (filtering WLCM suffixes whose
  gloss/gloss2 itself contains "self," 480 corpus instances: 18 verb+suffix, 440
  preposition+suffix, 20 noun+suffix) found:
  - **Verb-suffix (18/18 checked, clean)**: consistently renders as **अपने को** or
    **अपने लिये**, never the ordinary object pronoun. Lev 21:4 הֵחַלּוֹ ("profane
    himself") → "वह अपने को...अशुद्ध न करे"; 2 Sam 22:24 אֶשְׁתַּמְּרָה ("kept myself") →
    "अपने को बचाए रहा"; 1 Kgs 21:20 הִתְמַכֶּרְךָ ("sold yourself") → "अपने को बेच डाला
    है." Treat exactly like the noun-suffix reflexive rule: primary 1:1 to the suffix
    word-part, अपने substituting for the ordinary object pronoun the suffix's own
    person/number would otherwise predict.
  - **Preposition-suffix (sampled ~20 of 440)**: real but more nuanced. Genuine
    benefactive-reflexive (referent = subject) often takes अपने/अपनी (Gen 6:21 "अपने
    पास इकट्ठा"; Gen 13:11 "लूत अपने लिये...चुन"). Just as often, though, the same
    reflexive-flavored Hebrew construction is instead **absorbed into a Hindi vector
    verb (ले) with no separate word at all** — not अपने, not उसे, simply gone (Gen 3:7
    "लंगोट बना लिये"; Gen 4:19 "स्त्रियाँ ब्याह लीं"; Gen 6:14 "जहाज बना ले" — the same
    light/vector-verb absorption pattern documented in LIGHT AND VECTOR VERBS, applied
    to a reflexive Hebrew idiom). Check for vector-verb absorption before assuming a
    separate reflexive word is required.
  - **New strategy, not previously documented anywhere: आप (ही)**, an intensive/
    agentive reflexive for the "by/of one's own agency" sense, distinct from अपना's
    possessive/objective reflexive. Gen 22:8: "परमेश्वर...आप ही करेगा" ("he himself will
    provide"); Gen 22:16: "मैं अपनी ही यह शपथ खाता हूँ" ("I swear by myself" — अपनी ही,
    stacking the possessive reflexive with the intensive particle ही).
  - **Methodological caution**: WLCM's "self" gloss on a suffix is not always a
    reliable coreference signal by itself — Gen 8:9's אֵלָיו is glossed "himself" but
    the referent is Noah, not the dove (the clause's grammatical subject), and IRVHin
    correctly renders it as ordinary "उसके पास," not अपने. Verify actual subject
    coreference rather than trusting the gloss.

- **Object suffix on verb** — suffix word-part present → primary 1:1, suffix → Hindi
  object pronoun (मुझे/तुझे/उसे/हमें/तुम्हें/उन्हें), or अपने को when coreferential with
  the clause subject (see above), or a DOM-को-marked noun phrase.
  Example (hypothesized): שְׁמָרֵנוּ "he kept us" → "उसने हमें रखा"-type construction:
  source=[shamarPart], target=["रखा"] — primary 1:1; source=[nuPart], target=["हमें"] —
  primary 1:1.

- **Suffix on preposition** — suffix word-part present → primary 1:1 to the Hindi
  pronoun object of the postposition, or अपने/अपनी (or vector-verb absorption with no
  separate word) when coreferential with the clause subject (see above). Example
  (hypothesized): אֵלָיו "to him" → "उसकी ओर"/"उसके पास"-type construction:
  source=[elPart], target=["ओर"/"पास"] — primary; source=[sufPart], target=["उसकी"/
  "उसके"] — primary.

---

## CONJUNCTIONS AND PARTICLES **[hin]**

Align content words first; conjunctions and particles are residual.

- Waw word-part (pos=conjunction) → "और"/"परन्तु"/"तब"/"तो"/"इसलिये": primary 1:1.
  Asyndeton → NEQ source.
- כִּי — **CONFIRMED at corpus scale.** Polyfunctional (causal, content-clause,
  conditional, temporal, emphatic, recitative — base document §13.2); a 25-instance
  sample across a spread of books confirmed the hypothesized mapping holds cleanly with
  no cross-contamination observed: causal → क्योंकि, content-clause → कि, conditional →
  यदि, temporal → जब. Align to whichever Hindi word carries its force in context.
  Recitative כִּי rendered with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — **CONFIRMED at corpus scale (15-instance sample, 2,110 corpus
  instances).** जो is the overwhelming default correspondent — matches the NT
  document's Greek-participle finding for जो almost exactly. Absorbed without
  correspondent → NEQ source.

---

## IDIOMS **[hin]**

`meta.is_idiom: true` when phrase-level correspondence has no token-level equivalent.
All tokens implicitly primary; `meta.secondary` does not apply.

Last resort — prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom
marking whenever the construction is a recognized light or vector verb rather than a
genuinely non-compositional phrase. Function-word-only source records are never idioms.

Three Hebrew idiom candidates from the base document were checked against actual
IRVHin renderings — **all three are negative results**:

- **חָרָה אַף** ("burn of nose" = become angry, 53 corpus instances) — **NOT an idiom
  in IRVHin.** Consistently renders compositionally with ordinary क्रोध/कोप +
  भड़कना ("कोप भड़का," "क्रोध भड़केगा") — ordinary token-level treatment applies, not
  `is_idiom`.
- **שׂים/שִׁית לֵב** ("set the heart" = pay attention, 19 corpus instances) — **NOT an
  idiom in IRVHin.** Renders variably and compositionally: मन लगाना, ध्यान देना,
  चिन्ता करना, मन हटाना — genuinely flexible lexical choices, not a fixed idiom either.
- **נָשָׂא פָּנִים** ("lift up the face" = show favoritism) — **RESOLVED, NOT an idiom
  in IRVHin.** The earlier zero-hit search was a lemma-spelling/diacritic mismatch, not
  genuine absence — WLCM's lemma field is inconsistently diacritized. Searching by
  Strongs number (H5375 + H6440 co-occurring in-verse) found 77 real candidate verses.
  Clear instances confirm the idiom's meaning is present in the Hebrew (Job 34:19, Prov
  18:5), but IRVHin renders it either with **Hindi's own light-verb idiom पक्ष करना**
  ("take a side," itself an ordinary light-verb-noun construction, not a special idiom
  marker) or with a free compositional paraphrase that drops "face" entirely (Lev
  19:15, Deut 28:50, 2 Kings 3:14 vary — "मुँह देखकर आदर करना," "मुआवजे में कुछ न लेगा").
  Use ordinary/light-verb token-level treatment, not `is_idiom` — the same negative
  result as the other two candidates above.

**All three idiom candidates from the base document turned out compositional or
light-verb, not phrase-level idioms** — a useful confirmation that IDIOMS' conservative
"last resort" stance is correctly calibrated for this config; only μὴ γένοιτο-style
fixed expressions (the NT document's own confirmed idiom, कदापि नहीं) have actually
earned `is_idiom: true` treatment across either testament so far.

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
  animacy); still secondary to the noun, not NEQ. **Resolved by cross-checking OHCV**:
  every direct-object case IRVHin itself uses (Genesis 1:1, 1:27, 9:11) took the
  objective-genitive-का/की pattern (see CONSTRUCT CHAINS AND GENITIVE POSTPOSITION)
  because the corresponding Hebrew verb was rendered as a Hindi light verb — but OHCV
  on the identical verses uses ordinary DOM-को instead, including in Genesis 9:11 where
  OHCV *also* uses a light-verb rendering ("पृथ्वी को...नाश करूंगा") but still marks
  the object with को rather than का. So DOM-को is real, confirmed, and can co-occur
  even with a light-verb rendering in another translation — check which pattern the
  specific translation in hand actually uses; do not assume का/की excludes को.

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

**Correction — the OT does NOT show the NT's near-parity between नहीं and न.** The NT
document found नहीं (1,611) and न (1,747) roughly co-equal in raw frequency. Full-corpus
OT counts are नहीं = 2,334, न = 5,128, मत = 189: **न outnumbers नहीं more than 2:1 in
the OT**, likely driven by poetry's (Psalms, Proverbs, Isaiah) heavier use of
parallelism-style negation, where repeated short negated cola favor the shorter/more
flexible particle. Do not carry over the NT's "roughly co-equal" framing — treat न as
the more frequent particle in the OT specifically.

- **नहीं** — general-purpose negator, usable with almost any Hebrew-sourced verb form,
  though न is actually the more frequent choice corpus-wide (see above). Confirmed:
  Genesis 2:5 כִּי לֹא הִמְטִיר → "यहोवा...**नहीं** बरसाया" (indicative past). Copula
  ellipsis after नहीं in predicate-nominal/adjectival clauses is common — not a gap to
  fill.
- **न** — interchangeable literary variant of नहीं for ordinary negation, and the
  numerically dominant particle in the OT. Confirmed with both future/modal (Ps 23:1
  לֹא אֶחְסָר "I shall not want" → "मुझे कुछ घटी **न** होगी") and imperative-flavored
  (Gen 3:1 לֹא תֹאכְלוּ "you shall not eat" → "**न** खाना") contexts — matches the NT
  document's finding that the split is not conditioned by mood. Also the dedicated
  correlative form for "neither...nor" lists — **not isolated in this pass**; needs
  checking whether Hebrew has a comparably explicit correlative-negation construction or
  whether it is expressed more freely (e.g. repeated לֹא across parallel cola in poetry,
  per the base document's parallelism guidance, §15).
- **मत** — ordinary colloquial prohibitive. **Not isolated in this pass** — no imperative
  אַל-negation instance was checked. Caution: homographic with an unrelated noun मत
  ("opinion") — disambiguate by syntactic position.

**Simple negation (לֹא)** → नहीं/न, per the base document's simple-negation treatment
(§13.5). **CONFIRMED** — see examples above.

**Existential negation (אֵין) — CONFIRMED at corpus scale.** The original draft guessed
a fixed "नहीं है"/"नहीं हैं" expression, parallel to Indonesian's fixed "tidak ada"
idiom. A corpus-scale check (785 true existential instances, `morph=='Tn'` — excluding
a small set tagged `Ti`, an unrelated interrogative "where" homograph the earlier
count conflated with it; a 20-instance random sample) confirms IRVHin does NOT use a
single fixed idiom: it uses a flexible नहीं/न + tense-agreeing copula construction —
"कोई...नहीं है" (present, the dominant pattern), "नहीं था"/"नहीं रहा" (past),
"नहीं होता" (habitual), and occasional "न हुआ"-type perfect forms — matching whatever
tense the surrounding narrative is in, still landing as a 1:N record against אֵין per
the base document's general אֵין guidance (§13.5) rather than Indonesian's single fixed
phrase. **कोई ("anyone/no one") is a common, though not universal, companion word** for
personal/countable referents — close to a formulaic skeleton without being maximally
free.
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

### Compound / discontinuous negation — CONFIRMED at corpus scale, stronger

The NT document and OT Indonesian both found a "no longer" construction (Greek
οὐκέτι/μηκέτι; Hebrew לֹא...עוֹד) that is discontinuous in the target language more
often than a naive contiguity assumption would predict (OT Indonesian: ~70% of 222
Hebrew לֹא...עוֹד verses render with the verb/modal intervening between "tidak" and
"lagi," not the contiguous "tidak lagi"). **Confirmed for Hindi at corpus scale**: 231
WLCM verses contain both לֹא and עוֹד (revising the original 217 estimate; note not
every such verse forms the "no longer" idiom, since עוֹד also independently means plain
"still/yet/again" — treat 231 as an upper bound). A fresh 25-verse random sample found
~11 genuine "no longer" renderings, of which 9 were discontinuous and 2 contiguous
(**~82%**, matching or exceeding the original 3-of-4/75% spot-check estimate). A new
lexical variant was also found in this slot: **आगे को** (Lev 27:20, Gen 35:10) functions
as a real alternative to फिर, not previously documented. The original 4 cited instances:

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

Hebrew passive stems (Niphal, Pual, Hophal — base document §12.4) map onto the same
multi-strategy inventory the NT document confirmed for Greek passives, since the
strategies themselves are properties of Hindi, not of the source language. **7 of 8
strategies are now confirmed** (up from 3), following a 33-instance fresh sample across
Exodus, Leviticus, Deuteronomy, Judges, 1–2 Samuel, 1–2 Kings, Psalms, Proverbs,
Jeremiah, and Ezekiel (5,024 total passive-stem verbs in WLCM), on top of the original
Isaiah 53:5 + Genesis examples:

1. **True periphrastic passive (participle/vector-compound + जाना) — CONFIRMED,
   repeatedly.** Isaiah 53:5: מְחֹלָל (Pual, "pierced") → "**घायल किया गया**" (घायल
   primary + किया गया secondary, a light-verb passive: घायल करना "to wound" + जाना);
   מְדֻכָּא (Pual, "crushed") → "**कुचला गया**" (कुचला primary, participle; गया
   secondary). Also confirmed in the follow-up sample: Lev 6:23 "पहुँचाया जाए," Judg
   17:2 "ले लिए गए थे."
2. **Stative-perfect (participle + copula, no जाना) — RESOLVED, with a refinement.**
   The OT's own recurring "it is written" formula (כָּתוּב, 103 corpus instances by
   lemma/morph search) splits into two context-conditioned patterns: the rhetorical
   citation formula ("is it not written in the book of...," 1 Kings 22:39/46, 2 Kings
   1:18, 2 Chron 9:29, 2 Chron 35:27) uses **bare participle+है/हैं** ("लिखा है"/"लिखे
   हैं") — an exact match to the NT document's γέγραπται→लिखा है Strategy 2 exception.
   The "written on tablets/scroll" physical-inscription sense (Exod 31:18, 32:15, Deut
   9:10, Esth 6:2, Neh 8:14, Jer 17:1) instead uses **participle+हुआ+copula** ("लिखा
   हुआ था/है/मिला"), which is really Strategy 6 rather than a bare Strategy 2 instance.
   Both are real, lexically-anchored variants of the same root — check which sense
   (citation-formula vs. physical-inscription) is in play.
3. **Adjectival/nominal resultative (adjective + होना/बनना) — CONFIRMED, now a
   3-way cross-testament AND cross-translation match.** Isaiah 53:5: נִרְפָּא (Niphal,
   "healed") → "**चंगे हो जाएँ**" — the identical चंगा+होना mapping the NT document
   found for ἰαθήσεται. Cross-checking OHCV on the same verse independently confirms
   this ("हम **चंगे हुए**") — two independent testaments AND two independent
   translations converging on the same lexical strategy for "healed," the strongest
   evidence in this document that the mapping is a stable feature of Hindi's lexicon,
   not coincidence. Genesis 21:5: הִוָּלֶד (Niphal, "was born") → "**उत्पन्न हुआ**"
   (उत्पन्न "arisen/produced" + हुआ "became"). Also confirmed repeatedly in the
   follow-up sample: Exod 4:4 "बन गई," Deut 4:26/28:24 "नाश हो जाओगे"/"हो जाएगा."
4. **Dedicated intransitive/unaccusative verb — CONFIRMED.** Judg 10:7 "न मिला"
   (मिलना, "to be found") — Hindi's own transitive/intransitive verb pairs absorbing a
   passive with no voice marking at all.
5. **Light-verb/noun+होना idiomatic construction — CONFIRMED, multiple instances, with
   a new auxiliary.** Exod 22:9 "चोट खाए" (खाना), Deut 33:13 "आशीष **पाए**" (**पाना**,
   "receive/obtain" — a newly documented light-verb passive auxiliary alongside
   होना/देना/बनना/खाना), Judg 5:20 "लड़ाई हुई," 1 Kings 8:5 "गिनती...नहीं हो सकती थी" —
   all distinct from Strategy 1's light-verb+जाना pattern in specifically lacking जाना.
6. **Bare resultative participle (+ हुआ/हुई/हुए, no finite copula) — CONFIRMED.** Lev
   7:9 "पके हुए" (baked/cooked). Also the "written on tablets" sub-pattern of Strategy
   2 above (participle+हुआ+copula) belongs here structurally.
7. **Active-voice conversion — remains a marginal strategy, not upgraded.** Lev 5:23's
   stolen-goods clause recasts the Hebrew passive as an active Hindi clause. A dedicated
   follow-up search (30 fresh Niphal/Pual/Hophal instances across Numbers, Ruth, Ezra,
   Nehemiah, Ecclesiastes, Lamentations, Ezekiel) found **no additional instances** —
   every case sampled classified cleanly into one of the other 7 strategies instead
   (e.g. Ezek 16:4's four passives all stayed passive via जाना; Ezek 30:22 adjectival;
   Neh 5:8/Num 9:21 dedicated intransitive). Treat Strategy 7 as real but genuinely
   rare — Lev 5:23 is still the best evidence for it, not one example among a larger
   confirmed set.
8. **Naming/equational conversion — CONFIRMED, translation-dependent.** Genesis 2:23:
   יִקָּרֵא ("she shall be called") → "**इसका नाम नारी होगा**" ("her name will be
   woman/nari") — the passive verb is dropped entirely in favor of a naming/equational
   sentence, exactly parallel to the NT document's Revelation 19:13 example (उसका
   नाम...है for κέκληται). **Confirmed translation-dependent, like the NT finding**:
   OHCV on the same verse instead keeps a periphrastic passive verb ("उसे 'नारी' **नाम
   दिया जायेगा**," Strategy 1) — check which strategy the specific translation in hand
   uses rather than assuming Strategy 8 for every "shall be called" passive.

**Methodological caveat**: at least one Niphal encountered in the follow-up sample
(Judg 21:5 שָׁבַע "swore," a deponent reflexive-middle form, rendered actively "शपथ
खाई") is not a real semantic passive — the same deponent-verb caution the NT document's
passive-voice pass flagged for Greek middle/passive-form verbs like γίνομαι. Exclude or
separately tag these in any further sampling from the Niphal/Pual/Hophal set.

**Theological/divine passive — corrected, was unsupported by real text.** The original
hypothesis (Hebrew sometimes uses the passive to imply divine agency without naming
God; IRVHin might make the divine agent explicit with no Hebrew token, and that
supplied noun would then be NEQ target, base document §12.4) was checked against a
15-verse sample of candidates (passives with no divine-name token anywhere in the
verse, but with परमेश्वर/यहोवा present in IRVHin) and **not confirmed** — no clean
"passive verb → active clause with supplied God as agent" instance was found; the
passive verbs themselves stayed passive with no agent supplied at all (e.g. Job 9:24's
אֶרֶץ נִתְּנָה, "the land is given," stays passive in Hindi too).

**What actually recurs instead is a different, related phenomenon**: IRVHin supplies
परमेश्वर/यहोवा to disambiguate an unnamed third-person pronoun or possessive suffix
whose antecedent is God only from wider discourse context — a supplied-pronoun-
referent pattern, not a passive-voice-specific rule. Job 20:28 נִגָּרוֹת בְּיוֹם אַפּוֹ
("swept away in the day of *his* anger") → "परमेश्वर के क्रोध के दिन," supplying the
referent of "his"; Job 9:24 פְּנֵי שֹׁפְטֶיהָ יְכַסֶּה (an active verb with an unstated
3ms subject) → "परमेश्वर...मूँद देता है." Treat the supplied परमेश्वर/यहोवा as NEQ
target when it disambiguates a pronoun/suffix this way (per the base document's general
supplied-referent guidance), but do not expect it specifically tied to passive-voice
constructions — it is a pronoun-resolution phenomenon that happens to co-occur with
passives sometimes, not a passive-specific strategy.

---

## PARTICIPIAL CONSTRUCTIONS **[hin]**

Hebrew participles (base document §12.7) serve adjectival, substantive/nominal, and
verbal/predicative (continuous) functions — structurally different from Greek's
article+participle substantive construction, so this section needs more careful
adaptation than most.

- **Adjectival participle** — aligns to Hindi adjective or participial modifier,
  primary.
- **Substantive (nominal) participle — CONFIRMED at corpus scale.** A 40-instance
  sample from 1,479 article+participle pairs found जो + finite verb/relative clause
  dominant (~55%), वाला real but smaller (~10%), and a third "neither" outcome —
  a plain lexicalized noun or bare finite clause with no relativizer — larger than the
  NT document found for Greek (~32%, e.g. "पहरेदार जो..." using पहरेदार as a bare noun
  rather than a वाला-compound; "वे...तोड़ लेते" as a bare finite clause). जो dominance
  holds, matching NT's finding, but expect this third "neither" outcome to show up more
  often in OT narrative than it did in the NT sample — check for a natural lexicalized
  noun before assuming जो or वाला applies. वाला remains reserved for participles that
  compress into a stable, lexicalized agent-noun or role label, parallel to its NT
  restriction.
- **Verbal (predicative) participle — continuous/progressive** — participle primary;
  Hindi progressive auxiliary (है/था/थी) secondary. Parallel to base document's יֹשֵׁב
  example.
- **Participle + הָיָה (periphrastic construction) — CONFIRMED.** 112 adjacent
  participle+הָיָה instances found corpus-wide; a spot check consistently shows Hindi
  using verb+था/रहा था for this periphrastic-imperfect sense (e.g. "चराता था," 1 Chr
  12:17 "उपासना...करती रहीं"). When הָיָה is explicit, it aligns as a primary record to
  the Hindi auxiliary (था/थी/थे); the participle aligns to the main verbal element,
  also primary — two separate primary records, confirming the base document's
  2-record hypothesis. This is consistent with Hindi's own periphrastic default
  (participle + copula is *always* the ordinary way to form these tenses in Hindi, not
  an optional stylistic choice) layering onto Hebrew's own independent periphrasis.

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

**Correction — के लिये is NOT the confirmed default; को is at least as common.** The
original 2-instance spot-check (both light-verb infinitives) matched the NT document's
finding that के लिये is the translation-independent default, and this document
originally treated that as confirmed. **A corpus-scale check overturns that framing**:
4,572 לְ+infinitive-construct instances exist corpus-wide; excluding לֵאמֹר ("saying,"
939 instances, almost always → कि introducing reported speech, not a purpose
construction at all), a 25-verse sample of the remaining 3,633 found **को (10/25, 40%)
more common than के लिये (6/25, 24%)**. को deserves at least equal billing as a
purpose-infinitive strategy for this config — do not default to के लिये; check the
specific verse. The original two cited instances:

- Genesis 2:5: לַעֲבֹד אֶת־הָאֲדָמָה ("to work the ground") → "भूमि पर खेती **करने के
  लिये**" — लְ → के लिये, primary; the infinitive (עָבַד) → करने, primary (करने itself
  is the light-verb component of खेती करना "to farm").
- Genesis 9:11: לְשַׁחֵת הָאָרֶץ ("to destroy the earth") → "पृथ्वी का नाश **करने के
  लिये**" — לְ → के लिये, primary; the infinitive (שָׁחַת) → करने, primary (करने is again
  the light-verb component of नाश करना "to destroy"; पृथ्वी का is the objective genitive
  of नाश per CONSTRUCT CHAINS AND GENITIVE POSTPOSITION, not related to לְ at all).

Both original instances happen to involve a light-verb infinitive (करने के लिये rather
than a single-word infinitive) — the corpus-scale sample shows this was not
representative: को appears freely across both light-verb and simple-infinitive
renderings. Check which strategy a given verse actually uses rather than assuming
के लिये.

**Infinitive construct as verbal noun** (בְּ + infinitive → "when/while/in ...-ing," base
document §12.5): the infinitive aligns to the Hindi main verbal element; the preposition
word-part aligns to the Hindi temporal/logical connector (जब, जैसे ही, में) as primary.

### Infinitive absolute (cognate emphasis)

**CONFIRMED.** Hebrew's infinitive absolute + cognate finite verb for emphasis (מוֹת
תָּמוּת "you shall surely die," base document §12.6) — 882 total infinitive-absolute
forms corpus-wide, 433 adjacent cognate pairs. A 12-instance sample confirms the
Hindi emphasis-adverb hypothesis, with **निश्चय specifically the recurring choice**
("तू निश्चय मरेगा," "यह निश्चय बताया गया," "मैं निश्चय...दूँगा" ×2) — अवश्य/ज़रूर are
plausible synonyms but निश्चय is what actually shows up repeatedly. Infinitive absolute
primary to निश्चय; finite verb primary to the main Hindi verb, per the base document's
two-primary-record treatment. If the translation absorbs the emphasis into a strong
modal without a separate word, the infinitive absolute may be secondary to the finite
verb, or NEQ if definitively untranslated.

---

## Cross-translation methodology note

**A single-translation ~15-verse spot-check was followed by a two-part verification
pass**, matching the discipline the NT Hindi document already established. The
original spot-check joined `WLCM.tsv` (Hebrew source) to `ot_IRVHin.tsv` by verse and
inspected roughly 15 verses (Genesis 1:1, 1:27, 2:5, 2:23, 3:1, 8:12, 8:21, 9:11,
11:30, 21:5; Joshua 1:1; Psalm 23:1; Isaiah 53:5), chosen to cover articles, construct
chains, pronominal suffixes, ergative ने, negation, existentials, and passive voice.
This confirmed most carried-over NT-document findings and surfaced two OT-specific
findings not present in the NT document at all: the objective-genitive-का/की rule for
light-verb direct objects, and the reflexive अपना/अपने rule for subject-coreferent
possessive suffixes.

**Cross-translation check** (paralleling the NT document's HSB/OHCV check): against
OHCV (full OT coverage) and GLT (partial OT coverage — only Ruth, Ezra, Nehemiah,
Esther, Obadiah, Jonah; none of this document's original citation verses fall in GLT's
coverage, so GLT contributed mainly to the Joshua 1:1/Ruth 1:1 construct-chain
refinement). **GST was deliberately excluded** (per explicit direction, matching the
NT document's exclusion). This check **overturned one claim outright**: the objective-
genitive-का/की rule is IRVHin's own lexical choice, not a general Hindi-OT strategy —
OHCV uses ordinary DOM-को on the identical direct objects (see CONSTRUCT CHAINS AND
GENITIVE POSTPOSITION). It also resolved both of the document's previously flagged
"highest priority" open questions: the כָּתוּב ("it is written") formula (two
context-conditioned patterns found) and the הָאִישׁ הַהוּא demonstrative-after-article
construction (confirmed productive once the search broadened beyond an exact token-
spelling match). It confirmed the reflexive अपने rule (OHCV independently uses अपने on
Gen 1:27), ने ergative, the आदम proper-name convention, and Strategy 3's चंगा+होना
passive mapping (now a 3-way cross-testament/cross-translation match). It flagged the
naming-passive strategy (§8) and one article instance (Gen 3:1) as translation-
dependent rather than settled defaults.

**Corpus-scale check** (paralleling the NT document's full-corpus frequency-count
pass): full-corpus joins/counts against WLCM.tsv+IRVHin, covering sections that were
previously untested hypotheses (participles, infinitives, pronominal-suffix
generalization, idioms, conjunctions) or backed by only a handful of examples
(negation, passive voice, articles, construct chains). This expanded passive voice
from 3 to 7 of 8 confirmed strategies, confirmed construct chains and כִּי/אֲשֶׁר at
scale with no counter-examples, found a genuine OT-specific difference from the NT
(न outnumbers नहीं more than 2:1 in the OT, vs. near-parity in the NT — likely a
poetry/parallelism effect), and **overturned the claim that के लिये is the confirmed
purpose-infinitive default** — को is at least as common once לֵאמֹר is excluded. Two
candidate idioms (חָרָה אַף, שׂים לב) turned out to render compositionally, not
idiomatically.

What held up unchanged from the NT document: ergative ने, नहीं/न split by discourse
function (not mood, though the OT's frequency balance differs — see NEGATION), light-
verb N:1 treatment, the general shape of the passive-voice strategy inventory, article
Branch B default, and (via the לֹא...עוֹד parallel, now stronger at ~82%) discontinuous
"no longer" negation.

What remains genuinely new to the OT document: the objective-genitive-का/की rule (now
correctly scoped as IRVHin-specific, not general), the reflexive अपना/अपने rule (now
generalized to two more recurring idioms plus true verb-suffix and preposition-suffix
cases), the के-vs-का mid-chain construct-chain refinement, पाना as a newly documented
light-verb passive auxiliary, and आप (ही) as an intensive/agentive reflexive strategy
with no NT counterpart.

**A third, targeted follow-up pass** then closed out nearly every item still marked
open after the first two passes: it resolved the verb-suffix/preposition-suffix
reflexive question (with a genuinely new strategy, आप ही, surfacing along the way),
confirmed 3+-link construct chains (with two lexicalization-collapse refinements),
confirmed existential אֵין at real corpus scale (785 instances, not the earlier
estimate), identified the -कर conjunctive participle's actual Hebrew trigger
(wayyiqtol narrative chains — a clean resolution of a standing hypothesis), resolved
the נָשָׂא פָּנִים idiom search (a lemma-diacritic bug, not genuine absence — and, once
found, not an idiom in IRVHin either), and **corrected** the theological/divine-passive
hypothesis outright: the original passive-voice framing was not supported by real
text; what actually recurs is a distinct supplied-pronoun-referent phenomenon. Only
Strategy 7 (active-voice conversion) and the जब तक...न-for-עַד question remain without
a clean resolution — see Open questions below.

## Open questions for native-speaker and TSV-data review

Every item from the original open-questions list has now been investigated (most
resolved; a few produced a genuine correction rather than a confirmation) except
native-speaker review itself. What remains:

- **Genuinely unresolved, not investigated further**: does the जब तक...न false-friend
  trap (confirmed in the NT document) recur identically for Hebrew עַד ("until")
  constructions? Not checked in any pass.
- **Fine-grained, not corpus-decidable**: does IRVHin's construct-chain rendering ever
  use bare noun-noun juxtaposition (the Indonesian strategy) instead of का/की/के? Not
  observed in any sample so far (21-instance corpus-scale check, plus the 2,384-
  instance 3+-link search) — tentative, not exhaustive; a native speaker may know of a
  register or genre where it occurs.
- **Passive-voice Strategy 7 (active-voice conversion)** remains genuinely rare —
  confirmed marginal, not upgraded, after a 30-instance targeted follow-up search found
  no additional clear examples beyond Lev 5:23.
- **A new item from this pass**: is आप (ही) — the newly documented intensive/agentive
  reflexive strategy — productive beyond the two Genesis 22 instances found, or a
  narrower idiom than अपना/अपने's possessive reflexive? Worth a dedicated look if this
  document is extended further.
- This document has not been reviewed by a native Hindi speaker, matching the NT
  document's draft status — the one check no amount of corpus analysis substitutes
  for, especially now that this document has moved from mostly-hypothesis to
  mostly-corpus-confirmed.
