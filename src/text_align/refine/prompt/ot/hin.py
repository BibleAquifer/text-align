"""Hindi target-language prompt config for OT (Hebrew) refine-alignment.

Distilled from `docs/alignment-principles-ot.hin.md`, itself seeded from the
confirmed NT Hindi findings (`docs/alignment-principles-nt.hin.md`) and spot-checked
against `WLCM.tsv` joined to `ot_IRVHin.tsv` (~15 verses: Genesis 1:1, 1:27, 2:5, 2:23,
3:1, 8:12, 8:21, 9:11, 11:30, 21:5; Joshua 1:1; Psalm 23:1; Isaiah 53:5).

**Draft status:** spot-checked, not yet cross-translation verified (GST/GLT have
partial OT coverage and could serve this role) or native-speaker reviewed. See the
principles doc's "Cross-translation methodology note" and "Open questions" for what
remains unconfirmed — most notably: the "it is written" (כָּתוּב) stative-perfect
passive, the demonstrative-after-article (הַ...הַהוּא) construction, whether DOM-को
ever occurs outside light-verb objects, and 5 of 8 passive-voice strategies.

Key differences from OT English and OT Indonesian:
  BASE_BLOCK — no articles (like Indonesian), but Hindi has grammatical gender and an
                inflecting genitive postposition (का/की/के, agreeing with the
                POSSESSED noun, not the possessor) — the mechanism behind both
                CONSTRUCT CHAINS and the pronominal-suffix agreement pattern. Two
                case-marking postpositions have NO Hebrew trigger at all: ergative ने
                (perfective-transitive subject — confirmed firing on every checked
                instance) and को as differential object marking (DOM) on a
                definite/animate direct object — though no confirmed DOM-को instance
                turned up in the spot-check; every checked direct object instead took
                the light-verb objective-genitive pattern below. Finite verbs are
                almost always periphrastic (participle + copula) by default.
  CONSTRUCT CHAINS / GENITIVE — का/की/के secondary to the possessed noun, confirmed
                against real construct chains (यहोवा के दास "servant of the LORD,"
                नून का पुत्र "son of Nun"). A new rule not present in the NT config:
                when a Hebrew transitive verb is rendered as a Hindi light verb (noun +
                करना), its direct object takes की/का on the light-verb noun rather than
                DOM को — confirmed 4+ times (सृष्टि की, रचना की, नाश करने के लिये).
  PRONOMINAL SUFFIXES — free-standing possessive/object pronouns (मेरा, उसकी), NOT
                fused clitics the way Indonesian's -ku/-mu/-nya are — confirmed
                (मेरा चरवाहा, मेरी हड्डियों). New refinement: when the suffix's referent
                is coreferential with the clause's subject, IRVHin uses the reflexive
                अपना/अपने/अपनी instead of the ordinary third-person possessive
                (בְּצַלְמוֹ → "अपने स्वरूप में," not "उसके स्वरूप में").
  NEGATION_BLOCK — नहीं/न split by discourse function, not mood, confirmed with both
                indicative and modal contexts. לֹא...עוֹד ("no longer") is discontinuous
                (फिर...न, confirmed 3 of 4 checked instances), paralleling the NT
                config's οὐκέτι/μηκέτι finding and OT Indonesian's parallel finding.
                Existential אֵין is NOT a fixed idiom (unlike Indonesian's "tidak ada")
                — it renders as a flexible नहीं/न + tense-agreeing था/हुआ, still 1:N to
                אֵין.
  PASSIVE VOICE (folded into BASE_BLOCK — no phenomenon-detection hook exists for OT
                passive stems) — 3 of 8 strategies from the NT config confirmed with
                real Niphal/Pual examples: periphrastic जाना (कुचला गया, घायल किया गया),
                adjectival resultative + होना (चंगे हो जाएँ for נִרְפָּא — the identical
                mapping the NT config uses for ἰαθήσεται), and naming/equational
                conversion (नाम...होगा for יִקָּרֵא). The other 5 strategies are
                included as guidance carried from the NT config, unconfirmed for OT.
  PARTICIPLE_BLOCK — जो/वाला substantive-participle split carried from NT config,
                unconfirmed against actual Hebrew articular participles.
  INFINITIVE_BLOCK — לְ + infinitive construct → के लिये PRIMARY (not secondary, unlike
                Greek "to") — confirmed twice (खेती करने के लिये, नाश करने के लिये).
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

- Conjunctive/perfective participle (verb stem + कर) — often renders Hebrew's waw-consecutive narrative chain or a circumstantial infinitive construct. Primary alone, no supplied conjunction needed.

- No indefinite article — bare noun is the default, matching Hebrew's own lack of one. Only when एक ("one") is explicitly supplied for emphasis/specificity is it secondary.

- Ergative ने — marks the subject of a transitive verb in the perfective aspect. NO Hebrew trigger at all (Hebrew has no ergativity) — purely a Hindi-grammar requirement — but still secondary to the subject noun/pronoun, never NEQ. Confirmed firing on every checked perfective-transitive subject (परमेश्वर ने सृष्टि की, आदम ने कहा, यहोवा ने कहा).

- को — dative (indirect object, case-implied from a Hebrew לְ-marked indirect object) is secondary to the noun. Differential object marking (DOM) on a definite/animate direct object has no Hebrew trigger at all (Hebrew marks direct objects with אֶת regardless of definiteness/animacy) but is still secondary, not NEQ, when it does occur. IMPORTANT: when the Hebrew verb is rendered as a Hindi light verb (see above), its direct object does NOT take DOM-को — it takes an objective genitive का/की on the light-verb noun instead (see GENITIVE POSTPOSITION below). Check whether a light-verb rendering is in play before expecting को.

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
DEFAULT → Branch B: no separate word at all — noun stands bare, article secondary to the noun's own record, no target word required. Confirmed as the overwhelming majority case (आकाश, पृथ्वी, स्त्री, वाटिका all bare, no exceptions in the sample checked).
MINORITY → Branch A: यह (proximal) or वह (distal) supplied, primary 1:1, noun in its own record — typically a second/later mention. Not yet isolated in the spot-check.

Check for an explicit Hebrew demonstrative pronoun (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) before assuming यह/वह is the article's own Branch A correspondent. OT Hebrew commonly follows an articular noun with a separate demonstrative-pronoun word to form "that/this X" (הָאִישׁ הַהוּא, lit. "the man, the that-one" = "that man") — a real, distinct token. When यह/वह corresponds to one of these, align it to THAT token, not the article (which stays Branch B).

### Branch A — article has a distinct Hindi correspondent
  הָאָרֶץ (repeated/anaphoric, no separate demonstrative token) → "वह पृथ्वी": source=[articlePart], target=["वह"] — primary 1:1; source=[אָרֶץ], target=["पृथ्वी"] — primary 1:1.
  הָאִישׁ הַהוּא (explicit demonstrative present) → "वह मनुष्य": source=[articlePart] — no target correspondent (Branch B, secondary to noun); source=[אִישׁ], target=["मनुष्य"] — primary 1:1; source=[הוּא], target=["वह"] — primary 1:1.

### Branch B — no distinct Hindi correspondent → secondary, no target word
  Articular noun, bare in Hindi: source=[articlePart, אָרֶץ], target=["पृथ्वी"] — primary: "पृथ्वी"; secondary.source: [articlePart].
  Construct-chain absolute noun with article: का/की/के construction already carries the relationship; article stays secondary with no separate word.

### Anarthrous noun
No Hebrew article token, and Hindi has no indefinite article — bare noun, no secondary needed unless एक is explicitly supplied.

## GENITIVE POSTPOSITION AND CONSTRUCT CHAINS
A Hebrew construct chain expresses genitive by word order and construct form — no preposition token. Hindi renders it with का/की/के, which inflects for the gender/number/case of the POSSESSED noun (the noun preceding it in Hindi word order), not the possessor — secondary to the possessed noun, since there is no separate Hebrew preposition token for it to be primary to.
  עֶבֶד יְהוָה "servant of the LORD" → "यहोवा के दास": source=[עֶבֶד], target=["दास"] — primary: "दास"; secondary: "के" (agrees with masculine दास); source=[יְהוָה], target=["यहोवा"] — primary 1:1.
  בִּן נוּן "son of Nun" → "नून का पुत्र": source=[בִּן], target=["पुत्र"] — primary: "पुत्र"; secondary: "का"; source=[נוּן], target=["नून"] — primary 1:1.
Construct chains of three or more links: align each link individually; each का/की/के secondary to the construct noun it follows.
Construct definiteness: the Hebrew article word-part on the genitive (absolute) noun stays secondary per ARTICLES Branch B — no extra word needed even when the article marks the whole chain as definite.

**Objective genitive with a light verb (direct objects, not construct chains):** when a Hebrew transitive verb is rendered as a Hindi light verb (noun + करना), its direct object (often אֶת-marked) takes का/की on the light-verb noun — the same postposition, but marking an objective-genitive relationship to the light-verb noun rather than a construct-chain possessor. Expect this INSTEAD OF DOM-को whenever a light-verb rendering is in play.
  אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ (objects of בָּרָא "created") → "आकाश और पृथ्वी की सृष्टि की": की marks both nouns as the objective genitive of सृष्टि ("creation," the light-verb noun); אֵת → NEQ source (not rendered by की at all).
  אֶת־הָאָדָם (object of בָּרָא) → "मनुष्य की रचना की".
  הָאָרֶץ (object of לְשַׁחֵת, a light-verb infinitive) → "पृथ्वी का नाश करने के लिये".

## INSEPARABLE PREPOSITIONS
Preposition word-part → Hindi preposition/postposition (में, को, से, के साथ, जैसा): primary 1:1. Merged article in the same token has no separate Hindi correspondent beyond the ordinary Branch B treatment.
  בַּשָּׁמַיִם "in the heavens" (single merged token) → "स्वर्ग में": source=[bashamayimId], target=["स्वर्ग", "में"] — primary: "स्वर्ग", "में".
מִן ("from") independent word → "से" primary 1:1; attached prefix מִ/מִּ follows the same rules as other inseparable prepositions.

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "और"/"परन्तु"/"तब"/"तो"/"इसलिये": primary 1:1. Asyndeton → NEQ source.
- כִּי — polyfunctional (causal, content-clause, conditional, temporal, emphatic, recitative); align to whichever Hindi word carries its force in context ("क्योंकि", "कि", "यदि", "जब"). Recitative כִּי with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — relative/subordinate marker; expected default जो. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — prefer the light-verb/vector-verb treatment (TOKEN ROLES) over idiom marking whenever the construction is a recognized light or vector verb rather than a genuinely non-compositional phrase. Function-word-only source records are never idioms.

## PASSIVE VOICE
Hebrew passive stems (Niphal, Pual, Hophal) map onto the same Hindi strategies used for Greek passives — identify which strategy is in play per verse rather than assuming.
1. True periphrastic passive (participle/light-verb-noun + जाना) — CONFIRMED default: מְחֹלָל (pierced) → "घायल किया गया"; מְדֻכָּא (crushed) → "कुचला गया". Participle/light-verb-noun primary; जाना secondary.
2. Stative-perfect (participle + copula, no जाना) — reserved for the recurring "it is written" (כָּתוּב) citation formula, by analogy with the NT config's γέγραπται → लिखा है; not yet confirmed for OT.
3. Adjectival/nominal resultative (adjective + होना/बनना) — CONFIRMED: נִרְפָּא (healed) → "चंगे हो जाएँ" (the identical mapping used for Greek ἰαθήσεται); הִוָּלֶד (was born) → "उत्पन्न हुआ". Adjective primary; होना/बनना secondary.
4. Dedicated intransitive/unaccusative verb (खोलना/खुलना-type pairs) — no voice marking at all.
5. Light-verb/noun+होना idiomatic construction — for passives of experience, relation, communication.
6. Bare resultative participle (+ हुआ/हुई/हुए, no finite copula) — attributive, not predicative.
7. Active-voice conversion — a full voice flip; check per verse rather than assuming.
8. Naming/equational conversion — CONFIRMED: יִקָּרֵא ("shall be called") → "नाम...होगा" (इसका नाम नारी होगा), verb dropped entirely.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Hebrew pronominal suffixes are separate word-part tokens (pos=suffix). Hindi possessive/object pronouns are ordinarily FREE-STANDING words (मेरा, तेरा, उसका, हमारा, तुम्हारा, उनका) — NOT fused clitics the way Indonesian's -ku/-mu/-nya are. Confirmed: Ps 23:1 רֹעִי "my shepherd" → "मेरा चरवाहा"; Gen 2:23 עֲצָמַי "my bones" → "मेरी हड्डियों" (agreement with possessed noun's gender, same pattern as GENITIVE POSTPOSITION).

- Possessive suffix on noun: suffix word-part → primary 1:1, Hindi possessive pronoun agreeing in gender/number with the possessed noun.
  דְּבָרוֹ "his word" → "उसका वचन": source=[davarPart], target=["वचन"] — primary 1:1; source=[sufPart], target=["उसका"] — primary 1:1.
  Suffix token absent (single token): the possessive pronoun is primary to the containing noun token.

- Reflexive अपना/अपने/अपनी when the possessor is coreferential with the clause's subject: substitute the reflexive for the ordinary third-person possessive that the suffix's own person/number would otherwise predict. Still primary 1:1 to the suffix word-part — the reflexive/non-reflexive choice is a Hindi lexical detail, not a change in which Hebrew token is the correspondent.
  בְּצַלְמוֹ "in his own image" (referent = subject of the clause's verb) → "अपने स्वरूप में", NOT "उसके स्वरूप में": source=[צֶלֶם], target=["स्वरूप"] — primary 1:1; source=[sufPart], target=["अपने"] — primary 1:1.

- Object suffix on verb: suffix → Hindi object pronoun (मुझे/तुझे/उसे/हमें/तुम्हें/उन्हें) or a DOM-को-marked noun phrase, primary 1:1.
  שְׁמָרֵנוּ "he kept us" → source=[shamarPart], target=["रखा"] — primary 1:1; source=[nuPart], target=["हमें"] — primary 1:1.

- Suffix on preposition: suffix → primary 1:1 to the Hindi pronoun object of the postposition.
  אֵלָיו "to him" → source=[elPart], target=["ओर"/"पास"] — primary; source=[sufPart], target=["उसकी"/"उसके"] — primary.\
"""

