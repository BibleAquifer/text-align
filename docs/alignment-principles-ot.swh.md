# Alignment Principles — Swahili (swh), Old Testament

**STATUS: Pass 2 draft (Pass 1 plus a second round on the open items; see "Resolved in
Pass 2"). Drafted as `prompt/ot/swh.py` (not yet run). Not reviewed by a native
Swahili speaker.** Built from raw text plus reasoning, with no alignment data of any kind
used. Every finding below is either a corpus-scale count (marked as such, and almost
always a verse-level or whole-OT proxy, never real token-level alignment) or a
hand-read sample of 3-8 verses (marked "sample"). Treat every "default" and "majority"
claim as provisional. Every other from-scratch build in this project has had at least
one reversal between its first and second pass.

Guidelines used by `refine-alignment` when aligning ONEN (Biblica® Open Kiswahili
Contemporary Version, Neno) against the Hebrew/Aramaic Old Testament (MACULA Hebrew /
WLC) source. Shared structural conventions follow `alignment-principles-ot.md` and
`prompt/ot/eng.py`; Swahili-specific morphology follows `alignment-principles-nt.swh.md`
and `prompt/nt/swh.py`, which this document does not repeat. Sections marked **[swh]**
contain Swahili-OT-specific rules or examples. Unmarked sections inherit the shared
OT conventions unchanged.

Source files: `src/text_align/refine/prompt/ot/eng.py`, `src/text_align/refine/prompt/nt/swh.py`

---

## Corpus situation

- **ONEN** (`ot_ONEN.tsv`): 23,258 verses, keyed by the Hebrew `source_verse` ids, so no
  versification remapping is needed for the join. Median length is 1.16 ONEN words per
  Hebrew token (`WLCM`), but ONEN is a **dynamic, contemporary translation**: it
  regularly rewords, merges, or drops material (a dropped `וְאֵת` list item in Esth 9:8;
  Job 34:23 restructured into a negated "have need" clause). Expect real NEQ and
  restructuring, more than in a literal translation.
- **ONMM** (`ot_ONMM.tsv`): same 23,258 verses. **Not an independent translation.** It is
  a revision of ONEN aimed at a different dialect of Swahili: mean verse similarity to
  ONEN is 0.93 and 38.8% of verses are word-for-word identical. Its main systematic
  difference is lexical (the divine name, see below). Use it to separate dialect-specific
  wording from shared grammar. **Agreement between ONEN and ONMM is not independent
  confirmation of any rule.**
- **SRUV06** (`ot_SRUV06.tsv`): 22,606 verses; mean similarity to ONEN 0.44. The only
  genuinely independent Swahili text. **Not openly licensed: consult-only**, never an
  alignment-data source, never quoted at length.
- **No existing OT alignment is used.** (None exists for ONEN's OT in any case; the NT
  alignment was judged unreliable and is also not used.)

Method for this pass: `WLCM.tsv` joined to ONEN, ONMM, and SRUV06 by verse; random samples
per construction read by hand; corpus counts where a construction can be pattern-matched.
`WLCM`'s `morph` and `pos` tags are used to select verses, not as alignment evidence.

---

## Key differences from OT English **[swh]**

- **No articles at all.** The Hebrew article word-part has no Swahili word to align to in
  the ordinary case: secondary to its noun, never NEQ (the same rule as `nt/swh.py`).
- **A finite verb is one unspaced word** fusing subject marker (SM) + tense/aspect (TAM) +
  optional object marker (OM) + root + extensions + final vowel. Hebrew spreads the same
  information across a verb token and a separate pronominal-suffix word-part token.
  Several Hebrew tokens therefore routinely share one Swahili target token.
- **Waw-consecutive is most often a fused narrative tense `-ka-`, not a word, but not
  categorically.** Counted in Pass 2d over 367 verses with a single waw-consecutive verb
  (<=12 tokens): `-ka-` **75%**, plain `-li-` 18%, `-po-` 3%, `-me-` 1%, other 4%. By section:
  law 85% `-ka-`, prophets 89%, history 64% (27% `-li-`, mostly copular `וַיְהִי`), poetry only
  29% (42% `-li-`). See CONJUNCTIONS for the rules. (Whole-OT proxy: 12,303 clean `-ka-` forms
  against 14,978 waw-consecutive tokens; an earlier near-1:1 figure was a regex artifact.)
- **Construct chains take the associative "-a"** (`wa`/`la`/`ya`/`za`/`cha`/`vya`/`pa`/
  `mwa`, agreeing in class with the head noun). Unlike Indonesian or Arabic, the chain
  needs a supplied linker, as English "of" does.
- **Negation is fused into the verb** (`ha-`/`si-`/`-ja-`) or realized by a free word
  (`hakuna`, `wala`, `bila`, `pasipo`). Hebrew has a free particle (`לֹא`/`אַל`/`אֵין`).
- **Existentials and "have"** (`יֵשׁ`, `אֵין`, `לְ`+suffix "have") surface as locative-
  concord forms (`kuna`/`pana`/`mna`/`hakuna`/`lipo`) or `-na` "have" (`hana`, `ana`,
  `anayo`).
- **Hitpael/Niphal reflexive sense is often the reflexive prefix `ji-`** (`hujifanya`,
  `kujificha`), a verb-internal morpheme with no free-standing Hebrew counterpart.
- **The divine name is a single word in ONEN**: יְהוָה → `Bwana` (5,854 occurrences against
  4,905 verses containing the name). ONMM renders it `Mwenyezi Mungu` (two words, 5,797
  occurrences); SRUV06 uses `BWANA`. ONEN's rendering is a plain 1:1; any future ONMM
  config will need its own rule.

---

## ALIGNMENT DIRECTION

Translation → source. Each record asks what Hebrew (or Aramaic) word(s) or word-part(s)
are behind this Swahili word. Same as the shared OT principles.

---

## HEBREW WORD-PART TOKENS

MACULA Hebrew splits prefixed morphemes (waw, inseparable prepositions, the article) and
pronominal suffixes into separate word-part tokens with their own IDs. Swahili's fusion
runs on a different axis: several Hebrew word-parts routinely map onto ONE Swahili
whitespace token. The records below therefore often put several source tokens against a
single target token, with the primary/secondary distinction doing the real work. This is
unrelated to over-grouping: it is the structural norm, the same as OT Arabic and NT
Swahili (the existing `disable_signal_4` scoring override for `swh` is keyed by language
code, so it already applies to OT runs).

### One fused Swahili word = one record
A target token (a whitespace-delimited word) may appear in only **one** record per verse;
`clean-alignments` drops every record that shares a target token with another
(`DUPLICATETARGET`). So when several Hebrew tokens map onto ONE fused Swahili word (waw +
verb + SM + object-suffix + preposition + negator...), put **all** of them in a **single N:1
record**: source = every Hebrew token that word renders, target = that one word.
- **primary:** each source token with its own morpheme or lexical content (the verb root, a
  waw fused as `-ka-`/`-po-`, a negator fused as `ha-`/`-si-`, an object-suffix OM, a
  preposition absorbed into the verb).
- **secondary:** a source token that only supplies grammar (the SM when no explicit Hebrew
  pronoun exists, the article, an infinitive-subject suffix).
- A **separate** record is only for a Swahili word that is a free token of its own (`wala`,
  `Je`, `mimi`, `Kisha`).
Wherever this document says a morpheme is "primary, sharing the verb's word", it means this
single record, not a second record on the same target token. The NT run already behaves this
way: 78% of Greek negators sit in an N:1 record with their verb.

---

## TOKEN ROLES **[swh]**

primary — direct lexical/semantic connection to the Hebrew token.
secondary — exists only because of the Hebrew token's morphology; no separate Hebrew word.

### Subject marker (SM)
No explicit Hebrew pronoun: the SM is **secondary**, in the same record as the verb root
(primary), the ordinary "subject from verb ending" case.
  (Deut 18:17 וַיֹּאמֶר → `akaniambia`: `a-` is the secondary SM; see WAW-CONSECUTIVE for
  the `-ka-` interaction.)
Explicit nominative pronoun (אֲנִי/אַתָּה/הוּא/אֲנַחְנוּ...): when the Swahili renders it as a
free word (`mimi`, `wewe`, `yeye`, `sisi`, `ninyi`, `wao`), it is its own **primary** record to
the pronoun token, and the verb is a separate record. When it renders only as the fused SM
(no free pronoun word), the pronoun token goes **in the verb's single record as primary**
(one fused word; see above), not NEQ and not secondary.

### Object marker (OM)
In Hebrew the object suffix on a verb is a separate word-part token (see PRONOMINAL
SUFFIXES), so the OM is **primary** to that suffix token, in the **same N:1 record** as the
fused verb word, with the verb root also primary. This is simpler than NT Swahili's
OM-doubling rule, which exists because Greek has no suffix token to anchor the OM.
Where Hebrew has an explicit object noun AND Swahili has a discourse-topical OM on the
verb, follow the NT rule: OM secondary to the verb, noun primary.

---

## NEQ (NON-EQUIVALENT) **[swh]**

NEQ = positive claim that no correspondence exists. Never a fallback for uncertainty,
and never used just because a grammaticalized target feature is marked some other way.

- The direct-object marker אֵת/אֶת, almost always untranslated: **NEQ** (standard, per
  `alignment-principles-ot.md` §13.4). In Esth 9:8, ONEN also drops the `וְ` of each
  list item, so the waw is NEQ too.
- The Hebrew article: **secondary to its noun**, not NEQ (see ARTICLES).
- **A supplied copula** in a verbless Hebrew clause (no verb, participle or `הָיָה`): **NEQ
  target, always, and never secondary to the predicate.** This covers `ni`, the emphatic
  `ndiye`/`ndio`, the locative `upo`/`yuko`/`iko`, and the past `ilikuwa`/`lilikuwa`. (The first
  OT review, Pass 3, found the model NEQ'd the copula in Gen 1:2 and Ps 23:4 but marked
  `ni` secondary to `טוֹב` in Gen 1:4; the rule is now stated once with three examples.)
  When a Hebrew verb token IS present (`הָיָה`/`יְהִי`, or a participle), the Swahili word
  rendering it is in that token's record, not NEQ. A repeated copy of the same auxiliary for
  a second predicate of one Hebrew verb (`הָיְתָה תֹהוּ וָבֹהוּ` → `ilikuwa haina umbo, ilikuwa
  tupu`) is secondary to the second predicate's record.
- A Swahili word supplied with no Hebrew anchor (a restructuring connective such as
  `kwa hiyo`, `basi` with no waw behind it): NEQ.
- ONEN is dynamic, so a Hebrew content word that ONEN simply does not render is a real NEQ
  (the same call as any literal translation, just more frequent).

---

## ARTICLES **[swh]**

The Hebrew article (הַ/הָ/הֶ) is a separate word-part token. No Swahili article exists.
**Default: secondary to its noun** (source=[article, noun], target=[noun]; noun primary,
article in `meta.secondary.source`). Never NEQ.

**Check for an explicit Hebrew demonstrative pronoun before crediting a Swahili
demonstrative to the article.** OT Hebrew regularly forms "that/this X" as article + noun +
a real demonstrative token (הַ... הַהוּא, הַ... הַזֶּה). Corpus proxy (verse level, ONEN
demonstratives `huyu/huyo/yule/hawa/hao/wale/hii/hiyo/ile/...` matched by regex):

| Verses | ONEN contains a demonstrative |
|--------|-------------------------------|
| contain an article AND an explicit Hebrew demonstrative (n=1,862) | 86.5% |
| contain an article, no explicit demonstrative (n=9,454) | 40.0% |
| contain neither (n=11,417) | 17.9% |

So most of the raw co-occurrence is the Hebrew demonstrative, as in OT Indonesian. The
Pass-1 residual (40% vs 18%) is mostly an artifact, resolved in Pass 2 with three
controls: verse length (binned by Hebrew token count), a stricter Hebrew-demonstrative
test (also excluding verses with `Pp3` after an article, as in הַהוּא, and glosses
this/that/these/those/here/there/then/today/now), and removing the connective `Kwa hiyo`
("therefore") and `hivyo`, which were being counted as demonstratives. After all three,
verses with no Hebrew demonstrative show 15.5% with zero articles, 22.6% with one, 24.9%
with two, and ~31% with three or more. So the article does drive a Swahili demonstrative,
but only in about **7 verses per 100 per article**, rising with the number of articles.
Reading 10 of the residual verses by hand: 4 are a real anaphoric-article rendering
(`hizo nguzo` Exod 27:10, `huo mwezi` Ezek 45:18, `vile viumbe` Ezek 1:15, `hao wana-kondoo`
Lev 23:20), all on a noun already mentioned. The other 6 are supplied `Kwa hiyo`, `hawa`,
`Huu`, `huko`, with no article behind them.
- Explicit Hebrew demonstrative present: align the Swahili demonstrative **primary** to
  that token. The article stays secondary to the noun.
  (Sample, Job 3:7) הַלַּיְלָה הַהוּא → `Usiku ule`: `ule` primary to הוּא; article secondary
  to `Usiku`.
- No explicit Hebrew demonstrative but a Swahili `huyo/yule/hao/hizo/vile/huo` clearly
  anaphoric (a repeat mention of a noun already in the context): primary to the article
  (Branch A). This is a **small minority** (~7% of verses per article, see above). Do not
  force a demonstrative that is not there, and do not credit `hawa`/`huu`/`huko`/`Kwa hiyo`
  that ONEN supplied with no Hebrew behind them to the article: those are NEQ.
- Anarthrous noun: bare noun, no secondary needed.

---

## CONSTRUCT CHAINS **[swh]**

A construct-state head noun followed by its absolute noun renders with the **associative
"-a"**, agreeing in class with the head: `סִיר רַחְצִי` → `sinia langu la kunawia` (Ps
108:10); `שַׁעַר בֵּית יְהוָה` → `Lango la Juu la Hekalu la Bwana` (2 Chr 27:3, the chain nests:
each link takes its own `-a`); `מֶחְקְרֵי אָרֶץ` → `vilindi vya dunia` (Ps 95:4).
Corpus proxy: 23,511 construct-noun + noun pairs in 12,779 verses against 28,387 associative
words in those verses. The associative also serves non-genitive functions, so the ratio only
shows the two co-occur heavily.

Pass 2e, counted on 171 short verbless verses (<=8 tokens) with exactly one construct
noun + noun pair: **96% contain an associative `-a` word** (law 98%, history 97%, poetry 79%,
prophets 3 of 3). By possessor: 97% when the possessor is a proper name (n=140), 90% for a
common noun (n=31). The 7 verses without one are genealogical lists with the "sons of" dropped
(1 Chr 8:16, 8:25), a restructured clause (1 Chr 1:28 `Abrahamu alikuwa na wana wawili`), or a compound-like
lexicalization (`washauri wangu` for `אַנְשֵׁי עֲצָתִי`, Ps 119:24). The sample is short verses,
skewed to genealogies, so the 96% is an upper bound; poetry's 79% is the better guide for
looser registers.

Rule (same as the NT genitive): the associative "-a" is **secondary**, folded into the
**head (construct) noun's** record. The absolute (possessor) noun gets its own primary
record. The class-concord choice needs no attention.
  source=[סִיר], target=[`sinia`, `la`]: primary `sinia`, secondary `la`; source=[רַחְצִי],
  target=[`kunawia`]: primary.

Exceptions to confirm: possessor pronominal suffixes fuse into the possessive (`langu`,
`yake`), see PRONOMINAL SUFFIXES; and a chain restructured into an adjective or `mwenye`
phrase (e.g. `אִישׁ חֵיִל` → `shujaa`/`mtu mwenye nguvu`) is an ordinary content
correspondence, not a linker case.

---

## INSEPARABLE PREPOSITIONS **[swh]**

Evidence so far is thin (sample only; no corpus count). Observations:
- Hebrew בְּ/לְ/מִן/עַל are word-parts; Swahili renders them as free words (`katika`, `kwa`,
  `juu ya`, `mbele ya`) or as **locative case suffixes** on the noun (`Mkononi` for
  בְּיָד, `moyoni`, `duniani`). The locative `-ni` is a bound morpheme fused into the noun:
  primary to the preposition word-part, in the same N:1 record as the noun.
  (Sample, Ps 95:4) בְּיָדוֹ → `Mkononi mwake` (the `-ni` suffix is the בְּ; `mwake` the suffix).
- A preposition plus a pronominal suffix is typically `na` + pronoun (`nayo`, `naye`) or a
  locative-possessive (`mwake`, `kwake`). See PRONOMINAL SUFFIXES.

---

## CONJUNCTIONS AND PARTICLES **[swh]**

### Waw-consecutive (`וַיִּ...`): renderings (counted)
Counted over the 367 verses (law 161, history 92, prophets 76, poetry 38; ≤12 tokens) whose
only Hebrew verb is one waw-consecutive, classifying the ONEN verse's tense (priority order
`-ka-` > `-po-` > free connective only > `-li-` > `-me-` > `na ku-`):
- **`-ka-` narrative tense: 75%** (law 85%, prophets 89%, history 64%, poetry 29%):
  `וַיֹּאמֶר יְהוָה אֵלַי` → `Bwana akaniambia` (Deut 18:17).
