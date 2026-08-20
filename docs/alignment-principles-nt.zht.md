# Alignment Principles — Mandarin Chinese, Traditional script (zht), New Testament

**STATUS: Rebuilt from raw text + linguistic reasoning (no gold alignment data used
anywhere), matching the `ind`/`hin`/`arb` methodology. An earlier version of this
document was built from Clear-Bible's CUVMPS/CU2010T alignment JSONs; that version was
retracted by direction — see "Methodology" below for the full account, including a
concrete example of it producing a wrong conclusion. Not yet reviewed by a native
Mandarin speaker.**

Guidelines used by `refine-alignment` when aligning Bible translations into Traditional
Chinese against the Greek New Testament (SBLGNT) source.

Sections marked **[zht]** contain Chinese-specific rules or examples. Unmarked sections
are shared with the English guidelines (`alignment-principles-nt.md` and
`prompt/nt/eng.py`).

Target text: Chinese Union Version, Modern Punctuation, Traditional orthography (CUV,
staged locally at `data/alignments/alignments-cmn/data/targets/CUV/`). Every worked
example below is quoted directly from that data.

Source files (not yet written): `src/text_align/refine/prompt/nt/zht.py`

---

## Methodology

**No alignment data is used anywhere in this document.** Every claim rests on:

1. **Raw parallel text spot-checking** — for each construction, a random sample of
   Greek source tokens matching the relevant morphology/lemma (typically 12–25 verses
   per construction) is pulled from `data/sources/SBLGNT.tsv`, and the corresponding
   verse is read directly from two independent Traditional Chinese translations' raw
   target text: our own **CUV** (`data/alignments/alignments-cmn/data/targets/CUV/`)
   and **BOCCB2023T** (Biblica® Open Chinese Contemporary Bible 2023, Traditional —
   `data/alignments/alignments-cmn/data/targets/BOCCB2023T/`), a genuinely independent
   modern translation, not another Union Version edition. Verified directly: Genesis
   1:1 in the two editions reads 起初，上帝創造天地 (CUV) vs. 太初，上帝創造了天地
   (BOCCB2023T) — different opening word for "beginning," different aspect marking —
   confirming these are independently translated texts, not script/edition variants of
   the same wording.
2. **Whole-corpus raw character/token frequency counts** — unconditioned totals (e.g.
   "`被` appears 464 times in CUV's whole NT text") computed directly from both
   editions' target TSVs. These are real, repeatable, and re-derivable by anyone with
   the two files — but they are *not* conditioned on a specific Greek construction the
   way a true alignment-derived percentage would be, so they corroborate a pattern's
   existence and rough scale rather than proving an exact rate.
3. **General Mandarin/Koine Greek linguistic knowledge**, the same kind of reasoning
   `ind`/`hin`/`arb` relied on for their original passes.

