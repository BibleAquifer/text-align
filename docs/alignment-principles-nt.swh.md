# Alignment Principles — Swahili (swh), New Testament

**STATUS: Stage 2 complete for the questions raised so far.** Started as a
pure grammar-reasoning proposal (stage 1); every section below has since
been checked against real ONEN text — both close individual-verse reading
(~45+ verses, cross-checked against ONMM/SRUV06) and, for the highest-value
phenomena, whole-NT corpus counts (relative-clause strategies, counterfactual
conditionals, superlatives/elatives, reciprocal and causative verbs, the
`-enye` construction, the copula/locative split, the `aliye` state-vs-past
split, the `kuwa`/`kwa kuwa` distinction, recitative ὅτι) — and updated with
confirmed findings, marked as such per section. Several hypotheses from the
original proposal were overturned or substantially revised along the way
(the counterfactual present/past split; comparatives being `kuliko`-alone;
the copula split being complement-type-driven rather than a deep
identity-vs-existence distinction; a suspected plural/1st-person factor in
relative-clause choice that turned out to be one repeated rhetorical
formula) — see "Resolved" / "Still open" near the end for the full list and
the current state. Only one minor, non-blocking item remains open. Not yet
reduced to a `prompt/nt/swh.py` config — a reasonable next step from here.

## Corpus situation

**ONEN is the primary edition and the first translation we align.** ONMM and
SRUV06 are supplements/comparisons, consulted to understand variation, not
alternate primary targets.