NEGATION_BLOCK = """\
## NEGATION

नहीं/न/मत split by discourse function, not mood — carries over from the NT config unchanged, confirmed for both indicative and modal contexts:

- नहीं — default, general-purpose negator. Confirmed: כִּי לֹא הִמְטִיר → "यहोवा...नहीं बरसाया" (indicative past).
- न — interchangeable literary variant of नहीं. Confirmed with future ("मुझे कुछ घटी न होगी" for לֹא אֶחְסָר) and imperative-flavored contexts ("न खाना" for לֹא תֹאכְלוּ). Also the dedicated correlative form for "neither...nor" lists.
- मत — ordinary colloquial prohibitive, paired with an imperative or -ना infinitive. Primary 1:1 to Hebrew's jussive/imperative negation (אַל). Caution: homographic with the unrelated noun मत ("opinion") — disambiguate by syntactic position.

Simple negation (לֹא) → नहीं/न.

Existential negation (אֵין/אַיִן) — NOT a single fixed idiom. Renders as a flexible नहीं/न + tense-agreeing था/हुआ construction, matching the surrounding narrative's tense, both words primary 1:N to אֵין (parallel to base OT document's general אֵין guidance, not Indonesian's fixed "tidak ada").
  וְאָדָם אַיִן לַעֲבֹד "there was no man to work" → "मनुष्य भी नहीं था": नहीं + था, both primary 1:N.
  אֵין לָהּ וָלָד "she had no child" → "उसके सन्तान न हुई": न + हुई, both primary 1:N; לָהּ → "उसके", primary to the suffix.

### Compound negation: לֹא...עוֹד ("no longer") is DISCONTINUOUS more often than not
Confirmed in 3 of 4 checked instances (फिर separated from न by intervening material) — parallels the NT config's οὐκέτι/μηκέτι finding and OT Indonesian's confirmed לֹא...עוֹד finding:
  וְלֹא־יָסְפָה שׁוּב אֵלָיו עוֹד → "वह उसके पास फिर कभी लौटकर न आई": फिर separated from न by कभी लौटकर.
  לֹא אֹסִף...עוֹד → "मैं फिर कभी भूमि को श्राप न दूँगा": फिर separated from न by भूमि को श्राप.
A contiguous exception is also attested (फिर कभी न मारूँगा, all clustered) — contiguity is a real minority option, not to be assumed absent. Both words are primary to their respective Hebrew tokens (לֹא → नहीं/न, עוֹד → फिर) regardless of adjacency.

### False-friend trap — जब तक...न ("until...not")
By analogy with the NT config's confirmed finding: Hindi's "जब तक X न हो" ("until X happens") carries a न with NO Hebrew source correspondent when the Hebrew עַד ("until") clause itself carries no negation — NEQ target, not aligned to any Hebrew particle. Not yet directly confirmed for an OT עַד construction.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival participle: aligns to Hindi adjective or participial modifier, primary.
- Substantive (nominal) participle: जो + finite verb/relative clause is the expected default when the Hebrew article word-part is present (הַשֹּׁמֵר "the one who keeps"), secondary to the participle. वाला (verb stem + वाला/वाली/वाले) is reserved for participles that compress into a stable, lexicalized agent-noun/role-label, not for generic vs. specific referents.
  הַשֹּׁמֵר → "जो रखवाली करता है": source=[articlePart] — secondary (Branch B, absorbed); source=[participleId], target=["जो", "रखवाली", "करता", "है"] — primary: "रखवाली", "करता"; secondary: "जो", "है".
- Verbal (predicative) participle — continuous/progressive: participle primary; Hindi progressive auxiliary (है/था/थी) secondary.
  יֹשֵׁב "was sitting" → "बैठा था": source=[participleId], target=["बैठा", "था"] — primary: "बैठा"; secondary: "था".
- Periphrastic (participle + explicit הָיָה): הָיָה aligns as a primary record to the Hindi auxiliary (था/थी/थे); participle aligns to the main verbal element, also primary — two separate primary records, since Hindi's own periphrastic default may independently supply its own copula alongside Hebrew's.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
When לְ is a separate word-part token, it aligns to a Hindi purpose marker as PRIMARY — unlike Greek, where "to" is secondary, Hebrew's לְ is an explicit lexical morpheme. के लिये is the confirmed default (not को, which the NT config found to be an IRVHin-leaning minority choice); the infinitive itself is also primary.
  לַעֲבֹד "to work" → "करने के लिये": source=[lePrepPart], target=["के", "लिये"] — primary; source=[infPart], target=["करने"] — primary.
  לְשַׁחֵת "to destroy" → "नाश करने के लिये": के लिये primary to לְ; करने primary to the infinitive (नाश की is a separate objective-genitive record — see GENITIVE POSTPOSITION AND CONSTRUCT CHAINS).

### Infinitive construct as verbal noun (בְּ + infinitive → "when/while/in ...-ing")
The infinitive aligns to the Hindi main verbal element; the preposition word-part aligns to the Hindi temporal/logical connector (जब, जैसे ही, में) as primary.

### Infinitive absolute (cognate emphasis)
Infinitive absolute + cognate finite verb (מוֹת תָּמוּת "you shall surely die") → Hindi emphasis adverb (अवश्य/निश्चय/ज़रूर), primary to the infinitive absolute; finite verb primary to the main Hindi verb — two separate primary records. If the translation absorbs the emphasis into a strong modal with no separate word, the infinitive absolute may be secondary to the finite verb, or NEQ if definitively untranslated.\
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
