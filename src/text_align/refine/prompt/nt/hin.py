"""Hindi target-language prompt config for refine-alignment.

Distilled from `docs/alignment-principles-nt.hin.md`. Examples grounded in the
Indian Revised Version Hindi (IRVHin) and checked against the actual target
TSV, then cross-checked against two further Hindi NT translations — HSB
(Hindi Standard Bible) and OHCV (Open Hindi Contemporary Version) — to
separate general Hindi grammar from IRVHin's individual stylistic choices.
See the principles doc's "Cross-translation methodology note" for what that
check changed; corrections from it are already folded into the blocks below
(e.g. the emphatic-negation and ἵνα-clause blocks list several coexisting
strategies rather than one fixed rule, because that is what survived the
cross-check).

**Draft status:** this config has not yet been reviewed by a native Hindi
speaker. Portuguese, Spanish, and French configs were validated this way
before being trusted in production; Hindi should follow the same path before
being used for real alignment runs.

Key differences from the Romance-language and Indonesian configs:
  BASE_BLOCK  — no articles (like Indonesian), but Hindi has grammatical
                gender, an inflecting genitive postposition (का/की/के, which
                agrees with the POSSESSED noun, not the possessor), and two
                case-marking postpositions with NO Greek trigger at all:
                ergative ने (marks a perfective-transitive subject — purely
                Hindi's own split-ergative requirement) and को as
                differential object marking (DOM) on a definite/animate
                direct object. Finite verbs are almost always periphrastic
                (participle + copula) as the DEFAULT paradigm, not optional
                style the way Portuguese/Spanish periphrasis is. Light verbs
                (noun + करना/होना/देना/रखना) and vector verbs (V1 + a
                semantically bleached V2 marking aspect) are both pervasive
                and easily confused — light verbs are N:1 both primary,
                vector verbs are V1 primary / V2 secondary.
  PASSIVE_BLOCK — at least six coexisting strategies (true periphrastic
                passive with जाना is the actual default, not one option
                among equals; a narrow स्थिर-perfect exception for "it is
                written"; adjectival resultative for change-of-state
                passives; Hindi's own transitive/intransitive verb pairs
                absorbing many passives with no voice marking at all;
                light-verb/noun+होना idioms for passives of experience; and
                active-voice conversion). Identify which is in play per
                verse rather than assuming one.
  PARTICIPLE_BLOCK — जो is the true majority default for substantive
                participles (tracks nothing about genericity); वाला is
                reserved for participles that compress into a stable,
                lexicalized role-label, not for generic vs. specific
                referents; a plain already-lexicalized noun can bypass the
                choice entirely.
  HINA_BLOCK  — कि/ताकि/जिससे are free stylistic variants of the same
                conjunction (not markers of different constructions or
                genres); के लिये/को both mark purpose infinitives; a
                dedicated idiom ("ऐसा न हो कि") covers negative purpose.
  NEGATION_BLOCK — नहीं/न are free variants for ordinary negation (न is not
                restricted to subjunctive/prohibitive contexts); न is also
                the dedicated correlative form for "neither...nor" lists,
                aligning 1:1 to each Greek οὐδέ/οὔτε; मत is the true
                colloquial prohibitive; emphatic negation (οὐ μή) has no
                single dedicated construction, just an optional reinforcing
                intensifier; and "जब तक...न" ("until") is a false-friend trap
                whose न has no Greek correspondent at all.

`AUTOS_BLOCK`, `COMPARATIVE_BLOCK`, `CONDITIONAL_BLOCK`, `HOTI_BLOCK`,
`IMPERSONAL_BLOCK`, and `VERBAL_ASPECT_BLOCK` are imported unchanged from
`eng.py` — no Hindi-specific mechanics were identified for these during
principles-doc research; confirm with a native speaker before assuming this
holds.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import (
    AUTOS_BLOCK,
    COMPARATIVE_BLOCK,
    CONDITIONAL_BLOCK,
    BLOCK_ORDER,
    FORCED_INCLUSIONS,
    HOTI_BLOCK,
    IMPERSONAL_BLOCK,
    VERBAL_ASPECT_BLOCK,
)


# ---------------------------------------------------------------------------
# Hindi-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied postpositions, morphologically-implied pronouns, and grammar-required copulas or vector verbs. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Combine into N:M records only when tokens form an inseparable semantic unit (idiom, light verb, vector verb) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (periphrastic copula, ergative ने, DOM को, vector verb, reinstated demonstrative) are secondary to the source token whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor at all, including postpositions that arise purely from Hindi's own verbal/case system with no Greek trigger.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Greek token
secondary — exists only because of grammatical features in the Greek token's morphology (person, number, case, aspect, voice), or because Hindi's own grammar obligatorily requires a word with no separate Greek word behind it
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- Subject pronoun — Hindi verbs mark gender/number but not richly person; a dropped subject is discourse-driven (topic continuity), not grammar-guaranteed the way Portuguese/Spanish pro-drop is. Supplied on a new/switched subject → secondary. Dropped for topic continuity → none expected, leave unrecorded.
  ἦλθεν (new subject) → "वह आया": "आया" primary; "वह" secondary

- Periphrastic finite verb (participle + copula) — the DEFAULT paradigm for present, imperfect, and several other tenses, not optional style the way Portuguese "estava fazendo" is. Participle (agrees gender/number) primary; copula (agrees person) secondary.
  ἀποστέλλω → "भेजता हूँ": "भेजता" primary; "हूँ" secondary

- Light verb (noun/adjective + करना/होना/देना/रखना) — a Sanskrit/Persian/Arabic-derived noun supplies the verbal slot for a Greek verb with no simple Hindi verbal root. Both words primary, N:1 against the single Greek verb — not secondary-marker treatment.
  σώσει → "उद्धार करेगा" (will save): both primary
  κηρύσσων → "प्रचार करता" (preaches): both primary

- Vector/compound verb (V1 main verb + V2 aspectual auxiliary from a small closed set — देना, लेना, जाना, डालना, बैठना, पड़ना) — V1 primary; V2 secondary (marks completion/suddenness/benefit, no independent lexical content in this use). Distinct from a light verb: the test is whether V2 is a semantically bleached native verb adding aspectual nuance to a fully verbal V1, not a borrowed noun's supporting verb.
  ἔδωκεν → "दे दिया" (gave): "दे" primary; "दिया" secondary

- Conjunctive/perfective participle (verb stem + कर) — renders a Greek circumstantial (typically aorist) participle directly; -कर already means "having done X," so no supplied conjunction is needed. Primary alone.
  a circumstantial participle → "निकलकर" (having gone out): primary 1:1

- No indefinite article — bare noun is the default. Only when एक ("one") is explicitly supplied for emphasis/specificity is it secondary.
  φωνή → "एक...शब्द" (a voice): "शब्द" primary; "एक" secondary

- Ergative ने — marks the subject of a transitive verb in the perfective aspect. This has NO trigger in Greek at all — purely a requirement of Hindi's own split-ergative system — but it is still secondary to the subject noun/pronoun, never NEQ.
  θεός (subject of a Greek finite verb, no ergative-triggering morphology) → "परमेश्वर ने": "परमेश्वर" primary; "ने" secondary

- को — three functions, only one purely grammar-internal: (1) dative (indirect object, or a dative-experiencer subject construction like "को अच्छा लगना," "to seem good to") — case-implied, secondary to the noun, parallel to a case-implied preposition; (2) differential object marking (DOM) on a definite/animate direct object — NO Greek correspondent at all, but still secondary to the noun it marks, not NEQ; (3) a purpose-infinitive marker (करने को), primary to ἵνα when present (के लिये is the more common choice for this — see ἵνα CLAUSES).
  ἄγγελόν (plain accusative direct object) → "दूत को" (DOM): "दूत" primary; "को" secondary

- Genitive postposition का/की/के — inflects for the gender/number/case of the POSSESSED noun (not the possessor), unlike English "'s" or a simple case-implied "of." Case-implied secondary to the possessed noun for an ordinary Greek genitive; secondary to the light-verb noun for an objective genitive ("अपने लोगों का...उद्धार करेगा," "will save his people" — का marks the logical object of the light verb उद्धार करना).
  a genitive noun + πυστυχος-type head → "भविष्यद्वक्ता की पुस्तक" (the book of the prophet): "की" secondary to पुस्तक (agrees with feminine पुस्तक, not the masculine possessor)
  Compound postpositions built on के (के लिये "for," के साथ "with," के बाद "after," के पास "near") use the fixed के form regardless of gender — align the whole compound to whatever Greek preposition/case governs it.

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Supplied copula ("है"/"हूँ"/"हैं") with no Greek εἶναι token → NEQ target. Copula ELLIPSIS after नहीं is common in predicate-nominal/adjectival clauses ("योग्य नहीं [हूँ]," "कर्जदार नहीं [हैं]") — this is normal Hindi grammar, not a gap to fill; when both Greek and Hindi omit the copula there is simply nothing to align.
ने and को-as-DOM are never NEQ even though neither has a Greek trigger — secondary to the noun phrase they mark, since that noun phrase is itself the source anchor.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment — Hindi is SOV with postpositions, so token order diverges substantially from Greek.

## DEFINITENESS AND ARTICLES

Hindi has no definite or indefinite article. For every Greek article (POS T-*): does the translation supply a distinct correspondent (a demonstrative, or a generic head noun for a substantive participle)?
DEFAULT → Branch B: no separate word at all — the noun stands bare, article secondary to the noun's own record, no target word required.
MINORITY → Branch A: यह/वह (demonstrative — typically a SECOND or later mention, not the first) primary 1:1, noun in its own record.

### Branch A — article has a distinct Hindi correspondent
  ὁ λόγος (anaphoric/repeated mention) → "वह वचन": source=[ὁ], target=["वह"] — primary 1:1; source=[λόγος], target=["वचन"] — primary 1:1

### Branch B — no distinct Hindi correspondent → secondary, no target word
  ὁ λόγος (first mention) → "वचन" — no correspondent, article absorbed
  Article before a proper name: ὁ Ἰησοῦς → "यीशु": source=[ὁ, Ἰησοῦς], target=["यीशु"] — primary: "यीशु"; secondary.source: [ὁ]

### Substantive participle (article + participle)
See PARTICIPIAL CONSTRUCTIONS for the जो/वाला/plain-noun choice.

### Anarthrous noun
No Greek article, and no Hindi indefinite article by default — bare noun, no secondary needed unless एक is explicitly supplied (see TOKEN ROLES).

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.
कि also introduces indirect discourse and direct-speech content clauses in addition to purpose/result — see ὅτι and ἵνα CLAUSES for its overlapping functions.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom marking whenever the construction is a recognized light or vector verb rather than a genuinely non-compositional phrase. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

Several strategies coexist — identify which one applies to a given verse rather than assuming.

### True periphrastic passive (participle/vector-compound + जाना) — the default for ordinary transitive verbs
Spans every tense/mood, simple verbs, causatives, light verbs, and vector-compounds alike. Participle/light-verb-noun primary; जाना (in whatever tense/mood, plus any perfect है layered on top) secondary.
  κηρυχθήσεται → "प्रचार किया जाएगा" (will be proclaimed): "प्रचार" primary; "किया जाएगा" secondary
  a causative passive → "पकड़वाया जाता है" (is betrayed): "पकड़वाया" primary; "जाता है" secondary

### Stative-perfect (participle + है, no जाना at all) — a narrow exception
Reserved for the recurring "it is written" scripture-citation formula. Do not extend to other perfect passives by default — most use जाना.
  γέγραπται → "लिखा है": source=[γέγραπται], target=["लिखा","है"] — primary: "लिखा"; secondary: "है"

### Adjectival/nominal resultative (adjective/noun + होना/बनना "become")
For passives describing a change of state or quality, no verbal passive marking anywhere in the clause. Adjective/noun primary; होना/बनना secondary.
  ἰαθήσεται → "चंगा हो जाएगा" (will be healed): "चंगा" primary; "हो जाएगा" secondary
  πληρόω/τελέω-type passive → "पूरा"/"परिपूर्ण" + होना (be fulfilled/completed): same pattern, a very stable mapping

### Dedicated intransitive/unaccusative verb — no voice marking at all
Hindi has lexicalized transitive/intransitive verb pairs the way English has "open (something)"/"(something) opens": खोलना/खुलना (open), रोकना/रुकना (hinder), उठाना/उठना (raise/rise). The Greek passive verb corresponds to the single Hindi intransitive verb, primary alone — no periphrasis at all.
  ἀνεῴχθησαν → "कब्रें खुल गईं" (tombs opened/were opened): "खुल गईं" primary alone

### Light-verb / noun + होना idiomatic construction — passives of experience, relation, communication
Noun primary; होना/देना secondary.
  καταγγέλλεται → "चर्चा हो रही है" (is being talked about/proclaimed): "चर्चा" primary; "हो रही है" secondary
  ὤφθη → "दिखाई दिया" (appeared, an experiencer-को idiom): "दिखाई" primary; "दिया" secondary

### Bare resultative participle (+ हुआ/हुई/हुए, no finite copula)
Attaches directly to its head noun as a pure attributive adjective, with no separate finite copula. Content participle primary; हुआ/हुई/हुए secondary when it is separable from the main lexical verb.
  a sacrificial-offering passive → "बलि की हुई" (having been sacrificed): "बलि की" primary; "हुई" secondary

### Active-voice conversion
A full voice flip, recasting the passive event as an active clause with a real or supplied subject. Check per verse — a passive-with-द्वारा-agent-phrase (the true periphrastic passive above, with an agent phrase added) is always an available alternative, and some translations prefer it even where another converts fully to active. The whole active verb complex aligns to the single Greek passive verb; both words primary when it is a light-verb pattern (TOKEN ROLES).
  ἐβαπτίζοντο → "से बपतिस्मा लिया" (took baptism from... = "was baptized"): both primary

### Naming/equational conversion
Some "is called" passives (κέκληται, ὀνομάζομαι-type) drop the verb entirely for a plain "X's name is Y" sentence; others keep a lexicalized verb (कहलाना, "is called/named"). Check which a given verse uses.
  κέκληται → "उसका नाम...है" (his name is...): no verb corresponding to "is called" at all\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adverbial (circumstantial) — the -कर conjunctive participle
Verb stem + कर renders a Greek circumstantial (typically aorist) participle directly — primary alone, no supplied conjunction needed, because -कर already carries "having done X."
  a circumstantial participle → "निकलकर" (having gone out): primary 1:1
If the translation instead supplies an explicit conjunction alongside a non-कर verb form ("जब...तो"), treat the conjunction as secondary to the verb, per the general pattern in the base guidelines.

### Genitive absolute
Align each element to its correspondent; any supplied conjunction/adverb is secondary to the participle; supplied subject is secondary if introducing/switching subject (see TOKEN ROLES).

### Substantive — जो / वाला / plain-noun
जो + finite verb is the true majority default, used for both generic and specific referents alike — it does not track genericity. वाला (verb stem + वाला/वाली/वाले) is reserved for participles that compress into a stable, lexicalized agent-noun or role label — a verb forming what functions almost like a title or class name; it is attested on specific individuals too, not just generic classes. Light-verb-based participles (जय पाना "to overcome," प्रेम रखना "to love") more often resist वाला-compounding and get जो instead, even in a fixed recurring refrain. When Hindi already has a plain, already-lexicalized noun for the role (पाठक "reader," किसान "farmer"), that noun can bypass the जो/वाला choice entirely — check for one before defaulting to a participial construction.
  ὁ ἔχων-type generic construction → "जिसके...हों वह...ले" (whoever has...): जो-based
  a Pauline generic-conditional participle → "जो...मानता है" (whoever esteems...): जो
  τοὺς διώκοντας → "सतानेवालों" (persecutors): वाला, a stable role-label
  ὁ βαπτίζων-type construction → "बपतिस्मा देनेवाला": source=[participle], target=["देनेवाला"] — primary (the light-verb noun बपतिस्मा gets its own separate record per TOKEN ROLES)

### Discourse particle adjacent to a participle
δέ/καί/οὖν near a participle with no correspondent → NEQ source, only when certain no element in the surrounding clause carries its force.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Hindi has a true infinitive (verb stem + ना: करना, आना, जाना). The bare infinitive is primary alone after a modal or matrix verb — no additional marker word is needed.
  θέλω ἐλθεῖν-type construction → "आना चाहता हूँ" (wants to come): "आना" primary; "चाहता हूँ" aligns to the matrix verb in its own record

### Purpose infinitive with के लिये or को
के लिये ("for," "in order to") governing an oblique infinitive (करने के लिये) carries purpose force — primary to an explicit ἵνα-type Greek purpose marker when present, or secondary to the infinitive when the purpose sense is already carried by the Greek verb alone. को can also mark a purpose infinitive (करने को) — apply the same test; के लिये is the more common choice when the specific translation's practice is unknown. See ἵνα CLAUSES.

### Indirect discourse
Supplied कि introducing an indirect statement is secondary to the governing verb of speech/perception, not to the embedded verb.
  λέγει αὐτὸν εἶναι-type construction → "कहा कि...है": "कि" secondary to the verb of saying; "है" aligns to εἶναι\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- कि / ताकि / जिससे — free stylistic variants of the same purpose/result conjunction, translator-dependent; treat identically (all primary). Do not expect genre or clause-position to predict which one appears.
  ...प्रेम रखा कि जो कोई... — "कि" primary
- इसलिए...कि — a correlative construction where इसलिए ("for this [reason]") anticipates the purpose and कि introduces it. Treat as a single primary unit against ἵνα, both words primary.
- के लिये / को + oblique infinitive — the bare purpose-infinitive strategy (see INFINITIVAL CONSTRUCTIONS): के लिये/को primary to ἵνα, not secondary to the infinitive.
- Negative purpose (ἵνα μή / μήποτε-type "lest") — a dedicated idiom: "ऐसा न हो कि" or the shortened "न हो कि." Both particles (ἵνα + μή) are primary to this idiom as a single unit. When the idiom is absent (a bare कि/यदि + negated verb instead), treat the plain negator as the correspondent.
- No correspondent → NEQ source (only when certain no element expresses purpose/result force; occasionally the whole clause is recast as an independent coordinated main clause with no subordinating marker at all — check the Greek before defaulting to NEQ).\
"""

