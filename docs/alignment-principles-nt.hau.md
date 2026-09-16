# Alignment Principles — Hausa (hau), New Testament

Guidelines used by `refine-alignment` when aligning the Open Hausa Contemporary
Bible (OHCB) against the Greek New Testament (SBLGNT) source.

Sections marked **[hau]** contain Hausa-specific rules or examples. Unmarked
sections are shared with the English guidelines (`alignment-principles-nt.md`
and `prompt/nt/eng.py`).

Examples are grounded in `data/targets/OHCB/nt_OHCB.tsv` checked against the
Greek source TSV (`data/sources/SBLGNT.tsv`). Every construction below was
checked at full-corpus or large-random-sample scale (sample sizes given per
section) — this document was built entirely from raw text plus linguistic
reasoning, the same methodology used to rebuild `nt/zht.py`, rather than from
any pre-existing alignment (see the Cross-translation methodology note near
the end for why an existing UBS manual alignment was examined and rejected).
No second, independently-translated complete Hausa NT was available for
cross-checking the way fra/ind/hin/arb had one — this is the single biggest
methodological gap relative to those configs, and the main reason this
document is a **draft, not yet reviewed by a native Hausa speaker.**

Source files: `src/text_align/refine/prompt/nt/hau.py`,
`src/text_align/refine/prompt/nt/eng.py`

## Key differences from every currently-supported language

- **The Person-Aspect Complex (PAC)**: Hausa has no bare finite verb inflected
  for person. A single preverbal particle fuses subject pronoun + tense/
  aspect/mood into one word (`ya`, `muka`, `zai`, `ana`, `an`...). This is the
  single most alignment-relevant fact about Hausa, and the closest analogue is
  not any other supported language's mechanism but rather the *rule* English's
  own principles document already states for "subject pronoun from verb
  ending" (§8.1/§8.4 of `alignment-principles-nt.md`) — the PAC is that
  phenomenon realized as an obligatory fused particle rather than an
  occasional supplied word. See PRONOUNS AND THE PERSON-ASPECT COMPLEX.
- **Definiteness is a fused `-n`/`-r` suffix**, structurally like Arabic's
  fused `ال-` — never a separate token — but with a second, syntactically-
  triggered function (construct/"linked" state before any complement) that
  interacts directly with genitive marking. See ARTICLES AND DEFINITENESS and
  GENITIVE / POSSESSION.
- **A five-way copula system** split strictly by function (identity/
  existence/location/future/gloss), not by whether Greek's own εἰμί is
  morphologically present. See COPULA / "BE".
- **Passive voice has eight coexisting strategies**, the largest of which
  (impersonal `an`/`aka`/`ana`/`ake`) still falls short of a majority — richer
  and more evenly distributed than any other currently-supported language's
  passive system. See PASSIVE VOICE.
- **Substantive participles split nine ways**, with the second-most-common
  strategy (a `da`-relative clause attached to an overt head word) entirely
  unanticipated going in — the choice between it and the headless `wanda`-
  pronoun strategy tracks how the translator phrased the sentence, not
  anything in the Greek. See SUBSTANTIVE PARTICIPLES.
- **No infinitive at all**, and unlike every other non-infinitive language
  in this project, the record shape is governed almost entirely by syntactic
  *function* rather than one or two defaults: modal complements get a serial-
  verb chain built on a SECOND, distinct subjunctive PAC paradigm; purpose
  infinitives of every syntactic type collapse into the same word family as
  ἵνα-purpose and causal ὅτι; temporal articular infinitives mostly
  re-finitize into ordinary subordinate clauses. See INFINITIVAL
  CONSTRUCTIONS.
- **Purpose (ἵνα), causal ὅτι, and much of ὥστε-result share one word
  family** (`don`/`domin`/`saboda`/`gama`) — a considerably bigger unification
  across the reason/purpose/result system than any other language config in
  this project has found.
- **Comparison runs on one verb, `fi`** ("exceed"), realized four different
  ways depending on whether the comparison is predicative, attributive,
  explicitly binary ("than"), or superlative-among-a-group.

## PRONOUNS AND THE PERSON-ASPECT COMPLEX (PAC) — [hau]

Verified against 40 random verses (finite-verb / explicit-nominative-pronoun
co-occurrence) plus a targeted sample of 18 of the 957 NT verses containing an
explicit Greek nominative personal pronoun (ἐγώ/σύ/αὐτός/ἡμεῖς/ὑμεῖς)
alongside a finite verb.

The PAC particle appears in Hausa regardless of whether Greek has an explicit
subject pronoun — every sampled verse with a Greek finite verb and no explicit
pronoun still showed the expected PAC form (ἐφύτευσεν/ὤρυξεν/ᾠκοδόμησεν, "he
planted/dug/built," no pronoun, Matt 21:33 → `ya yi`/`ya haƙa`/`ya gina`;
παρεκάλεσα, "I begged," 2 Cor 12:8 → `na roƙi`). This is the same phenomenon
`alignment-principles-nt.md` §8.1/§8.4 already names "subject pronoun from
verb ending" and treats as **secondary** to the verb's own record, one
record — not a separate 0:1 or N:1-both-primary pattern. Applied to Hausa:
**Greek verb (1) → Hausa PAC (secondary) + verb-stem (primary)**, one record,
when Greek marks person only via verb morphology.

When Greek *does* have an explicit nominative pronoun, that pronoun is a
genuine lexical correspondent, not a "supplied word" case — the generous-
alignment principle (§2.1) applies directly: the PAC particle aligns
**primary**, in its own record, to the explicit Greek pronoun, exactly the way
ἐγώ→"I"/εἰμί→"am" splits into two primary records in English; the verb stem
separately aligns primary to the verb.
  αὐτοὶ οὐ συνῆκαν → `ba su fahimci... ba` (Mark 6:52): αὐτοί→`su` primary,
  own record; συνῆκαν→`fahimci` primary, own record.
  ὑμεῖς οὐ πιστεύετε → `ba ku gaskata ba` (John 10:26): ὑμεῖς→`ku`;
  πιστεύετε→`gaskata`.
  Αὐτὸς τὰς ἀσθενείας ἡμῶν ἔλαβεν → `Ya ɗebi rashin lafiyarmu` (Matt 8:17):
  Αὐτός→`Ya` (no extra emphatic word, even for this syntactically-emphatic
  αὐτός); ἔλαβεν→`ɗebi`.

