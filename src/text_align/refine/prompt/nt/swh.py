"""Swahili (swh) target-language prompt config for refine-alignment.

Built from raw text plus linguistic reasoning against ONEN (the primary
edition — first translation aligned), cross-checked against ONMM and SRUV06
(SRUV06 consult-only: not openly licensed, never used as an alignment-data
source). ONEN's existing alignment (`alignments-swh/data/alignments/ONEN/`)
is suspected sparse/statistical and was NOT used to build this config — the
same raw-text-plus-reasoning methodology used for zht and hau. Distilled from
`docs/alignment-principles-nt.swh.md`, which records the full evidence trail
(corpus counts, cross-translation comparisons, two hypotheses overturned
along the way) — see that document's "Resolved" sections for what each rule
below is actually grounded in. **Draft — not yet reviewed by a native
Swahili speaker.**

Key differences from every currently-supported language:

  BASE_BLOCK    — The Swahili finite verb fuses subject marker (SM) +
                  tense/aspect marker (TAM) + optional object marker (OM) +
                  root + optional derivational extensions + final vowel into
                  ONE unspaced word — closer to Arabic's fused proclitics
                  than to Hausa's space-preserving PAC particle. Object
                  marking (OM) can DOUBLE an explicit object noun already
                  present in the clause — conditioned by discourse
                  topicality/givenness (demonstrative, possessive, or
                  anaphora), not by mere noun-presence: a brand-new/
                  indefinite object gets no OM at all; an established one
                  gets OM (secondary) + noun (primary) in the same record.
                  Ditransitive/applicative OM tracks the recipient, not the
                  theme, regardless of which Greek case the recipient
                  carries. No articles of any kind — the Greek article
                  defaults to SECONDARY within the noun's own record, same
                  as every other supported language's unmarked-article case
                  (never NEQ merely because Swahili has no article word). The
                  associative "-a" genitive linker (wa/cha/ya/la/za...) is a
                  close typological match to genitive case — low-risk,
                  secondary to the possessed noun. Five copula/"be"/"have"
                  strategies split by COMPLEMENT TYPE (locative/circumstantial
                  vs. nominal/adjectival), not a deep identity-vs-existence
                  distinction. "na" covers FOUR distinct functions — "and",
                  comitative "with", the passive-agent marker "by", and the
                  "kuwa na" ("be with" = "have") construction — the single
                  biggest disambiguation risk in this config, since an
                  LLM defaulting to "na = and" will mis-align the passive-
                  agent case specifically.
  PASSIVE_BLOCK — The `-wa` suffix is the cleanest, most transparent passive
                  marker of any currently-supported language, plus a
                  productive stack of other verbal extensions: stative/
                  neuter `-ika`/`-eka` (resultative-flavored passives),
                  confirmed applicative recipient-tracking (see BASE_BLOCK),
                  confirmed causative `-isha`/`-esha` (a Greek periphrastic
                  causative — command-verb + causative-used infinitive —
                  can map onto two ordinary Swahili verbs, one of them
                  causative-suffixed, with NO special alignment handling
                  needed), and reciprocal `-ana` (two sub-patterns: genuine
                  mutual reciprocal, sometimes doubled with an external
                  "X kwa X" phrase; and a lexicalized non-mutual use that no
                  longer requires a plural subject at all).
  PARTICIPLE_BLOCK — No participle morphology; Greek's substantive/
                  attributive participles AND ordinary relative clauses both
                  funnel into Swahili's relative system, which has THREE
                  coexisting, all-common strategies, not one default:
                  an infixed relative concord inside a largely tenseless
                  verb form; the invariable particle `amba-` + relative
                  concord suffix (confirmed as common as the infixed
                  strategy at corpus scale, not a minor alternative); and
                  the "having/possessing" relative `-enye`, confirmed keyed
                  to a SEMANTIC FRAME ("characterized by/having X") rather
                  than to Greek's own surface part of speech — `-enye` wins
                  even when Greek encodes the same sense as a genuine finite
                  relative clause built on ἔχω. The infixed-vs-`amba-`
                  choice has one clean predictor (Greek relative ADVERBS
                  ὅπου/ὅθεν trigger `amba-` locative forms where an ordinary
                  relative PRONOUN in the same sentence gets infixed) plus a
                  second, independent trigger (pure discourse-restructuring
                  additions with no Greek relative word at all → `amba-`,
                  NEQ territory) — beyond that, the choice is stylistic, not
                  grammatically conditioned; do not hunt for further
                  triggers. The `-li-` inside an `aliye`-type relative is
                  itself split: a tenseless state-copula filler when
                  followed by an adjective/locative/PP predicate (no tense
                  value at all — confirmed against Greek constructions with
                  no tense element to license it), vs. a genuine past tense
                  when followed by a fused verb root.
  INFINITIVE_BLOCK — Swahili DOES have a true infinitive (class 15 `ku-` +
                  stem) — the first currently-supported non-European,
                  non-Romance language with one. Behaves closely to
                  English's infinitive rules, with one wrinkle: `ku-`
                  infinitives are simultaneously infinitives AND ordinary
                  class-15 nouns (taking class-15 concord), so the same
                  bare-nominal-use vs. explicit-nominalization split the
                  base principles give the Greek articular infinitive can
                  recur on the Swahili side too.
  HINA_BLOCK    — `ili` + subjunctive is the standard purpose conjunction,
                  confirmed distinct from an occasional periphrastic variant
                  (`-pata` "get/obtain," subjunctive + infinitive) that
                  distributes real "come to/manage to" semantic content
                  across two Swahili words for one Greek subjunctive verb.
  COMPARATIVE_BLOCK — No synthetic comparative/superlative morphology at
                  all. `kuliko` ("than") is the universal comparison
                  particle, sometimes paired with an analytic intensifier
                  `zaidi` ("more") on the adjective itself — confirmed
                  optional, not obligatory. Superlative is not a separate
                  construction: `kuliko wote` ("than all") is just ordinary
                  `kuliko` with "all" as the standard of comparison. Elative
                  superlative uses `kabisa` ("very/utterly").
  AUTOS_BLOCK   — When the Greek object is itself a pronoun (αὐτόν, ἐμέ,
                  σε...), Swahili doubles it near-categorically: the object
                  marker (OM) AND an independent pronoun both appear,
                  BOTH PRIMARY in the same record — a cleaner, more
                  automatic pattern than the topicality-conditioned
                  noun-doubling case in BASE_BLOCK, and NOT the same as
                  English's plain 1:1 pronoun treatment.
  HOTI_BLOCK    — THREE coexisting content-clause complementizers, not one:
                  `kwamba` (majority, ~700 corpus instances), `ya kwamba`
                  (a fuller cross-translation variant, same treatment), and
                  bare `kuwa` (confirmed real but a genuine minority,
                  roughly a tenth of `kwamba`'s frequency). The fixed idiom
                  `kwa kuwa` ("because") is a SEPARATE causal construction
                  that happens to share the string `kuwa` with the
                  complementizer — the single biggest disambiguation risk
                  in this block. Recitative ὅτι is NEQ, exactly as in
                  English — confirmed against six sampled instances with no
                  Swahili correspondent of any kind beyond quotation marks.
  CONDITIONAL_BLOCK — THREE coexisting real/open-condition strategies
                  (`kama`/`ikiwa` + plain indicative; negative `-sipo-`
                  infix with no conjunction; positive `-ki-` infix with no
                  conjunction) — confirmed via direct same-verse
                  cross-translation contrasts, so treat all three as equally
                  valid regardless of which one the current edition used.
                  Counterfactuals (`-nge-`/`-ngeli-` and `-ngali-`) are
                  BOTH confirmed to render the identical unreal-PAST
                  condition in different editions of the same verse — this
                  is free stylistic variation, NOT a present-vs-past split
                  as an early hypothesis assumed; do not tense-condition
                  which one to expect.
  NEGATION_BLOCK — TAM-conditioned and largely fused/circumfixal, not a
                  single free particle: a negative subject-marker set
                  (`ha-` + tense-specific marking, e.g. `-ja-` "not yet" for
                  the negative perfect, contrasting with positive `-me-`),
                  a DISTINCT subjunctive/purpose-clause negation infix
                  (`-si-`, with its own final-vowel change), and the
                  separate invariant copula-negation word `si` (see
                  BASE_BLOCK's COPULA section). Each negative marker aligns
                  as its own primary record against Greek's negation
                  particle, even when it is fused, unspaced morphology
                  rather than a free-standing word.

VERBAL_ASPECT_BLOCK is imported unchanged from eng.py — no Swahili-specific
override was found; the generic rule (both aspect element and main verb
primary when a translator renders aspect explicitly) already covers the
sampled cases with no adjustment needed.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import VERBAL_ASPECT_BLOCK


# ---------------------------------------------------------------------------
# Swahili-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied prepositions, morphologically-implied pronouns, fused subject/object/tense morphemes, and context-implied linking morphemes. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Create separate records whenever source tokens can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (fused subject marker, fused object marker, fused TAM morphology, associative "-a" linker, modal helpers) are secondary to the source token whose grammar requires them, OR primary in their own record when a real source token exists for them to correspond to — see PRONOUNS AND SUBJECT/OBJECT MARKING below for the general rule. NEQ is for words with no source-language grammatical anchor at all, not a default for "the target marks this some other way too."

## TOKEN ROLES

primary — direct lexical/semantic connection to the Greek token
secondary — exists only because of the Greek token's morphology (person, number, case, aspect, voice); no separate Greek word
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

## PRONOUNS AND SUBJECT/OBJECT MARKING

The Swahili finite verb fuses SM (subject marker) + TAM (tense/aspect marker) + optional OM (object marker) + root + optional extensions + final vowel into ONE unspaced word — there is no space between these morphemes the way there is in Hausa's PAC particle.

### Subject marker (SM)
- No explicit Greek pronoun (person marked only by verb morphology): the SM is SECONDARY, in the same record as the verb root (primary) — the ordinary "subject pronoun from verb ending" case.
  ἠγάπησεν → "aliupenda" (he-it-loved): source=[ἠγάπησεν], target=["aliupenda"] — primary: "penda" component; secondary: "a-li-" component (single fused token, but only the verb root is primary)
- Explicit Greek nominative pronoun (ἐγώ/σύ/αὐτός/ἡμεῖς/ὑμεῖς) present: the SM aligns PRIMARY, in its OWN record, to the explicit pronoun — the verb root separately aligns primary to the verb. Do not default this to secondary or NEQ.
  Αὐτὸς... ἔλαβεν → "Ya-debi": source=[Αὐτός], target=["Ya"] — primary 1:1 component; source=[ἔλαβεν], target=["debi"] — primary 1:1
- Independent/emphatic pronouns (mimi, wewe, yeye, sisi, ninyi, wao) are real, separately alignable tokens, not fused morphology — align as ordinary pronoun correspondents. See AUTOS for the doubling pattern when the Greek pronoun is an OBJECT.

### Object marker (OM) — THREE patterns, conditioned by topicality/givenness, not by mere noun-presence
1. **OM alone, no separate object noun/pronoun token** — an established/anaphoric referent already carried by context. The OM is PRIMARY to the Greek pronoun/implied-noun token it renders (or NEQ per the "specific noun supplied from context" rule, when nothing renders it on the Greek side either).
   "alipoiona" (when-he-it-saw, referring back to a treasure mentioned earlier in the verse, no repeated noun): OM component primary to the implied referent.
2. **No OM at all, bare object noun only** — the default for a newly-introduced/indefinite referent. Treat as an ordinary primary noun record; no special handling.
3. **OM doubling an explicit, discourse-topical object noun** — the noun is marked (or discourse-established) as definite by a demonstrative, a possessive suffix, or recent anaphoric mention. The OM is SECONDARY, folded into the verb's own record (parallel to how a Greek article is secondary to its noun); the noun carries the PRIMARY link to the Greek noun.
   ἠγάπησεν τὸν κόσμον → "aliupenda ulimwengu": source=[ἠγάπησεν], target=["aliupenda"] with OM component secondary, root primary; source=[τόν, κόσμον], target=["ulimwengu"] — primary: "ulimwengu"; secondary.source: [τόν]

### Ditransitive/applicative OM tracks the RECIPIENT, not the theme
In double-object constructions (give/tell/divide X to Y), the OM consistently cross-references the recipient/beneficiary noun, even when the theme is the Greek accusative and the recipient is only dative/genitive. The recipient noun gets its own primary record; the theme noun gets a separate primary record; the OM is secondary to the verb, tracking the recipient.
  ἐδίδου τοῖς μαθηταῖς τοὺς ἄρτους → "akawapa wanafunzi... mikate": OM component ("wa-") secondary to the verb, tracking "wanafunzi" (primary, own record); "mikate" separate primary record

### Possessive pronouns are fused suffixes on the host noun
Fold into the noun's own record — not a separately alignable token, same treatment as a fused article.

## ARTICLES AND DEFINITENESS
No article of any kind exists in Swahili — not even a fused suffix like Hausa's. The Greek article (definite or absent) has NO direct Swahili correspondent to align to in the overwhelming majority of cases. This means SECONDARY, not NEQ — exactly the same treatment every other supported language gives an unmarked article (English "articular noun, no 'the'"; Hausa's fused-suffix generalization): fold the article into the noun's own record as a secondary source token, with the noun itself carrying the primary link. NEQ is reserved for genuine no-correspondence cases — e.g. the noun phrase itself is dropped/restructured away entirely — not the ordinary case of "no separate word exists for this article." Do NOT default to NEQ merely because Swahili has no article word; that default is wrong and will inflate NEQ counts across nearly every verse (Greek articles are ~14% of all NT tokens).
  ὁ λόγος → "Neno": source=[ὁ, λόγος], target=["Neno"] — primary: "Neno"; secondary.source: [ὁ]
- A demonstrative (huyo, hii, hivi...) sometimes tracks anaphoric definiteness — when present, align it per its own sense (often closer to English "the"/"that" than to the bare article, likely primary); when absent, the ordinary secondary-to-noun treatment above still applies — do not force a demonstrative that isn't there.
- The OM-doubling pattern above sometimes does real definiteness work — do not treat OM presence as tracking the Greek article; it is conditioned by Swahili-internal topicality, not by the Greek article's presence. The article is still secondary to the noun regardless of whether OM doubling is also present in that clause.

## GENITIVE / ASSOCIATIVE "-a"
The connector "-a" (surfacing as wa/cha/ya/la/za/pa... depending on the possessed noun's class) is Swahili's all-purpose genitive/associative linker — a close typological match to Greek's genitive case and to English's case-implied "of". SECONDARY, folded into the possessed noun's record; the possessor noun gets a separate primary record. The concord prefix choice (which class the -a agrees with) needs zero alignment attention — fully mechanical.
  Mwanawe wa pekee → "his only Son": "-a" component secondary within "Mwana" ("Son") record; separate record for the possessor if explicit.

## COPULA / "BE" / "HAVE"
Five distinct strategies, split by COMPLEMENT TYPE, not by whether Greek's εἰμί is morphologically present:
- `ni` — invariant identity copula. PRIMARY when Greek's εἰμί is explicit; NEQ when Greek has no copula token (ellipsis) — same rule as English's supplied copula.
- `si` — the negative counterpart, equally invariant.
- Locative/existential `-ko`/`-po`/`-mo` fused onto the copula: triggered specifically when the copula's OWN complement is (or contains) a locative/spatial expression, OR a temporary/circumstantial-state predicate (e.g. "ready") — NOT by an abstract identity-vs-existence distinction. Align as PRIMARY to Greek's εἰμί/ἦν the same as plain `ni`.
  ὁ ἐν τοῖς οὐρανοῖς ("[the one] in heaven") → "aliye mbinguni" / "yuko mbinguni" — locative copula form, no separate Greek verb token needed to license it
- `-na` ("have," conjugates directly with subject concord like an ordinary verb: wana "they have", hana "he/she doesn't have") — the productive way Swahili expresses possession. Aligns to a Greek "have"-verb (ἔχω) as an ordinary lexical correspondent.
- Emphatic identificational `ndi-` + class concord (ndiye, ndivyo, ndio) — appears specifically where Greek itself marks emphasis (a fronted/emphatic ἐγώ εἰμι, or a demonstrative-led "this is how..."). Same treatment as plain `ni` — PRIMARY — just a marked/emphatic variant, not a different function.

The `-li-` inside an "aliye"-type relative form (aliye, uliye...) needs separate treatment — see PARTICIPLE for the state-copula-vs-past-tense split.

## NEQ (NON-EQUIVALENT)
NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty, and never use it just because a grammaticalized target feature is marked some other way too.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.
- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded
The Greek article defaults to SECONDARY, not NEQ (see ARTICLES above) — the ordinary "no separate word for this" case, exactly like every other supported language. Do NOT NEQ the Greek article just because Swahili has no article word. A pure translator-supplied relative clause with no Greek relative word at all (see PARTICIPLE) is legitimate NEQ/secondary-material territory.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

"na" covers FOUR distinct functions sharing one word — disambiguate by syntactic context before aligning, do not default to "and":
1. Coordinating "and" — the ordinary καί correspondent.
2. Comitative "together with" — corresponds to Greek πρός/μετά "with" contexts, not καί.
   πρὸς τὸν θεόν ("with God") → "pamoja na Mungu": "na" component primary to πρός, not treated as "and"
3. Passive-agent marker "by" — corresponds to Greek's ὑπό + genitive agent construction, NOT a coordinating καί, even though it is the identical Swahili word. Triggered when the preceding verb is passive and the following noun is an animate/personal agent.
   ἐβαπτίσθη ὑπὸ Ἰωάννου → "akabatizwa na Yahya": "na" primary to ὑπό (agent marker), not "and"
4. Existential "have" — the "-na"/"kuwa na" construction (see COPULA above).

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE AND VERBAL EXTENSIONS

The passive suffix `-wa` is fully productive and morphologically transparent — the cleanest, most direct passive marker of any currently-supported language. Fused into the verb word; the passive sense is PRIMARY to the verb root's own record.
  ἐβαπτίσθη → "akabatizwa" (he-was-baptized): primary to the verb root

Beyond `-wa`, other verbal extensions absorb some of what Greek expresses through separate words or middle voice:
- Stative/neuter `-ika`/`-eka` — a resultative-flavored passive strategy (found/appeared, not a plain event-passive).
  εὑρέθη ἐν γαστρὶ ἔχουσα → "alionekana kuwa na mimba" ("was found to be pregnant"): "-onekana" (see-STATIVE) primary to εὑρέθη
- Applicative — cross-references the recipient in a ditransitive; see BASE_BLOCK's OM section.
- Causative `-isha`/`-esha` — a Greek periphrastic causative (command-verb + causative-used infinitive) can map onto TWO ordinary Swahili verbs, one of them causative-suffixed. No special handling needed — align each verb normally as an ordinary lexical correspondent, both primary; the causative suffix is folded into its host verb's single record.
  ἐπέταξεν αὐτοῖς ἀνακλῖναι πάντας → "akawaamuru wawaketishe watu" ("he commanded them to seat the people"): source=[ἐπέταξεν], target=["akawaamuru"] — primary; source=[ἀνακλῖναι], target=["waketishe"] — primary ("-ketisha" = "-keti" "sit" + causative "-isha")
- Reciprocal `-ana` — two sub-patterns:
  1. Genuine mutual reciprocal, sometimes DOUBLED with an external "X kwa X" phrase for the same Greek reflexive-used-reciprocally expression — both the verb-internal "-ana" and the external phrase are PRIMARY (both genuine carriers of the reciprocal sense, not one redundant).
     συζητεῖν πρὸς ἑαυτούς → "wakaulizana wao kwa wao" ("asked-each-other, they to they"): both components primary
  2. Lexicalized, non-mutual use ("-kutana" "meet [with]," from "-kuta" "find" + "-ana") — used even for one person meeting one other person, the second party marked by comitative "na", not a direct object. Align as an ordinary lexical "meet" correspondent, not as a marker requiring a plural mutual subject.
     ὑπήντησαν αὐτῷ → "wakakutana naye" ("they met with-him"): ordinary primary correspondence, "na" here is part of the lexicalized verb's argument structure, not the quadruple-duty "na" of CONJUNCTIONS AND PARTICLES.

A repeated wrinkle: when the verb's object is a CONJOINED phrase spanning two different noun classes (e.g. "loaves and fish"), the object marker defaults to class 8 "vi-" regardless of either noun's own class — a genuine default/"elsewhere" agreement for mixed-class conjunction, confirmed recurring across parallel tellings of the same narrative. Does not change the primary/secondary rule in BASE_BLOCK — just expect this concord shape for conjoined mixed-class objects.\
"""

