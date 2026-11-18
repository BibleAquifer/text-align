"""Swahili target-language prompt config for OT (Hebrew/Aramaic) refine-alignment.

Primary edition: ONEN (Biblica Open Kiswahili Contemporary Version, Neno). Built from
raw text + reasoning (no alignment data), then counted at corpus scale at verse level
(WLCM joined to ONEN/ONMM/SRUV06). ONMM is a dialect revision of ONEN, not an
independent check; SRUV06 is consult-only. Full evidence trail, counts and open
questions: docs/alignment-principles-ot.swh.md. NT counterpart: nt/swh.py.

Key differences from OT English (eng.py):
  BASE_BLOCK            — one fused Swahili word = ONE record (several Hebrew tokens,
                          all primary); no articles (secondary to the noun); associative
                          "-a" for construct chains; waw-consecutive as fused "-ka-";
                          existentials; verb-stem extensions; divine names/titles.
  PRONOMINAL_SUFFIX     — suffix on a verb = fused object marker; suffix on a
                          preposition (free, absorbed into the verb, or dropped).
  NEGATION              — fused ha-/si- (NT precedent), free wala/bila/hakuna.
  PARTICIPLE            — relatives: infixed-first (not amba-), -enye, gnomic hu-.
  INFINITIVE            — ku- (secondary), subjunctive/-po-/-ki- renderings, lemor.

Draft — not yet reviewed by a native Swahili speaker.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language
from .eng import BLOCK_ORDER, FORCED_INCLUSIONS


# ---------------------------------------------------------------------------
# Prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation (Kiswahili, ONEN) and its Hebrew/Aramaic source
text (MACULA Hebrew / Westminster Leningrad Codex).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s) are behind this translation word.

## HEBREW WORD-PART TOKENS
MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own ID:
- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ; Aramaic emphatic-state ָא) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (article, construct relation)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

### One fused Swahili word = ONE record
The Swahili finite verb is a single unspaced word fusing subject marker + tense + object marker + root + extensions (and sometimes the Hebrew waw, preposition, negator). A target token may sit in only ONE record. So when several Hebrew tokens are rendered by one Swahili word, put ALL of them in ONE record (source = every Hebrew token it renders, target = that word) and mark each Hebrew token that has its own morpheme or lexical content primary. A Hebrew token that only supplies grammar (the article, an infinitive-subject suffix) is secondary. A separate record is only for a Swahili word that is a free token of its own (`wala`, `Je`, `Kisha`, `mimi`).
  וַיֹּאמֶר יְהוָה אֵלַי → "Bwana akaniambia":
    source=[יְהוָה], target=["Bwana"] — primary
    source=[וַ, יֹּאמֶר, אֵלַ, י], target=["akaniambia"] — all primary (-ka- = waw; root = verb; -ni- = suffix; -ia = the preposition); the subject marker "a-" has no Hebrew token

## SUBJECT MARKER AND EXPLICIT PRONOUNS
No Hebrew pronoun token: the subject marker is just part of the verb word — nothing extra to align.
Explicit Hebrew pronoun (אֲנִי/אַתָּה/הוּא/אֲנַחְנוּ…): a free Swahili pronoun (mimi, wewe, yeye, sisi, ninyi, wao) is its own primary record; if only the fused subject marker renders it, add the pronoun token to the verb's single record as primary (never NEQ).

## ARTICLES
Swahili has no article. The Hebrew article (and Aramaic emphatic-state ָא) is SECONDARY to its noun in the noun's record — never NEQ.
  הָאָרֶץ → "dunia": source=[הָ, אָרֶץ], target=["dunia"] — primary: אָרֶץ; secondary: הָ
- An explicit Hebrew demonstrative (הוּא/הִיא/זֶה/זֹאת/אֵלֶּה, often after the article) → Swahili demonstrative (huyo, yule, huu, hii, hao, hizo, ule…) PRIMARY to THAT token; the article stays secondary.
  הַלַּיְלָה הַהוּא → "Usiku ule": source=[הַ, לַּיְלָה], target=["Usiku"] — primary: לַּיְלָה; secondary: הַ; source=[הוּא], target=["ule"] — primary
- No Hebrew demonstrative, but ONEN has an anaphoric demonstrative on a noun already mentioned (hizo nguzo, huo mwezi): primary to the article — a small minority (~7 per 100 verses per article). Do not credit supplied "Kwa hiyo"/hawa/huu/huko to the article: those are NEQ.

## CONSTRUCT CHAINS AND THE ASSOCIATIVE "-a"
A construct-state head noun + its absolute noun renders with the associative "-a" (wa/la/ya/za/cha/vya/pa/mwa, agreeing in class with the HEAD): present in ~96% of short verses. The "-a" word is SECONDARY, folded into the HEAD noun's record; the possessor noun gets its own primary record.
  מֶחְקְרֵי אָרֶץ → "vilindi vya dunia":
    source=[מֶחְקְרֵי], target=["vilindi", "vya"] — primary: "vilindi"; secondary.target: ["vya"]
    source=[אָרֶץ], target=["dunia"] — primary
  Nested chains: each link takes its own "-a" (Lango la Juu la Hekalu la Bwana).
- A possessor pronominal suffix fuses into the possessive word (langu, yake, wao) — see PRONOMINAL SUFFIXES.
- A chain rendered as mwenye/wenye + noun, a compound, or one lexicalized word is an ordinary content correspondence (all words primary), not a linker case.
- Aramaic דִּי is a REAL word (relative or genitive): the associative/relative concord rendering it is PRIMARY to דִּי, not secondary.

## CONJUNCTIONS AND PARTICLES

### Waw
- Waw-consecutive (וַיִּ…/וַיְ…) renders mostly as the fused narrative tense -ka- (~75%; law/prophets higher, poetry only ~29%): waw and verb in ONE record, both primary. Temporal "when" -po- (alipoona) or -ki-: same, waw primary in the verb's record.
  A plain past -li-/-me- with no connective has no morpheme for the waw → waw NEQ (certain). וַיְהִי ("and it came to pass") dropped or reduced to "Ikawa" → NEQ if absent.
- A free Kisha/Basi/Ndipo/na → primary to the waw in its own record.
- וְלֹא → "wala": ONE record, source=[וְ, לֹא], target=["wala"] — both primary.
- "na" has four functions — disambiguate by context, never default to "and": (1) coordinating "and"; (2) comitative "with" (pamoja na); (3) passive agent "by" (after a passive verb + a personal agent); (4) "have" (-na, kuwa na).

### כִּי and אִם (MACULA's gloss predicts the rendering)
כִּי "for"/"because" → kwa kuwa/kwa maana/kwa sababu (57–75%); "that" → kwamba (41%); "but" → bali/lakini (77%); "if" → kama/ikiwa/-ki- (65%); "when" → wakati/-po-. אִם "if" → kama/ikiwa (88%); "or" → usually no word (Je … au); "though" → ingawa/ijapokuwa. The free connective is primary; fused (-po-/-ki-) → primary in the verb's record; truly absent (~30% for "for"/"that"/"when") → NEQ if certain, else unrecorded.

### הִנֵּה — Tazama/Sasa primary; ONEN often drops it → NEQ.
### Interrogative הֲ/הַ — "Je" primary 1:1 (85%); an alternative question's second clause → "au" primary; הֲלֹא → "si" primary to BOTH הֲ and לֹא in one record; carried only by word order/modal → הֲ NEQ.
### Interjections — הוֹי/אוֹי "woe" → "Ole" primary. סֶלָה (Selah) is never rendered → NEQ. נָא "now!" not rendered → NEQ.
### Vocative — Hebrew marks it with no particle; ONEN supplies "Ee". Put "Ee" in the vocative noun's record (target=["Ee", "Bwana"]), noun primary; NEQ only if no Hebrew vocative noun exists.
  יְהוָה (vocative) → "Ee Bwana": source=[יְהוָה], target=["Ee", "Bwana"] — primary

## RELATIVE אֲשֶׁר/שֶׁ
The Swahili relative is mostly an INFIXED concord inside the verb (-ye-/-o-/-lo-: aliyetukumbuka; ~56%), less often amba- + concord (ambaye, ambao; ~20%), or -enye "having" (~10%). The relative word or concord is PRIMARY to אֲשֶׁר; if it is fused into the verb word, אֲשֶׁר joins that verb's single record. A relative with no Hebrew אֲשֶׁר behind it → NEQ.

## EXISTENTIALS AND "HAVE"
- יֵשׁ "there is": kuna/pana/mna, locative -po/-ko/-mo (lipo, iko), or -na "have" (ana, wana). Primary to יֵשׁ; the fused locative/-na form is one word, one record. NB: יֵשׁ is also a NOUN "wealth/substance" (Prov 8:21 → utajiri) — not an existential.
- אֵין/אַיִן "there is no": hakuna/hamna/hapana (~34%); hana/hawana "has no"; bila/pasipo/wala; also frequently a verb of disappearance or a fused negative verb (אֵינָם "they are no more" → hutoweka, hawapo, hawatakuwepo tena). Primary to אֵין in all of these.
  אֵין מִשְׁפָּט → "hakuna haki": source=[אֵין], target=["hakuna"] — primary; source=[מִשְׁפָּט], target=["haki"] — primary
- לְ+suffix possessor ("X has Y", verbless): either -na "have" (zina masikio: source=[לָ, הֶם] primary to "zina") or "ni" + possessive pronoun (ni wangu, vyake): לְ+suffix primary to the possessive pronoun; the copula "ni" is NEQ (supplied).

## VERB STEMS (the extension folds into the host verb's single record; never a separate record)
Niphal → -wa passive (~40%) / -ika stative / -ana; Pual → -wa (~50%); Piel → often causative -isha/-esha (~19%); Hiphil → -isha/-esha (~17%) or periphrastic -fanya; Hitpael → reflexive ji- (~41%) or -ana. The Hebrew verb is primary; the extension is bound inside the word. Aramaic Peil/Ethpeel → -wa; Haphel → -wa or ordinary verb.

## DIVINE NAME AND TITLES (counted on every verse)
יְהוָה alone → "Bwana": primary 1:1.
אֲדֹנָי יְהוִה → "Bwana Mwenyezi" (95%): "Bwana" ← אֲדֹנָי, "Mwenyezi" ← יְהוִה — NOT the bare-name order.
יְהוָה צְבָאוֹת → "Bwana Mwenye Nguvu Zote" (98%): "Bwana" ← יְהוָה; "Mwenye Nguvu Zote" (3 words, all primary) ← צְבָאוֹת.
יְהוָה אֱלֹהֵי … → "Bwana, Mungu wa …"/"Bwana Mungu wenu": "Mungu" ← אֱלֹהֵי; its "wa" secondary (construct). שַׁדַּי → "Mwenyezi" or "Mungu". Bare אֲדֹנָי → "Bwana" (63%).

## ARAMAIC (Daniel 2:4b–7:28; Ezra 4:8–6:18, 7:12–26; Jeremiah 10:11)
Same principles. The emphatic-state ָא is a separate article word-part (secondary to its noun); דִּי as relative takes the relative concord (primary).

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty, and never just because a grammaticalized target feature is marked another way too.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded
Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases.
Hebrew article → SECONDARY to its noun, not NEQ (see ARTICLES). Hebrew waw with no connective morpheme (plain -li-/-me-, asyndeton) → NEQ source.
SUPPLIED COPULA — one rule, no exception for predicate adjectives. In a verbless Hebrew clause (no verb, no participle, no הָיָה) every copula ONEN supplies is NEQ target: "ni", the emphatic "ndiye"/"ndio", the locative "upo"/"yuko"/"iko", and the past "ilikuwa"/"lilikuwa"/"alikuwa". Never mark it secondary to the predicate.
  כִּי טוֹב → "ya kuwa nuru ni njema": source=[טוֹב], target=["njema"] — primary; "ni" → NEQ target (not secondary to טוֹב)
  חֹשֶׁךְ עַל פְּנֵי תְהוֹם → "Giza lilikuwa juu ya uso wa vilindi": "lilikuwa" → NEQ target
  אַתָּה עִמָּדִי → "wewe upo pamoja nami": "upo" → NEQ target
When a Hebrew verb token IS present (הָיָה/הָיְתָה/יְהִי, or a participle), the Swahili word rendering it belongs in THAT token's record and is not NEQ. A repeated copy of the same auxiliary for a second predicate of one Hebrew verb (הָיְתָה תֹהוּ וָבֹהוּ → "ilikuwa haina umbo, ilikuwa tupu") → secondary to the second predicate's record.
Swahili words ONEN supplied with no Hebrew anchor (Kwa hiyo, hivyo, a connective with no waw behind it) → NEQ target.
ONEN is a dynamic translation: a Hebrew content word it does not render is a real NEQ, but only when certain.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group — EXCEPT where one Swahili word renders several Hebrew tokens (then one N:1 record, see above). Grammar-required Swahili words (associative "-a", class concord, modal helpers) are secondary to the source token whose grammar requires them, not NEQ. Leaving tokens unrecorded when no genuine correspondence exists is deliberate.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Function-word-only source units are never idioms.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES
Suffixes are separate word-part tokens (pos=suffix); Swahili fuses them.

- On a VERB (object): the suffix IS the object marker inside the fused verb word. ONE record: source=[verb, suffix], target=[the verb word], both primary.
  תַּהַרְגֵם → "utawaua": source=[תַּהַרְגֵ, ם], target=["utawaua"] — both primary
- On a NOUN (possessive): the suffix → possessive form (langu, wako, wake/yake, chetu, wenu, wao), primary. If the noun and possessive are separate words, separate records; if one fused word, one record.
  שִׁבְטוֹ → "fimbo yake": source=[שִׁבְט], target=["fimbo"] — primary; source=[וֹ], target=["yake"] — primary
- On a PREPOSITION — three patterns:
  1. Free preposition + fused pronominal form (~52%): kwako, juu yao, ndani yangu, dhidi yangu, nyuma yako, pamoja naye/nami, kuliko yeye. Preposition and suffix both primary (separate records if separate words, one N:1 record if one fused word).
  2. ABSORBED INTO THE VERB (~26%) as object marker + applicative -ia/-ea (or just the transitive frame): ONE record, source=[verb, preposition, suffix], target=[the verb word], ALL PRIMARY (verb root, preposition, suffix OM).
     כָתַבְתִּי לְךָ → "sijakuandikia": source=[כָתַבְתִּ, י, לְ, ךָ], target=["sijakuandikia"] — all primary
     וַיְהִי דְבַר יְהוָה אֵלַי → "Neno la Bwana likanijia": source=[וַ, יְהִי, אֵלַ, י], target=["likanijia"] — all primary (-ni- = suffix, -ia = "to")
  3. Dropped/restructured (~22%): NEQ both only when certain, else unrecorded.
- Subject suffix of an infinitive construct (בְּהִמֹּלוֹ "when he was circumcised") restructured as a finite clause (alipotahiriwa): the suffix is SECONDARY to the verb (the subject marker carries it).\
"""

