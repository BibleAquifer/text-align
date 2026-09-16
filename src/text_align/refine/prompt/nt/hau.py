"""Hausa target-language prompt config for refine-alignment.

Examples grounded in OHCB (Open Hausa Contemporary Bible) — checked against the
actual target TSV (`data/targets/OHCB/nt_OHCB.tsv`) joined by verse to SBLGNT,
at full-corpus scale for every construction below (sample sizes noted per
section in docs/alignment-principles-nt.hau.md). No second Hausa NT translation
was available for cross-checking (unlike fra/ind/hin/arb); an existing UBS
manual alignment (`alignments-hau/alignments/OHCB/SBLGNT-OHCB-manual.json`) was
examined and rejected as a verification aid — it showed the same failure
pattern that sank zht's first draft (9.4% of negation particles aligned, 0.1%
of pronouns, 0% of articles, plus a confirmed wrong link) — see the
Cross-translation methodology note in the docs file. **Draft — not yet
reviewed by a native Hausa speaker.**

Key differences from every other currently-supported language:

  BASE_BLOCK    — Hausa's Person-Aspect Complex (PAC): a preverbal particle
                  fusing subject pronoun + tense/aspect/mood into ONE word
                  (ya/ta/muka/suka/zai/ana/an...). No separate PAC form is used
                  in equational/nominal clauses (those use the independent
                  pronoun directly). PAC aligns SECONDARY to the verb when
                  Greek marks person only via verb morphology (no separate
                  pronoun token — same rule as English's own "subject pronoun
                  from verb ending" case), but PRIMARY, in its own record, when
                  Greek has an explicit nominative pronoun (ἐγώ/σύ/αὐτός/
                  ἡμεῖς/ὑμεῖς) — exactly like English ἐγώ→"I"/εἰμί→"am"
                  splitting into two primary records. Contrastive/topicalized
                  fronting (Greek μέν...δέ) additionally fronts an independent
                  pronoun as its own primary record alongside the ordinary PAC.
                  Possessive pronouns are fused suffixes on the host noun (not
                  separate tokens); object pronouns ARE separate tokens (unlike
                  Indonesian's fused -ku/-mu/-nya).
                  Definiteness is a fused `-n`/`-r` suffix with TWO functions
                  sharing one form: plain definiteness on a bare noun, or an
                  obligatory "linked/construct state" before ANY following
                  complement (genitive noun, possessive suffix, even a
                  relative clause) — regardless of whether Greek has an
                  article at all. A free linker `na`/`ta` and a prepositional
                  `ga` cover genitive/possession's objective and complex-head
                  cases. Five other real genitive strategies exist beyond
                  simple linking (see the base block below).
                  Hausa's copula system is five-way, split by function, not by
                  whether Greek's εἰμί is morphologically present: `ne`/`ce`
                  for tenseless identity, `akwai`/`babu` for existence,
                  bare relative-continuous `yake`/`suke` for locative
                  predicates, `zama`/`kasance` for future or predicate-
                  adjective "be", and `wato` for the formulaic ὅ ἐστιν
                  explanatory gloss.
  PASSIVE_BLOCK — Impersonal `an`/`aka`/`ana`/`ake`/`akan`/bare `a` is the
                  single largest strategy (≥40-48% of verses) but NOT a
                  majority — seven other real, coexisting strategies:
                  unmarked ambitransitive verb choice (lexically conditioned
                  per Greek verb), light-verb (`yi`/`sha`/`kai`) + abstract
                  noun (a MAJOR strategy for psych/relational verbs — astonish,
                  err, reconcile, suffer, be saved — not a one-verb quirk),
                  agent promotion to active subject (including a supplied
                  `Allah` for implicit divine passives), stative `a`+deverbal-
                  adjective+copula for perfect/resultative aspect, nominali-
                  zation ("become/have"+noun/adjective), full restructuring
                  with no verbal correspondent, and a narrow Grade-7 `-u`
                  reflexive-verb pattern (2 confirmed instances, not
                  productive — do not hunt for it as a category).
  PARTICIPLE_BLOCK — NINE real strategies, not the `wanda`/`mai`/`duk wanda`
                  three anticipated: `wanda`-family headless relative (largest
                  single strategy); a `da`-relative clause attached to an overt
                  head noun/pronoun/demonstrative (the single biggest miss —
                  second most common strategy overall, chosen by whether the
                  translator supplied a head word, not by anything in the
                  Greek); `mai`/`masu` agentive (plus lexicalized `ma`-prefix
                  nouns that are just vocabulary); generic `duk`+wanda/mai or
                  bare `Kowa`; a cleft/focus construction with bare `yake`/
                  `suke` and no relative marker at all (concentrated in "it is
                  God who..." identity claims); privative `mara-`/`marasa`
                  ("lacking X"); a naming-idiom `(ake) kira X` for λεγόμενος/
                  καλούμενος; a lexicalized deverbal noun (`haifaffe`); and
                  full restructuring/omission.
  INFINITIVE_BLOCK — No infinitive form. Modal/phase complements (θέλω,
                  δύναμαι, μέλλω, ἄρχομαι, δεῖ...) mostly become a serial-verb
                  chain using a distinct SUBJUNCTIVE PAC paradigm (in/ka/ta/
                  yă/mu/su — separate from the ordinary indicative PAC in the
                  base block), with real nominalization as a minority option;
                  δεῖ often drops necessity-marking entirely. Purpose
                  infinitives of every type (bare, εἰς τό, πρός τό, τοῦ-
                  genitive) unify into the SAME `don`/`domin`/`saboda`+
                  subjunctive family as ἵνα (HINA_BLOCK) and causal ὅτι
                  (HOTI_BLOCK). ὥστε-result infinitives split by realized
                  (`har`+indicative or unmarked continuation) vs. intended
                  (same purpose family) vs. explicit-causative (`ya sa`/
                  `tilasta`). Temporal articular infinitives (μετὰ τό, ἐν τῷ)
                  mostly RE-FINITIZE into an ordinary temporal clause
                  (`bayan`/`da`/`sa'ad da`/`yayinda`+PAC+verb) rather than
                  staying nominal — contrary to the textbook default guess.
  HINA_BLOCK    — See INFINITIVE_BLOCK: `don`/`domin`/bare-subjunctive is a
                  unified purpose/reason system shared with causal ὅτι.
  COMPARATIVE_BLOCK — Six strategies built mostly on the verb `fi` ("exceed"):
                  predicative `fi`-clause (majority: "[PAC] fi [compared
                  entity] [quality-noun]"), attributive prenominal `mafi`+
                  adjective, explicit binary "than" `fiye da`, superlative-
                  among-a-group `mafi`+adjective+`a`/`cikin`+group (Greek's
                  genitive-of-comparison converts to a partitive "among"
                  phrase, not `fiye da`), quantity/majority `yawanci`, and a
                  formal-register nominalized `fifiko`+`a kan`. Caveat: several
                  comparative-tagged Greek-parallel words are lexicalized
                  nouns (πρεσβύτεροι "elders") with no live comparison sense.
  HOTI_BLOCK    — Causal ὅτι joins the SAME `don`/`domin`/`saboda`/`gama`
                  family as ἵνα-purpose and ὥστε-result — a bigger unification
                  than the textbook default assumed. Declarative ὅτι is a
                  separate system: NEQ for direct quotation, `cewa`/bare
                  parataxis (both real, coexisting) for indirect complements,
                  occasionally `yadda` or recast into the causal family.
  CONDITIONAL_BLOCK — εἰ has FOUR functions, not one: real conditional (→ `in`,
                  same as ἐάν), interrogative "whether" (→ no marker at all,
                  ordinary question), the fixed εἰ μή/ἐὰν μή idiom (→ `sai`/
                  `sai dai`, not decomposed), counterfactual (→ `da`, distinct
                  from `in`). ἐάν is mostly `in`+PAC, with indefinite readings
                  folding into PARTICIPLE_BLOCK's generic-relative machinery
                  and concessive readings taking `ko da yake`.
  NEGATION_BLOCK — Confirmed discontinuous `ba...ba`; separate existential
                  `babu`; separate discontinuous copular `ba [predicate] ba
                  ne/ce`; `kada` covers directive "don't" broadly (including
                  ἵνα μή/ὅπως μή purpose clauses, not just imperatives); οὐ μή
                  gets no special marking. οὐκέτι/μηκέτι is NOT a discontinuous
                  `ba...kuma ba` (a wrong original guess) — it's ordinary
                  negation plus a separate iterative/continuative AUXILIARY
                  VERB (`ƙara` majority, but `daina`/`ci gaba da`/`taɓa`/`sāke`
                  all real) — a 3-way split record, not a single word.

AUTOS_BLOCK and VERBAL_ASPECT_BLOCK are imported unchanged from eng.py — αὐτός
is fully covered by the PAC rule in BASE_BLOCK (an explicit pronoun, including
αὐτός, aligns primary to whatever carries person — see PRONOUNS AND THE
PERSON-ASPECT COMPLEX), and VERBAL_ASPECT's generic rule (both aspect element
and main verb primary when a translator renders aspect explicitly) already
matches the PAC+verb-stem pattern with no Hausa-specific addition needed.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import (
    AUTOS_BLOCK,
    VERBAL_ASPECT_BLOCK,
)


# ---------------------------------------------------------------------------
# Hausa-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied prepositions, morphologically-implied pronouns, fused affixes, and context-implied linking morphemes. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Create separate records whenever source tokens can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (PAC particle, fused definite/construct suffix, fused possessive suffix, modal helpers) are secondary to the source token whose grammar requires them, OR primary in their own record when a real source token exists for them to correspond to — see PRONOUNS below for the general rule. NEQ is for words with no source-language grammatical anchor at all, not a default for "the target marks this some other way too."

## TOKEN ROLES

primary — direct lexical/semantic connection to the Greek token
secondary — exists only because of the Greek token's morphology (person, number, case, aspect, voice); no separate Greek word
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

## PRONOUNS AND THE PERSON-ASPECT COMPLEX (PAC)

Hausa has no bare finite verb inflected for person — a preverbal particle (the PAC) fuses subject pronoun + tense/aspect/mood into one word: `ya`/`ta` (3sg completive), `muka`/`suka` (1pl/3pl completive-relative), `zai`/`za su` (future), `ana`/`ake` (continuous, independent/relative), `an`/`aka` (impersonal completive — see PASSIVE VOICE). A SEPARATE subjunctive PAC paradigm (`in`/`ka`/`ta`/`yă`/`mu`/`su`) is used in purpose/complement clauses — see HINA CLAUSES and INFINITIVAL CONSTRUCTIONS.

- No explicit Greek pronoun (person marked only by verb morphology): the PAC particle is SECONDARY, in the same record as the verb stem (primary) — exactly the "subject pronoun from verb ending" case.
  ἐφύτευσεν → "ya yi shuki": source=[ἐφύτευσεν], target=["ya", "yi", "shuki"] — primary: "yi", "shuki"; secondary: "ya"

- Explicit Greek nominative pronoun (ἐγώ/σύ/αὐτός/ἡμεῖς/ὑμεῖς) present: it is a genuine lexical correspondent, NOT a "supplied word" case — align it PRIMARY, in its OWN record, to the PAC particle (or the independent pronoun in an equational clause — see COPULA), while the verb stem separately aligns primary to the verb. Same shape as English ἐγώ→"I"/εἰμί→"am" splitting into two primary records. Do not default this to NEQ.
  αὐτοὶ οὐ συνῆκαν → "ba su fahimci... ba": source=[αὐτοί], target=["su"] — primary 1:1; source=[συνῆκαν], target=["fahimci"] — primary 1:1 (negation particles their own record — see NEGATION)
  Αὐτὸς... ἔλαβεν → "Ya ɗebi...": source=[Αὐτός], target=["Ya"] — primary 1:1 (no extra emphatic word for syntactically-emphatic αὐτός); source=[ἔλαβεν], target=["ɗebi"] — primary 1:1

- Contrastive/topicalized fronting (Greek μέν...δέ or a clear "I...but you..." contrast): an ADDITIONAL fronted independent pronoun aligns primary to the explicit Greek pronoun, in its own record; the ordinary PAC on the verb still gets the secondary-to-verb treatment above (its explicit-pronoun slot is already spoken for).
  ἡμεῖς δὲ κηρύσσομεν → "amma mu, muna wa'azin...": source=[ἡμεῖς], target=["mu"] — primary 1:1 (fronted, own record); source=[κηρύσσομεν], target=["muna", "wa'azin"] — primary: "wa'azin"; secondary: "muna"

- Equational/nominal clauses (no finite verb) use the INDEPENDENT pronoun directly, not a PAC particle — see COPULA. ἐγώ εἰμι ὁ ἄρτος → "Ni ne burodin rai": source=[ἐγώ], target=["Ni"] — primary 1:1; source=[εἰμι], target=["ne"] — primary 1:1

- Possessive pronouns are fused suffixes on the host noun (`almajiransa` = "disciples"+"his") — not a separately alignable token; treat as part of the noun's own record, same as a fused article/construct suffix (see ARTICLES AND DEFINITENESS, GENITIVE/POSSESSION).

- Object pronouns ARE separate, space-delimited tokens (`haife ni` "bore me", `tambaye su` "asked them") — align them normally/primarily to the Greek accusative/dative object pronoun; do not treat as fused.

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty, and never use it just because a grammaticalized target feature is marked some other way too (see PRONOUNS above).
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

A fused Hausa suffix (definite/construct `-n`/`-r`, possessive pronoun) is NEVER NEQ — it is either secondary within the host noun's own record (plain definiteness case) or simply absent as its own alignable unit when doing construct-state/genitive linking work (see ARTICLES AND DEFINITENESS). Discourse particles (`fa`, `kuwa`, `dai`) are frequently legitimate NEQ on the target side — see CONJUNCTIONS AND PARTICLES.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES AND DEFINITENESS

Hausa marks definiteness with a fused `-n`/`-r` suffix on the noun (`mutumin` "the man," `taron` "the crowd") — never a separate token. This suffix has TWO triggers sharing one form:

- **Plain definiteness** on a bare noun with nothing following it, correlating loosely with a Greek article on a concrete, previously-mentioned count noun: `taron` for τὸν ὄχλον. Greek article aligns SECONDARY within the noun's own record (primary) — the fused-morpheme generalization of the ordinary article rule, not NEQ.
- **Obligatory "linked state" before ANY following complement** — a genitive noun, a possessive suffix, or even a relative clause — regardless of whether Greek has an article at all: `mulkin Allah` ("kingdom of God"), `almajiransa` ("his disciples"), `begen da muka ce...` ("the hope that we..."). This is syntactically triggered, not a definiteness marker in the Greek/English sense — a Greek article here should default to NEQ; its function is absorbed by the construct/possessive construction, not recoverable from the suffix.
  τὴν βασιλείαν τοῦ θεοῦ → "mulkin Allah": source=[τήν] → NEQ; source=[βασιλείαν], target=["mulki", "-n"] — primary 1:1 (fused suffix not separately alignable); source=[θεοῦ], target=["Allah"] — primary 1:1

Proper nouns/unique referents (`Allah`, personal names) and collective/kinship/abstract-mass nouns (`Al'ummai` "Gentiles," `'yan'uwa` "brothers," `fasikanci` "sexual immorality") regularly appear BARE even with a Greek article — Greek article → NEQ (no fused marker present at all in these cases).

## GENITIVE / POSSESSION

Beyond simple `-n`/`-r`-vs-`na`/`ta` linking (see ARTICLES AND DEFINITENESS), the genitive's Hausa strategy tracks its SEMANTIC type:

- Free `na`/`ta` linker: used instead of stacking a further fused suffix when the head noun is already complex (contains its own fused genitive or `mai`-construction — see PARTICIPIAL CONSTRUCTIONS), or for partitive/measure genitives ("a measure of nard" → `wajen awo... na nardi`).
- Prepositional `ga` ("to/for"): objective/goal genitives — the genitive is the target of the head noun, not its possessor (`ἐλπίδα ζωῆς` → `begen... ga rai madawwami`, "hope for eternal life").
- Restructuring into a relative/finite clause with the genitive noun promoted to SUBJECT: genitive-of-agent/source constructions (an abstract action-noun + who performs it) — `διδασκαλίαις δαιμονίων` ("teachings of demons") → `abubuwan da aljanu suke koyarwa` ("things that demons are teaching"); `παρουσίᾳ κυρίου` ("coming of the Lord") → a temporal clause, `sa'ad da Ubangijimmu... ya dawo`.
- Restructuring into a prepositional adjunct inside a relative clause: genitive-of-instrument/location — `ἔργοις χειρῶν` ("works of hands") → `abin da suka ƙera da hannuwansu` ("what they made WITH their hands").
- Restructuring into a relative clause or plain adjective: the Hebraic/attributive genitive ("hearer of forgetfulness" = "forgetful hearer") — `ἀκροατὴς ἐπιλησμονῆς` → `mai ji ne kawai yă mance` ("just a hearer who forgets").
- Lexicalized/idiomatic substitution, no linking construction at all: ethnonym genitives → an appositive adjective (`Χριστοῦ Ναζωραίου` → `Yesu Kiristi Banazare`); fixed idioms get their own Hausa idiom (`αἰῶνας αἰώνων` → `har abada abadin`; `διαιρέσεις διακονιῶν` → `hidimomi iri-iri`).
- Elliptical kinship genitives get an explicit relationship noun supplied: `Μαρία Ἰωσῆτος` ("Mary of Joses") → `Maryamu uwar Yusuf` ("Mary, mother of Joseph," `uwa` "mother" supplied).
- Fused chains stack freely with no special handling: `κλεὶς φρέατος τῆς ἀβύσσου` → `mabuɗin ramin Abis` (two fused links).

## COPULA / "BE"

Five distinct strategies, chosen by FUNCTION, not by whether Greek's εἰμί is morphologically present:

- Identity/classification ("X is Y", noun=noun) → `ne`/`ce` (gender-agreeing: `ce` feminine singular, `ne` elsewhere/default/plural). TENSELESS — the same word regardless of whether Greek's copula is present, past, or embedded in reported speech/an infinitive. Ἐγώ εἰμι → "Ni ne"; ἦν... οὗτος (past) → "wannan Ɗan Allah ne".
- Existential "there is/was" → `akwai` (positive) / `babu` (negative) — a completely separate system, matching NEGATION's existential rule. Ἦν δέ τις μαθητής → "akwai wani almajiri".
- Locative/prepositional-phrase predicates ("X is in/with/among Y", "where is X") → the bare relative-continuous PAC (`yake`/`suke`/`take`), NOT `ne`/`ce`. Ποῦ ἐστιν ἐκεῖνος → "Ina mutumin yake".
- Future "will be" (any predicate) → `zama` ("become") or `kasance` ("remain/be") + future PAC, never `ne`/`ce`. ἔσομαι αὐτοῖς εἰς θεόν → "Zan zama Allahnsu".
- Predicate-adjective "be", especially with modal/necessity framing → `kasance`/`zama` + adjective. εἴ τίς ἐστιν ἀνέγκλητος → "Dole dattijo yă kasance marar aibi".
- The formulaic ὅ ἐστιν ("which is...") explanatory gloss → the dedicated marker `wato` ("that is to say"), not `ne`/`ce` or a relative clause. ὅ ἐστιν ῥῆμα θεοῦ → "wato, Maganar Allah".

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

Discourse/emphatic particles `fa`, `kuwa`, `dai` are frequent (kuwa alone in over 1,000 verses) and only loosely, inconsistently correlated with any single Greek connective (occasionally δέ) — very often they have NO Greek correlate at all. Treat as legitimate target-side NEQ by default; only align to a Greek particle when there's a plausible direct correlate. `dai` frequently pairs with `sai` for the CONDITIONAL BLOCK's εἰ μή/ἐὰν μή exceptive idiom.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

Eight real, coexisting strategies — impersonal marking is the single largest but is NOT a majority on its own (≥40-48% of passive-verb verses at most). Determine which the translator used per verse; do not assume one default.

### 1. Impersonal an/aka/ana/ake/akan/bare a — the largest single strategy
`an`/`ana` mark independent-clause completive/continuous impersonal; `aka`/`ake` the relative/subordinate-clause forms; bare `a` is non-completive (future/subjunctive); `akan` is habitual. Impersonal marker secondary to the verb (its own record, verb primary).
  ἐτύθη → "an miƙa Kiristi": source=[ἐτύθη], target=["an", "miƙa", "Kiristi"] — primary: "miƙa"; secondary: "an" ("Kiristi" its own record)

### 2. Unmarked lexical intransitive/ambitransitive verb choice
Many Hausa verbs are ambitransitive or have a natural intransitive counterpart; the translator picks that frame with zero passive marking. Lexically conditioned per Greek verb (πληρόω-family reliably → `cika` "be full/complete").
  κατεκάη → "ya ƙone" ("burned," intransitive): source=[κατεκάη], target=["ya", "ƙone"] — primary: "ƙone"; secondary: "ya" (PAC rule)

### 3. Light-verb (yi/sha/kai/cika da) + abstract noun — a MAJOR strategy, not a one-verb quirk
Dominant for psychological/relational/experiential passive verbs (astonish, err, reconcile, suffer, be saved, submit).
  σωθήσεται → "zai sami ceto": source=[σωθήσεται], target=["zai", "sami", "ceto"] — primary: "sami", "ceto"; secondary: "zai"
  ἐξεπλάγησαν → "suka yi mamaki": source=[ἐξεπλάγησαν], target=["suka", "yi", "mamaki"] — primary: "yi", "mamaki"; secondary: "suka"

### 4. Agent promotion to active subject
Used when the (explicit or contextually implicit) agent is nameable. A SPECIAL and common subtype: implicit-agent ("divine passive") verbs get `Allah` supplied as an explicit active subject — expect this even with no Greek subject token to anchor it to (source empty, target=["Allah", ...], or NEQ the supplied "Allah" if no other anchor is plausible).
  ἐλαλήθη (no stated agent) → "Allah ya ce masa": target "Allah" and PAC "ya" as a pair with no clean single Greek anchor — prefer NEQ for "Allah" specifically if the verse gives no other basis; align "ya ce" to ἐλαλήθη normally.
  ἐμαρτυρεῖτο ὑπὸ τῶν ἀδελφῶν → "Yan'uwa... sun yi magana mai kyau": source=[ἀδελφῶν], target=["Yan'uwa"] — primary 1:1 (agent promoted to subject); source=[ἐμαρτυρεῖτο], target=["sun", "yi", "magana", "mai", "kyau"] — primary: "yi", "magana", "kyau"; secondary: "sun"

### 5. Stative "a" + deverbal adjective + copula (perfect/resultative aspect)
γέγραπται is the clearest and most frequent case, but the construction is productive beyond it (confirmed with ἐφρουρούμεθα → `a daure`).
  γέγραπται → "a rubuce yake": source=[γέγραπται], target=["a", "rubuce", "yake"] — primary: "rubuce"; secondary: "a", "yake"

### 6. Nominalization: "become/have" + noun/adjective
The verb carrying voice information disappears entirely into `zama`/`yana da` + a noun/adjective complement.
  τετελείωται → "ta zama cikakkiya": source=[τετελείωται], target=["ta", "zama", "cikakkiya"] — primary: "cikakkiya"; secondary: "ta", "zama"

### 7. Full restructuring/omission — legitimate NEQ/idiom territory
No verbal correspondent at all; expect this, don't force an alignment.
  καλεῖται (ἥτις καλεῖται Βηθλέεμ, "which is called Bethlehem") → simple apposition with no "called" verb at all in the Hausa — καλεῖται → NEQ.

### 8. Grade 7 -u reflexive/passive-like forms — real but narrow, do not hunt for it
Only two confirmed instances (`raba`→`rabu`, "divide"→"become divided"). Treat as an ordinary lexical item within strategy 2, not a named category.\
"""

