"""Traditional Chinese (zht) target-language prompt config for refine-alignment.

Distilled from `docs/alignment-principles-nt.zht.md`. Every finding in that doc rests
on raw-text spot-checking (12-25 randomly sampled verses per construction) against two
independent Traditional Chinese texts — our own production target CUV
(`data/alignments/alignments-cmn/data/targets/CUV/`) and BOCCB2023T (Biblica® Open
Chinese Contemporary Bible 2023, Traditional, a genuinely independent modern
translation, not another Union Version edition) — plus general Mandarin/Koine Greek
linguistic reasoning. **No alignment data is used anywhere in this document or the
principles doc.**

An earlier draft of both files was built from Clear-Bible's `alignments-cmn` repo
(Biblica's CUVMPS gold alignment, cross-checked against UBS's CU2010T alignment) and
was retracted by direction: CUVMPS was found to differ from CUV in more than script
(a real `神`/`上帝` lexical divergence, the well-known 神版/上帝版 dual-edition
tradition, plus an unexplained 85.4% verse-level token-count mismatch between the two
TSVs), and CU2010T's alignment was confirmed unreliable for word-level verification
(98.8% of negation particles showed "unaligned" despite the Chinese text plainly
containing a negator in every sampled verse — it was built for a different purpose).
See the principles doc's "Methodology" section for the full account.

**Consequence for precision:** this rebuild has real, independently-verifiable worked
examples for every claim, but no exact corpus-wide percentages — every number below is
either a small hand-verified sample size (e.g. "19 of 25 sampled passives") or an
unconditioned whole-corpus character count (not conditioned on a specific Greek
construction). Treat percentages carried over from the earlier alignment-based draft
(now removed from this docstring) as unconfirmed estimates, not settled numbers.

**Draft status:** not yet reviewed by a native Mandarin speaker — the same caveat the
other non-Romance configs (`ind`, `hin`, `arb`) carried before their own review, on top
of the smaller sample sizes noted above.

**Orthography note:** CUV consistently uses the older variant characters `着` (not
`著`) and `裏` (not `裡`) — confirmed directly in the target TSV. All worked examples
below use CUV's actual characters, not the modern standard forms (which BOCCB2023T
uses instead).

Simplified Chinese (zhs) is a fully separate config, not derived from this one — see
`docs/alignment-principles-nt.zht.md`'s intro for why. It will get its own principles
doc and code once real Simplified target data is available.

Key differences from the other supported languages:
  BASE_BLOCK  — no articles at all (like Indonesian/Hindi; a 20-verse spot-check found
                no target correspondent for the large majority of Greek articles). `的`
                is the hardest-working function word in the language, covering
                genitive marker, attributive linker, substantive-participle
                nominalizer (see PARTICIPLE_BLOCK), and a temporal-clause marker
                (`...的時候`) all at once — role must be determined per instance. A
                related nominalizer, `所` (often `為...所`/`所...的`), surfaced
                repeatedly alongside `的`, especially for patient-oriented/passive
                senses — not documented in the earlier draft at all. The disposal
                construction (`將`/`把`) fronts a definite object with a marker that
                carries no lexical content of its own; genuinely polysemous, though —
                `將` also means "about to" (adverb) and appears in the fixed noun
                `將來` ("future"), neither of which is the disposal construction, so
                raw character counts overcount the true rate. Copula εἰμί splits at
                least four ways (existential `有`, comitative `同在`, identity
                `是`/`就是`, locative `在`); `就是` is real and appears independently in
                BOTH CUV and BOCCB2023T at different verses — directly refuting an
                earlier retracted claim that it was CUV-specific. Classifiers
                (個/位/etc.) ride secondary inside the counted noun's own record, not
                as unaligned filler. Locative words trail their noun (postpositional)
                rather than preceding it, and the common ones (裏/上/中/內) have
                distinct dominant senses, not interchangeable defaults. Pro-drop is
                discourse-driven like Indonesian, confirmed qualitatively throughout
                every sample (no precise rate re-derived without alignment data).
  PASSIVE_BLOCK — an UNMARKED verb (no passive morphology at all) is the clear
                majority strategy in a 25-verse spot-check (~19 of ~30 verb tokens).
                `被` did not appear at all in CUV's own text across that sample (though
                BOCCB2023T used it twice at verses where CUV didn't), consistent with
                but not proof of it being rare. `受`/`得`/`蒙` "receive/undergo NOUN" is
                real but a genuine minority (1 clear instance in the sample). A
                genuinely new finding this pass surfaced that the earlier
                alignment-based draft missed entirely (it only searched for
                `被`/`受`/`得`/`蒙` characters): a classical/literary passive marker,
                `為...所`/`所...的`, distinct from `被`. Also newly surfaced: a
                reflexive/self-directed active conversion (Greek passive recast with a
                reflexive object, e.g. `敗壞了自己` "ruin themselves").
  PARTICIPLE_BLOCK — only the substantive (nominalizing) case has real evidence: `的`
                nominalizes a Greek participle, confirmed repeatedly including a
                Romans 12:8-style chain of bare `的`-nominalized participles with no
                separate pronoun/head-noun needed. Adverbial/genitive-absolute
                participle handling was not specifically researched for Chinese;
                falls back to the general TOKEN ROLES guidance.
  AUTOS_BLOCK — the reflexive `自己` is confirmed genuinely narrow in a 15-verse
                spot-check of αὐτός instances: only 1 showed the coreference-driven
                substitution pattern (a plain Greek pronoun replaced by `自己` because
                its referent circles back to the clause's own subject); the other 14
                were ordinary non-reflexive pronoun translations. The split between
                "direct correspondence to an already-reflexive Greek word" and "genuine
                substitution" from the earlier alignment-based draft is a plausible but
                unconfirmed estimate at this sample size.
  VERBAL_ASPECT_BLOCK — `了` (perfective, telic/punctual events) and `過` (experiential,
                anterior reference) are both real and confirmed in a 12-verse
                spot-check of Greek perfect-tense verbs, but `過` is NOT obligatory even
                on negated perfects — a real counter-example was found (John 5:37's
                negated perfects took no `過` at all), correcting an over-generalization
                risk. Stative "know" verbs (οἶδα family) consistently take NO aspect
                particle at all, every time sampled, in both editions.

`IMPERSONAL_BLOCK`, `INFINITIVE_BLOCK`, `HINA_BLOCK`, `COMPARATIVE_BLOCK`,
`HOTI_BLOCK`, `CONDITIONAL_BLOCK`, and `NEGATION_BLOCK` are imported unchanged from
`eng.py` — these constructions were not part of the principles-doc research scope
(which focused on the phenomena that actually surfaced in the samples: no articles,
`的`, the disposal construction, copula splits, classifiers, passive voice, aspect
particles, reflexives, pro-drop, and locative postpositions). Unlike `hin.py`, which
explicitly researched negation and infinitives for Hindi, none of these seven areas has
Chinese-specific findings yet — confirm with a native speaker (or a dedicated follow-up
pass) before assuming English's rules transfer cleanly, particularly NEGATION_BLOCK,
since Mandarin negation (不/沒/別/未) is typologically nothing like English's.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import (
    COMPARATIVE_BLOCK,
    CONDITIONAL_BLOCK,
    BLOCK_ORDER,
    FORCED_INCLUSIONS,
    HINA_BLOCK,
    HOTI_BLOCK,
    IMPERSONAL_BLOCK,
    INFINITIVE_BLOCK,
    NEGATION_BLOCK,
)


# ---------------------------------------------------------------------------
# Traditional Chinese-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied prepositions, grammatically-implied particles (的, 了/着/過, 將/把), and construction-required markers even where Greek has no separate word for them, so long as the target word exists because of a grammatical or syntactic feature carried by a specific Greek token. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Combine into N:M records only when tokens form an inseparable semantic/idiomatic unit (light-verb compound, lexicalized naming formula) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (的, aspect particles, 將/把, reflexive substitution) are secondary to the source token whose grammar/discourse context requires them — not NEQ. NEQ is for words with no source-language anchor at all.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Greek token
secondary — exists only because of a grammatical or syntactic feature of the Greek token (case, aspect, voice, coreference, subordination); no independent Greek word backs it
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- 的 as genitive/possessive marker (the single largest 的 use) — secondary to the genitive-case Greek noun/pronoun.
  τῶν δούλων αὐτοῦ → "他僕人"/"他的僕人": 的 secondary to αὐτοῦ when present
- 的 as attributive-adjective linker — secondary to the adjective it links; no dedicated Greek word.
- 的 as substantive-participle nominalizer — see PARTICIPIAL CONSTRUCTIONS.
- 所 as a related nominalizer, often paired with 的 (所...的) or 為 (為...所) — a more literary strategy for the same nominalizing role, especially for patient-oriented/passive senses. τὸ ὅραμα ὃ εἶδεν → "所看見的異象": 所 and 的 both secondary, framing the verb 看見.
- 的時候 temporal-clause marker — a temporal preposition (ἐν/ἐπί/ἐφ᾽) triggers "...的時候" ("the time when..."); both 的 and 時候 secondary to the preposition.
  ἐπὶ τῆς μετοικεσίας Βαβυλῶνος → "百姓被遷到巴比倫的時候": 的 and 時候 secondary to ἐπί
- BA/JIANG disposal marker (將/把) — pure grammatical device that fronts a definite direct object; no independent lexical content, secondary to the fronted object noun phrase, not to the verb. A genuine but not overwhelming minority construction — do not expect it by default. CAUTION: 將 is polysemous — it also means "about to" (a future/imminent-aspect adverb, e.g. 那七日將完 "those seven days were about to end") and appears in the fixed noun 將來 ("the future"). Neither of those is the disposal construction. Disambiguate by checking whether 將/把 is immediately followed by a definite noun phrase + verb (disposal) rather than a bare verb or the noun 來.
  ἀπήλασεν αὐτοὺς ἀπὸ τοῦ βήματος → "就把他們攆出公堂": 把 secondary to the fronted object 他們; 攆出 primary to ἀπήλασεν
- Copula εἰμί — splits across several target verbs depending on clause type; do not assume one lexeme covers all εἰμί. Existential "there is/was" → 有. Comitative "was with" → a fused compound verb like 同在 (real but low-frequency; plain 在 is far more common for ordinary locative "be at"). Predicate-nominal identity (the majority) → 是, optionally intensified 就是 ("is precisely") — 就是 is real and not rare, and appears independently in multiple different Chinese Bible translations, not just one; align 就 as secondary to εἰμί when present. Locative "to be at/in" → 在.
  Ἐν ἀρχῇ ἦν ὁ λόγος → "太初有道": ἦν primary to 有
  ὁ λόγος ἦν πρὸς τὸν θεόν → "道與上帝同在": ἦν and πρὸς both primary, sharing 同在
- Light-verb / resultative-directional compound — head morpheme primary, result/direction morpheme secondary to the same Greek verb, unless the compound is itself a lexicalized idiom (e.g. a naming formula — see IDIOMS).
  σώσει → "救出來": 救 primary; 出來 secondary
- Classifier (個/位/隻/座/etc.) — secondary to the counted noun, sharing its record; required by Mandarin's obligatory numeral+classifier+noun grammar, no independent Greek word.
  υἱόν → "一個兒子": 個 secondary to υἱόν
  ἡγούμενος → "一位君王": 位 secondary (a person-classifier, selected for a person of status — the choice of classifier carries no independent translatable content)
- Pro-drop / topic continuity — subject pronoun supplied on a new/switched subject → secondary; dropped on a coordinate clause continuing the same topic → none expected, leave unrecorded. Absence of an explicit pronoun is the ordinary default, not a gap to fill.
- Locative postposition (裏/上/中/內) — Mandarin places location words after the noun (postpositional), unlike Greek's prepositions. Preposition + locative word both realize the same Greek preposition (a discontinuous target span). Each locative has its own dominant sense, not interchangeable: 裏 = general containment (ἐν/εἰς/ἐκ); 上 = surface contact (ἐπί/ἐν); 中 = "amid/among" (ἐν/ἐκ; also the fixed dream/vision idiom 夢中 for κατ᾽ ὄναρ); 內 = rare synonym of 裏.
  ἀπὸ τῶν ἁμαρτιῶν αὐτῶν → "從罪惡裏": 從 primary to ἀπό; 裏 secondary to ἀπό as well

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — always secondary to head when no distinct Chinese correspondent (the large-majority case). See ARTICLES → Branch B.
的, 所, aspect particles (了/着/過), and 將/把 are never NEQ even when they have no Greek trigger of their own — secondary to the source token whose grammar/discourse context requires them, since that token is itself the source anchor.
A parenthetical cross-reference → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment — Chinese is SVO but with extensive preposing (topic-comment, the BA-construction) not mirrored in Greek's own word order.

## ARTICLES

Chinese has no article system at all. For every Greek article (POS T-*): does the translation supply a distinct correspondent (a demonstrative)?
DEFAULT → Branch B: no separate word at all — the large majority case. The noun stands bare, article secondary to the noun's own record, no target word required.
MINORITY → Branch A: 這/那 (demonstrative/anaphoric reference) — real, but the exact choice is a translator decision, not a mechanical rule (different Chinese Bible translations sometimes diverge on the very same Greek article — one supplies a demonstrative, another doesn't). Primary 1:1; noun in its own record.

### Branch A — article has a distinct correspondent
  ὁ (anaphoric/demonstrative) → "這"/"那": primary 1:1
  οἱ ἀπὸ Ἱεροσολύμων καταβεβηκότες Ἰουδαῖοι → "那些從耶路撒冷下來的猶太人": 那些 primary 1:1

### Branch B — no distinct correspondent → secondary, no target word (the default)
  ὁ θεὸς → "上帝": 上帝 primary alone, ὁ secondary with no target word
  Article before a proper name: ὁ Ἰησοῦς → "耶穌": same pattern, secondary, absorbed

### Substantive participle (article + participle)
See PARTICIPIAL CONSTRUCTIONS — the article's nominalizing role is absorbed into 的 (or 所...的), not rendered as a separate demonstrative.

### Anarthrous noun
No Greek article, and no Chinese indefinite article by default — bare noun, no secondary needed unless a classifier phrase (一個/一位/etc.) is explicitly supplied for emphasis/specificity (see Classifier, above).

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — prefer the light-verb/resultative-compound or classifier treatment (TOKEN ROLES) over idiom marking whenever the construction is a recognized instance of one of those patterns rather than a genuinely non-compositional phrase. A lexicalized naming formula ("起名叫" for "call [X's] name") is a plausible idiom candidate when the two halves cannot be cleanly split against τὸ ὄνομα and καλέσεις separately. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

Do not assume any particular marking strategy for a Greek passive verb. An UNMARKED verb — no passive morphology of any kind — is the majority strategy, not 被. 被 does occur but is not a safe default assumption. 受/得/蒙 "receive/undergo NOUN" and the more literary 為...所/所...的 construction are both real minority strategies. Which (if any) marker appears is not predictable from Greek voice morphology alone — check the actual target text.

### Unmarked — the majority default
The target verb carries no passive morphology at all; many Mandarin verbs are ambitransitive/inchoative (usable both agentively and as "undergo X" with no formal change), or the whole clause is restructured as active voice with a real or generic agent supplied. Primary alone to the Greek passive verb.
  γεγέννημαι (I have been born) → "我生來就是": primary alone
  ἀπεκτάνθησαν (were killed) → "因地震而死的" (recast as an intransitive death-event, "died because of the earthquake"): primary alone
  κηρυχθῆναι (is to be proclaimed) → "人要...傳...道" (recast fully active, "people will proclaim..."): primary alone
  δεδωρημένης (having been given) → "已將...賜給我們" (recast fully active with the agent as subject, using the BA-construction to front the gift): primary alone

### 為...所 / 所...的 — a literary passive-marking construction, distinct from 被
Frames the verb with 所 (and often 為ᴀɢᴇɴᴛ before it), nominalizing the passive event. Secondary to the passive verb, framing it rather than replacing it as primary.
  ἀγνοούμενοι (unknown) → "不為人所知" ("not known by people"): 知 primary; 為, 人 (agent), 所 secondary
  ἐπιγινωσκόμενοι (well known) → "人所共知的" ("commonly known by people"): 知 primary; 所, 的 secondary

### 受/得/蒙 receive-construction — a real minority strategy
The patient (grammatical subject of the Chinese clause) surfaces as the subject of 受/得/蒙 ("receive"); the deep-structure agent surfaces as a possessor inside the nominalized object, not as a separate agent phrase. 受/得/蒙 primary to the passive verb; the possessor noun/pronoun primary to the ὑπό-agent phrase's object.
  ἐβαπτίσθη ὑπὸ Ἰωάννου (was baptized by John) → "受了約翰的洗": 受 primary to ἐβαπτίσθη; 了 secondary; 約翰 primary to Ἰωάννου
  παιδευόμενοι (disciplined) → "受責罰": 受 primary

### 被-marked passive — real but not the default; do not assume it
被 secondary to the passive verb (the verb itself, not 被, carries the primary lexical link). Confirmed present in the language but was not the strategy chosen for any of a 25-verse spot-check of passive-stem Greek verbs in CUV's own text — treat it as a real option, not a fallback.
  λεγόμενοι (so-called) → "被稱為神明的" (an independent Chinese translation's choice for this verse; CUV instead used the unmarked "稱為神的" for the same Greek): 被 secondary when present

### Reflexive/self-directed active conversion
A further restructuring strategy: the Greek passive verb is recast as an active verb with a reflexive object, rather than any of the above.
  φθείρονται (are destroyed/corrupted) → "敗壞了自己" ("ruin themselves"): 敗壞 primary; 自己 primary to the implied agent-patient identity, 了 secondary\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Substantive — 的-nominalizer, the confirmed default
的 nominalizes a verbal phrase into "the one(s) who...", parallel to Indonesian's "yang" or French/Spanish "qui/que". Always secondary to the participle it nominalizes — never NEQ, never treated as a free-floating possessive.
  πᾶς ὁ πιστεύων εἰς αὐτὸν → "一切信他的": 信 primary to πιστεύων; 的 secondary to πιστεύων; 他 primary to αὐτόν; 一切 primary to πᾶς
  A chain of substantive participles (ὁ παρακαλῶν... ὁ μεταδιδοὺς... ὁ προϊστάμενος... ὁ ἐλεῶν) → "勸化的...施捨的...治理的...憐憫人的": each verb gets its own bare 的-nominalized record, no separate pronoun or head noun needed for any of them
The article's nominalizing role is absorbed into 的 here — do not additionally expect a separate demonstrative (contrast the plain ARTICLES Branch A/B split, which governs an article NOT attached to a substantive participle). See also the related 所...的 strategy under PASSIVE VOICE, for patient-oriented substantive participles.

### Adverbial and genitive absolute
Not separately researched for Chinese — apply the general TOKEN ROLES guidance (a supplied conjunction/adverb introducing the participle's circumstantial force is secondary to the participle; a supplied subject pronoun follows the pro-drop guidance above).

### Discourse particle adjacent to a participle
δέ/καί/οὖν near a participle with no correspondent → NEQ source, only when certain no element in the surrounding clause carries its force.\
"""