**Why this document was rebuilt**: an earlier version used Clear-Bible's `alignments-
cmn` repo — specifically Biblica's `SBLGNT-CUVMPS-manual.json` gold alignment — as the
primary evidentiary basis, without surfacing that as a methodology change requiring
approval first. That data source was later found to raise two separate problems: (a)
its target, CUVMPS, was confirmed to differ from our own CUV in more than just script —
a direct check found CUVMPS uses `神` for "God" in verses where CUV uses `上帝` (the
well-documented 神版/上帝版 dual-edition tradition in Chinese Bible publishing), plus an
85.4% verse-level token-count mismatch between the two TSVs that was never fully
explained; and (b) a second alignment source used for cross-checking, UBS's CU2010T
alignment, was directly confirmed to be unreliable for this purpose — it systematically
leaves grammatical particles unrecorded (98.8% of negation particles showed
"unaligned" despite the Chinese text plainly containing a negator in every sampled
verse) because it was built for a different purpose than word-level alignment
verification. Neither CUVMPS's nor CU2010T's alignment data is used in this rebuild.

**What this means for the claims below**: precision is lower than an alignment-derived
pass could give (no exact corpus-wide percentages), but every example is directly
verifiable by re-reading the cited verse in both editions' raw text — nothing here
depends on trusting a third party's alignment methodology or completeness.

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Greek word(s) are behind
this translation word.

---

## ALIGNMENT PHILOSOPHY **[zht]**

Alignments are generous: include case-implied prepositions, grammatically-implied
particles, and construction-required markers (disposal `將`/`把`, aspect `了`/`著`/`過`,
nominalizer/relativizer `的`) even where Greek has no separate corresponding word for
them, so long as the target word exists *because of* a grammatical or syntactic feature
carried by a specific Greek token.

Prefer one record per source token — split rather than group. Combine into N:M records
only when tokens form an inseparable semantic/idiomatic unit or the target text cannot
otherwise assign words to individual source tokens.

Grammar-required translation words with no independent lexical content of their own
(structural `的`, aspect particles, the disposal marker, reflexive substitution for a
coreferential possessor) are secondary to the source token whose grammar/discourse
context requires them — not NEQ. NEQ is reserved for words with no source-language
anchor at all.

---

## TOKEN ROLES **[zht]**

- **primary** — direct lexical or semantic connection to the Greek token
- **secondary** — exists only because of a grammatical or syntactic feature of the
  Greek token (case, aspect, voice, coreference, subordination); no independent Greek
  word backs it
- correspondence to a different Greek token → separate record

**Structural constraints:** every record ≥1 primary per populated side; a lone token on
a side cannot be secondary; each target token ID in exactly one record per verse.

---

## ARTICLES **[zht]**

Chinese has no article system at all. Spot-checked against 20 randomly sampled verses
containing Greek articles (40+ individual article tokens, cross-checked against
BOCCB2023T): the overwhelming majority have **no target correspondent at all** — the
noun stands bare. Confirmed unconditioned frequency in CUV's whole NT: `這` 2,097
instances, `那` 1,855 instances, against 11,043 instances of `的` and thousands of
Greek articles in the source — consistent with demonstratives being a minority
phenomenon relative to total article count, though this is not a precise ratio since
`這`/`那` also translate genuine Greek demonstrative pronouns (οὗτος/ἐκεῖνος), not only
the bare article.

Example: `ὁ θεὸς` → `上帝` alone — no secondary needed, no NEQ needed.

The minority branch that *can* supply a target word is demonstrative/anaphoric
reference (`這`/`那`), confirmed in the sample:

- Acts 23:7 `ἐν ταύταις ταῖς ἡμέραις` ("in those days") → CUV `那時` — both editions
  agree (BOCCB2023T: `那時`).
- Acts 25:7 `οἱ ἀπὸ Ἱεροσολύμων καταβεβηκότες Ἰουδαῖοι` ("the Jews who had come down
  from Jerusalem") → CUV `那些從耶路撒冷下來的猶太人` — both editions agree (BOCCB2023T:
  `那些從耶路撒冷下來的猶太人`).
- 2 Cor 10:12 `τῶν ἑαυτοὺς συνιστανόντων` ("those who commend themselves") → CUV
  `那自薦的人` — both editions agree (BOCCB2023T: `那些自我推薦的人`).
- Acts 13:32 `τὴν... ἐπαγγελίαν` ("the promise") → CUV `那應許祖宗的話` (demonstrative
  present) vs. BOCCB2023T `上帝給我們祖先的應許` (no demonstrative, restructured) — a
  real editorial divergence on the SAME Greek article, showing this choice is a real
  translator decision, not a mechanical rule.

---

## COPULA / "TO BE" (εἰμί) STRATEGIES **[zht]**

Greek's single verb εἰμί splits across several distinct Chinese verbs depending on what
kind of clause it is heading — confirmed against a 20-verse spot-check spanning
Matthew, Mark, Luke, John, Acts, 1–2 Corinthians, and Philippians/1 Thessalonians:

1. **Predicate-nominal identity "was X"** — `是` is the clear majority default.
   Examples: Matt 14:26 `Φάντασμά ἐστιν` → `是個鬼怪`; John 4:19 `Σαμαρίτης ἦν` →
   `是撒馬利亞人`; 1 Cor 3:16 `ναὸς θεοῦ ἐστε` → `你們是上帝的殿`.
2. **Emphatic identity `就是`** — real and not rare, and critically, **independently
   confirmed in BOTH editions at different verses**, directly refuting an earlier
   (retracted) claim that `就是` was CUVMPS-specific: John 5:35 (`μήποτε αὐτὸς εἴη ὁ
   χριστός`, "whether he might be the Christ") → BOCCB2023T `也許約翰就是基督` (CUV uses
   plain `是` here — the *opposite* direction of the earlier retracted claim); John
   14:21 (`ἐκεῖνός ἐστιν ὁ ἀγαπῶν με`) → both editions independently use `就是` (CUV
   `這人就是愛我的`; BOCCB2023T `就是愛我的人`); John 8:58 (`Ἐγώ εἰμι`, the divine
   self-declaration) → both editions independently use `就是` (`我就是`); 1 Cor 3:16 →
   BOCCB2023T adds `就是` (`你們就是上帝的殿`) where CUV uses plain `是`. The pattern:
   `就是` tends to appear on a fronted/marked/emphatic predicate-nominal construction in
   the Greek, but which specific instances get it is a real per-translator, per-verse
   choice — not a fixed rule, and not limited to either edition.
3. **Comitative "was with"** — a compound verb, not bare copula + preposition. Mark
   2:19 / John 17:5 (`ἦν ... μετ' αὐτῶν` / `ἤμην ... μεθ' ὑμῶν`) → CUV consistently uses
   `同在` (`同在的時候`, `我與你們同在`); BOCCB2023T consistently uses a different
   surface form for the same strategy, `在一起` (`還在一起`, `跟你們在一起`) — same
   underlying comitative-copula strategy, different lexical realization per edition.
4. **Existential "there is/was"** — `有`. John 1:1 `ἦν ὁ λόγος` → `太初有道`; John 5:26
   (a "having life in himself" construction) similarly uses `有`.
5. **Locative "to be at"** — `在`. Acts 4:37/5:12 (people "were" together at a place) →
   `在...廊下`/`在一處`.

---

## 的 (DE) — MULTI-FUNCTION PARTICLE **[zht]**

`的` is the single hardest-working function word in Mandarin, observed across every
sample pulled for this document performing at least four distinct roles:

1. **Possessive/genitive marker** — secondary to the genitive-case Greek noun/pronoun.
   Matt 18:23 `τῶν δούλων αὐτοῦ` → `他僕人` (with `的` between pronoun and noun in the
   fuller form `他的僕人`, both attested depending on phrasing).
2. **Attributive-adjective linker** — secondary to the adjective it links; seen
   throughout (e.g. `永生的道`, `聖潔的恩典`).
3. **Nominalizer for substantive participles** — always secondary to the participle it
   nominalizes. Confirmed repeatedly: John 3:16-style `ὁ πιστεύων` constructions and
   Rom 12:8-style lists of substantive participles (`ὁ παρακαλῶν... ὁ μεταδιδοὺς... ὁ
   προϊστάμενος... ὁ ἐλεῶν`) → CUV `勸化的...施捨的...治理的...憐憫人的` — a chain of
   bare `的`-nominalized verbs with no separate pronoun/head-noun needed, matching
   Indonesian's "yang" and French/Spanish "qui/que."
4. **Related nominalizer `所`** — a second, more literary nominalizing strategy
   surfaced repeatedly alongside `的`, especially for passive/patient-oriented senses
   (see PASSIVE below): Acts 10:17 `τὸ ὅραμα ὃ εἶδεν` ("the vision which he saw") → CUV
   `所看見的異象` (`所` + verb + `的` + noun, a discontinuous nominalizing frame around
   the verb). This wasn't isolated as a separate pattern in the earlier alignment-based
   draft — worth its own attention alongside `的`.

---

## BA/JIANG DISPOSAL CONSTRUCTION (將/把) **[zht]**

Mandarin has a dedicated "disposal construction" that fronts a definite/specific direct
object before the verb, marked by `將` (literary/written register — dominant in CUV) or
`把` (colloquial). The marker itself is a pure grammatical device with **no independent
lexical content** — secondary to the direct-object noun phrase it fronts, not to the
verb.

**Important disambiguation caveat, discovered during this rebuild**: `將` is genuinely
polysemous. Of 15 verses sampled by searching for the bare character `將`/`把`, 2 were
false positives — `將` used as a "the seven days were **about to** finish" future/
imminent-aspect adverb (Acts 21:27 `那七日將完`) and as part of the fixed compound noun
`將來` ("the future," Heb 9:28 `將來要...顯現`) — neither is the disposal construction
at all. The raw character-frequency counts below (492 CUV / 429 BOCCB2023T instances of
`將`) are therefore an overcount of the true disposal-construction rate by a real but
unquantified margin; disambiguate by checking whether `將`/`把` is immediately followed
by a definite noun phrase + verb (disposal) versus a bare verb or the fixed noun `來`
(non-disposal).

Genuine disposal-construction examples confirmed across the 15-verse sample (13 of 15
after excluding the two false positives), spanning Matthew, Acts, and Revelation:

- Matt 5:24 `καὶ ἄφες ἐκεῖ τὸ δῶρόν σου` (restructured with a supplied "leave") → CUV
  `就把禮物留在壇前`
- Acts 18:16 `ἀπήλασεν αὐτοὺς ἀπὸ τοῦ βήματος` ("drove them from the tribunal") → CUV
  `就把他們攆出公堂`
- Rev 6:16 (people asking the mountains to hide them) → CUV `把我們藏起來`

Object aligns overwhelmingly to a noun or pronoun as expected; the marker itself is
secondary, never NEQ.

---

## REFLEXIVE 自己 **[zht]**

Spot-checked against 15 randomly sampled verses containing αὐτός (third-person
pronoun): only 1 showed a genuine reflexive-自己 substitution (Rom 9:11's "just as God
willed," CUV `隨自己的意思`, BOCCB2023T `按自己的旨意` — both editions independently
add `自己` reinforcing the implicit subject-coreference in "God... willed," even though
the Greek has no separate pronoun there at all). The other 14 were ordinary
non-reflexive third-person pronoun renderings (`他`/`他的`/`他們`/`她`), confirming the
earlier finding's shape: reflexive substitution is a real but genuinely narrow
phenomenon, conditioned specifically on the pronoun's referent circling back to the
clause's own subject — not a general pronoun-rendering strategy. Whole-NT unconditioned
counts (534 CUV / 516 BOCCB2023T instances of `自己`) are consistent with a real but
minority-of-pronoun-instances usage rate.

Both categories established earlier (direct correspondence to a Greek reflexive
ἑαυτοῦ/σεαυτοῦ/ἐμαυτοῦ, vs. genuine substitution for a plain αὐτός) remain the expected
split — this rebuild did not have the volume to re-derive their relative proportions
without alignment data, so treat the ~49%/~32% split from the earlier (retracted) pass
as a plausible but unconfirmed estimate, not a settled number.

---

## PASSIVE VOICE **[zht]**

Spot-checked against 25 randomly sampled Greek passive-stem verbs (aorist/present/
perfect passive across Matthew, Mark, Luke, John, Acts, Romans, 1–2 Corinthians,
Galatians, Hebrews, 1 Peter, 2 Peter, Revelation), cross-checked against BOCCB2023T:

**Unmarked / restructured active — the clear majority** (roughly 19 of ~30 individual
verb tokens in the sample): the Greek passive verb is rendered with a plain Chinese
verb carrying no passive morphology, or the whole clause is restructured as active
voice. Examples: Acts 22:28 `γεγέννημαι` ("I have been born [a citizen]") → CUV `我生來
就是` (both editions identical); Rev 11:13 `ἀπεκτάνθησαν` ("were killed") → CUV `因地震
而死的` ("died because of the earthquake" — the agent-demoting passive recast as an
intransitive death-event); Luke 24:47 `κηρυχθῆναι` ("[a message] is to be proclaimed")
→ CUV `人要...傳...道` (recast fully active, "people will proclaim..."); 2 Pet 1:3
`δεδωρημένης` ("having been given") → CUV `已將...賜給我們` (recast fully active with
God as subject, using the BA-construction to front the gift).

**A genuinely new finding from this raw-text pass**: a classical/literary
passive-marking construction, `為...所` / `所...的`, distinct from `被`, appearing
twice in one verse (1 Cor 4:9): `ἀγνοούμενοι` ("unknown") → CUV `不為人所知` ("not
known by people"); the parallel clause `ἐπιγινωσκόμενοι` ("well known") → CUV `人所共知
的` ("commonly known by people"). This construction did not surface in the earlier
alignment-based draft at all — that pass only searched for `被`/`受`/`得`/`蒙`
characters, so `為...所`/`所...的` instances were silently miscounted as "unmarked."
Treat `為`+agent+`所`+verb as a real, if apparently rare, marked-passive strategy
alongside `被` and the receive-construction below.

**`受`/`得`/`蒙` receive-construction** — present but genuinely rare in this sample (1
clear instance: 1 Cor 4:9 `παιδευόμενοι` "disciplined" → CUV `受責罰`), consistent with
it being a real but minority strategy rather than the general default (correcting the
original nine-verse spot-check's over-generalization from baptism-specific examples,
which both editions still confirm independently — Mark 1:5/1:9's `ἐβαπτίζοντο`/
`ἐβαπτίσθη` → `受...洗` in both CUV and BOCCB2023T).

**`被`** — zero instances in CUV's own text across this 25-verse sample, though
BOCCB2023T used `被` twice at verses where CUV didn't (1 Cor 8:5 `λεγόμενοι` "so-called"
→ BOCCB2023T `被稱為神明的` vs. CUV's unmarked `稱為神的`; Rom 10:10 `πιστεύεται`
"believes/is believed" → BOCCB2023T `被稱為義人` vs. CUV's active-restructured `心裏相
信就可以稱義`). This is consistent with `被` being genuinely rare and edition-dependent
rather than a default, but the sample is far too small (0 CUV instances observed) to
assign it a precise rate. Whole-NT unconditioned counts (464 CUV / 597 BOCCB2023T
instances of `被`) show it is not absent from CUV's text generally — just not landing
on any of the 25 randomly sampled passive-stem verbs in this pass.

**A reflexive/self-directed conversion, also new to this pass**: 2 Pet 2:12
`φθείρονται` ("are destroyed/corrupted") → CUV `敗壞了自己` ("ruin themselves") —
Greek passive recast as an active verb with a reflexive object, a fourth distinct
restructuring strategy alongside unmarked/`為...所`/`受`-construction.

**Revised guidance**: do not assume any particular marking strategy for a passive verb.
The unmarked/restructured-active outcome is clearly the most common in this sample;
`被`, `受`/`得`/`蒙`, and `為...所`/`所...的` are all real but minority strategies, and
which one (if any) appears for a given verse is not predictable from the Greek voice
morphology alone — check the actual target text.

---

## ASPECT PARTICLES (了/著/過) **[zht]** — tag: VERBAL_ASPECT

Mandarin marks verbal aspect (not tense) with post-verbal particles rather than
inflection. Spot-checked against 12 randomly sampled Greek perfect-tense verbs:

- **`了` (perfective/completed action)** — the default for telic/punctual completed
  events. Matt 26:56 `γέγονεν` ("has taken place") → CUV `成就了`; John 17:6
  `τετήρηκαν` ("have kept") → CUV `遵守了`.
- **`過` (experiential, "have ever...")** — for anterior/experiential-reference
  perfects, especially recalling a past event's occurrence rather than its completed
  result. John 5:37 `μεμαρτύρηκεν` ("has testified") → CUV `作過見證`; Rom 9:29
  `προείρηκεν` ("said before/predicted") → CUV `先前說過`.
- **No particle at all — stative verbs are the systematic exception.** Every sampled
  instance of the "know" family (οἶδα/οἴδαμεν/οἴδατε) — John 4:25, 7:27, 13:17-18,
  20:2 — rendered as bare `知道` with no `了`/`過` at all, in both editions, every time.
  Stative verbs describing an ongoing state of knowledge do not take an aspect
  particle the way telic/punctual events do.
- **`過` is not obligatory even for negated perfects** — a real correction to an
  over-generalization risk: John 5:37's negated perfects `ἀκηκόατε`/`ἑωράκατε` ("you
  have never heard... never seen") → CUV `從來沒有聽見...也沒有看見`, with **no** `過`
  at all, despite matching the same "negated perfect" shape that earlier examples
  (Matt 12:3 `沒有念過嗎`) did take `過` on. Whether `過` appears on a negated perfect
  is real per-instance variation, not a fixed rule — check the specific verb and verse.
- **`著`/`着` (durative)** — CUV consistently uses the variant character `着` (not
  `著`); BOCCB2023T consistently uses the standard form `著` — an orthographic
  difference between the two editions' printing conventions, not a grammatical one.
  Confirmed present in both editions' whole-NT counts (CUV: 1,212 instances of `着`;
  BOCCB2023T: 802 instances of `著`).

---

## LIGHT VERB / RESULTATIVE-DIRECTIONAL COMPOUNDS **[zht]**

Chinese verb compounds routinely fuse a main verb with a resultative or directional
complement into what surfaces as a single multi-character word, where Greek expresses
the same event with one plain verb. Treat the head morpheme as primary and the
result/direction morpheme as secondary to the same Greek verb, unless the compound is
itself a lexicalized idiom.

Confirmed repeatedly across samples pulled for other sections: Acts 16:24 (jailer
action) → CUV `把他們下在內監裏` uses a directional `下` ("put down/into"); Acts 18:16
→ `攆出` ("drive-out"); Acts 21:35 (soldiers) → `抬起來` ("lift-up"); Matt 1:21 →
`救出來` ("save-out"). All show the same primary-head + secondary-directional-
complement pattern.

---

## PRO-DROP / TOPIC CONTINUITY **[zht]**

Like Indonesian, Mandarin subject-pronoun use is discourse-driven, not
grammar-driven — visible throughout every sample pulled for this document. A pronoun
tends to be supplied when a clause introduces or re-establishes a subject/topic, and
dropped when a coordinate clause continues the same topic. Example: Acts 4:5's `ἦσαν
ὁμοθυμαδὸν ἅπαντες ἐν τῇ Στοᾷ Σολομῶντος` → CUV `他們都同心合意地在所羅門的廊下` (subject
supplied once, continuing from the prior clause's established topic); many verses in
the samples above show zero explicit subject pronoun at all across several coordinated
clauses. This document does not have a precise rate for this pass — the earlier
(retracted) 76%-no-pronoun figure came from alignment data and should be treated as an
unconfirmed estimate, not a settled number, though the qualitative pattern is solid.

---

## LOCATIVE POSTPOSITIONS (裏/上/中/內) **[zht]**

Mandarin places location words *after* the noun they modify (postpositional), unlike
Greek's prepositions. Confirmed throughout every sample: Acts 22:24 `ἐπὶ τὰς σκάλας`
("to the barracks/steps") → CUV `到了臺階上`; Mark 1:5 `ἐν τῷ Ἰορδάνῃ ποταμῷ` → `在約旦
河裏`. **Orthographic note**: CUV consistently uses the variant character `裏` (not
`裡`); BOCCB2023T consistently uses the standard form `裡` — matching the same
着/著 pattern noted under ASPECT PARTICLES, a printing-convention difference between
editions, not a grammatical one. Each locative has its own dominant sense (containment
`裏`/`裡`, surface `上`, "amid/among" `中`) — not interchangeable defaults, though this
rebuild did not have the volume to re-derive precise preposition-pairing rates without
alignment data.

---

## CLASSIFIERS / MEASURE WORDS **[zht]**

Greek has no classifier system at all, so every Mandarin numeral+classifier+noun
sequence is one Greek numeral/quantifier word rendered as three Chinese words, with the
classifier secondary to the counted noun, sharing its record. Confirmed in the original
sample: Matt 1:21 `υἱὸν` ("a son") → CUV `一個兒子` (`個` secondary); Matt 2:6
`ἡγούμενος` ("ruler") → CUV `一位君王` (`位` secondary, selected for a person of
status — the classifier choice itself carries no independent translatable content, but
its *selection* is noun-class-sensitive).

---

## TEMPORAL 的時候 **[zht]**

A temporal preposition phrase (ἐν/ἐπί/ἐφ᾽) is regularly rendered as `...的時候` ("the
time when..."), with both `的` and `時候` secondary to the governing preposition.
Example: Matt 1:11 `ἐπὶ τῆς μετοικεσίας Βαβυλῶνος` ("at the deportation of Babylon") →
CUV `百姓被遷到巴比倫的時候` (note: this example also shows a genuine `被`-marked
passive — `被遷到`, "were moved to" — inside the same clause, a useful reminder that
`被` does occur, just not as the default). Example: Matt 6:29 `ἐν πάσῃ τῇ δόξῃ αὐτοῦ`
("in all his glory") → CUV `他極榮華的時候`.

---

## Open questions for the next review pass

- **Precise rates for several sections** — this rebuild replaced alignment-derived
  percentages with verse-sample-based qualitative findings (12–25 verses per
  construction). The *direction* of every finding (unmarked-majority for passives,
  bare-default for articles, narrow-conditioning for reflexive `自己`, etc.) is
  consistent with the earlier alignment-based pass, but exact percentages should not be
  trusted from either pass until independently re-verified — the earlier pass's numbers
  came from data sources now known to be unreliable (CUVMPS's validity as a CUV stand-in
  is unresolved; CU2010T's alignment undercounts particles systematically), and this
  pass's numbers are unconditioned whole-corpus counts, not per-construction rates.
- **BA-construction disambiguation** — `將` is polysemous (disposal marker vs. "about
  to" adverb vs. part of the fixed noun `將來`). Any future automated frequency check
  needs to filter for the syntactic pattern (fronted definite NP + verb), not just the
  bare character.
- **`為...所`/`所...的` passive construction** — newly surfaced in this pass, only 2
  instances observed (both in the same verse, 1 Cor 4:9). Needs a dedicated,
  larger-sample check before its relative frequency against `被`/`受`-construction/
  unmarked can be estimated.
- **`著`/`着` and `裡`/`裏` orthographic variants** — CUV consistently uses the older
  variant forms (`着`, `裏`); BOCCB2023T consistently uses the modern standard forms
  (`著`, `裡`). Worth confirming this holds throughout the whole corpus, not just the
  sampled verses, before hard-coding either form into `zht.py`'s worked examples.
- **Native-speaker/Mandarin-linguist review** — no native-speaker review has happened
  yet for any finding in this document.