IMPERSONAL_BLOCK = """\
## IMPERSONAL VERBS

δεῖ/ἔξεστιν/πρέπει/συμφέρει/δοκεῖ frequently collapse into a PLAIN finite clause with NO necessity/propriety marker at all — do not force a "dole"/"ya kamata" word into every instance.
  τί με δεῖ ποιεῖν → "me zan yi": source=[δεῖ], target=[] → NEQ or leave unrecorded; ποιεῖν aligns to "yi" normally; no separate necessity word present

When a necessity/propriety word IS present, it is `dole` (necessity, often with `kasance` "be" — see COPULA) or `ya kamata` ("it is fitting/one ought"), both primary to the impersonal verb.
  δεῖ ἐν οἴκῳ θεοῦ ἀναστρέφεσθαι → "ya kamata mutane su tafiyar da halayensu... a cikin jama'ar Allah": source=[δεῖ], target=["ya", "kamata"] — primary 1:1; the infinitive complement aligns via its own subjunctive-PAC serial chain (see INFINITIVAL CONSTRUCTIONS)

Complementary infinitive after δεῖ/ἔξεστιν follows the same subjunctive-PAC serial-chain pattern as ordinary modal complements (see INFINITIVAL CONSTRUCTIONS) — it does not get a distinct treatment just because the governing verb is impersonal.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adverbial (circumstantial)
Introductory conjunction/adverb secondary; PAC particle follows the ordinary rule in PRONOUNS AND THE PERSON-ASPECT COMPLEX.
  ἀκούσας → "da ya ji": source=[ἀκούσας], target=["da", "ya", "ji"] — primary: "ji"; secondary: "da", "ya"

### Substantive — nine coexisting strategies
Determine which the translator used; do not assume `wanda` is the only option.

1. **`wanda`/`wadda`/`waɗanda` headless relative pronoun** (largest single strategy) — used when the clause has NO overt head word for the participle to attach to.
   ὁ πιστεύων → "wanda ya gaskata": source=[ὁ, πιστεύων], target=["wanda", "ya", "gaskata"] — primary: "gaskata"; secondary: "wanda", "ya"
2. **`da`-relative attached to an overt head** (noun/pronoun/demonstrative) — the second most common strategy, chosen when the translation DOES supply a head word. Same Greek construction as #1; the difference is purely how the translator phrased it.
   τοὺς πεπιστευκότας αὐτῷ Ἰουδαίους → "Yahudawan da suka gaskata da shi": head noun "Yahudawan" primary to Ἰουδαίους; "da suka gaskata" secondary/primary per the participle's own content, following the relative-clause pattern
3. **`mai`/`masu` agentive** — for ongoing role/occupation/characteristic senses (reaper, sower, believer, rider). Distinguish from lexicalized `ma`-prefix nouns (`magina` "builders," `masoyi` "lover") which are ordinary vocabulary, not a live construction.
   ὁ θερίζων → "mai girbi": source=[ὁ, θερίζων], target=["mai", "girbi"] — primary: "girbi"; secondary: "mai"
4. **Generic/gnomic "whoever"**: `duk`+`wanda`/`mai`, or bare `Kowa`.
   ὁ ὀργιζόμενος → "duk wanda ya yi fushi": primary "yi", "fushi"; secondary "duk", "wanda", "ya"
5. **Cleft/focus with bare `yake`/`suke`**, no relative marker at all — concentrated in "it is God who..." identity-claim contexts.
   τὸ ζῳοποιοῦν (Πνεῦμά ἐστιν τὸ ζῳοποιοῦν) → "Ruhu ne yake ba da rai": "Ruhu" + "ne" its own identity record (see COPULA); [ζῳοποιοῦν]→["yake", "ba", "da", "rai"] — primary: "ba", "rai"; secondary: "yake", "da"
6. **Privative `mara-`/`marar-`/`marasa`** ("lacking X") for participles/adjectives expressing a negative characteristic, not a relative clause.
   ὁ ἀσθενῶν → "marar ƙarfi": source=[ἀσθενῶν], target=["marar", "ƙarfi"] — both primary
7. **Naming-idiom `(ake) kira X`** for λεγόμενος/καλούμενος specifically ("the place/thing called X").
   τὴν λεγομένην → "ake kira": source=[λεγομένην], target=["ake", "kira"] — primary: "kira"; secondary: "ake"
8. **Lexicalized deverbal noun** (`haifaffe` "born-one") — real but narrow; treat as vocabulary.
9. **Full restructuring/omission** — a non-trivial fraction (~9%+), legitimate NEQ/idiom territory. A substantive-participle title collapsing into a plain finite clause, or a circumstantial-temporal participle becoming a plain adverbial — do not force a participle-shaped record onto these.

### Discourse particle adjacent to participle
δέ/καί/οὖν near participle with no correspondent → NEQ source (only when certain).\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

No infinitive form exists — the record shape is determined by syntactic function.

### Modal/phase complement (θέλω, δύναμαι, μέλλω, ἄρχομαι, δεῖ, ὀφείλω, βούλομαι, ζητέω, κελεύω, ἔξεστι(ν), ἰσχύω)
Overwhelmingly a serial-verb chain: the modal verb takes its own PAC, and the complement verb takes a DISTINCT SUBJUNCTIVE PAC (`in`/`ka`/`ki`/`ta`/`yă`/`mu`/`ku`/`su`) — not the ordinary indicative PAC from PRONOUNS AND THE PERSON-ASPECT COMPLEX.
  ἠθέλησα ἐπισυναγαγεῖν → "na so in tattara": source=[ἠθέλησα], target=["na", "so"] — primary: "so"; secondary: "na"; source=[ἐπισυναγαγεῖν], target=["in", "tattara"] — primary: "tattara"; secondary: "in"
Real minority: nominalization into a verbal noun (`-wa`-suffixed) or an abstract noun (`niyya` "intention") as the modal verb's object.
  οὐ θέλει μετανοῆσαι → "ba ta da niyya": source=[μετανοῆσαι], target=["niyya"] — primary 1:1 (nominalized)
δεῖ frequently drops necessity-marking entirely — see IMPERSONAL VERBS.

### Purpose-function infinitive (bare complement, εἰς τό, πρός τό, τοῦ-genitive)
Unifies with ἵνα-purpose (HINA CLAUSES) and causal ὅτι (ὅτι block): `don`/`domin`/bare `saboda` + subjunctive PAC, or bare subjunctive chaining with no connector when purpose is contextually obvious.
  εἰς τὸ σωθῆναι αὐτούς → "don su sami ceto": source=[εἰς, τό], target=["don"] — primary 1:1; source=[σωθῆναι], target=["su", "sami", "ceto"] — primary: "sami", "ceto"; secondary: "su"

### ὥστε-result infinitive — three-way split
- Realized/actual result → `har`+indicative PAC, or unmarked indicative continuation with no connector.
  ὥστε βυθίζεσθαι αὐτά → "har jiragen suka fara nutsewa": source=[ὥστε], target=["har"] — primary 1:1
- Intended/purpose-like result → same `domin`/`don`/`saboda`+subjunctive family as ordinary purpose.
- Explicit causative → `ya sa` ("it caused") or `tilasta` ("force/compel") + finite complement.
  ὥστε ἐξαπορηθῆναι ἡμᾶς → "ya sa muka fid da tsammani": source=[ὥστε], target=["ya", "sa"] — primary 1:1

### Temporal/circumstantial articular infinitive (μετὰ τό, ἐν τῷ) — mostly RE-FINITIZES
Majority: an ordinary temporal subordinate clause, `bayan`/`da`/`sa'ad da`/`yayinda`+PAC+verb — NOT kept nominal.
  μετὰ τὸ ἐγερθῆναί με → "bayan na tashi": source=[μετά, τό], target=["bayan"] — primary 1:1; source=[ἐγερθῆναί], target=["na", "tashi"] — primary: "tashi"; secondary: "na"
Real minority: nominalization into a possessed verbal/deverbal noun.
  μετὰ τὸ παθεῖν αὐτὸν → "Bayan wahalarsa": source=[παθεῖν], target=["wahala", "-rsa"] — primary 1:1 (fused possessive, see PRONOUNS)

### Genitive infinitive complementing a noun ("opportunity to betray him")
Renders via the `da`-relative-clause-on-a-noun strategy (PARTICIPIAL CONSTRUCTIONS #2), not a nominal phrase.
  εὐκαιρίαν τοῦ παραδοῦναι αὐτὸν → "zarafin da zai ba da Yesu": head noun "zarafi" its own record; "da zai ba da Yesu" follows the da-relative pattern\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

Part of the SAME unified purpose/reason system as purpose-function infinitives (INFINITIVAL CONSTRUCTIONS) and causal ὅτι (ὅτι block) — `don`/`domin`/bare `saboda` + subjunctive PAC, or bare subjunctive chaining with no connector when purpose is contextually obvious. `kada` appears alongside or instead of `don`/`domin` when the purpose itself is negative.
  ἵνα πληρωθῇ → "don a cika": source=[ἵνα], target=["don"] — primary 1:1
  ἵνα Χριστὸν κερδήσω → "domin in sami Kiristi": source=[ἵνα], target=["domin"] — primary 1:1; source=[κερδήσω], target=["in", "sami", "Kiristi"] — primary: "sami", "Kiristi"; secondary: "in"
  ἵνα μὴ μωμηθῇ → "domin kada... ta zama": source=[ἵνα], target=["domin"]; source=[μή], target=["kada"] — both primary, separate records
  ἵνα πιάσωσιν αὐτόν (purpose obvious from context) → "su kama shi": source=[ἵνα], target=[] → no correspondent needed, do not force one; source=[πιάσωσιν], target=["su", "kama"] — primary: "kama"; secondary: "su"

When an ἵνα-clause blurs into result rather than pure intention, Hausa may restructure into an ordinary indicative statement with no purpose connector at all — treat ἵνα as NEQ in that case rather than forcing "don"/"domin" onto unrelated text.\
"""