AUTOS_BLOCK = """\
## αὐτός / REFLEXIVE 自己

Two distinct categories — both align 自己 as primary either way; the distinction is about why 自己 was chosen, not the primary/secondary call. The genuine-substitution category is confirmed genuinely narrow (in a spot-check of random αὐτός instances, only a small minority triggered it) — do not treat 自己 as a general pronoun-rendering default; it is conditioned specifically on the referent circling back to the clause's own subject.

### Direct correspondence — ordinary translation, not a special case
Greek itself already uses a reflexive/self-referential word: ἑαυτοῦ/σεαυτοῦ/ἐμαυτοῦ (reflexive pronouns) or ἴδιος ("one's own"). Plain primary translation.
  μὴ εἴπητε ἐν ἑαυτοῖς → "不要自己心裏說": 自己 primary to ἑαυτοῖς

### Genuine substitution — a real, narrowly-conditioned coreference-driven translation choice
Greek uses a plain personal pronoun (αὐτός/σύ/ἐγώ), but Chinese substitutes the reflexive 自己 specifically because the referent is coreferential with the clause subject. Still primary to that plain pronoun. This condition must actually hold — most plain third-person pronouns in a verse do NOT refer back to the clause's own subject, and get ordinary pronoun treatment instead (see below).
  σώσει τὸν λαὸν αὐτοῦ (subject = Jesus, αὐτοῦ = his own people) → "將自己的百姓...救": 自己 primary to αὐτοῦ; 的 secondary (see 的 in TOKEN ROLES)
  οἱ οἰκιακοὶ αὐτοῦ (his household members) → "自己家裏的人": 自己 primary to αὐτοῦ
  καθὼς ἠθέλησεν (an implicit-subject "as [God] willed") → "隨自己的意思" (自己 reinforces the implicit subject-coreference, even with no separate Greek pronoun token present): 自己 secondary, anchored to the verb's own subject

### Ordinary (non-reflexive) third-person uses of αὐτός — the majority case
Follow standard pronoun translation (他/她/它/他們/牠 etc.) — no special treatment. This is what most αὐτός instances get.
  Translation substitutes proper name: name primary; additionally supplied subject pronoun secondary.

### No correspondent
→ NEQ source (only when certain).\
"""

