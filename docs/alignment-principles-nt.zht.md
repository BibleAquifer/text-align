# Alignment Principles — Mandarin Chinese, Traditional script (zht), New Testament

**STATUS: Rebuilt from raw text + linguistic reasoning (no gold alignment data used
anywhere), matching the `ind`/`hin`/`arb` methodology. An earlier version of this
document was built from Clear-Bible's CUVMPS/CU2010T alignment JSONs; that version was
retracted by direction — see "Methodology" below for the full account, including a
concrete example of it producing a wrong conclusion. Since the rebuild, six sections
(orthographic variants, BA-construction disambiguation, `為...所` passive, the passive-
voice strategy split, articles, and reflexive `自己`) have been re-verified at
full-corpus scale by programmatically joining SBLGNT's `pos`/`morph`/`lemma` tags to
both target editions' text — see each section's own notes and "Open questions" below
for exact percentages and the (still real) limits of that method. Pro-drop was scaled
to a 40-verse hand-classified sample. Not yet reviewed by a native Mandarin speaker.**

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
**CUVMPS is itself a Simplified-script edition, not Traditional** — a categorical
mismatch with this document's own zht (Traditional) target, on top of which CUVMPS was
also confirmed to differ from our own CUV lexically — a direct check found CUVMPS uses
`神` for "God" in verses where CUV uses `上帝` (the well-documented 神版/上帝版
dual-edition tradition in Chinese Bible publishing), plus an 85.4% verse-level
token-count mismatch between the two TSVs that was never fully explained; and (b) a
second alignment source used for cross-checking, UBS's CU2010T
alignment, was directly confirmed to be unreliable for this purpose — it systematically
leaves grammatical particles unrecorded (98.8% of negation particles showed
"unaligned" despite the Chinese text plainly containing a negator in every sampled
verse) because it was built for a different purpose than word-level alignment
verification. Neither CUVMPS's nor CU2010T's alignment data is used in this rebuild.

**What this means for the claims below**: precision is lower than a real word-level
alignment pass could give — none of the full-corpus counts below are token-level
attributed the way an actual alignment would be, they're verse-level or pattern-level
proxies (e.g. "does this verse contain `被` anywhere" rather than "is `被` linked to
this specific Greek token") — but every example is directly verifiable by re-reading
the cited verse in both editions' raw text, and every full-corpus figure is
re-derivable by anyone with `SBLGNT.tsv` and the two target TSVs. Nothing here depends
on trusting a third party's alignment methodology or completeness. Several sections
(see STATUS above) have since moved beyond the original 12–25-verse spot-check stage to
full-corpus or large-sample counts using this same non-alignment-based method — those
sections' own text states exactly what was counted and how, and flags where a
correction method's assumptions (not just its sample size) are the remaining source of
uncertainty.

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
BOCCB2023T), then **upgraded to a full-corpus estimate**: the overwhelming majority
have **no target correspondent at all** — the noun stands bare.

**Full-corpus quantification.** SBLGNT tags 19,795 genuine article tokens (`pos=det`,
lemma `ὁ` — this excludes the separate demonstrative-pronoun lemmas below) across the
NT. Whole-NT `這`/`那` counts: CUV 2,097 + 1,855 = 3,952; BOCCB2023T 1,789 + 1,528 =
3,317. Naively attributing every `這`/`那` instance to an article gives an **upper
bound of 20%** of articles — but `這`/`那` also render genuine Greek demonstrative
pronouns (οὗτος: 1,387 tokens, ἐκεῖνος: 243 tokens = 1,630 total), so subtracting those
first (assuming they render as `這`/`那` at close to 100%, itself unverified) tightens
the upper bound to **11.7% (CUV) / 8.5% (BOCCB2023T)**.

That upper bound is itself still too high: a control check on the 851 CUV verses (856
BOCCB2023T) containing **neither** an article **nor** a demonstrative pronoun in the
Greek source found `這`/`那` still present in ~18–20% of them (173 / 183 character
instances) — i.e. a real rate of *idiomatic, non-triggered* `這`/`那` supply (temporal
idioms like `那時候`, discourse-organizing `這樣`, etc., with no Greek article or
demonstrative pronoun behind them at all). Extrapolating that same idiomatic base rate
across the whole corpus and subtracting it from the upper-bound figure pushes the
article-driven estimate down to **roughly 3–4% for CUV**, and for BOCCB2023T the same
arithmetic goes slightly negative — a sign the assumption chain (demonstrative pronouns
render at ~100%; idiomatic rate is uniform across verse types) is too aggressive to
trust as a precise point estimate, not that the true rate is literally zero or negative.