IMPERSONAL_BLOCK = """\
## IMPERSONAL VERBS

δεῖ/ἔξεστιν/πρέπει/συμφέρει/δοκεῖ ("must," "is necessary," "is lawful," "seems") show confirmed cross-translation variation in HOW the impersonal sense is carried: a 2nd-person-plural subject marker ("you all ought") in one edition vs. an impersonal-class subject marker ("it behooves") in another, for the identical Greek clause. Both are equally valid renderings — align whichever subject-marking strategy the current edition used normally; do not expect one specific SM shape.
  Impersonal verb → Swahili equivalent — primary. Complementary infinitive aligns normally per INFINITIVAL CONSTRUCTIONS; "ku-" secondary.\
"""

PARTICIPLE_BLOCK = """\
## RELATIVE CLAUSES / SUBSTANTIVE PARTICIPLES

No participle morphology; Greek's substantive/attributive participles AND ordinary relative clauses both funnel into Swahili's relative system. THREE coexisting strategies, all common — determine which the translator used; do not assume one default.

### 1. Infixed relative concord inside a largely tenseless verb form
  ὁ πιστεύων εἰς αὐτόν → "amwaminiye" (a-mw-amini-ye, SM-OM-believe-REL): relative concord component primary to the Greek relative word (article/participle); OM component per BASE_BLOCK's OM rule; verb root primary.

### 2. Invariable particle `amba-` + relative concord suffix
Confirmed as common as the infixed strategy at corpus scale — NOT a marginal alternative. One clean predictor found: Greek relative ADVERBS (ὅπου "where," ὅθεν "whence") consistently trigger `amba-` LOCATIVE forms (ambako/ambapo/ambamo), where an ordinary relative PRONOUN in the SAME sentence gets the infixed strategy instead.
  ὅπου ἦν Λάζαρος (place-relative) → "ambako": primary to ὅπου
  ὅν ἤγειρεν (pronoun-relative, same verse) → "aliyekuwa amefufuliwa": infixed strategy, primary to ὅν
A second, independent trigger: `amba-` is also used for pure translator-supplied discourse restructuring with NO Greek relative word at all (a bare prepositional phrase or genitive noun phrase expanded into a full relative clause). In these cases the Swahili relative word is NEQ or generous-alignment secondary material tied to the noun/preposition it restructures — not forced onto a nonexistent Greek relative pronoun.
Beyond these two triggers, the choice between infixed and `amba-` is stylistic (can even appear stacked back-to-back on the same head noun) — do not hunt for further grammatical conditioning; align what the translator did either way: relative concord primary when a genuine Greek relative word (pronoun or adverb) triggers it; NEQ when it is pure restructuring; verb root primary; OM per BASE_BLOCK.

### 3. The "having/possessing" relative `-enye`
Confirmed keyed to a SEMANTIC FRAME — "characterized by/having a quality or possession" — rather than to Greek's own surface part of speech. Wins even when Greek encodes the identical sense as a genuine finite relative clause built on ἔχω, not just when Greek uses a bare adjective or participle.
  λεπρός ("leper," adjective) → "mwenye ukoma" ("having leprosy"): both components primary to λεπρός, parallel to a compound-lexical-item split (§8.1-style: multiple target words, all primary, to one source token)
  οἱ πεινῶντες καὶ διψῶντες ("those hungering and thirsting," participles) → "wenye njaa na kiu" ("having hunger and thirst")
  ἄνθρωπος ὃς ἕξει πρόβατον ("a man who will have a sheep" — a GENUINE Greek relative clause with finite ἔχω) → "mwenye kondoo wake" — STILL `-enye`, not a verbal relative clause with a Swahili "have"-verb.
Genuinely eventive/action relative clauses (who did/does/will do something, not "who has/is characterized by X") get strategy 1 or 2 instead, never `-enye`.

### The `-li-` inside an "aliye"-type relative form splits by what follows it
- `-li-` + adjective/locative/PP predicate (aliye na, aliye hai, aliye mbinguni, aliye mkuu...) — a TENSELESS state-copula relative, confirmed against Greek constructions that carry no tense element at all (the bare substantival article+locative pattern τὸν/τοῦ ἐν [τοῖς] οὐρανοῖς has no verb or tense in the Greek at all). The relative concord is primary to whatever Greek article/substantival construction licenses it; the `-li-` itself contributes no independent tense meaning to align against.
- `-li-` + fused verb root (aliyekuwa, aliyeitwa, aliyezaliwa...) — a GENUINE past-tense relative, matching Greek aorist/perfect/imperfect forms. `-li-` folds into the verb's own record like any other TAM marker.

### Discourse particle adjacent to a relative/participial construction
δέ/καί/οὖν with no correspondent → NEQ source (only when certain).\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

Swahili DOES have a true infinitive — class 15 `ku-` + verb stem — unlike Indonesian, Hindi, Arabic, and Hausa. Behaves closely to the ordinary infinitive rules: infinitive primary; `ku-` secondary (parallel to English "to").
  λαβεῖν → "kuchukua": source=[λαβεῖν], target=["kuchukua"] — primary: verb-root component; secondary: "ku-" component

### Nominal duality
Class 15 `ku-` infinitives are simultaneously infinitives AND ordinary class-15 nouns (taking class-15 concord, e.g. a class-15 possessive "kwake" = "of-his"). This can recur on a Greek genitive absolute or articular infinitive the same two-track way English's own articular-infinitive treatment splits: bare-infinitive-as-noun (secondary `ku-`) vs. explicit nominalization (a supplied nominalizing noun, primary, alongside the infinitive, also primary).
  Kuzaliwa kwake ("the birth of him" = "his birth") → source=[τό, γεννηθῆναι] or equivalent genitive-absolute construction, target=["Kuzaliwa", "kwake"] — primary: "Kuzaliwa"; class-15 possessive concord "kwake" secondary/primary per the specific construction (treat like a possessive-marked noun record, not a bare infinitive record).\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

`ili` + subjunctive (final vowel "-e", no TAM marker) is the standard purpose conjunction — primary 1:1 to ἵνα; the subjunctive verb aligns primary.
  ἵνα... μὴ ἀπόληται → "ili... asipotee": source=[ἵνα], target=["ili"] — primary 1:1

A confirmed periphrastic variant: `-pata` ("get/obtain," subjunctive) + infinitive distributes real "come to/manage to" semantic content across TWO Swahili words for a single Greek subjunctive verb — both words primary to that Greek verb, not one secondary to the other (parallel to the base principles' verbal-aspect distribution pattern).
  ἵνα... εἰδῆτε → "ili... mpate kujua" ("so that you may get to know"): source=[εἰδῆτε], target=["mpate", "kujua"] — both primary; "ku-" secondary within "kujua"\
"""

