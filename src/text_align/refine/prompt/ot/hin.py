"""Hindi target-language prompt config for OT (Hebrew) refine-alignment.

Distilled from `docs/alignment-principles-ot.hin.md`, itself seeded from the
confirmed NT Hindi findings (`docs/alignment-principles-nt.hin.md`), spot-checked
against `WLCM.tsv` joined to `ot_IRVHin.tsv` (~15 verses: Genesis 1:1, 1:27, 2:5, 2:23,
3:1, 8:12, 8:21, 9:11, 11:30, 21:5; Joshua 1:1; Psalm 23:1; Isaiah 53:5), then put
through a follow-up two-part verification pass: (1) cross-translation checked against
OHCV (full OT coverage) and GLT (partial OT coverage — Ruth, Ezra, Nehemiah, Esther,
Obadiah, Jonah; GST deliberately excluded), and (2) corpus-scale checked against
WLCM.tsv+IRVHin for sections that were previously untested hypotheses or backed by only
a handful of examples.

A third, targeted follow-up pass then closed out nearly every remaining open item:
verb-suffix/preposition-suffix reflexives, 3+-link construct chains, existential אֵין
at scale, the -कर conjunctive participle's Hebrew trigger, the theological/divine
passive hypothesis (corrected), passive Strategy 7's rarity, and the נָשָׂא פָּנִים
idiom search.

**Draft status:** corpus-scale and cross-translation checked across three passes, not
yet native-speaker reviewed. See the principles doc's "Cross-translation methodology
note" and "Open questions" for what remains — mostly fine-grained items not resolvable
by corpus analysis (the जब तक...न-for-עַד question, bare noun-noun construct-chain
juxtaposition) plus native-speaker review itself.

Key differences from OT English and OT Indonesian:
  BASE_BLOCK — no articles (like Indonesian), but Hindi has grammatical gender and an
                inflecting genitive postposition (का/की/के, agreeing with the
                POSSESSED noun, not the possessor) — the mechanism behind both
                CONSTRUCT CHAINS and the pronominal-suffix agreement pattern. Two
                case-marking postpositions have NO Hebrew trigger at all: ergative ने
                (perfective-transitive subject — confirmed firing on every checked
                instance) and को as differential object marking (DOM) on a
                definite/animate direct object — confirmed real by cross-checking OHCV,
                which uses को on the same direct objects IRVHin renders with an
                objective genitive (see below) — even alongside a light-verb rendering
                in one case. Finite verbs are almost always periphrastic (participle +
                copula) by default.
  CONSTRUCT CHAINS / GENITIVE — का/की/के secondary to the possessed noun, confirmed at
                corpus scale (21/21 clean instances) against real construct chains
                (यहोवा के दास "servant of the LORD," नून का पुत्र "son of Nun"). के
                (not का) is used when the possessed noun is mid-chain, followed by an
                appositive name/title — confirmed 2-translation (नून के पुत्र यहोशू,
                and GLT's independent यहूदा के बैतलहम का एक पुरुष). **Correction**: an
                earlier draft claimed IRVHin's objective-genitive-का/की pattern for
                light-verb direct objects (सृष्टि की, रचना की, नाश करने के लिये,
                confirmed 4+ times within IRVHin) was a general Hindi-OT strategy —
                cross-checking OHCV disproves this: OHCV uses ordinary DOM-को on the
                identical direct objects instead. Treat का/की-on-light-verb-object as
                IRVHin's own confirmed choice, not a translation-general rule — check
                को first in any other Hindi OT edition.
  PRONOMINAL SUFFIXES — free-standing possessive/object pronouns (मेरा, उसकी), NOT
                fused clitics the way Indonesian's -ku/-mu/-nya are — confirmed
                (मेरा चरवाहा, मेरी हड्डियों). Reflexive अपना/अपने/अपनी when the suffix's
                referent is coreferential with the clause's subject (בְּצַלְמוֹ →
                "अपने स्वरूप में," not "उसके स्वरूप में") — confirmed well beyond the
                single original example, via the "gathered to his people" death
                formula, the "hardened his heart" idiom, and now true verb-suffix
                (18/18 clean → अपने को/अपने लिये) and preposition-suffix (real, but
                often absorbed into a vector verb with no separate word) reflexives
                too. A previously undocumented intensive/agentive reflexive strategy,
                आप (ही) ("he himself will provide"), was also found — distinct from
                अपना's possessive reflexive.
  NEGATION_BLOCK — नहीं/न split by discourse function, not mood, confirmed with both
                indicative and modal contexts. **OT-specific correction**: unlike the
                NT config's near-parity between नहीं and न, the OT's full-corpus counts
                (नहीं 2,334, न 5,128) show न outnumbering नहीं more than 2:1, likely a
                poetry/parallelism effect — do not assume the NT's balance carries
                over. לֹא...עוֹד ("no longer") is discontinuous (फिर...न, confirmed at
                ~82% in a corpus-scale re-sample, plus a newly documented आगे को
                variant), paralleling the NT config's οὐκέτι/μηκέτι finding and OT
                Indonesian's parallel finding. Existential אֵין is NOT a fixed idiom
                (unlike Indonesian's "tidak ada") — confirmed at corpus scale (785
                true instances) it renders as a flexible नहीं/न + tense-agreeing
                था/हुआ construction, with कोई as a common (not universal) companion
                word for personal referents, still 1:N to אֵין. The -कर conjunctive
                participle's Hebrew trigger is now confirmed too: Hebrew's wayyiqtol
                (waw-consecutive) narrative chain, near-exceptionless — IRVHin
                converbializes all-but-the-last verb of a narrative sequence into -कर.
  PASSIVE VOICE (folded into BASE_BLOCK — no phenomenon-detection hook exists for OT
                passive stems) — 7 of 8 strategies from the NT config now confirmed
                with real Niphal/Pual/Hophal examples: periphrastic जाना (कुचला गया,
                घायल किया गया), the "it is written" (כָּתוּב) stative-perfect (bare
                participle+है for the citation formula; participle+हुआ+copula for
                physical inscription — two context-conditioned sub-patterns), adjectival
                resultative + होना (चंगे हो जाएँ for נִרְפָּא — a 3-way cross-testament
                AND cross-translation match after OHCV independently confirmed it),
                dedicated intransitive verbs (न मिला), light-verb+होना without जाना
                (चोट खाए, आशीष पाए — पाना is a newly documented auxiliary), bare
                resultative participle (पके हुए), a plausible active-voice-conversion
                instance, and naming/equational conversion (नाम...होगा for יִקָּרֵא,
                though confirmed translation-dependent — OHCV instead keeps a
                periphrastic passive verb on the same verse). Strategy 7 (active-voice
                conversion) remains genuinely rare — a dedicated 30-instance follow-up
                search found no additional examples beyond the single Lev 5:23 case.
                The theological/divine-passive hypothesis (supplied परमेश्वर as agent
                of an unstated-agent passive) was checked and NOT supported by real
                text — what recurs instead is a distinct supplied-pronoun-referent
                phenomenon (परमेश्वर supplied to disambiguate an ambiguous 3rd-person
                pronoun/suffix from context), not a passive-specific rule.
  PARTICIPLE_BLOCK — जो/वाला substantive-participle split confirmed at corpus scale
                (जो ~55%, वाला ~10%, a "neither"/bare-noun-or-finite-clause outcome
                ~32% — larger than the NT document found, so check for a natural
                lexicalized noun before defaulting to जो/वाला). Participle+הָיָה
                periphrastic construction also confirmed (verb+था/रहा था).
  INFINITIVE_BLOCK — לְ + infinitive construct → के लिये/को PRIMARY (not secondary,
                unlike Greek "to"). **Correction**: an earlier draft treated के लिये as
                the confirmed default from 2 examples; a corpus-scale sample (excluding
                לֵאמֹר "saying," which almost always maps to कि instead) found को
                (40%) at least as common as के लिये (24%) — check the specific verse,
                do not default to के लिये. Infinitive absolute + cognate finite verb
                confirmed with निश्चय specifically as the recurring emphasis word.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language
from .eng import BLOCK_ORDER, FORCED_INCLUSIONS


# ---------------------------------------------------------------------------
# Hindi-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Hebrew source
text (MACULA Hebrew / Westminster Leningrad Codex).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s) are behind this translation word.

## HEBREW WORD-PART TOKENS
MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own BCVWP ID:
- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

Word-part present → align Hindi correspondent primary to that token. No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists only because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness), or because Hindi's own grammar obligatorily requires a word with no separate Hebrew word behind it
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- Subject pronoun — Hindi verbs agree in gender/number but not richly in person; pro-drop is discourse-driven (topic continuity), not grammar-guaranteed. Supplied on a new/switched subject → secondary. Dropped for topic continuity → none expected, leave unrecorded.

- Periphrastic finite verb (participle + copula) — the DEFAULT paradigm for present, imperfect, and several other tenses, not optional style. Participle primary; copula secondary.

- Light verb (noun/adjective + करना/होना/देना/रखना) — a Hebrew verb with no simple Hindi verbal root is rendered as noun + light verb. Both words primary, N:1 against the single Hebrew token.
  בָּרָא (created) → "सृष्टि की"/"रचना की": both primary.

- Vector/compound verb (V1 main verb + V2 aspectual auxiliary — देना, लेना, जाना, डालना, बैठना, पड़ना) — V1 primary; V2 secondary (marks completion/suddenness/benefit).

- Conjunctive/perfective participle (verb stem + कर) — CONFIRMED trigger: Hebrew's wayyiqtol (waw-consecutive) narrative chain, near-exceptionless. IRVHin systematically converbializes all-but-the-last verb of a Hebrew narrative verb sequence into -कर, keeping only the final verb finite (e.g. a three-verb chain "arose/came/said" → first finite, second -कर, third finite). Primary alone, no supplied conjunction needed.

- No indefinite article — bare noun is the default, matching Hebrew's own lack of one. Only when एक ("one") is explicitly supplied for emphasis/specificity is it secondary.

- Ergative ने — marks the subject of a transitive verb in the perfective aspect. NO Hebrew trigger at all (Hebrew has no ergativity) — purely a Hindi-grammar requirement — but still secondary to the subject noun/pronoun, never NEQ. Confirmed firing on every checked perfective-transitive subject (परमेश्वर ने सृष्टि की, आदम ने कहा, यहोवा ने कहा).

- को — dative (indirect object, case-implied from a Hebrew לְ-marked indirect object) is secondary to the noun. Differential object marking (DOM) on a definite/animate direct object has no Hebrew trigger at all (Hebrew marks direct objects with אֶת regardless of definiteness/animacy) but is still secondary, not NEQ, when it does occur — confirmed real (cross-translation check against OHCV) and can occur even when the Hebrew verb is rendered as a Hindi light verb. IRVHin itself has a confirmed tendency to instead mark the direct object of a light-verb rendering with an objective genitive का/की on the light-verb noun (see GENITIVE POSTPOSITION below) — but this is IRVHin's own lexical choice, not a rule that rules out को; check which pattern the source text actually uses rather than assuming.

- Genitive postposition का/की/के — inflects for gender/number/case of the POSSESSED noun (not the possessor), unlike a simple case-implied preposition. Case-implied secondary to the possessed noun for an ordinary Hebrew construct-chain relationship, or to the light-verb noun for an objective genitive marking a direct object (see GENITIVE POSTPOSITION AND CONSTRUCT CHAINS below).

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases — including when the direct object it marks is otherwise rendered with का/की on a light-verb noun (की's source anchor is the light-verb-object relationship, not אֶת itself).
Supplied copula ("है"/"हूँ"/"हैं") with no Hebrew verb token → NEQ target (verbless clause). Copula ellipsis after नहीं in predicate-nominal/adjectival clauses is normal Hindi grammar, not a gap to fill.
ने and को-as-DOM are never NEQ even with no Hebrew trigger — secondary to the noun phrase they mark, since that noun phrase is itself the source anchor.
Waw conjunction + Hindi asyndeton → waw word-part NEQ source. Hindi conjunction with no Hebrew conjunction token → NEQ target.
A parenthetical cross-reference (e.g. "(यहोवा 1:10)") → NEQ target. IRVHin appends these in both testaments.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Combine into N:M records only when tokens form an inseparable semantic unit (idiom, light verb, vector verb) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (periphrastic copula, ergative ने, DOM को, vector verb, reinstated demonstrative) are secondary to the source token or word-part whose grammar requires them — not NEQ.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
DEFAULT → Branch B: no separate word at all — noun stands bare, article secondary to the noun's own record, no target word required. Confirmed as the overwhelming majority case (आकाश, पृथ्वी, स्त्री, वाटिका all bare, no exceptions in the sample checked); a precise ratio is out of reach without token-level data (the same वह/वे pronoun-homonymy confound the NT config has), but Branch B is solidly the default.
MINORITY → Branch A: यह (proximal) or वह (distal) supplied, primary 1:1, noun in its own record — typically a second/later mention.

Check for an explicit Hebrew demonstrative pronoun (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) before assuming यह/वह is the article's own Branch A correspondent. OT Hebrew commonly follows an articular noun with a separate demonstrative-pronoun word to form "that/this X" (הָאִישׁ הַהוּא, lit. "the man, the that-one" = "that man") — a real, distinct token, confirmed productive (Gen 1:12/10:11 הָאָרֶץ הַהִוא → "उस देश," Gen 12:7 הָאָרֶץ הַזֹּאת → "यह देश"). When यह/वह corresponds to one of these, align it to THAT token, not the article (which stays Branch B). Distinguish from a separate, also-real predicative "X is the one that..." use of the same pronouns — only the noun-phrase-internal (attributive) use triggers this rule.

### Branch A — article has a distinct Hindi correspondent
  הָאָרֶץ הַהִוא (confirmed, "that land") → "उस देश": source=[articlePart] — no target correspondent (Branch B, secondary to the noun); source=[אֶרֶץ], target=["देश"] — primary 1:1; source=[הִוא], target=["उस"] — primary 1:1 (the demonstrative pronoun, not the article, is उस's real correspondent).
  הָאָרֶץ הַזֹּאת (confirmed, "this land") → "यह देश": same pattern, source=[זֹּאת], target=["यह"] — primary 1:1.

### Branch B — no distinct Hindi correspondent → secondary, no target word
  Articular noun, bare in Hindi: source=[articlePart, אָרֶץ], target=["पृथ्वी"] — primary: "पृथ्वी"; secondary.source: [articlePart].
  Construct-chain absolute noun with article: का/की/के construction already carries the relationship; article stays secondary with no separate word.

### Anarthrous noun
No Hebrew article token, and Hindi has no indefinite article — bare noun, no secondary needed unless एक is explicitly supplied.

## GENITIVE POSTPOSITION AND CONSTRUCT CHAINS
A Hebrew construct chain expresses genitive by word order and construct form — no preposition token. Hindi renders it with का/की/के, which inflects for the gender/number/case of the POSSESSED noun (the noun preceding it in Hindi word order), not the possessor — secondary to the possessed noun, since there is no separate Hebrew preposition token for it to be primary to. Confirmed at corpus scale (21/21 clean instances across several books), no bare noun-noun juxtaposition counter-example found.
  עֶבֶד יְהוָה "servant of the LORD" → "यहोवा के दास": source=[עֶבֶד], target=["दास"] — primary: "दास"; secondary: "के" (agrees with masculine दास); source=[יְהוָה], target=["यहोवा"] — primary 1:1.
  בִּן נוּן "son of Nun" → "नून का पुत्र": source=[בִּן], target=["पुत्र"] — primary: "पुत्र"; secondary: "का"; source=[נוּן], target=["नून"] — primary 1:1.
Refinement (confirmed 2-translation): के, not का, is used when the possessed noun is mid-chain and immediately followed by an appositive name/title (नून के पुत्र यहोशू, "Joshua son of Nun" — another name follows) — bare का/की still applies when the possessed noun is chain-final with nothing else following. This is a position-sensitive layer on top of the ordinary agreement rule, not a contradiction of it.
Construct chains of three or more links: CONFIRMED, align each link individually; each का/की/के secondary to the construct noun it follows and agrees with its gender (e.g. "hand of king of Assyria" → "अश्शूर के राजा के हाथ से," two chained के's). Caution: an apparent 3-link chain often collapses to fewer links in Hindi via lexicalization — "sons of X" (בְּנֵי) routinely renders as a single demonym/gentilic noun + one postposition (इस्राएलियों की मण्डली, not two postpositions), and idioms like "all the days of the life of X" collapse to "X की कुल आयु" — these collapses don't mean the agreement rule breaks, just that fewer Hindi links are needed.
Construct definiteness: the Hebrew article word-part on the genitive (absolute) noun stays secondary per ARTICLES Branch B — no extra word needed even when the article marks the whole chain as definite.

**Objective genitive with a light verb (direct objects, not construct chains) — IRVHin-specific, not a general Hindi-OT rule.** When a Hebrew transitive verb is rendered as a Hindi light verb (noun + करना), IRVHin's own confirmed pattern (4+ instances) has its direct object (often אֶת-marked) take का/की on the light-verb noun — the same postposition, but marking an objective-genitive relationship to the light-verb noun rather than a construct-chain possessor. IMPORTANT: cross-checking OHCV on the same verses shows this is IRVHin's own lexical choice, not a translation-general strategy — OHCV uses ordinary DOM-को on the identical direct objects instead, including in one case where OHCV *also* uses a light-verb rendering but still marks the object with को, not का. Check which pattern the specific translation in hand actually uses; do not assume का/की excludes को.
  אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ (objects of בָּרָא "created") → IRVHin "आकाश और पृथ्वी की सृष्टि की" (की marks both nouns as the objective genitive of सृष्टि, the light-verb noun; אֵת → NEQ source) vs. OHCV "आकाश एवं पृथ्वी को रचा" (ordinary verb + DOM को).
  אֶת־הָאָדָם (object of בָּרָא) → IRVHin "मनुष्य की रचना की".
  הָאָרֶץ (object of לְשַׁחֵת, a light-verb infinitive) → IRVHin "पृथ्वी का नाश करने के लिये" vs. OHCV "पृथ्वी को...नाश करूंगा" (को even with a light-verb rendering).

## INSEPARABLE PREPOSITIONS
Preposition word-part → Hindi preposition/postposition (में, को, से, के साथ, जैसा): primary 1:1. Merged article in the same token has no separate Hindi correspondent beyond the ordinary Branch B treatment.
  בַּשָּׁמַיִם "in the heavens" (single merged token) → "स्वर्ग में": source=[bashamayimId], target=["स्वर्ग", "में"] — primary: "स्वर्ग", "में".
מִן ("from") independent word → "से" primary 1:1; attached prefix מִ/מִּ follows the same rules as other inseparable prepositions.

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "और"/"परन्तु"/"तब"/"तो"/"इसलिये": primary 1:1. Asyndeton → NEQ source.
- כִּי — CONFIRMED at corpus scale: polyfunctional (causal, content-clause, conditional, temporal, emphatic, recitative); align to whichever Hindi word carries its force in context (causal → "क्योंकि", content-clause → "कि", conditional → "यदि", temporal → "जब"), confirmed with no cross-contamination in a 25-instance sample. Recitative כִּי with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — CONFIRMED at corpus scale: जो is the overwhelming default correspondent. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom marking whenever the construction is a recognized light or vector verb rather than a genuinely non-compositional phrase. Function-word-only source records are never idioms.
חָרָה אַף ("burn of nose" = anger), שׂים/שית לב ("set the heart" = pay attention), and נָשָׂא פָּנִים ("lift up the face" = show favoritism) are NOT idioms in IRVHin — all three render compositionally or via an ordinary Hindi light verb (क्रोध/कोप + भड़कना; मन लगाना/ध्यान देना/चिन्ता करना; पक्ष करना or a free paraphrase) — use ordinary/light-verb token-level treatment, not is_idiom.

## PASSIVE VOICE
Hebrew passive stems (Niphal, Pual, Hophal) map onto the same Hindi strategies used for Greek passives — identify which strategy is in play per verse rather than assuming. 7 of 8 strategies confirmed with real Hebrew examples.
1. True periphrastic passive (participle/light-verb-noun + जाना) — CONFIRMED, repeatedly: מְחֹלָל (pierced) → "घायल किया गया"; מְדֻכָּא (crushed) → "कुचला गया"; also Lev 6:23 "पहुँचाया जाए," Judg 17:2 "ले लिए गए थे". Participle/light-verb-noun primary; जाना secondary.
2. Stative-perfect (participle + copula, no जाना) — CONFIRMED, two context-conditioned sub-patterns for the recurring "it is written" (כָּתוּב) citation formula: bare participle+है/हैं ("लिखा है"/"लिखे हैं") for the rhetorical citation formula ("is it not written in the book of..."), matching the NT config's γέγραπται → लिखा है exactly; participle+हुआ+copula ("लिखा हुआ था/है") for the "written on tablets/scroll" physical-inscription sense — check which sense is in play (this second pattern is really Strategy 6, not a bare Strategy 2 instance).
3. Adjectival/nominal resultative (adjective + होना/बनना) — CONFIRMED, a 3-way cross-testament AND cross-translation match: נִרְפָּא (healed) → "चंगे हो जाएँ" (the identical mapping used for Greek ἰαθήσεται, independently confirmed by OHCV too); הִוָּלֶד (was born) → "उत्पन्न हुआ"; also Exod 4:4 "बन गई," Deut 4:26/28:24 "नाश हो जाओगे"/"हो जाएगा". Adjective primary; होना/बनना secondary.
4. Dedicated intransitive/unaccusative verb (खोलना/खुलना-type pairs) — CONFIRMED: Judg 10:7 "न मिला" (मिलना). No voice marking at all.
5. Light-verb/noun+होना idiomatic construction — CONFIRMED, multiple: Exod 22:9 "चोट खाए" (खाना), Deut 33:13 "आशीष पाए" (पाना — a light-verb auxiliary alongside होना/देना/बनना/खाना), Judg 5:20 "लड़ाई हुई," 1 Kings 8:5 "गिनती...नहीं हो सकती थी". For passives of experience, relation, communication — distinct from Strategy 1 in lacking जाना.
6. Bare resultative participle (+ हुआ/हुई/हुए, no finite copula) — CONFIRMED: Lev 7:9 "पके हुए". Attributive, not predicative.
7. Active-voice conversion — genuinely rare, still just one plausible instance (Lev 5:23, stolen-goods clause) after a dedicated 30-instance follow-up search across 7 more books found no additional examples. Real but marginal — do not expect it as a routine option; check per verse.
8. Naming/equational conversion — CONFIRMED, translation-dependent: יִקָּרֵא ("shall be called") → IRVHin "नाम...होगा" (इसका नाम नारी होगा), verb dropped entirely — but OHCV on the same verse keeps a periphrastic passive verb ("नाम दिया जायेगा," Strategy 1) instead. Check which strategy the specific translation uses.

Caution: at least one Niphal (e.g. שָׁבַע "swore," a deponent reflexive-middle) is not a real semantic passive despite the morphology — exclude deponent verbs from passive-strategy classification.

Theological/divine passive — CORRECTED, was unsupported by real text. The hypothesis that IRVHin makes an implicit divine agent of a passive verb explicit (a supplied "परमेश्वर" then NEQ target) was checked and not confirmed — passive verbs stayed passive with no agent supplied in every case sampled. What actually recurs is different: IRVHin supplies परमेश्वर/यहोवा to disambiguate an unnamed 3rd-person pronoun/suffix whose antecedent is God only from context (e.g. "in the day of his anger" → "परमेश्वर के क्रोध के दिन") — a supplied-pronoun-referent phenomenon (NEQ target per the base document's general supplied-referent rule), not tied specifically to passive voice.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Hebrew pronominal suffixes are separate word-part tokens (pos=suffix). Hindi possessive/object pronouns are ordinarily FREE-STANDING words (मेरा, तेरा, उसका, हमारा, तुम्हारा, उनका) — NOT fused clitics the way Indonesian's -ku/-mu/-nya are. Confirmed: Ps 23:1 רֹעִי "my shepherd" → "मेरा चरवाहा"; Gen 2:23 עֲצָמַי "my bones" → "मेरी हड्डियों" (agreement with possessed noun's gender, same pattern as GENITIVE POSTPOSITION).

- Possessive suffix on noun: suffix word-part → primary 1:1, Hindi possessive pronoun agreeing in gender/number with the possessed noun.
  דְּבָרוֹ "his word" → "उसका वचन": source=[davarPart], target=["वचन"] — primary 1:1; source=[sufPart], target=["उसका"] — primary 1:1.
  Suffix token absent (single token): the possessive pronoun is primary to the containing noun token.

- Reflexive अपना/अपने/अपनी when the possessor is coreferential with the clause's subject: substitute the reflexive for the ordinary third-person possessive that the suffix's own person/number would otherwise predict. Still primary 1:1 to the suffix word-part — the reflexive/non-reflexive choice is a Hindi lexical detail, not a change in which Hebrew token is the correspondent. CONFIRMED well beyond one example: the "gathered to his people" death formula (אֶל עַמָּיו) and the "hardened his heart" idiom (אֶת־לִבּוֹ) both consistently take अपने; a true verb-suffix (object fused directly onto a verb) is CONFIRMED 18/18 clean → अपने को/अपने लिये (Lev 21:4 הֵחַלּוֹ "profane himself" → "वह अपने को...अशुद्ध न करे"); a suffix on a preposition with no intervening noun is real (अपने/अपनी) but is frequently instead absorbed into a Hindi vector verb (ले) with no separate reflexive word at all (Gen 3:7 "लंगोट बना लिये," no reflexive trace) — check for vector-verb absorption before assuming a separate word is required. Caution: WLCM's "self" gloss on a suffix is not always a reliable coreference signal by itself — verify the actual clause subject.
  בְּצַלְמוֹ "in his own image" (referent = subject of the clause's verb) → "अपने स्वरूप में", NOT "उसके स्वरूप में": source=[צֶלֶם], target=["स्वरूप"] — primary 1:1; source=[sufPart], target=["अपने"] — primary 1:1.

- Intensive/agentive reflexive आप (ही) — a distinct strategy from अपना's possessive/objective reflexive, for the "by/of one's own agency" sense: "परमेश्वर...आप ही करेगा" ("he himself will provide"); "मैं अपनी ही यह शपथ खाता हूँ" ("I swear by myself," stacking अपनी + ही). Primary 1:1 to the coreferential pronoun/suffix, parallel treatment to the possessive reflexive above.

- Object suffix on verb: suffix → Hindi object pronoun (मुझे/तुझे/उसे/हमें/तुम्हें/उन्हें), or अपने को when coreferential with the clause subject (see above), or a DOM-को-marked noun phrase, primary 1:1.
  שְׁמָרֵנוּ "he kept us" → source=[shamarPart], target=["रखा"] — primary 1:1; source=[nuPart], target=["हमें"] — primary 1:1.

- Suffix on preposition: suffix → primary 1:1 to the Hindi pronoun object of the postposition, or अपने/अपनी (or vector-verb absorption with no separate word) when coreferential with the clause subject (see above).
  אֵלָיו "to him" → source=[elPart], target=["ओर"/"पास"] — primary; source=[sufPart], target=["उसकी"/"उसके"] — primary.\
"""

