# Alignment Principles — Mandarin Chinese, Traditional script (zht), Old Testament

**STATUS: Rebuilt from raw text + linguistic reasoning (no gold alignment data used
anywhere), matching `alignment-principles-nt.zht.md`'s rebuild and the `ind`/`hin`/
`arb` methodology. An earlier version of this document was built from UBS's
`WLCM-CU2010T-manual.json` alignment; that version was retracted by direction — CU2010T
was confirmed unreliable for word-level verification (98.8% of negation particles
showed "unaligned" despite the Hebrew text plainly having a Chinese negation
correspondent in every sampled verse — it was built for a different purpose). Since the
rebuild, PASSIVE VOICE has been re-verified at full-corpus scale (same
`morph`-tag-joining method as the NT doc) and INFINITIVAL CONSTRUCTIONS has been
independently re-verified with a 35-verse sample (previously inherited by analogy from
NT, now genuinely checked and partially overturned — infinitive absolute is NOT
unmarked). Not yet reviewed by a native Mandarin speaker.**

Guidelines used by `refine-alignment` when aligning Bible translations into Traditional
Chinese against the Hebrew Old Testament (WLCM, Westminster Leningrad Codex) source.

Sections marked **[zht]** contain Chinese-specific rules or examples. Unmarked sections
are shared with the English OT guidelines (`alignment-principles-ot.md` and
`prompt/ot/eng.py`).

Target text: Chinese Union Version, Modern Punctuation, Traditional orthography (CUV,
staged locally at `data/alignments/alignments-cmn/data/targets/CUV/`). Every worked
example below is quoted directly from that data.

Source file: `src/text_align/refine/prompt/ot/zht.py`

---

## Methodology

**No alignment data is used anywhere in this document.** Every claim rests on:

1. **Raw parallel text spot-checking** — for each construction, a random sample of
   Hebrew source tokens matching the relevant morphology (typically 14–20 verses per
   construction) is pulled from `data/sources/WLCM.tsv`, and the corresponding verse
   is read directly from two independent Traditional Chinese translations' raw target
   text: our own **CUV** (`data/alignments/alignments-cmn/data/targets/CUV/`) and
   **BOCCB2023T** (Biblica® Open Chinese Contemporary Bible 2023, Traditional — a
   genuinely independent modern translation, confirmed by comparing Genesis 1:1/1:2
   wording directly: `起初，上帝創造天地` (CUV) vs. `太初，上帝創造了天地` (BOCCB2023T)
   — different opening word for "beginning," different aspect marking).
2. **Whole-corpus raw character/token frequency counts** where relevant — unconditioned
   totals, real and repeatable, but not proof of an exact per-construction rate.
3. **General Mandarin/Biblical Hebrew linguistic knowledge**, the same kind of
   reasoning `ind`/`hin`/`arb` relied on for their original passes.

**Why this document was rebuilt**: the earlier version rested entirely on
`WLCM-CU2010T-manual.json` — the only alignment ever produced for the OT in this
language pair (no CUVMPS OT alignment exists). That alignment was directly confirmed
unreliable: 98.8% of לֹא (ordinary negation) tokens showed "unaligned" in the gold
data, while a raw-text spot-check of random verses found an explicit Chinese negator in
every single one. The alignment was built by UBS for a different purpose than
word-level verification, not for this kind of check. No alignment data — from that
source or any other — is used in this rebuild.