COMPARATIVE_BLOCK = """\
## COMPARATIVES AND SUPERLATIVES

No synthetic comparative/superlative morphology at all — Swahili has no "-er"/"-est" equivalent. `kuliko` ("than") is the universal comparison particle, following a plain adjective.
  μείζων Ἰωάννου → "mkuu kuliko Yahya": source=[μείζων], target=["mkuu", "kuliko"] — both primary; source=[Ἰωάννου], target=["Yahya"] — primary 1:1

Comparison can be TWO-PART: `kuliko` paired with an analytic intensifier `zaidi` ("more") on the adjective/predicate itself — confirmed OPTIONAL, not obligatory, for the same comparative category. When present, `zaidi` and the adjective are both primary to the single Greek comparative token, alongside `kuliko`.
  εὐκοπώτερόν... ἢ... → "rahisi zaidi... kuliko...": source=[εὐκοπώτερον], target=["rahisi", "zaidi"] — both primary; source=[ἤ], target=["kuliko"] — primary 1:1

Superlative is NOT a separate construction — `kuliko wote` ("than all") is ordinary `kuliko` with "all" as the standard of comparison.
  nani aliye mkuu κuliko wote → source=[superlative Greek form], target=["mkuu", "kuliko", "wote"] — all primary

Elative superlative uses `kabisa` ("very/utterly/completely") — primary, in the same record as the adjective it intensifies.
  aliye mdogo kabisa ("the least," lit. "very small") → "kabisa" primary alongside the adjective\
"""

