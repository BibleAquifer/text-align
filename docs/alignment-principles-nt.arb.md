# Alignment Principles — Arabic (arb), New Testament

Guidelines used by `refine-alignment` when aligning the Arabic Van Dyck Bible (AVD)
against the Greek New Testament (SBLGNT) source.

Sections marked **[arb]** contain Arabic-specific rules or examples. Unmarked sections
are shared with the English guidelines (`alignment-principles-nt.md` and
`prompt/nt/eng.py`).

Examples are grounded in `data/targets/AVD/nt_AVD.tsv` checked against the Greek source
TSV (`data/sources/SBLGNT.tsv`), and cross-checked against a second, independently-
translated Arabic NT — ONAV (Open New Arabic Version, a more dynamic/idiomatic
translation than the literal 1860s Van Dyck) — via `data/targets/ONAV/nt_ONAV.tsv`, to
separate general Arabic grammar from AVD's own stylistic/register choices. The base
fused-clitic/iḍāfa/article material comes from an initial 4-verse pass (Matt 1:1–2,
Mark 1:9, John 4:2); PASSIVE, NEGATION, PARTICIPLE, COMPARATIVE, and CONDITIONAL were
each additionally checked against a separate stratified ~20–30 verse sample spanning
the whole NT (see each section for its own verse list). See the Cross-translation
methodology note near the end.

Source files: `src/text_align/refine/prompt/nt/arb.py`,
`src/text_align/refine/prompt/nt/eng.py`

**Review status:** reviewed by a native Arabic speaker and confirmed "very good." Note
that even the expanded sample this document is built from (PASSIVE/NEGATION/PARTICIPLE:
~25 verses each; COMPARATIVE/CONDITIONAL: ~20 verses each) is still well short of
Hindi's hundreds-to-low-thousands-per-construction validation, but the native-speaker
review is the stronger form of confirmation the other pre-review drafts were waiting on.

**Key differences from every currently-supported language:**

- **AVD's target tokenization is whitespace-only, and Arabic orthography attaches
  function morphemes to the following/preceding word with no space at all.** This is
  the single biggest structural difference from every other supported language,
  including Hindi (whose fused clitics are limited to pronominal suffixes). One Arabic
  *token* — one whitespace-delimited unit — routinely corresponds to what Greek
  tokenizes as 2–4 separate words: conjunction + article + noun + pronominal suffix can
  all be one token (e.g. `وَإِخْوَتَهُ` = wa- "and" + ʾikhwat "brothers" + -hu "his",
  Matt 1:2). There is no way to mark part of a token secondary and leave the rest
  untouched at the *character* level — the record's granularity is still the whole
  token — so the practical effect is that N:1 records (multiple Greek source tokens →
  one fused Arabic target token) are the *dominant* pattern for Arabic, not an
  occasional case the way article-absorption is for English. See FUSED PROCLITICS AND
  SUFFIXES below.
- **Construct-state (ʾiḍāfa) genitive chains** — a sequence of nouns in construct
  relation (e.g. `كِتَابُ مِيلَادِ يَسُوعَ` "book-of birth-of Jesus", Matt 1:1) marks
  the genitive relationship through case/definiteness morphology alone — no preposition
  token, no clitic, nothing written between the nouns at all. Unlike English's
  case-driven "of" (a real secondary *token* that must be included in the record),
  Arabic's ʾiḍāfa relator has no token to include, secondary or otherwise. Parallels
  Hebrew construct chains (flagged as a pending Hebrew-OT topic in the main
  `alignment-principles-nt.md` §10) — both are Semitic construct-state genitives. See
  ʾIḌĀFA CONSTRUCT-STATE GENITIVES below.