NEGATION_BLOCK = """\
## NEGATION
Follow the NT precedent: every negative morpheme aligns PRIMARY to the Hebrew negator (לֹא/אַל/אֵין/בַּל/בְּלִי), wherever it surfaces; locate it inside the fused verb word even though it is not a separate token. NEQ ONLY when certain the translator dropped the negator; otherwise leave unrecorded.

- FUSED negative verb (ha-, -ja-, -ku-, si-, hu-…): the negator and the verb are ONE record (source=[לֹא, verb], target=[the verb word]), both primary.
  לֹא יָדַע → "hakufahamu": source=[לֹא, יָדַע], target=["hakufahamu"] — both primary
  לֹא יֵעָנֶה → "hatajibiwa" (negative future); אַל תִּתֵּן → "Usiruhusu" (prohibitive/subjunctive -si-: אַל + yiqtol)
- Free negative words — own record, primary: "wala" (וְלֹא), "bila"/"pasipo" (לֹא/בְּלִי + noun), "sio"/"si" (verbless לֹא clause), "hakuna"/"hamna"/"hapana" (אֵין).
- אֵין/אַיִן as "no more / is gone" (אֵינָם) → often a verb of disappearance or negative verb (hutoweka, hawapo): still primary to אֵין, fused into that verb's record.
- A negator ONEN restructures away (an affirmative rephrase) → NEQ if certain, else unrecorded; ~11% of OT verses with a single negator show no recognisable negative form.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS AND RELATIVES
Swahili has no participle morphology: Hebrew participles (substantive/attributive) and אֲשֶׁר/שֶׁ relatives all funnel into the relative system. Infixed-first in the OT (≈56% vs amba- ≈20% for אֲשֶׁר):
1. INFIXED relative concord inside the verb (-ye-/-o-/-lo-/-cho-/-vyo-…): "aliyetukumbuka", "wamtumainio". The concord is primary to אֲשֶׁר (or the article before a participle); the verb root primary to the verb; if fused into one word, ONE record.
2. amba- + concord (ambaye, ambao, ambapo…) — the minority (higher in poetry): primary to אֲשֶׁר.
   אֲשֶׁר לֹא יָדַע → "ambaye hakufahamu": source=[אֲשֶׁר], target=["ambaye"] — primary; source=[לֹא, יָדַע], target=["hakufahamu"] — both primary
3. wale/yule + relative (wale wanaoshikilia) for article + participle — wale primary to the article.
4. -enye "having" (mwenye/wenye/yenye…) when the sense is "characterized by X" — primary to the participle/adjective; also for Hebrew בּוֹ "in whom" (Lev 21:19 mwenye).
5. Passive relative (lililowekwa na baba zako): the verb with -wa; "na" = agent marker, primary to the agent noun's preposition role.
6. Article + participle may instead be a plain finite verb with no relative word, esp. generic statements: the Hebrew article is then SECONDARY to the participle's record.
GNOMIC hu-: a habitual/gnomic present (hutuma, husema; ~2,100 forms, over half in Proverbs/Psalms/Job) rendering yiqtol, participles or generic perfects. hu- is a tense morpheme with no Hebrew word of its own: nothing to mark separately — the verb word is primary.
A relative the translator supplied with no Hebrew אֲשֶׁר → NEQ or secondary material.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS
Swahili has a true infinitive (class 15 ku- + stem).
- Infinitive construct (לְ+inf, bare inf) → "ku-" verb (one word): infinitive primary, the לְ SECONDARY (the dominant case, ~72%).
  Or a SUBJUNCTIVE (…-e) or "-ki-" clause (~24% of לְ+inf): the Swahili verb is primary to the infinitive, the לְ secondary.
  לְנַחֵל (אֶת בְּנֵי יִשְׂרָאֵל) → "wagawanye (urithi)": source=[לְ, נַחֵל], target=["wagawanye"] — primary: נַחֵל; secondary: לְ
- לְ+inf of purpose also → "ili"/"kusudi": primary to לְ; infinitive → its verb, primary.
- בְּ/כְּ+inf (temporal) → "-po-"/"wakati"/"-ki-" (~75%/60%): fused into the verb → בְּ/כְּ primary in the verb's ONE record; "wakati" free → primary in its own record. The inf's suffix = subject → secondary (subject marker).
  בְּהִמֹּלוֹ → "alipotahiriwa": source=[בְּ, הִמֹּל, וֹ], target=["alipotahiriwa"] — בְּ and the verb primary; וֹ secondary
- לֵאמֹר → "kusema" primary (only ~24%); when the preceding speech verb (akaniambia, alipoambiwa) already introduces the quotation and no say-word remains → לֵאמֹר NEQ.
- Infinitive absolute: (a) COGNATE emphasis next to a finite verb of the same root → an intensifier word (hakika, kabisa, kamwe, kwa makini, kupita kiasi, lazima for the death formula מוֹת יוּמָת → "ni lazima auawe"), primary 1:1 to the infinitive absolute (~46% of cognate cases); the finite verb aligns separately. (b) Not rendered → secondary to the finite verb if it carries the force, NEQ only when certain. (c) Standing as an IMPERATIVE (פָּתוֹת, עָשֹׂה) → ordinary imperative, primary 1:1 to the main verb.
  מוֹת תְּמֻתוּן → "Hakika hamtakufa": source=[מוֹת], target=["Hakika"] — primary; source=[תְּמֻתוּ, ן], target=["hamtakufa"] — primary\
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

SWH_OT_CONFIG = LanguagePromptConfig(
    language_code="swh",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(SWH_OT_CONFIG)
