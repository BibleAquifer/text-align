# Alignment Principles — Arabic (arb), Old Testament

Guidelines used by `refine-alignment` when aligning the Arabic Van Dyck Bible (AVD)
against the Hebrew Old Testament (MACULA Hebrew / Westminster Leningrad Codex) source.

Sections marked **[arb]** contain Arabic-specific rules or examples. Unmarked sections
follow the shared structural conventions of the English guidelines
(`alignment-principles-ot.md` and `prompt/ot/eng.py`).

Examples are grounded in `data/targets/AVD/ot_AVD.tsv` checked against the Hebrew source
TSV (`data/sources/WLCM.tsv`), and cross-checked against a second, independently-
translated Arabic OT — ONAV (Open New Arabic Version, the same more dynamic/idiomatic
translation used for the NT cross-check) — via `data/targets/ONAV/ot_ONAV.tsv`, to
separate general Arabic grammar from AVD's own stylistic/register choices, following the
same methodology as `alignment-principles-nt.arb.md`. Sampling covered: Genesis 1:1-2
(creation, construct chains, article fusion), Genesis 2:23 (bone/flesh idiom, pronominal
suffixes), Genesis 2:17 and 24:2-3 (infinitive absolute, temporal infinitive construct,
construct chains), Genesis 4:2 (occupational participle + construct complement),
Genesis 19:17 (jussive negation, purpose clause), Deuteronomy 6:4-5,7 (nominal negation,
pronominal suffixes, temporal infinitive construct x4), Numbers 23:19 (nominal and
indicative negation), Joshua 1:1 (construct chains, participle-as-title, formulaic
לֵאמֹר), Judges 21:25 (existential negation), Psalm 23:1 (construct chain with
pronominal suffix). A second pass then re-verified NEGATION (existential אֵין/אַיִן and
the לֹא...עוֹד discontinuity) and CONSTRUCT CHAINS (the occupational-participle
exception) at full-corpus or full-corpus-derived-sample scale, and ARTICLES with a
precise full-corpus demonstrative-cooccurrence count — see the Cross-translation
methodology note near the end for what changed.

Source files: `src/text_align/refine/prompt/ot/arb.py`,
`src/text_align/refine/prompt/ot/eng.py`

**Draft status:** this document has not yet been reviewed by a native Arabic speaker or
Arabist, and follows `alignment-principles-nt.arb.md` in that respect. The sample here
(~15 verses, one dedicated pass per construction rather than NT arb's later 20-30-verse
stratified samples) is considerably thinner than even NT arb's initial draft — treat
every rule below as a well-evidenced working hypothesis grounded in real AVD/ONAV data,
not an established fact. Do not use for production alignment runs until reviewed.

**Key differences from OT English (eng.py), inherited from NT Arabic:**

- **AVD's OT target TSV tokenizes on whitespace only, and Arabic orthography fuses
  conjunctions (وَ/فَ), prepositions (بِ/لِ/كَ), the definite article (ال), and
  pronominal suffixes onto the adjacent word with no space** — identical mechanism to
  NT Arabic, and if anything more pervasive in OT prose, where waw-consecutive narrative
  chains produce a fused وَ- on nearly every clause-initial verb. One Arabic token
  routinely corresponds to 2-4 Hebrew word-part tokens (conjunction + article + noun +
  pronominal suffix all fused, e.g. Genesis 1:1's `وَٱلْأَرْضَ` = wa- "and" +
  al- "the" + arḍ "earth"). N:1 records are the dominant pattern, as in NT Arabic.