NEGATION_BLOCK = """\
## NEGATION

नहीं/न/मत split by discourse function, not mood — carries over from the NT config, confirmed for both indicative and modal contexts. CORRECTION: unlike the NT's near-parity between नहीं and न, the OT's full-corpus counts (नहीं 2,334, न 5,128, मत 189) show न outnumbering नहीं more than 2:1, likely a poetry/parallelism effect — treat न as the numerically dominant particle here, not a rarer variant.

- नहीं — general-purpose negator, usable with almost any verb form, though numerically less frequent than न in the OT. Confirmed: כִּי לֹא הִמְטִיר → "यहोवा...नहीं बरसाया" (indicative past).
- न — interchangeable literary variant of नहीं, and the numerically dominant particle in the OT. Confirmed with future ("मुझे कुछ घटी न होगी" for לֹא אֶחְסָר) and imperative-flavored contexts ("न खाना" for לֹא תֹאכְלוּ). Also the dedicated correlative form for "neither...nor" lists.
- मत — ordinary colloquial prohibitive, paired with an imperative or -ना infinitive. Primary 1:1 to Hebrew's jussive/imperative negation (אַל). Caution: homographic with the unrelated noun मत ("opinion") — disambiguate by syntactic position.

Simple negation (לֹא) → नहीं/न.

Existential negation (אֵין/אַיִן) — CONFIRMED at corpus scale (785 true instances): NOT a single fixed idiom. Renders as a flexible नहीं/न + tense-agreeing copula construction ("कोई...नहीं है" present-dominant, "नहीं था"/"नहीं रहा" past, "नहीं होता" habitual), matching the surrounding narrative's tense, both words primary 1:N to אֵין (parallel to base OT document's general אֵין guidance, not Indonesian's fixed "tidak ada"). कोई is a common, not universal, companion word for personal/countable referents.
  וְאָדָם אַיִן לַעֲבֹד "there was no man to work" → "मनुष्य भी नहीं था": नहीं + था, both primary 1:N.
  אֵין לָהּ וָלָד "she had no child" → "उसके सन्तान न हुई": न + हुई, both primary 1:N; לָהּ → "उसके", primary to the suffix.

### Compound negation: לֹא...עוֹד ("no longer") is DISCONTINUOUS more often than not
CONFIRMED at corpus scale: ~82% discontinuous in a fresh 25-verse sample (231 corpus-wide candidate verses), matching or exceeding the original 3-of-4/75% estimate — parallels the NT config's οὐκέτι/μηκέτι finding and OT Indonesian's confirmed לֹא...עוֹד finding. A lexical variant, आगे को, also functions alongside फिर in this slot.
  וְלֹא־יָסְפָה שׁוּב אֵלָיו עוֹד → "वह उसके पास फिर कभी लौटकर न आई": फिर separated from न by कभी लौटकर.
  לֹא אֹסִף...עוֹד → "मैं फिर कभी भूमि को श्राप न दूँगा": फिर separated from न by भूमि को श्राप.
A contiguous exception is also attested (फिर कभी न मारूँगा, all clustered) — contiguity is a real minority option, not to be assumed absent. Both words are primary to their respective Hebrew tokens (לֹא → नहीं/न, עוֹד → फिर) regardless of adjacency.

### False-friend trap — जब तक...न ("until...not")
By analogy with the NT config's confirmed finding: Hindi's "जब तक X न हो" ("until X happens") carries a न with NO Hebrew source correspondent when the Hebrew עַד ("until") clause itself carries no negation — NEQ target, not aligned to any Hebrew particle. Not yet directly confirmed for an OT עַד construction.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival participle: aligns to Hindi adjective or participial modifier, primary.
- Substantive (nominal) participle: CONFIRMED at corpus scale (40-instance sample from 1,479 article+participle pairs). जो + finite verb/relative clause dominates (~55%) when the Hebrew article word-part is present (הַשֹּׁמֵר "the one who keeps"), secondary to the participle. वाला (verb stem + वाला/वाली/वाले) is real but smaller (~10%), reserved for participles that compress into a stable, lexicalized agent-noun/role-label. A third, larger-than-expected outcome (~32%) uses neither — a plain lexicalized noun or a bare finite clause with no relativizer — check for a natural noun before defaulting to जो/वाला.
  הַשֹּׁמֵר → "जो रखवाली करता है": source=[articlePart] — secondary (Branch B, absorbed); source=[participleId], target=["जो", "रखवाली", "करता", "है"] — primary: "रखवाली", "करता"; secondary: "जो", "है".
- Verbal (predicative) participle — continuous/progressive: participle primary; Hindi progressive auxiliary (है/था/थी) secondary.
  יֹשֵׁב "was sitting" → "बैठा था": source=[participleId], target=["बैठा", "था"] — primary: "बैठा"; secondary: "था".
- Periphrastic (participle + explicit הָיָה) — CONFIRMED (112 corpus instances, spot-checked): הָיָה aligns as a primary record to the Hindi auxiliary (था/थी/थे, e.g. verb+था/रहा था); participle aligns to the main verbal element, also primary — two separate primary records, since Hindi's own periphrastic default independently supplies its own copula alongside Hebrew's.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
When לְ is a separate word-part token, it aligns to a Hindi purpose marker as PRIMARY — unlike Greek, where "to" is secondary, Hebrew's לְ is an explicit lexical morpheme. CORRECTION: an earlier draft treated के लिये as the confirmed default from 2 examples; a corpus-scale sample (excluding לֵאמֹר "saying," which almost always maps to a following कि instead) found को (40%) at least as common as के लिये (24%). Check the specific verse rather than defaulting to के लिये; the infinitive itself is also primary either way.
  לַעֲבֹד "to work" → "करने के लिये": source=[lePrepPart], target=["के", "लिये"] — primary; source=[infPart], target=["करने"] — primary.
  לְשַׁחֵת "to destroy" → "नाश करने के लिये": के लिये primary to לְ; करने primary to the infinitive (नाश की is a separate objective-genitive record — see GENITIVE POSTPOSITION AND CONSTRUCT CHAINS).

### Infinitive construct as verbal noun (בְּ + infinitive → "when/while/in ...-ing")
The infinitive aligns to the Hindi main verbal element; the preposition word-part aligns to the Hindi temporal/logical connector (जब, जैसे ही, में) as primary.

### Infinitive absolute (cognate emphasis)
CONFIRMED (12-instance sample from 433 adjacent cognate pairs). Infinitive absolute + cognate finite verb (מוֹת תָּמוּת "you shall surely die") → Hindi emphasis adverb, with निश्चय specifically the recurring choice ("तू निश्चय मरेगा," "मैं निश्चय...दूँगा") — अवश्य/ज़रूर are plausible synonyms but निश्चय is what actually recurs. निश्चय primary to the infinitive absolute; finite verb primary to the main Hindi verb — two separate primary records. If the translation absorbs the emphasis into a strong modal with no separate word, the infinitive absolute may be secondary to the finite verb, or NEQ if definitively untranslated.\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PRONOMINAL_SUFFIX": PRONOMINAL_SUFFIX_BLOCK,
    "NEGATION":          NEGATION_BLOCK,
    "PARTICIPLE":        PARTICIPLE_BLOCK,
    "INFINITIVE":        INFINITIVE_BLOCK,
}

HIN_OT_CONFIG = LanguagePromptConfig(
    language_code="hin",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(HIN_OT_CONFIG)
