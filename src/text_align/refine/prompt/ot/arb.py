"""Arabic (Van Dyck) target-language prompt config for OT (Hebrew) refine-alignment.

Distilled from `docs/alignment-principles-ot.arb.md`. Examples grounded in the Arabic
Van Dyck Bible (AVD) OT target TSV, cross-checked against a second Arabic OT translation
(ONAV) for the same verses, following the same methodology as `nt/arb.py`. Pass 1 was a
~15-verse spot-check across Genesis, Numbers, Deuteronomy, Joshua, Judges, Psalms; Pass 2
re-verified NEGATION (existential אֵין/אַיִן, the לֹא...עוֹד discontinuity) and CONSTRUCT
CHAINS (the occupational-participle exception) at full-corpus or full-corpus-derived-
sample scale, and ARTICLES with a precise full-corpus demonstrative-cooccurrence count.
PASSIVE VOICE (30-verse stratified sample across niphal/pual/hophal — new in Pass 2,
folded into BASE_BLOCK since the shared OT block set has no dedicated PASSIVE
conditional block), PARTICIPLE (25-verse sample plus a 96-instance exhaustive search
for the casuistic כָּל+participle construction, plus a 9-verse sample of verbal/
predicative participle use), INFINITIVE (14-verse sample of purposive/complement
לְ+infinitive, 20-verse sample of infinitive absolute), PRONOMINAL_SUFFIX (host-type
breakdown across ~47,000 corpus instances), and dual number (7-verse sample of 1,933
corpus instances) were all extended in Pass 2 — every item on the original Pass-1
open-questions list has now been addressed. See the principles doc's "Cross-translation
methodology note" and "Open questions" sections for what remains unconfirmed (mostly
finer-grained sub-questions the Pass-2 findings themselves raised).

**Draft status:** this config has not yet been reviewed by a native Arabic speaker or
Arabist. Do not use for production alignment runs until that review happens.

Key differences from OT English (eng.py), inherited from nt/arb.py's mechanics:
  BASE_BLOCK  — AVD's OT target TSV tokenizes on whitespace only; Arabic fuses
                conjunctions (wa-/fa-), prepositions (bi-/li-/ka-), the definite
                article (al-), and pronominal suffixes onto the adjacent word with
                no space, so N:1 records are the norm (same mechanism as NT
                Arabic, arguably more pervasive in OT narrative's dense
                waw-consecutive chains). Construct-state (idafa) genitive chains
                are a genuine typological match, not merely a parallel: Hebrew
                and Arabic both mark possession by bare noun-noun juxtaposition
                with the same head-first order, so no supplied "of"-equivalent
                is ever needed for a true construct chain — closer to
                Indonesian's OT finding than to NT Arabic's (which supplies
                idafa for a Greek case-marked genitive Arabic itself doesn't
                morphologically mark). Verified at scale (28-verse exhaustive
                sample of construct-participles after haya/way'hi): bare idafa
                is the actual majority even for occupational-title participles
                (armor-bearer, ark-bearers, archer all stayed bare) — the one
                confirmed exception is a lexicalized "avi" ("father of") +
                participle idiom, not a general occupational-participle rule;
                Genesis 4:2's shepherd/tiller pair remains an unexplained
                outlier. The article al-, though always fused, is treated as
                primary (not secondary) for the same reason NT Arabic gives —
                open question carried over unchanged. Dual number — verified
                at scale (7-verse sample of 1,933 corpus dual nouns): the
                dual-to-dual match is the majority pattern but not automatic;
                real lexeme-specific exceptions collapse to Arabic singular
                ("nostrils" -> "nose") or plural ("doors", "eyelids").
  PRONOMINAL_SUFFIX_BLOCK — verified across all host types (~47,000 corpus
                instances): the deciding factor is subject-vs-object/possessor
                ROLE, not host type, a distinction not present in any other OT
                config. Object/possessive suffixes fuse onto whatever Arabic
                word carries them (noun, verb, participle, or an infinitive's
                own object) and are always PRIMARY (matching NT Arabic and
                Indonesian's -ku/-mu/-nya); only a suffix marking the SUBJECT
                of an infinitive construct is SECONDARY when the infinitive is
                restructured as an Arabic finite clause, since Arabic's own verb
                agreement morphology already encodes that person/number
                information with no separate word needed.
  NEGATION_BLOCK — Hebrew's two negators (lo indicative, al jussive/prohibitive)
                both converge on Arabic la, mirroring NT Arabic's convergence
                for Greek's separate prohibition moods. Nominal/copular negation
                uses laysa (matches NT Arabic exactly). Existential ein/ayin —
                verified at scale (24-verse stratified sample of 659 corpus
                instances) — has THREE coexisting strategies, not a single
                fixed phrase like Indonesian's "tidak ada": la al-nafiya
                lil-jins (bare la + accusative predicate, no copula) is most
                common overall, especially in poetic/wisdom books; laysa
                (often + man, "there is no one who...") is a close second;
                "lam yakun" (negated "to be") is real but narrower, clustering
                in narrative prose with a definite concrete-noun subject. The
                lo...od ("no longer") discontinuity is confirmed at scale
                (20-verse stratified sample of 222 corpus instances) — matches
                NT Arabic's ouketi/meketi and Indonesian OT's own finding.
  PARTICIPLE_BLOCK — verified at scale (96-instance full-corpus search of the
                casuistic kol+article+participle construction, plus a 25-verse
                broader sample): three-way split matching NT Arabic's ism
                al-fa'il/alladhi/man structure. Genuine Arabic participle
                (ism al-fa'il) for attributive modification of a specific/
                already-identified referent or occupational title, matching
                NT Arabic. alladhi relative clause when the participle governs
                a direct object or names a specific historical group. "kullu
                man"/"kullu ma" is the dominant strategy specifically for
                Hebrew's casuistic/conditional legal formula kol ha+participle
                ("whoever/whatever does X, Y") — resolves the open question
                Indonesian OT flagged as unproductive via a similar search.
                The formulaic quotative le'mor ("saying") renders as
                "qa'ilan" — the identical fixed participle NT Arabic found for
                Greek "legon," a striking cross-testament confirmation.
                Verbal/predicative participle use (participle as main clause
                predicate) — REVISED after a 9-verse sample: finite-verb
                conversion is the MAJORITY strategy, reversing the original
                incidental single-instance assumption that a bare participle
                predicate was the default. Bare-participle predication is
                real but minority, clustering around postural/stative verbs
                (standing, sitting) rather than dynamic actions.
  INFINITIVE_BLOCK — temporal infinitive construct (be/ke + infinitive) renders
                as a finite clause with "hina"/"lamma" ("when"), never a
                nonfinite form — same mechanism as NT Arabic's ev to + infinitive
                and Indonesian OT's temporal-infinitive handling. Purposive/
                complement le+infinitive (verified against 4,573 corpus
                instances, the largest infinitive category) splits three ways:
                purposive li/likay+subjunctive (majority), an+subjunctive
                complement clause (matches NT Arabic's an strategy), and
                nominalization (masdar+preposition, real but less common).
                Infinitive absolute (cognate emphasis) — REVISED at scale
                (20-verse sample): cognate accusative (a genuinely closer
                Arabic structural parallel than any other supported language)
                and complete non-marking turned out roughly EQUALLY common,
                including within AVD itself — not a stable AVD-cognate-vs-
                ONAV-adverb split as the original single-instance finding
                suggested.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language
from .eng import BLOCK_ORDER, FORCED_INCLUSIONS


# ---------------------------------------------------------------------------
# Prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between the Arabic Van Dyck Bible (AVD) and its Hebrew source text (MACULA Hebrew / Westminster Leningrad Codex).

DRAFT CONFIG — not yet reviewed by a native Arabic speaker or Arabist.

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s) are behind this Arabic word.

## HEBREW WORD-PART TOKENS
MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own BCVWP ID:
- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

## AVD TOKENIZATION AND FUSION
AVD's target TSV tokenizes on whitespace only. Arabic orthography fuses conjunctions (وَ/فَ), prepositions (بِ/لِ/كَ), the definite article (ال), and pronominal suffixes onto the adjacent word with no space. One Arabic token routinely corresponds to 2-4 Hebrew word-part tokens. N:1 records (multiple Hebrew word-parts → one fused Arabic token) are the norm, not an occasional case. There is no way to mark part of a fused Arabic token secondary and leave the rest untouched — the record's granularity is still the whole token.
  וְהָאָרֶץ → وَٱلْأَرْضَ (waw + article + noun, one fused token): all three source parts primary to the one target token.

## TOKEN ROLES
primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Subject pronoun (pro-drop) — Arabic verbs mark subject person/number/gender through agreement morphology, so a dropped pronoun is fully recoverable from the verb form. No supplied Arabic pronoun expected when a waw-consecutive verb has no separate Hebrew pronoun token.
- No linking word for a true construct chain (see CONSTRUCT CHAINS) — Arabic's own idafa matches Hebrew's construct order exactly, no secondary needed.
- Merged article — treated as PRIMARY, not secondary (see ARTICLES); an open question, unlike every other supported OT language.
- Suffix marking the subject of an infinitive construct restructured as a finite clause — secondary to the finite verb, since Arabic verb agreement already carries that information (see PRONOMINAL SUFFIXES).

## NEQ (NON-EQUIVALENT)
NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.
Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (no Arabic equivalent particle).
Waw conjunction + Arabic asyndeton → waw word-part NEQ source (rare — Arabic almost always preserves the waw as fused وَ-).
Arabic conjunction with no Hebrew conjunction token → NEQ target.
Bare transliterated proper name with a Hebrew article token → NEQ source (Arabic never fuses al- onto a bare transliterated proper name, same rule as NT Arabic).

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.
Dual number: Biblical Hebrew has a living dual, and Arabic also has a fully productive dual — a genuine typological match (unlike NT Greek, whose dual is not living). Dual-to-dual is the majority pattern (knees, feet, "two years") but NOT automatic — real lexeme-specific exceptions collapse to Arabic singular (אַפָּיו "his nostrils" → أَنْفِهِ "his nose") or plural (דְּלָתַיִם "double doors" → مَصَارِيعُ; עַפְעַפַּי "my eyelids" → أَجْفَانِي) even within the same verse as a dual-matching pair. Check the specific target lexeme rather than assuming dual transfers automatically.

## PASSIVE VOICE
Hebrew niphal/pual/hophal derived stems mark passive/reflexive/reciprocal/middle voice. Four coexisting Arabic strategies (30-verse stratified sample, ~5,024 corpus instances):
- True morphological passive (Form I/II/IV, yufʿal(u)/fuʿila) — the DEFAULT expectation, ~77% of clean instances.
  יֻסַּךְ (hophal, "is poured") → يُسْكَبُ: primary 1:1. נִתְּנָה (niphal, "was given") → أُعْطِيَتِ: primary 1:1.
- Derived-stem active-form verb (Form V/VII/VIII: tafaʿʿala/infaʿala/iftaʿala) — narrow, clusters around reciprocal/collective/self-affecting actions where the subject's own action produces the result, not an external agent.
  יֵחָלֵק (niphal, "was divided") → ٱنْقَسَمَ (Form VII, "split itself"): primary 1:1. Same root/stem CAN take true passive instead when the reading is a genuine external-agent event rather than self-affecting — check sense, not just the lexeme (e.g. נִקְרָא "called" → دُعِيَ true-passive for "your name is invoked over this city" vs. → تَسَمَّى Form-V for "he took on their name/identity").
- Adjectival/stative (plain Arabic adjective or ordinary active participle) — for niphal forms marking an inherent STATE, not a passive EVENT.
  נִרְחָב (niphal, "wide," describing pastureland) → وَاسِعٍ (plain adjective, no verbal marking): primary 1:1. נִרְדָּם ("sound asleep") → نَائِمًا (plain active participle): primary 1:1.
- Active-voice conversion (agent promoted to subject) — rare, more common in ONAV's dynamic register than AVD's literal one.

## GRANULARITY
Prefer one record per source token — split rather than group. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
TREATED AS PRIMARY, not secondary — an open question carried over from NT Arabic (every other OT config treats the article as secondary). Arabic's al- is a real, productive definite-article morpheme, not a merely grammatically-supplied filler. Because al- is always fused, there is no Branch A/Branch B split the way other OT languages have — the article's primary link to the noun's record is automatic whenever the Hebrew article word-part is present.
  הָאָרֶץ → ٱلْأَرْضُ "the earth": source=[articlePart, אָרֶץ], target=["ٱلْأَرْضُ"] — both primary
Do not confuse the fused article with an explicit Hebrew demonstrative pronoun (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה) following an articular noun ("the man, the that-one" = "that man"). Arabic's demonstrative pronouns (هَذَا/هَذِهِ/ذَلِكَ/تِلْكَ) are separate, non-fused words and align primary 1:1 to that demonstrative token specifically, never to the article.

### Anarthrous noun
No Hebrew article token, and Arabic has no indefinite article — bare noun, no secondary needed.
  אִישׁ → إِنْسَانًا "a man": primary alone

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token. Arabic's own idafa construction works identically: bare noun-noun juxtaposition, head noun first — the exact same order Hebrew already uses. No linking word needed — a genuine structural match, not merely a parallel.
  רוּחַ אֱלֹהִים → رُوحُ ٱللهِ "Spirit of God": source=[רוּחַ], target=["رُوحُ"] — primary 1:1 (no secondary needed); source=[אֱלֹהִים], target=["ٱللهِ"] — primary 1:1
  מֹשֶׁה עֶבֶד יְהוָה → مُوسَى عَبْدِ ٱلرَّبِّ: source=[עֶבֶד], target=["عَبْدِ"] — primary 1:1 (no secondary needed)

Distinguish a true construct chain from Hebrew's לְ-possession construction (common in psalm superscriptions): a bound/construct-state noun with no preposition token is a true construct chain (above). An absolute noun + separate לְ token expressing possession is NOT a construct chain — לְ is a real Hebrew token, gets its own primary record, fused onto the Arabic noun as لِ-.
  מִזְמוֹר לְדָוִד → مَزْمُورٌ لِدَاوُدَ: source=[מִזְמוֹר], target=["مَزْمُورٌ"] — primary 1:1; source=[לְPrepPart], target=["لِدَاوُدَ"] — primary; source=[דָוִד], target=["لِدَاوُدَ"] — primary (shares token)

Occupational participles after הָיָה/וַיְהִי (e.g. "was a shepherd/archer/armor-bearer"): bare construct is the actual MAJORITY even here (confirmed against all 28 corpus instances) — do not expect a supplied preposition by default. The one confirmed exception is a lexicalized idiom: אֲבִי + participle-phrase ("father of X-ers") consistently supplies لِ, secondary to the participle's record, while any inner construct chain inside the same phrase stays bare.
  וַיְהִי לוֹ נֹשֵׂא כֵלִים → وَكَانَ لَهُ حَامِلَ سِلَاحٍ "and he had an armor-bearer" (bare, the norm): source=[נֹשֵׂא-construct], target=["حَامِلَ"] — primary 1:1 (no secondary needed); source=[כֵלִים], target=["سِلَاحٍ"] — primary 1:1
  אֲבִי יֹשֵׁב אֹהֶל → أَبًا لِسَاكِنِي ٱلْخِيَامِ "father of tent-dwellers" (لِ-idiom exception): source=[אֲבִי-construct], target=["أَبًا"] — primary 1:1; source=[יֹשֵׁב-construct], target=["لِسَاكِنِي"] — primary; the fused لِ- has no separate Hebrew correspondent (supplied, secondary); source=[אֹהֶל], target=["ٱلْخِيَامِ"] — primary 1:1 (inner chain, still bare)

## INSEPARABLE PREPOSITIONS
Preposition word-part → Arabic preposition, fused as a proclitic (بِ-/لِ-/كَ-) or a separate word (مِنْ/عَلَى/تَحْتَ never fuse): primary 1:1. Merged article in the same fused token keeps its own primary link per ARTICLES.
  בְּיִשְׂרָאֵל → فِي إِسْرَائِيلَ (فِي never fuses): source=[בְPrepPart], target=["فِي"] — primary 1:1
  לְדָוִד → لِدَاوُدَ (bound proclitic): source=[לְPrepPart], target=["لِدَاوُدَ"] — primary

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part → fused وَ-/فَ-: primary. Confirmed dominant across nearly every verse sampled — OT Arabic fuses the waw more consistently than Indonesian drops it. Asyndeton (rare) → NEQ source.
- כִּי — polyfunctional; align to whichever Arabic word/particle carries its force (لِأَنَّ/إِنَّ/أَنَّ/etc.). Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר — Arabic's relative pronoun family (ٱلَّذِي/ٱلَّتِي/ٱلَّذِينَ, agreeing in gender/number, unlike Indonesian's invariant "yang"): primary, when functioning as a true relative. When אֲשֶׁר functions as a complementizer introducing an oath/command complement clause instead, it aligns to Arabic's complementizer أَنْ.
  אֲשֶׁר לֹא תִקַּח (oath complementizer) → أَنْ لَا تَأْخُذَ: source=[אֲשֶׁר], target=["أَنْ"] — primary 1:1

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Function-word-only source units are never idioms.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Pronominal suffixes are separate word-part tokens (pos=suffix). The deciding factor for primary-vs-secondary is the suffix's grammatical ROLE (subject vs. object/possessor), NOT which kind of word it attaches to — not present in any other supported OT config, since Arabic has genuine person/number verb agreement that can independently carry subject information.

- Object suffix or possessive suffix — PRIMARY, fused, regardless of host type (noun, preposition, finite verb, participle used nominally or verbally, or an infinitive construct's OBJECT). The suffix attaches directly onto whatever Arabic word ends up carrying it as ONE fused token — BOTH the head token and the suffix word-part are primary.
  עֲצָמַי → عِظَامِي "my bones" (noun): source=[עֶצֶם-noun, sufPart], target=["عِظَامِي"] — both primary
  שֹׁפְטָיו → قُضَاتَهُمْ "his judges" (participle used nominally, possessive): both primary
  כָּל מֹצְאִי → كُلُّ مَنْ وَجَدَنِي "whoever finds me" (participle used verbally as object, restructured as finite verb — suffix still fuses onto the finite verb): both primary
  לְהַכְעִיסוֹ → لِإِغَاظَتِهِ "to provoke him" (infinitive construct's OBJECT suffix, fused onto the resulting masdar/verbal noun — NOT the subject-marking case below): both primary
  אֵלָיו → إِلَيْهِ "to him" (preposition): both primary

- Suffix marking the SUBJECT of an infinitive construct — SECONDARY, absorbed. The one genuine exception, and only for SUBJECT-marking (not object-marking — contrast above). When the infinitive construct is restructured as an Arabic finite clause (the default for temporal/purpose uses — see INFINITIVAL CONSTRUCTIONS), Arabic's own verb agreement morphology already encodes the subject's person/number/gender, so the suffix has no separate Arabic word to attach to.
  בְּשִׁבְתְּךָ → حِينَ تَجْلِسُ "when you sit": source=[שֶׁבֶת-infC, sufPart], target=["تَجْلِسُ"] — primary: שֶׁבֶת; secondary: sufPart (2ms agreement already in تَجْلِسُ)
  בְּמָלְכוֹ → حِينَ مَلَكَ "when he became king": source=[מָלַךְ-infC, sufPart], target=["مَلَكَ"] — primary: מָלַךְ; secondary: sufPart

Practical check for an infinitive-construct suffix: is it the logical SUBJECT of the infinitive's action (intransitive/unaccusative sense, e.g. "his becoming king") or its OBJECT/possessor (e.g. "his provoking [someone]")? If Arabic restructures into a full finite clause, the suffix is almost always absorbed (secondary); if Arabic keeps a masdar/verbal-noun rendering, the suffix fuses onto that noun as primary like any other noun+suffix.\
"""