- **Plain `-li-` past: 18%** (history 27%, poetry 42%), with no morpheme of its own for the
  waw. Mostly the copular `וַיְהִי` ("was/came to be": `Eneo la urithi wao lilijumuisha`,
  Josh 19:41; `Neno la Bwana lilinijia`, Jer 2:1) and ordinary past verbs.
- **`-po-` "when": 3%** (`Malkia wa Sheba alipoona`, 2 Chr 9:3), concentrated where MACULA
  itself glosses the waw "when". **Much rarer than a read of the non-`-ka-` residue suggests.**
- **`-me-` 1%; coordinated infinitive `na ku-` ~1%** (1 Kgs 3:16); **a free
  `Kisha`/`Basi`/`Ndipo` with no tense of its own, under 1%** (Esth 4:15).
- **Other ~4%:** the verb restructured away (`hapakuwa na vita`, 1 Kgs 22:1; an infinitive
  `Baada ya Abimeleki kutawala`, Judg 9:22; the copula `ni`, Gen 36:11).
The verse-level counts are a proxy (a verse can carry other tenses), but the pattern is
clear and consistent across sections except poetry.

Rules:
- **`-ka-` and `-po-`:** the waw word-part is **primary** (a real conjunction/subordinator
  morpheme, as Arabic's fused וַ/וְ), in the **single N:1 record** with the verb: source =
  [waw, verb] (plus an object suffix, preposition, etc. if also fused), target = the one
  word; waw and verb root primary, SM secondary.
- **`-li-`/`-me-` with no free connective:** the waw has no morpheme of its own: **NEQ**
  (standard, as asyndeton).
- **Free `Kisha`/`Basi`/`Ndipo`/`na`:** primary to the waw, in its own record (a separate
  Swahili word).
- The `אֵלַי` "to me" suffix in `akaniambia` is in the same word (`-ni-`), see PRONOMINAL
  SUFFIXES.

Hebrew `וַיְהִי` ("and it came to pass") is often dropped or reduced to `Ikawa` (97 forms):
NEQ when absent.

### Waw as a free `na`
`na` covers "and", comitative "with", the passive-agent "by", and "have" (NT rule). In the
OT, plain `וְ` → `na` is the ordinary primary. Disambiguate `na` by syntactic context before
aligning, exactly as in `nt/swh.py`.

### Asyndeton and supplied connectives
Hebrew waw + Swahili asyndeton: waw NEQ (standard). Swahili `Kisha`/`Basi`/`Hata`/`Hapo`
with no waw behind it: NEQ.

### `wala` ("nor/and not")
`וְלֹא` → `wala` (Job 21:13, Prov 6:4): one Swahili word for waw + negator. **One N:1
record**: source = [waw, negator], target = [`wala`], both primary (a target word cannot be
in two records).

### Interrogative `הֲ`/`הַ` (the `Ti` particle)
716 `Ti` tokens (gloss `?`) in 651 verses. In the 595 verses with exactly one, **508 (85.4%)
contain the free word `Je`** (baseline `Je` rate in verses with no `Ti`: 0.5%), and 82% of the
237 `הֲלֹא` ("is it not...?") verses do. `Je` is **primary 1:1** to the `Ti` word-part. Of the
19 short single-`Ti` verses lacking `Je`, the 14 read show four patterns:
- **The question carried by a modal or word order only** (`Waweza kupitisha kamba...`, Job
  40:26; `Unaliona hili, mwanadamu?`, Ezek 8:15): the `Ti` has no word: NEQ.
- **`au` ("or") for the second and later clauses** of an alternative question (Job 38:34,
  39:10; Prov 24:28 `וַהֲ` → `au`): `au` primary to the `Ti` (or to the `אִם`/`אוֹ` that
  follows it).
- **`הֲלֹא` as `si`** (rhetorical "is it not?"), without `Je` (Ps 60:12/108:12 `si ni wewe`,
  Ezek 21:5 `Huyu si huzungumza`): `si` is **primary to both** the `Ti` and the `Tn`, as one
  record with two source tokens.
- **Quoted or embedded question** with a plain complementizer (`Kama`, Job 34:31).
A dropped `Je` (SRUV06 drops it in Ps 77:10; ONEN keeps it) is NEQ.

### `הִנֵּה` ("behold")
1,713 `Tm` ("behold/look/here/there is") tokens in WLCM. ONEN renders it as `Tazama`
(`Tazama, wako hapa`, Isa 41:27), `Sasa` (Jer 49:15), or **drops it** (2 of 5 sampled:
Ps 127:3 and Ps 7:15, where SRUV06 keeps `Tazama` in both; ONMM keeps it in Ezek 7:6 where
ONEN drops it). Present: primary 1:1.
Dropped: **NEQ**.

### `כִּי` and `אִם` (Pass 2d, counted)
MACULA's gloss on the Hebrew word predicts the Swahili connective well. In verses with
exactly one `כִּי` (783, ≤14 tokens), the rate at which ONEN contains each class (classes
can co-occur):

| `כִּי` gloss (n) | most likely ONEN rendering | no connective found |
|---|---|---|
| for (486) | causal `kwa kuwa`/`kwa maana`/`kwa sababu` 57% | 30% |
| that (94) | `kwamba` 41% | 33% |
| because (60) | causal 75% | 12% |
| when (52) | `wakati`/`-po-` 35% | 40% |
| but (22) | `bali`/`lakini` 77% | 18% |
| if (17) | `kama`/`ikiwa`/`-ki-` 65% | 24% |
| indeed (13) | `kama`/`-ki-` 38%, `bali` 23% | 38% |

For `אִם` (197 verses): gloss "if" (128) → conditional 88%; "or" (27) → **no connective 78%**
(an alternative question is carried by `Je` and `au`, not a separate word); "when" (11) →
`wakati`/`-po-` 55%; "though" (7) → concessive `ingawa`/`ijapokuwa` 57%.
Rules: the free connective is **primary** to the Hebrew conjunction; the ~30-40% "no
connective" for `for`/`that`/`when` is a real dropped/fused case (a bare complement after
`Najua`, or a `-po-`/`-ki-` fused subordinator): NEQ when the conjunction is certainly
absent, and **primary in the verb's N:1 record** when the subordination is fused into it
(`-po-`, `-ki-`). Readings were made through the gloss, not by hand; the "no connective"
share is a proxy and includes both real drops and forms the regexes miss.