- **Definite article ال (al-)** is a real, semantically meaningful definite article —
  the closest typological match to Greek's article of any currently-supported
  language — but it is *always* a bound prefix, never its own token. Case 1 of §6.1 in
  the main doc (a separate "the" token) can never apply to Arabic; only Case 2 (article
  secondary, absorbed into the noun's record) is reachable, and it applies far more
  often than it does for English, because absorption is forced by orthography rather
  than optional.
- **No indefinite article**, same as Greek — simpler than English's Case 4.
- **Pro-drop with rich verb agreement**: Arabic finite verbs mark subject
  person/number/gender through circumfixal agreement morphology (prefix + suffix,
  e.g. yaf ʿal- "he does" vs. taf ʿal- "she/you do"), so a dropped subject pronoun is
  fully recoverable from the verb form itself — closer to Spanish/Portuguese pro-drop
  (grammar-guaranteed) than to Hindi's discourse-driven pro-drop. No new rule needed
  beyond the existing "subject pronoun from verb ending" pattern (main doc §3.2); this
  should just be expected far more often than in English.
- **Passive voice has (at least) six coexisting strategies — REVISED after a 26-verse
  sample; the original single-verse claim that Arabic "avoids" true morphological
  passive does not hold.** True passive (finite fuʿila/yufʿalu forms and true passive
  participles, e.g. `مَكْتُوبٌ` maktūbun "written," `مَا قِيلَ` mā qīla "that which was
  said") turned out to be the single most common strategy overall (~14 of ~34 sampled
  tokens), not a marginal alternative. A dedicated intransitive/unaccusative verb with
  no voice marking at all (e.g. `تَمَّ`/`يَتِمَّ` tamma/yatimma for "be fulfilled") is
  also very common and highly consistent across both translations. The derived-stem
  active verb (Form V/VII/VIII) pattern the original draft was built on — Mark 1:9's
  ἐβαπτίσθη → `ٱعْتَمَدَ`/`تَعَمَّدَ` — is real but narrower than first thought: it
  clusters around verbs of the subject's OWN physical/experiential change of state
  (baptize, recline, be taken up, be filled), not passive voice generally. Active-voice
  conversion (agent promoted to subject) is real too, but confirmed almost exclusively
  in ONAV — AVD never converted to active in this sample when a true-passive
  alternative was available, suggesting a real register difference worth expecting
  between the two translations. See PASSIVE VOICE below for the full breakdown.
- **Passive agent (ὑπό/διά + case) is not preserved as a passive-agent construction —
  it converts to a real preposition or fixed idiom.** Confirmed across the expanded
  sample: `مِنْ` (min, "from" — AVD's most common choice), `عَلَى يَدِ` (ʿalā yad, "at
  the hand of"), `بِ-` (bi-, itself a FUSED proclitic), `لَدَى` (ladā, "among/with"),
  `بِلِسَانِ` (bi-lisāni, "by the tongue of"). Align the Greek preposition primary to
  whichever the specific translation used; never expect a literal "by."
- **Negation particle choice is tense/aspect-conditioned, not free variation — REVISED
  after a 24-verse sample.** لم (lam + jussive) turned out broader than "simple past":
  it covers any negated event Greek presents as a completed/perfective whole — aorist
  AND perfect alike — and `لَمْ يَكُنْ` ("was not") covers both a negated continuous-
  past VERB (John 4:2's `لَمْ يَكُنْ يُعَمِّدُ`) and a negated predicate NOUN/ADJECTIVE
  (John 1:3's `لَمْ يَكُنْ شَيْءٌ`, "nothing was") — one construction, two complement
  types. لا covers present/gnomic negation AND all prohibitions uniformly, regardless
  of whether the Greek prohibition is a present imperative or aorist subjunctive — a
  mood distinction Arabic doesn't grammaticalize. Nominal/existential negation splits
  between لا النافية للجنس (categorical "there is no X," no copula token at all) and
  ليس (laysa, a real verb-like negator) — genuinely translator-variable, no confirmed
  conditioning factor. **Emphatic negation (οὐ μή) has no single dedicated
  construction** — لا and لن are BOTH attested for the identical Greek pattern,
  sometimes differing between AVD and ONAV on the same verse; an optional intensifier
  (أَبَداً/قَطُّ) is stylistic (common in ONAV, rare in AVD), not grammatically
  required. See NEGATION below for the full breakdown.
- **Dual number.** Koine Greek has no living dual (it survives in Attic but not NT
  Greek), while Arabic has a fully productive dual for nouns, verbs, and pronouns.
  Arabic dual forms simply align to Greek plural — a surface-form difference, not a
  problem (main doc §2.1) — worth stating explicitly so a future reviewer doesn't
  mistake an Arabic dual/Greek plural pairing for an error.
- **Titles receive the article by convention even when the Greek is anarthrous.**
  Confirmed live: Greek χριστοῦ (Matt 1:1, no article — Χριστός functions almost as a
  second proper name here) → AVD `ٱلْمَسِيحِ` / ONAV `الْمَسِيحِ`, both with the
  article fused on. This is systematic for "Messiah/Christ" specifically (parallel to
  Hebrew ha-Mashiach) — treat as a lexicalized, expected article-without-Greek-article
  case (like main doc §6.1 Case 3, but conventionalized rather than translator-
  improvised) rather than a discrepancy to flag.
- **The article is not used with bare transliterated proper names.** Confirmed live:
  Greek τὸν Ἰσαάκ / τὸν Ἰακώβ (Matt 1:2, article retained before a proper name — one
  of the exceptions in main doc §6.1 Case 2 that normally makes the Greek article
  primary) → AVD/ONAV `إِسْحَاقَ` / `يَعْقُوبَ`, no ال at all. Since Arabic never
  attaches the article to a bare transliterated name, there is no possible Arabic
  correspondent for τόν here — the default outcome is **NEQ**, not primary, breaking
  from the pattern followed by English/Portuguese/Spanish/French for this construction.
- **Substantive participles split three ways by referent type — NEW, after a 25-verse
  sample, closer to Indonesian's yang/barangsiapa split than Hindi's single-default
  जो.** A genuine Arabic participle (ism al-fāʿil/ism al-mafʿūl) for attributive
  modification of an already-identified noun or elevated/hymnic register; `الَّذِي`
  (al-ladhī) + finite verb for a specific/deictic referent; `مَنْ` (man) + finite verb
  as the DOMINANT strategy for generic "whoever…" formulaic refrains (the best-attested
  pattern in the sample — confirmed 6× across 3 lexemes, holding even where a natural
  Arabic participle exists and goes unused, e.g. Revelation's `ὁ νικῶν` → `مَنْ
  يَغْلِبُ` at both 2:7 and 3:21). Circumstantial participles default to a FINITE
  SUBORDINATE CLAUSE (`لَمَّا`/`حِينَ` + verb), not Arabic's own ḥāl-participle
  construction, except in elevated/hymnic passages — with a second common strategy of
  collapsing participle+main-verb into two coordinate finite verbs (`وَ`/`ثُمَّ`).
  `λέγων` ("saying") has an extremely stable formulaic rendering (`قَائِلًا`) largely
  independent of either strategy. See PARTICIPIAL CONSTRUCTIONS below.
- **The أَفْعَل (afʿal) elative disambiguates comparative/superlative cleanly, but
  Greek's suppletive "first"/"last" bypass it entirely — NEW, after a 20-verse
  sample.** Arabic's single elative form (comparative and superlative are
  morphologically identical) resolves via three co-occurring markers: bare + `مِنْ`
  (min) = comparative, `ال-` + elative = superlative, bare alone = implicit/absolute
  comparison. But πρῶτος/ἔσχατος map to dedicated ordinal lexemes (`أَوَّل`/`آخِر`),
  not the elative — a Greek COMPARATIVE tag doesn't reliably predict which Arabic
  strategy applies; the specific lemma must be checked. See COMPARATIVES AND
  SUPERLATIVES below.
- **Arabic has (at least) four conditional particles, not a simple two-way split — NEW,
  after a 19-verse sample.** `لَوْ` (law) is dedicated to genuine contrary-to-fact
  conditions (2nd class, confirmed 3/3); `إِنْ` (in) is the default for BOTH Greek
  1st- and 3rd-class conditions alike (Arabic collapses that distinction — the real
  split is open vs. counterfactual); `إِذَا` (idhā) appears for ἐάν when the condition
  is framed as likely/expected. **`εἰ μή` ("except/only") is not a conditional at
  all** — a fixed exceptive idiom rendering uniformly as `إِلَّا` (confirmed 4/4), high-
  frequency enough that it dominated an early naive sampling pass. See CONDITIONAL
  CONSTRUCTIONS below.

- **Ordinary pronominal αὐτός has essentially no independent target token — NEW, after
  a 17-verse sample.** It is absorbed as a possessive/object suffix fused directly onto
  the noun or verb it belongs to — the majority case by far, and a direct application
  of the fused-pronominal-suffix rule above, now stated explicitly for αὐτός. One
  wrinkle: dative pronouns sometimes fuse onto a SEPARATE small preposition-carrier
  token (`لَهُ`/`إِلَيْهِ`) rather than the main verb, so the correspondent isn't
  always inside the verb's own token. Intensive "himself" is highly consistent (`نَفْس`
  "self" + possessive suffix, confirmed 5×); "same" turned out to need three distinct
  strategies depending on construction type, not one. See AUTOS below.
- **Causal and content-clause ὅτι get genuinely different Arabic renderings, and
  content-clause "that" itself splits further by matrix-verb type — NEW, after a
  24-verse sample.** Causal ὅτι → `لِأَنَّ` (li-anna, a fused preposition+
  complementizer); content-clause "that" → `أَنَّ` after cognition/belief/hope verbs
  but `إِنَّ` specifically after verbs of saying — a split not previously documented,
  confirmed in minimal pairs within single verses. **Recitative ὅτι is NOT uniformly
  NEQ/punctuation-only** as a single-pattern default would assume — Arabic sometimes
  inserts an `إِنَّ`-type opener (or an alternative like `حَقّاً` "truly") at the
  direct-quote boundary, and its presence tracks the Greek ὅτι (confirmed by a negative-
  control asyndetic quote with no ὅτι and no opener inserted) — so it should align
  primary to ὅτι when present, not default to NEQ. See HOTI below.
- **Arabic has NO true infinitive form at all — NEW, after a 22-verse INFINITIVE sample
  and a 24-verse ἵνα sample.** The Greek infinitive's role is split across (at least)
  five distinct Arabic strategies by syntactic function: a complementary infinitive
  gets `أَنْ` (an) + subjunctive (a real standalone token, both primary); a purpose
  infinitive fragments into a family of markers (`لِ-`/`لِكَيْ`/coordination-sharing/
  verb-serialization); a subject/predicate articular infinitive nominalizes into a
  plain abstract noun; a temporal articular infinitive becomes a finite clause. **The
  same split applies to ἵνα**: when ἵνα substitutes for an infinitive complement (θέλω
  ἵνα-type), it collapses to the identical bare `أَنْ`+subjunctive strategy — NOT a
  purpose marker — while genuine adverbial purpose ἵνα uses a free-variant family
  (`لِ-`/`لِكَيْ`/`كَيْ`, confirmed interchangeable within a single verse). See
  INFINITIVAL CONSTRUCTIONS and ἵνα CLAUSES below.
- **Arabic impersonal verbs never take a dummy subject pronoun — NEW, after a 22-verse
  sample.** No token slot for "it" exists at all (not even `هُوَ`), so the English
  "dummy it → NEQ" rule does not transfer — leave it unrecorded, not NEQ'd. See
  IMPERSONAL VERBS below.
- **Arabic marks iterative/conative/ingressive verbal-aspect nuances explicitly LESS
  often than Greek/English do — NEW, after a 20-verse sample.** A plain, unmarked
  perfective verb was the majority outcome (~60%) when checked against genuine
  aspectual instances. Most notably, the project's own canonical conative example
  (main doc §9.1.3, Mark 15:23) gets NO conative marking in either sampled Arabic
  translation at all. See VERBAL ASPECT below.

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Greek word(s) are behind this
translation word.

---

## ALIGNMENT PHILOSOPHY **[arb]**

Alignments are generous: include grammar-required fused proclitics (conjunction,
preposition, article) and pronominal suffixes when a Greek trigger exists. Do not
restrict to strict lexical equivalents.

Because fusion is orthographically forced rather than a translator choice, prefer
building one record per Arabic token that captures every Greek token it corresponds to,
rather than trying to force a 1:1 split that the target script does not support. When a
single Arabic token plausibly corresponds to multiple adjacent Greek tokens (conjunction
+ article + noun, or noun + pronominal suffix), a single N:1 record is normal and
expected — not a fallback.

Grammar-required fused elements (wa-/bi-/li-/ka- proclitics, al- article, pronominal
suffixes) are **primary** source-side companions to the noun/verb they attach to when a
distinct Greek token motivates them (a real conjunction, preposition, article, or
pronoun) — not secondary and not NEQ. Reserve NEQ for the rarer case where the Arabic
word supplies no fusable element at all corresponding to a given Greek token (e.g. the
Greek article before a bare proper name — see above), or where a Greek particle has no
plausible Arabic correspondent, fused or otherwise.

---

## TOKEN ROLES **[arb]**

- **primary** — direct lexical or semantic connection to the Greek token
- **secondary** — exists only because of grammatical features in the Greek token's
  morphology (person, number, case, aspect, voice), or because Arabic's own grammar
  obligatorily requires a word/morpheme with no separate Greek word behind it
- correspondence to a different Greek token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse (this
applies at the *token* level — a fused Arabic token that corresponds to several Greek
tokens is still one target ID, used once).

**Common secondary/primary cases:**

- **Fused conjunction (wa- "and", occasionally fa- "so/then")** — when a Greek καί or δέ
  motivates it, include the conjunction's Greek token as an additional **primary**
  source alongside the noun/verb the Arabic token belongs to (parallel to how a genuine
  conjunction token gets a primary link elsewhere — here it just cannot be its own
  record because it isn't its own Arabic token).
  Example (Matt 1:2): δέ + Ἰσαάκ → AVD/ONAV `وَإِسْحاقُ` (wa-Isḥāqu): source=[δέ token,
  Ἰσαάκ token], target=[وَإِسْحاقُ] — both source tokens primary, one target token.
- **Fused article (al-)** — when a Greek article motivates it, include the article's
  Greek token as an additional **primary** source in the noun's record (this is Case 2
  of the main doc's §6.1, but forced rather than exceptional — see DEFINITENESS below).
- **Fused preposition (bi-/li-/min/etc.)** — when a Greek preposition motivates it,
  include it as an additional **primary** source in the same record, same pattern.
- **Fused pronominal suffix (possessive on nouns, object on verbs)** — when a Greek
  pronoun/pronominal ending motivates it, include the pronoun's Greek token (or the
  verb's own person/number morphology) as **primary**/secondary per the usual test —
  the suffix itself carries real pronominal meaning, so treat it like any other pronoun
  correspondence, just packaged inside a larger fused token.
  Example (Matt 1:2): ἀδελφοὺς αὐτοῦ ("his brothers") → AVD/ONAV `وَإِخْوَتَهُ`
  (wa-ʾikhwatahu): source=[δέ/καί? — not present here, but ἀδελφούς, αὐτοῦ],
  target=[وَإِخْوَتَهُ] — ἀδελφούς and αὐτοῦ both primary (the suffix -hu is a genuine
  lexical pronoun, not a grammatical filler), one fused target token. (Matt 1:2's actual
  Greek has καὶ τοὺς ἀδελφοὺς αὐτοῦ — see the full worked example under FUSED PROCLITICS
  below.)
- **No indefinite article** — a bare noun is the default, same as Greek. No secondary
  token is ever needed for Arabic indefiniteness (contrast English's Case 4).

---

## NEQ (NON-EQUIVALENT) **[arb]**

NEQ is a positive claim that no correspondence exists — never a fallback for
uncertainty. Unrecorded means correspondence was not determined (normal). NEQ records
must not include `meta.secondary`.

- Certain no correspondent → NEQ (source or target empty, `meta.rel: "NEQ"`).
- Uncertain → leave unrecorded.

**Arabic-specific NEQ case:** the Greek article before a bare transliterated proper name
(τὸν Ἰσαάκ, τὸν Ἰακώβ, Matt 1:2) → **NEQ**, since Arabic never attaches ال to a bare
name and there is no other candidate token to absorb it into. This differs from
English/Portuguese/Spanish/French, where the article-before-proper-name case is one of
the primary-link exceptions in main doc §6.1 Case 2.

**Not NEQ:** fused conjunctions, articles, prepositions, and pronominal suffixes with a
real Greek trigger are primary/secondary companions in the noun/verb's record (see
above), not NEQ — even though they have no independent token of their own to point to.

---

## SURFACE FORM DIFFERENCES

Tense, voice, number, and aspect differences do not prevent alignment. Align on
lexical/semantic correspondence, not surface form. This explicitly includes Arabic dual
number aligning to Greek plural (no living NT-era Greek dual exists) and Arabic's
active-form derived-stem verbs (Form V/VII/VIII) aligning to Greek passive-voice verbs
(see PASSIVE VOICE).

---

## CANDIDATES

The alignment candidates provided are initial automated word-level suggestions with no
secondary classification, no idiom flags, and some errors. Restructure, split, merge, or
discard them freely. Arabic is VSO/SVO with a rich case/agreement system; word order
divergence from Greek is real but generally less severe than Hindi's SOV divergence.
Arabic is written right-to-left; token order in the TSV still follows document (reading)
order, so treat token sequence the same way as any other language when reasoning about
adjacency and discontiguous records.

---

## FUSED PROCLITICS AND SUFFIXES **[arb]**

This is the central structural fact about aligning Arabic: the target TSV tokenizes on
whitespace, and Arabic writes conjunctions (وَ wa- "and", فَ fa- "so/then"),
prepositions (بِ bi- "with/by", لِ li- "to/for", كَ ka- "like/as"), the definite article
(ٱلْ al-), and pronominal suffixes (possessive on nouns, object on verbs — ـهُ -hu
"his/him", ـهَا -hā "her", ـهُمْ -hum "their/them", ـنَا -nā "our/us", etc.) as bound
morphemes with **no space and no separate token**, in any combination and stacking
order (conjunction + article + noun + suffix can all be one token).

**Rule:** when a fused element has a real, identifiable Greek trigger (a conjunction,
preposition, article, or pronoun token in the source), include that Greek token as an
additional source token — primary — in the record for the Arabic token it is fused
into. Do **not** try to represent the fusion with `meta.secondary` on the target side
(there is nothing to mark secondary; the whole target token is one indivisible unit) —
the secondary/primary distinction, where it applies at all, lives on the *source* side
for these constructions, exactly as it already does for other N:1 records.

**Worked example** (Matt 1:2, full verse): Greek `Ἰσαὰκ δὲ ἐγέννησεν τὸν Ἰακώβ, Ἰακὼβ
δὲ ἐγέννησεν τὸν Ἰούδαν καὶ τοὺς ἀδελφοὺς αὐτοῦ` → AVD `وَإِسْحاقُ وَلَدَ يَعْقُوبَ.
وَيَعْقُوبُ وَلَدَ يَهُوذَا وَإِخْوَتَهُ.`

| Source | Target | Note |
|---|---|---|
| Ἰσαάκ, δέ | `وَإِسْحاقُ` | both primary — δέ fused as wa-; no separate target token for δέ |
| ἐγέννησεν | `وَلَدَ` | primary — AVD's literal "begat"; ONAV uses `أَنْجَبَ` (lexical variant, same slot) |
| τόν, Ἰακώβ | `يَعْقُوبَ` | Ἰακώβ primary; τόν → **NEQ** (no article possible on a bare name) |
| Ἰακώβ, δέ | `وَيَعْقُوبُ` | both primary — same wa-fusion pattern |
| ἐγέννησεν | `وَلَدَ` | primary; wa- here has no Greek trigger of its own (clause-initial default), so no extra source token is added for it — the wa- simply rides along with the verb as part of ordinary Arabic clause-linking style, same treatment as an untriggered conjunction elsewhere (Tier 2, main doc §9.7.1) |
| τόν, Ἰούδαν | `يَهُوذَا` | Ἰούδαν primary; τόν → NEQ |
| καί, τούς, ἀδελφούς, αὐτοῦ | `وَإِخْوَتَهُ` | καί, ἀδελφούς, αὐτοῦ primary (conjunction, noun, and the genuine pronominal-suffix meaning of -hu); τούς → NEQ (no article possible on a possessed-and-conjoined proper item, same reasoning as the bare-name cases; article is grammatically expected to drop before a possessive-suffixed noun in Arabic regardless of Greek) |

Note the last row's τούς NEQ: a possessed noun (noun + pronominal suffix) is inherently
definite in Arabic and **cannot** take ال at all — a different, purely grammar-internal
reason than the proper-name case above, but the same NEQ outcome for the Greek article.
This should be treated as a general rule (possessive-suffixed nouns never carry ال) once
confirmed against more examples, not re-derived case by case.

---

## ʾIḌĀFA CONSTRUCT-STATE GENITIVES **[arb]**

Arabic marks a genitive/possessive relationship between two nouns primarily through the
construct state (ʾiḍāfa): noun₁ (the possessed, "construct" form — no article even if
definite) immediately followed by noun₂ (the possessor, in the genitive case where
case is marked). No preposition, no clitic, and no separate token realizes the "of"
relationship — it is expressed purely by word order plus the first noun's
morphology (loss of nunation/article).

**Worked example** (Matt 1:1): Greek `Βίβλος γενέσεως Ἰησοῦ χριστοῦ` ("book of [the]
genealogy of Jesus Christ") → AVD `كِتَابُ مِيلَادِ يَسُوعَ ٱلْمَسِيحِ` — a three-link
construct chain (كِتَابُ ↔ مِيلَادِ ↔ يَسُوعَ ٱلْمَسِيحِ), exactly mirroring the Greek's
own three-link genitive chain, word for word, with no Arabic token at all corresponding
to "of."

| Source | Target | Note |
|---|---|---|
| Βίβλος | `كِتَابُ` | primary — no secondary "of" needed; ʾiḍāfa has no token to carry it |
| γενέσεως | `مِيلَادِ` | primary — same |
| Ἰησοῦ | `يَسُوعَ` | primary |
| χριστοῦ | `ٱلْمَسِيحِ` | primary; article fused per the lexicalized-title case above |

**Rule:** when Greek's case-driven genitive ("of X") is rendered as an ʾiḍāfa chain in
Arabic (very common, since ʾiḍāfa is Arabic's default possessive/genitive strategy),
each noun aligns 1:1 primary to its Greek counterpart, and — unlike the English pattern
in main doc §8.1/§8.4 where the supplied "of" is a real secondary target token — there
is **no secondary target token to add**, because Classical Arabic ʾiḍāfa supplies no
word for the relation at all. Do not search for a token to mark secondary here; there
isn't one.

**When Arabic instead uses an explicit preposition** (مِنْ min "from/of", لِ- li- "for/
belonging to") rather than ʾiḍāfa for a genitive relationship — this does happen,
particularly for looser or descriptive genitives, and needs broader corpus sampling to
characterize when — treat the preposition as an ordinary case-driven secondary/primary
token per the existing rules for explicit prepositions (main doc §9.6.1), since in that
case there *is* a real token to align.

---

## DEFINITENESS AND ARTICLES **[arb]**

Arabic's definite article ٱلْ/الْ (al-, assimilating in pronunciation but not spelling
before "sun letters") is a real definite article, closely paralleling Greek's — but it
is always a bound proclitic, never a separate token. This means only Case 2 of the main
doc's §6.1 (Greek article present, absorbed as secondary into the noun's record) is
reachable, and it is the default outcome, not an exception.

**DEFAULT — Greek article present, Arabic noun takes al-:** the article's Greek token is
included as an additional **primary** source token in the noun's record (see FUSED
PROCLITICS above) — treated as primary, not secondary, because unlike English's "the,"
Arabic's al- is not merely grammatically supplied by the translation; it is itself a
real definite-article morpheme with the same function as the Greek article, just fused
rather than free-standing. (This is a genuine difference from every Latin-script
language documented so far, all of which treat their article — free-standing "the," or
its absence — as secondary when the source has a matching article. Confirm this
"primary, not secondary" call during native-speaker review — it may be judged more
consistent with the rest of the system to keep the article secondary regardless of
Arabic's morphological richness, exactly parallel to Portuguese/French/Spanish's own
articles. Flagged as an open question below.)

**Bare transliterated proper names never take al-:** → Greek article, if present, is
**NEQ** (see NEQ section above and the worked τὸν Ἰσαάκ/τὸν Ἰακώβ example).

**Possessive-suffixed nouns never take al-:** a noun that already carries a pronominal
possessive suffix is inherently definite and cannot also carry the article — → Greek
article, if present, is **NEQ** (see the τοὺς ἀδελφοὺς αὐτοῦ example above).

**Lexicalized titles take al- even when Greek is anarthrous:** Χριστός → ٱلْمَسِيحِ /
الْمَسِيحِ, confirmed in both AVD and ONAV at Matt 1:1 despite no Greek article on
χριστοῦ here. Treat as an expected, conventionalized case — align the noun primary as
usual; no extra Greek token exists to add (there's no article present in the Greek to
draw in), so this is simply an ordinary 1:1 primary noun record, not a discrepancy.

**No indefinite article:** same as Greek, no secondary token ever needed.

**Attributive-adjective definiteness concord (confirmed 2×, Jude 1:20, Rev 2:4):** an
adjective/elative modifying a possessive-suffixed noun STILL takes its own al-, even
though the noun itself cannot (see above). This is ordinary Arabic definiteness
concord — the adjective agrees with the noun's definiteness independently — not a
contradiction of the possessive-noun NEQ-article rule. `إِيمَانِكُمُ ٱلْأَقْدَسِ`
("your most-holy faith") keeps `ٱلْأَقْدَسِ`'s article even though `إِيمَانِكُمُ`
(possessive-suffixed) has none.

---

## PASSIVE VOICE **[arb]**

Six strategies coexist; identify which one a given verse uses rather than assuming.
Confirmed against a 26-verse sample (~34 passive-tagged Greek tokens) spanning Matthew,
Mark, Luke, John, Acts, Romans, 1 Corinthians, Ephesians, Hebrews, and Revelation,
covering every major Greek passive tense/mood (aorist, present, perfect, future,
participle, infinitive, subjunctive).

**Revision from the original single-verse draft:** the claim that "Arabic avoids true
morphological passive" does not hold and is reversed here. True passive turned out to
be the single most common strategy (~14 of ~34 tokens), not a marginal alternative. The
derived-stem strategy the original rule was built on (Mark 1:9) is real but narrower —
it clusters around a specific verb class, not passive voice generally.

### 1. True passive — finite internal-vowel passive (faʿala → fuʿila/yufʿalu) and true passive participle (mafʿūl/mufʿal pattern) — the single most common strategy overall
Same underlying mechanism (participle vs. finite form of the same passive stem); treat
as one family. High confidence — 14 confirmed instances, spanning every tense sampled.
Participle often takes a copula for a periphrastic "is/was X-ed" reading (copula
secondary, participle primary, same as English/Hindi) or stands bare in a zero-copula
predicate (Arabic's own present copula is itself zero):
- ἐγεννήθη ("was born") → `وُلِدَ` (wulida): primary 1:1
- γέγραπται ("it is written") → `مَكْتُوبٌ` (maktūbun, bare) or `هُوَ مَكْتُوبٌ` (with
  copula): primary `مَكْتُوبٌ`; secondary `هُوَ` when present
- τὸ ῥηθέν ("that which was spoken," a formula repeated 6× in Matthew's fulfillment
  citations) → `مَا قِيلَ` (mā qīla): `قِيلَ` (true internal-vowel passive of قال "to
  say") primary; `مَا` (substantivizing relativizer, ↔ τό) primary
- a naming participle (λεγομένην/καλούμενος-type, "a city called Nazareth") → `يُقَالُ
  لَهَا`/`تُسَمَّى` ("it-is-said-to-her"/"is-named"): a stable Arabic naming-formula
  equivalent, primary

### 2. Dedicated intransitive/unaccusative verb — no voice marking at all, the verb's own lexical meaning is inherently intransitive
High confidence, very common (6+ instances) — both translations converge on the
identical verb every time, especially `تَمَّ`/`يَتِمُّ` (tamma/yatimmu, "to become
complete") for πληρόω-passive "be fulfilled," confirmed 3×. Primary alone, no
periphrasis, no secondary tokens:
- πληρωθῇ → `يَتِمَّ`; σωθήσεται → `يَخْلُصُ` (from خَلَصَ khalaṣa "become saved");
  ἐξηράνθη → `يَجِفُّ` (from جَفَّ jaffa "become dry")

### 3. Active-form derived-stem verb (Form V/VII/VIII) with reflexive/middle/resultative semantics — real but narrower than a general passive strategy
High confidence for this specific verb class (7 instances, both translations always
pick *some* derived stem, though not always the same Form or root) — clusters around
verbs describing the SUBJECT'S OWN physical/experiential change of state: βαπτίζω
specifically, plus deponent/middle-passive verbs of motion or bodily change (recline,
cling/join, be taken up, be filled):
- ἐβαπτίσθη → `ٱعْتَمَدَ` (Form VIII) or `تَعَمَّدَ` (Form V): primary despite being
  morphologically active
- ἀνελήμφθη ("was taken up") → `ٱرْتَفَعَ` (Form VIII); πληρωθῆτε ("may be filled") →
  `تَمْتَلِئُوا` (Form VIII) — confirms this isn't limited to motion verbs

For ordinary transitive passives (was caught, was written, was sent, was rejected),
expect strategy 1 or 5 instead — do not present strategy 3 as the general Arabic
passive default.

### 4. Adjectival/stative predicate (negated copula + pronoun + active participle used predicatively) — narrow, single instance
Low confidence: ὑποτάσσεται negated → `لَيْسَ هُوَ خَاضِعًا` (laysa huwa khāḍiʿan, "it
is not submissive"): primary `خَاضِعًا`; secondary `لَيْسَ`, `هُوَ`. May simply be a
participial variant of strategy 2 (both trace to the same intransitive verb خَضَعَ).

### 5. Active-voice conversion (agent promoted to subject) — a real translation-register tendency, confirmed almost exclusively in ONAV
Medium confidence (4 clear instances, all ONAV — AVD never converted to active in this
sample when a true-passive/passive-participle alternative was available):
- ῥηθὲν ὑπὸ κυρίου → AVD keeps `قِيلَ...مِنَ ٱلرَّبِّ` (true passive + min-agent);
  ONAV converts fully: `قَالَهُ ٱلرَّبُّ` ("the Lord said it")

**Pattern:** expect AVD specifically to preserve Greek passive voice far more reliably
than a more dynamic translation would; when aligning AVD, active-conversion is the less
likely outcome, not a coin-flip alternative. Voice conversion is bidirectional — a
Greek ACTIVE verb can render as an Arabic passive too (John 15:6 ONAV: συνάγουσιν/
βάλλουσιν "they gather/cast" → `تُجْمَعُ`/`وَتُطْرَحُ`, true passives) — do not assume
a Greek-active verse guarantees an Arabic-active rendering.

### 6. Nominalization — abstract/legal-register passive infinitives recast as a verbal-noun (maṣdar) phrase with no verb at all
Low confidence, single instance (Heb 9:16, a legal-formula verse), likely limited to
register-heavy passages: φέρεσθαι ("to be established/proven") → `بَيَانُ مَوْتِ
ٱلْمُوصِي` (bayānu mawti al-mūṣī, "a declaration of the death of the testator" —
verbal noun + iḍāfa chain, no verb at all).

### Explicit agent (ὑπό/διά + case) — never a literal "by"
Align the Greek preposition primary to whichever the specific translation uses:

| Greek construction | AVD | ONAV |
|---|---|---|
| ὑπὸ + person (Mark 1:9) | `مِنْ` (min) | `عَلَى يَدِ` (ʿalā yad, idiom) |
| ὑπὸ + person (Matt 1:22) | `مِنَ` (min) | (active-converted, no prep) |
| ὑπὸ πάντων (Matt 10:22) | `مِنَ` (min) | `لَدَى` (ladā, "among/with") |
| διὰ + person (Matt 21:4) | `بِ-` (bi-, FUSED proclitic) | `بِلِسَانِ` (bi-lisāni, "by the tongue of," idiom) |
| παρὰ θεοῦ (John 1:6) | `مِنَ` (min) | (active-converted, no prep) |

Note the AVD Matt 21:4 case: the agent preposition itself can be a fused proclitic
(`بِٱلنَّبِيِّ` = bi- + al- + nabiyy, "by-the-prophet," one token) — this interacts
directly with the fused-proclitics rule above; ὑπό/διά is pulled in as an additional
primary source token exactly like any other fused preposition, not uniquely to
passive-agent constructions.

**Remaining open questions:** whether the AVD-conservative/ONAV-dynamic split in
strategy 5 is a stable property of these two translations or an artifact of this
sample; whether strategy 4 is a genuine third strategy or a variant of strategy 2;
whether strategy 6 generalizes beyond legal-formula register; whether the strategy 1
vs. 5 split holds the same way for present-tense passives (no instance sampled).

---

## NEGATION **[arb]**

Arabic negation particle choice is conditioned by tense/aspect, not free stylistic
variation the way it is in Hindi. Confirmed against a 24-verse sample spanning Matthew,
Mark, Luke, John, Acts, Romans, Hebrews, 1 John, and Revelation, covering aorist,
perfect, present, prohibition, nominal/existential, compound-list, οὐκέτι/οὔπω, and
emphatic (οὐ μή) negation.

| Particle | Slot | Typical Greek trigger |
|---|---|---|
| لا (lā) | present/gnomic negation; AND all prohibitions (μή + imperative or aorist subjunctive alike) | οὐ, μή |
| لم (lam) + jussive | any negated event Greek presents as completed/perfective — aorist AND perfect, not just "simple past" | οὐ/μή + aorist, perfect, or "not yet" perfective sense |
| لن (lan) + subjunctive | future negation | οὐ + future |
| ما (mā) | attested as a real alternative to لم for negating a perfect-type verb (ONAV) | οὐ, μή |
| لا النافية للجنس / ليس (laysa) | nominal/existential negation — translator-variable, no confirmed conditioning factor | negated ἔστιν / supplied-copula ellipsis |

**Revision from the original draft:** لم is broader than "simple past" — confirmed for
aorist (Matt 13:58 οὐκ ἐποίησεν → `لَمْ يَصْنَعْ`), perfect (John 3:18 μὴ
πεπίστευκεν → `لَمْ يُؤْمِنْ`; 1 John 4:18 οὐ τετελείωται → `فَلَمْ يَتَكَمَّلْ`),
and "not yet" (John 7:6 οὔπω πάρεστιν → `لَمْ يَحْضُرْ بَعْدُ`). `لَمْ يَكُنْ`
("was not") covers both a negated continuous-past VERB and a negated predicate
NOUN/ADJECTIVE — one construction, two complement types:
- John 4:2, οὐκ ἐβάπτιζεν ("was not baptizing") → `لَمْ يَكُنْ يُعَمِّدُ`: source=[οὐ],
  target=[`لَمْ`] primary 1:1; source=[ἐβάπτιζεν], target=[`يَكُنْ`, `يُعَمِّدُ`] both
  primary (`يَكُنْ` = auxiliary "to be," parallel to English "was"; `يُعَمِّدُ` =
  lexical verb) — **contiguous**, unlike English's discontiguous "was **not**
  baptizing" (main doc §9.7.2)
- John 1:3, οὐδὲ ἕν... ἐγένετο ("nothing was made") → `لَمْ يَكُنْ شَيْءٌ`: same
  `لَمْ يَكُنْ` construction, but the complement `شَيْءٌ` is a predicate noun, not a verb

**لا covers present/gnomic negation and ALL prohibitions uniformly:**
- Matt 6:25, μὴ μεριμνᾶτε (present imperative) → `لَا تَهْتَمُّوا`
- Matt 1:20, μὴ φοβηθῇς (aorist subjunctive) → `لَا تَخَفْ` — same لا+jussive outcome
  despite the different Greek mood; Arabic doesn't grammaticalize that distinction
- Matt 7:1, ἵνα μὴ κριθῆτε ("lest," negated purpose) → AVD `لِكَيْ لَا تُدَانُوا`
  (transparent two-word "so that not") vs. ONAV `لِئَلّا تُدَانُوا` (a fused
  single-word idiom, li- + an + la) — two live strategies for negative purpose

**Compound list negation (οὐδέ)** just repeats لا with the ordinary wa- conjunction, no
dedicated lexeme: Matt 6:26, οὐ σπείρουσιν οὐδὲ θερίζουσιν οὐδὲ συνάγουσιν →
`لَا تَزْرَعُ وَلَا تَحْصُدُ وَلَا تَجْمَعُ` — first negator plain لا, each
subsequent οὐδέ gets `وَلَا`, wa- absorbed as the ordinary fused conjunction.

**Nominal/existential negation splits between لا-absolute and ليس, translator-variable
— no confirmed conditioning factor:**
- لا النافية للجنس ("لا of absolute/categorical negation") — لا governing a bare noun,
  no copula token at all: 1 John 4:18, φόβος οὐκ ἔστιν ἐν τῇ ἀγάπῃ → `لَا خَوْفَ فِي
  ٱلْمَحَبَّةِ` ("no-fear in-the-love") — ἔστιν has NO target token (NEQ, parallel to
  ordinary copula ellipsis, main doc §9.1.5)
- ليس (laysa) — a real verb-like negator: Acts 4:12, οὐκ ἔστιν... ἡ σωτηρία → `وَلَيْسَ
  بِأَحَدٍ غَيْرِهِ ٱلْخَلَاصُ`: οὐ+ἔστιν together align primary to ليس as a single
  record (parallel to compound-negation-token treatment)
- ONAV switches strategies between these two verses where AVD's choice differs too —
  genuinely translator/register-driven, not a fixed grammatical trigger.

**Emphatic negation (οὐ μή) — NO single dedicated construction.** Confirmed across 9
verses: لا and لن are BOTH attested for the identical Greek οὐ μή + aorist subjunctive
pattern, sometimes differing between AVD and ONAV on the *same* verse (Matt 23:39: AVD
`لَا تَرَوْنَنِي` vs. ONAV `لَنْ تَرَوْنِي`; John 10:28: AVD `لَنْ تَهْلِكَ` vs. ONAV
`فَلا تَهْلِكُ`) — genuinely free variation, not a rule waiting to be discovered. An
optional reinforcing intensifier (أَبَداً "never/ever", قَطُّ) is stylistic — ONAV adds
it in 6 of 9 sampled verses, AVD almost never. Align both οὐ and μή as primary in a
single record against whichever Arabic negation is used, contiguous with the verb; add
the intensifier as primary alongside when present with a motivating element (πώποτε
"ever," or the emphatic force of οὐ μή itself).

**οὐδείς/μηδείς — no dedicated Arabic negative pronoun.** The negative-pronoun subject
becomes a plain INDEFINITE noun (أَحَدٌ "someone/anyone"), with negation carried
entirely by the verb's own particle: John 1:18, θεὸν οὐδεὶς ἑώρακεν πώποτε → `ٱللهُ
لَمْ يَرَهُ أَحَدٌ قَطُّ` — οὐδείς's negation-content aligns primary to `لَمْ` (the
verb's own negator); `أَحَدٌ` aligns primary to the "someone" component of οὐδείς;
πώποτε → `قَطُّ`, primary.

**Remaining open questions:** any real conditioning factor for لا-absolute vs. ليس;
relative frequency of ما vs. لم; full characterization of أَبَداً/قَطُّ/بَعْدُ/أَيْضًا
reinforcement particles; whether a dedicated correlative "neither...nor" construction
exists distinct from plain وَلَا-repetition.

---

## PARTICIPIAL CONSTRUCTIONS **[arb]**

Confirmed against a 25-verse sample spanning Matthew, Mark, Luke, John, Acts, Romans,
Philippians, Hebrews, 1 Peter, and Revelation. Supersedes the earlier plan to import
`eng.py`'s participle handling unchanged — Arabic's own participle system (ism
al-fāʿil/ism al-mafʿūl) plus two distinct relative/generic-pronoun strategies
(`الَّذِي` vs. `مَنْ`) make the English who/whoever framing a poor structural fit.

### Substantive — three coexisting strategies, conditioned by referent type
This is a real structural split, not translator inconsistency — typologically similar
to Indonesian's yang/barangsiapa split, unlike Hindi's single-default जो.

**(a) Genuine Arabic participle (ism al-fāʿil/ism al-mafʿūl)** — attributive
modification of an already-identified/concrete noun, or elevated/hymnic register.
Primary, directly parallel to the Greek participle; a fused Greek article is a primary
companion per DEFINITENESS above, not secondary. High confidence (5 instances):
- ὁ λαὸς ὁ καθήμενος ("the people sitting [in darkness]") → `ٱلشَّعْبُ ٱلْجَالِسُ`
  (al-jālis, ism al-fāʿil from جلس "to sit")
- ὁ σπείρων (a parable's specific sower) → `ٱلزَّارِعُ` (al-zāriʿ)
- Phil 2:7 (elevated hymnic register): μορφὴν δούλου λαβών → AVD `آخِذًا` / ONAV
  `مُتَّخِذاً` — genuine ḥāl-participles

**(b) `الَّذِي` (al-ladhī, "who/which") + finite verb** — a specific/deictic referent,
often when no natural Arabic participle fits smoothly or discourse parallelism with
neighboring clauses favors a uniform clause shape. Medium confidence (2 instances, 1
direct AVD/ONAV divergence on the same verse):
- John 1:15, ὁ ὀπίσω μου ἐρχόμενος (the forerunner formula, a specific referent) → AVD
  `ٱلَّذِي يَأْتِي بَعْدِي`; **ONAV instead uses a genuine participle** (`الآتِيَ`,
  strategy a) for the exact same Greek word — confirms both strategies are live
  options for the same construction, translator-dependent.

**(c) `مَنْ` (man, "whoever") + finite verb — the DOMINANT strategy for GENERIC/gnomic
"whoever does X" formulaic refrains.** High confidence (6 instances across 3 distinct
lexemes, both translations consistent on structure every time) — the single
best-attested pattern in the sample, holding even where a corresponding Arabic
participle exists and goes unused:
- Rev 2:7 / 3:21, ὁ νικῶν ("the one who overcomes," Revelation's stock refrain) → AVD
  `مَنْ يَغْلِبُ` **identically at both verses**, despite a perfectly good active
  participle (`غَالِب`, ghālib, "conqueror") being available and NOT used
- Matt 11:15 / Rev 2:7, ὁ ἔχων ὦτα... ἀκουέτω → `مَنْ لَهُ أُذُنَانِ فَلْيَسْمَعْ`:
  `مَنْ` primary; `لَهُ` ("to him," existential-possessive for "he has") secondary,
  grammar-required with no independent Greek trigger, parallel to Hindi's
  existential-possessive pattern

**Working rule:** default to (c) `مَنْ`+finite-verb for GENERIC/gnomic substantive
participles; default to (a) genuine Arabic participle when the referent is attributive
to an already-identified concrete noun or the register is elevated/hymnic; treat (b)
`الَّذِي`+finite-verb as a fallback for a SPECIFIC/deictic referent lacking a natural
participle, or when discourse parallelism favors it.

### Adverbial (circumstantial) — finite subordinate clause is the DEFAULT, NOT Arabic's own ḥāl-construction
Confirmed 4 independent times, both translations, 3 different Greek lexemes:
`لَمَّا`/`حِينَ` ("when") + finite perfect verb, ordinary narrative aorist participles:
- ἀκούσας δέ ("having heard") → AVD `لَمَّا سَمِعَ` / ONAV `حِينَ سَمِعَ`

**A second recurring strategy** collapses the participle + following main verb into
TWO COORDINATE FINITE VERBS (`وَ`/`ثُمَّ` "and"/"then"), no subordinating conjunction
at all, for a tight two-action sequence sharing a subject:
- ὁ δὲ ἀποκριθεὶς εἶπεν ("but answering, he said") → AVD `فَأَجَابَ وَقَالَ` (two
  coordinate finite verbs); ONAV diverges, keeping a ḥāl-participle instead
  (`فَأَجَابَهُ قَائِلاً`)
- Working hypothesis (needs more data): a longer/more complex main clause favors the
  `لَمَّا`-clause; a short, tightly-bound two-action pair favors coordinate-verb
  collapse.

**`λέγων`** ("saying," introducing direct speech) has an extremely stable,
near-universal formulaic rendering independent of either strategy above:
`قَائِلًا`/`قَائِلاً` (qāʾilan, accusative indefinite ism al-fāʿil from قال "to say," a
fixed quotative ḥāl-marker) — primary 1:1 by default (confirmed 6+ times), unless the
translation collapses it into a coordinate finite verb (`وَقَالَ`) instead — both
outcomes attested, participle form more common (5 of 7).

### Genitive absolute — no distinct treatment needed
Every genitive absolute in the sample follows the same pattern as ordinary
circumstantial participles above, differing only in which temporal conjunction is
chosen — confirming Arabic tracks Greek's punctual/durative (aorist/present) aspectual
distinction via conjunction choice, not just lexically:
- **Punctual** (aorist, "X having happened") → `لَمَّا` ("when"): Matt 2:19,
  Τελευτήσαντος → `لَمَّا مَاتَ`
- **Durative** (present participle, "while X was happening") → `فِيمَا`/`بَيْنَمَا`
  ("while"): Matt 9:18, Ταῦτα αὐτοῦ λαλοῦντος → AVD `وَفِيمَا هُوَ يُكَلِّمُهُمْ`

**Explicit genitive subject (αὐτοῦ)** gets an explicit Arabic pronoun (`هُوَ`) when the
translation keeps it — primary, matching main doc §9.2.2 (an explicit genitive-absolute
subject is primary, not grammatically implied). Some translations drop the explicit
pronoun (relying on the verb's own agreement) — align it primary only when present.

**Remaining open questions:** what conditions the `لَمَّا`-clause vs.
coordinate-verb-collapse choice; whether the (a)/(b)/(c) substantive split holds up
outside this sample's Matthew/Revelation weighting (thin on Mark/Luke/Pauline
instances); a single ONAV maṣdar+preposition circumstantial variant (Matt 8:16,
`وَعِنْدَ حُلُولِ ٱلْمَسَاءِ`) — real recurring minority pattern or one-off?

---

## COMPARATIVES AND SUPERLATIVES **[arb]**

Confirmed against a 20-verse sample spanning Matthew, Mark, Luke, John, Acts,
1 Corinthians, Hebrews, Jude, and Revelation, covering synthetic comparatives,
superlatives, analytic comparatives, and an elative-superlative use. Supersedes the
earlier plan to import `eng.py`'s comparative handling unchanged.

### Rule 1 — the أَفْعَل (afʿal) elative is the default for TRUE degree adjectives; three surface forms disambiguate comparative/superlative/absolute
Arabic's elative pattern is morphologically identical for comparative and superlative;
disambiguation is purely syntactic and maps cleanly onto Greek's own distinction. High
confidence — confirmed consistently across both translations wherever both used the
elative pattern.
1. **Bare elative + `مِنْ` (min) + comparandum → comparative** ("greater than X").
   Confirmed 4×: μείζων Ἰωάννου → `أَعْظَمُ مِنْ يُوحَنَّا`: source=[μείζων],
   target=[`أَعْظَمُ`] primary 1:1; `مِنْ` primary to whatever Greek token licenses
   the comparison (typically the genitive noun — a case-driven "than" realized as an
   explicit token in Arabic, unlike English's own case-implied "than"); source=[the
   comparandum], target=[the noun after `مِنْ`] primary 1:1.
2. **Definite article + elative (al-elative) → superlative** ("the greatest/least").
   Confirmed 3×, holds across number: ὁ μικρότερος → `ٱلْأَصْغَرَ` — the article's
   Greek token is an additional primary source per the fused-article rule; the elative
   is primary to the base Greek comparative/superlative form.
3. **Bare elative, no `مِنْ`, no article → implicit/absolute comparison** ("does
   better," against an implicit discourse alternative). Confirmed 2×: primary alone; no
   secondary "than" token to add since none is present in the Arabic.

### Rule 2 — πρῶτος/ἔσχατος ("first"/"last") map to dedicated ordinal lexemes, NOT the elative
Confirmed 6×. `أَوَّل` (awwal, "first") and `آخِر` (ākhir, "last/other") are closed-
class ordinal words, not built on the elative pattern, and carry no comparative/
superlative morphological distinction — Greek's own suppletive/lexical superlatives map
to Arabic's equally lexical ordinals:
- Matt 19:30 (chiastic "first will be last, last first") → `أَوَّلُونَ...آخِرِينَ...`:
  each Greek ordinal primary 1:1 to its Arabic counterpart
- Mark 9:35, ἔσχατοι πάντων ("last of all") → `آخِرَ ٱلْكُلِّ`: an ordinary iḍāfa
  construct-genitive, no secondary token needed for "of"

**Caveat (Acts 2:17):** ἔσχαταις ἡμέραις ("last days") uses a DIFFERENT lexeme,
`ٱلْأَخِيرَة` (al-akhīra, an ordinary attributive adjective, not `آخِر`) — "last" has
(at least) two lexical strategies depending on collocation; treat both as free lexical
variants for alignment purposes, both primary 1:1 to ἔσχατος.

**Also flagged:** πρεσβύτεροι (morphologically a Greek comparative of πρέσβυς but a
frozen substantive "elders") → `شُيُوخُكُمْ`, an ORDINARY noun with no elative marking
at all — when a Greek COMPARATIVE-tagged token is really a lexicalized noun, check
whether it's genuinely comparing degree before applying Rule 1/2.

### Rule 3 — a third superlative strategy: bare elative in an iḍāfa chain ("least of the matters")
Medium confidence, single verse (Luke 12:26) shows AVD using the al-elative pattern
while ONAV uses a bare elative in construct with a definite plural noun (`أَصْغَرِ
الأُمُورِ`, "the-smallest-of-the-matters") — functionally equivalent to English's
"least of these." The elative is the construct-first term (drops its own article per
the iḍāfa rule in the base doc); a translator-supplied generic completion noun with no
Greek anchor is NEQ target, not secondary.

**Bottom line on the "elative ambiguity" question:** Arabic's single afʿal form
covering both comparative and superlative resolves cleanly via co-occurring markers
(Rule 1) — not a genuine source of ambiguity once the marker is checked. The real
wrinkle is Rule 2: a Greek COMPARATIVE tag does not reliably predict which Arabic
morphological strategy (elative vs. dedicated ordinal vs. plain adjective) will appear;
check the specific Greek lemma.

**Remaining open questions:** μᾶλλον does not reliably get its own token (may absorb
into an adjacent conjunction, e.g. ἀλλὰ μᾶλλον → `بَلْ` alone); πλείων/πλεῖον used as a
loose quantifier sometimes renders as a plain adjective (`كَثِيرَةٍ`) rather than the
elative — check whether the Greek form is a true degree comparison or a loose
quantifier; degree-correlative constructions (τοσούτῳ...ὅσῳ) don't map token-for-token
cleanly and may need native-speaker input to divide the periphrasis.

---

## CONDITIONAL CONSTRUCTIONS **[arb]**

Confirmed against a 19-verse sample (8 first-class εἰ+indicative, 8 third-class
ἐάν+subjunctive, and all 3 second-class/contrary-to-fact conditions in the whole NT)
spanning Matthew, Mark, Luke, John, Acts, Romans, 1 Corinthians, Hebrews, 1 John, and
Revelation. Supersedes the earlier plan to import `eng.py`'s conditional handling
unchanged — Arabic has (at least) four particles in play, not the simple إِنْ/لَوْ
two-way split originally assumed.

### `لَوْ` (law) — dedicated to genuine contrary-to-fact conditions (2nd class), confirmed 3/3, no exceptions
Every 2nd-class Greek condition (εἰ + past indicative + ἄν) in the sample — the only 3
in the whole NT — uses `لَوْ` in both AVD and ONAV:
- John 11:32, εἰ ἦς ὧδε οὐκ ἄν ... ἀπέθανεν → `لَوْ كُنْتَ هَهُنَا لَمْ يَمُتْ أَخِي`

`لَوْ` → primary 1:1 to εἰ, but ONLY reachable for a genuine 2nd-class Greek condition.
The apodosis regularly takes a `لَ-` (la-) proclitic prefix on a `كَانَ`-periphrasis —
the closest Arabic correspondent to ἄν, primary to ἄν, fused into the apodosis verb's
record per the ordinary fused-proclitic pattern. **Negated counterfactual apodoses do
NOT reliably carry an ἄν-correspondent** — AVD sometimes drops it entirely (John 11:32:
`لَمْ يَمُتْ`, plain negated jussive, ἄν → NEQ) while ONAV fuses `لَ-` into the negator
(`لَمَا`, "would-not-have," a portmanteau where `لَ-` IS primary to ἄν) — check per
instance, do not assume.

**Caution:** a superficially similar `لَ-` prefix marks an unrelated construction — the
"lam of the oath" combined with an energetic-mood verb (after e.g. ὤμοσεν "he swore") —
do not conflate the two; only the counterfactual-apodosis `لَ-` is primary to ἄν.

### `إِنْ` (in) — the default for GENUINE open/hypothetical conditions of EITHER Greek 1st or 3rd class
Confirmed 8+/11 genuine conditionals. **Overturns the assumption that إِنْ tracks one
Greek class specifically** — Arabic does not preserve the Greek 1st/3rd-class
distinction with a different particle. The real split is إِنْ (open) vs. لَوْ
(counterfactual), a two-way split, not a three-way match to Greek's three classes:
- Rom 3:3 (εἰ + indicative, 1st-class) → `إِنْ كَانَ قَوْمٌ لَمْ يَكُونُوا أُمَنَاءَ`
- Matt 18:15 (ἐάν, 3rd-class) → `إِنْ أَخْطَأَ`

`إِنْ` primary 1:1 to εἰ/ἐάν regardless of Greek mood. Correlative ἐάν τε...ἐάν τε
("whether...or") — each clause gets its own `إِنْ`, correlative structure preserved.

### `إِذَا` (idhā) — a third particle, for ἐάν when the condition is framed as likely/expected/habitual
Attested 2/8 in the 3rd-class sample — matches the traditional Classical Arabic
distinction between إِنْ (genuinely open) and إِذَا (temporal-conditional "when," used
for likely/habitual conditions), now confirmed live rather than just textbook
description:
- Luke 16:30, ἐάν τις... πορευθῇ... μετανοήσουσιν (a live, expected hypothetical within
  the parable's own logic) → `إِذَا مَضَى إِلَيْهِمْ وَاحِدٌ... يَتُوبُونَ`

Both `إِنْ` and `إِذَا` align primary 1:1 to the Greek conditional particle regardless
of which is chosen — the choice is a translator framing judgment, not a different Greek
trigger. Needs more sampling to confirm the distinction holds at scale.

### `مَهْمَا` (mahmā) and similar free-choice relatives — for ἐάν fused with an indefinite pronoun ("whatever/whoever")
Single instance: Mark 6:23, ὅ τι ἐάν με αἰτήσῃς δώσω σοι → `مَهْمَا طَلَبْتِ مِنِّي
لَأُعْطِيَنَّكِ` — `مَهْمَا` replaces the whole ὅ τι ἐάν combination. When ἐάν combines
with a relative pronoun (ὅ τι ἐάν, ὃς ἐάν, ὅπου ἐάν) to form a generalizing
"whatever/whoever" clause rather than a plain conditional, expect a dedicated Arabic
free-choice particle (`مَهْمَا`, `مَنْ`, `حَيْثُمَا`) instead of `إِنْ` — a distinct
construction, closer to substantive-participle "whoever" handling (see PARTICIPIAL
CONSTRUCTIONS) than to ordinary conditionals. Flagged as provisional, single instance.

### `εἰ μή` = "except/only" — NOT a conditional sentence; a fixed exceptive idiom, high-frequency
Confirmed 4/4 (both translations, dominated an early naive "1st-class" sampling
bucket): renders uniformly as `إِلَّا` (illā), never `إِنْ`, never `لَوْ`. Typically
follows a negated main clause, restricting an otherwise universal/negative statement:
- 1 Cor 1:14, οὐδένα ὑμῶν ἐβάπτισα εἰ μὴ Κρίσπον → `لَمْ أُعَمِّدْ أَحَدًا مِنْكُمْ
  إِلَّا كِرِيسْبُسَ`: source=[εἰ, μή], target=[`إِلَّا`] — both Greek particles
  primary as a single fused unit, parallel to how μὴ γένοιτο is treated as an
  idiom-like fixed unit. Do NOT treat εἰ as ordinary conditional and μή as ordinary
  negation here — together they form one exceptive marker with no independent
  "if"/"not" meaning. Given how common εἰ μή is, this is a high-value, high-frequency
  rule.

### `εἰ` as an indirect-question marker ("whether") — a Koine Hebraism, not conditional at all
Single instance: Acts 1:6, ...εἰ ἐν τῷ χρόνῳ τούτῳ ἀποκαθιστάνεις... → `هَلْ فِي هَذَا
ٱلْوَقْتِ تَرُدُّ...` — εἰ introducing an embedded yes/no question after a verb of
asking renders as `هَلْ` (hal), the ordinary Arabic yes/no interrogative. Align εἰ
primary to `هَلْ` when the translation converts the embedded question to direct-
question form. A known Koine phenomenon documented in Greek grammars — the trigger is a
Greek-grammar fact, not an Arabic one, so this needs less further Arabic-specific
sampling than the particle choices above.

### Apodosis `فَ-` (fa-) — no Greek trigger, unrepresented
Extremely common as a fused proclitic on the apodosis's first word, but no sampled
Greek apodosis had its own particle (τότε/ἄρα/οὖν) to trigger it — matches the main
doc's existing "supplied then" rule. Simply don't represent it — nothing to mark NEQ
either, since it's fused, not an independent token. Confirmed non-obligatory (absent in
some apodoses, e.g. Rev 3:20), a stylistic default, not grammatically required the way
the counterfactual `لَ-` is.

**Remaining open questions:** whether the إِذَا/إِنْ split holds at scale; whether
`مَهْمَا`-treatment generalizes beyond the single sampled instance to ὃς ἐάν/ὅπου ἐάν;
whether the AVD/ONAV negated-counterfactual-apodosis divergence is a stable
register difference or verse-specific (only 1 negated 2nd-class apodosis existed to
check, since only 3 second-class conditions exist in the whole NT).

---

## αὐτός **[arb]**

Confirmed against a 17-verse sample spanning Matthew, Mark, Luke, John, Acts, Romans,
1–2 Corinthians, Philippians, 1 Thessalonians, Hebrews, and 1 Peter, covering ordinary
pronoun uses (all cases), intensive uses, "same" uses, and emphatic/contrastive subject
uses. Supersedes the earlier plan to import `eng.py`'s AUTOS handling unchanged.

### Ordinary pronoun (genitive/accusative) — almost always ZERO independent target token
The majority case by far: αὐτός is absorbed as a possessive/object suffix fused
directly onto the noun or verb it belongs to, per FUSED PROCLITICS AND SUFFIXES above —
stated explicitly here since it needed calling out rather than left implicit. High
confidence (8+ instances):
- τὸ ὄνομα αὐτοῦ / τὸν λαὸν αὐτοῦ → `ٱسْمَهُ` (ism-ahu) / `شَعْبَهُ` (shaʿb-ahu):
  source=[ὄνομα, αὐτοῦ], target=[`ٱسْمَهُ`] — both primary, one fused token
- ἤγειρεν αὐτήν → `وَأَقَامَهَا` (wa-aqāma-hā): αὐτήν fused as an object suffix,
  primary alongside the verb's own primary link

### Dative pronoun — sometimes fuses onto a SEPARATE small preposition-carrier token, not the main verb
High confidence (3 instances) — a real, distinct sub-pattern not covered by the general
fused-suffix rule as originally stated. Some Arabic verbs take a bare object (dative
pronoun fuses directly onto the verb); others require a preposition, in which case the
dative pronoun fuses onto THAT token instead (`لَهُ`/`لَهَا`/`لَهُمْ` "to/for
him/her/them", `إِلَيْهِ`/`إِلَيْهَا`/`إِلَيْهِمْ`) — itself a separate whitespace
token from the verb, and itself a fusion of preposition+suffix (ordinary fused-
preposition treatment applies). Do not assume the dative pronoun's correspondent is
always inside the verb's own token:
- λέγει αὐτῇ → `قَالَ` `لَهَا` (TWO tokens): αὐτῇ primary to `لَهَا`, not to `قَالَ`
- διανεύων αὐτοῖς → `يُومِئُ` `إِلَيْهِمْ` (two tokens): same pattern

### Intensive ("himself/herself/itself") — نَفْس (nafs, "self") + possessive suffix, highly consistent
High confidence — 5 confirmed instances across persons/genders, both translations
converge every time, never a dedicated intensive pronoun:
- αὐτὸς ἐγώ ("I myself") → `أَنَا` `نَفْسِي`: source=[ἐγώ], target=[`أَنَا`] primary
  1:1; source=[αὐτός], target=[`نَفْسِي`] primary 1:1
- αὐτὸ τὸ πνεῦμα ("the Spirit itself," neuter in Greek) → `ٱلرُّوحُ` `نَفْسُهُ`
  (masculine suffix, agreeing with Arabic's own grammatical gender for روح, not Greek's
  neuter — a surface-form difference, not a problem)

The intensified noun/pronoun always gets its own separate primary record, matching the
main doc's AUTOS pattern (§9.5.1) — only the target-side morphology differs (a
noun+suffix construction rather than a dedicated particle).

### "Same" — THREE distinct strategies by construction type, not one
More fragmented than the single consistent نفس-strategy for ordinary intensive use;
check which sub-construction is in play:
1. **Identity-of-source/material** ("of the same lump") → `وَاحِدَة` ("one/single"),
   NOT نفس or عين: ἐκ τοῦ αὐτοῦ φυράματος → `مِنْ كُتْلَةٍ وَاحِدَةٍ`: source=[αὐτοῦ],
   target=[`وَاحِدَةٍ`] primary
2. **Adverbial "in the same way/likewise"** (τὸ αὐτό, adverbial) → `عَيْن` (ʿayn,
   idiomatically "very/self") + possessive suffix: τὸ αὐτὸ καὶ ὑμεῖς χαίρετε → AVD
   `وَبِهَذَا` `عَيْنِهِ`: primary. ONAV drops it entirely for a generic "likewise" —
   when dropped, αὐτό → NEQ target, no token realizes it.
3. **Predicate "is the same" (unchanging identity)** → a fixed doubled-pronoun idiom
   `هُوَ هُوَ` ("he [is] he"): Heb 13:8, ὁ αὐτός (substantivized article+αὐτός as a
   predicate, implied copula) → AVD/ONAV both `هُوَ` `هُوَ` — not compositional,
   cannot cleanly assign "the" to one `هُوَ` and "same" to the other. Treat as a single
   N:1 record: source=[ὁ, αὐτός], target=[`هُوَ`, `هُوَ`], both target tokens primary.

### Emphatic/contrastive subject use — LOW CONFIDENCE, translator-variable
The messiest category, only 5 instances total — flagged as a working hypothesis, not a
firm rule. Sometimes an independent `هُوَ`, sometimes zero token:
- **Zero token** (absorbed into verb agreement) — confirmed 3×, all narrative
  topic-continuity uses (fronted αὐτός resuming an already-active subject, no real
  contrastive force): Luke 8:54, αὐτὸς δὲ κρατήσας → AVD `وَأَمْسَكَ`, no separate
  token for αὐτός.
- **Independent `هُوَ` used** — confirmed 2×, both genuinely CONTRASTIVE (explicitly
  contrasting the subject with a different, previously-mentioned subject): Matt 3:11,
  αὐτὸς ὑμᾶς βαπτίσει ("HE will baptize you," contrasting the Coming One with John) →
  AVD `هُوَ سَيُعَمِّدُكُمْ`: source=[αὐτός], target=[`هُوَ`] primary.

**Tentative rule (not confirmed at scale):** contrastive emphasis → independent `هُوَ`,
primary; topic-continuity/paragraph-transition use → zero token. When zero token
results, this is NOT NEQ — the pronoun's grammatical content is fully carried by the
verb's own agreement, so it is more naturally left unrecorded, parallel to how ordinary
pro-drop subject pronouns are handled.

**Remaining open questions:** does the contrastive-vs-topic-continuity split hold at
scale (the least confident, most alignment-relevant finding here — "zero token, don't
NEQ it" vs. "primary token" is a decision the LLM will face constantly)? Is the dative-
pronoun-on-separate-token pattern fully predictable from Arabic verb valence, or
translator-variable too (only 2 verbs checked)? Is `هُوَ هُوَ` doubling better treated
as `meta.is_idiom: true` instead of a plain N:1 record (both defensible)? Does the
نَفْس+suffix strategy also cover true reflexives (distinct from intensive use), or does
Arabic use a different construction (e.g. a dedicated reflexive derived stem) — not
addressed in this sample.

---

## ὅτι **[arb]**

Confirmed against a 24-verse sample spanning Matthew, Mark, Luke, John, Acts,
1 Corinthians, 2 Corinthians, Philippians, James, 1 John, and Revelation, covering
causal, content-clause, and recitative uses. Supersedes the earlier plan to import
`eng.py`'s HOTI handling unchanged — causal and content-clause ὅτι do not collapse to
one particle, content-clause "that" itself splits by matrix-verb type, and recitative
ὅτι is not uniformly NEQ.

### Causal ("because/for") → `لِأَنَّ` (li-anna), a fused preposition+complementizer, often further fused with a pronominal-subject suffix
High confidence (8 instances, both translations converge every time). `لِأَنَّ` = `لِ`
("because of") + `أَنَّ` (complementizer) — itself a fused-proclitic construction. When
the causal clause's subject is a supplied pronoun (from Greek verb agreement, no
separate Greek token), that pronoun fuses onto `لِأَنَّ` as a suffix — secondary
(supplied-subject-pronoun), same pattern as an ordinary supplied subject (main doc
§9.2.1), just packaged into the fused token:
- ὅτι εἴδετε (καὶ ἐχορτάσθητε) → `لِأَنَّكُمْ رَأَيْتُمْ`: ὅτι primary to
  `لِأَنَّكُمْ`; the `-kum` suffix is secondary
- ὅτι τὸ μωρὸν τοῦ θεοῦ (subject is a full NOUN, not a pronoun) → `لِأَنَّ جَهَالَةَ
  ٱللهِ`: `لِأَنَّ` appears bare, no suffix, since there's no pronoun to fuse
- διότι (διά+ὅτι) triggers the identical `لِأَنَّ` strategy as bare causal ὅτι

**Alternative causal strategy (single instance, both translations agree):** `إِذْ`
(idh, "since/as," a lighter causal-temporal connective, NOT built on أَنَّ, no suffix)
— attested once for a causal clause embedded in ongoing narrative description; needs
more sampling to characterize when preferred over `لِأَنَّ`.

### Content-clause ("that") — TWO complementizers, chosen by matrix-verb type
A genuine split, not free variation — check the governing verb, not just clause
structure:
- **`أَنَّ` (anna)** after verbs of knowing/believing/understanding/hoping/being-
  ignorant-of (γινώσκω, πιστεύω, οἶδα, ἐλπίζω, ἀγνοέω-type). High confidence, 6
  confirmed instances, no exceptions: οἶδα ὅτι... → `أَعْلَمُ أَنِّي أَمْكُثُ`: ὅτι
  primary to `أَنِّي` (fused 1sg suffix secondary as supplied subject)
- **`إِنَّ` (inna)** specifically after verbs of SAYING (λέγω/εἶπον-type), functioning
  almost as a quotative marker. Medium confidence, confirmed in minimal pairs within
  single verses — the deciding factor is the matrix verb, not clause structure: an
  embedded-object-clause structurally identical to the `أَنَّ` cases still gets `إِنَّ`
  when the matrix verb is "say": ὑμεῖς λέγετε ὅτι θεὸς ἡμῶν ἐστιν → `تَقُولُونَ
  أَنْتُمْ إِنَّهُ إِلَهُكُمْ`: ὅτι primary to `إِنَّهُ`

Any pronominal-subject suffix fused onto either complementizer follows the same
secondary-supplied-pronoun logic as the causal case above.

### Recitative (introducing direct speech, no "that" meaning) — check what the translation did; NOT uniformly NEQ
Two live outcomes, both attested — this is a genuine departure from a single-pattern
default and should not be assumed either way:
(a) **Punctuation only** (colon/quotation marks, no opener word) → ὅτι NEQ, matching
   main doc §9.7.3, still a valid and common outcome: Mark 12:19, Μωϋσῆς ἔγραψεν ἡμῖν
   ὅτι ἐάν τινος ἀδελφὸς ἀποθάνῃ... → AVD `كَتَبَ لَنَا مُوسَى: إِنْ مَاتَ...` (colon
   only; the quoted content opens with its own particle `إِنْ` "if," a plausible reason
   no `إِنَّ` also appears)
(b) **A quotative-opener word is inserted at the boundary** (`إِنَّ`+optional pronoun
   suffix, or occasionally a different word like `حَقّاً` "truly") → ὅτι recitative
   aligns PRIMARY to that opener, since its presence tracks the Greek ὅτι rather than
   occurring independently of it: John 6:14, ἔλεγον ὅτι Οὗτος ἔστιν... → AVD `قَالُوا:
   «إِنَّ هَذَا هُوَ...»`; ONAV instead uses `حَقّاً` in the same structural slot — a
   different lexical choice filling the same position, not إِنَّ itself, but the same
   functional role.

**Confirmed by a negative control:** when the Greek has NO ὅτι at all before a bare/
asyndetic direct quote (Matt 3:9's first clause), AVD uses punctuation only, no `إِنَّ`
— confirming `إِنَّ`-insertion correlates with the presence of a Greek ὅτι (recitative
or content), not simply Arabic's own free quotative habit — which supports treating
outcome (b) as a genuine primary link rather than an unrelated stylistic addition.

**Remaining open questions:** is the `لِأَنَّ` vs. `إِذْ` causal split conditioned by
register/discourse position, or free variation (only 1 `إِذْ` instance)? Does the
`أَنَّ`/`إِنَّ` content-clause split hold at scale, and are there matrix verbs that
pattern ambiguously (only 9 instances total, unevenly split 6/3)? What determines
whether Arabic inserts a recitative-boundary opener versus using punctuation alone (the
"quoted content already has its own opening particle" hypothesis is speculative,
untested beyond one instance)? Should ONAV's `حَقّاً`-type alternative openers be
treated the same as `إِنَّ` (primary to recitative ὅτι), or are they a distinct
phenomenon?

---

## IMPERSONAL VERBS **[arb]**

Confirmed against a 22-verse sample (of only 121 IMPERSONAL-tagged verses in the whole
NT — δεῖ/ἔξεστιν/ἔξεστι/πρέπει/συμφέρει/δοκεῖ). Supersedes the earlier plan to import
`eng.py`'s IMPERSONAL handling unchanged.

**Headline: Arabic impersonal verbs are bare 3rd-masculine-singular finite forms (or
zero-copula adjectival predicates) with NO subject pronoun at all — never an explicit
`هُوَ` ("it"). The English "dummy it → NEQ" rule does NOT carry over.** NEQ asserts a
positive claim that a word is untranslated — but there is no token slot for "it" in
Arabic to begin with. Simply leave the dummy subject unrecorded, the same way ordinary
pro-drop subjects are handled when fully recoverable from verb agreement.

**δεῖ ("it is necessary/must"):** `يَنْبَغِي` (yanbaghi) is AVD's dominant strategy
(8/9 sampled); ONAV instead consistently prefers `لَابُدَّ` (lā budda, "there is no
escape from," a fixed idiom) — different lexemes, identical bare-3ms mechanism. `يَجِبُ`
(yajibu) is attested once as an AVD alternative — treat all three as free lexical
variants, primary 1:1 to δεῖ.
  δεῖ γενέσθαι → `يَنْبَغِي أَنْ يَكُونَ`: δεῖ primary to `يَنْبَغِي`; γενέσθαι primary
  to `يَكُونَ`; `أَنْ` secondary

**ἔξεστιν/ἔξεστι ("it is lawful"):** `يَحِلُّ` (yaḥillu) dominates in religious-law
contexts (Sabbath/purity); `يَجُوزُ` (yajūzu, broader "permissible") attested once for a
civil/political context (the tribute-to-Caesar question) — possibly domain-conditioned,
only 1 instance, flagged as a hypothesis.

**συμφέρει ("it is better/profitable"):** TWO free-variant strategies — (a) a bare
zero-copula adjectival predicate `خَيْرٌ` (khayrun, "[it is] better"), AVD's more
common choice for "better X than Y" senses, primary alone, no verb, no copula; (b) a
genuine finite verb `يَنْفَعُ` (yanfaʿu, "profits"), with the person-affected as a
fused OBJECT suffix directly on the verb (contrast the AUTOS section's dative
preposition-carrier pattern — `نفع` takes a bare object in Arabic).

**Complementary clause — THREE strategies, not one, confirmed across all three
impersonal-verb families:**
1. `أَنْ` + subjunctive (bare infinitive-substitute, same logical subject) — the
   default; `أَنْ` is a pure grammatical connector, secondary (main doc §8.4); the
   following verb is primary to the Greek infinitive.
2. `أَنَّ` + full clause with its own subject (when the embedded clause's subject
   differs from/is more explicit than the matrix predicate implies) — `أَنَّ` still
   secondary, but licenses its own case marking on the clause's subject (a purely
   Arabic-internal requirement, no Greek trigger).
3. Bare verbal noun (maṣdar) — no `أَنْ`/`أَنَّ` at all (e.g. `يَنْبَغِي فِيهَا
   ٱلْعَمَلُ`, `هَلْ يَحِلُّ ٱلْإِبْرَاءُ`) — the maṣdar itself is primary to the
   Greek infinitive; no secondary connector token exists in this strategy.

**Caution for anyone sampling further:** not every IMPERSONAL-tagged δοκέω instance is
genuinely impersonal — Greek δοκέω is also used personally ("τις δοκεῖ..." = "if
anyone thinks himself...", confirmed 2× in this sample), which renders as an ordinary
personal verb (`يَظُنُّ`/`ظَنَّ`) with an explicit subject, no impersonal construction
at all. The phenomenon detector does not distinguish these — check context.

**Remaining open questions:** is δεῖ → `يَجِبُ` (vs. dominant `يَنْبَغِي`) register- or
genre-conditioned, or free variation (1 instance)? Is ἔξεστιν → `يَجُوزُ` domain-
conditioned (civil vs. religious-law), or free variation (1 instance)? Is the choice
among the three complementation strategies fully predictable from clause structure, or
translator/register-variable too? No genuinely impersonal δοκέω ("it seems to me," μοι/
σοι δοκεῖ) instance was sampled — needs deliberate targeted sampling. πρέπει was not
reached in this sample at all.

---

## INFINITIVAL CONSTRUCTIONS **[arb]**

Confirmed against a 22-verse sample. Supersedes the earlier plan to import `eng.py`'s
INFINITIVE handling unchanged — **Classical Arabic has NO true infinitive form**, so
the strategy depends entirely on which of (at least) five Greek infinitive uses is in
play; a single "'to' secondary to the infinitive" rule does not transfer.

### 1. Complementary infinitive (after θέλω/δύναμαι/ἄρχομαι/ἔξεστιν-type verbs) → `أَنْ` (an) + subjunctive — the cleanest, most consistent pattern
High confidence, both translations converge every time: `أَنْ` here is a real,
standalone target token (not fused) realizing the Greek infinitive's "to"-function —
BOTH `أَنْ` and the following subjunctive verb are primary (unlike English's secondary
"to" — `أَنْ` is the actual subordinator, doing more structural work).
  χρείαν ἔχω...βαπτισθῆναι ("I have need to be baptized") → `مُحْتَاجٌ أَنْ أَعْتَمِدَ`:
  source=[βαπτισθῆναι], target=[`أَنْ`, `أَعْتَمِدَ`] — both primary
When the infinitive clause is negated, expect either an embedded `لَا` inside the
`أَنْ`-clause, or a lexicalized negative matrix verb + nominalized complement — both
attested, check per verse.

### 2. Purpose infinitive — MULTIPLE coexisting strategies; check the whole series, not each infinitive independently
- **Bare purpose infinitive** (no τό/εἰς τό/πρός τό) → `لِ-` (fused proclitic) +
  subjunctive — rock-solid across both translations, treat like any other fused
  preposition (primary alongside the verb).
- **Prepositional-articular purpose infinitive** (πρός τό/εἰς τό + inf) → `لِكَيْ`
  (li-kay) + subjunctive — a heavier, free-standing two-word marker, primary 1:1.
- **Coordinated purpose-infinitive series** — the marker is often established once,
  with later members sharing it via plain `وَ` + subjunctive, no repeated marker.
- **Purposive verb-serialization** — no overt marker at all: a motion verb followed
  directly by bare coordinated present-tense verb(s) (`ذَهَبَ يُعَلِّمُ` "went [and]
  taught," parallel to English "go teach"). When used, align the infinitive primary to
  the bare finite verb with no marker token to add.

### 3. Articular infinitive as SUBJECT/PREDICATE (nominal use) → a plain abstract noun, NOT a verb form
High confidence, both translations independently nominalize: τὸ ζῆν/τὸ ἀποθανεῖν ("to
live"/"to die," as clause subjects) → `ٱلْحَيَاةَ`/`ٱلْمَوْتُ` (genuine lexical nouns) —
the Greek article fuses as al- per DEFINITENESS above; the infinitive is primary to the
noun despite the total word-class change.

### 4. Articular infinitive with a TEMPORAL preposition (μετά τό/ἐν τῷ) → a finite subordinate clause, NOT nominalization
Distinct from §2 and §3 — matches the same `لَمَّا`/`فِيمَا`-type pattern as
circumstantial participles and genitive absolutes (see PARTICIPIAL CONSTRUCTIONS):
μετὰ τὸ παθεῖν αὐτόν ("after he suffered") → `بَعْدَ مَا تَأَلَّمَ`: μετά primary to
`بَعْدَ`; τό primary to `مَا`; παθεῖν primary to a FINITE verb; the infinitive's own
accusative subject (αὐτόν) has no separate token, folded into the finite verb's
agreement.

### 5. Accusative + infinitive indirect discourse → the SAME `أَنَّ`/`إِنَّ` complementizer system as ὅτι content clauses (see ὅτι below) — but sometimes converts to a bare direct quotation instead
Medium-high confidence: accusative+infinitive after a verb of saying gets `إِنَّ`
(τίνα με λέγουσιν...εἶναι → `مَنْ يَقُولُ ٱلنَّاسُ إِنِّي أَنَا؟`), matching the
إِνᾶ-after-λέγω finding below exactly — not a structurally distinct alignment problem
from ὅτι content clauses. The infinitive copula (εἶναι) has NO target token — zero-
copula predicate. After a cognition/expectation verb, `أَنَّ` is used instead, and a
complementary infinitive can nest inside the `أَنَّ`-clause as its own `أَنْ`-clause.
**Confirmed AVD/ONAV divergence on the same verse (Acts 28:6):** the whole clause
sometimes converts to a bare DIRECT quotation with no complementizer at all — check per
translation, do not assume either outcome.

**Remaining open questions:** does the `لِ-`-vs-`لِكَيْ` split for purpose infinitives
correlate with anything predictable, or is it dominated by coordination-sharing
behavior (§2)? Is negation-within-a-complementary-infinitive reliably embedded `لَا` vs.
lexicalized-negative-matrix-verb, or free variation (1 instance, translations diverge)?
Does the temporal-articular-infinitive → finite-clause strategy hold for ἐν τῷ as well
as μετά τό (only μετά τό sampled)? Is the accusative+infinitive → bare-quotation
conversion a recurring AVD pattern or a one-off (1 instance)?

---

## ἵνα CLAUSES **[arb]**

Confirmed against a 24-verse sample. Supersedes the earlier plan to import `eng.py`'s
HINA handling unchanged. **TWO genuinely distinct systems, not one** — Arabic's
purpose-marker choice tracks whether ἵνα is a VERBAL COMPLEMENT or a genuine ADVERBIAL
PURPOSE/RESULT clause; do not treat all ἵνα uniformly as "purpose conjunction, primary."

### 1. Complement-clause ἵνα (θέλω/παρακαλῶ/εἶπον-as-command + ἵνα) → bare `أَنْ` + subjunctive, NO purpose marker
High confidence — 5 instances, both translations converge every time. When ἵνα
substitutes for what would otherwise be an infinitive complement of a matrix verb of
wanting/urging/commanding, Arabic uses the same `أَنْ`-complement strategy as an
ordinary complementary infinitive. The trigger is the SYNTACTIC ROLE of the ἵνα-clause,
not a closed lexical list — confirmed extending beyond θέλω to παρακαλῶ and
εἶπον-as-command:
  ὅσα ἐὰν θέλητε ἵνα ποιῶσιν ὑμῖν οἱ ἄνθρωποι (Golden Rule) → `تُرِيدُونَ أَنْ يَفْعَلَ
  ٱلنَّاسُ بِكُمُ`: ἵνα ποιῶσιν primary to `أَنْ يَفْعَلَ` — ἵνα itself is primary to
  `أَنْ`, a genuine correspondent, just not a "purpose marker" one

**Contrast — the SAME matrix-verb family with a GENUINE adverbial purpose clause
attached does NOT collapse to `أَنْ`:** confirmed by a clean minimal pair — Gal 4:17's
θέλω has its OWN infinitive complement, with a separate purpose ἵνα attached (→ full
`لِكَيْ`, not `أَنْ`); 1 Thess 4:13 shows the same pattern. Same verb, opposite
syntactic role, opposite Arabic strategy — the clearest evidence the split is
structural, not lexical.

### 2. Adverbial purpose ἵνα → a FAMILY of free-variant particles: `لِ-` (fused), `لِكَيْ` (full), `كَيْ` (bare)
High confidence (13 instances) — genuinely interchangeable, confirmed by a single verse
(John 1:7) using BOTH `لِ-` and `لِكَيْ` for two consecutive, structurally identical
purpose clauses with no discernible conditioning factor. When `لِ-` is used, ἵνα's
Greek token is pulled in as an additional primary source alongside the verb it's fused
to, per FUSED PROCLITICS above; when `لِكَيْ`/`كَيْ` appear as their own standalone
token, ἵνα aligns primary 1:1 directly.

### 3. Result/consecutive ἵνα and ὥστε → `حَتَّى` (ḥattā, "until/so that") — a real alternative, leaning result/consecutive but NOT strictly reserved for it
Medium-high confidence (4 instances), one clear counter-example (a translator uses
`حَتَّى` for an ordinary purpose ἵνα too) — treat as a genuine alternative to the
purpose family generally, with a lean toward result/consecutive contexts, not a hard
categorical rule. `حَتَّى` primary 1:1 to ἵνα/ὥστε either way.

### 4. Negative purpose (ἵνα μή, "lest") — (at least) FOUR-FIVE live realizations, genuinely free variation, NOT a fixed AVD-vs-ONAV split
**Revises an earlier finding from the NEGATION section** (which claimed AVD uses
`لِكَيْ لَا` and ONAV uses `لِئَلَّا`, based on a single verse) — this does NOT hold
once more instances are checked. Confirmed realizations: `لِكَيْ لَا` (two words),
`لِئَلَّا` (fused, li-+an+la), `كَيْ لَا` (bare kay+la), `حَتَّى لَا` (ḥattā+la), and a
zero-marker outcome (clause simply coordinated with `فَلَا`, no purpose word at all).
**Both AVD and ONAV use multiple variants each** — genuinely free variation across both
translations, not a stable per-translation register difference; the earlier single-
data-point generalization should not have been trusted. Align both ἵνα and μή as
primary in a single record against whichever realization the translation used.

**Remaining open questions:** is there any real conditioning factor for `لِ-` vs.
`لِكَيْ` vs. `كَيْ` (register, verb class, clause position), or is it purely free
variation as John 1:7 suggests? Does `حَتَّى`'s result-leaning tendency hold up
statistically? For the negative-purpose zero-marker outcome, what is the correct
alignment call when literally no dedicated word realizes either particle — NEQ, or a
looser primary link to the bare negator? This sample did not encounter ἵνα used
independently as a jussive-like construction (a known minor Koine usage) — worth
checking separately.

---

## VERBAL ASPECT **[arb]**

Confirmed against a 20-verse sample. Supersedes the earlier plan to import `eng.py`'s
VERBAL_ASPECT handling unchanged.

**Headline: Arabic marks iterative/conative/ingressive nuances EXPLICITLY LESS OFTEN
than Greek/English do** — a plain perfective verb with the nuance left unmarked/
implicit was the majority outcome (~60% of sampled tokens), not the exception. This is
a real departure from the main doc's implicit assumption (§9.1.3) that when a
translator renders aspect explicitly, both elements are primary — for Arabic, the
translator very often does NOT render it explicitly, and that is the more frequent
outcome. Do not assume explicit marking by default; check per verse.

**Iterative/habitual/durative imperfect:** explicit `كَانَ` (kāna, "was") + imperfect
verb (or + adjective/participle for a maintained STATE) — both primary, matching main
doc §9.1.3, confirmed 5×, both translations converge on the periphrasis whenever it's
used:
  ἀπέλυεν ("he used to release") → `وَكَانَ يُطْلِقُ`: source=[ἀπέλυεν],
  target=[`كَانَ`, `يُطْلِقُ`] — both primary
**Collapses to a plain perfective verb, no periphrasis** when (a) negated, or (b) the
imperfect denotes a single/distributive event within one narrated episode rather than
genuine repetition — primary alone, nothing extra to align, parallel to how a Greek
historical present collapses to an ordinary past tense (main doc §9.1.2).

**Ingressive imperfect/aorist ("began to X"):** when marked, one of (at least) four
attested auxiliaries — `صَارَ` (ṣāra), `قَامَ` (qāma), `جَعَلَ` (jaʿala), `بَدَأَ`
(badaʾa) — + imperfect verb, both primary; auxiliary choice is inconsistent even within
a single verse across translations (free lexical variation). **A plain perfective verb
with NO ingressive marking is actually the MORE common outcome** in this sample — treat
explicit marking as one live but non-guaranteed option to check for, not the default.

**Conative imperfect ("tried to X but did not succeed"):** **genuinely UNMARKED when
the Greek verb is an ordinary action verb.** The project's own canonical example (main
doc §9.1.3, Mark 15:23, ἐδίδουν, "they offered him wine... but he did not take it")
gets NO conative marking in either Arabic translation — a plain perfective verb
(`أَعْطَوْهُ`/`قَدَّمُوا لَهُ`), primary alone, with the "attempted but refused" sense
left entirely to the following negated clause, exactly as bare Greek leaves it to
pragmatic inference rather than grammatical marking. **Only appears "marked" when the
Greek verb's OWN LEXEME already means "try/attempt"** (πειράζω, ἐπιχειρέω) — Arabic
then supplies `حَاوَلَ` (ḥāwala, "to try") + `أَنْ` + subjunctive complement, but this
is ORDINARY LEXICAL correspondence (the Greek word's own meaning IS "try," main doc
§3.4), not a special periphrastic aspect construction, even though the Greek form
happens to be imperfect tense.

**Remaining open questions:** is the single sampled true-conative instance (Mark 15:23)
generalizable, or could other rare conative-imperfect verses show explicit marking?
Does the negation-blocks-habitual-periphrasis pattern hold at scale (1 instance)? What
precisely conditions the plain-perfective-vs-periphrastic-`كَانَ` choice for iterative/
habitual imperfects? Is there any pattern to which of the four ingressive auxiliaries a
translation picks? No epistle instances with clear aspectual nuance surfaced in this
sample (candidates were essentially all Gospels/Acts narrative) — worth confirming
whether that reflects genuine scarcity in epistolary Greek or a sampling gap.

---

## Cross-translation methodology note

Every structural claim above that says "confirmed" or gives an instance count was
checked against **both** AVD and ONAV for the same verse before being written down.
Where the two translations agreed on structure despite differing lexical choices (e.g.
AVD `وَلَدَ` vs. ONAV `أَنْجَبَ` for ἐγέννησεν, or AVD `مِنْ` vs. ONAV `عَلَى يَدِ` for
the passive agent), that is treated as confirmation of a general Arabic-grammar pattern
rather than an AVD-specific quirk. Where AVD and ONAV diverged on the *same* verse
(several confirmed cases: John 1:15's participle-vs-relative-clause choice, Matt 23:39's
لا-vs-لن emphatic negation, John 11:32's negated-counterfactual-apodosis treatment,
Rev 2:7's dual-vs-singular number), that divergence is documented as genuine free
variation or a possible register difference, not resolved into a single rule.

Sampling was done in four passes: an initial 4-verse pass (Matt 1:1–2, Mark 1:9, John
4:2) establishing the base fused-clitic/iḍāfa/article material, followed by five
separate ~20–30-verse stratified samples (PASSIVE, NEGATION, PARTICIPLE, COMPARATIVE,
CONDITIONAL), two more ~17–24-verse samples (AUTOS, HOTI), and a final round of four
~20–24-verse samples (IMPERSONAL, INFINITIVE, HINA, VERBAL_ASPECT) — every conditional
block in `arb.py` now has its own dedicated sample, none still import `eng.py`
unchanged. Each sample spans Gospels, Acts, epistles, and Revelation and is drawn from
the full set of NT verses `detect_phenomena` tags for that construction. This is still
well short of the
systematic, corpus-wide sampling done for Hindi (which
checked hundreds to low-thousands of instances per construction, e.g. "all 1,339
SBLGNT article+participle sequences") — treat every rule here as a well-evidenced
working hypothesis, not a final answer, especially where only 1–2 instances support a
claim (flagged individually in each section's "remaining open questions").

ONAV is a substantially more dynamic/paraphrastic translation than AVD (it supplies an
explicit demonstrative subject "this" at Matt 1:1 where AVD has none, prefers more
contemporary lexical choices throughout, and converted to active voice far more often
than AVD when both had a true-passive option) — useful for confirming which structural
patterns are general-Arabic versus AVD-specific, but not a reliable source for AVD's own
register or literalness level. Where the two translations disagree, prefer AVD's choice
as the primary target for `arb.py` (since AVD/Van Dyck is this project's actual target
edition) and treat ONAV's divergence as evidence of what else is grammatically possible.

---

## Open questions for native-speaker/Arabist review

The native-speaker review referenced in the status note above confirmed the document
overall as "very good"; the specific dispositions of each item below were not recorded
back into this document, so the list is left as-is rather than marked resolved without
evidence for each individual point.

1. **Is the fused definite article primary or secondary?** This document currently
   treats it as primary (because al- is a real definite-article morpheme, not a
   grammatically-supplied filler word), breaking from every other supported language's
   article-as-secondary default. Confirm whether this distinction is worth making, or
   whether consistency with the rest of the system favors treating it as secondary
   regardless.
2. **PASSIVE VOICE**: is the AVD-conservative/ONAV-dynamic split in active-voice
   conversion a stable property of these two translations, or an artifact of this
   sample? Is the adjectival/stative-predicate strategy (§4) a genuine third strategy or
   a participial variant of the dedicated-intransitive strategy (§2)? Does the
   nominalization strategy (§6) generalize beyond legal-formula register? Does the
   true-passive/active-conversion split hold the same way for present-tense passives
   (none sampled)?
3. **NEGATION**: is there any real conditioning factor for لا-النافية-للجنس vs. ليس in
   nominal negation, or is it purely free stylistic variation? How common is ما
   relative to لم for perfect/aorist negation (only 1 instance, ONAV only)? Full
   characterization of أَبَداً/قَطُّ/بَعْدُ/أَيْضًا reinforcement particles. Does
   Arabic have a dedicated correlative "neither...nor" construction distinct from plain
   وَلَا-repetition?
4. **PARTICIPLE**: does the (a)/(b)/(c) substantive-participle split hold up outside
   this sample's Matthew/Revelation weighting (thin on Mark/Luke/Pauline instances)?
   What conditions the لَمَّا-clause vs. coordinate-verb-collapse choice for
   circumstantial participles? Is the single ONAV maṣdar+preposition circumstantial
   variant (Matt 8:16) a real recurring minority pattern or a one-off?
5. **COMPARATIVE**: does μᾶλλον reliably absorb into an adjacent conjunction, or was
   that specific to the ἀλλὰ μᾶλλον collocation sampled? Does πλείων/πλεῖον's
   plain-adjective-vs-elative split hold at scale? How should the τοσούτῳ...ὅσῳ
   degree-correlative periphrasis be divided token-by-token?
6. **CONDITIONAL**: does the إِذَا/إِنْ "likely vs. open" split hold at scale (only 2
   إِذَا instances found)? Does the مَهْمَا free-choice-relative treatment generalize
   to ὃς ἐάν/ὅπου ἐάν (only 1 instance)? Is the AVD/ONAV negated-counterfactual-
   apodosis divergence (John 11:32) a stable register difference or verse-specific
   (only 1 negated 2nd-class apodosis exists in the whole NT to check)?
7. **When does Arabic use an explicit preposition (من / لِ) instead of ʾiḍāfa for a
   Greek genitive?** — needs broader sampling to characterize the split.
8. **Dual number**: AVD tends to track Greek number literally while ONAV normalizes to
   Arabic's natural default (dual for paired body parts) regardless of Greek number
   (confirmed live at Rev 2:7) — confirm this AVD/ONAV split holds beyond one instance,
   and find a case where Arabic dual would plausibly appear against Greek plural rather
   than singular.
9. **AUTOS**: does the contrastive-vs-topic-continuity split for emphatic/contrastive
   subject use hold at scale (only 5 instances, the least confident finding in that
   section)? Is the dative-pronoun-on-separate-token pattern fully predictable from
   Arabic verb valence? Should `هُوَ هُوَ` doubling (Heb 13:8) be `meta.is_idiom: true`
   or a plain two-token N:1 record? Does `نَفْس`+suffix cover true reflexives, distinct
   from intensive use?
10. **HOTI**: is the `لِأَنَّ` vs. `إِذْ` causal split conditioned by register/discourse
    position, or free variation (only 1 `إِذْ` instance)? Does the `أَنَّ`/`إِنَّ`
    content-clause split hold at scale (9 instances, unevenly split)? What determines
    whether Arabic inserts a recitative-boundary opener versus punctuation alone? Should
    ONAV's `حَقّاً`-type alternative openers be treated the same as `إِنَّ`?
11. **IMPERSONAL**: is δεῖ → `يَجِبُ` (vs. dominant `يَنْبَغِي`) register/genre-
    conditioned or free variation (1 instance)? Is ἔξεστιν → `يَجُوزُ` domain-
    conditioned (civil vs. religious-law) or free variation (1 instance)? Is the choice
    among the three complementation strategies fully predictable from clause structure?
    No genuinely impersonal δοκέω ("it seems to me") instance was sampled at all — the
    two δοκέω instances found turned out to be the unrelated personal construction.
    πρέπει was not reached in this sample.
12. **INFINITIVE**: does the `لِ-`-vs-`لِكَيْ` purpose-marker split correlate with
    anything predictable, or is it dominated by coordination-sharing behavior? Is
    negation-within-a-complementary-infinitive reliably embedded `لَا` vs. lexicalized-
    negative-matrix-verb (1 instance, translations diverge)? Does the temporal-
    articular-infinitive → finite-clause strategy hold for ἐν τῷ as well as μετά τό
    (only μετά τό sampled)? Is the accusative+infinitive → bare-quotation conversion a
    recurring AVD pattern or a one-off (1 instance)?
13. **ἵνα CLAUSES**: is there any real conditioning factor for `لِ-` vs. `لِكَيْ` vs.
    `كَيْ` (register, verb class, clause position), or is it purely free variation as
    John 1:7 suggests? Does `حَتَّى`'s result-leaning tendency hold up statistically?
    What is the correct alignment call for the negative-purpose zero-marker outcome
    (NEQ vs. a looser primary link to the bare negator)?
14. **VERBAL ASPECT**: is the single sampled true-conative instance (Mark 15:23)
    generalizable, or could other rare conative-imperfect verses show explicit marking?
    Does the negation-blocks-habitual-periphrasis pattern hold at scale (1 instance)?
    What precisely conditions the plain-perfective-vs-periphrastic-`كَانَ` choice for
    iterative/habitual imperfects? No epistle instances with clear aspectual nuance
    surfaced in this sample — worth confirming whether that reflects genuine scarcity
    in epistolary Greek or a sampling gap.