**Conclusion**: treat "demonstrative rendering of a bare article" as a real but small
single-digit-percent minority phenomenon — meaningfully smaller than the original
20-verse spot-check's already-cautious framing suggested, and well below the naive
20%/11.7% upper bounds a bare `這`/`那` count would imply. This is the best full-corpus
estimate obtainable without alignment data (which would allow exact token-level
attribution); the negative BOCCB2023T result flags that the correction method's
assumptions, not the underlying claim, are the remaining weak point.

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

**Disambiguation, upgraded to a full-corpus token-level check.** The earlier 15-verse
character-search pass found `將` genuinely polysemous — 2 of 15 hits were an "about to"
adverb or part of the fixed noun `將來`, not the disposal construction — and left the
true rate "an overcount by an unquantified margin." Re-run at full-corpus scale using
the target TSV's own word-tokenization (not a bare character search) resolves most of
that margin directly: the tokenizer already segments `將`/`把` as their own token only
when they function as the free grammatical marker, keeping the adverbial/lexicalized
uses (`將要`, `將來`, `將到`, `必將`, `將近`, `把手`, `火把`, `把柄`, `一把`/`兩把`,
`把守`, `把握`, …) fused into their own separate compound tokens. Counting only the
standalone single-character token:

| | CUV standalone `將` | CUV standalone `把` | BOCCB2023T standalone `將` | BOCCB2023T standalone `把` |
|---|---|---|---|---|
| count | 308 | 561 | 277 | 752 |

A cheap but effective proxy for "is this really disposal" is what token immediately
follows: disposal requires a definite NP (pronoun/proper noun/demonstrative/common
noun), not a bare verb. Checked across the full token set: **`把` is essentially clean
in both editions** — CUV's `把` is followed by a pronoun/noun-initial token in the
overwhelming majority of its 561 instances (top followers: `他` 81, `他們` 29, `耶穌`
26, `我` 24, `那` 21…), and BOCCB2023T's `把` (752 instances) shows the same shape with
only ~7 verb-initial followers (`在`/`被`/`悔改`/`勸`, ≈0.9%). CUV's standalone `將`
(308 instances) is similarly clean — only ~7 verb-initial followers (`稱為`, `被`,
`有`×5, ≈2.3%) once the fused adverbial/noun forms are already excluded by
tokenization.

**A genuinely new finding, only visible at this scale**: BOCCB2023T's standalone `將`
(not `把`) has a real, systematic minority pattern that is *not* disposal —
`將`+`被`+verb, a future-tense/prospective adverb fronting an explicit passive clause
("will be [verb]ed"), confirmed by direct reading of all 27 instances (≈9.7% of
BOCCB2023T's 277 standalone `將`): Matt 9:15 `將被帶走` ("will be taken away"), Matt
10:17 `將被送上法庭` ("will be brought before courts"), Matt 24:40 `一個將被接去，一個
將被撇下` ("one will be taken, one will be left"), Matt 17:22/20:18 `人子將被交在人手中`
/`將被交給祭司長` ("the Son of Man will be delivered up"). CUV shows almost none of this
(1 `將被` instance across its whole standalone-`將` set) — a genuine cross-edition
difference in how the two translations mark future passive voice, not sampling noise.
**Guidance**: when scanning `將` (not `把`) for disposal-construction candidates, first
check whether it is immediately followed by `被` — if so, it is the future-passive
adverb, not disposal, and the record should instead treat `將` as secondary to the verb
it modifies (aspect/tense marking), with `被` handled under PASSIVE VOICE below.

Genuine disposal-construction examples, spanning Matthew, Acts, and Revelation:

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
pronoun), then **upgraded to a full-corpus check** using SBLGNT's lemma tags: genuine
Greek reflexive pronouns (ἑαυτοῦ 823 + σεαυτοῦ 43 + ἐμαυτοῦ 37 = 903 tokens) vs. plain
αὐτός (4,982 tokens), each joined to CUV/BOCCB2023T verse text, plus a zero-trigger
control population (verses with neither) to measure the baseline idiomatic rate of
`自己`.

**Full-corpus results** (percentage of verses containing `自己` anywhere):