- **Construct-state (ʾiḍāfa) genitive chains** carry no linking word between the two
  Hebrew construct nouns, and Arabic's own ʾiḍāfa uses the identical bare
  noun-noun juxtaposition — this is a genuine structural match between Hebrew and
  Arabic, not merely a parallel to NT Greek's genitive-case construct. Confirmed
  repeatedly and consistently (`בֵּית ה' → بَيْت الله`-type examples throughout the
  sample): unlike NT Arabic (which supplies iḍāfa for a Greek case-marked genitive that
  Arabic itself doesn't mark morphologically), OT Arabic and OT Hebrew share the exact
  same construction — no supplied secondary "of"-equivalent is ever needed for a true
  Hebrew construct chain, parallel to Indonesian's OT finding (`ot/ind.py`) but for a
  different underlying reason (typological identity, not simplification). **Verified at
  scale** (28-verse exhaustive sample of construct-participles after הָיָה/וַיְהִי):
  bare ʾiḍāfa is the actual majority even for occupational-title participles
  (armor-bearer, ark-bearers, archer all stayed bare) — the one confirmed supplied-
  preposition pattern is a specific lexicalized `אֲבִי` + participle idiom ("father
  of..."), not a general occupational-participle rule. See CONSTRUCT CHAINS below.
- **Definite article ال (al-)** — same open question inherited from NT Arabic: this
  document treats the fused article as primary (not secondary, unlike every other
  supported OT language), since it is a real definite-article morpheme with a
  productive definite/indefinite semantic contrast in Arabic, the same reasoning
  `alignment-principles-nt.arb.md` gives. Because the article is always fused, Branch B
  (no separate word) is effectively the *only* outcome — there is no OT-Arabic analogue
  to Indonesian's occasional itu/ini Branch A supplement, since Arabic's demonstrative
  pronouns (هَذَا/ذَلِكَ) are separate, non-fused words that align to an explicit Hebrew
  demonstrative token (הוּא/הִיא/זֶה/זֹאת) when one is present, not to the article.
- **Passive voice** — not a dedicated OT-config block (the shared `ot/eng.py` block set
  has no PASSIVE_BLOCK, unlike NT's), so this document folds it into a dedicated
  PASSIVE VOICE section under general prompt guidance rather than a conditional block.
  **Sampled at scale (30-verse stratified sample across niphal/pual/hophal, ~5,024
  corpus instances):** true morphological passive is even more dominant here than NT
  Arabic's own (already-revised) finding — ~77% of clean instances. A derived-stem
  active-form verb (Form V/VII/VIII) is real but narrow, clustering around reciprocal/
  collective/self-affecting actions (dividing, gathering, adopting a name), closely
  matching NT Arabic's physical/experiential-change-of-state clustering. A genuine
  fourth strategy not found in NT Arabic: plain adjectival/stative rendering for niphal
  forms marking an inherent state rather than a passive event. See PASSIVE VOICE below.
- **Pronominal suffixes — REVISED after a broader sample across all host types (~47,000
  corpus instances total).** The deciding factor is the suffix's grammatical ROLE
  (subject vs. object/possessor), not which kind of word it attaches to, a finding NOT
  present in any other OT config. Object suffix or possessive suffix — on a noun, a
  preposition, a finite verb, a participle (used either nominally or verbally), OR an
  infinitive construct's OBJECT — is always PRIMARY, fused onto whatever Arabic word
  ends up carrying it, exactly like NT Arabic and Indonesian's -ku/-mu/-nya. Only a
  suffix marking the SUBJECT of an infinitive construct specifically (e.g. `שִׁבְתְּךָ`
  "your sitting," `מָלְכוֹ` "his becoming king") is SECONDARY, absorbed when Arabic
  restructures the infinitive as a finite clause — Arabic's own verb agreement
  morphology (e.g. `تَجْلِسُ`, already 2ms) already carries that information. See
  PRONOMINAL SUFFIXES below for the full breakdown, including infinitive-construct
  OBJECT suffixes (which remain primary, unlike the subject-marking case).
- **Negation** particle choice largely mirrors NT Arabic's findings translated to OT
  morphology: לֹא and אַל (Hebrew's two distinct negators, indicative vs.
  jussive/prohibitive) both converge on Arabic لَا regardless of the Hebrew mood
  distinction — the same convergence NT Arabic found for Greek's separate
  imperative/subjunctive prohibition moods. Nominal/copular negation (`לֹא אִישׁ אֵל`
  "God is not a man") uses `لَيْسَ`, matching NT Arabic's `laysa`-for-copular-negation
  finding exactly. **Existential אֵין/אַיִן — verified at scale (24-verse stratified
  sample of 659 corpus-wide instances):** three coexisting strategies, none a single
  fixed phrase the way Indonesian's "tidak ada" is — `لا النافية للجنس` (bare لَا +
  accusative predicate, no copula) is the single most common overall, especially in
  poetic/wisdom books; `لَيْسَ` (often with `مَنْ`, "there is no one who...") is a close
  second; `لَمْ يَكُنْ` (negated "to be") is real but narrower, clustering in narrative
  prose with a definite concrete-noun subject. **`לֹא...עוֹד` ("no longer") — verified
  at scale (20-verse stratified sample of the 222 corpus-wide co-occurrence verses):**
  confirmed discontinuous, matching NT Arabic's οὐκέτι/μηκέτι and Indonesian OT's own
  finding — the negator fuses to the verb while the "again"-adverb trails at clause end.
- **Infinitive absolute — REVISED at scale (20-verse sample of 730 corpus instances);
  the original single-verse framing does not hold.** Arabic's own maṣdar used as a
  cognate accusative (`مَوْتًا تَمُوتُ`-type constructions) is a genuinely closer
  structural parallel than any other currently-supported language has, and IS a real,
  fairly common strategy (~half of clean paired instances) — but it is NOT a reliable
  AVD default with ONAV as the adverbial alternative, as the original single-instance
  finding suggested. Completely unmarked (no cognate accusative, no adverb, the
  emphatic force simply dropped) is equally common, including within AVD itself — the
  variation is genuinely per-instance, not a stable translation-register split. A
  separate, non-paired usage (a string of bare infinitive absolutes as imperatival
  commands, no matching finite verb) always renders as ordinary finite verbs. See
  INFINITIVAL CONSTRUCTIONS below.
- **Temporal infinitive construct** (Hebrew's `בְּ`/`כְ` + infinitive construct, "when/as
  X happened") renders as an ordinary finite clause introduced by `حِينَ`/`لَمَّا`
  ("when"), never as a nonfinite Arabic form — the identical mechanism NT Arabic uses
  for `ἐν τῷ` + infinitive, and Indonesian OT uses for the same Hebrew construction.
  Confirmed 5x across two separate samples (Deuteronomy 6:7's four instances, Genesis
  2:17's one instance).
- **Purposive/complement `לְ` + infinitive construct — NEW, checked against a 14-verse
  sample of the single largest infinitive category (4,573 corpus instances).** Three
  coexisting strategies: purposive `لِ`/`لِكَيْ` + subjunctive verb (majority, for
  genuine purpose clauses); `أَنْ` + subjunctive complement clause (for infinitive
  complements of volition/refusal/permission verbs, matching NT Arabic's `أَنْ`
  strategy exactly); nominalization (masdar + preposition, real but less common,
  mostly fixed idiomatic phrases like "for going out and coming in"). The same
  Hebrew construction (`בִּלְתִּי`+infinitive, "so as not to X") was found rendered
  three different ways across the sample — genuinely translator-variable.
- **Substantive/attributive participles — verified at scale, three-way split matching
  NT Arabic's ism al-fāʿil/الَّذِي/مَنْ structure.** Genuine Arabic participle (ism
  al-fāʿil, e.g. `הַ+מֹּשֵׁל → ٱلْمُسْتَوْلِي`) for attributive modification of a
  specific/already-identified referent or occupational title — matching NT Arabic.
  `ٱلَّذِي` relative clause when the participle governs a direct object or names a
  specific historical group. **`كُلُّ مَنْ`/`كُلُّ مَا` is the dominant strategy
  specifically for Hebrew's casuistic/conditional legal formula `כָּל הַ` + participle
  ("whoever/whatever does X, Y")** — confirmed against a targeted 96-instance
  full-corpus search, resolving the open question Indonesian OT flagged as unproductive
  via its own similar search. The formulaic quotative `לֵאמֹר` ("saying," introducing
  direct speech) renders as `قَائِلًا`, the exact same fixed participle NT Arabic found
  for Greek `λέγων` — a striking cross-testament confirmation that this is a stable
  Arabic Bible-translation convention, not coincidence.
- **Predicative participles (participle as the main clause predicate) — verified at
  scale, and the finding REVERSES the original single-instance assumption.**
  Conversion to a finite verb (imperfect or perfect, depending on the reading) is the
  MAJORITY strategy, not a bare Arabic participle predicate — bare-participle
  predication is real but a minority pattern clustering around specifically
  postural/stative verbs (standing, sitting), since Arabic's own active participle most
  naturally expresses a resultant state rather than an ongoing dynamic action. A rarer
  third strategy substitutes a lexicalized noun/title as the predicate entirely (`God
  ... הוּא ← هُوَ ٱلدَّيَّانُ` "He is THE JUDGE"). See PARTICIPIAL CONSTRUCTIONS below.
- **Dual number — verified at scale (1,933 corpus instances sampled).** The
  straightforward Hebrew-dual-to-Arabic-dual match is the majority pattern (knees,
  feet, "two years," etc.) but is NOT automatic: real lexeme-specific exceptions exist
  where Hebrew's dual collapses to Arabic singular (`nostrils → nose`) or plural
  (`double doors → مَصَارِيعُ`, `eyelids → أَجْفَانِي`) — even within the same verse,
  one paired body-part noun matched dual-to-dual while another collapsed to plural. See
  SURFACE FORM DIFFERENCES below.

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

Word-part present → align Arabic correspondent primary to that token. No word-part
(morpheme merged into main token) → align correspondent primary to the main token.

---

## TOKEN ROLES **[arb]**

- **primary** — direct lexical or semantic connection to the Hebrew token
- **secondary** — exists because of Hebrew grammar with no separate source token
  (construct relation, verbal morphology, merged definiteness)
- correspondence to a different Hebrew token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

**Common secondary cases:**

- **Subject pronoun (pro-drop)** — Arabic finite verbs mark subject person/number/gender
  through circumfixal agreement morphology, so a dropped subject pronoun is fully
  recoverable from the verb form itself — grammar-guaranteed pro-drop, matching NT
  Arabic exactly. When a Hebrew waw-consecutive verb introduces a new clause with no
  separate pronoun token, no supplied Arabic pronoun is expected — the verb's own
  conjugation carries the subject. When a distinct subject noun follows in Hebrew, it
  gets its own record as usual.

- **No linking word for a true construct chain** — Arabic's own ʾiḍāfa construction
  juxtaposes head noun + modifier noun directly, matching Hebrew's own construct order
  exactly; no secondary "of"-equivalent is needed (see CONSTRUCT CHAINS).

- **Merged article** — no article word-part; the noun's al- is fused with no separate
  word boundary, but (unlike every other OT config) this document treats the article as
  PRIMARY to the noun's record rather than secondary — see ARTICLES for the open
  question this raises.

- **Suffix marking the subject of an infinitive construct** — when a Hebrew pronominal
  suffix on an infinitive construct (e.g. שִׁבְתְּךָ "your sitting") marks the
  infinitive's subject, and the translation restructures the infinitive as an Arabic
  finite clause, Arabic's own verb agreement morphology (already inflected for
  person/number, e.g. تَجْلِسُ "you sit," 2ms) absorbs that information — the suffix
  is secondary to the finite verb's record, with no separate Arabic word. See
  INFINITIVAL CONSTRUCTIONS.

- **Fused possessive/object clitic** — Arabic's pronominal suffixes (-ي/-ك/-ه/-ها/-نا/
  etc.) attach directly onto the noun, preposition, or verb they modify, forming ONE
  Arabic token. When Hebrew expresses this with a pronominal-suffix word-part, BOTH the
  head token and the suffix word-part are primary, sharing the single fused target
  token — same mechanism as NT Arabic and as Indonesian's -ku/-mu/-nya.
  Example: עֲצָמַי → عِظَامِي "my bones": source=[עֶצֶם-noun, sufPart],
  target=["عِظَامِي"] — both primary.
  Example: אֱלֹהֵי+נוּ → إِلَهُنَا "our God" (construct noun already fused with the
  suffix in one Arabic word): source=[אֱלֹהֵי-noun-construct, sufPart],
  target=["إِلَهُنَا"] — both primary.

---

## NEQ (NON-EQUIVALENT) **[arb]**

NEQ is a positive claim that no correspondence exists — never a fallback for
uncertainty. Unrecorded means correspondence was not determined (normal). NEQ records
must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ").
- Uncertain → leave unrecorded.

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases
(marks definite direct objects; Arabic has no equivalent particle — case marking alone
covers this).

Supplied copula with no Hebrew verb token → NEQ target (verbless clause) when the
translation supplies an explicit Arabic copula word (rare — Arabic verbless clauses are
usually left verbless in translation too, unlike English's obligatory "is").

Waw conjunction + Arabic asyndeton → waw word-part NEQ source (rare — Arabic's own
narrative style almost always preserves the waw as a fused وَ-, unlike Indonesian which
drops it more freely).
Arabic conjunction with no Hebrew conjunction token → NEQ target.

Bare transliterated proper name with a Hebrew article token (e.g. הַ before a name in
apposition) → NEQ source, since Arabic never fuses al- onto a bare transliterated proper
name — same rule as NT Arabic.

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent
alignment. Align on lexical/semantic correspondence.

**Dual number — verified against a 7-verse stratified sample of the 1,933 corpus dual
nouns.** Biblical Hebrew has a living dual (for paired body parts, time units, etc.),
and Arabic also has a fully productive dual — unlike NT Greek, whose dual has no living
Greek counterpart to align against. The straightforward Hebrew-dual-to-Arabic-dual match
DOES hold as the majority pattern (~5 of 8 clean instances: knees, hands/sides
[idiomatic "spacious of hands" → `ٱلطَّرَفَيْنِ` "the two sides," still dual though a
different lexeme], "two years," feet, and one eye of a suffixed pair). But it is not
automatic — real exceptions exist for specific lexemes/idioms, where Hebrew's dual
collapses to Arabic SINGULAR or PLURAL instead:
- אַפָּיו "his nostrils" (dual, idiom "breathed into his nostrils") → `أَنْفِهِ` "his
  nose" — Arabic SINGULAR; the breath-of-life idiom treats the nose as one organ, not a
  literal pair, despite Hebrew's dual morphology.
- דְּלָתַיִם "double doors/gates" (dual) → `مَصَارِيعُ` — Arabic PLURAL, not dual;
  paired-object nouns like doors don't automatically trigger Arabic's dual just because
  Hebrew marks them dual.
- עַפְעַפַּי "my eyelids" (dual + suffix, in the SAME verse as a dual eye that DID
  render as Arabic dual) → `أَجْفَانِي` — Arabic PLURAL, showing the exception is
  lexeme-specific, not predictable from "body part" alone (two paired body-part nouns
  in one verse, one matched dual-to-dual, the other collapsed to plural).

Check the specific target-language lexeme rather than assuming dual transfers
automatically — the default expectation (dual→dual) is reliable for count nouns used
literally (knees, feet, "two years"), but idiomatic or conventionally-singular/plural
body-part expressions in Arabic (nose, eyelids, and likely others not yet checked) are
a real, lexeme-conditioned exception.

---

## PASSIVE VOICE **[arb]** — NEW, based on a 30-verse stratified sample

**Not sampled at all in Pass 1 — added in Pass 2.** Hebrew marks passive/reflexive/
reciprocal/middle voice through derived verbal stems (binyanim), primarily niphal (נִפְעַל,
~4,144 corpus instances), pual (פֻּעַל, ~461), and hophal (הֻפְעַל, ~419) — 5,024 tokens
total, none independently examined until this pass. Sampled 30 verses stratified across
all three stems (every ~167th instance in corpus order), narrowed to instances with a
clear semantic reading, checked against both AVD and ONAV. Four coexisting strategies
emerged — narrower than NT Arabic's six, but the same general shape (true passive
dominant, a real derived-stem-active minority clustering around a specific semantic
class, plus two further minority strategies):

- **True morphological passive (Form I/II/IV passive, yufʿal(u)/fuʿila pattern) is
  overwhelmingly dominant — ~10 of 13 clean instances (≈77%), even more dominant than
  NT Arabic's own (already-revised) finding that true passive is merely the single most
  common of six strategies.** This is the default expectation for a niphal/pual/hophal
  verb describing a genuine passive event (an external, often unstated, agent acts on
  the subject).
  Example: יֻסַּךְ (hophal, "is poured") → `يُسْكَبُ`: primary 1:1.
  Example: נִסְלַח (niphal, "is forgiven") → `يُصْفَحُ`: primary 1:1.
  Example: נִתְּנָה (niphal, "was given") → AVD `أُعْطِيَتِ` / ONAV `وُهِبَتِ` (both
  true passive, different lexemes): primary 1:1.
  Example: יִוָּסֶר (niphal, "is disciplined") → AVD `لَا يُؤَدَّبُ` (true passive):
  primary 1:1. (ONAV instead converted to an active imperative, `لَا تُؤَدِّبِ` "do not
  discipline" — see active-voice conversion below.)

- **Derived-stem active-form verb (Form V/VII/VIII: tafaʿʿala/infaʿala/iftaʿala) — real
  but narrow, clustering around reciprocal, collective, or self-affecting actions where
  the subject's own action produces the result, not an external agent's.** Matches NT
  Arabic's finding almost exactly (there: physical/experiential change-of-state verbs
  like baptize, recline; here: divide/split, gather/assemble, adopt-a-name).
  Example: יֵחָלֵק (niphal, "was divided") → `ٱنْقَسَمَ` (Form VII infaʿala, "split
  itself"): primary 1:1 — not true passive morphology, but the natural Arabic verb for
  a group dividing itself into parts.
  Example: נֶאֱסָפִים (niphal participle, "gathered together") → `مُجْتَمِعَةٍ` (Form
  VIII iftaʿala participle, "assembled/congregated"): primary 1:1 — reciprocal/
  collective sense, both AVD and ONAV agree.
  Example: וַיִּקָּרֵא עַל שְׁמָם (niphal, "and was called by their name" = "took on
  their name/identity") → `وَتَسَمَّى بِٱسْمِهِمْ` (Form V tafaʿʿala, "named himself
  by"): primary 1:1 — contrast the same verb קָרָא/niphal used with true passive
  `دُعِيَ` elsewhere (see below) when the reading is a genuine external-agent passive
  event ("your name IS CALLED [by someone] over your city") rather than a
  self-affecting identity-adoption sense ("he TOOK ON their name through marriage") —
  the same root and stem can take either strategy depending on which sense is meant,
  not a fixed lexeme-to-strategy mapping.

- **Adjectival/stative (plain Arabic adjective or ordinary active participle) — for
  niphal forms that mark an inherent STATE rather than a passive EVENT.** A second
  genuine minority strategy, distinct from the derived-stem-active case above (no
  action or event is implied at all, just a description).
  Example: נִרְחָב (niphal, "wide/broad," describing pastureland) → `وَاسِعٍ` (a plain
  adjective, no verbal/passive marking whatsoever): primary 1:1.
  Example: נִרְדָּם (niphal, "sound asleep") → `نَائِمًا` (a plain active participle,
  "sleeping" — not "was put to sleep"): primary 1:1.

- **Active-voice conversion (agent promoted to subject)** — attested but rare in this
  sample (1 instance, ONAV only), matching NT Arabic's finding that this strategy is
  the exception rather than the rule and skews toward the more dynamic/paraphrastic
  translation (ONAV) rather than the more literal one (AVD).
  Example: יִוָּסֶר → ONAV `لَا تُؤَدِّبِ` ("do not discipline," 2nd-person imperative
  addressed to the reader, vs. AVD's passive `لَا يُؤَدَّبُ`): a genuine
  translator-variable voice conversion, not evidence the underlying Hebrew passive
  should default to an Arabic active rendering.

**Not observed in this sample, unlike NT Arabic:** nominalization (verbal-noun phrase
replacing the passive verb entirely) and a dedicated explicit-agent-preposition
conversion (the OT sample did not happen to include a case with an explicit Hebrew
agent phrase, e.g. בְּיַד "by the hand of," attached to a passive verb) — both remain
open questions for a future sample rather than confirmed absent.

---

## GRANULARITY **[arb]**

Prefer one record per source token — split rather than group. Create separate records
whenever source tokens (or word-parts) can each independently map to distinct target
tokens. Combine into N:M records only when tokens form an inseparable semantic unit
(idiom) or target words cannot be individually assigned to separate source tokens. When
in doubt, split.

Because AVD's target tokenization is whitespace-only and Arabic fuses several morphemes
into one written word (see the fused-proclitic material in the key-differences list
above), N:1 records — several Hebrew word-part tokens mapping to one Arabic token — are
the norm, not an occasional case, exactly as in NT Arabic. There is no way to mark part
of an Arabic token secondary and leave the rest untouched at the character level; the
record's granularity is still the whole token.

Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a
failure.

---

## ARTICLES **[arb]**

Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.

**Treated as PRIMARY, not secondary — an open question carried over from NT Arabic.**
Unlike every other OT config (Portuguese, Spanish, French, Indonesian, Hindi), this
document aligns the article word-part primary to the noun's record rather than
secondary, because Arabic's al- is a real, productive definite-article morpheme with a
genuine definite/indefinite semantic contrast — closer typologically to Greek's/Hebrew's
own article than to a merely grammatically-supplied filler. Because al- is always fused
(never its own separate word, unlike English "the" or Indonesian's occasional "itu"),
there is no Branch A/Branch B split the way other OT configs have — no separate word is
structurally possible; the article's primary-vs-secondary status is a records-modeling
decision, not a Branch A/B choice.
Example: הָאָרֶץ → ٱلْأَرْضُ "the earth": source=[articlePart, אָרֶץ],
target=["ٱلْأَرْضُ"] — both primary (contrast every other OT config, which would mark
articlePart secondary here).

**Do not confuse the fused article with an explicit Hebrew demonstrative pronoun.** OT
Hebrew commonly follows an articular noun with a separate demonstrative-pronoun word
(הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) to form "that/this X" (e.g. הָאִישׁ הַהוּא, lit. "the man,
the that-one" = "that man") — a real, distinct Hebrew token. Arabic's demonstrative
pronouns (هَذَا/هَذِهِ/ذَلِكَ/تِلْكَ) are separate, non-fused words and align primary
1:1 to that demonstrative-pronoun token, never to the article itself (which keeps its
own primary link to the noun as usual). Not independently re-verified at scale for
Arabic in this pass — carried over from the Indonesian OT document's finding that this
distinction matters more in OT than NT. **Measured directly for Arabic (full corpus,
24,090 article word-parts):** only 3.06% (737/24,090) of Hebrew articular nouns are
immediately followed (within 3 tokens) by a demonstrative pronoun — a real, non-trivial
minority case, but confirming it is not something that comes up often in practice.

### Anarthrous noun

No Hebrew article token exists, and Arabic has no indefinite article (bare noun,
optionally with tanwin nunation in the source script, not represented in AVD's
whitespace tokenization) — bare noun, no secondary needed.
Example: אִישׁ → إِنْسَانًا "a man": primary alone.

---

## CONSTRUCT CHAINS **[arb]**

A construct chain expresses genitive by word order and construct form — no preposition
token. Arabic's own ʾiḍāfa construction works identically: bare noun-noun juxtaposition,
head noun (muḍāf) first, absolute/modifier noun (muḍāf ilayh) second — the exact same
order Hebrew's construct chain already uses. No linking word is needed, confirmed
repeatedly and consistently across the sample:

Example: רוּחַ אֱלֹהִים → رُوحُ ٱللهِ "Spirit of God": source=[רוּחַ], target=["رُوحُ"]
— primary 1:1 (no secondary needed); source=[אֱלֹהִים], target=["ٱللهِ"] — primary 1:1.

Example: פְּנֵי תְהוֹם → وَجْهِ ٱلْغَمْرِ "surface of the deep": source=[פְּנֵי],
target=["وَجْهِ"] — primary 1:1; source=[תְהוֹם, articlePart], target=["ٱلْغَمْرِ"] —
both primary (article per ARTICLES above).

Example: מֹשֶׁה עֶבֶד יְהוָה → مُوسَى عَبْدِ ٱلرَّبِّ "Moses, servant of the LORD":
source=[מֹשֶׁה], target=["مُوسَى"] — primary 1:1; source=[עֶבֶד], target=["عَبْدِ"] —
primary 1:1 (no secondary needed); source=[יְהוָה, articlePart], target=["ٱلرَّبِّ"] —
both primary.

**Distinguish a true construct chain from Hebrew's לְ-possession construction** — these
look similar in translation but are different Hebrew structures with different
alignment outcomes. A bound/construct-state noun (no preposition token at all) is a true
construct chain, above. An absolute noun followed by a separate לְ preposition token
expressing possession/attribution (common in psalm superscriptions, e.g. מִזְמוֹר
לְדָוִד "a psalm of/belonging to David") is NOT a construct chain — לְ is a real,
separate Hebrew token and gets its own primary record per INSEPARABLE PREPOSITIONS,
fused onto the Arabic noun as لِ-.
Example: מִזְמוֹר לְדָוִד → مَزْمُورٌ لِدَاوُدَ: source=[מִזְמוֹר], target=["مَزْمُورٌ"]
— primary 1:1; source=[לְPrepPart], target=["لِدَاوُدَ"] — primary (the לְ, fused as
لِ-, not a construct-chain artifact); source=[דָוִד], target=["لِدَاوُدَ"] — primary
(shares the fused token with the preposition).

**Occupational/predicative participle-in-construct — REVISED after a 28-verse
full-corpus sample of construct-state participles immediately following a form of
הָיָה/וַיְהִי (all such instances in WLCM; not a stratified sample, an exhaustive one).
Bare ʾiḍāfa remains the clear majority even here, contrary to the original
single-verse-based "minority exception" framing.** Of the sampled instances with a
genuine noun-complement (excluding false positives and cases where the Arabic
preposition matches the participle's own lexical valence, e.g. יֹצֵא-מִן "issue
from" → خَارِجٌ مِنْ, which is not idafa-breaking any more than an English verb's own
required preposition would be), clear BARE construct outnumbered supplied-preposition
instances roughly 4-to-2: נֹשֵׂא כֵלִים "armor-bearer" → حَامِلَ سِلَاحٍ (bare),
נֹשְׂאֵי אֲרוֹן "ark-bearers" → حَامِلُو تَابُوتِ (bare), רֹבֶה קַשָּׁת "archer"
→ رَامِيَ قَوْسٍ (bare), פֹּרְשֵׂי כְנָפַיִם "wing-spreaders" → بَاسِطَيْنِ
أَجْنِحَتَهُمَا (bare, with the possessive suffix substituting for the second
construct noun). **The real conditioning factor found in this sample is not
"occupational participle" but a specific lexicalized idiom: אֲבִי + participle-phrase
("father of X-ers," i.e. "the first/ancestor of a group") consistently supplies لِ**
— הוּא הָיָה אֲבִי יֹשֵׁב אֹהֶל "he was the father of tent-dwellers" →
كَانَ أَبًا لِسَاكِنِي ٱلْخِيَامِ, אֲבִי כָּל תֹּפֵשׂ כִּנּוֹר "father of all who
play the lyre" → أَبًا لِكُلِّ ضَارِبٍ — both supply لِ after أَب specifically,
while the INNER construct chain inside the same phrase (سَاكِنِي ٱلْخِيَامِ
"dwellers-of the-tents") stays bare. This looks like a fixed Arabic idiom
("أَبًا لِـ" = "a father to/of") triggered by the predicate-אֲבִי construction
itself, not a general occupational-participle rule. Genesis 4:2's רֹעֵה
צֹאן/עֹבֵד אֲדָמָה → رَاعِيًا لِلْغَنَمِ/عَامِلًا فِي ٱلْأَرْضِ (AVD) remains a
genuine, still-unexplained outlier within this pattern — treat as an isolated
exception pending further sampling, not as evidence of a broader rule, and do not
expect a supplied preposition for ordinary occupational/title construct-participles
(armor-bearer-type) by default.
Example (bare, the actual majority pattern): וַיְהִי לוֹ נֹשֵׂא כֵלִים → وَكَانَ لَهُ
حَامِلَ سِلَاحٍ "and he had an armor-bearer": source=[נֹשֵׂא-construct],
target=["حَامِلَ"] — primary 1:1 (no secondary needed); source=[כֵלִים],
target=["سِلَاحٍ"] — primary 1:1.
Example (lexicalized אֲבִי-לְ exception): אֲבִי יֹשֵׁב אֹהֶל → أَبًا لِسَاكِنِي
ٱلْخِيَامِ: source=[אֲבִי-construct], target=["أَبًا"] — primary 1:1; source=[יֹשֵׁב-
construct], target=["لِسَاكِنِي"] — primary; the fused لِ- has no separate Hebrew
correspondent (supplied, secondary to the participle's record, per this lexicalized
pattern); source=[אֹהֶל], target=["ٱلْخِيَامِ"] — primary 1:1 (inner construct chain,
still bare).

Construct definiteness: Hebrew article word-part on the absolute noun keeps its own
primary link to that noun per ARTICLES above — Arabic's own iḍāfa already signals the
relationship, so no extra secondary marking is needed even when the article marks the
whole chain as definite.

---

## INSEPARABLE PREPOSITIONS **[arb]**

Preposition word-part → Arabic preposition, fused as a proclitic (بِ-/لِ-/كَ-) or a
separate word (مِنْ/عَلَى/تَحْتَ/etc. do not fuse): primary 1:1. A merged article in
the same fused token keeps its own primary link per ARTICLES — the fusion doesn't
change which tokens are primary, only that they share one written Arabic word.

Example: בְּיִשְׂרָאֵל → فِي إِسْرَائِيلَ "in Israel" (preposition rendered as a
separate word, not fused, because فِي — unlike بِ/لِ/كَ — is never a bound proclitic in
Arabic): source=[בְPrepPart], target=["فِي"] — primary 1:1; source=[יִשְׂרָאֵל],
target=["إِسْرَائِيلَ"] — primary 1:1.

Example: לְדָוִד → لِدَاوُدَ "for/of David" (bound proclitic لِ-, one fused Arabic
word): source=[לְPrepPart], target=["لِدَاوُدَ"] — primary; source=[דָוִד],
target=["لِدَاوُدَ"] — primary (shares the token).

---

## CONJUNCTIONS AND PARTICLES **[arb]**

Align content words first; conjunctions and particles are residual.

- Waw word-part (pos=conjunction) → fused وَ-/فَ-: primary. Confirmed as the dominant
  strategy across nearly every verse sampled — OT Arabic narrative prose fuses the waw
  far more consistently than Indonesian drops it. Asyndeton (rare) → NEQ source.
- כִּי — polyfunctional; align to whichever Arabic word/particle carries its force in
  context (لِأَنَّ/إِنَّ/أَنَّ/etc., paralleling NT Arabic's HOTI findings).
  Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר — Arabic's relative pronoun family (ٱلَّذِي/ٱلَّتِي/ٱلَّذِينَ/etc., agreeing
  in gender/number/case with its antecedent, unlike Indonesian's invariant "yang"):
  primary. When אֲשֶׁר instead functions as a complementizer introducing an oath or
  command complement clause rather than a true relative clause, it aligns to Arabic's
  complementizer أَنْ instead — a different word for a different function of the same
  Hebrew particle, not a discrepancy.
  Example: אֲשֶׁר אֲנֹכִי יוֹשֵׁב בְּקִרְבּוֹ (relative, "in whose midst I dwell") →
  ٱلَّذِينَ أَنَا سَاكِنٌ بَيْنَهُمْ: source=[אֲשֶׁר], target=["ٱلَّذِينَ"] —
  primary 1:1.
  Example: אֲשֶׁר לֹא תִקַּח (oath complementizer, "that you shall not take") →
  أَنْ لَا تَأْخُذَ: source=[אֲשֶׁר], target=["أَنْ"] — primary 1:1.

---

## IDIOMS **[arb]**

meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All
tokens implicitly primary; meta.secondary does not apply.

Last resort — always prefer standard records, even with loose primary matches. Use idiom
only when no plausible token-level decomposition exists. Function-word-only source units
are never idioms — they have individual correspondences or NEQ determinations.

---

## PRONOMINAL SUFFIXES **[arb]** — REVISED after a full-corpus-derived breakdown by host type (~47,000 total suffix instances)

Pronominal suffixes are separate word-part tokens (pos=suffix). **The deciding factor
for primary-vs-secondary is the suffix's grammatical ROLE (subject vs. object/
possessor), not which kind of word it happens to attach to** — a cleaner and more
general rule than the original framing, which described the split narrowly as
"infinitive construct vs. everything else." Verified by checking suffixes hosted by
nouns (~25,227 corpus instances), prepositions (~11,488), finite verbs (~6,508, of
which participles are ~877), and infinitive constructs (~1,486) — a distinction not
present in any other currently-supported OT config, since Arabic (unlike Indonesian)
has genuine person/number verb agreement that can independently carry subject
information.

- **Object suffix or possessive suffix — PRIMARY, fused, regardless of host type.**
  Whether the Hebrew host is a noun (possessive), a preposition (its object), a finite
  verb (its direct object), a participle used nominally (possessive) or verbally
  (object), or even an infinitive construct (its object) — the suffix is always
  primary, fused onto whatever Arabic word ends up carrying it. The Arabic word itself
  can vary (a noun, a finite verb, or a masdar/verbal noun after restructuring), but the
  suffix's own PRIMARY status does not.
  Example (noun, possessive): עֲצָמַי → عِظَامِي "my bones": source=[עֶצֶם-noun,
  sufPart], target=["عِظَامِي"] — both primary.
  Example (participle used nominally, possessive): שֹׁפְטָיו "his judges" → `قُضَاتَهُمْ`
  (ONAV, "their judges" — suffix fused onto a plural noun exactly like an ordinary
  noun+suffix case): both primary.
  Example (participle used verbally, object — restructured as a finite verb, suffix
  still fuses onto the resulting verb): כָּל מֹצְאִי "whoever finds me" → `كُلُّ مَنْ
  وَجَدَنِي`: source=[participleId, sufPart], target=["وَجَدَنِي"] — both primary
  (fused object clitic -نِي on the finite verb وَجَدَ).
  Example (infinitive construct, OBJECT suffix — NOT the subject-marking case below):
  לְהַכְעִיסוֹ "to provoke him to anger" → `لِإِغَاظَتِهِ` (li-ighāẓatihi, "for
  provoking-him" — masdar/verbal-noun + fused genitive-object suffix): both primary.
  Example (infinitive construct as a bare direct object, OBJECT/genitive-style suffix):
  צֵאתְךָ וּבוֹאֶךָ "your going out and your coming in" → `خُرُوجَكَ وَدُخُولَكَ`
  (masdar forms with fused possessive-style suffix, since Arabic treats the whole
  phrase like a possessed noun phrase): both primary.
  Example (preposition): אֵלָיו → إِلَيْهِ "to him": source=[elPart, sufPart],
  target=["إِلَيْهِ"] — both primary.

- **Suffix marking the SUBJECT of an infinitive construct — SECONDARY, absorbed.** This
  is the one genuine exception, and only when the suffix marks the infinitive's
  SUBJECT (not its object) — confirmed across a broader sample beyond the original two
  verses (Genesis 1:2's `בְּהִבָּרְאָם` "when they were created," Deuteronomy 28:20's
  `עַד אֲבָדְךָ` "until your perishing," 2 Samuel 2:10's `בְּמָלְכוֹ` "when he became
  king," Isaiah 40:13's `תִּתּוֹ קוֹלוֹ` "his giving his voice"). When the infinitive
  construct is restructured as an Arabic finite clause (the default strategy for
  temporal/purpose uses — see INFINITIVAL CONSTRUCTIONS), Arabic's own verb agreement
  morphology already encodes the subject's person/number/gender, so the suffix has no
  separate Arabic word to attach to.
  Example: בְּשִׁבְתְּךָ בְּבֵיתֶךָ → حِينَ تَجْلِسُ فِي بَيْتِكَ "when you sit in
  your house": source=[בְPrepPart], target=["حِينَ"] — primary; source=[שֶׁבֶת-infC,
  sufPart], target=["تَجْلِسُ"] — primary: שֶׁבֶת; secondary: sufPart (2ms agreement
  already in تَجْلِسُ); source=[בְPrepPart2], target=["فِي"] — primary;
  source=[בַּיִת-noun-construct, sufPart2], target=["بَيْتِكَ"] — both primary (this
  second suffix, on the noun בַּיִת "house," is the ordinary possessive case above, not
  the infinitive-subject case — contrast the two suffixes in the same verse).
  Example: בְּמָלְכוֹ עַל יִשְׂרָאֵל "when he became king over Israel" → `حِينَ مَلَكَ
  عَلَى إِسْرَائِيلَ`: source=[מָלַךְ-infC, sufPart], target=["مَلَكَ"] — primary:
  מָלַךְ; secondary: sufPart (3ms agreement already in مَلَكَ).

**Practical check when a suffix attaches to an infinitive construct specifically:**
determine whether the suffix is the logical SUBJECT of the infinitive's action ("his
becoming king," "your perishing" — intransitive/unaccusative sense) or its OBJECT ("his
provoking," "your going out [somewhere]" as a nominalized event with the suffix as
possessor/agent-of-the-noun rather than embedded-clause-subject). In practice: if
Arabic restructures the infinitive into a full finite clause (temporal `حِينَ`/`لَمَّا`
constructions), the suffix is almost always absorbed as secondary; if Arabic keeps a
masdar/verbal-noun rendering (nominalization strategy — see INFINITIVAL CONSTRUCTIONS),
the suffix fuses onto that noun as primary, same as any other noun+suffix.

---

## NEGATION **[arb]**

Hebrew's two morphologically distinct negators (לֹא indicative, אַל
jussive/prohibitive) both converge on Arabic لَا — a mood distinction Hebrew
grammaticalizes but Arabic doesn't for ordinary negation, the same convergence NT
Arabic found for Greek's separate imperative/subjunctive prohibition moods.

- **לֹא (indicative, any tense/aspect) → لَا + verb:** primary 1:1. Verb gets its own
  record. Confirmed for both perfective narrative negation and gnomic/habitual
  imperfect negation in the sample — לֹא does not require distinguishing Hebrew's own
  tense/aspect the way NT Arabic's لم/لا split (aorist/perfect vs. present) does for
  Greek, since Hebrew's negation particle itself is invariant across those categories.
  Example: וְלֹא יַעֲשֶׂה → وَلَا يَفْعَلُ "and does not do": source=[loId],
  target=["لَا"] — primary 1:1; source=[verbId], target=["يَفْعَلُ"] — primary 1:1.

- **אַל (jussive/prohibitive) → لَا + jussive/imperative verb:** primary 1:1 — the
  same particle as indicative לֹא above; only the Arabic verb's own mood morphology
  (jussive تَنْظُرْ vs. indicative يَنْظُرُ) distinguishes the prohibition, not the
  negator choice.
  Example: אַל תַּבִּיט אַחֲרֶיךָ → لَا تَنْظُرْ إِلَى وَرَائِكَ "do not look behind
  you": source=[alId], target=["لَا"] — primary 1:1; source=[verbId],
  target=["تَنْظُرْ"] — primary 1:1.

- **Nominal/copular negation → لَيْسَ:** a conjugated negator-verb (agreeing with its
  subject), for negating a noun/predicate-noun clause rather than a verbal clause —
  matches NT Arabic's laysa-for-copular-negation finding exactly.
  Example: לֹא אִישׁ אֵל וִיכַזֵּב → لَيْسَ ٱللهُ إِنْسَانًا فَيَكْذِبَ "God is not a
  man, that he should lie": source=[loId], target=["لَيْسَ"] — primary 1:1.

- **אֵין/אַיִן (existential negation) — REVISED after a 24-verse full-corpus-stratified
  sample (out of 659 total אֵין/אַיִן verses in WLCM): the original single-instance
  claim ("→ لَمْ يَكُنْ") does not hold as the default.** Three coexisting strategies,
  none of them a single fixed phrase the way Indonesian's "tidak ada" is:
  - **لا النافية للجنس (bare لَا + accusative predicate noun, no copula at all)** is the
    single most common strategy in the sample (≈8 of 22 usable instances, concentrated
    in poetic/wisdom register — Psalms, Proverbs, Ecclesiastes) — a genuine categorical-
    negation construction, not merely "لَا" borrowed from ordinary verbal negation.
    Example: וְאֵין קֵץ → لَا نِهَايَةَ لَهَا "there is no end": source=[einId],
    target=["لَا"] — primary 1:1 (categorical negation, predicate noun accusative, no
    copula); source=[qetsId], target=["نِهَايَةَ"] — primary 1:1.
  - **لَيْسَ (conjugated existential/copular negator)** is nearly as common (≈6 of 22),
    especially in the fixed pattern لَيْسَ + مَنْ ("there is no one who...") for אֵין +
    an implied agent/relative sense.
    Example: וְאֵין מוֹשִׁיעֵךְ → وَلَيْسَ مَنْ يُخَلِّصُكِ "and there is no one to save
    you": source=[einId], target=["وَلَيْسَ", "مَنْ"] — both primary.
  - **لَمْ يَكُنْ (negated finite "to be")** is real but narrower than the original
    single-instance draft suggested (≈3 of 22) — it clusters in narrative prose with a
    definite, concrete-noun subject ("there was no king," "there was no sword," "no
    stone was seen"), not in poetic/relative-clause contexts.
    Example: אֵין מֶלֶךְ בְּיִשְׂרָאֵל → لَمْ يَكُنْ مَلِكٌ فِي إِسْرَائِيلَ "there was
    no king in Israel": source=[einId], target=["لَمْ", "يَكُنْ"] — both primary.
  - A minority of sampled instances used no negation particle at all — e.g. אֵינֶנּוּ
    ("he is no more," of Joseph presumed dead) → `مَفْقُودٌ` ("missing," a single
    predicate adjective) — worth flagging but too rare (1 instance) to generalize.
  **Caution for detection:** אַיִן is also the ordinary interrogative "where?"
  (`מֵאַיִן` "from where") — a homograph, not existential negation; check the gloss
  field, not just the surface form, before classifying an אַיִן token.

### Compound negation: לֹא...עוֹד ("no longer") is DISCONTINUOUS — confirmed at scale

**Checked against a 20-verse stratified sample of the 222 full-corpus verses
containing both לֹא and עוֹד** (matching Indonesian OT's own count for this exact
construction) — confirmed decisively, not merely plausible: AVD consistently splits the
negator from the "again/anymore" adverb, almost always fusing the negator directly onto
the verb (`لَمْ يَعُدْ` / `فَلَمْ`/`لَا` + verb) while `بَعْدُ`/`أَيْضًا` trails at the
very end of the clause, frequently separated by the verb's own object or additional
material. This parallels NT Arabic's οὐκέτι/μηκέτι finding and Indonesian OT's own
לֹא...עוֹד finding exactly — treat "the negator and its adverb land together" as the
exception, not the rule, for this specific construction.
Example: וְלֹא יָסְפָה שׁוּב אֵלָיו עוֹד → فَلَمْ تَعُدْ تَرْجِعُ إِلَيْهِ أَيْضًا "she
did not return to him again": source=[loId], target=["فَلَمْ", "تَعُدْ"] — primary
1:1 to the fused negation+verb; source=[odId], target=["أَيْضًا"] — primary 1:1,
non-adjacent (separated by "تَرْجِعُ إِلَيْهِ").
Example: וְלֹא הָיָה בָם עוֹד רוּחַ → وَلَمْ تَبْقَ فِيهِمْ رُوحٌ بَعْدُ "and there was
no longer any courage in them": source=[loId], target=["وَلَمْ"] — primary 1:1;
source=[odId], target=["بَعْدُ"] — primary 1:1, clause-final, separated by the entire
predicate ("تَبْقَ فِيهِمْ رُوحٌ").

---

## PARTICIPIAL CONSTRUCTIONS **[arb]** — REVISED after a stratified sample (~25 verses across two searches)

**Substantive/attributive participles split three ways by referent type, closely
paralleling NT Arabic's ism al-fāʿil / الَّذِي / مَنْ split, and directly answering
the casuistic-law open question flagged after Pass 1.**

- **Genuine Arabic participle (ism al-fāʿil, often a derived-stem or lexicalized
  agent-noun) — the majority strategy, for attributive modification of an
  already-identified/specific referent, occupational titles, and epithets.**
  Example: הַ+מֹּשֵׁל בְּכָל אֲשֶׁר לוֹ → ٱلْمُسْتَوْلِي عَلَى كُلِّ مَا كَانَ لَهُ "the
  one in charge of all that he had": source=[articlePart, participleId],
  target=["ٱلْمُسْتَوْلِي"] — both primary.
  Example (lexicalized occupational title): הָרֹאֶה "the seer" → `ٱلرَّائِي`; הַצֹּפֶה
  "the watchman" → `ٱلرَّقِيبُ`; הָרָצִים "the runners/guards" → `ٱلسُّعَاةُ` — all
  genuine Arabic active-participle-derived nouns, not relative clauses.
  Example (specific historical group, not a legal class): כָּל הַנֹּפְלִים "all who
  fell" (a particular battle's casualties) → `جَمِيعُ ٱلسَّاقِطِينَ`: source=[כָּל,
  articlePart, participleId], target=["جَمِيعُ", "ٱلسَّاقِطِينَ"] — primary.

- **`ٱلَّذِي`/`ٱلَّتِي`/`ٱلَّذِينَ` (relative clause + finite verb)** — used instead
  of a bare participle mainly when the participle governs a direct object the Arabic
  participle form doesn't easily carry, or (like the ism al-fāʿil case above) for a
  specific already-identified group rather than a hypothetical legal class.
  Example: הַנֹּגֵעַ בָּעֶצֶם "the one who touches the bone" (participle + direct
  object) → `ٱلَّذِي مَسَّ ٱلْعَظْمَ`: source=[articlePart, participleId],
  target=["ٱلَّذِي", "مَسَّ"] — primary: مَسَّ; secondary: ٱلَّذِي.
  Example (specific group): כָּל הַנִּשְׁאָרִים "all who remained" (a particular
  historical remnant) → `كُلَّ ٱلَّذِينَ بَقُوا`: primary to the relative + verb.

- **`كُلُّ مَنْ`/`كُلُّ مَا` + finite verb — the DOMINANT strategy specifically for
  Hebrew's casuistic/conditional legal formula `כָּל הַ` + participle ("whoever/
  whatever does X, [then] Y"), confirmed against a targeted 96-instance full-corpus
  search of this exact construction (all `כָּל` + article + participle sequences) —
  answering the open question Indonesian OT flagged as unproductive via its own
  `כָּל`+participle proxy search.** `مَنْ` for a personal/animate referent (the
  large majority — ritual-purity law in Leviticus/Numbers, plus poetic/wisdom
  generalizations); `مَا` for an impersonal/inanimate referent (rarer, e.g. "whatever
  touches the altar," "whatever remains" of food). **The deciding factor is NOT the
  presence of `כָּל` alone — `כָּל הַ`+participle also renders as a genuine participle
  or relative clause (above) when it describes an already-identified specific group
  rather than a hypothetical open legal class** — check whether the clause is stating
  a general rule/law (→ `مَنْ`/`مَا`) or describing a particular historical group (→
  participle/relative clause).
  Example (casuistic law, personal referent): כָּל הַנֹּגֵעַ בְּנִבְלָתָם יִטְמָא
  "whoever touches their carcass shall be unclean" → `كُلُّ مَنْ مَسَّ جُثَثَهَا
  يَكُونُ نَجِسًا`: source=[כָּל, articlePart, participleId], target=["كُلُّ",
  "مَنْ"] — both primary; source=[verbId], target=["مَسَّ"] — primary.
  Example (casuistic law, impersonal referent): כָּל הַנֹּגֵעַ בַּמִּזְבֵּחַ יִקְדָּשׁ
  "whatever touches the altar shall be holy" → `كُلُّ مَا مَسَّ ٱلْمَذْبَحَ يَكُونُ
  مُقَدَّسًا`: target=["كُلُّ", "مَا"] — both primary.
  Example (poetic/wisdom generalization, not narrow legal code, same مَنْ pattern):
  כָּל הַנִּשְׁבָּע בּוֹ "everyone who swears by him" → `كُلُّ مَنْ يَحْلِفُ بِهِ`:
  target=["كُلُّ", "مَنْ"] — both primary.

- **Occupational/predicative, in a construct chain after הָיָה/וַיְהִי:** see CONSTRUCT
  CHAINS above — bare ʾiḍāfa is the actual majority here too; only the lexicalized
  `אֲבִי` + participle idiom reliably supplies a preposition.

- **Predicative (participle as the main clause predicate) — REVISED after a 9-verse
  targeted sample; the original single-instance framing (bare participle predicate as
  the default) does NOT hold.** Conversion to a FINITE VERB (imperfect for ongoing
  present-tense readings, perfect for a completed-action sense) is actually the
  MAJORITY strategy (5 of 7 clean instances) — a bare Arabic participle predicate,
  matching Hebrew's own nominal-clause structure, is real but a MINORITY strategy that
  clusters specifically around POSTURAL/STATIVE verbs (standing, sitting, lying) rather
  than ongoing dynamic actions (hovering, ruling, commanding, coming) — Arabic's active
  participle most naturally expresses a resultant STATE, which favors a finite verb for
  genuinely dynamic predicates. A third, rarer strategy uses a lexicalized noun/title as
  the predicate instead of any verb form at all.
  Example (finite-verb conversion, the majority pattern): וְרוּחַ אֱלֹהִים מְרַחֶפֶת "and
  the Spirit of God was hovering" → `وَرُوحُ ٱللهِ يَرِفُّ`: source=[participleId],
  target=["يَرِفُّ"] — primary (finite imperfect verb, not a participle at all).
  Example (finite-verb conversion, present→perfect tense shift): אָנֹכִי מְצַוְּךָ "I am
  commanding you" → `أَنِّي أَوْصَيْتُكَ` "that I commanded you" (finite perfect):
  primary.
  Example (bare participle predicate, postural/stative verb — the minority pattern):
  וְהַכֹּהֵן נִצָּב "and the priest was standing" → `وَٱلْكَاهِنُ وَاقِفٌ`: source=[הַ,
  participleId], target=["وَٱلْكَاهِنُ", "وَاقِفٌ"] — the subject noun primary to its
  own token; source=[participleId], target=["وَاقِفٌ"] — primary (bare participle,
  nominal-clause predicate, matching Hebrew's own structure exactly — contrast the
  finite-verb examples above).
  Example (lexicalized noun/title predicate, rare): אֱלֹהִים שֹׁפֵט הוּא "God, he is
  judge" → `ٱللهَ هُوَ ٱلدَّيَّانُ` "God, He is THE JUDGE": source=[participleId],
  target=["ٱلدَّيَّانُ"] — primary (a lexicalized agent-noun/title used as a nominal
  predicate, not a participle form or a finite verb).

- **Formulaic quotative לֵאמֹר ("saying," introducing direct speech):** a fixed,
  extremely stable rendering قَائِلًا, identical to NT Arabic's finding for Greek
  λέγων — a striking cross-testament confirmation of a stable Bible-translation
  convention rather than a coincidence.
  Example: וַיֹּאמֶר יְהוָה אֶל יְהוֹשֻׁעַ ... לֵאמֹר → ... كَلَّمَ يَشُوعَ ... قَائِلًا
  "... spoke to Joshua ... saying": source=[leEmorId], target=["قَائِلًا"] —
  primary 1:1.

---

## INFINITIVAL CONSTRUCTIONS **[arb]** — REVISED/EXTENDED after full-corpus-derived samples

### Purpose/temporal constructions (בְּ/כְ + infinitive construct) → finite clause

Classical Arabic has no true infinitive form usable this way (the same structural gap NT
Arabic documents in detail, with five separate strategies depending on syntactic
function). For the temporal/purpose use specifically, Hebrew's `בְּ`/`כְ` + infinitive
construct ("when/as X happened") renders as an ordinary finite clause introduced by
`حِينَ`/`لَمَّا` ("when"), never as a nonfinite Arabic form — the identical mechanism NT
Arabic uses for `ἐν τῷ` + infinitive, and Indonesian OT uses for the same Hebrew
construction. Confirmed 5x across two separate samples (Deuteronomy 6:7's four
instances — שִׁבְתְּךָ, לֶכְתְּךָ, שָׁכְבְּךָ, קוּמֶךָ — and Genesis 19:17's `כְ` +
infinitive `הוֹצִיאָם` → `لَمَّا أَخْرَجَاهُمْ`).

The infinitive's own subject suffix, if present, is absorbed into the finite verb's
agreement morphology rather than surfacing as a separate word — see PRONOMINAL SUFFIXES
above for the full mechanics and worked example.

### Purposive/complement `לְ` + infinitive construct — NEW, checked against a 14-verse
### sample of the 4,573 corpus instances (the single largest infinitive category)

Three coexisting strategies, none a single default — closely matching NT Arabic's
multi-strategy infinitive breakdown:

- **Purposive `لِ`/`لِكَيْ` + subjunctive verb — the majority strategy for genuine
  purpose clauses** ("in order to X").
  Example: לְהַבְדִּיל בֵּין הַיּוֹם וּבֵין הַלָּיְלָה "to separate between day and night"
  → `لِتَفْصِلَ بَيْنَ ٱلنَّهَارِ وَٱللَّيْلِ`: source=[lePrepPart], target=["لِتَفْصِلَ"]
  — primary (لِ fused onto the subjunctive verb).
  Example: לְרַמּוֹתַנִי "to betray me" → `لِكَيْ تَدْفَعُونِي` (the compound purpose
  marker لِكَيْ, still the purposive-`لِ` family): primary.

- **`أَنْ` + subjunctive complement clause — for infinitive complements of volition/
  refusal/permission verbs** (want, be willing, allow, agree), matching NT Arabic's
  `أَنْ`+subjunctive strategy exactly.
  Example: מֵעֲשֹׂתִי זֹאת "from my doing this" (oath/refusal idiom, "far be it from me
  to do this") → `أَنْ أَفْعَلَ ذَلِكَ`: primary.
  Example: לֹא אָבָה לִשְׁתּוֹתָם "was not willing to drink it" → `لَمْ يَشَأْ أَنْ
  يَشْرَبَهُ`: primary.
  Example: לְבִלְתִּי קְחַת כֶּסֶף "so as not to take money" (בִּלְתִּי + infinitive,
  a negated purpose/result construction) → `عَلَى أَنْ لَا يَأْخُذُوا فِضَّةً`: primary
  (أَنْ + negated subjunctive).

- **Nominalization (masdar + preposition) — real, though less common than either
  strategy above**, typically for fixed idiomatic phrases rather than live purpose
  clauses.
  Example: לָצֵאת וְלָבוֹא "for going out and coming in" (military-campaign idiom) →
  `لِلْخُرُوجِ وَلِلدُّخُولِ` (literally "for-the-going-out and for-the-coming-in," a
  verbal noun with `لِ`, not a subjunctive verb): primary.
  Example: לֹא נָתַן ... עֲבֹר "did not allow ... to pass" (bare infinitive complement,
  no preposition on the Hebrew side) → `لَمْ يَسْمَحْ ... بِٱلْمُرُورِ` (restructured
  with `بِ` + masdar `ٱلْمُرُورِ` "the-passing"): primary.

**Caution:** the same בִּלְתִּי+infinitive construction was found rendered THREE
different ways across the sample (`أَنْ لَا`+subjunctive above; also a bare relative
clause `ٱلَّذِي لَا يَنْفَعُ` for לְבִלְתִּי הוֹעִיל "so as not to profit" in a
different verse) — treat the specific strategy as genuinely translator-variable rather
than fully predictable from the Hebrew construction alone.

### Infinitive absolute (cognate emphasis) — REVISED after a 20-verse stratified sample
### of the 730 corpus instances; the original single-verse framing does not hold

**The original claim (AVD reliably uses a cognate-accusative masdar; ONAV reliably uses
a plain adverbial intensifier) does not survive a larger sample.** Cognate accusative
and complete non-marking are roughly equally common — genuine instance-by-instance
variation, not a stable AVD-vs-ONAV register split, and the variation shows up WITHIN
AVD itself, not just between the two translations:

- **Cognate accusative (masdar as accusative object of the matching finite verb)** — a
  real, available, and reasonably common strategy (~4 of 8 clean paired instances in
  this sample), and a genuine structural parallel unique to this pair of Semitic
  languages among all currently-supported configs.
  Example: אָכֹל תֹּאכֵל "you shall surely eat" → `تَأْكُلُ أَكْلًا`: source=[infAbsId],
  target=["أَكْلًا"] — primary 1:1 (cognate accusative, structural match, not merely an
  adverb); source=[verbId], target=["تَأْكُلُ"] — primary 1:1.
  Example: מוֹת יוּמָת "he shall surely die" → `يُقْتَلُ قَتْلًا`: primary 1:1 to the
  cognate accusative — but the SAME construction (`מוֹת יוּמָת`, near-identical Hebrew)
  renders in a DIFFERENT verse's ONAV translation as plain `يُقْتَلْ` with no cognate
  accusative at all — confirming this is genuine per-instance variation, not a fixed
  lexeme-to-strategy mapping.
- **Completely unmarked (plain finite verb, no cognate accusative, no adverb, no
  emphasis marking of any kind)** — equally common (~4 of 8), including in AVD itself,
  not only ONAV.
  Example: עָלֹה נַעֲלֶה "we will surely go up" → AVD `نَصْعَدُ` (plain imperfect, no
  emphasis marker whatsoever): primary 1:1 alone — no secondary or NEQ needed for the
  infinitive absolute; its emphatic force is simply not reproduced.
  Example: הָיֹה הָיָה דְבַר יְהוָה "the word of the LORD came" (idiomatic narrative
  opening formula) → AVD `صَارَ كَلَامُ ٱلرَّبِّ` (single plain verb): primary 1:1
  alone.
- **Rare periphrastic/lexical variants**: a light-verb + definite noun-object
  periphrasis (`تَلْتَزِمُونَ ٱلصَّمْتَ` "you commit to THE silence," for `הַחֲרֵשׁ
  תַּחֲרִישׁוּן` "keep completely silent" — a noun-object construction distinct from
  true cognate accusative, since the noun is definite rather than an indefinite
  accusative); occasional full lexical substitution/paraphrase with no trace of the
  emphasis construction at all.

**When there is no matching finite verb to pair with** — Hebrew occasionally strings
several bare infinitive absolutes together as a series of imperatival commands (not the
cognate-emphasis pairing above), e.g. `עָרֹךְ הַשֻּׁלְחָן צָפֹה הַצָּפִית אָכוֹל שָׁתֹה`
"prepare the table, spread the rug, eat, drink" (Isaiah 21:5) — these render as
ordinary finite imperative/imperfect verbs (`يُرَتِّبُونَ`, `يَحْرُسُونَ`, `يَأْكُلُونَ`,
`يَشْرَبُونَ`), with no cognate accusative possible since there is no finite verb of
the same root to attach one to.

Absorbed without any separate Arabic marking → infinitive absolute secondary to the
finite verb's record when a cognate accusative or other marking IS present; when
completely unmarked (the equally-common alternative above), leave it unrecorded rather
than forcing a secondary link — there is no Arabic word bearing its emphatic force to
attach it to.

## Cross-translation methodology note

Every structural claim above was checked against **both** AVD and ONAV for the same
verse before being written down, following the exact methodology of
`alignment-principles-nt.arb.md`. Where the two translations agreed on structure despite
differing lexical choices (construct chains, temporal-infinitive-as-finite-clause,
formulaic לֵאמֹר → قَائِلًا, negation particle choice), that is treated as confirmation
of a general Arabic-grammar pattern rather than an AVD-specific quirk. Where AVD and
ONAV diverged on the same verse (the infinitive-absolute cognate-accusative-vs-adverb
split at Genesis 2:17; the occupational-participle construct-chain restructuring choice
at Genesis 4:2, لِ vs. فِي; the article inclusion in وَٱلْأَرْضَ vs. وَالأَرْضَ, a
spelling/orthographic difference not a structural one), that divergence is documented as
genuine free variation, not resolved into a single rule.

**Pass 1** was a single spot-check of ~15 verses (Genesis 1:1-2, 2:17, 2:23, 4:2, 19:17,
24:2-3; Numbers 23:19; Deuteronomy 6:4-5,7; Joshua 1:1; Judges 21:25; Psalm 23:1), chosen
to hit each of the four OT conditional blocks (PRONOMINAL_SUFFIX, NEGATION, PARTICIPLE,
INFINITIVE) at least twice, plus the BASE_BLOCK-level construct-chain and article
material.

**Pass 2** re-verified three sections at full-corpus or full-corpus-derived-sample
scale, mirroring the approach the Indonesian OT document used for ARTICLES/CONSTRUCT
CHAINS/NEGATION:
- **NEGATION (existential אֵין/אַיִן):** a 24-verse stratified sample drawn evenly
  across all 659 corpus-wide אֵין/אַיִן verses, checked against both AVD and ONAV.
  This overturned the Pass-1 single-instance claim (see NEGATION above) — לَمْ يَكُنْ
  turned out to be a minority strategy (~3/22 usable instances) behind both لا
  النافية للجنس (~8/22, concentrated in poetic/wisdom books) and لَيْسَ (~6/22).
- **NEGATION (לֹא...עוֹד discontinuity):** a 20-verse stratified sample of the full
  222-verse corpus-wide set (identical verse-selection method to the Indonesian OT
  document's own count for this construction), checked against AVD. Confirmed
  decisively, not merely plausible — every sampled instance showed the negator fused
  to the verb and the "again"-adverb trailing at clause end, non-adjacent.
- **CONSTRUCT CHAINS (occupational-participle exception):** an exhaustive (not
  stratified) pass over all 28 corpus-wide instances of a construct-state participle
  immediately following a form of הָיָה/וַיְהִי, checked against AVD. This substantially
  narrowed the Pass-1 "minority exception" framing — bare ʾiḍāfa turned out to be the
  actual majority even for occupational participles (armor-bearer, ark-bearers,
  archer, wing-spreaders all stayed bare); the real conditioning factor found is a
  specific lexicalized אֲבִי + participle idiom, with Genesis 4:2's shepherd/tiller
  pair remaining an unexplained outlier rather than representative of a general rule.
- **ARTICLES (demonstrative-pronoun co-occurrence):** a full-corpus mechanical count
  (24,090 article word-parts) replacing the Pass-1 "not independently verified"
  placeholder with a precise 3.06% co-occurrence rate.
- **PASSIVE VOICE:** entirely new in Pass 2 — a 30-verse stratified sample across all
  three passive-associated Hebrew stems (niphal/pual/hophal, ~5,024 corpus instances),
  checked against both AVD and ONAV. This was previously flagged as "highest priority
  for a Pass 3" in the Pass-1 open questions; addressed here instead. Found four
  coexisting strategies (true passive dominant at ~77%, a narrow derived-stem
  active-form minority, a genuine adjectival/stative minority, and rare active-voice
  conversion) — see PASSIVE VOICE above.
- **PARTICIPLE (substantive/attributive split, casuistic "whoever" formula):** a
  ~25-verse stratified sample of articular substantive participles (drawn from 1,461
  full-corpus instances), plus a targeted, exhaustive 96-instance full-corpus search
  specifically for `כָּל` + article + participle (the casuistic-law candidate
  construction), both checked against AVD. Resolved the open question Indonesian OT
  flagged as unproductive via a similar proxy search — `כָּל הַ`+participle reliably
  splits into `كُلُّ مَنْ`/`كُلُّ مَا` (legal/generalizing "whoever/whatever") vs. a
  genuine participle or relative clause (specific historical group), not one fixed
  rendering — see PARTICIPIAL CONSTRUCTIONS above.
- **INFINITIVE (purposive/complement `לְ`+infinitive, infinitive absolute):** a
  14-verse sample of the 4,573 corpus instances of `לְ`+infinitive construct (checked
  against both translations), plus a 20-verse stratified sample of the 730 corpus
  infinitive-absolute instances. The purposive/complement sample confirmed a
  three-strategy split (purposive `لِ` majority, `أَنْ`+subjunctive complement,
  nominalization) closely matching NT Arabic's own multi-strategy infinitive
  breakdown. The infinitive-absolute sample OVERTURNED the Pass-1 single-verse
  finding — cognate accusative and complete non-marking turned out roughly equally
  common, including within AVD itself, not a stable AVD-vs-ONAV register split as
  Genesis 2:17 alone suggested — see INFINITIVAL CONSTRUCTIONS above.
- **PRONOMINAL SUFFIXES (host-type breakdown at scale):** sampled across suffixes
  hosted by nouns, prepositions, finite verbs, participles, and infinitive constructs
  (~47,000 corpus instances total, sampled by host-type category rather than a flat
  verse sample). REFINED the Pass-1 finding into a cleaner, more general rule: the
  deciding factor is subject-vs-object/possessor ROLE, not host type as such —
  object/possessive suffixes are always primary regardless of host (including
  infinitive-construct OBJECT suffixes, which the original framing did not
  distinguish from the genuinely-secondary subject-marking case) — see PRONOMINAL
  SUFFIXES above.
- **PARTICIPLE (verbal/predicative use):** a 9-verse targeted sample of subject +
  anarthrous-participle nominal clauses (drawn from ~2,895 corpus candidates), checked
  against AVD. REVERSED the incidental single-instance assumption that a bare Arabic
  participle predicate is the default — finite-verb conversion is actually the
  majority, with bare-participle predication a minority pattern specifically for
  postural/stative verbs — see PARTICIPIAL CONSTRUCTIONS above.
- **DUAL NUMBER:** a 7-verse stratified sample of the 1,933 corpus dual-noun instances,
  checked against AVD. Confirmed the carried-over NT Arabic expectation as the majority
  pattern, but found genuine lexeme-specific exceptions (nostrils→singular, doors/
  eyelids→plural) — see SURFACE FORM DIFFERENCES above.

**Every item from the Pass-1 open-questions list has now been addressed in Pass 2**:
NEGATION, CONSTRUCT CHAINS, ARTICLES, PASSIVE VOICE, PARTICIPLE (both the substantive
split/casuistic-formula question and verbal/predicative use), INFINITIVE (both
purposive/complement `לְ`+infinitive and infinitive absolute), PRONOMINAL SUFFIXES
(host-type breakdown), and dual number. This document is still well short of NT
Arabic's later per-construction stratified passes (20-30 verses each, vs. this
document's mostly 7-30-verse or targeted-search samples) for any given section, and
further short of native-speaker/Arabist review — treat Pass-2-revised findings as more
solid than Pass-1 spot-checks, but still not final. A Pass 3 would need to go deeper on
individual sections (larger samples per construction) rather than breadth across new
sections, plus the still-unaddressed items in the open-questions list below (mostly
finer-grained sub-questions raised BY the Pass-2 findings themselves, not gaps in
coverage).

---

## Open questions for native-speaker/Arabist review

1. **Is the fused definite article primary or secondary?** Carried over unchanged from
   NT Arabic's open question #1 — this document currently treats it as primary. Confirm
   whether this distinction is worth making for OT as well, or whether consistency with
   every other OT config favors treating it as secondary regardless. (Not addressed by
   Pass 2 — the 3.06% demonstrative-cooccurrence measurement addresses a different
   question, when to align "itu"-equivalents, not this one.)
2. **CONSTRUCT CHAINS**: Pass 2 (28-verse exhaustive sample) found bare ʾiḍāfa is the
   real majority even for occupational participles, and narrowed the exception to a
   specific אֲבִי + participle idiom. Still open: does the אֲבִי-לְ idiom hold at a
   larger scale beyond the 2 instances found? Is Genesis 4:2's shepherd/tiller pair a
   genuine one-off, or would a targeted search for other occupational predicate-nominal
   participles (not immediately after הָיָה, or with a different verb of becoming) turn
   up a real pattern? Does the same אֲבִי idiom apply when the complement is a plain
   noun rather than a participle?
3. **NEGATION**: Pass 2 established that existential אֵין/אַיִן has (at least) three
   coexisting strategies (لا النافية للجنس most common overall, لَيْسَ close behind —
   especially with مَنْ, لَمْ يَكُنْ narrower and prose/concrete-noun-conditioned) and
   confirmed the לֹא...עוֹד discontinuity decisively. Still open: is the
   register/context conditioning for the three existential strategies (poetic/wisdom vs.
   narrative-prose vs. relative-clause "no one who") a real predictive rule, or a loose
   tendency? Is there any real conditioning factor between לَيْسَ and لا النافية للجنس
   for ordinary (non-existential) nominal negation specifically — the NT document
   flagged the identical question and left it unresolved, and Pass 2 did not target
   ordinary nominal negation separately from existential אֵין.
4. **PARTICIPLE**: addressed in Pass 2 — the ism al-fāʿil/الَّذِي/كُلُّ مَن split was
   confirmed (25-verse stratified sample plus a 96-instance exhaustive search for the
   casuistic `כָּל`+participle construction specifically), unlike Indonesian OT's own
   attempt at the same question, which the ind.py document reported as unproductive.
   Still open: what precisely distinguishes the ism al-fāʿil-vs-الَّذِي choice when
   BOTH readings describe a specific historical group (rather than the casuistic-legal
   vs. specific-group split already established) — register, whether the participle
   takes a direct object, translator preference? What conditions verbal/predicative
   participle rendering — addressed later in Pass 2 (9-verse sample): finite-verb
   conversion turned out to be the majority, reversing the incidental single-instance
   assumption; bare-participle predication is real but minority, clustering around
   postural/stative verbs. Still open: is the postural/stative-vs-dynamic-action split
   a clean binary, or are there dynamic-action verbs that also take a bare-participle
   predicate (not observed in this 9-verse sample, but not ruled out)? Is the
   periphrastic הָיָה+participle pattern (eng.py's own PARTICIPLE_BLOCK documents this
   for English) real for Arabic too, and does it differ from the bare-predicative case
   — not distinguished from plain subject+participle clauses in this sample, since most
   sampled instances had no explicit הָיָה? Does the lexicalized-noun-predicate strategy
   (`ٱلدَّيَّانُ` for שֹׁפֵט) generalize to other participles used as divine/royal
   titles, or was it specific to that one root?
5. **INFINITIVE**: addressed in Pass 2. The Genesis-2:17-only "AVD=cognate-accusative,
   ONAV=adverb" split did NOT hold at scale (20-verse sample) — both strategies are
   roughly equally common, and vary within AVD itself. Still open: is there ANY
   predictable conditioning factor for cognate-accusative vs. complete non-marking
   (verb lexeme, register, narrative vs. legal-formula context), or is it genuinely
   free variation with no rule to state? Does the light-verb+definite-noun periphrasis
   (`تَلْتَزِمُونَ ٱلصَّمْتَ`) recur elsewhere, or was it a one-off for that specific
   root? For purposive/complement `לְ`+infinitive: does the purposive-`لِ` vs.
   `أَنْ`+subjunctive choice correlate with anything predictable (matrix-verb class,
   as NT Arabic found for the analogous Greek construction), or is it more free than
   that? Does the `בִּלְתִּי`-rendered-three-ways finding hold up as three genuinely
   free variants, or would a larger sample reveal conditioning?
6. **PRONOMINAL SUFFIXES**: addressed in Pass 2 — resolved the participle-object-vs-
   subject ambiguity (a participle+suffix never marks the participle's subject; it is
   always object-marking or possessive, and always primary either way) and refined the
   infinitive rule to a general subject-vs-object distinction rather than a blanket
   "infinitive construct" rule. Still open: precisely how common is each of the two
   infinitive-suffix cases (subject-marking/secondary vs. object-marking/primary)
   relative to each other — not counted, only confirmed both occur? When an infinitive
   construct's OBJECT suffix is present AND the infinitive is restructured as a finite
   clause (rather than staying a masdar noun phrase) — does the object suffix then fuse
   onto the finite verb as an ordinary object clitic, or could it ever get dropped
   the way subject suffixes do? No clean example of that specific combination was
   found in this pass.
7. **PASSIVE VOICE**: addressed in Pass 2 (30-verse stratified sample across niphal/
   pual/hophal) — found four strategies (true passive dominant ~77%, derived-stem
   active-form minority, adjectival/stative minority, rare active-voice conversion).
   Still open: does true passive's dominance hold at NT Arabic's larger 20-30-verse-
   per-stem scale, or would a bigger sample surface NT Arabic's remaining two
   strategies (nominalization, explicit-agent-preposition conversion) that this sample
   happened not to include? Is the same-root/different-strategy split found for קָרָא
   (true passive `دُعِيَ` for "name called over a place" vs. derived-stem `تَسَمَّى`
   for "adopt a name") a general semantic-conditioning pattern for other verbs, or
   specific to that root? Does an explicit Hebrew agent phrase (e.g. בְּיַד "by the hand
   of") on a passive verb convert to a real Arabic preposition the way NT Arabic found
   for ὑπό/διά, or does OT Hebrew's own agent-marking behave differently (no clean
   instance was found in the sample to check)?
8. **Dual number**: addressed in Pass 2 (7-verse stratified sample). The
   straightforward dual-to-dual match is confirmed as the majority pattern, but with
   genuine lexeme-specific exceptions (singular for "nostrils," plural for "doors"/
   "eyelids"). Still open: is there a predictable semantic class distinguishing
   dual-preserving vs. dual-collapsing body-part nouns (e.g. paired sensory organs used
   in perception idioms vs. paired organs used in physical-action idioms), or is it
   purely lexeme-by-lexeme with no generalizable rule? Only checked against AVD in this
   pass — ONAV's parallel renderings for the same verses were not systematically
   compared, unlike most other Pass-2 findings.
9. **When does Arabic supply an explicit preposition (مِنْ/لِ) instead of ʾiḍāfa for a
   Hebrew construct-adjacent relationship, beyond the אֲבִי-idiom and participle-
   valence cases documented in Pass 2?** Needs broader sampling of non-participial
   construct chains, paralleling NT Arabic's open question #7 for the Greek genitive.
10. **Waw-consecutive narrative chains**: this document asserts (in the key-differences
    list) that OT Arabic fuses the waw far more consistently than Indonesian drops it,
    based on the density of وَ-/فَ- fusion observed across both samples — not a
    systematically counted claim, just an impression from the verses checked. Worth a
    targeted frequency check (parallel to the Indonesian OT document's waw/asyndeton
    counting) before treating as established.