VERBAL_ASPECT_BLOCK = """\
## VERBAL ASPECT (了/着/過)

Mandarin marks aspect with post-verbal particles, not inflection. Secondary to the Greek verb whose aspect they reflect — grammar-required, not NEQ candidates.

- 了 (perfective/completed action) — the default for telic/punctual completed events.
  γέγονεν (has taken place) → "成就了": 了 secondary
  τετήρηκαν (have kept) → "遵守了": 了 secondary
- 過 (experiential, "have ever...") — for anterior/experiential-reference perfects, recalling that a past event occurred rather than marking its completed result. NOT obligatory even on a negated perfect — check the specific verb rather than assuming.
  μεμαρτύρηκεν (has testified) → "作過見證": 過 secondary
  προείρηκεν (said before/predicted) → "先前說過": 過 secondary
  Counter-example: ἀκηκόατε/ἑωράκατε negated ("you have never heard/seen") → "從來沒有聽見...也沒有看見" — no 過 at all, despite the same negated-perfect shape that other verses do take 過 on.
- No particle at all — stative verbs are the systematic exception. The "know" family (οἶδα/οἴδαμεν/οἴδατε) consistently renders as bare 知道 with no 了/過, every time — an ongoing state of knowledge does not take an aspect particle the way telic/punctual events do.
- 著/着 (durative, "in the process of/while") — secondary to an imperfective/ongoing Greek form (present participle, imperfect). CUV uses the variant character 着, not 著.
  βοῶντος → "喊着說": 着 secondary
  γέγραπται → "記着說" (fixed citation formula, "as it is written"): 着 secondary
- Stacking — more than one aspect particle (and/or 被) can attach to a single Greek perfect-passive form; all secondary to the same source token, not grounds for separate records.\
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

ZHT_CONFIG = LanguagePromptConfig(
    language_code="zht",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(ZHT_CONFIG)