AUTOS_BLOCK = """\
## αὐτός

When the Greek pronoun (αὐτός used non-intensively, ἐμέ, σε, etc.) is a GREEK OBJECT, Swahili doubles it near-categorically: the object marker (OM) fused in the verb AND an independent pronoun (mimi, wewe, yeye, sisi, ninyi, wao) both appear — BOTH PRIMARY in the same record (a multi-primary target-token record), not one secondary to the other. This is a cleaner, more automatic pattern than the topicality-conditioned noun-doubling case in BASE_BLOCK, and is NOT the same as a plain 1:1 pronoun treatment.
  ᾔτησας αὐτόν → "ungelimwomba yeye": source=[αὐτόν], target=["mwomba" OM component, "yeye"] — both primary
  πιστεύων εἰς ἐμέ → "aniaminiye mimi": source=[ἐμέ], target=["ni-" OM component, "mimi"] — both primary

Third-person SUBJECT pronoun (αὐτός non-intensive, subject position): the subject marker (SM) fused in the verb aligns primary to the explicit Greek pronoun, per BASE_BLOCK's SM rule — no independent pronoun is added unless the discourse is contrastive/topicalized.

Intensive/reflexive uses of αὐτός not yet independently attested in this config — if encountered, apply the practical test (what Greek word explains this Swahili word's presence) rather than assuming a fixed correspondent.\
"""