COMPARATIVE_BLOCK = """\
## COMPARATIVES AND SUPERLATIVES

Six strategies, mostly built on the verb `fi` ("exceed/surpass") — determine which applies; do not assume a single `mafi`/`fiye da` default.

1. **Predicative comparison** ("X is more/-er than Y") — the verb `fi` governing the compared-to entity as its object, with the quality as a following noun: `[PAC] + fi + [compared entity] + [quality-noun]`. The majority strategy.
   μείζων Ἰωάννου → "ya fi Yohanna... girma": source=[μείζων], target=["ya", "fi", "girma"] — primary: "fi", "girma"; secondary: "ya"; source=[Ἰωάννου], target=["Yohanna"] — primary 1:1
   The genitive "than"-standard sometimes folds into the quality-noun itself: σοφώτερον τῶν ἀνθρώπων → "ta fi hikimar mutum" ("exceeds human wisdom") — both τῶν and ἀνθρώπων align within the "hikimar mutum" record.
2. **Attributive comparison** (modifying a noun directly) — prenominal `mafi` + adjective.
   μείζονος... σκηνῆς → "tabanakul mafi girma": source=[μείζονος], target=["mafi", "girma"] — both primary
   Real minority: a `da`-relative with an embedded `fi`-verb covers the same slot (see PARTICIPIAL CONSTRUCTIONS #2).
3. **Explicit binary "than"** — the grammaticalized preposition `fiye da`.
   φρονιμώτεροι ὑπὲρ τοὺς υἱοὺς τοῦ φωτός → "fiye da 'yan haske": source=[ὑπέρ], target=["fiye", "da"] — primary 1:1; source=[τοὺς υἱοὺς τοῦ φωτός], target=["'yan haske"] — primary 1:1
4. **Superlative-among-a-group** — `mafi` + adjective + `a`/`cikin` + [the group]. Greek's genitive-of-comparison converts to a partitive "among" phrase here, NOT to `fiye da`.
   μείζων ὑμῶν → "Mafi girma a cikinku": source=[μείζων], target=["Mafi", "girma"] — both primary; source=[ὑμῶν], target=["a", "cikinku"] — primary: "cikinku"; secondary: "a"
5. **Quantity/majority comparatives** ("more/most of X") — the dedicated noun `yawanci` ("majority"), not `fi`/`mafi`.
   πλείονας τῶν ἀδελφῶν → "yawancin 'yan'uwa": source=[πλείονας], target=["yawanci", "-n"] — primary 1:1
6. **Nominalized "have superiority over"** — a formal-register alternative built on `fifiko` ("superiority") + `a kan` ("over").
   κρείττων... γενόμενος τῶν ἀγγέλων → "yake da fifiko a kan mala'iku": source=[κρείττων], target=["fifiko"] — primary 1:1

Caveat: several comparative-morphology Greek-parallel words are lexicalized as ordinary nouns with no live comparison sense — πρεσβύτεροι ("elders") and the νεώτεροι-family ("younger men/widows" as an age-cohort label) get plain noun or `mai`-construction translations; πρότερον/προτέραν ("former/previously") is a temporal expression, not a degree comparison. Do not force a comparison strategy onto these.\
"""