**Exception — contrastive/topicalized fronting** (Greek μέν...δέ, or a clear
"I...but you..." discourse contrast): an ADDITIONAL fronted independent
pronoun aligns primary to the fronted Greek pronoun, in its own record; the
ordinary PAC on the verb then falls back to the secondary-to-verb pattern,
since the explicit-pronoun slot is already filled by the fronted word.
  ἡμεῖς δὲ κηρύσσομεν (Ἰουδαίοις μέν... ἔθνεσιν δέ) → `amma mu, muna
  wa'azin...` (1 Cor 1:23): independent `mu` fronted, primary, own record;
  ordinary continuous PAC `muna` secondary to the verb `wa'azin`.
  Ἐγὼ δὲ καὶ γεγέννημαι (Paul contrasting with the previous speaker's Ἐγώ) →
  `Ni kuwa an haife ni...` (Acts 22:28): independent `Ni` + contrastive
  particle `kuwa` fronted; the passive verb itself uses the impersonal `an`
  strategy (see PASSIVE VOICE).

**Equational/nominal clauses** (no finite verb) use the independent pronoun
directly, since there is no verb to host a PAC — a clean, ordinary 1:1
correspondent: ἐγώ εἰμι ὁ ἄρτος → `Ni ne burodin rai` (John 6:35, `Ni`
independent + `ne` copula — see COPULA); Σὺ εἶ ὁ υἱός μου → `Kai ne Ɗana`
(Mark 1:11).

**Possessive pronouns are fused suffixes on the host noun** — `almajiransa`
("his disciples" = `almajirai` + `-nsa`), `gaskiyarmu` ("our truth" = `gaskiya`
+ `-rmu`) — not a separately alignable token; treat the same way Arabic's
pronominal suffixes are treated, folded into the noun's own record.
**Object pronouns after a verb ARE separate, space-delimited tokens** —
`haife ni` ("bore me"), `tambaye su` ("asked them") — contra Indonesian's
fused `-ku`/`-mu`/`-nya`; align them normally/primarily.

## ARTICLES AND DEFINITENESS — [hau]

Verified against 25 sampled verses from 13,909 candidate Greek article+noun
sequences.

Hausa marks definiteness with a bound `-n` (masc./default) or `-r` (fem.)
suffix that is fused into the host word's spelling: `mutumin` ("the man,"
Luke 8:38), `taron` ("the crowd," Acts 14:14), `kifayen` ("the fish," Matt
15:36) are each single tokens in `nt_OHCB.tsv`. There is structurally no
separate target token available for a Greek article to align to when this
suffix is present — the same situation as Arabic's fused `ال-`, except this
suffix forms the whole noun's grammatical "state" rather than prefixing.

This one surface form has (at least) two distinct triggers — a genuine Hausa
"absolute state vs. linked state" alternation, not two separate morphemes:

- **Plain definiteness** on a bare noun with nothing following it: `taron`
  (no genitive/relative complement, Acts 14:14); `kifayen nan` ("these
  fish," reinforced by the demonstrative `nan`, Matt 15:36). Correlates
  loosely with a Greek article on a concrete, previously-mentioned count
  noun.
- **Obligatory "linked form" before ANY following complement**, regardless
  of whether Greek has an article at all — a genitive noun (`mulkin Allah`
  "kingdom of God," Luke 8:10; `gaskiyar bishara` "truth of the gospel," 2 Cor
  4:2; a nested chain `kyautar alherin Allah` "gift of the grace of God," Rom
  5:15), a possessive pronoun suffix (`almajiransa`, `ɗan'uwana` "my brother,"
  John 20:17; `tabarmarka` "your mat," Mark 2:9), or even a relative clause
  (`begen da muka ce...` "the hope that we...", Heb 10:23). This branch is
  syntactically triggered by what follows the noun, not by the Greek's own
  article — directly parallel to OT Arabic's construct-state (ʾiḍāfa)
  finding, not a definiteness marker in the Greek/English sense.

Possession structurally pre-empts plain definiteness marking: a Greek article
on a genitive-modified or possessed noun phrase is absorbed into the
construct/possessive construction and should default to **NEQ** — its
function is not recoverable from the fused suffix, which is doing different
syntactic work. A free linker `na`/`ta` still coexists alongside the fused
`-n`/`-r` (see GENITIVE / POSSESSION).

Proper nouns/unique referents (`Allah` for ὁ θεός; `Magdalin` for ἡ
Μαγδαληνή) and collective/kinship/abstract-mass nouns (`Al'ummai` for τῶν
ἐθνῶν; `'yan'uwa` for τοὺς ἀδελφούς; `fasikanci` for τὰς πορνείας) regularly
appear bare even with a Greek article — the article should default to NEQ in
these cases too.

## GENITIVE / POSSESSION — [hau]

Verified against 70 sampled instances from 3,096 candidate Greek noun+
genitive-noun sequences (pronoun-genitive was already established above and
is reconfirmed pervasively throughout this sample).

Beyond the fused `-n`/`-r` vs. free `na`/`ta` split (see ARTICLES AND
DEFINITENESS), Hausa's genitive strategy tracks the SEMANTIC type of the
relationship at least as much as any syntactic property of the Greek:

1. **Fused `-n`/`-r`** — the dominant strategy for ordinary possessive/
   associative noun+noun genitives, and it stacks freely in chains with no
   special handling needed: `κλεὶς φρέατος τῆς ἀβύσσου` ("key of the pit of
   the abyss") → `mabuɗin ramin Abis` (Rev 9:1, two fused links); `οἴνου
   θυμοῦ τοῦ θεοῦ` ("wine of the wrath of God") → `ruwan inabin fushin Allah`
   (Rev 14:10, three-deep chain).
2. **Free `na`/`ta`** — real, but not a free variant of #1: used when the
   head NP is already complex (contains its own fused genitive or a
   `mai`-agentive construction, see SUBSTANTIVE PARTICIPLES) rather than
   stacking a third suffix (`γραμματεῖς λαοῦ` within "scribes of the law of
   the people" → `malaman dokoki na mutane`, Matt 2:4), or for partitive/
   measure genitives (`λίτραν μύρου` → `wajen awo... na nardi`, John 12:3).
3. **Prepositional `ga`** ("to/for") for objective/goal genitives, where the
   genitive is the target of the head noun rather than its possessor:
   `ἐλπίδα ζωῆς` ("hope of/for life") → `begen... ga rai madawwami` (Titus
   1:2).
4. **Restructuring into a relative/finite clause with the genitive noun
   promoted to subject** — a large, real strategy for genitive-of-agent/
   source constructions: `διδασκαλίαις δαιμονίων` ("teachings of demons") →
   `abubuwan da aljanu suke koyarwa` (1 Tim 4:1); `λογίων θεοῦ` ("oracles of
   God") → `abubuwan da Allah ya faɗa` (Heb 5:12); `παρουσίᾳ κυρίου` ("coming
   of the Lord") → `sa'ad da Ubangijimmu... ya dawo` (Phil 4:5, a temporal
   clause — this last case echoes the finding in INFINITIVAL CONSTRUCTIONS
   that Greek's abstract event-nouns re-finitize generally in Hausa, not
   just with infinitives).
5. **Restructuring into a prepositional adjunct inside a relative clause**
   for genitive-of-instrument/location: `ἔργοις χειρῶν` ("works of hands") →
   `abin da suka ƙera da hannuwansu` ("what they made WITH their hands,"
   Acts 7:41); `αἵματος σταυροῦ` ("blood of the cross") → `jinin Kiristi da
   ya zubar a kan gicciye` ("blood he shed ON the cross," Col 1:20).
6. **Restructuring into a relative clause or plain adjective** for the
   Hebraic/attributive genitive Greek retains ("hearer of forgetfulness" =
   "forgetful hearer"): `ἀκροατὴς ἐπιλησμονῆς` → `mai ji ne kawai yă mance`
   (James 1:25); `κτήτορες χωρίων` ("owners of lands") → `waɗanda suke da
   gonaki` ("those who have farms," Acts 4:34).
7. **Lexicalized/idiomatic substitution with no linking construction at
   all**: ethnonym/origin genitives become a derived appositive adjective
   (`Χριστοῦ Ναζωραίου` → `Yesu Kiristi Banazare`, Acts 4:10); fixed
   superlative/totality idioms get their own reduplicated Hausa idiom
   (`αἰῶνας αἰώνων` → `har abada abadin`, Rev 4:9; `διαιρέσεις διακονιῶν`,
   "varieties of services" → `hidimomi iri-iri`, 1 Cor 12:5).
8. **Elliptical kinship genitives get an explicit relationship noun
   supplied**: `Μαρία Ἰωσῆτος` ("Mary of Joses") → `Maryamu uwar Yusuf`
   ("Mary, mother of Joseph," `uwa` "mother" supplied + fused `-r`, Mark
   15:47).

## COPULA / "BE" — [hau]

Verified against 25 sampled instances from 2,458 NT finite εἰμί tokens. Five
distinct strategies, chosen by FUNCTION, not by whether Greek's own copula is
morphologically present:

- **Identity/classification** ("X is Y," noun=noun) → `ne`/`ce` (gender-
  agreeing: `ce` feminine singular, `ne` elsewhere/default/plural).
  **Tenseless** — the same word regardless of whether Greek's copula is
  present-tense (Ἐγώ εἰμι → `Ni ne`, Matt 14:27), past-tense (ἦν... οὗτος,
  "this WAS the Son of God" → `wannan Ɗan Allah ne`, Matt 27:54), embedded in
  reported speech (Βασιλεὺς... εἰμί → `shi sarkin Yahudawa ne`, John 19:21),
  or an infinitive (Χριστοῦ εἶναι, "to be of Christ" → `shi na Kiristi ne`, 2
  Cor 10:7).
- **Existential "there is/was"** → `akwai` (positive) / `babu` (negative) —
  a completely separate system matching the negation section's existential
  rule, not `ne`/`ce`: Ἦν δέ τις μαθητής → `akwai wani almajiri` (Acts 9:10);
  ἁμαρτία... οὐ ἔστιν → `babu zunubi` (1 John 3:5).
- **Locative/prepositional-phrase predicates** ("X is in/with/among Y,"
  "where is X") → the bare relative-continuous PAC form (`yake`/`suke`/
  `take`), NOT `ne`/`ce`: Ποῦ ἐστιν ἐκεῖνος → `Ina mutumin yake` (John 7:11);
  ἥτις ἐστὶν ἐκκλησία θεοῦ (a relative-clause predicate) → `wadda take
  ikkilisiyar Allah` (1 Tim 3:15).
- **Future "will be"** (any predicate type) → `zama` ("become") or
  `kasance` ("remain/be") + future PAC, never `ne`/`ce`: ἔσομαι αὐτοῖς εἰς
  θεόν → `Zan zama Allahnsu` (Heb 8:10); πολλοὶ... ἔσονται πρῶτοι → `za su
  zama na farko` (Matt 19:30).
- **Predicate-adjective "be"**, especially with modal/necessity framing →
  `kasance`/`zama` + adjective: εἴ τίς ἐστιν ἀνέγκλητος → `Dole dattijo yă
  kasance marar aibi` (Titus 1:6).
- **The formulaic ὅ ἐστιν gloss** ("which is...", explaining a foreign term
  or restating a metaphor) → the dedicated marker `wato` ("that is to
  say"), not `ne`/`ce` or a relative clause: ὅ ἐστιν ῥῆμα θεοῦ → `wato,
  Maganar Allah` (Eph 6:17).

## PASSIVE VOICE — [hau]

Identified 1,508 finite indicative Greek passive verbs (morph voice position
= `P`) across 1,273 distinct verses; total passive-voice verb tokens of all
moods in the NT: 3,172 of 28,102 verb tokens (~11.3%). Ran a full-corpus proxy
check on all 1,273 verses for the one keyword-searchable strategy, then
manually classified two random samples totaling 80 verses (30 + 50) for the
rest, since the remaining strategies require reading, not keyword search.

An initial pass used a case-sensitive regex checking only `an|aka|akan`,
undercounting real hits (Hausa sentences routinely open with a capitalized
`An`/`Aka`, and the very common continuous/relative-continuous forms
`ana`/`ake` weren't in the pattern at all). Corrected (case-insensitive,
added `ana`/`ake`) before drawing conclusions.

**Full-corpus result**: `an`/`aka`/`ana`/`ake`/`akan` appears in **39.4%** of
the 1,273 verses; `za a` (future impersonal) in **11.1%**; either, **47.8%**.
This is a floor, not the true rate — it excludes bare `a` (the non-completive/
subjunctive impersonal form), which is real and appeared repeatedly in the
manual samples but is too ambiguous with the ordinary preposition "a" to
search for reliably at corpus scale. Even generously estimated, impersonal
marking is not a majority strategy on its own — confirming that several real
strategies genuinely coexist.

**Eight real, coexisting strategies:**

1. **Impersonal `an`/`aka`/`ana`/`ake`/`akan` (+bare `a`)** — confirmed at
   corpus scale, ~40-48%+ of verses, the single largest strategy but not a
   majority. `an`/`ana` mark independent-clause completive/continuous
   impersonal; `aka`/`ake` the corresponding relative/subordinate-clause
   forms; bare `a` is non-completive (future/subjunctive); `akan` is
   habitual. ἐτύθη → `an miƙa Kiristi` (1 Cor 5:7); ἠγέρθη → `aka tashe shi`
   (Rom 4:25); ἀνακρίνεται → `ta Ruhu ne ake fahimtarsu` ("it is BY THE
   SPIRIT that it is understood," 1 Cor 2:14, a cleft using the relative
   continuous `ake`).
2. **Unmarked lexical intransitive/ambitransitive verb choice** — the
   largest non-impersonal strategy. Many Hausa verbs are ambitransitive or
   have a distinct intransitive/inchoative counterpart, and translators
   simply pick that frame with zero passive marking. Lexically conditioned
   per Greek verb — πληρόω-family verbs (fullness/completion) reliably →
   `cika` ("become full/complete," John 7:8, Matt 22:10, Luke 1:20);
   κατεκάη ("were burned up," x3) → `ya ƙone`/`suka ƙone`/`ta ƙone` (Rev
   8:7); ἐκλυθήσονται → `kāsa` ("fail/be unable," Matt 15:32); ἐπλανήθησαν →
   `bauɗe` ("stray," Jude 11).
3. **Light-verb (`yi`/`sha`/`kai`/`cika da`) + abstract noun** — a major,
   productive strategy for psychological/relational/experiential passive
   verbs, not a one-verb quirk: ἐκπλήσσομαι-family (x3+) → `yi mamaki` ("be
   astonished," Mark 6:2, Luke 4:32, Matt 7:28); σῴζω/σωθήσεται (x4+) →
   `sami ceto` ("obtain salvation," Matt 10:22, 1 Cor 3:15, Rom 10:13); πλανᾶσθε
   → `yi kuskure` ("make a mistake," 1 Cor 15:33); ἀποκατηλλάγητε → `Allah ya
   yi sulhu da ku` ("God made reconciliation," Col 1:21); σκοτισθήσεται →
   `yi duhu` ("become darkness," Matt 24:29).
4. **Agent promotion to active subject**, confirmed repeatedly (7+ clear
   instances), including a special and common subtype: implicit-agent
   ("divine passive") verbs get `Allah` supplied as an explicit active
   subject. εὐνουχίσθησαν ὑπὸ τῶν ἀνθρώπων → `mutane... suka mai da su
   haka` (Matt 19:12); ἐμαρτυρεῖτο ὑπὸ τῶν ἀδελφῶν → `Yan'uwa... sun yi
   magana mai kyau` (Acts 16:2); εἰσηκούσθη/ἐμνήσθησαν (implicit divine
   agent) → `Allah ya ji addu'arka, ya kuma tuna` ("God heard your prayer,
   and remembered," Acts 10:31); ἐθεάθη ὑπ' αὐτῆς → `ta gan shi` ("she saw
   him," patient demoted to object, John 20:18). This means an agent word —
   often `Allah` — can appear with NO Greek subject token to align it to.
5. **Stative "`a` + deverbal adjective" + copula** for perfect/resultative
   passives — γέγραπται is the clearest and most frequent case (5+ instances
   sampled: `a rubuce yake`, Matt 4:4/4:6/Luke 4:8/Acts 1:20/2 Cor 9:9), but
   the construction is productive beyond it: ἐφρουρούμεθα → `mun kasance a
   daure a kurkuku` ("we were in a bound state in prison," Gal 3:23, `daure`
   = "bound," same shape as `rubuce` = "written").
6. **Nominalization: "become/have" + noun/adjective**, absorbing the
   passive verb's content into a non-verbal complement: τετελείωται → `ta
   zama cikakkiya` (1 John 2:5); τεθεμελίωτο → `yana da harsashinsa` ("it
   has its foundation," Matt 7:25).
7. **Full omission/restructuring with no verbal correspondent at all** —
   rarer, but real, and should be expected as legitimate NEQ/idiom
   territory: καλεῖται (ἥτις καλεῖται Βηθλέεμ, "which is called Bethlehem")
   → simple apposition with no "called" verb at all (Matt 2:4); ἐγεννήθημεν
   ("in which we were born") → `yarensa` ("his own language," nativity
   absorbed into a possessive noun phrase, Acts 2:8).
8. **Grade 7 `-u` reflexive/passive-like verb forms** — real but narrow,
   two confirmed instances (`ἐμερίσθη` → `ya rabu`, Matt 12:26; `ἐσχίσθη` →
   `suka rarrabu`, Acts 14:4, both from `raba`/`rarraba` "divide"). Not a
   systematically-reached-for category — treat as ordinary lexical items
   within strategy 2, not a named category to hunt for.

## SUBSTANTIVE PARTICIPLES — [hau]

Identified 1,433 Greek article+participle sequences (article immediately
followed by a participle); 1,262 not immediately followed by a noun across
1,084 distinct verses. Ran a full-corpus proxy search, then manually
classified 80 instances by reading.

**Heuristic caveat**: "article+participle with no noun immediately after"
also catches post-nominal attributive participles (noun+article+participle,
e.g. ὁ ναὸς ὁ ἁγιάσας "the temple, the one that sanctifies," Matt 23:17)
where the participle modifies a *preceding* noun. In practice this doesn't
change the findings below, since both genuinely-headless and post-nominal-
attributive participles are handled by the same Hausa constructions.

**Full-corpus proxy** (floor estimates — see caveat on strategy 2 below):
`wanda`/`wadda`/`waɗanda` family in **48.8%** of verses; `mai`/`masu` in
**33.0%** (corrected upward from an initial 22.5% that missed the plural
`masu`); `duk`/`dukan` in 24.0%; `kowa` in 2.0%.

**Nine strategies, roughly in order of frequency in the 80-instance sample:**

1. **`wanda`/`wadda`/`waɗanda` headless relative pronoun** — the plurality
   strategy (~30% of the sample). Used when the clause has no overt head
   word for the participle to attach to: τὸν πέμψαντά → `wanda ya aiko ni`
   (John 5:24); ὁ πιστεύων → `wanda ya gaskata` (John 3:36).
2. **`da`-relative clause attached to an overt head (noun, pronoun, or
   demonstrative)** — a major strategy this document's earlier draft missed
   entirely, second most common overall (~19% of the sample). `da` is
   Hausa's general-purpose relativizer, invariant for gender/number (unlike
   `wanda`), but requires — or strongly prefers — an explicit head
   immediately before it. **The choice between strategy 1 and strategy 2 is
   about whether the translator supplied a head word, not about the Greek**:
   τοὺς πεπιστευκότας αὐτῷ Ἰουδαίους → `Yahudawan da suka gaskata da shi`
   (John 8:31); τὸ βλεπόμενον → `abin da ake gani` ("the thing that is
   seen," Heb 11:3); ὁ ἐλθὼν → `wannan da ya taɓa zuwa` ("this one who
   came," John 3:2, attached to a demonstrative); ὁ πέμψας → `shi da ya
   aiko ni` ("he who sent me," John 7:28, attached to a pronoun). The
   combined shape `[head] da yake/suke [verbal noun]` is the default for
   continuous-aspect participles specifically.
3. **`mai`/`masu` (singular/plural) agentive nominal** — for ongoing role/
   occupation/characteristic senses: ὁ θερίζων/ὁ σπείρων → `mai girbi`/`mai
   shuka` (John 4:36); τοῖς ἀγαπῶσιν (pl.) → `masu ƙaunarsa` (Rom 8:28, 2
   Tim 4:8); ὁ καθήμενος → `mai hawansa` ("its rider," Rev 6:8). **Related
   but distinct**: lexicalized agentive nouns with the fixed `ma-` prefix
   (`magina` "builders," Acts 4:11; `masoyi` "lover," Matt 5:46; `mazauna`
   "inhabitants," Rev 11:10) are ordinary vocabulary, not a live syntactic
   strategy — align as normal noun matches.
4. **Generic/gnomic "whoever"** — two coexisting strategies: `duk`+
   `wanda`/`mai` (ὁ ὀργιζόμενος → `duk wanda ya yi fushi`, Matt 5:22; ὁ
   ἀγαθοποιῶν → `Duk mai yin abin da yake nagari`, 3 John 11) confirms the
   expected pattern; a bare generic pronoun **`Kowa`** ("whoever/anyone,"
   no `wanda`/`mai` at all) also appears (ὁ πίνων → `Kowa ya sha wannan
   ruwa`, John 4:13) — a fourth strategy, rarer (~2% of verses) but real.
5. **Cleft/focus construction with a bare relative-continuous PAC form**
   (`yake`/`suke`) and no relative pronoun, `da`, or `mai` at all — used for
   emphatic identity/agency claims ("it is X who/that Y"), concentrated in
   theological "it is God who..." statements: τὸ ζῳοποιοῦν (Πνεῦμά ἐστιν τὸ
   ζῳοποιοῦν) → `Ruhu ne yake ba da rai` (John 6:63); ὁ ἐνεργῶν (ὁ αὐτὸς
   θεός ὁ ἐνεργῶν τὰ πάντα) → `Allah ɗaya ne yake aikata su` (1 Cor 12:6).
6. **Privative `mara-`/`marar-`/`marasa`** ("lacking X") for participles/
   adjectives expressing a negative characteristic, not a relative clause:
   ὁ ἀσθενῶν → `ɗan'uwa marar ƙarfi` ("brother lacking strength," Rom
   14:21); `marasa laifi` ("without fault," Luke 20:20) confirms the
   pattern recurs, not a one-off.
7. **Naming-participle idiom `(ake) kira X`** for λεγόμενος/καλούμενος
   specifically ("the place/thing called X"): τὴν λεγομένην → `ake kira
   Kyakkyawa` ("that is called Beautiful," Acts 3:2).
8. **A lexicalized deverbal participial noun** — real but narrow: ὁ
   γεγεννημένος → `kowane haifaffe na Allah` ("every born-one of God," 1
   John 5:18, `haifaffe` a fixed nominalization of `haifa` "give birth").
   Like Grade 7 in PASSIVE VOICE, treat as vocabulary.
9. **Full restructuring/omission with no NP correspondent at all** — a
   non-trivial fraction (~9% of the sample), legitimate NEQ/idiom territory:
   Ὁ ποιῶν τοὺς ἀγγέλους... (a substantive-participle title for God)
   collapses into a plain finite main clause, `Ya mai da mala'ikunsa iska`
   (Heb 1:7); a circumstantial-temporal participle (τῇ ἐπιφωσκούσῃ, "at the
   dawning") becomes a plain adverbial, `da sassafe` ("at dawn," Matt
   28:1).

## INFINITIVAL CONSTRUCTIONS — [hau]

Sampled 72 instances across four syntactic categories, identified by what
precedes the infinitive: modal/phase complement verbs (θέλω, δύναμαι, μέλλω,
ἄρχομαι, δεῖ, ὀφείλω, βούλομαι, ζητέω, κελεύω, ἔξεστι(ν), ἰσχύω — 367
candidates, 25 sampled), ὥστε-result (23 candidates, 15 sampled), articular
infinitive (τό/τοῦ/τῷ + infinitive not preceded by εἰς/πρός — 159 candidates,
20 sampled), εἰς τό/πρός τό-purpose (63 candidates, 12 sampled). **The
"verbal noun/gerund" default assumed at the outset turned out to be a real
but minority strategy — the majority pattern across every category is
re-finitization: the infinitive clause becomes an ordinary finite clause
rather than staying nominal.**

1. **Modal/phase complement infinitives overwhelmingly become a serial-verb
   chain using Hausa's distinct SUBJUNCTIVE PAC paradigm** (`in`/`ka`/`ki`/
   `ta`/`yă`/`mu`/`ku`/`su` — a different set from the ordinary indicative
   PAC in PRONOUNS AND THE PERSON-ASPECT COMPLEX) for the complement verb,
   chained after the modal verb's own PAC: θέλω μένειν → `na so yă kasance`
   ("I wanted, he-SUBJ remain," John 21:22); ἠθέλησα ἐπισυναγαγεῖν → `na so
   in tattara` ("I wanted, I-SUBJ gather," Matt 23:37). **Real secondary
   strategy**: nominalization into a verbal noun (often `-wa`-suffixed) or
   an abstract noun (`niyya` "intention") as the modal verb's object: οὐ
   θέλει μετανοῆσαι → `ba ta da niyya` ("she has no intention," Rev 2:21);
   μέλλει πορεύεσθαι → `yake niyyar tafiya` ("he is in intention of going,"
   John 7:35). **δεῖ frequently drops necessity-marking entirely**: τί με
   δεῖ ποιεῖν → `me zan yi` ("what will I do," no `dole`/`wajibi` at all,
   Luke 3:10).