HOTI_BLOCK = """\
## ὅτι

THREE coexisting content-clause complementizers — determine which the current edition used; `kwamba` is the majority but not the only valid option.
- `kwamba` — the majority strategy (confirmed at roughly 700 corpus instances). Primary 1:1 to ὅτι.
  ἵνα... εἰδῆτε ὅτι... → "ili... kujua kwamba...": source=[ὅτι], target=["kwamba"] — primary 1:1
- `ya kwamba` — a fuller cross-translation variant of the same complementizer, same treatment; "ya" folds in as part of the complementizer, not a separately-decided token.
- Bare `kuwa` — confirmed real but a genuine MINORITY (roughly a tenth of `kwamba`'s frequency). Same treatment: primary 1:1 to ὅτι.
  ἔγνωσαν ὅτι... → "walimjua kuwa...": source=[ὅτι], target=["kuwa"] — primary 1:1

CRITICAL DISAMBIGUATION: the fixed idiom `kwa kuwa` ("because") is a SEPARATE causal construction (matching causal ὅτι/γάρ, "for/because"), structurally `kwa` ("for") + `kuwa` fused into one causal conjunction — NOT an instance of the content-clause complementizer, despite sharing the string `kuwa`. Align `kwa kuwa` as a unit, primary to causal ὅτι/γάρ; do not split it into a stray locative/instrumental `kwa` plus a complementizer `kuwa`.
  ὅτι (causal, "because/for") → "kwa kuwa...": source=[ὅτι], target=["kwa", "kuwa"] — both primary, one unit

Recitative ὅτι (introduces direct speech) → NEQ, exactly as in English — confirmed against multiple sampled instances with no Swahili correspondent of any kind beyond quotation marks.
  λέγων ὅτι "..." → source=[ὅτι] → NEQ; the quote follows with no complementizer\
"""