| Population | CUV | BOCCB2023T |
|---|---|---|
| Contains a genuine reflexive pronoun (n≈819) | 27.0% | 20.9% |
| Contains plain `αὐτός`, no reflexive (n≈3,140) | 5.5% | 5.5% |
| Contains neither (control/baseline, n≈3,976) | 2.4% | 3.2% |

**Two findings, one confirming the earlier spot-check and one genuinely new.**

*New*: even a genuine Greek reflexive pronoun renders as `自己` only a **minority of
the time** — 27.0%/20.9%, not a near-default. Reading a 20-verse sample of the CUV
majority that does *not* get `自己` shows this isn't a rendering failure — it splits
into a small reciprocal-construction branch (`彼此` "each other" / `自相` "mutually," a
combined ~6.6% of the no-`自己` cases — e.g. Acts 15:39's mutual sharp disagreement, or
a `ἐφ᾽ ἑαυτὴν` "against itself" rendered `自相紛爭`) and a much larger plain-pronoun/
no-marker branch (~93%, the rest) where a reflexive possessive or reflexive object
simply renders as an ordinary pronoun with no distinct reflexivity marking at all —
Mark 6:22's `τοῦ πατρὸς αὐτῆς` ("her own father") → CUV `她父親`, no `自己` needed, is
representative; Chinese frequently doesn't need to mark reflexive possession
explicitly when the antecedent is already the clause's subject and no ambiguity would
result.

*Confirming, now with a real number*: comparing the plain-`αὐτός` population (5.5%)
against the zero-trigger control baseline (2.4%/3.2%) isolates the genuine
reflexive-substitution-for-plain-`αὐτός` effect at roughly **~3.1% (CUV) / ~2.3%
(BOCCB2023T) net above baseline** — small but real, matching the original 15-verse
sample's 1/15 (≈6.7%) finding in order of magnitude and confirming "genuinely narrow,
conditioned on subject-coreference" rather than a general pronoun-rendering strategy.
This directly supersedes the earlier (retracted) draft's ~49%/~32% split, which came
from unreliable alignment data and should no longer be cited even as a rough estimate.

---

## PASSIVE VOICE **[zht]**

Spot-checked against 25 randomly sampled Greek passive-stem verbs (aorist/present/
perfect passive across Matthew, Mark, Luke, John, Acts, Romans, 1–2 Corinthians,
Galatians, Hebrews, 1 Peter, 2 Peter, Revelation), cross-checked against BOCCB2023T,
then **upgraded to a full-corpus check**: every SBLGNT verb token tagged with passive
voice (any tense/mood — Robinson morph code `V-_P_`, 2,012 tokens across 1,662 distinct
NT verses) was matched to its CUV/BOCCB2023T verse text and scanned for `被` and the
`為...所` pattern (see BA/JIANG section above for the exact regex), giving a clean,
exhaustive count for those two strategies; a 35-verse random resample of the verses
containing *neither* marker was then hand-read to separate genuine
receive-construction (`受`/`得`/`蒙`) hits from `得`'s heavy noise as an ordinary
verb-complement particle (e.g. `害怕得很` "very afraid" has nothing to do with passive
marking).

**Full-corpus results** (percentage of the 1,662/1,657 passive-verb verses):

| Strategy | CUV | BOCCB2023T |
|---|---|---|
| `被`-marked (exact count) | 13.7% (227) | 16.9% (280) |
| `為...所`-marked (exact count) | 0.5% (8) | 0.3% (5) |
| receive-construction 受/得/蒙 (corrected via 35-verse resample for `得`-particle noise) | ~9–11% | ~10–11% |
| **unmarked / restructured active (remainder, clear majority)** | **~75–77%** | **~72–75%** |

Confirming the direction of the original spot-check with real full-corpus numbers: the
Greek passive verb is most often rendered with a plain Chinese verb carrying no passive
morphology, or the whole clause is restructured as active voice. Examples: Acts 22:28
`γεγέννημαι` ("I have been born [a citizen]") → CUV `我生來就是` (both editions
identical); Rev 11:13 `ἀπεκτάνθησαν` ("were killed") → CUV `因地震而死的` ("died
because of the earthquake" — the agent-demoting passive recast as an intransitive
death-event); Luke 24:47 `κηρυχθῆναι` ("[a message] is to be proclaimed") → CUV
`人要...傳...道` (recast fully active, "people will proclaim..."); 2 Pet 1:3
`δεδωρημένης` ("having been given") → CUV `已將...賜給我們` (recast fully active with
God as subject, using the BA-construction to front the gift); 40027003 `κατακρίνω`
("condemned") → CUV `已經定了罪` (unmarked-active), vs. BOCCB2023T `耶穌被定了罪`
(`被`-marked) — same Greek verb, same verse, genuinely different strategy per edition,
underscoring that this is a real translator choice, not a fixed rule.