2. **Purpose infinitives of every syntactic type (bare complement, εἰς τό,
   πρός τό, τοῦ-genitive-purpose) unify into ONE construction: `don`/
   `domin`/bare `saboda` + subjunctive PAC** — the same family used for
   ἵνα-purpose clauses and causal ὅτι (see below): εἰς τὸ ἀποκαλυφθῆναι
   αὐτὸν → `don a bayyana shi` (2 Thess 2:6); εἰς τὸ σωθῆναι αὐτούς → `don
   su sami ceto` (2 Thess 2:10, the σῴζω light-verb pattern from PASSIVE
   VOICE recurring here too); a genitive purpose infinitive complementing a
   noun (τοῦ διδάσκειν) → `don yă koyar` (Matt 11:1). When context makes
   purpose obvious without a connector, bare subjunctive chaining suffices:
   εἰς τὸ ἐμπαῖξαι καὶ μαστιγῶσαι καὶ σταυρῶσαι → `su yi masa ba'a, su yi
   masa bulala, su kuma gicciye shi` (three bare subjunctive clauses in a
   row, Matt 20:19).
3. **ὥστε-result infinitives split three ways** by whether the result is
   realized/actual or intended/purpose-like: (a) **realized result** → `har`
   + indicative PAC, or unmarked indicative continuation with no connector:
   ὥστε βυθίζεσθαι αὐτά → `har jiragen suka fara nutsewa` ("so the boats
   began sinking," Luke 5:7); ὥστε πιστεῦσαι → `har Yahudawa... suka
   gaskata` (Acts 14:1). (b) **Intended/purpose-like result** collapses into
   the same `domin`/`don`/bare `saboda` + subjunctive family as ordinary
   purpose: ὥστε παραδοῦναι αὐτὸν → `domin su ba da shi` (Luke 20:20). (c)
   **Explicit causative** `ya sa` ("it caused") or `tilasta` ("force/
   compel") + a finite complement for a strongly causal reading: ὥστε
   ἐξαπορηθῆναι ἡμᾶς → `ya sa muka fid da tsammani` ("it caused us to lose
   hope," 2 Cor 1:8).
4. **Temporal/circumstantial articular infinitives (μετὰ τό "after X-ing,"
   ἐν τῷ "while/when X-ing") mostly RE-FINITIZE into an ordinary temporal
   subordinate clause** — contrary to the "stays nominal" default assumed
   going in: `bayan` ("after") + PAC + verb (μετὰ τὸ ἐγερθῆναί με → `bayan
   na tashi`, Matt 26:32); `da`/`sa'ad da`/`yayinda` ("when/while") + PAC +
   verb, often with a verbal noun retained (ἐν τῷ εἰσελθεῖν αὐτοὺς →
   `yayinda suke shiga`, Luke 9:34); `bayan da` (a fused "after"+
   relativizer compound, μετὰ τὸ ἀποκτεῖναι → `bayan da ya kashe jikin`,
   Luke 12:5). A real minority does nominalize, especially with μετὰ τό:
   μετὰ τὸ παθεῖν αὐτὸν → `Bayan wahalarsa` ("after his suffering," a
   possessed verbal/deverbal noun, Acts 1:3).
5. **A genitive τοῦ-infinitive complementing a noun** (e.g. "opportunity to
   betray him") renders via the `da`-relative-clause-on-a-noun strategy from
   SUBSTANTIVE PARTICIPLES, not as a nominal phrase: τοῦ παραδοῦναι αὐτὸν
   (ἐζήτει εὐκαιρίαν τοῦ παραδοῦναι αὐτὸν) → `neman zarafin da zai ba da
   Yesu` ("seeking the opportunity that he would give Jesus," Matt 26:16).

## ἵνα CLAUSES — [hau]

Sampled 25 of 663 NT ἵνα instances. Strongly confirms and generalizes the
INFINITIVAL CONSTRUCTIONS finding: `don`/`domin` (or bare subjunctive with no
overt connector when purpose is contextually obvious) + subjunctive PAC is
overwhelmingly the strategy, in ~20 of 25 sampled instances. ἵνα πληρωθῇ →
`don a cika` ("so that it would be fulfilled," Matt 4:14); ἵνα Χριστὸν
κερδήσω → `domin in sami Kiristi` (Phil 3:8); ἵνα ἐντραπῇ → `don yă ji
kunya` ("so that he would feel shame," 2 Thess 3:14, another instance of the
PASSIVE VOICE light-verb-for-psych-verb pattern). `kada` appears alongside
or instead of `don`/`domin` when the purpose itself is negative (ἵνα μὴ
μωμηθῇ → `domin kada hidimarmu ta zama abin zargi`, 2 Cor 6:3). Bare
subjunctive chaining with no connector is common when purpose is obvious from
context (ἵνα πιάσωσιν αὐτόν → `su kama shi`, John 7:32). A real minority: when
an ἵνα-clause blurs into result rather than pure intention, Hausa restructures
into an ordinary indicative statement (ἵνα φανερωθῶσιν → `wannan ya nuna a
fili`, "this made it clear," 1 John 2:19) — matching INFINITIVAL
CONSTRUCTIONS' finding that Hausa doesn't rigidly distinguish purpose from
result.

## ὅτι — [hau]

Sampled 30 of 1,294 NT ὅτι instances. **Causal ὅτι collapses onto the SAME
`don`/`domin`/`saboda` word family used for ἵνα-purpose and ὥστε-result, plus
a new member, `gama` ("for") — a much bigger unification across the whole
purpose/result/reason system than assumed going in.** Declarative ὅτι has its
own separate and more variable set of strategies.

**Causal ὅτι ("because")**: ζητεῖτέ με ἀποκτεῖναι ὅτι ὁ λόγος ὁ ἐμὸς οὐ
χωρεῖ ἐν ὑμῖν ("you seek to kill me BECAUSE my word has no place in you") →
`kuna shiri ku kashe ni, don maganata ba ta da wurin zama` (John 8:37); οὐ
ὅτι καθ ὑστέρησιν λέγω ("not that/because I speak from want") → `Ba na faɗin
haka domin ina cikin bukata` (Phil 4:11); ἀλλ ὅτι ταῦτα λελάληκα ("but
because I have said these things") → `Saboda na faɗa waɗannan abubuwa` (John
16:6); Λεγιών, ὅτι εἰσῆλθεν δαιμόνια πολλὰ ("Legion, because many demons
entered him") → `"Tuli," gama aljanu masu ɗumbun yawa ne suna cikinsa` (Luke
8:30). One verse shows the causal/declarative split side by side: γέγραπται
ὅτι Ἅγιοι ἔσεσθε ὅτι ἐγὼ ἅγιος ("it is written THAT you shall be holy,
BECAUSE I am holy") → `a rubuce yake cewa, "Ku zama masu tsarki, domin ni
mai tsarki ne."` (1 Pet 1:16) — declarative ὅτι → `cewa`, causal ὅτι →
`domin`, in the same sentence.

**Declarative ὅτι**:
- Introduces DIRECT quoted speech → NEQ (no word at all — punctuation/
  quotation alone introduces it, matching the general project convention):
  εἶπεν αὐτοῖς ὅτι Οὐ χρείαν ἔχουσιν... → `Yesu ya ce musu, "Ai, masu lafiya
  ba sa bukatar likita..."` (Mark 2:17).
- Introduces an indirect/embedded factual complement (after verbs of
  knowing, saying, perceiving) — genuinely varies between two coexisting
  strategies, not a strict rule: explicit `cewa` ("that") — Οἴδαμεν ὅτι
  καλὸς ὁ νόμος → `Mun san cewa doka tana da kyau` (Rom 7:16); or
  PARATACTIC direct complementation with no connecting word at all — οἶδα
  ὅτι σπέρμα Ἀβραάμ ἐστε → `Na dai san ku zuriyar Ibrahim ne` (John 8:37).
  Occasionally `yadda` ("how") substitutes when coordinated with a
  preceding "how"-clause: διηγήσατο... πῶς... καὶ ὅτι ἐλάλησεν → `ya gaya
  musu yadda... ya ga Ubangiji kuma cewa Ubangiji ya yi magana...` (Acts
  9:27).
- A real gray zone: some declarative ὅτι complements get recast with a
  causal-family word anyway when the translator reads the complement as
  reason-giving rather than fact-reporting — πιστεύετε ὅτι οὐ ἐστὲ ἐκ τῶν
  προβάτων τῶν ἐμῶν ("you do not believe THAT you are not my sheep") → `ba
  ku gaskata ba domin ku ba tumakina ba ne` (John 10:26) — not a Hausa-
  specific error, a genuine translation-level blur that shows up in other
  Bible translations too.

## CONDITIONAL CONSTRUCTIONS — [hau]

Sampled 15 of 502 NT εἰ instances and 15 of 331 NT ἐάν instances. **Both
Greek forms converge on the same Hausa strategy when functioning as genuine
open conditionals — the real dividing lines in Hausa are semantic-pragmatic,
not Greek's grammatical realis/irrealis class distinction.**

**εἰ has (at least) four distinct functions — only one is an ordinary
conditional:**
1. Genuine real/open conditional → `in` + PAC, same as ἐάν: εἰ σὺ οὐ εἶ ὁ
   χριστός → `in kai ba Kiristi ba ne` (John 1:25).
2. Interrogative "whether" (embedded or direct yes-no questions, a
   completely separate Greek use) → NO conditional marker at all, rendered
   as an ordinary question: ἐπηρώτων αὐτὸν εἰ ἔξεστιν... → `suka gwada
   shi... cewa, "Daidai ne bisa ga doka..."` (Mark 10:2, a direct embedded
   question); Εἰ πνεῦμα ἅγιον ἐλάβετε → `Kun karɓi Ruhu Mai Tsarki...?`
   (Acts 19:2).
3. The fixed **εἰ μή idiom ("except/only")** → a dedicated exceptive
   particle, `sai`/`sai dai`, NOT built from any conditional word: οὐ...
   εἰ μὴ ὁ ἀλλογενὴς → `Ba wanda... sai dai wannan baƙon` ("none... except
   this foreigner," Luke 17:18) — this idiom recurs constantly (6+ of the
   15 sampled εἰ instances) and should be recognized as its own fixed
   construction, not decomposed into "if"+"not."
4. **Counterfactual/irrealis conditionals** → `da` (not `in`): εἰ ἐμὲ
   ᾔδειτε καὶ τὸν πατέρα μου ἂν ᾔδειτε ("if you had known me, you would
   have known my Father too") → `Da kun san ni, da za ku san Ubana ma`
   (John 8:19). The choice between `in` and `da` tracks the translator's
   realis/irrealis reading, not Greek's lexical εἰ/ἐάν split — a single
   verse can mix both for two clauses built on the same construction (John
   15:20: εἰ ἐμὲ ἐδίωξαν → `In sun tsananta mini` [ordinary], but εἰ τὸν
   λόγον μου ἐτήρησαν → `Da sun yi biyayya...` [counterfactual reading of
   the identical construction]).

**ἐάν overwhelmingly renders as `in` + PAC**, with `sai in` for the ἐὰν μή
"unless" idiom (paralleling εἰ μή): ἐὰν... ἁμάρτῃ ὁ ἀδελφός σου → `In
ɗan'uwanka ya yi zunubi` (Matt 18:15). Real minority patterns: indefinite/
generic ἐάν clauses (ἐάν τις, "if anyone...") restructure into SUBSTANTIVE
PARTICIPLES' generic-relative constructions (`duk wanda`, `kome` "whatever")
rather than staying `in`-conditionals (ἐάν τις γνῷ → `duk wanda ya san`,
Matt 26:16); a concessive-flavored ἐάν gets its own dedicated marker, `ko da
yake` ("even though"), distinct from ordinary `in` (Ἐὰν ᾖ ὁ ἀριθμὸς... ὡς ἡ
ἄμμος → `Ko da yake yawan Isra'ilawa yana kama da yashi`, Rom 9:27).

## COMPARATIVES AND SUPERLATIVES — [hau]

Sampled 24 of 300 NT comparative-morphology adjective tokens. Six real,
semantically-conditioned strategies, mostly built on the verb `fi`
("exceed/surpass"), not simply the two-word `mafi`/`fiye da` pattern assumed
going in.

1. **Predicative comparison** ("X is more/-er than Y") — the verb `fi`
   governing the compared-to entity as its direct object, with the quality
   expressed as a following noun: `[PAC] + fi + [compared entity] +
   [quality-noun]`. The single most frequent pattern: μείζων Ἰωάννου
   ("greater than John") → `ya fi Yohanna... girma` ("he exceeds John [in]
   greatness," Matt 11:11); μὴ ἰσχυρότεροι αὐτοῦ ("not stronger than him")
   → `Mun fi shi ƙarfi` (1 Cor 10:22). The genitive "than"-standard
   sometimes gets absorbed as a modifier of the quality-noun itself:
   σοφώτερον τῶν ἀνθρώπων ("wiser than men") → `ta fi hikimar mutum`
   ("exceeds human wisdom," 1 Cor 1:25).
2. **Attributive comparison** (modifying a noun directly) — the
   grammaticalized prenominal particle `mafi` + adjective: μείζονος...
   σκηνῆς → `tabanakul mafi girma` ("a greater tabernacle," Heb 9:11).
   Real minority: a `da`-relative clause with an embedded `fi`-verb covers
   the same slot: μείζονα τούτων... ἔργα → `abubuwan da suka fi waɗannan
   girma` ("things that exceed these in size," John 5:20).
3. **Explicit binary "than" comparison** — the grammaticalized compound
   preposition `fiye da` ("exceed-with"), distinct from bare `fi`:
   φρονιμώτεροι ὑπὲρ τοὺς υἱοὺς τοῦ φωτὸς → `suna da wayon... fiye da 'yan
   haske` ("more shrewd... than the sons of light," Luke 16:8).
4. **Superlative-among-a-group** — `mafi` + adjective + `a`/`cikin` + [the
   group], a partitive standard-of-comparison rather than a binary "than."
   Greek's genitive-of-comparison converts to this shape rather than to
   `fiye da` when the sense is "greatest of a set": μείζων ὑμῶν → `Mafi
   girma a cikinku` ("the greatest among you," Matt 23:11); μεῖζον τῶν
   λαχάνων → `mafi girma cikin tsire-tsiren lambu` ("greatest among the
   garden plants," Matt 13:32) — the same clean pattern found independently
   twice.
5. **Quantity/majority comparatives** ("more/most of X") use a dedicated
   lexical noun, `yawanci` ("majority"), not `fi`/`mafi`: πλείονας τῶν
   ἀδελφῶν → `yawancin 'yan'uwa` ("the majority of the brothers," Phil
   1:14).
6. **Nominalized "have superiority over"** — a real, more formal-register
   alternative built on a noun `fifiko` ("superiority") derived from the
   same root: κρείττων... γενόμενος τῶν ἀγγέλων → `yake da fifiko a kan
   mala'iku` (Heb 1:4).

**Heuristic caveat**: several comparative-morphology Greek-parallel words
are lexicalized as ordinary nouns in Koine usage with no live comparison
sense — πρεσβύτεροι ("elders") and the νεώτεροι-family ("younger men/
widows" as an age-cohort label) get plain noun or `mai`-construction
translations, not any comparison strategy; πρότερον/προτέραν ("former/
previously") is a temporal expression, not a degree comparison, handled with
ordinary time adverbials.

## NEGATION — [hau]

Verified against 20 sampled verses with plain οὐ negation, all 69 NT
instances of οὐκέτι/μηκέτι (15 sampled), and 10 sampled μή+subjunctive/
imperative "prohibitive candidate" verses (from 400 total).

1. **Standard verbal negation is discontinuous, `ba...ba`**, circumfixing
   the predicate: `ba ku da gidajen...` ("you don't have houses," 1 Cor
   9:4); `ba zan ƙara muku wani nauyi ba` ("I will not add to you another
   burden," Rev 2:24); `ba su gane... ba` ("they did not understand," Acts
   8:27). PAC forms routinely contract with the leading `ba`: `bai` (`ba` +
   `ya`), `ban` (`ba` + `na`).
2. **Existential/quantifier negation uses `babu`** ("there is not"), a
   distinct strategy from verbal `ba...ba`: οὐ ἔστιν ποιῶν χρηστότητα
   ("there is none who does good") → `babu wani mai aikata nagarta` (Rom
   3:12); οὐ πολλοὶ σοφοί ("not many wise") → `Babu masu hikima da yawa` (1
   Cor 1:26).
3. **Copular/predicate-nominal negation is its own discontinuous pattern,
   `ba [predicate] ba ne/ce`** — the circumfix wraps the predicate and the
   copula particle (see COPULA / "BE") is retained after the closing `ba`:
   ἐλπὶς... οὐ ἔστιν ἐλπίς ("hope... is not hope") → `ba bege ba ne sam`
   (Rom 8:24); ἄρα οὖν οὐκέτι ἐστὲ ξένοι → `ku ba baƙi ba ne` (Eph 2:19).
4. **The prohibitive `kada` covers any directive/purposive "don't,"
   including μή/ἵνα μή/ὅπως μή in subordinate purpose clauses**, not just
   true 2nd-person imperatives: Μὴ ἐρεθίζετε ("do not provoke!") → `kada ku
   matsa...` (Col 3:21); ἵνα μὴ ἀθυμῶσιν ("so that they not be
   discouraged") → `don kada su fid da zuciya` (same verse); ὅπως μὴ
   γένηται ("so that... not happen") → `don kada yă ɓata lokaci` (Acts
   20:16). By contrast, declarative/conditional μή-subjunctive uses plain
   `ba` — ἔργα δὲ μὴ ἔχῃ ("if he does not have works") → `ba shi da ayyuka`
   (James 2:14), correctly distinguishing directive force from ordinary
   negation. Interrogative μή (rhetorical "surely not") uses neither — a
   separate rhetorical-question particle, `Ashe`.
5. **οὐ μή emphatic negation has no dedicated construction** — renders as
   ordinary negation with no extra marker: οὐ μὴ γεύσωνται θανάτου ("will
   never taste death") → `ba za su ga mutuwa ba` (Luke 9:27, ordinary
   future negation).
6. **οὐκέτι/μηκέτι ("no longer") is NOT a discontinuous `ba...kuma ba`
   construction** (an original guess with no supporting instances in a
   15-verse sample of all 69 NT occurrences). Instead, Hausa lexicalizes
   "again/still/continue" as a separate auxiliary VERB, and negates the
   whole auxiliary+main-verb complex with ordinary `ba...ba`/`kada` — a
   3-way split record (negation + auxiliary + main verb), not a single
   discontinuous negator. **`ƙara`** ("add/increase") is the closest thing
   to a default (~half the sample): `ba kwa ƙara barinsa...` ("you no
   longer let him," Mark 9:25); `ba zan ƙara yi muku magana ba` ("I will no
   longer speak with you," John 14:30). At least four other lexical
   strategies coexist: `daina` "stop/cease" (`bari mu daina ba wa juna
   laifi`, "let us stop blaming each other," Rom 14:13); `ci gaba da`
   "continue with" (`kada ku ci gaba da yin rayuwa`, "don't continue
   living like," Eph 4:17); `taɓa` "ever/experience" (`ba zai taɓa ruɓewa
   ba`, "he would never decay," Acts 13:34); `sāke` "repeat/again" (`ba
   kuwa za a sāke yin irinsa ba`, "it will not happen again," Mark 13:19).
   No single dominant word should be hardcoded as "the" translation for
   οὐκέτι/μηκέτι.

## DISCOURSE/EMPHATIC PARTICLES — [hau]

Checked corpus-wide frequency and sampled contexts for three particles named
in the original grammar-based hypothesis. All three are real, frequent, and
confirmed as genuine Hausa-internal discourse devices with only loose,
inconsistent correlation to any single Greek connective.

- `kuwa` (1,023 verses) — by far the most frequent; sometimes loosely
  tracks δέ (contrastive) but very often has no Greek correlate at all:
  δοξαζόμενος ὑπὸ πάντων ("glorified by all," a passive participle with no
  discourse particle in Greek) → `kowa kuwa ya yabe shi` (Luke 4:15,
  `kuwa` purely Hausa-internal continuity marking).
- `fa` (142 verses) — an emphasis/topic marker attaching after a fronted
  topic or transitional expression; sometimes tracks δέ (Σὺ δὲ πόσον
  ὀφείλεις → `Kai fa, nawa...`, Luke 16:7) but also appears where Greek has
  a different particle entirely (λοιπόν, "finally/now" → `Yanzu fa`, 1 Cor
  4:2) or none.
- `dai` (461 verses) — a mitigating/assertive particle ("just/merely/
  indeed"); frequently pairs with `sai` for the CONDITIONAL CONSTRUCTIONS
  εἰ μή/ἐὰν μή exceptive idiom, but also stands alone for plain emphasis
  with no Greek correlate: Ἠκούσατε ὅτι ἐρρέθη → `Kun dai ji an faɗa`
  ("you have indeed heard that it was said," Matt 5:27).

Treat as legitimate NEQ on the Hausa side by default (supplied for
discourse-pragmatic reasons, not translating a specific Greek word), except
in the minority of cases with a plausible δέ correlate.

## Plural marking — low alignment relevance

Hausa pluralization is heavily irregular (dozens of patterns: suffixing,
reduplication, internal change, similar in spirit to Arabic/Hebrew "broken
plurals"). This affects word *choice* but is not itself a distinct
alignment phenomenon — noted here only so it isn't mistaken for
tokenization noise when reviewing alignment output. Not independently
corpus-checked; low priority given its lack of alignment consequences.

## Cross-translation methodology note

Unlike fra/ind/hin/arb, no second, independently-translated complete Hausa
NT was available for cross-checking this document's findings against a
different translation's stylistic choices. All findings here rest on OHCB
alone, verified at full-corpus or large-random-sample scale (each section
above states its sample size), which is the strongest substitute available
absent a second translation — but it cannot separate general Hausa grammar
from OHCB's own individual stylistic tendencies the way the fra/ind/hin/arb
cross-checks could.

An existing UBS manual alignment (`SBLGNT-OHCB-manual.json`, in Biblica's
`alignments-hau` repository, `conformsTo: 0.3`, `creator: United Bible
Societies`) was found alongside the OHCB target TSV and examined as a
possible verification aid before this document was written. It was rejected:
a rigorous check showed the same failure pattern that caused the zht rebuild
(see `project_zht_alignment_paused` in the auto-memory system) — negation
particles aligned only 9.4% of the time (318/3,393), pronouns 0.1%
(16/16,123), articles 0% (0/19,796), and a spot-check of Matthew 19:6 found
not just missing links but a confirmed wrong one (Greek σάρξ "flesh" mapped
to the Hausa negation particle `ba` from an unrelated part of the clause).
This alignment was set aside entirely; no alignment data was used anywhere
in this document's construction, following the same raw-text-plus-reasoning
methodology used to rebuild `nt/zht.py`.

## Open questions for native-speaker review

- **PAC and object/possessive-suffix interaction with alignment tooling**:
  the PAC and fused-suffix rules in this document are the highest-value and
  least-precedented findings (no other supported language has an exact
  analogue), and have not been checked against actual LLM alignment output
  — only against hand-read Hausa/Greek verse pairs. Confirm the prompt
  guidance in `nt/hau.py` actually produces the expected record shapes once
  real alignment runs exist.
- **Free `na`/`ta` vs. fused `-n`/`-r` linker conditioning**: the "complex
  head NP avoids stacking a third suffix" generalization rests on a
  handful of examples (`malaman dokoki na mutane`, `abubuwa masu banƙyama
  na duniya`) — worth a dedicated, larger-scale check once possible.
  Likewise the `-n` (noun complement) vs. free `na` (adjective/ordinal
  complement) split noted for `tashin matattu na farko` is a working
  hypothesis from one example, not independently verified.
  the split of the `-n`/`-r` linker's two functions (plain definiteness vs.
  construct/linked-state) is corpus-confirmed at the level of "both
  functions exist and interact," but the exact conditions under which
  Hausa marks plain definiteness at all (vs. leaving a definite noun bare)
  were not independently quantified the way Indonesian's Branch A/B split
  was.
- **The subjunctive PAC paradigm** (`in`/`ka`/`ta`/`yă`/`mu`/`su`) is
  documented as a real, distinct set from the ordinary indicative PAC based
  on its consistent appearance in modal-complement and purpose contexts,
  but its full paradigm (all persons/numbers) was not independently
  tabulated from a reference grammar — confirm the forms used in this
  document are complete and accurate.
- **οὐκέτι/μηκέτι's auxiliary-verb ranking** (`ƙara` as "closest to a
  default") is based on a 15-verse sample; a larger sample could reveal a
  different distribution, or a translation-register conditioning (`sāke`
  vs. `ƙara` vs. `daina`) not yet identified.
- **A native Hausa speaker has not reviewed any part of this document.**
  Every finding here should be treated as provisional pending that review,
  particularly the more counterintuitive ones (the `da`-relative vs.
  `wanda` split being purely a phrasing choice; the causal-ὅτι/ἵνα/ὥστε
  unification; the four-way split of εἰ's functions).