NEGATION_BLOCK = """\
## NEGATION

Hebrew's two morphologically distinct negators (לֹא indicative, אַל jussive/prohibitive) both converge on Arabic لَا — a mood distinction Hebrew grammaticalizes but Arabic doesn't for ordinary negation, mirroring NT Arabic's convergence for Greek's separate imperative/subjunctive prohibition moods.

- לֹא (indicative, any tense/aspect) → لَا + verb: primary 1:1. Verb gets its own record.
  וְלֹא יַעֲשֶׂה → وَلَا يَفْعَلُ "and does not do": source=[loId], target=["لَا"] — primary 1:1; source=[verbId], target=["يَفْعَلُ"] — primary 1:1
- אַל (jussive/prohibitive) → لَا + jussive/imperative verb: primary 1:1. Same particle as indicative לֹא; only the Arabic verb's own mood morphology distinguishes the prohibition.
  אַל תַּבִּיט → لَا تَنْظُرْ "do not look": source=[alId], target=["لَا"] — primary 1:1
- Nominal/copular negation → لَيْسَ (conjugated negator-verb, agreeing with its subject): matches NT Arabic's laysa-for-copular-negation finding exactly.
  לֹא אִישׁ אֵל → لَيْسَ ٱللهُ إِنْسَانًا "God is not a man": source=[loId], target=["لَيْسَ"] — primary 1:1
- אֵין/אַיִן (existential) — THREE coexisting strategies (confirmed against a 24-verse stratified sample of all 659 corpus instances), none a single fixed phrase like Indonesian's "tidak ada":
  (a) لا النافية للجنس (bare لَا + accusative predicate noun, no copula) — most common overall, especially in poetic/wisdom books (Psalms/Proverbs/Ecclesiastes).
    וְאֵין קֵץ → لَا نِهَايَةَ لَهَا "there is no end": source=[einId], target=["لَا"] — primary 1:1 (categorical, no copula); source=[qetsId], target=["نِهَايَةَ"] — primary 1:1
  (b) لَيْسَ (conjugated existential negator), often + مَنْ for "there is no one who...": nearly as common as (a).
    וְאֵין מוֹשִׁיעֵךְ → وَلَيْسَ مَنْ يُخَلِّصُكِ "and there is no one to save you": source=[einId], target=["وَلَيْسَ", "مَنْ"] — both primary
  (c) لَمْ يَكُنْ (negated finite "to be") — real but narrower than (a)/(b); clusters in narrative prose with a definite concrete-noun subject ("there was no king/sword").
    אֵין מֶלֶךְ בְּיִשְׂרָאֵל → لَمْ يَكُنْ مَلِكٌ فِي إِسْرَائِيلَ "there was no king in Israel": source=[einId], target=["لَمْ", "يَكُنْ"] — both primary
  Caution: אַיִן is also the interrogative "where?" (מֵאַיִן "from where") — check the gloss, not just the surface form, before classifying as existential negation.

לֹא...עוֹד ("no longer") is DISCONTINUOUS — confirmed against a 20-verse stratified sample of all 222 corpus instances (matches NT Arabic's οὐκέτι/μηκέτι and Indonesian OT's own finding). The negator fuses onto the verb; the "again"-adverb (بَعْدُ/أَيْضًا) trails at the very end of the clause, usually separated by the verb's object or other material — do not expect them adjacent.
  וְלֹא יָסְפָה שׁוּב אֵלָיו עוֹד → فَلَمْ تَعُدْ تَرْجِعُ إِلَيْهِ أَيْضًا "she did not return to him again": source=[loId], target=["فَلَمْ", "تَعُدْ"] — primary 1:1 (fused negation+verb); source=[odId], target=["أَيْضًا"] — primary 1:1, non-adjacent\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

Substantive/attributive articular participles split three ways by referent type (verified against a 96-instance full-corpus search of כָּל+article+participle, plus a 25-verse broader sample):

- Genuine Arabic participle (ism al-fāʿil, often lexicalized as an agent-noun) — majority strategy, for attributive modification of an already-identified/specific referent, occupational titles, epithets.
  הַ+מֹּשֵׁל → ٱلْمُسْتَوْلِي "the one in charge": source=[articlePart, participleId], target=["ٱلْمُسْتَوْلِي"] — both primary
  Occupational titles: הָרֹאֶה "the seer" → ٱلرَّائِي; הַצֹּפֶה "the watchman" → ٱلرَّقِيبُ (lexicalized agent-nouns, not relative clauses)
- ٱلَّذِي/ٱلَّتِي/ٱلَّذِينَ (relative clause + finite verb) — when the participle governs a direct object, or for a specific historical group.
  הַנֹּגֵעַ בָּעֶצֶם "the one who touches the bone" → ٱلَّذِي مَسَّ ٱلْعَظْمَ: primary: مَسَّ; secondary: ٱلَّذِي
- كُلُّ مَنْ / كُلُّ مَا + finite verb — the DOMINANT strategy specifically for the casuistic/conditional legal formula כָּל הַ+participle ("whoever/whatever does X, Y"), NOT bare-article-participle generally. مَنْ for personal referents (majority — ritual-purity law, wisdom generalizations); مَا for impersonal. Distinguish from a genuine participle/relative clause, which is used when the SAME כָּל הַ+participle syntax describes an already-identified specific group rather than a hypothetical legal class.
  כָּל הַנֹּגֵעַ בְּנִבְלָתָם יִטְמָא "whoever touches their carcass shall be unclean" → كُلُّ مَنْ مَسَّ جُثَثَهَا يَكُونُ نَجِسًا: source=[כָּל, articlePart, participleId], target=["كُلُّ", "مَنْ"] — both primary
  כָּל הַנֹּגֵעַ בַּמִּזְבֵּחַ יִקְדָּשׁ "whatever touches the altar shall be holy" (impersonal referent) → كُلُّ مَا مَسَّ ٱلْمَذْبَحَ: target=["كُلُّ", "مَا"] — both primary
  Contrast (specific historical group, NOT casuistic law, stays participle/relative): כָּל הַנֹּפְלִים "all who fell" (a particular battle's casualties) → جَمِيعُ ٱلسَّاقِطِينَ (genuine participle, not مَنْ)
- Occupational/predicative, in a construct chain after הָיָה/וַיְהִי: see CONSTRUCT CHAINS — bare idafa is the majority even here; only the lexicalized אֲבִי + participle idiom reliably supplies a preposition.
- Predicative (participle as main clause predicate) — REVISED after a 9-verse sample: finite-verb conversion is the MAJORITY strategy, not a bare participle predicate as originally assumed. Bare-participle predication is real but minority, clustering around postural/stative verbs (standing, sitting) — Arabic's active participle naturally expresses a resultant state, favoring a finite verb for dynamic actions instead.
  Finite-verb conversion (majority): וְרוּחַ אֱלֹהִים מְרַחֶפֶת "and the Spirit of God was hovering" → وَرُوحُ ٱللهِ يَرِفُّ: source=[participleId], target=["يَرِفُّ"] — primary (finite imperfect verb, not a participle)
  Bare participle predicate (minority, postural/stative): וְהַכֹּהֵן נִצָּב "and the priest was standing" → وَٱلْكَاهِنُ وَاقِفٌ: source=[participleId], target=["وَاقِفٌ"] — primary (bare participle, nominal-clause predicate)
  Lexicalized noun/title predicate (rare): אֱלֹהִים שֹׁפֵט הוּא "God, he is judge" → ٱللهَ هُوَ ٱلدَّيَّانُ "God, He is THE JUDGE": source=[participleId], target=["ٱلدَّيَّانُ"] — primary (lexicalized agent-noun/title, not a participle or finite verb)
- Formulaic quotative לֵאמֹר ("saying," introducing direct speech): a fixed, extremely stable rendering قَائِلًا — identical to NT Arabic's finding for Greek λέγων, a striking cross-testament confirmation.
  ... לֵאמֹר → ... قَائِلًا: source=[leEmorId], target=["قَائِلًا"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Purpose/temporal constructions (בְּ/כְ + infinitive construct) → finite clause
Classical Arabic has no true infinitive usable this way (same structural gap NT Arabic documents with five strategies by syntactic function). For the temporal/purpose use, Hebrew's בְּ/כְ + infinitive construct ("when/as X happened") renders as an ordinary finite clause introduced by حِينَ/لَمَّا ("when"), never a nonfinite form — the same mechanism NT Arabic uses for ἐν τῷ + infinitive, and Indonesian OT uses for the same Hebrew construction. Confirmed 5x across two samples. The infinitive's own subject suffix, if present, is absorbed into the finite verb's agreement morphology (see PRONOMINAL SUFFIXES) rather than surfacing as a separate word.
  בְּשִׁבְתְּךָ בְּבֵיתֶךָ → حِينَ تَجْلِسُ فِي بَيْتِكَ "when you sit in your house": source=[בְPrepPart], target=["حِينَ"] — primary; source=[שֶׁבֶת-infC, sufPart], target=["تَجْلِسُ"] — primary: שֶׁבֶת; secondary: sufPart

### Purposive/complement לְ + infinitive construct
Three coexisting strategies, verified against the largest infinitive category (4,573 corpus instances) — none a single default:
- Purposive لِ/لِكَيْ + subjunctive verb — majority, for genuine purpose clauses.
  לְהַבְדִּיל → لِتَفْصِلَ "to separate": primary
- أَنْ + subjunctive complement clause — for infinitive complements of volition/refusal/permission verbs (matches NT Arabic's أَنْ strategy).
  לֹא אָבָה לִשְׁתּוֹתָם → لَمْ يَشَأْ أَنْ يَشْرَبَهُ "was not willing to drink it": primary
- Nominalization (masdar + preposition) — real but less common, mostly fixed idioms.
  לָצֵאת וְלָבוֹא → لِلْخُرُوجِ وَلِلدُّخُولِ "for going out and coming in": primary
The same בִּלְתִּי+infinitive ("so as not to X") construction was found rendered three different ways (أَنْ لَا+subjunctive; a bare relative clause ٱلَّذِي لَا يَنْفَعُ) — treat as genuinely translator-variable.

### Infinitive absolute (cognate emphasis) — REVISED after a 20-verse sample; original single-verse claim does not hold
Cognate accusative and complete non-marking are roughly EQUALLY common (~half each), including within AVD itself — NOT a stable AVD-cognate-accusative-vs-ONAV-adverb split as the original single-instance finding suggested.
- Cognate accusative (masdar as accusative object of the matching finite verb) — real, structurally unique to this Semitic pair among supported languages.
  אָכֹל תֹּאכֵל → تَأْكُلُ أَكْلًا "you shall surely eat": source=[infAbsId], target=["أَكْلًا"] — primary 1:1 (structural cognate accusative); source=[verbId], target=["تَأْكُلُ"] — primary 1:1
- Completely unmarked (plain finite verb, no cognate accusative, no adverb) — equally common; do not force a secondary link when nothing bears the emphatic force.
  עָלֹה נַעֲלֶה → نَصْعَدُ "we will surely go up" (no emphasis marker at all): primary 1:1 alone
A separate usage — a string of bare infinitive absolutes as imperatival commands with no matching finite verb (e.g. Isaiah 21:5's "prepare... spread... eat... drink") — always renders as ordinary finite imperative/imperfect verbs; no cognate accusative is possible without a same-root finite verb to attach one to.\
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

ARB_OT_CONFIG = LanguagePromptConfig(
    language_code="arb",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(ARB_OT_CONFIG)