---

## PRONOMINAL SUFFIXES **[swh]**

Suffixes appear as separate word-part tokens (`Sp*`). Split by host:
- **On a verb (object):** primary, in the same N:1 record as the verb (the OM inside the
  fused word): `תַּהַרְגֵם` → `utawaua` is one record, source = [verb, ם], target =
  [`utawaua`], verb root and `-wa-` OM both primary, SM secondary (Prov 1:32; `תְאַבְּדֵם` →
  `kutawaangamiza`). A Hebrew verb with an explicit object noun AND a suffix does not occur
  (the suffix is the object), so the NT doubling rule rarely applies.
- **On a noun (possessive):** primary, fused into the possessive form (`שִׁבְט וֹ`→ `fimbo
  yake`; `נַעֲלִי` → `kiatu changu`, Ps 108:10). The possessive stem (`-ake`, `-ngu`) is the
  suffix's correspondent. If `fimbo` and `yake` are separate Swahili words, the noun and
  the suffix are separate records; a fused form (one word) is one N:1 record.
- **On a preposition** (11,488 preposition+suffix pairs in WLCM: `לְ` 4,489, `אֶל` 1,633,
  `עַל` 1,556, `בְּ` 1,387, `מִן` 579, `עִם` 535, `אֵת` 459, `אַחַר` 270, `תַּחַת` 160).
  A stratified sample of 27 verses (3 each for 9 prepositions) gives three renderings:
  1. **Free preposition + fused pronominal form, ~14 of 27 (52%)** (`kwako`, `juu yao`,
     `ndani yangu`, `dhidi yangu`, `pamoja naye`/`nami`, `nyuma yako`, `kuliko yeye`,
     `mahali pao`; also `wangu` for `לִי` in `Ole wangu`, Ps 120:5): preposition and suffix
     both **primary**: separate records when they are separate Swahili words (`juu` /
     `yao`), one N:1 record when one fused word renders both.
  2. **Absorbed into the verb, ~7 of 27 (26%)** (`אֵלֶיךָ אֶשְׁמֹרָה` → `ninakutazama`, Ps
     59:10; `בְּךָ בָּטוּחַ` → `anakutumaini`, Isa 26:3; `אֵלַי` → `likanijia`, Ezek 21:13;
     `לִי` → `kinaningojea`, Job 17:1; `אִתְּכֶם` → `sitakuangamiza`, Jer 5:18; `מִמֶּנִּי` →
     `unanikataa`, Ps 88:15; `לָךְ` → `ulitendee`, Job 5:27 with an applicative `-ee` and no
     OM): **one N:1 record** per fused verb word: source = [verb, preposition, suffix],
     target = [the verb word]; the verb root, the **preposition (decided: primary)**, and the
     suffix OM are all primary; the SM is secondary when no explicit pronoun exists. The
     preposition's relation is carried by the applicative `-ia`/`-ea` when present, otherwise
     by the transitive frame itself; either way it is primary, not secondary or NEQ.
  3. **Dropped or restructured, ~6 of 27 (22%)** (Prov 15:4 `בָּהּ`, Job 17:3 `עִמָּךְ`, Ps
     18:37 `תַּחְתָּי`; Lev 21:19 `בּוֹ` → the `-enye` relative `mwenye`; 1 Chr 11:12 `אַחֲרָיו`
     → `Aliyefuata`): NEQ both only when certain, otherwise leave unrecorded. In the `-enye`
     case the `בּוֹ` is primary to `mwenye`.