- **ONEN** — TSV target text in
  `~/git/Clear-Bible/alignments-swh/data/targets/ONEN/`. Openly licensed.
  **Has an existing alignment**
  (`data/alignments/ONEN/SBLGNT-ONEN-manual.json`), but it is not considered
  reliable enough to build from: it is described as sparse and
  statistically-derived (fast-align-style), not a careful manual alignment —
  the same failure category that sank the first zht and hau drafts (see
  `alignment-principles-nt.hau.md`'s Cross-translation methodology note). The
  sampling below (§ OBJECT MARKING especially) makes this plausible on its
  face — a fused object marker competing with an adjacent free-standing noun
  inside an unspaced Bantu verb word is exactly the kind of thing a
  statistical word-aligner gets wrong. **Plan: raw-text-plus-reasoning
  against ONEN**, the same methodology used for zht and hau, not building
  from the existing alignment.
- **ONMM** — TSV target text in the same repo, no existing alignment data at
  all. Very close to ONEN (visibly a shared base text with independent
  updates — compare the John 3:16 and Matt 1:18 samples below, identical or
  near-identical between the two). Used here as a comparison text. Once ONEN
  has a trustworthy from-scratch alignment, `diff-migrate` is likely viable
  to seed ONMM from it — a later-stage question, noted here for when we get
  there.
- **SRUV06** — available in the same repo, but **not openly licensed** and
  therefore usable only for *consultation* (understanding what a second,
  independent Swahili translation does with a given Greek construction), never
  as a source of alignment data or training material, and never quoted at
  length in committed docs/code. It also has an existing alignment
  (`data/alignments/SRUV06/SBLGNT-SRUV06-manual.json`) described as sparse and
  aimed at key-term/keyword coverage rather than comprehensive token
  alignment — useful the way ONAV's UBS alignment or the retracted zht/hau
  alignments were *not* useful, so plan to treat it with the same skepticism,
  not as ground truth. Already useful below purely as raw comparison text —
  it surfaced a genuine conditional-marking strategy split (§ CONDITIONAL
  CONSTRUCTIONS) that ONEN/ONMM alone would not have shown.

All examples below are drawn directly from `nt_ONEN.tsv` (cross-checked
against `nt_ONMM.tsv`/`nt_SRUV06.tsv`) joined to `SBLGNT.tsv` by verse, not
invented or drawn from memory of Swahili grammar in the abstract — but they
remain spot checks (~25 verses total across all sections), not corpus-scale
verification. Sections marked "confirmed"/"resolved" reflect that sampling;
unmarked sections remain stage-1 hypotheses. **Every frequency claim, every
"X is the default", and every "Y is rare" below is provisional pending
larger-scale verification, even where a section says "confirmed."**

## Key differences from every currently-supported language

- **No articles, same as Indonesian and Hausa** — but Swahili's answer to
  "how is definiteness/specificity marked instead" is different from both:
  primarily through the noun-class concord system's obligatory agreement
  (which itself has no direct English or Greek analogue to align against) and
  through object marking on the verb (see below), not through demonstratives
  doing most of the work the way Indonesian's itu/ini do.
- **A fused subject-marker + tense/aspect + object-marker verbal complex** —
  structurally the same *category* of phenomenon as Hausa's Person-Aspect
  Complex (a single word fuses what English/Greek spread across a pronoun +
  auxiliary + verb), but Swahili's is richer: the subject marker (SM), a
  tense/aspect marker (TAM), an optional object marker (OM), the verb root,
  optional derivational extensions (causative/applicative/passive/stative/
  reciprocal — see below), and the final vowel (FV) all fuse into one
  orthographic word with **no internal spaces at all** — closer to Arabic's
  fusion-by-agglutination-with-no-token-boundary than to Hausa's
  space-preserving preverbal particle. This is the single most
  alignment-relevant fact about Swahili: a single Swahili verb token
  routinely corresponds to what Greek expresses as verb + explicit pronoun +
  explicit object pronoun/noun, all at once.
- **Object marking (OM) can double an explicit object noun — confirmed, and
  resolved against a 14-verse sample (see OBJECT MARKING).** Unlike Hausa/
  English, where a pronoun and its antecedent noun cannot literally co-occur
  in the same clause slot, Swahili regularly marks the object *inside the
  verb* even when the object noun is also present as a separate word
  immediately after it: `aliupenda ulimwengu` ("he-it-loved world" = "he
  loved the world," John 3:16) has `-u-` (class 3 OM, agreeing with
  `ulimwengu`) inside the verb *and* the noun `ulimwengu` right after it. The
  doubling turns out to be **conditioned by discourse topicality/givenness**
  (demonstrative, possessive, or recent anaphoric mention), not simply "an
  accusative noun is present" — a brand-new/indefinite object noun gets no
  OM at all, while an established/pronominal one reliably does. This has no
  clean equivalent in any currently-supported language's principles.
- **The associative "-a" (genitive) linker agrees in noun class with the
  possessed noun**, not the possessor — `wa`, `cha`, `ya`, `la`, `za`... are
  all the *same* morpheme (`-a`) with different noun-class concord prefixes,
  not separate words. This is structurally close to Hausa's fused `-n`/`-r`
  genitive linker, but realized as agreement rather than a single invariant
  suffix.
- **A relative-clause system with at least two coexisting strategies** — an
  infixed relative concord inside a tenseless verb form (`aliye`, `waliomo`,
  `uliye`) and a separate invariable particle `amba-` + ordinary relative
  concord suffix (`ambaye`, `ambao`) — both attested even within a couple of
  the sample verses below, tracking style/register more than any Greek
  distinction. Comparable in spirit to Hausa's nine-way substantive
  participle split or Arabic's three-way split, but built on a different
  mechanism (concord infixation vs. separate word choice).
- **A multi-strategy copula/"be"/"have" system**: `ni` (invariant identity
  copula), `si` (invariant negative identity copula), locative/existential
  `-ko`/`-po`/`-mo` suffixed onto `-wa`/`-li` ("niko" = "I am [here/present]"),
  and `-na` ("have/with") which itself takes subject concord directly like an
  ordinary verb (`wana` = "they have", `hana` = "he/she doesn't have") — at
  least four distinct systems, similar in spirit to Hausa's five-way split but
  with different membership (Swahili's split is identity/negative-identity/
  locative-existential/possessive, not identity/existence/location/future/
  gloss).
- **A single word `na` covers "and", comitative "with", AND the passive
  agent marker "by"** — `akabatizwa na Yahya` ("he-was-baptized na John" =
  "he was baptized by John," Mark 1:9) uses the *same* word Swahili uses for
  "and" and for "together with". No currently-supported language conflates
  the coordinator and the passive-agent marker this severely; this needs an
  explicit rule so the three functions aren't run together in alignment
  decisions.
- **A large, fully productive system of verbal derivational extensions**
  (causative `-isha`/`-esha`, applicative `-ia`/`-ea`, passive `-wa`, stative/
  neuter `-ika`/-eka`, reciprocal `-ana`) stacked between the root and the
  final vowel, all still inside the single fused verb word. Greek's own
  voice/valency system (active/middle/passive, plus some verbal compounds)
  routinely maps onto one of these extensions rather than onto a free-standing
  helper word.
- **Comparison has no synthetic degree morphology at all** (no "-er"/"-est"
  equivalent) and runs through one grammaticalized particle, `kuliko`
  ("than"), following a plain adjective — structurally parallel to Hausa's
  `fi`-based system in that comparison is unified onto one recurring
  morpheme, but `kuliko` is a fixed comparison particle rather than a verb
  taking different syntactic forms.
- **Negation is TAM-conditioned and often circumfixal**, similar in shape to
  Arabic's aspect-conditioned negation-particle choice but realized as
  affixes fused into the verb word rather than free particles: a negative
  subject-marker set (`ha-` + often-irregular person/class forms) combines
  with different post-root or infix negative markers depending on tense —
  perfect negation uses `-ja-` ("not yet" — `hawajakutana`, "they had not
  met," in a context where the positive counterpart would use `-me-`), and
  subjunctive/purpose-clause negation uses an entirely different infix `-si-`
  plus a final-vowel change (`asipotee`, "so that he might not perish," John
  3:16 — contrast positive subjunctive `-e`).

## NOUN CLASSES AND CONCORD — [swh]

Background needed before any other section makes sense, not itself a
direct source of alignment records. Swahili nouns belong to one of ~15-18
noun classes (traditionally numbered, following Bantu comparative practice,
1/2 m-/wa- [humans], 3/4 m-/mi- [plants, misc.], 5/6 ji-/ma-, 7/8 ki-/vi-,
9/10 n-/n- [often zero-marked, largest class], 11 u-, 15 ku- [infinitives],
16/17/18 locatives pa-/ku-/mu-, plus a diminutive/augmentative ki-/vi- and
u- abstract). Every agreeing element in the clause — subject marker, object
marker, adjective concord, associative `-a` linker, relative concord,
demonstrative — takes a class-specific prefix keyed to the noun class of its
controller. This is why `wa`/`cha`/`ya`/`la`/`za` in the examples below all
"mean" the same thing (genitive linker) despite looking unrelated: they are
the same underlying morpheme surfacing with different class agreement.

**Alignment consequence:** none of this concord machinery has an independent
Greek or English token to align to — it rides along on whatever noun/verb it
attaches to. The open question for step 2 is not *whether* concord prefixes
get their own alignment records (they should not — folded into the host
token's own record, the way Arabic's fused proclitics are), but whether any
individual concord-bearing word (adjective, associative particle, relative
form) should be its *own* target token in a multi-word record, or is itself
one atomic token with no internal token boundary to worry about. TSV
tokenization (whitespace-delimited, per `token_ONMM.tsv`/`token_ONEN.tsv`)
determines this mechanically — needs checking in step 2, not assumed.

## ARTICLES AND DEFINITENESS — [swh]

**Corrected after real refined-alignment output surfaced a bug: the default
is SECONDARY, not NEQ.** The original proposal below said the Greek article
"should generally have no direct Swahili correspondent to align to" and
called this "likely the majority NEQ case" — that phrasing made it into
`prompt/nt/swh.py` as an explicit instruction to default the article to NEQ,
and running `score-alignment` against the real ONEN LLM-REFINED output for
Titus 1–3 and 3 John 1 (59 verses, already produced before this was caught)
showed exactly that: 14 of 21 NEQ'd source tokens in Titus 1 alone were
plain articles (`det` POS), and `article_neq` alone was driving 30 of 39
retry flags corpuswide (51% of all verses). This is wrong — "no separate
word for the article" is the ORDINARY case every other supported language
already handles by folding the article into the noun's own record as a
**secondary** source token (English's unmarked article, Hausa's fused-suffix
generalization, etc.) — never NEQ merely because the target language has no
article word. NEQ is for genuine no-correspondence cases (the noun phrase
itself dropped/restructured away), which should be rare, not the ~14% of
all Greek NT tokens that are articles. `prompt/nt/swh.py` has been corrected
to default to secondary; this document is corrected to match, and stands as
a cautionary note about phrasing a "no direct correspondent" hypothesis in
terms that read as license to NEQ rather than the ordinary secondary
treatment.

Swahili has no article morpheme of any kind — no equivalent even to Hausa's
fused `-n`/`-r` suffix or Indonesian's itu/ini defaults. The Greek article
(definite or absent) should generally have no direct Swahili correspondent
to align to, but that means **secondary to the noun**, the same default
every other supported language uses, not NEQ.

Two exceptions worth checking specifically in step 2, both visible in the
sample verses above:
- **Demonstratives** (`huyo`, `hii`, `hivi`) do appear and often track a
  Greek demonstrative or an anaphoric definite article — `naye huyo Neno`
  ("and that/the same Word," John 1:1, ONMM) where Greek has no demonstrative
  at that point (bare καὶ ὁ λόγος), so `huyo` may turn out to be a
  translator-supplied anaphoric marker (parallel to English "the," §6 Case 3
  of the base principles) rather than aligned to any one Greek token — or it
  may track ὁ λόγος's implicit definiteness in a way worth a dedicated rule.
  Needs a real sample of ὁ + noun with and without a following Swahili
  demonstrative.
- **The object-marking system** (see next section) may end up doing real
  alignment work in cases where English uses "the" and Swahili instead
  chooses to (or declines to) cross-reference the object inside the verb —
  worth checking whether OM presence correlates with Greek article presence
  at all, or is fully independent (more likely, since OM in Bantu languages
  is generally conditioned by topicality/animacy/specificity of the referent
  in discourse, not by a Greek article token).

## VERB MORPHOLOGY AND SUBJECT MARKING — [swh]

The Swahili finite verb is built (roughly) SM-TAM-OM-ROOT-EXT-FV, one
orthographic word, no internal spaces. Common TAM markers visible in the
samples: `-li-` (past, `aliupenda` "he loved"), `-na-` (present
progressive/habitual, not sampled above but standard), `-me-` (perfect, not
sampled above but standard — contrast negative `-ja-`), `-ka-` (consecutive/
narrative "and then," `akamtoa` "and-he-gave," `akabatizwa`
"and-he-was-baptized" — very frequent in narrative, likely the default
rendering of Greek narrative καί + finite verb or a participle in a
paratactic chain), `-taka-`/`-ta-` (future, not sampled above), subjunctive
`-e` final vowel with no TAM slot filled (`awe` "may he be," `amwaminiye`
uses the *relative* form of this, see RELATIVE CLAUSES).

**Proposed core rule (parallel to Hausa PAC and to the base English rule for
"subject pronoun from verb ending", §8.1/§8.4):** when Greek marks person
only through verb morphology (i.e., no explicit nominative pronoun), the
Swahili SM is **secondary** to the verb root in one combined record — same
one-record-not-two treatment already used for Hausa. When Greek *has* an
explicit nominative pronoun (ἐγώ, σύ, αὐτός used non-intensively, ὑμεῖς...),
the generous-alignment principle (§2.1) suggests the SM should be **primary**
in its own record against the explicit Greek pronoun — matching the Hausa PAC
rule. This needs checking against real instances in step 2, including
whether Swahili's SM is distinguishable enough from the TAM slot for an
aligner (human or LLM) to reliably identify it as a separate morpheme within
an unspaced word, which is a harder task than Hausa's space-delimited PAC
particle.

**Independent/emphatic pronouns exist and are real tokens** (`mimi`, `wewe`,
`yeye`, `sisi`, `ninyi`, `wao`) — seen in `Mimi niko` ("I am," John 8:58) and
`si juu yangu mimi` (Mark 10:40). These behave like ordinary alignable
pronoun tokens, not fused morphology, and are likely the primary correspondent
for an explicit Greek pronoun when the translator chose emphasis via a
separate word rather than relying on the SM alone — needs a rule
distinguishing this from the SM-primary case above (are both used together,
as in `Mimi niko` where `ni-` [copula "am"] is followed by `-ko`
[locative "here"] AND the independent `Mimi` precedes it — a possible
double-marking case parallel to Hausa's fronted-pronoun/PAC-fallback pattern).

## OBJECT MARKING — [swh]

**Resolved against a 14-verse sample** (John 3:16, Matt 1:18, Mark 1:9, Matt
13:44, Luke 15:22, John 4:10, John 4:15, Mark 6:41, Matt 26:26, Matt 9:2,
John 1:14, Matt 9:6, John 3:3/3:5, Matt 18:8, John 11:25 — ONEN, cross-checked
against ONMM/SRUV06) — enough to propose a confident working rule, though
still short of corpus-scale confirmation. Three clearly distinct patterns
emerged, not two, and the conditioning factor is **discourse
topicality/givenness**, not merely "is there a Greek accusative noun":

1. **OM alone, no separate object token** — the ordinary case for an
   established/anaphoric referent already carried by context: `alipoiona`
   /`akaificha` (Matt 13:44, "when he found it" / "he hid it," referring back
   to `hazina` "treasure" mentioned earlier in the same verse, no repeated
   noun). Structurally identical to a Greek verb's person/number ending
   supplying an implied subject — the OM is **primary** to the Greek
   pronoun/implied-noun token it renders (or NEQ per the base principles'
   "specific noun supplied from context" rule, when nothing renders it on the
   Greek side either).
2. **No OM at all, bare object noun only** — the default for a **newly
   introduced / indefinite** referent: `Leteni... joho` ("bring... a robe,"
   Luke 15:22, brand new, no demonstrative), `akachukua mkate` ("he took
   bread," Matt 26:26, Greek ἄρτον is anarthrous/indefinite too),
   `wakamletea... mtu aliyepooza` ("they brought to him... a paralyzed man,"
   Matt 9:2, the paralytic is new information — note the OM there instead
   marks the *recipient* "him"/Jesus, an already-established discourse
   participant, not the new patient). This is the same pattern as ordinary
   English/Greek indefinite-noun objects — no special rule needed beyond a
   normal primary noun record.
3. **OM doubling an explicit, discourse-topical object noun** —
   `aliupenda ulimwengu` (John 3:16), `akamtoa Mwanawe` (John 3:16),
   `akalinunua lile shamba` (Matt 13:44, note co-occurring demonstrative
   `lile`), `akaumega ile mikate` / `akawapa wanafunzi wake` (Mark 6:41, one
   with a demonstrative, one with a possessive), `akaumega` alone later in
   the same discourse without a demonstrative but still anaphoric to a
   `mkate` mentioned two clauses earlier (Matt 26:26), `alimwambia yule mtu
   aliyepooza` (Matt 9:2, demonstrative `yule` since the man was just
   introduced), `tukauona utukufu wake` (John 1:14, definite via possessive
   `wake`). The unifying factor across all of these is **not** "Greek has an
   accusative noun" (pattern 2 above has that too, with no OM) but that the
   Swahili noun is itself marked (or discourse-established) as definite —
   by a demonstrative, a possessive suffix, or recent anaphoric mention —
   the same semantic space the base principles' article guidelines (§6)
   cover for English "the," just realized through OM-doubling instead of a
   separate article word.

**Proposed rule:** OM is **secondary**, folded into the verb's own record,
whenever it co-occurs with an explicit noun (pattern 3) — parallel to how the
base principles treat a Greek article as secondary to its noun (§6.1 Case 2)
rather than claiming its own record; the noun carries the **primary** link to
the Greek noun. When OM appears with no co-occurring noun (pattern 1), OM
itself is **primary** to the Greek token it renders. This resolves the
"redundancy" concern raised in the original proposal: the OM is not a random
grammatical alternative but a definiteness/topicality marker structurally
analogous to Hausa's fused `-n`/`-r` suffix and to the Greek article itself —
which is exactly why the correlation with demonstratives/possessives/
anaphora, not raw noun-presence, is the right generalization.

**A distinct, higher-confidence sub-case: OM doubling an independent object
pronoun.** When the Greek object is itself a pronoun (αὐτόν, ἐμέ, σε...),
Swahili appears to double it near-categorically, not merely when topical:
`ungelimwomba yeye` ("you would have asked him," John 4:10: OM `-mw-` +
independent `yeye`), `aniaminiye mimi` ("believes in me," John 11:25: OM
`-ni-` + independent `mimi`). This is a cleaner, more automatic pattern than
noun-doubling and should get its own sub-rule: OM **primary** to the Greek
pronoun; independent pronoun **primary** in the same record (a multi-primary
target-token record, §3.6), not secondary — both Swahili elements are
genuine, non-redundant lexical carriers of "him"/"me" in a way the plain
noun-doubling case is not.

**Ditransitive/applicative object competition:** in double-object
constructions (give/tell/divide X to Y), the OM consistently cross-references
the **recipient/beneficiary**, not the theme, even when the theme is the
Greek accusative and the recipient is only dative/genitive:
`akawapa wanafunzi wake` ("he gave [to] his disciples," Mark 6:41 & Matt
26:26: OM `wa-` = disciples-as-recipient; the theme "bread"/`mikate` gets its
own separate record), `akawagawia... samaki` (Mark 6:41: OM `wa-` again
tracks the implied recipients, not `samaki` "fish," which is class 9/10 and
would take a different OM shape if it were the one being cross-referenced).
Needs a purpose-built rule keyed to which Greek argument (dative recipient
vs. accusative theme) the Swahili OM actually tracks — likely: OM secondary
to the verb, tracking the recipient noun's own separate primary record,
independent of which Greek case the recipient carries.

**The `akavibariki` wrinkle is now confirmed, not just a one-off.**
`akavibariki` ("he blessed them" — loaves+fish together) uses OM `vi-`
(class 8) rather than the class-4 `i-` that would agree narrowly with
`mikate` "loaves" alone, and the identical pattern recurs in the parallel
tellings of the same feeding-miracle narrative across three different
Gospels: Matt 14:19, Mark 6:41, and Luke 9:16 all use `akavibariki` for the
conjoined "five loaves and two fish" object. This is genuinely a **default/
"elsewhere" agreement for a conjoined object spanning two different noun
classes** (loaves, class 4; fish, class 9/10), not an error or a fluke of
one verse — confirmed as distinct from *ordinary* class-8 concord by a
control case, Mark 8:7, where `akavibariki` again appears but this time
agreeing with a genuinely singular class-8 noun (`visamaki`, "small fish,"
diminutive-class-8-prefixed on an otherwise class-9/10 root) — the same
surface OM shape, arising from two different grammatical causes. Does not
change the primary/secondary rule above, just confirms which concord shape
to expect when a Swahili verb's object is a conjoined phrase spanning
multiple noun classes.

## GENITIVE / ASSOCIATIVE "-a" — [swh]

The connector `-a` (surfacing as `wa`, `cha`, `ya`, `la`, `za`, `pa`...
depending on the possessed noun's class) is Swahili's all-purpose genitive/
associative linker — `Mwanawe wa pekee` ("his only Son," John 3:16, `wa`
agreeing with class-1 `Mwana`), `ufalme wa mbinguni` ("kingdom of heaven,"
Matt 5:3, class-14 `wa`), `uzima wa milele` ("eternal life," John 3:16).
Functionally this is the direct Swahili analog of Greek's genitive case and
of English's "of" — likely **secondary**, folded into the possessed noun's
record, the same treatment the base principles already give English "of"
when it is case-implied (§8.1, §9.6.1) — with the possessor noun getting a
separate primary record. This is a comparatively low-risk hypothesis (the
mechanism is genuinely a close typological match to genitive case, unlike
e.g. Arabic's construct state needing no linker at all) but the concord
prefix choice itself (which class the `-a` agrees with) needs zero alignment
attention — it is fully mechanical.

## COPULA / "BE" / "HAVE" — [swh]

At least **five** distinct systems, all seen in the sample verses (one more
than the original proposal — the emphatic identificational copula below was
not anticipated going in):

- **`ni`** — invariant identity copula, no subject or tense marking at all:
  `ni wao` ("is theirs," Matt 5:3), `ni mkuu` ("is greater," Matt 11:11 ONMM).
  Direct correspondent to a supplied Greek copula ellipsis (§9.1.5) — likely
  **NEQ** when Greek has no εἰμί token, **primary** when Greek's εἰμί is
  explicit.
- **`si`** — the negative counterpart, equally invariant: `si juu yangu`
  ("is not up to me," Mark 10:40).
- **Locative/existential `-ko`/`-po`/`-mo`** fused onto `-wa`/no-TAM:
  `niko` ("I am [here/existing]," John 8:58, ἐγώ εἰμι rendered with a
  locative-existential copula rather than `ni`), `alikuwako` ("he existed/
  was there," John 1:1, ἦν). This is a real, alignment-relevant choice
  distinct from plain `ni`.

  **The conditioning is now resolved, and it is complement-type driven
  rather than a deep identity/existence semantic split.** A corpus sample
  of the genuine locative-copula forms (`yuko` 41×, `niko` 24×, `tuko` 14×,
  `uko` 10×, `mko` 7×, plus `wapo`/`umo`/`ipo`/`yapo`... — note `wako`, the
  single most frequent `-ko`-shaped string at 172 hits, is almost entirely
  the unrelated 2sg possessive "your," a homograph, and was excluded)
  showed **every single instance co-occurring with a locative/spatial
  complement** (`yuko mbinguni` "is in heaven," `yuko kule` "is there,"
  `niko pamoja nao` "I am with them," `yuko humo` "is in there," `yuko
  chini` "is below") **or a temporary/circumstantial-state complement**
  (`niko tayari` "I am ready," Luke 22:33, for Greek
  ἕτοιμός εἰμι — a plain adjectival predicate, not literally locative, but
  still a stage-level/circumstantial state rather than a defining identity).
  A direct cross-translation contrast confirms `ni` remains the more general
  default even for temporary predicates: Luke 22:33's ἕτοιμός εἰμι is
  `niko tayari` in ONEN/ONMM but SRUV06 restructures the same clause as
  `niwapo pamoja nawe, mimi ni tayari` — pulling the locative element
  ("while I am with you") into its own `-po`-marked clause and reverting to
  plain `ni` + adjective for "ready" once the locative element is removed
  from that immediate clause. **Working rule:** `-ko`/`-po`/`-mo` copula
  forms are triggered specifically when the copula's own complement is (or
  contains) a locative/spatial expression — matching their historical origin
  as the locative noun-class concords (classes 16/17/18) — not by an
  abstract identity-vs-existence distinction per se, though Greek's own bare
  existential ἦν/εἰμί (denoting presence rather than predication) reliably
  falls on the locative side of this split in practice. Align the copula
  form as **primary** to Greek's εἰμί/ἦν (or NEQ per §9.1.5 when the
  copula is supplied and Greek has none), the same as plain `ni`.
- **`-na`** ("have," lit. historically "with," but now conjugates directly
  with subject concord like an ordinary verb) — `wana mapango` ("[foxes]
  have holes," Matt 8:20), `hana mahali` ("[the Son of Man] has no place,"
  same verse, negative). This is the productive way Swahili expresses
  possession and, per the `awe na uzima` example above (lit. "may-he-be with
  life" = "may have eternal life"), overlaps with the periphrastic `kuwa na`
  ("to-be with" = "to have") construction built on **"na" as comitative**
  (see the dedicated "na" section below) rather than as a distinct lexeme.
  Needs a rule for whether `-na`/`kuwa na` aligns to a Greek "have"-verb
  (ἔχω) as an ordinary lexical correspondent (likely, straightforward) versus
  cases where it is a periphrastic existential-possession idiom translating
  something else entirely.
- **Emphatic identificational `ndi-` + class concord** (`ndiye`, `ndivyo`,
  `ndio`) — a fifth, previously unanticipated strategy: `Mimi ndiye huo
  ufufuo na uzima` ("I am the resurrection and the life," John 11:25 — an
  emphatic, fronted ἐγώ εἰμι) and `Hivi ndivyo mnavyopaswa kuomba` ("This is
  how you ought to pray," Matt 6:9). `ndi-` appears specifically where Greek
  itself marks emphasis (a fronted/emphatic ἐγώ εἰμι, or a demonstrative-led
  "this is how...") rather than plain unmarked identity, which plain `ni`
  covers. Likely rule: `ndi-` → **primary**, same treatment as plain `ni`,
  but worth flagging as the emphatic variant so an aligner does not treat
  `ni` and `ndi-` as interchangeable when choosing which Greek token (if any)
  the emphasis itself corresponds to.

**Confirmed variation in the "ought/must" (δεῖ-type) impersonal
construction** (§9.1.4 of the base principles): Matt 6:9's two coexisting
translations render the same Greek clause with different subject-marking
strategies — ONEN `mnavyopaswa` (2nd-plural SM `mna-`, "you-all ought") vs.
SRUV06 `iwapasavyo` (impersonal class-9 SM `i-`, "it-behooves"). Both are
legitimate translation choices for an impersonal Greek construction and
should receive the same alignment treatment regardless of which SM the
translator chose — parallel to how the base principles already treat
"it is necessary" / "you must" as equally valid renderings of δεῖ.

## PASSIVE VOICE AND VERBAL EXTENSIONS — [swh]

The passive suffix `-wa` (`akabatizwa`, "he was baptized," Mark 1:9) is
fully productive and morphologically transparent — likely the majority
strategy for Greek passive voice, structurally the cleanest match of any
currently-supported language (compare Arabic's and Hausa's much more
fragmented multi-strategy passive systems). Needs a real sample to confirm
it really is the majority strategy rather than one of several, the way every
other language's initial "obviously the passive marker" hypothesis has
turned out to be only part of the picture (Arabic NT's own passive finding
reversed between an early single-verse hypothesis and the corpus-scale
result — see `alignment-principles-nt.arb.md`).

Beyond `-wa`, Swahili has a productive stack of other verbal extensions that
sit between the root and the final vowel and are likely to absorb some of
what Greek expresses through separate words or through middle voice:

- **Stative/neuter `-ika`/`-eka`** — `alionekana` ("she was found/appeared,"
  Matt 1:18, from `-ona` "see" + stative `-ek-` = "be seen/found") — likely
  the Swahili strategy for a subset of Greek passives with a
  resultative/stative flavor (εὑρέθη-type), parallel to Indonesian's
  ter-+ada resultative-passive split and to Arabic's fourth,
  adjectival/stative passive strategy.
- **Applicative** confirmed already in OBJECT MARKING above (`-gawia`,
  `-letea` cross-referencing the recipient via OM).
- **Causative `-isha`/`-esha` — confirmed, with a clean periphrastic-Greek
  example.** Corpus search finds genuine causatives distinct from
  lexicalized false positives sharing the same string (`maisha` "life,"
  `kisha` "then," `mabishano` "arguments," and `kuwisha`-family "finish"
  forms all excluded): `fundisha` ("teach," causative of `-funda` "learn"),
  `onyesha` ("show," causative of `-ona` "see"), `thibitisha` ("confirm"),
  `hakikisha` ("make sure"), `lisha` ("feed," causative of `-la` "eat"),
  `julisha` ("inform," causative of `-jua` "know"), `sababisha` ("cause"),
  `kamilisha` ("fulfill/complete"). The clearest alignment-relevant case:
  Mark 6:39, ἐπέταξεν αὐτοῖς ἀνακλῖναι πάντας ("he commanded them to make
  everyone recline" — a Greek periphrastic causative: command-verb +
  dative "them" + infinitive used causatively/transitively + accusative
  "everyone") → `akawaamuru wawaketishe watu` ("he commanded them,
  they-should-seat the people" — `-ketisha` = `-keti` "sit" [intransitive]
  + causative `-isha`, in the subjunctive). Both Greek verbs (ἐπέταξεν
  "commanded," ἀνακλῖναι used causatively "make-sit") are preserved as two
  separate Swahili verbs (`amuru` "command" + causative-suffixed `ketisha`
  "seat"), not collapsed into one — a transparent, no-special-handling
  correspondence: align each verb normally as an ordinary lexical
  equivalent, both **primary**, with the causative suffix folded into its
  host verb's single record rather than requiring its own secondary/primary
  decision (it isn't adding an extra target-language word to place — it's
  simply how Swahili spells this particular lexeme).
- **Reciprocal `-ana` — confirmed**, corpus search finds genuine instances
  clearly distinct from lexicalized false positives sharing the same string
  (`maana`, `sana`, `mwana`, `bwana` all excluded, not reciprocal): 15
  instances of `wakaulizana` ("they asked each other"), several of
  `wakakutana` ("they met [with]"), and a family built on `-shindana`
  ("compete/struggle with"). Two confirmed patterns:
  1. **Genuine mutual reciprocal**, matching a Greek reflexive-used-
     reciprocally phrase: Mark 1:27, συζητεῖν πρὸς ἑαυτούς ("questioned
     among themselves") → `wakaulizana wao kwa wao` ("asked-each-other, they
     to they") — the Swahili **doubles** the reciprocal marking, both the
     verb-internal `-ana` suffix *and* the external phrase `wao kwa wao`
     ("they to they" = "each other"), for one Greek phrase. Likely rule:
     `-ana` **primary** to the verb root in the same record; `wao kwa wao`
     **primary** as well (both genuine lexical carriers of the reciprocal
     sense, parallel to the OM+independent-pronoun doubling rule in OBJECT
     MARKING, not a case of one being redundant filler).
  2. **Lexicalized, non-mutual use**: `-kutana` ("meet up," from `-kuta`
     "find/encounter" + `-ana`) is used even for one person meeting a single
     other person, not just mutual "each other" — Matt 8:28, ὑπήντησαν αὐτῷ
     ("[two men] met him," an ordinary transitive "meet" + dative object) →
     `wakakutana naye` ("they met with-him," the second party marked by
     comitative `na`, not a direct object). This confirms `-ana` has, at
     least for this root, grammaticalized past its literal reciprocal
     meaning into an ordinary lexical item — align it as a normal verb
     correspondent to Greek's "meet," not as a marker requiring a plural
     mutual subject.

## RELATIVE CLAUSES / SUBSTANTIVE PARTICIPLES — [swh]

Swahili has no participle morphology comparable to Greek's, so — like every
other supported language — Greek's substantive/attributive participles and
ordinary relative clauses both funnel into Swahili's relative-clause system.
**Corpus-scale count confirms both of the originally-hypothesized strategies
are common, in the same order of magnitude** — a whole-NT search finds 876
genuine `amba-` relative tokens (`ambaye` 306, `ambao` 203, `ambayo` 156,
`ambalo` 46, `ambapo` 43, `ambacho` 37, `ambako` 34, `ambavyo` 29, `ambazo`
17, `ambamo` 5) against several hundred infixed instances (a partial count
of just the clearest singular forms already exceeds 300: `aliye` 153,
`awezaye` 39, `aitwaye` 24, `asiye` 22, `atendaye` 22, `ajaye` 14, plus a long
tail — the true total including plural/other-class infixed forms is
certainly larger). Neither strategy is marginal.

1. **Infixed relative concord inside a (largely) tenseless verb form** —
   `amwaminiye` ("who believes in him," John 3:16: `a-` SM + `-mw-` OM +
   `amini` root "believe" + `-ye` relative concord), `waliozaliwa` ("who were
   born," Matt 11:11, retains `-li-` past tense + `-o-` relative), `aliye
   mkuu` ("who is greater," Matt 11:11), `uliye mbinguni` ("who is in
   heaven," Matt 6:9, 2sg form of the same paradigm addressed to God).

   **The `-li-` question is now resolved, and it splits cleanly by what
   follows it.** A frequency breakdown of `aliye`-family forms shows two
   sharply distinct patterns: `aliye` + a bare adjective/predicate/locative
   (`aliye na` 32×, `aliye hai` "who is alive" 17×, `aliye mbinguni` "who is
   in heaven" 13×, `aliye mkuu`, `aliye mdogo`, `aliye juu`, `aliye
   mtakatifu`...) is a **tenseless state-copula relative**, confirmed
   against Greek that has no past-tense element to license it at all: Matt
   5:16/5:45/6:1's `aliye mbinguni` all render Greek's bare substantival
   article-plus-locative construction τὸν/τοῦ ἐν (τοῖς) οὐρανοῖς ("[the one]
   in heaven[s]," §6.3 of the base principles — no verb, no tense, in the
   Greek at all). By contrast, `aliye` + a fused verb root (`aliyekuwa`
   108×, `aliyenituma` 25×, `aliyeitwa` 20×, `aliyepooza` 13×, `aliyezaliwa`
   12×, `aliyetumwa`, `aliyemfufua`, `aliyekufa`...) is a **genuine past-
   tense relative**, matching Greek aorist/perfect/imperfect participles or
   finite verbs in every sampled instance. **Working rule:** `-li-` +
   adjective/locative/PP predicate → the relative concord is **primary** to
   whatever Greek article/substantival construction licenses it (often no
   separate tense correspondent at all — the `-li-` itself is NEQ-adjacent,
   contributing no independent meaning to align against); `-li-` + verb
   root → ordinary past-tense verb, `-li-` folds into the verb's own record
   the same way any other TAM marker does.
2. **Invariable particle `amba-` + ordinary (non-infixed) relative concord
   suffix** — `ambaye`, `ambao`, `ambacho`, etc.

**A clean, confirmed sub-pattern: Greek relative *adverbs* (ὅπου "where,"
ὅθεν "whence") consistently map to `amba-` locative forms
(`ambako`/`ambapo`/`ambamo`), not to the infixed strategy**, sampled directly
in two verses: John 12:1, `Bethania mahali ambako Lazaro... alikuwa
anaishi` (ὅπου ἦν Λάζαρος → `ambako` — literally "the place ambako Lazarus
was living"), and Acts 14:26, `Antiokia, ambako walikuwa wamesifiwa kwa
ajili ya neema ya Mungu` (ὅθεν ἦσαν παραδεδομένοι τῇ χάριτι τοῦ θεοῦ →
`ambako`). Both verses simultaneously use the **infixed** strategy for an
ordinary relative *pronoun* in the same sentence (ὅν ἤγειρεν → `aliyekuwa
amefufuliwa`; ὅ ἐπλήρωσαν → `waliyokuwa wameikamilisha`) — a genuine,
repeated within-sentence contrast between adverb-triggered `amba-` and
pronoun-triggered infixation. This is not absolute, though: Rom 4:24
(`ambao Mungu atatupatia haki`) uses `amba-` for an ordinary relative
pronoun (οἷς) too, in a 1st-person-plural context — so the adverb
correlation looks like the strongest single predictor found so far, but not
an exceptionless rule.

**The 1st/2nd-person-plural hypothesis raised by that single instance is
now retracted — checked and not supported.** Infixed 1st/2nd-plural relative
forms turn out to be common and unremarkable (`mlio`, `tulio`, `mlivyo`,
`tulivyo`, `tunaye`, `tunayo`, `tunao`, `tunalo`, `mnaye`...), so a
1st/2nd-plural referent does not by itself push toward `amba-`. What looked
like a person-based pattern instead resolves into something more specific:
four separate verses in Acts (2:36, 3:13, 4:10, 5:30) reuse the identical
rhetorical template `ambaye ninyi mli-VERB` ("[Jesus,] whom you
[crucified/killed/...]") — Peter's sermons repeatedly accusing the same
audience in the same words. This is one author's repeated formula, not a
grammatical trigger — a caution about small samples: what first looked like
a systematic factor turned out, on checking, to be four instances of the
same phrase.

**A second confirmed pattern: `amba-` is also used for translator-supplied
relative clauses with no Greek relative word at all** — genuine discourse
restructuring (§9.8.1 of the base principles), not triggered by any specific
Greek token: Matt 1:3, Ἐκ τῆς Θαμάρ ("by/from Tamar," a bare prepositional
phrase) → `ambao mama yao alikuwa Tamari` ("whose mother was Tamar" — a
supplied relative clause where Greek has no relative word); Luke 15:17,
Πόσοι μίσθιοι τοῦ πατρός μου... ("how many hired-servants of my father...,"
no relative clause in Greek at all) → `walioajiriwa na baba yangu ambao wana
chakula...` ("who were hired by my father, who have food...," **two**
Swahili relative clauses — one infixed, one `amba-` — supplied for a single
Greek genitive noun phrase). In cases like this, the Swahili relative word(s)
should be **NEQ** or handled as generous-alignment secondary material tied
to the noun/preposition they restructure, per the base principles' existing
discourse-restructuring guidance — not forced onto a specific Greek relative
pronoun that does not exist.

**Working conclusion on strategy choice:** adverb-vs-pronoun is the
clearest signal found; discourse restructuring is a second, independent
trigger; author-level stylistic formulas (like Peter's repeated Acts
template) explain some of the remaining variation without needing a new
grammatical rule. The two strategies can appear stacked back-to-back on the
same head noun (as in the Luke 15:17 example) apparently for stylistic
variatio rather than any grammatical trigger. **Alignment treatment should
not depend on which strategy is used**: relative concord (infixed `-ye`/`-o`/etc., or `amba-` + suffix) →
English "who"/"which"/"that" equivalent — **primary** when a genuine Greek
relative word (pronoun or adverb) triggers it; **NEQ** when the relative
clause is a pure discourse-restructuring addition with no Greek trigger;
verb root → **primary**; any OM inside the relative form → folded in per the
OBJECT MARKING rule above.

**A third, related-but-distinct strategy confirmed: the "having/possessing"
relative `-enye`.** Corpus search finds ~410 clear instances of the
possessive-relative forms (`wenye` 192, `mwenye` 166, `yenye` 35, `lenye`
10, `zenye` 7) — not to be confused with the locative preposition `kwenye`
("at/in," 355 instances, a different grammaticalized use of the same root)
or the ordinary 3rd-person independent pronoun `yeye`/conjunction-pronoun
fusion `naye` (unrelated homophones flagged during the search, correctly
excluded from these counts). `-enye` renders a "having X" sense
periphrastically where Greek has a single lexical item: `Herode... akatoa
amri ya kuwaua watoto... wenye umri wa miaka miwili` ("Herod... ordered the
killing of children... having [wenye] an age of two years," Matt 2:16, an
attributive age phrase) and, more sharply, `wenye kifafa` ("having epilepsy"
= "epileptics," Matt 4:24, for the single Greek participle
σεληνιαζομένους) — both `wenye` and the following noun are **primary** to
the single Greek token in this pattern, parallel to the base principles'
treatment of a Greek compound lexical item split across multiple English
words (§8.1 "atoning sacrifice" → ἱλασμός). Confirmed as a genuine
alternative to full relative-clause periphrasis for the same semantic
territory: SRUV06 renders the adjacent δαιμονιζομένους ("demon-possessed,"
same verse) with `wenye pepo` ("having spirits") where ONEN instead chose a
full infixed-relative-plus-passive periphrasis, `waliopagawa na pepo
wachafu` ("who were seized by unclean spirits") — the same underlying
concept, two different Swahili strategies, confirming `-enye` is a real,
productive competitor to the relative-clause system rather than a marginal
form.

**The choice between `-enye` and a full relative clause is now resolved,
and it is systematic, not free variation** — a clean semantic-frame split
confirmed across several verses regardless of Greek's own surface
encoding: `-enye` is the default whenever the underlying sense is
"having/characterized by a quality or possession," **even when Greek
encodes that sense as a genuine finite relative clause with ἔχω**, not just
when Greek uses an adjective or participle. Matt 5:6, μακάριοι οἱ πεινῶντες
καὶ διψῶντες ("blessed are those hungering and thirsting," a substantive
participle) → `wenye njaa na kiu` ("having hunger and thirst"); Matt 8:2/
10:8/11:5, λεπρός/λεπρούς/λεπροί ("leper[s]," a plain adjective) → `wenye
ukoma` ("having leprosy") consistently across all three verses; and most
tellingly, Luke 15:4, ἄνθρωπος ὃς ἕξει πρόβατον ("a man who will have a
sheep" — a genuine Greek relative clause built on the finite verb ἔχω) →
`mwenye kondoo wake` ("having his sheep") — **still `-enye`, not an infixed
or `amba-` clause with a Swahili verb "have,"** even though Greek's own
grammar here is a true action/state relative clause. This confirms the
conditioning is about the **semantic frame** ("characterized by X"), not
about whether Greek happens to package that frame as an adjective, a
participle, or a relative clause — genuinely eventive/action relative
clauses (who did/does/will do something, not "who has/is characterized by
X") are the ones that get the infixed/`amba-` treatment instead. This
question is now closed enough to build a rule on: whenever the sense is
possession/characterization, expect and align `-enye` + noun (both
primary) against whatever Greek token(s) carry that sense, regardless of
Greek's own part of speech.

## INFINITIVAL CONSTRUCTIONS — [swh]

Swahili **does** have a true infinitive, class 15 `ku-` + verb stem
(`kuomba` "to pray/ask," Matt 6:9; `kuzaliwa` "to be born" / "birth," Matt
1:18; `kupenda` "to love"), unlike Indonesian, Hindi, Arabic, and Hausa, all
of which lack one — this is the first currently-supported non-European,
non-Romance language with a real infinitive class. Likely the most
straightforward infinitive-handling case in the project: probably maps
closely to the base principles' existing infinitive rules (§9.3.1) with `ku-`
patterning like English "to." One wrinkle already visible: `kuzaliwa` is used
*nominally* ("the birth of...", Matt 1:18) where Greek might have a genitive
absolute or a nominalized construction rather than a bare infinitive — since
class 15 infinitives are simultaneously infinitives *and* ordinary class-15
nouns (they take class-15 concord, as in `kwake` "of-his" agreeing with
`ku-`, seen in the same verse), Swahili's infinitive-as-noun duality may end
up needing the same two-track treatment the base principles already give the
Greek articular infinitive (§6.3) — bare-infinitive-as-noun vs. explicit
nominalization. Needs checking against a real sample of genitive absolutes
and articular infinitives specifically.

## ἵνα / PURPOSE CLAUSES — [swh]

`ili` + subjunctive (final vowel `-e`, no TAM marker) is the standard
Swahili purpose conjunction: `ili kila mtu amwaminiye asipotee` ("so that
everyone who believes in him should not perish," John 3:16 — note the
subjunctive `-e` on both the relative-clause verb `amwaminiye` and the
purpose-clause verb `asipotee`). Likely maps directly onto the base
principles' ἵνα rules (§9.3.2) — `ili` → "so that"/"that," primary; the
subjunctive verb → primary. Confirmed distinct from a **periphrastic
`-pata` (get/obtain, subjunctive) + infinitive** strategy also attested for
ἵνα + subjunctive: `ili mpate kujua kwamba...` ("so that you may know/get to
know that...," Matt 9:6, ONEN) renders ἵνα...εἰδῆτε with `ili` (purpose,
as expected) but then a periphrasis (`mpate` "you-may-obtain," subjunctive +
`kujua` "to-know," infinitive) rather than a single finite subjunctive verb
for "know." Likely rule: both `mpate` and `kujua` are **primary** to the
single Greek subjunctive verb (parallel to the base principles' treatment of
verbal-aspect distribution across two English words, §9.1.3), not `mpate`
secondary to `kujua` — `pata` here is not a meaningless auxiliary but carries
real "come to/manage to" semantic content the translator chose to make
explicit. Needs checking whether this periphrasis is a common variant or
this single instance's idiosyncrasy, and whether `ili` is used consistently
for ἵνα or shares space with a bare-subjunctive-with-no-conjunction pattern
or the same purpose/reason unification seen in Hausa's
`don`/`domin`/`saboda`/`gama` family.

## ὅτι / COMPLEMENT CLAUSES — [swh]

**`kwamba` confirmed as the standard content-clause complementizer**:
`ili mpate kujua kwamba Mwana wa Adamu anayo mamlaka...` ("so that you may
know that the Son of Man has authority...," Matt 9:6, ONEN/ONMM) — a clean
ὅτι → "that" content-clause match, likely **primary** 1:1 per the base
principles' ὅτι content-clause rule (§9.7.3). SRUV06 uses the fuller variant
`ya kwamba` for the same slot in the same verse — a genuine, low-risk
cross-translation variant (both should get the same alignment treatment,
`ya` folded in as part of the complementizer rather than treated as a
separate token needing its own decision).

**`kuwa` confirmed as a genuine third content-clause complementizer,
distinct from and much rarer than `kwamba`.** Corpus search finds clean
instances: `walimjua kuwa yeye ndiye Kristo` ("they knew that he was the
Christ," Luke 4:41), `watu wote watajua kuwa ninyi ni wanafunzi wangu`
("all people will know that you are my disciples," John 13:35),
`wakasikia kuwa watu wa Mataifa... wamepokea neno la Mungu` ("they heard
that the Gentiles... had received the word of God," Acts 11:1) — all bare
`kuwa` directly after a verb of knowing/hearing, structurally identical to
`kwamba`'s content-clause role and requiring the same alignment treatment
(**primary** 1:1 to ὅτι), but at roughly a tenth of the frequency (a
double-digit count of clear instances against 699 `kwamba` tokens in the
same corpus) — a real but minority variant, not a co-equal default.

**Causal ὅτι/γάρ ("because") is confirmed separately, and must not be
confused with the complementizer**: the fixed idiom `kwa kuwa` ("because,"
252 corpus instances) is structurally `kwa` ("for/by") + `kuwa`
("to-be"/complementizer) fused into a single causal conjunction — a much
more frequent pattern than either content-clause complementizer variant.
Align `kwa kuwa` as a unit, **primary** to causal ὅτι/γάρ, and take care
that an LLM-assisted pass does not mis-split it as a locative/instrumental
`kwa` plus a stray complementizer `kuwa` — the two need distinct,
non-overlapping treatments despite sharing the string `kuwa`.

**Recitative ὅτι — confirmed: NEQ, same as English.** A corpus search for
a speech verb (λέγω) immediately followed by ὅτι finds 106 candidates;
sampling six of them directly (Matt 9:18, Matt 10:7, Matt 14:26, Matt 16:7,
Mark 1:15, Mark 2:12) shows **no Swahili word of any kind** corresponding to
the recitative ὅτι in any instance — only quotation marks (or, in the raw
source text, none at all) introduce the direct speech, exactly the base
principles' existing rule (§9.7.3: ὅτι recitative → NEQ when only
punctuation introduces the quotation). No separate Swahili-specific rule is
needed here; the ordinary base-principles treatment transfers cleanly.

## CONDITIONAL CONSTRUCTIONS — [swh]

**Confirmed: (at least) three coexisting strategies for real/open
conditions**, sampled directly against John 3:3, John 3:5, and Matt 18:8 —
richer than the single-strategy hypothesis in the original proposal:

1. **`kama`/`ikiwa` + negative perfect indicative**, with no `-ki-`/`-si-`
   TAM marking at all: `kama hajazaliwa mara ya pili` ("if he has not been
   born again," ONEN/ONMM, John 3:3, for ἐὰν μή τις γεννηθῇ). Here the whole
   conditional force rides on the conjunction; the verb is ordinary negative
   perfect indicative.
2. **Negative conditional-relative infix `-sipo-`** (`-si-` negation +
   `-po-` conditional/locative-relative), **no separate conjunction**:
   `Mtu asipozaliwa mara ya pili` (SRUV06, same verse) — the conditional
   force is carried entirely by the verb's own morphology; no `kama`/`ikiwa`
   present. This is the clean TAM-marked strategy the original proposal
   predicted, but SRUV06 uses it where ONEN instead chose strategy 1 for the
   *same verse* — a genuine, confirmed translation-level choice, not
   dialectal variation.
3. **`-ki-` infix alone, no conjunction**, for a real *positive* condition:
   `mkono wako... ukikukosesha` ("if your hand... causes you to sin,"
   SRUV06, Matt 18:8, for Εἰ...σκανδαλίζει) — contrasted with ONEN/ONMM's
   own choice for the *same verse*, `Ikiwa mkono wako... unakusababisha`
   (conjunction `Ikiwa` + plain indicative, no `-ki-` at all). Also `hata
   akifa atakuwa anaishi` ("even if/though he dies, he will live," John
   11:25, κἂν ἀποθάνῃ — `-ki-` here paired with the concessive particle
   `hata` "even").

**Working rule:** whichever strategy a given translation/verse uses, the
element(s) carrying the conditional force (`kama`/`ikiwa`/`hata` when
present, and/or the `-ki-`/`-sipo-` infix when present) align **primary** to
Greek εἰ/ἐάν (and to μή within it, when the infix itself is negative) — the
same "align what the translator actually did" principle already governing
the base document's conditional section (§9.7.4). The main remaining
question is not *whether* to align these (clear) but making sure an
LLM-assisted pass can reliably locate `-ki-`/`-sipo-` as fused TAM morphology
inside an otherwise-ordinary-looking verb word when no conjunction is
present to flag the clause as conditional at all.

**Counterfactuals — confirmed, and the present/past split revised.**
Corpus search finds `-nge-`/`-ngeli-` (dozens of clear instances: `ingekuwa`,
`mngekuwa`, `angekuwa`, `ningeweza`, `angeweza`, `wangekuwa`, `ungelikuwa`...)
and `-ngali-` (a dozen clear instances after excluding the unrelated
`-angalia-`/`-angalifu-` "watch/careful" root family: `ungalikuwa`,
`hangalikufa`, `wasingalikuwa`, `angaliweza`...) both real and productive.
But **two direct cross-translation comparisons on the same verse overturn
the original present-vs-past split hypothesis**:

- John 11:21, εἰ ἦς ὧδε οὐκ ἂν ἀπέθανεν ("if you had been here, [my brother]
  would not have died" — a classical unreal-*past* condition): ONEN
  `ungalikuwa hapa, ndugu yangu hangalikufa` (`-ngali-`) vs. ONMM
  `ungekuwa hapa, ndugu yangu hangekufa` (`-nge-`) — **the same translation
  family renders the identical unreal-past condition with both strategies
  in its own two editions.**
- Matt 11:21, a second unreal-past condition (ἐγένοντο ... ἂν ...
  μετενόησαν): ONEN/ONMM `ingefanyika... ingekuwa imetubu` (`-nge-`) vs.
  SRUV06 `ingalifanyika... wangalitubu` (`-ngali-`) for the same verse.

**Revised conclusion:** `-nge-`/`-ngeli-` is not restricted to *present*
counterfactuals — it covers past counterfactuals too, in free variation
with the more explicit `-ngali-` — a translation-level stylistic choice, not
a grammatical present/past distinction. Both should receive the same
alignment treatment (primary to εἰ/ἐάν and to the counterfactual force
however Greek marks it — imperfect+ἄν, aorist+ἄν, etc.), regardless of which
of the two morphemes a given translation happens to use.

## COMPARATIVES — [swh]

**Revised after sampling Matt 11:11 and Mark 10:25:** `kuliko` ("than") is
confirmed as the standard marker of the compared standard, but comparison is
not always `kuliko`-alone — it commonly pairs with an **analytic
intensifier `zaidi`** ("more/additionally") on the adjective/predicate
itself: `Ni rahisi zaidi kwa ngamia... kuliko mtu tajiri...` ("it is easier
[lit. easy-more] for a camel... than [for] a rich man...," Mark 10:25, for
εὐκοπώτερόν... ἢ...). This means Greek's *synthetic* comparative morpheme
(εὐκοπώτερον, itself one word) can render as a **two-part** Swahili
construction — `zaidi` intensifying the adjective, `kuliko` marking the
standard — both **primary** to the single Greek comparative token, parallel
to the base principles' analytic-comparative treatment (§9.4.1, "more" +
adjective both primary) despite Greek using synthetic morphology, not
analytic μᾶλλον. `mkuu kuliko Yahya` (Matt 11:11) shows the simpler,
`zaidi`-less pattern (bare adjective + `kuliko`) for the same comparative
category, so `zaidi` is confirmed to be optional, not obligatory — still
needs a larger sample to know what conditions its presence (translator style
vs. something in the Greek).

**Superlative — confirmed: `kuliko wote` ("than all"), a corpus search finds
10 clear instances**, e.g. `nani aliye mkuu kuliko wote katika Ufalme wa
Mbinguni?` ("who is greatest [lit. great-than-all] in the kingdom of
heaven?," Matt 18:1/18:4). This is not a separate superlative construction
at all — it is the ordinary `kuliko` comparative with `wote` ("all") as the
standard of comparison, exactly as the original hypothesis predicted:
Swahili has no dedicated superlative morphology, and Greek's synthetic
superlative (μικρότερος, μείζων used superlatively, etc.) maps onto the same
`kuliko` mechanism as ordinary comparatives, distinguished only by `wote`
filling the comparison-standard slot. `wote` → **primary**, part of the same
record as `kuliko` and the adjective.

**Elative — confirmed: `kabisa` ("very/utterly/completely")**, a corpus
search finds 57 instances, several in a clearly elative-superlative role
parallel to English "least"/"most": `aliye mdogo kabisa katika Ufalme wa
Mbinguni` ("the least [lit. very-small] in the kingdom of heaven," Matt
5:19, 11:11) and `atasagwa kabisa` ("will be utterly crushed," Matt 21:44).
Likely rule, parallel to the base principles' elative superlative treatment
(§9.4.1, "most holy": intensifier + adjective both primary): `kabisa` →
**primary**, in the same record as the adjective it intensifies, whenever
Greek's own form is being used elatively/superlatively rather than as an
ordinary positive-degree adjective.

## NEGATION — [swh]

Negation is TAM-conditioned and largely circumfixal/fused, not a single
free-standing particle:

- **Negative subject-marker set** (`ha-` + often-irregular class/person
  combination) obligatorily co-occurs with tense-specific post-marking —
  seen in `hana` ("he/she has not," Matt 8:20, negative of `-na` "have"),
  `hajakuwa`/`hajatokea` ("had not yet been/appeared," John 8:58 / Matt
  11:11 — negative perfect uses `-ja-` "not yet," contrasting with positive
  `-me-`), `hawajakutana` ("they had not yet met," Matt 1:18).
- **Subjunctive/purpose-clause negation uses a distinct infix `-si-`** with
  a final-vowel change to `-e`: `asipotee` ("so that he might not perish,"
  John 3:16) — structurally its own paradigm, not a simple insertion of the
  ordinary negative marker into the subjunctive form. This distinction
  (ordinary-tense negation vs. subjunctive/relative negation using different
  machinery entirely) parallels the base principles having no single
  "negation" rule that covers every mood, and needs its own explicit
  sub-rule once verified.
- **Copula negation is the separate invariant word `si`** (see COPULA
  above), not a `ha-`/TAM-conditioned verb form at all — `si juu yangu` (Mark
  10:40).

Likely rule (pending verification): each negative marker — wherever it
surfaces in the fused verb word — aligns as its own **primary** record
against the Greek negation particle (οὐ/οὐκ/μή/οὐ μή etc.), the same
treatment the base principles give English "not" (§9.7.2), even though the
Swahili marker is not a separate space-delimited token. The main open
question is whether an LLM-assisted refine pass can reliably *locate* the
negative morpheme inside an unspaced fused verb word — a harder task
mechanically than Hausa's free-standing `ba... ba` circumfix, and possibly
harder than anything any other currently-supported language's negation
system has required.

## "na" — AND / WITH / BY (passive agent) / HAVE — [swh]

Flagged once above under Key Differences but important enough to treat as
its own section: the single word `na` covers at minimum four distinct
alignment-relevant functions, all seen in the small sample:

1. **Coordinating "and"** between clauses/phrases — likely the default,
   ordinary καί correspondent.
2. **Comitative "together with"** — `pamoja na Mungu` ("together with God,"
   John 1:1) — likely corresponds to Greek πρός + accusative or μετά +
   genitive in "with" contexts, distinct from plain καί.
3. **Passive agent marker "by"** — `akabatizwa na Yahya` ("he was baptized
   by John," Mark 1:9) — corresponds to Greek's ὑπό + genitive agent
   construction (§9.1.1), NOT to a coordinating καί even though it is the
   same Swahili word. This is the case most likely to be mis-analyzed by an
   LLM defaulting to "na = and" and needs an explicit disambiguation rule
   keyed to whether the preceding verb is passive and the following noun is
   an animate/personal agent.
4. **Existential "have"** — `kuwa na`/the fused verb `-na-` itself (see
   COPULA above) — "to-be with X" = "to have X."

Needs a real sample stratified across all four functions (not hard to find —
Mark 1:9's passive-agent `na` and John 1:1's comitative `na` are both in the
tiny sample already pulled for this document) before proposing the specific
per-function alignment rule, but the core methodological point — that `na`'s
four functions must be disambiguated by syntactic context before an
alignment decision is made, not treated as a single lexical item with one
default — should already be treated as settled.

## Cross-translation methodology note (for step 2)

- **ONMM** is the from-scratch alignment target with no existing data — the
  primary object of verification.
- **ONEN**'s existing alignment is suspected sparse/statistical and should be
  spot-checked, not trusted, before any decision to lean on it (same caution
  applied to the retracted zht/hau UBS alignments and to ONAV's OT source
  alignment).
- **SRUV06** is consult-only (not openly licensed): useful for seeing how a
  second, independent Swahili translation handles a specific construction
  (the way BOCCB2023T or ONAV serve for zht/arb), but its own alignment data
  is reportedly sparse and keyed to key-term coverage rather than
  comprehensive token alignment, so it should be treated the same skeptical
  way ONAV's UBS-manual OT alignment and the retracted zht/hau alignments
  were treated — read the raw SRUV06 *text* for comparison, do not trust its
  alignment JSON as ground truth without its own spot-check.
- ONEN and ONMM track each other closely enough (near-identical wording in
  every sample verse above) that once one has a trustworthy from-scratch
  alignment, `diff-migrate` is likely to be a strong candidate for seeding
  the other — a stage-3 question, noted here for later, not attempted yet.

## Resolved (working rules established, confirmed against real samples)

- **Object marking (OM) doubling an explicit object noun** — resolved:
  topicality/givenness-conditioned, not noun-presence-conditioned; three
  patterns identified (OM-alone, no-OM-bare-noun, OM+noun-doubling), plus a
  distinct near-categorical OM+independent-pronoun doubling sub-case and a
  recipient-tracking rule for ditransitives/applicatives. See OBJECT MARKING.
- **ὅτι-equivalents** — `kwamba` (ONEN/ONMM) and `ya kwamba` (SRUV06)
  confirmed as content-clause complementizers in a real instance (Matt 9:6).
  `kuwa`, causal ὅτι, and recitative ὅτι remain unattested.
- **Conditional constructions (real/open)** — (at least) three coexisting
  strategies confirmed across John 3:3/3:5, Matt 18:8, and John 11:25:
  `kama`/`ikiwa` + plain indicative (no TAM marking), negative `-sipo-`
  infix (no conjunction), and positive `-ki-` infix (no conjunction,
  sometimes with concessive `hata`) — with ONEN and SRUV06 making
  *different* choices for the *same* verse in two of the sampled cases,
  confirming this is translation-level variation, not free variation within
  one text.
- **Counterfactual conditionals** — `-nge-`/`-ngeli-` and `-ngali-` both
  confirmed productive at corpus scale. The original present-vs-past split
  hypothesis is revised: two direct same-verse cross-translation comparisons
  (John 11:21, Matt 11:21) show `-nge-` and `-ngali-` both rendering the
  identical unreal-*past* Greek condition in different editions — free
  stylistic variation, not a grammatical present/past split. See
  CONDITIONAL CONSTRUCTIONS.
- **Comparatives** — revised: comparison can be two-part (`zaidi` + `kuliko`),
  not `kuliko`-alone, for a Greek synthetic comparative.
- **Superlative** — confirmed: `kuliko wote` ("than all"), the ordinary
  comparative with `wote` as the standard — not a separate construction, 10
  corpus instances.
- **Elative** — confirmed: `kabisa` ("very/utterly"), e.g. `mdogo kabisa`
  ("least," lit. "very small") for a Greek superlative used elatively.
- **Copula system** — revised from four strategies to five: added the
  emphatic identificational `ndi-` (+ concord) strategy, unanticipated in the
  original proposal.
- **δεῖ-type impersonal "ought" construction** — confirmed genuine
  cross-translation variation in subject-marking strategy (2pl vs.
  impersonal-class SM) for the same Greek clause, parallel to how the base
  principles already treat "it is necessary" / "you must" as equally valid.
- **Relative-clause strategy selection (infixed vs. `amba-`)** — both
  confirmed common at corpus scale (876 `amba-` tokens vs. 300+ in a partial
  infixed count). Strongest single predictor found: Greek relative
  *adverbs* (ὅπου/ὅθεν) consistently trigger `amba-` locative forms
  (`ambako`/`ambapo`/`ambamo`) where an ordinary relative *pronoun* in the
  same sentence gets the infixed strategy — not exceptionless (a
  1st-person-plural pronoun context also pulled toward `amba-`). `amba-`
  is also confirmed used for pure translator-supplied discourse
  restructuring with no Greek relative word at all (NEQ territory). Working
  rule established: align what the translator did regardless of strategy;
  NEQ only when there is no Greek trigger. See RELATIVE CLAUSES.
- **The "having/possessing" relative `-enye`** — confirmed as a third,
  distinct, productive strategy (~410 corpus instances) competing with full
  relative-clause periphrasis for the same semantic territory (a direct
  same-verse cross-translation contrast in Matt 4:24 shows one edition using
  `-enye`, the other a full relative+passive clause, for parallel Greek
  participles).
- **Reciprocal `-ana`** — confirmed with two sub-patterns: genuine mutual
  reciprocal (sometimes doubled with an external `wao kwa wao` phrase) and
  a lexicalized non-mutual use (`-kutana` "meet [with]," no longer requiring
  a plural mutual subject). Applicative confirmed already via OBJECT
  MARKING's recipient-tracking pattern.

## Resolved in this second pass

- **The `-li-` question** — resolved: splits cleanly by what follows it.
  `-li-` + adjective/locative/PP predicate (`aliye na`, `aliye hai`, `aliye
  mbinguni`...) is a tenseless state-copula relative, confirmed against
  Greek constructions (the bare substantival article+locative pattern, §6.3)
  that carry no tense at all; `-li-` + fused verb root (`aliyekuwa`,
  `aliyeitwa`, `aliyezaliwa`...) is a genuine past-tense relative matching
  Greek aorist/perfect/imperfect forms in every sampled instance. See
  RELATIVE CLAUSES.
- **Copula/existential-locative split** — resolved, and revised from a
  Hausa-style identity/existence split to a complement-type-driven one:
  `-ko`/`-po`/`-mo` are triggered specifically when the copula's own
  complement is (or contains) a locative/spatial expression, or a
  temporary/circumstantial-state predicate — not by an abstract
  identity-vs-existence distinction. A direct cross-translation contrast
  (Luke 22:33) shows a translator actively restructuring a clause to move
  the locative element into its own `-po`-marked clause specifically so the
  remaining predicate ("ready") could revert to plain `ni`, confirming the
  conditioning is genuinely about the complement, not free variation. See
  COPULA.
- **Causative `-isha`/`-esha`** — confirmed productive, with a clean example
  (Mark 6:39) of a Greek periphrastic causative (command-verb + causative-
  used infinitive) mapping onto two separate ordinary Swahili verbs, one of
  them causative-suffixed — no special alignment handling needed beyond
  normal lexical correspondence. See PASSIVE VOICE AND VERBAL EXTENSIONS.
- **The `akavibariki` class-8 default-agreement wrinkle** — confirmed as a
  real, repeated pattern (not a one-off): identical across three
  independent Synoptic tellings of the same feeding-miracle narrative
  (Matt 14:19, Mark 6:41, Luke 9:16), and distinguished from ordinary
  class-8 concord by a control case (Mark 8:7) using the same OM shape for
  a genuinely singular class-8 noun. See OBJECT MARKING.
- **`kuwa` as a ὅτι-equivalent** — confirmed as a genuine but minority
  third complementizer (a double-digit count of clear instances against
  `kwamba`'s 699), and clearly distinguished from the unrelated, much more
  frequent causal idiom `kwa kuwa` ("because," 252 instances) that happens
  to share the string `kuwa`. See ὅτι / COMPLEMENT CLAUSES.

## Resolved in this third pass

- **Recitative ὅτι** — confirmed NEQ, same treatment as English (§9.7.3).
  Six sampled instances of λέγω/λέγοντες + ὅτι + direct speech all show no
  Swahili word corresponding to the recitative ὅτι itself — only quotation
  marks. No Swahili-specific rule needed.
- **`-enye` vs. full relative-clause periphrasis** — resolved: systematic,
  not free variation. `-enye` is the default whenever the underlying sense
  is "having/characterized by a quality or possession," regardless of
  whether Greek encodes that as an adjective, a participle, or — most
  tellingly — a genuine finite relative clause built on ἔχω (Luke 15:4,
  ἄνθρωπος ὃς ἕξει πρόβατον → `mwenye kondoo wake`, still `-enye`, not a
  verbal relative clause). Full relative-clause periphrasis (infixed or
  `amba-`) is reserved for genuinely eventive/action relatives. See
  RELATIVE CLAUSES.
- **The plural/1st-person pull toward `amba-`** — retracted. Infixed
  1st/2nd-plural relative forms (`mlio`, `tulio`, `tunaye`...) turn out to
  be common, so person/number is not a real conditioning factor. The
  apparent cluster was four instances of one repeated rhetorical formula in
  Peter's Acts sermons (`ambaye ninyi mli-VERB`), not a grammatical trigger
  — a useful caution about small samples.

## Still open (minor, and narrow enough not to block drafting the config)

- The homographic `ambao` (class 2 human-plural vs. class 11 concord,
  spelled identically) — noted, doesn't change alignment treatment, but
  worth a footnote if it ever causes confusion downstream.
- The working assumption going forward should remain that at least one
  claim above could still turn out wrong or incomplete once checked at
  larger scale — every other from-scratch build in this project (zht's
  participle/pronoun reversals, Hausa's unanticipated second
  substantive-participle strategy, OT Arabic's Pass-1→Pass-2 reversals) has
  had at least one genuine reversal along the way, and this document has
  already had several across three passes (comparatives, copula, the
  counterfactual present/past split, the retracted plural/`amba-` link).
  That said, every substantive open question raised across all three passes
  now has a working rule with real evidence behind it — drafting
  `prompt/nt/swh.py` from the current state of this document is a
  reasonable next step.