CONDITIONAL_BLOCK = """\
## CONDITIONAL CONSTRUCTIONS

εἰ/ἐάν (real/open conditions): THREE coexisting Swahili strategies, confirmed via direct same-verse cross-translation contrasts — treat all three as equally valid regardless of which one the current edition used; do not expect a single default.
1. `kama`/`ikiwa` + plain indicative verb, no TAM conditional marking at all. The conditional force rides entirely on the conjunction.
   Εἰ... σκανδαλίζει → "Ikiwa... unakusababisha": source=[εἰ], target=["Ikiwa"] — primary 1:1
2. Negative conditional-relative infix `-sipo-` (`-si-` negation + `-po-` conditional/locative-relative), NO separate conjunction — the conditional force is carried entirely by the verb's own fused morphology.
   ἐὰν μή τις γεννηθῇ → "Mtu asipozaliwa": source=[ἐάν, μή], target=["-sipo-" component] — primary, fused within the verb word
3. Positive `-ki-` infix, NO conjunction (sometimes paired with concessive `hata` "even").
   Εἰ... σκανδαλίζει → "...ukikukosesha": source=[εἰ], target=["-ki-" component] — primary, fused within the verb word
   κἂν ἀποθάνῃ → "hata akifa": source=[κἄν], target=["hata", "-ki-" component] — both primary

Whichever strategy is used, the element(s) carrying the conditional force (kama/ikiwa/hata and/or the -ki-/-sipo- infix) align primary to Greek εἰ/ἐάν (and to μή within it, when the infix itself is negative).

Counterfactuals: `-nge-`/`-ngeli-` and `-ngali-` are BOTH confirmed to render the IDENTICAL unreal-past Greek condition in different editions of the same verse — this is free stylistic variation, NOT a present-vs-past split. Do not tense-condition which one to expect; align either the same way, primary to εἰ/ἐάν and to whatever marks the counterfactual force on the Greek side (imperfect+ἄν, aorist+ἄν, etc.).
  εἰ ἦς ὧδε, οὐκ ἂν ἀπέθανεν → "ungalikuwa hapa... hangalikufa" (one edition) / "ungekuwa hapa... hangekufa" (another edition, same verse) — both are the SAME valid rendering strategy for the SAME Greek condition\
"""