- **Subject of an infinitive construct** (`בְּהִמֹּלוֹ`, Gen 17:24 "when he was circumcised"):
  ONEN restructures it as a finite clause with its own SM (`alipotahiriwa`); the suffix is
  **secondary** to the verb there (the SM carries the subject), as in OT Arabic.

---

## NEGATION **[swh]**

Hebrew `לֹא`/`אַל`/`אֵין`/`בִּלְתִּי` correspond to several Swahili devices, split by form
rather than by Hebrew word:
- **Fused negative verb** (`ha-`/`si-`/`-ja-`/`-si-` with final-vowel change): the
  negative morpheme is **primary**, in the **same N:1 record** as the verb word (verb root
  also primary), the NT run's actual behaviour (78% of its negators). Same logic as
  `nt/swh.py`'s NEGATION. Examples: `לֹא יָדַע` → `hakufahamu` (Exod 1:8: `ha-`+`-ku-`
  past negation); `לֹא יֵעָנֶה` → `hatajibiwa` (Prov 21:13, negative future); `אַל תִּתֵּן`
  → `Usiruhusu` (Prov 6:4: the jussive/prohibitive `אַל` + yiqtol is the negative
  subjunctive `-si-`); `אַל תְּבַעֲתַנִּי` → `usiendelee kunitia hofu` (Job 9:34).