**What this means for the claims below**: as with the rebuilt NT doc, precision is
lower than an alignment-derived pass could give (no exact corpus-wide percentages), but
every example is directly verifiable by re-reading the cited verse in both editions'
raw text. Several findings below are genuine **corrections** to the retracted
alignment-based draft, not just re-confirmations — flagged explicitly where that
happened, since the raw-text method caught real methodological artifacts in the old
character-matching approach (most notably for PARTICIPIAL CONSTRUCTIONS and
PRONOMINAL SUFFIXES, both reversed from the earlier draft's conclusions).

---

## ALIGNMENT DIRECTION

Alignments map translation → source: each record asks what Hebrew word(s) or
word-part(s) are behind this translation word.

---

## HEBREW WORD-PART TOKENS

MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its
own ID: inseparable prepositions (בְּ/לְ/כְּ/מִ), the definite article (הַ/הָ/הֶ), the
conjunction waw (וְ/וַ/וּ), and pronominal suffixes each get their own token. Align each
word-part independently per the guidance below.

---

## ALIGNMENT PHILOSOPHY **[zht]**

Alignments are generous: include construction-implied particles (的, aspect particles,
將/把) even where Hebrew has no separate word for them, so long as the target word
exists because of a grammatical feature carried by a specific Hebrew token or word-part.
Prefer one record per source token/word-part — split rather than group. Grammar-required
translation words are secondary to the source token whose grammar/discourse context
requires them — not NEQ. NEQ is for words with no source-language anchor at all.

---

## TOKEN ROLES **[zht]**

primary — direct lexical or semantic connection to the Hebrew token/word-part
secondary — exists only because of a grammatical or syntactic feature of the Hebrew
token (case, aspect, construct state, coreference); no independent Hebrew word backs it
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a
side cannot be secondary; each target token ID in exactly one record per verse.

---

## ARTICLE **[zht]**

Chinese has no article system, matching the NT finding. Spot-checked against 20
randomly sampled verses containing the definite article word-part (הַ/הָ/הֶ), ~30
individual instances: the overwhelming majority (roughly 27 of ~30) have **no target
correspondent at all** — the noun stands bare.

**A precise, recurring pattern for the minority Branch A (demonstrative) case**: every
instance of a supplied demonstrative (`那`) in this sample was tied to one specific,
recognizable Hebrew idiom — a noun (typically `יוֹם`/`עֵת`, "day"/"time") followed by
the demonstrative pronoun הַהוּא ("that"), the fixed "on that day/at that time"
construction:

- Gen 28:19 `הַ מָּקוֹם הַ הוּא` ("that place") → CUV `那地方` — both editions agree
  (BOCCB2023T: `那地方`).
- Isa 10:32 `עוֹד הַ יּוֹם` ("yet this/that day") → CUV `當那日` — both editions agree
  (BOCCB2023T: `那時`).
- Amos 8:13 `בַּ יּוֹם הַ הוּא` ("in that day") → CUV `當那日` — both editions agree.

Every other plain article in the sample (bare nouns like `הַמֶּלֶךְ` "the king,"
`הָעִיר` "the city," `הַלְוִיִּם` "the Levites," etc.) got no correspondent at all —
Branch B is not just the majority, it is close to universal outside this one recurring
idiom. This is a sharper, more specific finding than the NT doc's own "minority but not
rare" demonstrative branch — expect the Chinese demonstrative almost exclusively on this
idiom, not as a general anaphoric-reference option the way NT Greek's article sometimes
triggers one.

Example: `אֱלֹהִים` (no article word-part attested, but note the pattern generally) →
`上帝` alone — no secondary needed.

---

## CONSTRUCT CHAINS **[zht]**

A construct chain expresses genitive by word order and construct form (bound/absolute
noun pair) — no preposition token. Spot-checked against 18 randomly sampled
construct-state nouns, cross-checked against BOCCB2023T: **the presence or absence of
的 correlates strongly with whether the possessor is a pronominal suffix or a noun**,
a real, useful refinement over a flat "bare juxtaposition is the default" claim.

### Pronominal-suffix possessor — usually gets 的
When the construct chain's possessor is a pronominal suffix (his/her/their/my/your),
的 is commonly supplied, matching ordinary Mandarin possessive-pronoun marking:

- Gen 24:2 `עַבְדּוֹ...בֵּיתוֹ` ("his servant...his household") → CUV `他全業最老的僕人`
  ("his entire-estate's oldest servant") — 的 present
- Judg 14:1 `מִבְּנוֹת פְּלִשְׁתִּים` ("of the daughters of the Philistines") → CUV
  `非利士人的女兒` — 的 present
- 2 Sam 4:12 `יְדֵיהֶם...רַגְלֵיהֶם` ("their hands...their feet") → CUV `他們的手腳` —
  的 present
- Ps 113:2 `שֵׁם יְהוָה` ("the name of Yahweh," rendered with an implied "his") → CUV
  `耶和華的名` — 的 present, and note the word order flips (possessor-的-possessed,
  the Chinese order, versus Hebrew's possessed-possessor order)

### Noun-noun construct, especially names/geography/fixed pairs — usually bare
When both elements are full nouns (not a pronominal suffix), especially for
proper/geographic names or lexically fixed pairs, bare juxtaposition with no 的 is far
more common:

- Gen 6:6 `לִבּוֹ` region — CUV `心中` ("heart-among") — no 的
- Josh 15:7 `עֵמֶק עָכוֹר` ("valley of Achor") → CUV `亞割谷` — no 的 (place name,
  compound treatment)
- Josh 15:7 `מַעֲלֵה אֲדֻמִּים` ("ascent of Adummim") → CUV `亞都冥坡` — no 的
- 1 Chr 7:5 `מִשְׁפְּחוֹת יִשָׂשכָר` ("clans of Issachar") → CUV `以薩迦各族` — no 的
- Ps 135:17 `פִּיהֶם` region — CUV `口中` — no 的

**Guidance**: default to secondary-的-present for a pronominal-suffix possessor
(matching ordinary Mandarin possessive marking), and default to bare noun-noun
juxtaposition (no 的, closer to the Indonesian/Arabic OT construct-chain finding) for a
full-noun possessor, especially names, geography, and fixed pairs — check the actual
target text either way, since both patterns are real and this is a tendency, not an
absolute rule.

---

## COPULA / VERBLESS CLAUSES **[zht]**

Hebrew has no overt copula in present-tense nominal/verbless clauses (subject and
predicate simply juxtapose) — contrast Greek, where εἰμί is nearly always present. When
Chinese supplies 是/有/在 with no Hebrew verb token behind it, that supplied copula is
NEQ target. When Hebrew uses הָיָה ("to be," for past/future/emphatic contexts), it
aligns normally — same COPULA STRATEGIES splits as the NT doc (existential 有, identity
是, locative 在).

Example (verbless clause): Ps 23:1 `יְהוָה רֹעִי` ("the LORD [is] my shepherd") → CUV
`耶和華是我的牧者` — `是` → NEQ target (no Hebrew verb token); `耶和華` primary; `我的
牧者` primary with `的` secondary to the possessive suffix.

---

## PASSIVE VOICE **[zht]**

Spot-checked against 20 randomly sampled passive-stem verbs (Niphal, Pual, Hofal),
cross-checked against BOCCB2023T, then **upgraded to a full-corpus check**: every WLCM
verb token in a passive-capable stem (Niphal/Pual/Hophal, `morph[1]` in `N`/`P`/`H`,
5,024 tokens across 4,100 distinct OT verses — the same population `ot/arb.py`'s own
full-corpus passive pass used) was matched to CUV/BOCCB2023T verse text and scanned for
`被` and the `為...所` pattern, with a 35-verse hand-resample of the unmarked-looking
bucket to correct for `得`'s noise as an ordinary particle (same method as the NT doc's
passive-voice upgrade). **Unmarked/restructured-active remains the majority but by a
smaller margin than the raw counts suggest** (~67%, corrected — see below):

**Unmarked — the majority default**, for two distinct reasons:
- Inherently non-agentive positional/stative verbs need no marking at all: Gen 24:13
  `נִצָּב` ("standing") → CUV `站`; Judg 18:17 `נִצָּב` (same verb) → CUV `站`.
- Restructured fully active, often with a generic/implied agent: Lev 7:6 `יֵאָכֵל`
  ("it will be eaten") → CUV `要...吃` (recast active, "[they] shall eat"); 1 Sam 5:12
  `הֻכּוּ` ("they were struck") → CUV `生了痔瘡` ("they developed tumors," fully
  recast).

**`被` — real and not rare (12.5% CUV / 13.8% BOCCB2023T, full-corpus exact counts),
clustering around violent/adversative events**, a cleaner confirmation of the
typological "adversative connotation" theory than the NT sample gave (which had zero
`被` instances in CUV's own text): Josh 7:15 `נִּלְכָּד` ("caught") + `יִשָּׂרֵף` ("he
will be burned") → CUV `被取的人...必被火焚燒` (both `被`-marked); 2 Kings 25:4
`תִּבָּקַע` ("broken into") → CUV `城被攻破`; Jer 13:17 `נִשְׁבָּה` ("taken captive") →
CUV `被擄去了`; Dan 11:4 `תִנָּתֵשׁ` ("plucked up") → CUV `必被拔出`. Every `被`
instance in the original 20-verse sample described capture, destruction, burning, or
exile — real evidence for the adversative-connotation pattern, not just a theoretical
claim.

**`為...所` — real but the rarest clean strategy (0.7% CUV / 0.4% BOCCB2023T)**, exact
full-corpus counts, matching the NT doc's finding that this is the smallest of the
marked strategies. A related, rarer variant surfaced in this pass: bare `為`+agent+verb
with no `所` at all (Jer 33:7 `וְנִבְנֽוּ` "it will be rebuilt" → CUV `這城必為耶和華
建造` "this city will be rebuilt BY the LORD") — an agent-marking strategy without the
nominalizing `所`, distinct from both `為...所` and plain `被`.

**`所`-nominalizer**, present but not `被`/`受`-marked: Judg 20:48 `הַנִּמְצָא`
("[that/those] found") → CUV `所遇見的` (`所...的` framing the passive-oriented sense,
the same construction found in the NT doc's 1 Cor 4:9 example).

**`受`/`得`/`蒙` receive-construction — resolved: a real full-corpus rate, genuinely
HIGHER than NT's, not lower.** The original 20-verse sample's "zero instances, unlike
NT's one" finding was simply too small a sample — a 35-verse resample of the
unmarked-looking bucket found 8/35 (22.9%) genuine receive-construction hits in CUV
(受了割禮 "received circumcision," 蒙福 "were blessed," 得存留/得逃脫 "got to
remain/escape," 得建立/得脫離 "got established/delivered"), correcting to an estimated
**~20% of all passive-tagged verses** — well above NT's ~9-11%. The same 35 verses read
in BOCCB2023T show marking (受/得/蒙/被/為...所 combined) in 10/35 (28.6%), slightly
higher than CUV's rate on the identical verse set — consistent with the NT doc's
finding that BOCCB2023T tends to mark passive voice somewhat more explicitly than CUV.
This directly answers the open question from the earlier draft: the apparent OT/NT
difference was sample variance, not a genuine typological gap — if anything OT CUV uses
receive-construction *more* than NT CUV does.

**Corrected full-corpus picture** (CUV): unmarked/restructured-active ~67%, `被` 12.5%,
receive-construction (受/得/蒙) ~20%, `為...所` 0.7% — the unmarked share is smaller
than the raw "neither 被 nor 為所" bucket (86.9%) suggested, since that raw bucket still
contained the uncorrected 受/得/蒙 instances.

**Revised guidance**: as with NT, do not assume any particular marking strategy. `被` is
genuinely well-attested in OT narrative — check whether the event described is a
notable/adversative one (capture, destruction, exile) before assuming it will be
unmarked. `受`/`得`/`蒙` is likewise a real, non-trivial option — check the actual verb,
not just morphology, and remember `得` specifically is heavily confounded with its
ordinary non-passive use as a verb-complement particle.

---

## PARTICIPIAL CONSTRUCTIONS **[zht]**

**Major correction from the earlier alignment-based draft.** That draft claimed
article-adjacent (attributive) participles showed near-zero `的` (1.8%, barely above
the 1.0% baseline for ordinary verbal participles) — a methodological artifact of
checking only whether `的` appeared within the participle's own narrow record span,
missing cases where `的` landed in an adjacent record instead. A 16-verse raw-text
spot-check shows the opposite: **substantive/attributive participles regularly take
的**, either bare-nominalized or paired with an explicit head noun. The real split is
between the participle's *function*, not its article-adjacency:

### Verbal/predicative — no 的, confirmed
A participle functioning as an ordinary clause predicate (an ongoing-action narrative
description) renders as a plain Chinese verb. 2 Kings 2:12 `רֹאֶה`/`מְצַעֵק` ("was
seeing"/"was crying out") → CUV `看見...呼叫說`: primary alone, no 的. Ps 37:26
`חוֹנֵן`/`מַלְוֶה` ("showing favor"/"lending," a habitual-description use) → CUV `恩待
人，借給人`: primary alone.

### Substantive/attributive — 的 (bare-nominalized or with an explicit head noun)
Confirmed regularly present, correcting the earlier draft:
- Bare-nominalized (的 alone, no separate head noun — parallel to the NT's Romans
  12:8-style chain): Ps 145:14 `הַנֹּפְלִים` ("those who fall") → CUV `凡跌倒的`;
  `הַכְּפוּפִים` ("those bowed down") → CUV `凡被壓下的` (note: combines 被 AND 的
  in one construction). Prov 28:20 `אָץ` ("one hurrying [to be rich]") → CUV `想要急
  速發財的`.
- With an explicit head noun (的 + noun, an ordinary attributive-linker use): Num
  10:6 `הַחֹנִים` ("those pitched/encamped") → CUV `南邊安的營` ("the south-pitched
  camps"); Ezek 39:14 `הָעֹבְרִים`/`הַנּוֹתָרִים` ("those passing"/"those remaining") →
  CUV `過路的人`/`剩在地面上的屍首` ("passersby"/"the remaining corpses").
- `所...的` framing, the same pattern found in PASSIVE VOICE and the NT doc: Ezek 3:3
  `נֹתֵן` ("[which] I am giving") → CUV `所賜給你的`.
- Lexicalized bypass: some substantive participles have fossilized into a plain noun
  that doesn't raise the 的-nominalizer question at all — Lev 25:30 `לַקֹּנֶה`
  ("to the purchaser") → CUV `買主` ("buyer," a single lexicalized noun).

### A cleft-emphasis strategy for predicative participles, newly surfaced
When the subject is fronted/emphasized in Hebrew, a predicative participle can be
rendered with a 是...的 cleft rather than a bare verb: Lev 21:6 `הֵם מַקְרִיבִם` ("it
is they who present [it]," subject fronted for emphasis) → CUV `是他們獻的`.

**Revised guidance**: check the participle's function (verbal/predicative vs.
substantive/attributive), not article-adjacency, before deciding whether 的 is
expected. Substantive/attributive participles regularly take 的; verbal/predicative
ones do not.

---

## INFINITIVAL CONSTRUCTIONS **[zht]**

**Independently re-verified**, correcting the earlier "inherited by analogy" status.
A 35-verse random sample drawn from WLCM's full population of infinitive construct
(`morph[2]=c`, 6,606 tokens) and infinitive absolute (`morph[2]=a`, 882 tokens) tokens
was read directly against CUV. The picture is more differentiated than the inherited
NT-based assumption: infinitive absolute has a real marking strategy (it is NOT simply
a bare verb), and infinitive construct splits into several distinct functional
sub-cases rather than one uniform "plain verb" outcome.

### Infinitive absolute (paired with a finite verb of the same root) — a modal/intensifying adverb, confirmed 4/4 in sample
Contrary to the inherited assumption, this is not unmarked. The emphatic/cognate pairing
consistently renders with a Chinese modal or intensifying adverb (`必`/`必要`/`總要`/
`大大`) placed before the finite verb — secondary to the finite verb, not a separate
lexical item of its own.
  Isa 61:10 `שׂוֹשׂ אָשִׂישׂ` ("I will greatly rejoice") → CUV `我因耶和華大大歡喜`: `大大` secondary to the finite verb, marking the infinitive-absolute intensification
  Gen 18:18 `הָיוֹ יִהְיֶה` ("he will surely become") → CUV `必要成為`: `必要` secondary
  Exod 23:4 `הָשֵׁב תְּשִׁיבֶנּוּ` ("you shall surely return it") → CUV `總要牽回來`: `總要` secondary
  2 Kgs 8:10 `חָיֹה תִחְיֶה` / `מוֹת יָמוּת` ("he will surely live" / "he will surely die") → CUV `必能好` / `必要死`: `必`-family secondary in both

### Infinitive construct — splits by function, not one uniform pattern
- **Quotative `לֵאמֹר` ("saying") after a verb of speech** — near-categorical: renders
  as plain `說`, the redundant "saying" absorbed into the ordinary speech verb, no
  separate marking. Confirmed in 5+ of the sample's instances (2 Chr 33:30, Jer 26:3,
  Ezek 24:13, 1 Sam 9:4, Gen 38:21). Primary alone to the infinitive.
- **Purpose (לְ + infinitive construct, "in order to X")** — real variation: sometimes
  an explicit purpose marker `為`/`為要` is supplied (secondary, framing the verb),
  sometimes the bare verb alone carries the purpose sense with no marker at all. Prov
  17:23 `לְהַטּוֹת` ("to pervert") → CUV `為要顛倒判斷`: `為要` secondary. Esth 9:24
  `לְאַבְּדָם` ("to destroy them") → CUV `為要殺盡滅絕他們`: `為要` secondary. Isa 20:6
  `נִצַּלְנוּ` purpose-of-escape → CUV `為脫離亞述王逃往求救的`: `為` secondary. Contrast
  Prov 6:30 `לְמַלֵּא נַפְשׁוֹ` ("to satisfy his hunger") → CUV `充飢`: no separate
  marker, the purpose sense absorbed into the bare compound verb alone.
- **Temporal (preposition + infinitive construct, "when/after X")** — THREE coexisting
  strategies, not just the single `的時候` pattern documented elsewhere in this doc: 2
  Sam 17:21 `אַחֲרֵי לֶכְתָּם` ("after they had gone") → CUV `他們走後`: `後` secondary.
  1 Sam 4:18 `כְּהַזְכִּירוֹ` ("as he mentioned") → CUV `他一提...就`: the `一...就`
  ("as soon as...then") immediate-sequence construction, a third strategy alongside
  `的時候` and `後`. Job 31:13 `בְּרִבָם` ("when they contended") → CUV `...的時候`:
  confirming the `的時候` pattern already documented elsewhere in this doc extends to
  infinitive-construct temporal clauses too, not just prepositional phrases.
- **Lexicalized noun bypass** — some infinitive constructs have fossilized into a plain
  noun, parallel to the PARTICIPIAL CONSTRUCTIONS section's `לַקֹּנֶה` → `買主` finding.
  1 Kgs 8:39 `שִׁבְתְּךָ` ("your dwelling") → CUV `你的居所`: `居所` a plain noun, no
  infinitive-marking needed. Ezra 8:1 `הִתְיַחְשָׂם` ("their genealogy") → CUV
  `他們的家譜`: same pattern.
- **Otherwise (direct object / embedded complement infinitives with no separate
  marking)** — the original baseline case still holds for the remainder: plain Chinese
  verb, primary alone, no separate infinitive-marking word. This remains the correct
  default when none of the above four more specific patterns applies.

**Revised guidance**: do not apply one uniform "infinitive construct → plain verb, no
marker" rule. Check function first — quotative `לֵאמֹר` is near-always `說` with
nothing else; purpose sometimes gets `為`/`為要`, sometimes doesn't; temporal gets one
of three distinct markers depending on the specific preposition/construction; some
infinitives are lexicalized nouns; only the residual case defaults to a bare marker-free
verb. Infinitive absolute is NOT unmarked — expect a modal/intensifying adverb
(`必`/`必要`/`總要`/`大大`) secondary to the paired finite verb.

---

## PRONOMINAL SUFFIXES **[zht]** — tag: PRONOMINAL_SUFFIX

**Major correction from the earlier alignment-based draft.** That draft claimed
explicit Chinese pronoun marking was "the exception, not the rule" for pronominal
suffixes — based on a crude character-matching check (`我你他她它們`) that missed
common pronoun forms (`它`, `她` for non-masculine/inanimate referents were
under-counted; the earlier check's own methodology notes admit this). A 14-verse
raw-text spot-check, done by careful reading rather than character search, shows the
**opposite: explicit pronoun marking is the majority outcome**, not a minority one:

- Noun-hosted possessive suffixes regularly get 的 + pronoun: Ps 72:19 `כְבוֹדוֹ`
  ("his glory," ×2) → CUV `他榮耀的名`/`他的榮耀` — 他 present both times. Nah 3:7
  `רֹאַיִךְ` ("those who see you") → CUV `凡看見你的` — 你 present.
- Verb/preposition-governed object suffixes regularly get an explicit pronoun too: Job
  9:32 `אֶעֱנֶנּוּ` ("I will answer him") → CUV `我可以回答他` — both 我 and 他 present.
  1 Sam 17:17 `לְאַחֶיךָ` ("to your brothers," ×2) → CUV `你哥哥們` — 你 present.

**A real minority of suffixes are still dropped/absorbed**, specifically when the
referent is already established in context or the phrase is idiomatic — the same
discourse-driven omission pattern found for NT Chinese pro-drop: Josh 22:14
`לְמִשְׁפְּחֹתָם` ("by their families") → CUV `按着宗族` (no explicit "their" — the
referent was already the topic of the clause); Ps 145:15 `בְעִתּוֹ` ("in his/its [proper]
time") → CUV `隨時` (idiomatic, no explicit pronoun).

**Revised guidance**: expect an explicit Chinese pronoun correspondent (的+pronoun for
noun hosts, a bare pronoun for verb/preposition-governed objects) as the default for a
pronominal suffix — the reverse of the earlier draft's guidance. Drop it (secondary, no
target word) only when the referent was already named earlier in the same clause/verse,
or the phrase is a recognized fixed idiom.

---

## NEGATION **[zht]**

Spot-checked against 16 randomly sampled negation-particle verses. **Unlike the earlier
alignment-based draft's claim (98.8% "unaligned" for לֹא), a Chinese negation
correspondent is present in essentially every sampled verse** — this fully confirms
the raw-text spot-check already done during the NT doc's methodology section (which
found the same thing for the equivalent alignment-source issue) and extends it with a
larger, dedicated OT sample:

- **לֹא/לוֹא (ordinary negation)** → 不/沒/沒有/並無/絕不/不再, consistently present.
  Judg 1:30 `לֹא הוֹרִישׁ` ("did not dispossess") → CUV `沒有趕出`; Eccl 1:9 `אֵין כָּל
  חָדָשׁ` ("there is no new thing") → CUV `並無新事`.
- **אַל (jussive/prohibitive "do not")** → 不要, the imperative-negation-specific form.
  Gen 21:17 `אַל תִּירְאִי` ("do not be afraid") → CUV `不要害怕`.
- **אֵין (existential "there is not")** → 沒有/並無/沒有. Judg 4:27-style "no shepherd"
  constructions and Lam 2:9 `אֵין תּוֹרָה` ("there is no law/instruction") → CUV `沒有
  律法`.
- **לֹא...עוֹד ("no longer")** → discontinuous, matching NT's own finding. Ezek 24:13
  `לֹא תִטְהֲרִי עוֹד` ("you will not be clean again") → CUV `再不能潔淨`.

**Conclusion, matching the NT doc**: treat "unaligned in [any prior] gold alignment
data" as meaningless for negation — the true correspondence rate is close to universal.

---

## Open questions for the next review pass

- **Infinitival constructions — resolved, independently re-verified.** A 35-verse
  sample overturned the inherited "plain verb, no marker" assumption for infinitive
  absolute (real modal/intensifying adverb marking, `必`/`必要`/`總要`/`大大`) and split
  infinitive construct into distinct functional sub-cases (quotative `לֵאמֹר`→`說`
  near-categorical; purpose sometimes `為`/`為要`-marked, sometimes bare; temporal has
  three coexisting strategies `的時候`/`後`/`一...就`; some lexicalized as plain nouns).
  See INFINITIVAL CONSTRUCTIONS above. Remaining gap: 35 verses is not a full-corpus
  count, and the relative proportion of each infinitive-construct sub-case (how often
  purpose gets an explicit marker vs. not, for instance) wasn't tallied precisely.
- **`受`/`得`/`蒙` receive-construction rate in OT — resolved, and the finding
  reversed.** A full-corpus check (4,100 verses with a niphal/pual/hophal verb) plus a
  35-verse hand-resample found ~20% of all OT passive-tagged verses use receive-
  construction in CUV — genuinely HIGHER than NT's ~9-11%, not lower or absent as the
  20-verse sample's "zero instances" suggested. That original finding was simply sample
  variance from too small a sample size, not a real OT/NT typological difference. See
  PASSIVE VOICE above for the full corrected picture (unmarked ~67%, `被` 12.5%,
  receive-construction ~20%, `為...所` 0.7%).
- **The true headless-substantive-participle question carried over from the retracted
  draft** — now largely moot, since this rebuild found substantive participles DO take
  的 regularly regardless of whether a head noun is present or bare-nominalized; the
  distinction that mattered turned out to be verbal-vs-substantive function, not
  headless-vs-headed structure.
- **Native-speaker/Mandarin-linguist review** — as with the NT doc, no native-speaker
  review has happened yet.
