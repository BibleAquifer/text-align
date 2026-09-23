"""Traditional Chinese (zht) target-language prompt config for OT (Hebrew) refine-alignment.

Distilled from `docs/alignment-principles-ot.zht.md`. Every finding rests on raw-text
spot-checking (14-20 randomly sampled verses per construction) against two independent
Traditional Chinese texts — our own production target CUV
(`data/alignments/alignments-cmn/data/targets/CUV/`) and BOCCB2023T (Biblica® Open
Chinese Contemporary Bible 2023, Traditional, a genuinely independent modern
translation) — plus general Mandarin/Biblical Hebrew linguistic reasoning. **No
alignment data is used anywhere in this document or the principles doc.**

An earlier draft rested entirely on UBS's `WLCM-CU2010T-manual.json` (the OT's only
ever-produced alignment — there is no CUVMPS OT alignment to fall back on) and was
retracted by direction: that alignment was directly confirmed unreliable for
word-level verification (98.8% of לֹא tokens showed "unaligned" despite the Hebrew
text plainly having a Chinese negation correspondent in every sampled verse — it was
built for a different purpose). This rebuild mirrors `nt/zht.py`'s rebuild exactly,
using WLCM.tsv joined to both editions' raw target text by verse.

**Two genuine reversals surfaced by reading real text instead of trusting
character-matching over the retracted alignment**: (1) substantive/attributive
participles were previously claimed to show near-zero `的` — false; they regularly
take `的`, either bare-nominalized or with an explicit head noun, once the real
functional split (verbal/predicative vs. substantive/attributive) is checked instead
of mere article-adjacency. (2) pronominal suffixes were previously claimed to mostly
drop explicit pronoun marking — also false, an artifact of a crude character set that
missed pronoun forms like `它`/`她`; careful reading shows explicit marking is the
majority outcome.

**Consequence for precision, updated:** PASSIVE VOICE has since been re-verified at
full-corpus scale (every WLCM niphal/pual/hophal verb token, 5,024 tokens / 4,100
verses, joined to both editions' text) with real percentages, not a small sample.
INFINITIVAL CONSTRUCTIONS has been independently re-verified with a 35-verse sample
(previously inherited by analogy from NT and explicitly flagged as unconfirmed) and
found infinitive absolute is NOT unmarked, contrary to the inherited assumption. The
remaining blocks (articles, construct chains, copula, pronominal suffixes, negation,
participles) are still at their original 14-20-verse spot-check stage. See
`docs/alignment-principles-ot.zht.md` for exact numbers and methodology.

**Draft status:** not yet reviewed by a native Mandarin speaker — the same caveat
`nt/zht.py` carries, on top of these smaller sample sizes.

Key differences from OT English (`eng.py`), inherited from `nt/zht.py`'s mechanics
where they transfer, with real OT-specific findings where they don't:
  BASE_BLOCK  — no articles (spot-checked, ~27 of ~30 sampled article instances have no
                correspondent). The demonstrative branch has a precise, recurring
                trigger: the fixed `יוֹם/עֵת הַהוּא` ("that day/time") idiom — every
                Branch A instance in the sample was this construction, not general
                anaphoric reference the way NT Greek's article sometimes triggers one.
                Construct chains: presence of `的` correlates with whether the
                possessor is a pronominal suffix (usually gets `的`, e.g. `他的僕人`)
                versus a full noun, especially names/geography/fixed pairs (usually
                bare, e.g. `亞割谷`) — a real refinement over a flat "bare is the
                default" claim. Copula/verbless clauses follow the shared OT base
                pattern (supplied `是`/`有`/`在` with no Hebrew verb behind it → NEQ).
                Passive voice (folded into BASE_BLOCK since OT's shared tag set has no
                dedicated PASSIVE conditional, matching `ot/arb.py`'s approach):
                full-corpus-quantified against every WLCM niphal/pual/hophal verb
                (5,024 tokens / 4,100 verses). Unmarked/restructured-active is still
                the majority but by a smaller margin than the raw counts suggest
                (~67%, corrected). `被` is real and NOT rare (12.5% exact count) — it
                clustered specifically around violent/adversative events (capture,
                destruction, burning, exile), a cleaner confirmation of the
                adversative-connotation theory than the NT sample gave. `受`/`得`/`蒙`
                receive-construction is real and, after correcting for sample-size
                noise, genuinely HIGHER in OT than NT — ~20% vs. NT's ~9-11% —
                reversing the earlier 20-verse sample's "zero instances" finding, which
                was simply too small a sample. A `所`-nominalizer strategy also
                appears (0.7%), matching the NT doc's `為...所`/`所...的` finding, plus
                a related bare `為`+agent+verb variant with no `所` at all.
  PRONOMINAL_SUFFIX_BLOCK — REVERSED from the earlier draft: explicit Chinese pronoun
                marking (的+pronoun for noun hosts, bare pronoun for verb/preposition-
                governed objects) is confirmed the MAJORITY outcome in a 14-verse
                spot-check, not the exception. Dropped only when the referent was
                already named earlier in the clause (discourse-driven omission,
                matching NT Chinese pro-drop) or the phrase is a fixed idiom.
  NEGATION_BLOCK — three Hebrew negators (לֹא ordinary, אַל jussive/prohibitive,
                אֵין/אַיִן existential) map to different Chinese forms, confirmed by a
                16-verse raw-text spot-check with a Chinese negator present in
                essentially every verse: לֹא → 不/沒/沒有/並無/絕不/不再; אַל → 不要;
                אֵין → 沒有/並無; לֹא...עוֹד ("no longer") discontinuous, matching NT's
                own finding.
  PARTICIPLE_BLOCK — REVERSED from the earlier draft (see above): the real split is
                the participle's function (verbal/predicative → no `的`; substantive/
                attributive → `的`, bare-nominalized or with a head noun), not
                article-adjacency. Also newly surfaced: a `是...的` cleft-emphasis
                strategy for a fronted/emphasized predicative participle.
  INFINITIVE_BLOCK — Independently re-verified with a 35-verse sample, overturning the
                inherited "plain verb, no marker" assumption for infinitive absolute:
                it consistently gets a Chinese modal/intensifying adverb
                (必/必要/總要/大大) secondary to the paired finite verb, confirmed 4/4
                in sample — not unmarked. Infinitive construct splits by function
                rather than one uniform pattern: quotative לֵאמֹר ("saying") after a
                speech verb is near-categorically bare 說; purpose (לְ + infinitive)
                sometimes gets an explicit 為/為要 marker and sometimes doesn't (real
                variation, not predictable from the construction alone); temporal
                (preposition + infinitive) has THREE coexisting strategies
                (的時候/後/一...就), not just the single 的時候 pattern documented
                elsewhere; some infinitives are lexicalized into a plain noun
                (居所, 家譜); the residual case still defaults to a bare marker-free
                verb.

Source files: `src/text_align/refine/prompt/ot/zht.py`, `src/text_align/refine/prompt/ot/eng.py`
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language


# ---------------------------------------------------------------------------
# Traditional Chinese-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Hebrew source
text (MACULA Hebrew / Westminster Leningrad Codex).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Hebrew word(s) or word-part(s) are behind this translation word.

## HEBREW WORD-PART TOKENS
MACULA Hebrew splits prefixed morphemes into separate word-part tokens, each with its own BCVWP ID. Common word-parts:
- Inseparable prepositions (בְּ/לְ/כְּ/מִ) — pos=preposition
- Definite article (הַ/הָ/הֶ) — pos=particle
- Conjunction waw (וְ/וַ/וּ) — pos=conjunction
- Pronominal suffixes (וֹ, הוּ, ם, etc.) — pos=suffix

Word-part present → align Chinese correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include construction-implied particles (的, aspect particles, 將/把) even where Hebrew has no separate word for them, so long as the target word exists because of a grammatical feature carried by a specific Hebrew token or word-part. Prefer one record per source token/word-part — split rather than group. Grammar-required translation words are secondary to the source token whose grammar/discourse context requires them — not NEQ. NEQ is for words with no source-language anchor at all.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token/word-part
secondary — exists only because of a grammatical or syntactic feature of the Hebrew token (case, aspect, construct state, coreference); no independent Hebrew word backs it
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Supplied subject pronoun — no Hebrew pronoun token; person/gender/number encoded in verb ending. Supplied on a new/switched subject → secondary. Dropped for topic continuity → none expected, leave unrecorded.
- 的 as construct-chain marker — see CONSTRUCT CHAINS below; expect it for a pronominal-suffix possessor, expect bare juxtaposition (no 的) for a full-noun possessor especially names/geography. When present, secondary to the construct (bound-form) noun or to the pronominal suffix.
- Merged article — no separate article word-part; correspondent secondary to the noun token.
- Preposition+article merged (בַּ/לַ/כַּ) — Chinese preposition primary; any demonstrative/article correspondent secondary, both to that merged token.
- Auxiliary verbs for participles — main verb primary; auxiliary secondary.
- Classifier (個/位/隻/座/etc.) — secondary to the counted noun, sharing its record; required by Mandarin's obligatory numeral+classifier+noun grammar, no independent Hebrew word.

- Periphrastic rendering — when a single Hebrew token is rendered by multiple Chinese words, all words carrying lexical content are primary; purely grammatical connectors are secondary to the same token. Never NEQ a target word that expresses a component of the source word's meaning.
  מָשַׁל → "行使統治權": all words carrying content primary
  הוֹדוּ → "感謝": both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no Chinese equivalent).
Supplied copula (是/有/在) with no Hebrew verb token → NEQ target (verbless clause) — see COPULA / VERBLESS CLAUSES.
的, 所, aspect particles (了/著/過), and 將/把 are never NEQ even when they have no Hebrew trigger of their own — secondary to the source token whose grammar/discourse context requires them.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.

## ARTICLE
Chinese has no article system, matching NT Chinese. Hebrew's definite article (הַ/הָ/הֶ, a separate word-part) has no target correspondent by default — confirmed the large majority in a spot-check. Never NEQ — secondary to the noun, no target word required.
  אֱלֹהִים → "上帝" alone — no secondary needed even without an article word-part present
The demonstrative branch (這/那) has a precise, recurring trigger: the fixed idiom "NOUN (typically יוֹם/עֵת) + הַהוּא" ("that day/time"). Every demonstrative instance found in the spot-check was this construction — not general anaphoric reference.
  הַ יּוֹם הַ הוּא ("that day") → "那日"/"那時": 那 primary 1:1
Outside this idiom, expect no correspondent at all, even more consistently than NT Greek's article.

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form (bound/absolute noun pair) — no preposition token. Whether 的 is supplied correlates with the possessor type:
- Pronominal-suffix possessor (his/her/their/my/your) — usually gets 的, matching ordinary Mandarin possessive-pronoun marking.
  עַבְדּוֹ ("his servant") → "他的僕人": 的 secondary to the suffix
  שֵׁם יְהוָה (with implied "his") → "耶和華的名": 的 secondary (note the word order flips to possessor-的-possessed)
- Full-noun possessor, especially proper/geographic names or fixed pairs — usually bare, no 的.
  עֵמֶק עָכוֹר ("valley of Achor") → "亞割谷": no 的, both nouns primary in their own records
  מִשְׁפְּחוֹת יִשָׂשכָר ("clans of Issachar") → "以薩迦各族": no 的
Check the actual target text either way — both patterns are real and this is a tendency, not an absolute rule.

## COPULA / VERBLESS CLAUSES
Hebrew has no overt copula in present-tense nominal/verbless clauses (subject and predicate simply juxtapose) — unlike Greek's εἰμί, which is nearly always present. When Chinese supplies 是/有/在 with no Hebrew verb token behind it, that supplied copula is NEQ target.
  יְהוָה רֹעִי ("the LORD [is] my shepherd") → "耶和華是我的牧者": "是" → NEQ target; "耶和華" primary; "我的牧者" primary with 的 secondary to the possessive suffix
When Hebrew uses הָיָה ("to be," for past/future/emphatic contexts), it aligns normally, same COPULA STRATEGIES splits as NT Chinese (existential 有, identity 是, locative 在).

## PASSIVE VOICE
Do not assume any particular marking strategy for a Hebrew passive-stem verb (Niphal, Pual, Hofal). Unmarked/restructured-active is the majority (~67% of passive-tagged verbs, full-corpus-checked) but by a smaller margin than a raw character search suggests: either an inherently non-agentive positional/stative verb needing no marking, e.g. נִצָּב "standing" → 站, or the clause recast fully active with a generic/implied agent, e.g. יֵאָכֵל "it will be eaten" → 要...吃.
被 is real and NOT rare (~12.5%) — it clustered specifically around violent/adversative events (capture, destruction, burning, exile) in every sampled instance, a clean confirmation of Mandarin 被's known adversative connotation. Do not assume it by default, but do not treat it as absent either — check whether the event is a notable/adversative one.
  נִּלְכָּד (caught) + יִשָּׂרֵף (he will be burned) → "被取的人...必被火焚燒": 被 secondary to each verb
  תִּבָּקַע (broken into) → "城被攻破": 被 secondary
  נִשְׁבָּה (taken captive) → "被擄去了": 被 secondary
受/得/蒙 receive-construction is real and NOT rare (~20%, higher than NT's rate — check the actual verb, don't assume OT skips this strategy). CAUTION: 得 alone is also the ordinary verb-complement particle with no passive sense at all — check the clause.
  נָצַל (be delivered, Niphal) → "得逃脫": 得 secondary
  מוּל (he will be circumcised, Niphal) → "要受割禮": 受 secondary
A 所-nominalizer strategy also occurs (~0.7%), framing the passive-oriented sense (secondary to the verb it frames, same pattern as the temporal/participle 所...的 construction), plus a related bare 為+agent+verb variant with no 所 at all.
  הַנִּמְצָא ("[that] found") → "所遇見的": 所, 的 secondary
  וְנִבְנֽוּ ("it will be rebuilt," agent supplied without 所) → "這城必為耶和華建造": 為 secondary, marking the agent
Check the actual target text — unmarked is the most likely outcome but far from the only real option.

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → 和/而/但/於是/就: primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever Chinese word carries its force in context. Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — 的 (relativizer, see PARTICIPIAL CONSTRUCTIONS) or a relative clause without a separate marker. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply. Last resort — always prefer standard records, even with loose primary matches. Function-word-only source units are never idioms.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Pronominal suffixes are separate word-part tokens (pos=suffix). Explicit Chinese pronoun marking is the DEFAULT expectation for a pronominal suffix — check the immediate context before assuming one is dropped, not the other way around.

- Noun-hosted possessive suffixes regularly get 的 + pronoun. Primary.
  כְבוֹדוֹ ("his glory") → "他的榮耀": 他 primary; 的 secondary
  רֹאַיִךְ ("those who see you") → "凡看見你的": 你 primary
- Verb/preposition-governed object suffixes regularly get an explicit pronoun too. Primary.
  אֶעֱנֶנּוּ ("I will answer him") → "我可以回答他": both 我 and 他 primary
  לְאַחֶיךָ ("to your brothers") → "你哥哥們": 你 primary

A real minority of suffixes are dropped/absorbed — specifically when the referent is already established in context (discourse-driven omission, the same pattern as NT Chinese pro-drop) or the phrase is a fixed idiom. Secondary, no target word, in these cases.
  לְמִשְׁפְּחֹתָם ("by their families," referent already the topic of the clause) → "按着宗族": no explicit "their"
  בְעִתּוֹ ("in his/its proper time," idiomatic) → "隨時": no explicit pronoun
Fixed honorific/divine titles can also fossilize the suffix away entirely — אֲדֹנָי ("my Lord," a lexicalized divine title) → 主, no "my."

Default to expecting an explicit correspondent; drop it only when one of the above conditions clearly applies.\
"""