NEGATION_BLOCK = """\
## NEGATION

TAM-conditioned and largely fused/circumfixal, not a single free particle. Locate the negative morpheme inside the fused verb word even when no separate space-delimited "not"-word is present.

### Negative subject-marker set (ha- + tense-specific marking)
Obligatorily co-occurs with tense-specific post-marking, e.g. the negative perfect uses `-ja-` ("not yet"), contrasting with the positive `-me-`.
  hana → "he/she has not" (negative of -na "have"): "ha-" component primary to Greek negation
  hajakuwa → "had not yet been/existed": "ha-...-ja-" components primary to Greek negation; verb root separate

### Subjunctive/purpose-clause negation — a DISTINCT infix `-si-`
Not a simple insertion of the ordinary negative marker into the subjunctive form — its own paradigm, with a final-vowel change to "-e".
  ἵνα μὴ ἀπόληται → "asipotee" (so that he might not perish): "-si-" component primary to μή, fused within the verb; final-vowel "-e" is part of the subjunctive, not separately aligned

### Copula negation is the separate invariant word `si`
See BASE_BLOCK's COPULA section — not a ha-/TAM-conditioned verb form at all.
  οὐκ ἔστιν → "si...": primary 1:1, invariant word

Each negative marker — wherever it surfaces in the fused verb word — aligns as its own PRIMARY record against the Greek negation particle (οὐ/οὐκ/μή/οὐ μή etc.), the same treatment given a free-standing "not," even when the Swahili marker is not a separate space-delimited token. Emphatic negation (οὐ μή) not yet independently attested in this config.\
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
    "HINA": {"INFINITIVE"},
}

SWH_CONFIG = LanguagePromptConfig(
    language_code="swh",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(SWH_CONFIG)