HOTI_BLOCK = """\
## ὅτι

Causal ὅτι ("because") joins the SAME `don`/`domin`/`saboda` family used for ἵνα-purpose and ὥστε-result, plus a new member `gama` ("for") — NOT a separate causal-only marker.
  ζητεῖτέ με ἀποκτεῖναι ὅτι ὁ λόγος ὁ ἐμὸς οὐ χωρεῖ ἐν ὑμῖν → "...don maganata ba ta da wurin zama": source=[ὅτι], target=["don"] — primary 1:1
  Λεγιών, ὅτι εἰσῆλθεν δαιμόνια πολλὰ → "gama aljanu masu ɗumbun yawa ne suna cikinsa": source=[ὅτι], target=["gama"] — primary 1:1

Declarative ὅτι is a separate system:
- Introduces DIRECT quoted speech → NEQ (punctuation/quotation alone introduces it, matching the general project convention).
  εἶπεν αὐτοῖς ὅτι Οὐ χρείαν ἔχουσιν... → source=[ὅτι] → NEQ; quote follows with no complementizer
- Introduces an indirect/embedded factual complement (after verbs of knowing/saying/perceiving) — TWO real, coexisting strategies, not a strict rule: explicit `cewa` ("that"), or bare PARATACTIC complementation with no connecting word at all.
  Οἴδαμεν ὅτι καλὸς ὁ νόμος → "Mun san cewa doka tana da kyau": source=[ὅτι], target=["cewa"] — primary 1:1
  οἶδα ὅτι σπέρμα Ἀβραάμ ἐστε → "Na dai san ku zuriyar Ibrahim ne": source=[ὅτι], target=[] → no correspondent, do not force "cewa"
- Occasionally recast with `yadda` ("how") when coordinated with a preceding "how"-clause, or recast into the causal `don`/`domin`/`saboda` family when the translator reads the complement as reason-giving rather than fact-reporting — a genuine translation-level blur, not an error to correct against.\
"""