NEGATION_BLOCK = """\
## NEGATION

Three source forms map to different Chinese strategies, confirmed by a raw-text spot-check: a Chinese negation correspondent is present in essentially every sampled verse. Never NEQ a negation particle when the target text plainly contains a negator.

- לֹא/לֹּא/לוֹא (ordinary negation) → 不/沒/沒有/並無/絕不/不再: primary to the negated verb's negation, in its own record (discontiguous from the verb — do not include "不" as secondary in the verb's own record).
  לֹא הוֹרִישׁ ("did not dispossess") → "沒有趕出": primary 1:1
- אַל (jussive/prohibitive) → 不要: primary 1:1, the imperative-negation-specific "don't" form.
  אַל תִּירְאִי ("do not be afraid") → "不要害怕": primary 1:1
- אֵין/אַיִן (existential "there is no") → 沒有/並無: all words carrying the negation primary.
  אֵין תּוֹרָה ("there is no law") → "沒有律法": primary
  Pronominal suffixes on אֵין (e.g. אֵינֶנּוּ "he is not") → suffix word-part primary 1:1 (see PRONOMINAL SUFFIXES).
- לֹא...עוֹד ("no longer") — discontinuous, matching NT Chinese's own οὐκέτι/μηκέτι finding.
  לֹא תִטְהֲרִי עוֹד ("you will not be clean again") → "再不能潔淨": both words primary to the single discontinuous Hebrew construction.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

The real split is the participle's FUNCTION — verbal/predicative vs. substantive/attributive — not whether it is adjacent to the article.

### Verbal/predicative — no 的
A participle functioning as an ordinary clause predicate (an ongoing-action narrative description) renders as a plain Chinese verb, primary alone, no 的.
  רֹאֶה / מְצַעֵק ("was seeing" / "was crying out") → "看見...呼叫說": primary alone
  חוֹנֵן / מַלְוֶה ("showing favor" / "lending," habitual description) → "恩待人，借給人": primary alone

### Substantive/attributive — 的, bare-nominalized or with an explicit head noun
Confirmed regularly present — do not assume article-adjacency alone predicts a low 的 rate; check the participle's function instead.
  הַנֹּפְלִים ("those who fall," bare-nominalized, no separate head noun) → "凡跌倒的": 的 secondary, nominalizing the participle
  הַכְּפוּפִים ("those bowed down") → "凡被壓下的": 被 AND 的 both secondary, stacking passive-marking and nominalization on the same participle
  הַחֹנִים ("those pitched/encamped," with an explicit head noun) → "南邊安的營" ("the south-pitched camps"): 的 secondary, linking the participle to 營 ("camp")
  A lexicalized bypass is also real: some substantive participles fossilize into a plain noun that doesn't raise the 的-nominalizer question at all — לַקֹּנֶה ("to the purchaser") → "買主" ("buyer"), a single lexicalized noun.

### 所...的 framing, an alternative to bare 的
Matches the PASSIVE VOICE and general 的 pattern.
  נֹתֵן ("[which] I am giving") → "所賜給你的": 所, 的 secondary

### A cleft-emphasis strategy for a fronted/emphasized predicative participle
When the subject is fronted for emphasis in Hebrew, a predicative participle can be rendered with a 是...的 cleft rather than a bare verb.
  הֵם מַקְרִיבִם ("it is THEY who present [it]," subject fronted for emphasis) → "是他們獻的": 是, 的 secondary, framing the emphasized subject-verb relationship

### Periphrastic (participle + explicit הָיָה)
הָיָה → Chinese auxiliary, separate primary record; participle → main verb, primary.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

Independently re-verified against a 35-verse sample. Infinitive construct and infinitive absolute behave differently — check which one you have before applying either rule.

### Infinitive absolute (cognate/emphatic construction — verb doubled for emphasis) — NOT unmarked
Confirmed 4/4 in sample: consistently renders with a Chinese modal or intensifying adverb (必/必要/總要/大大) placed before the finite verb — secondary to the finite verb, not a separate lexical item, and not simply absorbed with no trace.
  שׂוֹשׂ אָשִׂישׂ ("I will greatly rejoice") → "我...大大歡喜": 大大 secondary
  הָיוֹ יִהְיֶה ("he will surely become") → "必要成為": 必要 secondary
  הָשֵׁב תְּשִׁיבֶנּוּ ("you shall surely return it") → "總要牽回來": 總要 secondary
  מוֹת יָמוּת ("he will surely die") → "必要死": 必要 secondary

### Infinitive construct (bare verbal noun, usually governed by a preposition) — splits by function
- Quotative לֵאמֹר ("saying") after a verb of speech — near-categorical: bare 說, the redundant "saying" absorbed into the ordinary speech verb, no separate marking. Primary alone.
  וַיֹּאמֶר...לֵאמֹר ("and he said, saying") → "...說": 說 primary alone, לֵאמֹר absorbed
- Purpose (לְ + infinitive construct, "in order to X") — real variation: sometimes an explicit purpose marker 為/為要 is supplied (secondary, framing the verb), sometimes the bare verb alone carries the purpose sense with no marker. Check the actual text rather than assuming either.
  לְהַטּוֹת ("to pervert") → "為要顛倒判斷": 為要 secondary
  לְמַלֵּא נַפְשׁוֹ ("to satisfy his hunger") → "充飢": no separate marker, purpose absorbed into the bare compound verb
- Temporal (preposition + infinitive construct, "when/after X") — THREE coexisting strategies, not just 的時候:
  אַחֲרֵי לֶכְתָּם ("after they had gone") → "他們走後": 後 secondary
  כְּהַזְכִּירוֹ ("as he mentioned") → "他一提...就": the 一...就 ("as soon as...then") construction
  בְּרִבָם ("when they contended") → "...的時候": the same 的時候 pattern used elsewhere in this config
- Lexicalized noun bypass — some infinitive constructs fossilize into a plain noun (parallel to PARTICIPIAL CONSTRUCTIONS' לַקֹּנֶה → 買主 finding).
  שִׁבְתְּךָ ("your dwelling") → "你的居所": 居所 a plain noun, no infinitive marking needed
  הִתְיַחְשָׂם ("their genealogy") → "他們的家譜": same pattern
- Otherwise (direct object / embedded complement infinitives with none of the above functions) — the residual default: plain Chinese verb, primary alone, no separate marking.
  הַבְדִּיל ("to separate") → "分": primary alone\
"""


# ---------------------------------------------------------------------------
# Block registry and config
# ---------------------------------------------------------------------------

BLOCK_ORDER = [
    "PRONOMINAL_SUFFIX",
    "NEGATION",
    "PARTICIPLE",
    "INFINITIVE",
]

CONDITIONAL_BLOCKS: dict[str, str] = {
    "PRONOMINAL_SUFFIX": PRONOMINAL_SUFFIX_BLOCK,
    "NEGATION":          NEGATION_BLOCK,
    "PARTICIPLE":        PARTICIPLE_BLOCK,
    "INFINITIVE":        INFINITIVE_BLOCK,
}

FORCED_INCLUSIONS: dict[str, set[str]] = {}

ZHT_OT_CONFIG = LanguagePromptConfig(
    language_code="zht",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(ZHT_OT_CONFIG)