**A genuinely new finding from this raw-text pass, now confirmed and scaled to the
full corpus**: a classical/literary passive-marking construction, `為`+agent+`所`+verb
(distinct from `被`), first surfaced from only 2 instances in one verse (1 Cor 4:9):
`ἀγνοούμενοι` ("unknown") → CUV `不為人所知` ("not known by people"); the parallel
clause `ἐπιγινωσκόμενοι` ("well known") → CUV `人所共知的` ("commonly known by
people"). A full-corpus pattern search (`為` not preceded by `因` — excludes the
unrelated conjunction `因為` "because" — followed within a few characters by `所` not
immediately followed by `以` — excludes `所以` "therefore") finds this construction is
**far more than a 1-verse curiosity**: ~27 genuine instances in CUV's NT and ~18 in
BOCCB2023T's, after manually excluding several systematic false-positive categories
that share the same character sequence but are unrelated constructions — `以為X`
("think/consider X," not agent-marking `為`), `稱為X` ("called/named X," where `所`
belongs to the following word by coincidence, e.g. `稱為所羅門` = "called Solomon"),
`為X為Y` ("call/count X as Y," e.g. `稱他們為義` "count them as righteous"), and `為`
in its ordinary "for/because of/concerning/until" senses with no following passive
clause (`為止` "until," `為所信的福音` "for the faith [one] believes"). Representative
genuine hits: Matt 24:45 `為主人所派` ("appointed by the master"), Rom 1:7 `為上帝所愛`
("beloved of God"), Acts 10:22/10:35 `為猶太通國所稱讚`/`為主所悅納` ("praised by
the whole Jewish nation" / "accepted by the Lord"), 1 Cor 8:3 `為上帝所喜悅` ("known/
approved by God"). This construction did not surface in the earlier alignment-based
draft at all — that pass only searched for `被`/`受`/`得`/`蒙` characters, so
`為...所` instances were silently miscounted as "unmarked." Treat `為`+agent+`所`+verb
as a real, moderately common marked-passive strategy alongside `被` and the
receive-construction below — not rare, just easy to miss without a targeted search.

**`受`/`得`/`蒙` receive-construction** — full-corpus-confirmed as a real, second-tier
minority strategy (~9–11% of all passive-tagged verses, see table above), correcting
both the original 25-verse sample (which found only 1 clear instance and called it
"genuinely rare") and the earlier nine-verse spot-check's opposite over-generalization
from baptism-specific examples. Genuine hits from the 35-verse resample: Matt 26:75-style
`ἐβαπτίζοντο`/`ἐβαπτίσθη` → `受...洗` (baptism, confirmed in both editions); John 8:33
`πεπλάνησθε` ("you are deceived") → CUV `你們也受了迷惑`; Mark 10:38-39
`βαπτίζομαι`/`βαπτισθῆναι` → CUV `我所受的洗，你們能受嗎`; Luke 16:25's
`ὀδυνᾶσαι`/`παρακαλεῖται` in the same verse → CUV `也受過苦...如今他在這裏得安慰，你倒
受痛苦` (both `受` and `得` in one verse). `得` specifically requires hand-verification
per instance — it is also the ordinary verb-complement particle (`害怕得很` "very
afraid") with no passive sense at all, and that noise is *not* filtered out by a bare
character search.

**`被`** — full-corpus-confirmed as the second most common strategy overall, not rare:
13.7% of CUV's and 16.9% of BOCCB2023T's passive-tagged verses (227 / 280 verses,
exact counts — see table above), correcting the earlier 25-verse sample's "zero CUV
instances, genuinely rare" finding, which was simply too small a sample (25 verb tokens
out of a full-corpus population of 2,012) to land on a representative rate. BOCCB2023T
uses `被` at a moderately higher rate than CUV, consistent with the earlier finding that
BOCCB2023T favors more explicit passive marking generally (see the `將`+`被` future-
passive finding under BA/JIANG above). The two editions still frequently diverge on the
*same* verse (1 Cor 8:5 `λεγόμενοι` "so-called" → BOCCB2023T `被稱為神明的` vs. CUV's
unmarked `稱為神的`; Rom 10:10 `πιστεύεται` "believes/is believed" → BOCCB2023T `被稱為
義人` vs. CUV's active-restructured `心裏相信就可以稱義`) — `被` is common enough to be
a real live option for either editor, but which specific verses get it remains a
per-translator choice, not predictable from the Greek voice morphology alone.

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
  **Full-corpus-verified, categorical, zero exceptions**: whole-NT counts show CUV uses
  `着` 1,212 times and `著` 0 times; BOCCB2023T uses `著` 802 times and `着` 0 times.

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
supplied once, continuing from the prior clause's established topic).

**Scaled up to a 40-verse hand-read sample, with an important scope clarification.**
There is no morphological trigger in SBLGNT to filter on directly — pro-drop is about
an *absent* pronoun, not a tagged one — so this used a proxy population instead: NT
verses containing ≥2 finite 3rd-person indicative verb tokens (3,440 such verses,
11,382 verb tokens total), the environment where same-subject coordinate-clause chains
concentrate. A random sample of 40 of these verses was read in full, with every clause
classified as either (a) introducing/re-establishing a subject (a genuine subject
shift, or a return to a topic after an interruption) or (b) continuing the immediately
preceding clause's same subject. Only category (b) — true continuation — is the
pro-drop-relevant case; category (a) is expected to be explicit and consistently was.

**Result, isolating the continuation case specifically**: of 35 clearly-identifiable
same-subject-continuation slots found across the 40-verse sample, **33 (94.3%) dropped
the pronoun entirely**, 1 supplied an explicit pronoun anyway (explainable by an
intervening quoted-speech clause breaking discourse flow — itself closer to a
re-establishment than a pure continuation), and 1 repeated the full noun rather than
using either a pronoun or nothing (Rom 5:12's personified "death," where CUV re-uses
`死` rather than a pronoun — plausibly because Chinese avoids a bare pronoun for an
abstract/non-human referent in that position). Representative examples: Mark 5:38-style
chains with zero subject marking across 4–5 coordinate verbs in one unbroken subject
run (Acts 27:17 `既然把小船拉上來，就用纜索捆綁船底，又恐怕在賽耳底沙灘上擱了淺，就落下
篷來，任船飄去` — five coordinate verb phrases, not one explicit subject pronoun
anywhere, the subject carried entirely by discourse context from the preceding verse);
Mark 1:10-11-style pattern where introduction/re-establishment gets an explicit pronoun
and every subsequent same-subject clause drops it (Mark 10:1 `耶穌...來到猶太的境界...
[他]照常教訓他們` — `起身` and `來到` share `耶穌` stated once with no repeat, then `他`
is explicitly re-supplied only when the clause returns to Jesus after an intervening
different-subject clause about the crowd).

**This is a different, more precise number than the earlier retracted 76% figure** —
that number (from unreliable alignment data, and never independently reproduced) most
likely mixed introduction/re-establishment positions (which are reliably explicit) in
with continuation positions (which this sample shows are dropped at a near-categorical
~94% rate), diluting toward the middle. The two findings aren't necessarily in tension;
they're measuring different populations. Treat **~94% pronoun-drop specifically for
same-subject coordinate continuation** (n=35, one 40-verse sample) as the current best
estimate for that sub-case, and the introduction/re-establishment case as reliably
near-100% explicit — but note this is still one 40-verse sample, not a full-corpus
count, since clause-boundary classification requires reading judgment that doesn't
reduce to a token filter the way the other sections' constructions did.

---

## LOCATIVE POSTPOSITIONS (裏/上/中/內) **[zht]**

Mandarin places location words *after* the noun they modify (postpositional), unlike
Greek's prepositions. Confirmed throughout every sample: Acts 22:24 `ἐπὶ τὰς σκάλας`
("to the barracks/steps") → CUV `到了臺階上`; Mark 1:5 `ἐν τῷ Ἰορδάνῃ ποταμῷ` → `在約旦
河裏`. **Orthographic note, full-corpus-verified, categorical, zero exceptions**: CUV
uses `裏` 1,755 times and `裡` 0 times across the whole NT; BOCCB2023T uses `裡` 1,340
times and `裏` 0 times — matching the same 着/著 pattern under ASPECT PARTICLES, a
printing-convention difference between editions, not a grammatical one. Each locative
has its own dominant sense (containment `裏`/`裡`, surface `上`, "amid/among" `中`) —
not interchangeable defaults, though this rebuild did not have the volume to re-derive
precise preposition-pairing rates without alignment data.

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

- **Pro-drop — upgraded from a 12-verse qualitative note to a 40-verse hand-classified
  sample, but still not a full-corpus count.** No morphological trigger exists to
  filter on (pro-drop is about an *absent* pronoun), so this used a proxy population
  (verses with ≥2 finite 3rd-person indicative verbs, n=3,440) and manual clause-by-
  clause reading rather than a token filter. Result: ~94% (33/35) pronoun-drop rate
  specifically for same-subject coordinate-clause continuation, with
  introduction/re-establishment reliably explicit — a more precise, mechanistically
  scoped number than the earlier retracted 76% figure, which likely mixed both
  populations together. See PRO-DROP / TOPIC CONTINUITY above. Remaining gap: this is
  one 40-verse sample (n=35 continuation slots), not exhaustive, and clause-boundary
  classification requires human reading judgment that resists further automation
  without a real dependency parse.
- **Reflexive `自己` — resolved at full-corpus scale, with a genuinely new finding.**
  Net substitution rate for plain `αὐτός` (controlled against a zero-trigger baseline):
  ~3.1% (CUV) / ~2.3% (BOCCB2023T), confirming "genuinely narrow." New: even a genuine
  Greek reflexive pronoun (ἑαυτοῦ/σεαυτοῦ/ἐμαυτοῦ) renders as `自己` only 27.0%/20.9% of
  the time — most of the rest use a plain pronoun with no distinct reflexivity marker at
  all, not a competing marked strategy. This supersedes the earlier (retracted) draft's
  ~49%/~32% split. See REFLEXIVE 自己 above.
- **Articles — resolved at full-corpus scale, with a caveat on the correction method.**
  19,795 SBLGNT article tokens counted directly; naive `這`/`那` upper bound tightened
  from 20% to 11.7% (CUV) / 8.5% (BOCCB2023T) by subtracting demonstrative-pronoun-
  driven instances, then further corrected for idiomatic non-triggered `這`/`那` supply
  (measured directly from the 851/856 verses with zero article or demonstrative-pronoun
  trigger) down to ~3–4% for CUV. The BOCCB2023T version of the same correction goes
  slightly negative, which is a red flag on the correction method's assumptions
  (100% demonstrative-pronoun rendering rate; uniform idiomatic base rate across verse
  types), not evidence the true rate is zero — a native-speaker or alignment-based
  follow-up would be needed to pin down an exact point estimate rather than this
  bounded range. See ARTICLES above.
- **Passive voice — resolved at full-corpus scale.** Every SBLGNT passive-tagged verb
  token (2,012 tokens / 1,662 verses) matched against both editions' text, with a
  35-verse hand-resample to correct for `得`'s noise as a verb-complement particle. Real
  percentages now replace "roughly 19 of ~30, unquantified": unmarked/restructured-
  active ~75–77% (CUV) / ~72–75% (BOCCB2023T), `被` 13.7%/16.9%, receive-construction
  ~9–11% both editions, `為...所` 0.5%/0.3%. See PASSIVE VOICE above.
- **BA-construction disambiguation — resolved at full-corpus scale.** Token-level
  filtering (standalone `將`/`把` tokens only, excluding fused adverbial/lexicalized
  compounds) plus a next-token NP-check confirms the construction is clean in both
  editions (~1–2% false-positive rate), and surfaced a genuine new pattern —
  BOCCB2023T's `將`+`被`+verb future-passive, absent from CUV. See BA/JIANG DISPOSAL
  CONSTRUCTION above. Remaining gap: the next-token heuristic was not verified against
  every individual instance, only spot-checked for the `將`+`被` subset (all 27 read
  directly) — the ~2% CUV/BOCCB2023T tail flagged as possibly-verb-initial was not
  individually reclassified.
- **`為...所` passive construction — resolved, folded into the full-corpus passive-voice
  pass below.** ~27 genuine CUV / ~18 genuine BOCCB2023T raw pattern-search instances,
  0.5%/0.3% when conditioned specifically on verses containing a Greek passive-tagged
  verb (see PASSIVE VOICE above) — confirming it as real but the smallest of the four
  marked/unmarked strategies, not a fluke.
- **Native-speaker/Mandarin-linguist review** — no native-speaker review has happened
  yet for any finding in this document.