CONDITIONAL_BLOCK = """\
## CONDITIONAL CONSTRUCTIONS

εἰ has FOUR distinct functions — only one is an ordinary conditional. Do not map εἰ→one word and ἐάν→another; both converge on the same strategy for genuine open conditionals.

1. **Genuine real/open conditional** → `in` + PAC, same as ἐάν.
   εἰ σὺ οὐ εἶ ὁ χριστός → "in kai ba Kiristi ba ne": source=[εἰ], target=["in"] — primary 1:1
2. **Interrogative "whether"** (embedded or direct yes-no questions — not conditional at all) → NO conditional marker; rendered as an ordinary question.
   ἐπηρώτων αὐτὸν εἰ ἔξεστιν → source=[εἰ] → NEQ or unrecorded; the clause becomes a plain question
3. **The fixed εἰ μή/ἐὰν μή idiom** ("except/only"/"unless") → the dedicated exceptive particle `sai`/`sai dai`, NOT decomposed into "if"+"not."
   οὐ... εἰ μὴ ὁ ἀλλογενὴς → "Ba wanda... sai dai wannan baƙon": source=[εἰ, μή], target=["sai", "dai"] — both primary, treated as one idiom unit
4. **Counterfactual/irrealis** → `da` (NOT `in`) — semantically driven, not tied to either Greek form; a single verse can mix `in` (ordinary) and `da` (counterfactual) across two clauses on the same construction.
   εἰ ἐμὲ ᾔδειτε... ἄν ᾔδειτε → "Da kun san ni, da za ku san Ubana ma": source=[εἰ], target=["Da"] — primary 1:1

ἐάν overwhelmingly renders as `in`+PAC (`sai in` for the ἐὰν μή "unless" idiom). Real minority patterns: indefinite/generic ἐάν (ἐάν τις, "if anyone...") restructures into PARTICIPIAL CONSTRUCTIONS' generic-relative strategies (`duk wanda`, `kome` "whatever") rather than staying an `in`-conditional; a concessive-flavored ἐάν gets its own marker, `ko da yake` ("even though"), distinct from ordinary `in`.
  ἐάν τις γνῷ → "duk wanda ya san": source=[ἐάν, τις], target=["duk", "wanda"] — primary 1:1
  Ἐὰν ᾖ ὁ ἀριθμὸς... ὡς ἡ ἄμμος → "Ko da yake yawan Isra'ilawa yana kama da yashi": source=[ἐάν], target=["Ko", "da", "yake"] — primary 1:1\
"""