- **`hakuna`/`hapana`/`hamna`/`hana`** for אֵין/אַיִן (existential negation, "there is no/
  he has no"): see EXISTENTIALS. Example: `אֵין מִשְׁפָּט` → `hakuna haki` (Job 19:7).
- **`bila`/`pasipo`** ("without") for `לֹא`+noun or `בְּלִי`/`בִּלְתִּי` (Job 34:24:
  `לֹא חֵקֶר` → `Bila kuuliza`). Free word, ordinary primary.
- **`sio`/`si`** copular negation for a verbless `לֹא` clause (Ps 115:17 `לֹא הַמֵּתִים` →
  `Sio wafu`). Primary.
- **`wala`** for `וְלֹא` / `גַּם לֹא` ("nor"), see CONJUNCTIONS.

Whole-OT proxy (929 verses with exactly one Hebrew negator and at most 14 tokens; regex
matches of ONEN forms, not alignment): fused `ha-` verb 342, fused `si-` (prohibitive/
subjunctive) 144, `wala` 110, `hakuna`/`hamna`/`hapana` 53, `bila`/`pasipo` 42, `sio`/`si`
39 (forms overlap within a verse). Hebrew negator lemma counts: `לֹא` 5,167, `אַיִן` 785,
`אַל` 731, `לָא` (Aramaic) 82, `בַּל` 73, `בְּלִי` 31.
(Correction, Pass 2c: an earlier draft said 39% of these verses showed no negative form. That
was a regex artifact: the pattern missed `hawezi`, `sitafuti` and similar. With a broader
pattern applied identically to both testaments, **10.9% of OT single-negator verses and 11.6%
of NT ones** lack a recognisable form, so ONEN restructures OT negation no more than NT.)

**Precedent: how the NT run handled locating fused negators.** `nt/swh.py`'s NEGATION block
only instructs the model to "locate the negative morpheme inside the fused verb word" and
align it primary to the Greek negator; the NT doc flagged this as an unverified risk. The
511-chapter ONEN NT run (Gemini 3.7 Flash first pass, 3.1 Pro retry) shows it worked: of
2,642 Greek `οὐ`/`μή` tokens, **2,608 (98.7%) are aligned, 33 (1.2%) NEQ, 1 unrecorded**;
2,558 of the aligned are primary. 2,040 (78%) sit in the same N:1 record as the verb whose
word carries the fused negator, 568 (22%) in their own record. Ten spot-checked non-obvious
cases were correct (`οὐκ ὀλίγαι` → `wengi`, `οὐ μετρίως` → `sana`, a rhetorical `οὐ` →
`Je`). The caveat: this shows the negator was placed in a sensible record, not that every
target-token choice is right. **Apply the same block to the OT**, adding the free-word
cases above (`wala`, `bila`, `hakuna`), rather than inventing a new method.

**Decision (follows the NT precedent exactly):** every negative morpheme, wherever it
surfaces (fused `ha-`/`-ja-`/`-si-`, or a free `wala`/`bila`/`hakuna`/`si`), aligns as its
**primary** link to the Hebrew negator (`לֹא`/`אַל`/`אֵין`/`בַּל`/`בְּלִי`): in the verb's
single N:1 record where the negator is fused, in its own record where it is a free word.
NEQ **only when certain** the translator dropped the negator
or restructured the clause so no negative is left (the NT run's NEQ rate for negators was
1.2%); **otherwise leave it unrecorded**, never as a fallback. No separate OT rule for dropped
negators: the base NEQ rule already covers it.

---

## EXISTENTIALS AND "HAVE" **[swh]**

(Pass 2d: counts plus reading.)
- **`יֵשׁ` "there is"** (Tm tag; 129 verses, 28 short ones read). Classified by ONEN form:
  `-na` "have" 29% (`hana`/`ana`, Prov 13:7), existential `kuna`/`pana`/`mna` 19% (Prov
  11:24, Job 6:30, Job 28:1), locative `-po`/`-ko`/`-mo` 19% (`Iko njia`, Prov 16:25; `lipo
  tumaini`, Job 11:18), other 33%. The "other" read as: restructured (Eccl 6:1 `יֵשׁ רָעָה`
  → `Nimeona ubaya mwingine`), a negative wish (Job 9:33 `לֹא יֵשׁ` → `Laiti angelikuwepo`),
  and **`יֵשׁ` the noun "wealth/substance"** (Prov 8:21 → `utajiri`), so the Tm tag also
  carries a homograph: do **not** align that as an existential. The existential/locative
  form is **primary** to `יֵשׁ`, the class concord part of the same word (a fused `-po`/`-ko`
  is one N:1 record).
- **`אֵין`/`אַיִן` "there is no"** (116 single-occurrence verses): `hakuna`/`hamna`/`hapana`
  types 34%, `bila`/`pasipo`/`wala` 14%, `hana`/`hawana`/`sina` 9%, negative locative
  (`haipo`, `hakuko`) 3%, and **41% with none of these**. Reading 9 of the 41: most are `אֵינָם`/`אֵינֶנּוּ`
  "they are no more / he is gone" rendered as a **verb of disappearance or a negative verb**,
  not a negative existential (`hutoweka` Prov 10:25, `hawatakuwa na chochote` Isa 34:12,
  `hutakuwepo tena` Ezek 27:36, `hawapungukiwi` Ps 34:10, `hawawezi kuokoa` Ps 146:3).
  Primary to `אֵין` in every case where a negative or disappearance word is clearly its
  rendering; the fused `ha-` form is one N:1 record with its verb. This is the main reason
  `אֵין` is not just `hakuna`.
- **`לְ`+suffix "X has Y"** (verbless clauses; only 13 found at ≤11 tokens): `-na` "have" 31%
  (`zina masikio`, Ps 135:17) and **`ni` + possessive pronoun 31%** (`Mpenzi wangu kwangu mimi
  ni...`, Song 1:14; `vya Mungu`, Job 12:13; `ni wangu`, Ps 50:10; `zilikuwa zake`, 1 Kgs 4:10).
  So "have" is not only `-na`: the Pass-1 claim came from one verse. `-na`: the `לְ`+suffix
  pair is a single N:1 primary to the `-na` word. `ni` + possessive: the `לְ`+suffix is
  primary to the possessive pronoun (`wangu`, `vyake`); the copula `ni` is NEQ (a supplied
  copula, as in `nt/swh.py`).
---

## IDIOMS **[swh]**

As in the shared principles: last resort, never for function-word-only records. Hebrew
idioms rendered by a single Swahili lexical item (`בֶּן־...` age idioms, `מִי־יִתֵּן`)
follow the ordinary rule.

---

## PARTICIPLES AND RELATIVES **[swh]**

Swahili has no participle morphology, so Hebrew substantive/attributive participles and
`אֲשֶׁר`/`שֶׁ` relatives funnel into the same relative system as the NT. **Counted (Pass 2d)**
in verses with exactly one `אֲשֶׁר`/`שֶׁ` (552, ≤16 tokens), the rate of each strategy in the ONEN
verse (strategies can co-occur; regex proxy):

| | infixed (`-ye-`/`-o-`/`-lo-`) | `amba-` | `-enye` | `wale`-led | none |
|---|---|---|---|---|---|
| all `Tr` (552) | **56%** | 20% | 10% | 6% | 24% |
| law (181) | 61% | 15% | 9% | 6% | 23% |
| history (120) | 62% | 18% | 9% | 4% | 19% |
| prophets (97) | 54% | 22% | 12% | 9% | 21% |
| poetry (154) | 46% | 25% | 10% | 7% | 31% |

Article + participle (no `אֲשֶׁר`, 128 verses): infixed 45%, none 38%, `wale`-led 16%,
`amba-` 9%, `-enye` 9%. **Unlike the NT, where `amba-` was as common as the infixed
strategy, the OT is clearly infixed-first (about 2.8x `amba-`)**, with `amba-` rising only in
poetry. Whole-OT form counts: `amba-` forms 2,530; `mwenye`-type forms 3,566. The
"none" share is a mix of restructured clauses and forms the regex misses. Strategies seen:
1. **Infixed relative concord** (`ambaye`-less): `-ye-`/`-o-`/`-lo-` inside the verb
   (`wamtumainio`, Ps 125:1; `aliyetukumbuka`, Ps 136:23 for `שֶׁבְּשִׁפְלֵנוּ זָכַר לָנוּ`).
2. **`amba-` + concord** (`ambaye`, `ambao`): Exod 1:8 `אֲשֶׁר לֹא יָדַע` → `ambaye hakufahamu`;
   Ps 83:13 `אֲשֶׁר אָמְרוּ` → `ambao walisema`.
3. **A demonstrative-led relative** (`wale wanaoshikilia`, Ps 31:7; `wale washukao`, Ps
   115:17) for article + participle.
4. **The habitual/gnomic `hu-` tense** (see below): a tense morpheme, not a participle
   strategy. Ps 147:15 `הַשֹּׁלֵחַ אִמְרָתוֹ` → `Hutuma amri yake`; Job 9:7 `הָאֹמֵר לַחֶרֶס` →
   `Husema na jua`.
5. **`-enye` ("having")** and **passive relatives** (`lililowekwa na baba zako`, Prov 22:28
   `אֲשֶׁר עָשׂוּ אֲבֹתֶיךָ`) are the same as in the NT.

Rule (same as NT): the relative concord/word is **primary** to the Hebrew `אֲשֶׁר` or the
article-plus-participle's article; the verb root is **primary** to the participle/verb.
A relative the translator supplied with no Hebrew `אֲשֶׁר` is NEQ or secondary material.

### Habitual/gnomic `hu-` (Pass 2: counted)
2,101 clean `hu-` verb forms in 1,540 ONEN OT verses (excluding the nouns `huruma`,
`hukumu`, `huzuni`, `huduma`, `Hushai`). **55% of those verses are in Proverbs, Psalms and
Job** (845 of 1,540), so it is a wisdom/poetry register marker. Against Hebrew conjugation
in verses with exactly one Hebrew finite/participial verb and one `hu-` form (n=148):
yiqtol 72, participle 35 (only 10 with the article), perfect 30, wayyiqtol 4. As a share of
all single-verb verses of that conjugation: yiqtol ~9.8%, participle ~8.3%, perfect ~3.3%,
wayyiqtol ~0.5%. So `hu-` renders a gnomic/habitual present for **yiqtol or a participle
(with or without the article) or a generic perfect**; it is not specific to articular
participles, which the Pass-1 draft implied.
Rule: `hu-` is a TAM morpheme with no Hebrew word of its own: **secondary** to the verb's
record, never a separate record, never NEQ'd. The Hebrew article before a participle so
rendered is secondary to the participle's record.

---

## INFINITIVAL CONSTRUCTIONS **[swh]**

Swahili has a true infinitive (class 15 `ku-` + stem).
- **Infinitive construct, counted (Pass 2e)** over verses with exactly one infinitive
  construct (<=16 tokens), the share of ONEN verses containing each form (forms co-occur):

  | Hebrew | n | `ku-` infinitive | `ili`/`kusudi` | `-po-`/`wakati`/`-ki-` |
  |---|---|---|---|---|
  | `לְ`+inf | 387 | 72% | 17% | 20% |
  | `לֵאמֹר` | 257 | 37% | 12% | 9% |
  | `בְּ`+inf | 122 | 40% | 3% | **75%** |
  | `כְּ`+inf | 25 | 20% | 4% | 60% |
  | `מִן`+inf | 24 | 83% | 21% | 21% |
  | bare inf | 97 | 65% | 7% | 19% |

  - **`לְ`+inf:** the infinitive root primary, `ku-` **secondary** (the dominant case, 72%).
    24% (94 of 387) show neither `ku-` nor `ili`: the purposive infinitive restructured as a
    **subjunctive** (`wagawanye`, `-e` final vowel, Num 34:29), a `-ki-` participle-like clause
    (`wakitafuta chakula`, Ps 59:16), or a negated finite verb. Align the Swahili verb primary
    to the Hebrew infinitive, the `לְ` secondary, in these cases too.
  - **`לֵאמֹר`** (363 verses, <=20 tokens): the literal `kusema` in only **24%**; 35% have no
    say-form at all in the verse beyond the quote marker, because the preceding speech verb
    (`akaniambia`, `alipoambiwa`) already introduces the quotation. When there is no `kusema`,
    the `לֵאמֹר` is **NEQ** (certain: the quotation frame carries it).
  - **`בְּ`/`כְּ`+inf (temporal):** 75% / 60% `-po-`/`wakati`/`-ki-`: `-po-` or `-ki-` fused
    into the verb makes the `בְּ`/`כְּ` primary in the verb's N:1 record (as for `-ka-`/`-po-`);
    `wakati` is a free word, primary in its own record.
- **Infinitive absolute** (882 tokens). 14 single-infinitive-absolute verses read in Pass 2:
  - 5 an **adverb/intensifier**: `Hakika hamtakufa` (Gen 3:4 `מוֹת תְּמֻתוּן`), `hakika
    nimekujengea` (1 Kgs 8:13), `kwa makini` (Job 21:2), `kasi` (Job 27:22 `בָּרוֹחַ`),
    `kupita kiasi` (Eccl 7:16 `הַרְבֵּה`): primary 1:1 to the infinitive absolute token.
  - 2 the **modal `lazima`** for the emphatic death formula (`מוֹת יוּמָת` → `ni lazima
    auawe`, Lev 24:17, Exod 22:18): `lazima` primary to the infinitive absolute; the verb
    aligns separately.
  - 2 an **infinitive absolute standing as an imperative** (Lev 2:6 `פָּתוֹת`; 2 Kgs 3:16
    `עָשֹׂה` → `Chimbeni`): ordinary primary 1:1 to the main verb; the Swahili is the
    imperative, not an adverb.
  - 5 **not rendered at all** (Lev 13:35, Ps 118:13, Prov 25:27, Lam 3:52, Ps 132:16): the
    infinitive absolute is then secondary to the finite verb when that verb is intact; NEQ
    only when certain it is dropped (an emphasis lost, not a conflation).
  So roughly a third each: intensifier word, unrendered, other (modal/imperative).
  **Pass 2e, at scale:** across 231 single-infinitive-absolute verses (<=20 tokens), an
  intensifier/adverb word (`hakika`, `kabisa`, `kamwe`, `sana`, `lazima`, `kupita kiasi`...)
  appears in 33%. Split by whether the verse has a finite verb of the same root (the cognate
  emphasis, n=138): **46%**; no cognate verb (the imperatival/adverbial use, n=93): **14%**.
  So the intensifier rule belongs to the cognate case; the non-cognate case is mostly an
  ordinary imperative or adverbial verb.

---

## VERBAL STEMS **[swh]**

Pass 2e, counted over single-Hebrew-verb verses (<=12 tokens): the share of ONEN verses
containing each Swahili marker, by Hebrew stem. The Qal row is the baseline (ordinary verbs
also carry these endings); the signal is the excess over it.

| stem | n | `-wa` passive | `-ika`/`-eka` stative | `-ana` reciprocal | `ji-` reflexive | `-isha`/`-esha` causative |
|---|---|---|---|---|---|---|
| Qal (baseline) | 942 | 22% | 6% | 3% | 4% | 8% |
| Niphal | 94 | **40%** | 12% | 10% | 9% | 11% |
| Piel | 260 | 8% | 2% | 1% | 2% | **19%** |
| Pual | 26 | **50%** | 8% | 4% | 8% | 4% |
| Hiphil | 168 | 16% | 6% | 4% | 2% | **17%** |
| Hitpael | 22 | 18% | 5% | **23%** | **41%** | 5% |

(Hophal: under 10 verses, not tabulated. Regex proxy: the endings also occur in ordinary
Qal verbs, hence the baseline; Hitpael is a small sample.)
- **Niphal** (passive/middle): `-wa` passive is the main marker (40% vs 22%), then stative
  `-ika`/`-eka` (`hupatikana`, Prov 16:31) and reciprocal `-ana`. The extension is folded into
  the verb's single record, primary to the Niphal verb.
- **Pual:** the clearest passive stem (`-wa` 50%).
- **Piel (a correction):** Pass 1 said Piel is "usually unmarked". It shows a **causative
  `-isha`/`-esha` 19%** (vs 8% baseline) and *less* passive than Qal; Piel is factitive/
  causative. The extension is folded into the host verb's record; no separate record.
- **Hiphil** (causative): `-isha`/`-esha` 17% (vs 8%), or periphrastic `-fanya` (`ameufanya
  moyo wangu kuzimia`, Job 23:16), or no overt causative (Job 32:15 `yamewaishia`). A reflexive
  `ji-` is rare for Hiphil (2%; Isa 10:31 `wanajificha` is an outlier).
- **Hitpael** (reflexive/middle): **`ji-` 41%** (vs 4%) and **`-ana` reciprocal 23%** (vs 3%)
  (`hujifanya`, Prov 13:7), or no marker (`wafurahie` for `הִתְעַנְּגוּ`, Ps 37:11). `ji-` is a
  bound morpheme inside the verb's record, primary to the Hebrew verb.
Same as NT: align each verb as an ordinary lexical correspondence; the extension is folded
into its host verb's single record, never a separate one.

---

## INTERJECTIONS AND VOCATIVES **[swh]**

(Pass 2d; 331 `Tj` interjection tokens in WLCM; 663 supplied `Ee` in ONEN's OT.)
- **`הוֹי`/`אוֹי` ("woe") → `Ole`**: primary 1:1 (Isa 5:21 `Ole wao walio...`, Isa 18:1 `Ole kwa
  nchi`, Lam 5:16 `Ole wetu`, where `wetu` carries the `לָנוּ` "to us" suffix; Hab 2:12 `Ole
  wake yeye`). A pronoun ONEN supplies to head a substantive adjective (`wao`) is secondary
  to that adjective's record, as for the NT's supplied head noun.
- **`סֶלָה` (Selah, 66 tokens): never rendered**: 0 of the 66 ONEN verses contain `sela`.
  **NEQ**, certain.
- **`Ee` before a vocative (`Ee Bwana`, `Ee Mungu`, `Ee mfalme`)** is supplied; Hebrew
  marks the vocative with no particle. **Follow the NT precedent**: of the NT run's 8 `Ee`
  tokens, 7 sit in the Greek vocative noun's own record (`κύριε` → `Ee Bwana`) and only 1 is
  NEQ. Put `Ee` in the vocative noun's record (target `["Ee", "Bwana"]`, noun primary), not
  NEQ. NEQ only when there is no Hebrew vocative noun to attach it to.
- **`נָא` as `Te` ("now!")** in `אוֹי נָא לָנוּ` is not rendered (Lam 5:16): NEQ. The
  particle `נָא` as `Tj` (72 tokens) was not examined.

---

## DIVINE NAME AND TITLES **[swh]**

`יְהוָה` alone → `Bwana` (ONEN): primary 1:1. **Compounds do not follow the bare-name
mapping** (Pass 2, 3 verses sampled per compound against 253 / 234 / 809 verses):
- `אֲדֹנָי יְהוִה` → `Bwana Mwenyezi` (Ezek 11:21, 30:13): here `Bwana` is `אֲדֹנָי` and
  `Mwenyezi` is `יְהוִה`. Opposite to the bare name. Both primary, each in its own record.
- `יְהוָה צְבָאוֹת` → `Bwana Mwenye Nguvu Zote` (Zech 1:17, Jer 49:7, Mal 2:12): `Bwana` is
  `יְהוָה`; `Mwenye Nguvu Zote` (three words) is `צְבָאוֹת`, all primary to that one token.
- (Pass 2e, **exhaustive** over every verse with the Hebrew title: `אֲדֹנָי יהוה` 291
  verses → `Bwana Mwenyezi` in 95%; `יהוה צְבָאוֹת` 248 → `Bwana Mwenye Nguvu Zote` in 98%;
  `יהוה אֱלֹהֵי…` 820 → `Bwana Mungu`/`Bwana, Mungu` in 70% (`Mungu` in 99%); `שַׁדַּי` 85 →
  `Mwenyezi` in 58%, `Mungu` in 35%; `אֱלֹהֵי צְבָאוֹת` 21 → `Bwana Mungu` 76%; bare `אֲדֹנָי`
  296 → `Bwana` 63%, `Mungu` 14%.) So the three principal mappings below hold at corpus scale,
  not just in 3 verses each; `שַׁדַּי` is the one that varies (`Mwenyezi` or `Mungu`).
- `יְהוָה אֱלֹהֵי ...` → `Bwana, Mungu wa ...` / `Bwana Mungu wenu` (Deut 1:21, 2 Chr
  28:25): `Mungu` primary to `אֱלֹהֵי` (the construct `-a` of `wa` secondary to it, per
  CONSTRUCT CHAINS).
ONMM's `Mwenyezi Mungu` for the bare name is two words, both primary to `יְהוָה`; ONMM's
compounds differ again (`Bwana Mungu Mwenyezi`, `Mwenyezi Mungu, Mungu wa majeshi ya
mbinguni`). A future ONMM config needs its own divine-name section.

---

## ARAMAIC SECTIONS **[swh]**

The Aramaic sections (Daniel 2:4b-7:28; Ezra 4:8-6:18, 7:12-26; Jeremiah 10:11) follow the
same principles, per `alignment-principles-ot.md` §1. Pass 2 sampled 5 Daniel verses:
- The Aramaic emphatic-state article is already a **separate `Td` word-part** in WLCM
  (`מַלְכָּ`+`א`), so the ordinary ARTICLES rule applies (secondary to its noun; 805
  emphatic-state noun tokens). `כֹּלָּא` "all this" → `Haya yote` (Dan 4:25).
- Aramaic `דִּי` is a **real word**, not a bare construct: `הֵיכַל מַלְכוּתָא דִּי בָבֶל` →
  `jumba la kifalme la Babeli` (Dan 4:26). The associative `la` is **primary to `דִּי`**
  (contrast Hebrew construct chains, where it is secondary because no Hebrew word exists).
  `דִּי` as a relative (`מַן דִּי לָא יִפֵּל` → `yeyote ambaye hataanguka`, Dan 3:11) takes the
  relative concord, primary to `דִּי`.
- Aramaic demonstratives and `הֲוָה` (periphrastic past) follow Hebrew practice.
- Ezra and Jeremiah (3 verses): `דִּי` as a relative → `mliyotutumia` (infixed relative, Ezra
  4:18) or `ambayo haikuumba` (`amba-`, Jer 10:11), so both NT relative strategies appear;
  the `Td`/emphatic-state rule and the demonstrative-primary rule hold. Ezra 7:8 is Hebrew,
  not Aramaic.
- **Aramaic verb stems** (Pass 2d; Aramaic verb tokens: Peal 629, Haphel 143, Pael 83, Peil
  62, Ethpeel 33, Aphel/other 24+, Hophal 12). Sampled 4 Haphel, 3 Peil, 2 Ethpeel verses:
  Peil and Ethpeel passives render as the `-wa` passive (`akauawa`, `waliruhusiwa`,
  `ikatolewa`) or restructure to an active (`ili wawaue` for `לְהִתְקְטָלָה`); Haphel
  causatives render as `-wa` passive-causative (`yataondolewa`, `waletwe`) or an ordinary
  verb (`kutoa dhabihu`). All follow the Hebrew-stem rules in VERBAL STEMS: the extension
  is folded into the host verb's record, primary to the Aramaic verb. Hophal/Hithpeel are too
  rare in the sampled sections to say more.
Not yet checked: a larger Ezra sample.

---

## Cross-translation methodology note

This pass used one primary text (ONEN) and two supplements:
- **ONMM** is a dialect revision, not a check (see Corpus situation). Where ONEN and ONMM
  differ, treat the difference as dialect/lexicon unless the grammar visibly changes.
- **SRUV06** is the only independent check and is consult-only. Where it differs from ONEN
  on a Hebrew construction (e.g. `ambaye` vs bare `asiyemjua` for the Exodus 1:8 relative),
  that is evidence of a real strategy split, not an error in either.
- **No alignment data was used.** ONEN has an existing alignment judged sparse and
  statistically derived; nothing in this document depends on it.
- Corpus counts here are **proxies**: regex matches of ONEN word forms against WLCM tag
  counts, joined at verse level. They show co-occurrence, not alignment. Pass 2 showed how
  easily a regex inflates one: the Pass-1 `-ka-` count included 1,494 `wakati` ("time") and
  `mkate` ("bread"), and the article's demonstrative rate included `Kwa hiyo` ("therefore").

---

## Resolved in Pass 2

- **Article residual (was open question 1):** not a 22-point mystery. Controlling for verse
  length, a stricter Hebrew-demonstrative test, and the connective `Kwa hiyo`, the article
  drives a Swahili demonstrative in about 7 verses per 100 per article, always on an
  anaphoric noun. Rule unchanged (secondary default, Branch A only when a demonstrative is
  really there); the evidence is now much firmer than in Pass 1.
- **Waw-consecutive and `-ka-` (reversed):** Pass 1 reported 14,978 tokens vs 14,930 `-ka-`
  forms. That match was an artifact: 1,494 hits were `wakati`, plus `mkate` and names. The
  clean figures are 12,303 forms for 14,978 tokens (0.37 in poetry to 0.74 in prose), with
  four other renderings. The primary-waw rule for `-ka-`/`-po-` stands, but the claim that
  `-ka-` is near-categorical does not.
- **The habitual `hu-` (was open question 4, reframed):** a counted gnomic-TAM morpheme
  (2,101 forms, 55% in Proverbs/Psalms/Job), not a participle strategy. Secondary to the
  verb.
- **Divine titles (was open question 5):** resolved above; the compounds invert the bare
  name's mapping.
- **Infinitive absolute (was open question 6):** 14 verses read; a three-way split, still a
  small sample.
- **`הִנֵּה`/`כִּי`/`אִם` and Aramaic (open questions 8, 9):** sampled. `הִנֵּה` is often
  dropped (NEQ); Aramaic `דִּי` is a real word, unlike a Hebrew construct.
- **Interrogative `הֲ` (Pass 2c, larger sample):** 508 of 595 single-`Ti` verses (85.4%)
  have `Je` (baseline 0.5%); four patterns for the rest, listed above.
- **Preposition + suffix (open question 4, Pass 2c, 27-verse stratified sample):** 52% both
  primary, 26% absorbed into the verb (suffix primary OM, preposition secondary), 22% dropped.
- **Negator locating (open question 2, narrowed):** the NT run located 98.7% of Greek
  negators with the same prompt strategy; the earlier "39% unrecognised" OT figure was a
  regex artifact (true rate 10.9%, NT 11.6%).
- **Fused-word record structure (Pass 2e, a real defect in Pass 2):** several rules put a
  fused morpheme in a second record on the same Swahili word, which the cleaning pass would
  drop (`DUPLICATETARGET`). Fixed with a general "one fused word = one N:1 record" rule and
  corrections to the SM, OM, waw, `wala`, suffix and negation rules.
- **Preposition absorbed into the verb:** now **primary** (decided).
- **Waw-consecutive renderings (Pass 2d, counted, 367 verses):** `-ka-` 75% (law 85, prophets
  89, history 64, poetry 29), `-li-` 18%, `-po-` only 3%. The Pass-2 "five renderings, `-po-`
  common" reading came from the non-`-ka-` residue and overstated `-po-`.
- **`כִּי`/`אִם` (Pass 2d):** the MACULA gloss predicts the Swahili connective; table above.
- **Relatives (Pass 2d):** OT is infixed-first (56% vs `amba-` 20%), unlike the NT.
- **Stems, construct chains, infinitives, divine titles (Pass 2e, counted):** Piel is
  causative (19% `-isha`), not "unmarked"; Hitpael `ji-` 41%; construct chains carry an
  associative in 96% of short verses (poetry 79%); `לְ`+inf is `ku-` 72% with 24%
  restructured; `לֵאמֹר` is `kusema` only 24% (NEQ otherwise); the infinitive absolute's
  intensifier is a cognate-only pattern (46% vs 14%); divine titles confirmed exhaustively.
- **Existentials (Pass 2d):** `יֵשׁ` is ~29% `-na`, 19% `kuna`, 19% locative, 33% other, and
  a homograph noun; `אֵין` is 34% `hakuna`-type with 41% restructured as verbs; `לְ`+suffix
  "have" is `-na` or `ni`+possessive in roughly equal parts.
- **Negators / dropped negators (open question 2, closed):** NT precedent adopted exactly:
  primary when rendered, NEQ only when certain, otherwise unrecorded.
- **Vocative `Ee` and interjections (open question 5, partly closed):** `Ee` goes in the
  vocative noun's record (7 of 8 in the NT run); `Ole` primary; Selah NEQ (0 of 66 rendered).
- **Aramaic stems (open question 6, narrowed):** Peil/Ethpeel → `-wa`, Haphel → `-wa` or an
  ordinary verb, 9 verses, nothing new.
- **ONEN omission (open question 7, narrowed):** a length proxy shows ONEN is about as long
  as SRUV06 (median ratio 0.96); rewording, not wholesale omission. The few verses where ONEN
  is much shorter (1.9%) are probably verse spans (one translation verse covering several
  Hebrew verses, so some Hebrew verses map to little or no text); this is not a problem.
- **Ezra/Jeremiah Aramaic (open question 6, narrowed):** both NT relative strategies appear
  for `דִּי`; the article/demonstrative rules hold.

## Open questions

1. **Waw primary or secondary in `-ka-`/`-po-`.** The rule credits the waw word-part as
   primary (a real conjunction morpheme), parallel to Arabic's fused `وَ`. Greek has no
   equivalent fused token in the NT Swahili doc. Needs native-speaker review; it affects
   most of the 14,978 waw-consecutive tokens.
2. **Negators: closed, following the NT precedent** (see NEGATION: decision). What remains
   is only to confirm on a real OT run that the NT prompt strategy transfers, as the data
   predicts (OT unrecognised-negator rate 10.9% vs NT 11.6%).
3. **`hu-` is secondary to the verb**, a TAM morpheme with no Hebrew word of its own, the
   same treatment the NT gives other fused TAM markers; no reason found to treat it
   differently. Native confirmation still welcome, but not blocking.
4. **Preposition + suffix, absorbed-into-verb pattern** (26% of the sample): **decided:
   the preposition is primary** (owner's call, Pass 2e), in the verb's single N:1 record
   with the suffix OM and the verb root. Native confirmation still welcome.
5. **Poetic parallelism:** not sampled; no Swahili-specific alignment issue found (parallel
   lines are just ordinary clauses). Vocatives and interjections are now covered above
   (`Ee` follows the NT precedent; `Ole` primary; Selah NEQ).
6. **Aramaic:** stems sampled (small: 9 verses); no problem found. A larger Ezra sample and
   Hophal/Hithpeel remain unsampled.
7. **The NEQ baseline for ONEN.** The length proxy (median ONEN/SRUV06 length ratio 0.96;
   2.1-2.3 words per Hebrew content token) shows no sign that ONEN omits much, and the few
   short verses are probably verse spans. Set `neq_baseline` from a real run's measured
   rate, not this proxy.
8. **Scoring:** `_LANGUAGE_SCORING_OVERRIDES["swh"]` sets `disable_signal_4` and is keyed by
   language code, not corpus (checked in `refine/scoring.py`), so it already covers OT runs
   with no code change. Revisit if OT turns up a Hebrew-specific over-grouping problem.