NEGATION_BLOCK = """\
## NEGATION

नहीं and न are free stylistic variants for ordinary negation, usable with almost any verb form — indicative, future, or modal. Do NOT treat न as restricted to subjunctive or prohibitive contexts; it appears just as often with plain indicative forms. नहीं is the more common default. Copula ellipsis after नहीं is normal in predicate-nominal/adjectival clauses ("योग्य नहीं [है]") — not a gap to fill.
  ἔγνω (negated) → "नहीं पहचाना" (did not recognize): "नहीं" primary 1:1; "पहचाना" primary in its own record

न is also the dedicated form for correlative "neither...nor" lists (न...न... / न तो...न ही), aligning 1:1 to each Greek οὐδέ/οὔτε in the list — the single most reliable use of न.
  οὐκ ἐξ αἱμάτων, οὐδὲ ἐκ θελήματος σαρκός, οὐδὲ ἐκ θελήματος ἀνδρός → "न तो लहू से, न शरीर की इच्छा से, न मनुष्य की इच्छा से": each न primary 1:1 to its οὐκ/οὐδέ

मत — the ordinary colloquial prohibitive, paired with an imperative or the -ना infinitive form ("मत डरना," "मत करना"). Primary 1:1 to μή + imperative/aorist subjunctive. Caution: मत is homographic with an unrelated noun meaning "opinion/vote" — disambiguate by syntactic position (preverbal particle vs. object noun), not string match alone.

### Emphatic negation (οὐ μή)
No single dedicated construction — one of several reinforcement strategies layered onto नहीं/न, or sometimes no reinforcement at all:
- कभी / कदापि ("ever") + न/नहीं — the most common "never" strategy; कभी and कदापि are free variants.
- अनन्तकाल तक ("forever") + न — a durative-flavored strategy common in "whoever believes/drinks..." formula sayings.
- किसी रीति से / किसी प्रकार से ("by no means") + न — a modal-flavored reinforcement.
- Bare न/नहीं, no reinforcement — a legitimate, attested choice; do not force a reinforcing word that is not present in the text.
Both Greek particles (οὐ + μή) are primary in a single record against whatever Hindi words carry the emphasis — the negator plus any reinforcing word when present.

### Compound negation tokens (single Greek token → all Hindi words primary)
Expect multi-word renderings rather than a single fused lexeme in most cases: οὐδέποτε-type "never" → कभी नहीं (lit. "ever not"); οὐκέτι/μηκέτι-type "no longer" → फिर कभी (lit. "again ever").

### False-friend trap — जब तक...न ("until...not")
Hindi idiomatically expresses "until X happens" as "जब तक X न हो" (literally "as long as X does not happen, then..."). This न has NO Greek source correspondent when the Greek ἕως/ἄχρι clause carries no negative particle of its own — NEQ target, not aligned to any Greek particle. Some verses contain BOTH this idiomatic न AND a separate, genuine emphatic-negation rendering in the same sentence — do not conflate them.
  "जब तक आकाश और पृथ्वी टल न जाएँ" (idiomatic "until," न → NEQ target) "...नहीं टलेगा" (the actual οὐ μὴ παρέλθῃ rendering, नहीं primary)\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

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

HIN_CONFIG = LanguagePromptConfig(
    language_code="hin",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(HIN_CONFIG)