NEGATION_BLOCK = """\
## NEGATION

### Standard verbal negation — discontinuous ba...ba
οὐ/οὐκ/οὐχ/μή → the circumfix `ba...ba`, both particles primary, wrapping the predicate (verb its own record between them).
  ba ku da gidajen → source=[οὐ], target=["ba", "ba"] — both primary; the verb/predicate is its own record in between. PAC forms routinely contract with the leading `ba` (`bai`=ba+ya, `ban`=ba+na).

### Existential negation — babu
A distinct strategy from verbal `ba...ba`, for "there is/are not."
  οὐ ἔστιν ποιῶν χρηστότητα → "babu wani mai aikata nagarta": source=[οὐ, ἔστιν], target=["babu"] — both primary, one record

### Copular/predicate-nominal negation — ba [predicate] ba ne/ce
Its own discontinuous pattern — the circumfix wraps the predicate, and the copula particle (see COPULA) is retained after the closing `ba`.
  ἐλπὶς... οὐ ἔστιν ἐλπίς → "ba bege ba ne sam": source=[οὐ], target=["ba", "ba"] — both primary; source=[ἔστιν], target=["ne"] — primary 1:1

### Directive negation — kada
Covers any directive/purposive "don't," INCLUDING μή/ἵνα μή/ὅπως μή in subordinate purpose clauses — not just true 2nd-person imperatives.
  Μὴ ἐρεθίζετε → "kada ku matsa...": source=[μή], target=["kada"] — primary 1:1
  ἵνα μὴ ἀθυμῶσιν → "don kada su fid da zuciya": source=[μή], target=["kada"] — primary 1:1
Declarative/conditional μή-subjunctive (no directive force) uses plain `ba`, NOT `kada`: ἔργα δὲ μὴ ἔχῃ → "ba shi da ayyuka".
Interrogative μή (rhetorical "surely not") uses neither — a separate rhetorical-question particle, `Ashe`.

### Emphatic negation (οὐ μή) — no dedicated marking
Renders as ordinary negation with no intensifier — do not expect or force a distinct "emphatic" word.
  οὐ μὴ γεύσωνται θανάτου → "ba za su ga mutuwa ba": source=[οὐ, μή], target=["ba", "ba"] — both primary, same as plain negation

### οὐκέτι/μηκέτι ("no longer") — NOT a discontinuous ba...kuma ba
Ordinary negation (`ba...ba`/`kada`) PLUS a separate iterative/continuative AUXILIARY VERB — a 3-way split record (negation + auxiliary + main verb), not a single word. `ƙara` ("add/increase") is the closest to a default (~half of instances), but `daina` ("stop"), `ci gaba da` ("continue with"), `taɓa` ("ever"), and `sāke` ("repeat/again") are all real, coexisting alternatives — do not hardcode one.
  οὐκέτι δύναμαι...ποιῆσαι → "ba... ƙara... ba": source=[οὐκέτι], target=["ba", "ƙara", "ba"] — all primary, non-adjacent (the main verb is a separate record in between)\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

BLOCK_ORDER = [
    "PASSIVE",
    "IMPERSONAL",
    "PARTICIPLE",
    "INFINITIVE",
    "HINA",
    "COMPARATIVE",
    "AUTOS",
    "HOTI",
    "CONDITIONAL",
    "NEGATION",
    "VERBAL_ASPECT",
]

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PASSIVE":        PASSIVE_BLOCK,
    "IMPERSONAL":     IMPERSONAL_BLOCK,
    "PARTICIPLE":     PARTICIPLE_BLOCK,
    "INFINITIVE":     INFINITIVE_BLOCK,
    "HINA":           HINA_BLOCK,
    "COMPARATIVE":    COMPARATIVE_BLOCK,
    "AUTOS":          AUTOS_BLOCK,
    "HOTI":           HOTI_BLOCK,
    "CONDITIONAL":    CONDITIONAL_BLOCK,
    "NEGATION":       NEGATION_BLOCK,
    "VERBAL_ASPECT":  VERBAL_ASPECT_BLOCK,
}

FORCED_INCLUSIONS: dict[str, set[str]] = {
    "PASSIVE":     {"IMPERSONAL"},
    "HINA":        {"INFINITIVE"},
    "CONDITIONAL": {"PARTICIPLE"},
}

HAU_CONFIG = LanguagePromptConfig(
    language_code="hau",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(HAU_CONFIG)
