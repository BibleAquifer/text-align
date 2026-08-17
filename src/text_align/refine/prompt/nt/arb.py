"""Arabic (Van Dyck) target-language prompt config for refine-alignment.

Distilled from `docs/alignment-principles-nt.arb.md`. Examples grounded in the
Arabic Van Dyck Bible (AVD) target TSV, cross-checked against a second Arabic
NT translation (ONAV) for the same verses to separate general Arabic grammar
from AVD's own register/style. The base fused-clitic/idafa/article material
comes from a 4-verse initial pass (Matthew 1:1-2, Mark 1:9, John 4:2);
PASSIVE, NEGATION, PARTICIPLE, COMPARATIVE, CONDITIONAL, AUTOS, and HOTI were
each additionally checked against a stratified ~17-30 verse sample spanning
the whole NT. See the principles doc's "Cross-translation methodology note"
and "Open questions" sections for what remains unconfirmed.

**Draft status:** this config has not yet been reviewed by a native Arabic
speaker or Arabist. Do not use for production alignment runs until that
review happens.

Key differences from every other currently-supported language:
  BASE_BLOCK  — AVD's target TSV tokenizes on whitespace only, and Arabic
                orthography fuses conjunctions (wa-/fa-), prepositions
                (bi-/li-/ka-), the definite article (al-), and pronominal
                suffixes onto the following/preceding word with no space.
                One target token routinely corresponds to 2-4 Greek tokens
                (conjunction + article + noun + suffix all fused). The
                fused element's Greek trigger is pulled in as an additional
                PRIMARY source token in the noun/verb's record — there is no
                target-side secondary marking possible, since the fusion
                can't be split at the token level. Construct-state (idafa)
                genitive chains (noun-noun, no preposition/clitic at all)
                need no secondary "of" token on either side, unlike the
                English case-driven "of" pattern. The definite article
                al-, though always fused, is treated as a real definite
                article (primary alongside the noun) rather than a merely
                grammatically-supplied filler the way English "the" is
                treated when unmarked — this is flagged as an open question
                in the principles doc and may need to change after native-
                speaker review. Bare transliterated proper names and
                possessive-suffixed nouns never take al- at all, so a Greek
                article in either of those positions is NEQ, not primary
                (a divergence from every Latin-script config, which treats
                article-before-proper-name as a primary-link exception). An
                attributive adjective modifying a possessive-suffixed noun
                STILL takes its own al- (ordinary definiteness concord) —
                this does not extend the noun's own NEQ-article rule to the
                adjective.
  PASSIVE_BLOCK — REVISED after a 26-verse sample. The original single-verse
                claim ("Arabic avoids true passive") does not hold: true
                morphological passive (finite fuʿila/yufʿalu forms and true
                passive participles) is the single most common strategy
                overall. Six strategies coexist and must be identified per
                verse: true passive (most common), a dedicated intransitive/
                unaccusative verb with no voice marking at all (very
                consistent, e.g. tamma for "be fulfilled"), an active-form
                derived-stem verb (Form V/VII/VIII) — real but narrower than
                first thought, clustering around the subject's own physical/
                experiential change of state (baptize, recline, be taken
                up) — active-voice conversion (agent promoted to subject;
                confirmed almost exclusively in ONAV, not AVD, a likely
                register difference worth expecting), an adjectival/stative
                predicate, and nominalization (verbal-noun phrase, legal/
                register-heavy passages). Explicit agent (hupo/dia + case)
                converts to a real preposition or idiom (min, ala yad,
                bi-, ladaa, bi-lisani) — align the Greek preposition primary
                to whichever the translation used; never expect a literal
                "by." Voice conversion is bidirectional — a Greek active can
                render as an Arabic passive too.
  NEGATION_BLOCK — REVISED after a 24-verse sample. Particle choice remains
                tense/aspect-conditioned but lam turned out broader than
                "simple past": it covers any negated event Greek presents as
                a completed/perfective whole (aorist AND perfect, not just
                aorist), and lam yakun covers both "was not doing X" (verb)
                and "was not X" (predicate noun/adjective) as one
                construction. la covers present/gnomic negation and ALL
                prohibitions uniformly, regardless of whether the Greek
                prohibition is a present imperative or aorist subjunctive —
                a distinction Arabic does not grammaticalize. Nominal/
                existential negation splits between laa-al-nafiya-lil-jins
                (categorical "there is no X," no copula token at all) and
                laysa (a real verb-like negator) — genuinely translator-
                variable, no confirmed conditioning factor yet. Emphatic
                negation (ou me) has NO single dedicated construction — la
                and lan are both attested for the identical Greek pattern,
                sometimes differing between AVD and ONAV on the same verse;
                an optional intensifier (abadan/qattu) is a stylistic
                choice (common in ONAV, rare in AVD), not grammatically
                required. Compound list negation (oude) just repeats la
                with the ordinary wa- conjunction, no dedicated lexeme.
                oudeis has no dedicated Arabic negative pronoun — it
                becomes a plain indefinite noun (ahad) with negation
                carried entirely by the verb's own particle.
  PARTICIPLE_BLOCK — NEW (was previously an unchanged eng.py import; now has
                its own dedicated block after a 25-verse sample). Substantive
                participles split three ways by referent type, closer to
                Indonesian's yang/barangsiapa split than Hindi's single-
                default jo: a genuine Arabic participle (ism al-faʿil/ism
                al-mafʿul) for attributive modification of an already-
                identified noun or elevated/hymnic register; al-ladhi +
                finite verb for a specific/deictic referent; man + finite
                verb as the dominant strategy for generic "whoever…"
                formulaic refrains (the single best-attested pattern in the
                sample, holding even where a natural participle exists and
                goes unused). Circumstantial participles default to a
                finite subordinate clause (lamma/hina + verb) for ordinary
                narrative aorist participles, NOT Arabic's own hal-participle
                construction — except in elevated/hymnic passages. A second
                common strategy collapses a participle+main-verb pair into
                two coordinate finite verbs (wa-/thumma) with no
                subordinating conjunction at all. legon ("saying") has an
                extremely stable formulaic rendering (qa'ilan, a genuine
                hal-participle) independent of either strategy. Genitive
                absolutes need no separate treatment — same lamma/fima
                pattern, tracking Greek's aorist/present aspect via which
                temporal conjunction is chosen (lamma = punctual, fima/
                baynama = durative); an explicit genitive subject gets an
                explicit Arabic pronoun, primary, when present.
  COMPARATIVE_BLOCK — NEW (was an eng.py import). Arabic's single af'al
                elative form (comparative and superlative are
                morphologically identical) disambiguates cleanly via three
                co-occurring markers: bare elative + min = comparative,
                al-+elative = superlative, bare elative alone = implicit/
                absolute comparison. But Greek's own suppletive "first"/
                "last" (protos/eschatos) bypass the elative pattern
                entirely and map to dedicated ordinal lexemes (awwal/akhir,
                or akhira in some collocations) — a Greek COMPARATIVE tag
                does not reliably predict which Arabic strategy applies;
                check the specific lemma.
  CONDITIONAL_BLOCK — NEW (was an eng.py import). Arabic has (at least) four
                particles, not a simple two-way split: law is dedicated to
                genuine contrary-to-fact conditions (2nd class, confirmed
                3/3); in is the default for BOTH 1st- and 3rd-class Greek
                conditions alike (Arabic collapses that Greek distinction —
                the real split is open vs. counterfactual, not a 3-way
                match to Greek's three classes); idha appears for ean when
                the condition is framed as likely/expected rather than
                genuinely open; mahma and similar free-choice relatives
                handle eis-with-indefinite-pronoun ("whatever/whoever")
                constructions. ei me functioning as "except/only" is NOT a
                conditional at all — it is a fixed exceptive idiom
                rendering uniformly as illa and needs its own rule, high-
                frequency enough to matter. ei as an indirect-question
                marker (a Koine Hebraism) renders as hal, also not
                conditional. The fa- apodosis marker has no Greek trigger
                and stays unrepresented (parallel to the "supplied then"
                NEQ pattern); a distinct la- proclitic marks a
                counterfactual apodosis and IS primary to Greek an, though
                negated counterfactual apodoses do not reliably carry an
                an-equivalent.

  AUTOS_BLOCK — NEW (was an eng.py import), after a 17-verse sample. Ordinary
                pronominal autos (genitive/accusative) has essentially no
                independent target token — it is absorbed as a possessive/
                object suffix fused directly onto the noun or verb, exactly
                per BASE_BLOCK's fused-pronominal-suffix rule; this needed
                stating explicitly since it is the majority case by far.
                Dative pronouns sometimes fuse onto a separate small
                preposition-carrier token (lahu/ilayhi) rather than the main
                verb — a sub-pattern not covered by the general fused-suffix
                rule as originally stated. Intensive "himself" is highly
                consistent: nafs ("self") + possessive suffix, agreeing in
                gender/case, confirmed 5x. "Same" turned out to have THREE
                distinct strategies depending on construction type (identity-
                of-source -> wahida "one"; adverbial "likewise" -> ayn+suffix
                or dropped/NEQ; predicate "is the same" -> a fixed huwa huwa
                pronoun-doubling idiom) rather than one strategy. Emphatic/
                contrastive subject use is the weakest finding: sometimes an
                independent huwa, sometimes zero token, a tentative
                contrastive-vs-topic-continuity split from only 5 instances.
  HOTI_BLOCK — NEW (was an eng.py import), after a 24-verse sample. Causal
                and content-clause hoti get genuinely different Arabic
                renderings (li-anna vs anna/inna), confirming they do not
                collapse — but content-clause "that" itself splits further
                by matrix-verb type, not previously documented: anna after
                cognition/belief/hope verbs (know, believe, hope) but inna
                specifically after verbs of saying, confirmed cleanly in
                minimal pairs within single verses. Recitative hoti is NOT
                uniformly NEQ/punctuation-only as the original single-
                pattern assumption held — Arabic sometimes inserts that same
                inna (or an alternative like haqqan "truly") at the direct-
                quote boundary, and its presence tracks the Greek hoti
                (confirmed by a negative-control asyndetic-quote instance
                with no hoti and no inna inserted) — so it should align
                primary to hoti rather than defaulting to NEQ when present.

  IMPERSONAL_BLOCK — NEW (was an eng.py import), after a 22-verse sample.
                Arabic impersonal verbs are bare 3rd-masculine-singular
                finite forms (or zero-copula adjectival predicates) with NO
                subject pronoun at all, ever — not even an explicit huwa
                ("it"). The English "dummy it -> NEQ" rule does not carry
                over: NEQ asserts a word was untranslated, but there is no
                token slot for "it" in Arabic to begin with, so it should
                simply be left unrecorded. dei -> yanbaghi (AVD default) /
                labudda (ONAV default); exestin -> yahillu (dominant,
                religious-law contexts) with yajuzu attested once for a
                civil/political context; sumpherei splits between a bare
                zero-copula adjectival predicate (khayrun "better") and a
                genuine finite verb (yanfaʿu), free variants. The
                complementary clause after any impersonal verb has three
                strategies: an + subjunctive (bare infinitive-substitute,
                default), anna + full clause (when the embedded clause has
                its own overt subject), or a bare verbal noun/masdar with no
                connector at all. Side-finding: some IMPERSONAL-tagged dokei
                instances are actually the unrelated personal "thinks
                himself" construction, not true impersonal dokeo — the
                phenomenon detector doesn't distinguish these.
  INFINITIVE_BLOCK — NEW (was an eng.py import), after a 22-verse sample.
                Classical Arabic has NO true infinitive form, so the
                strategy depends entirely on which of (at least) five Greek
                infinitive uses is in play — eng.py's single "'to' secondary
                to the infinitive" rule does not transfer. Complementary
                infinitive (after thelo/dunamai-type verbs) -> an (an, a
                real standalone token, not fused) + subjunctive, both
                primary — the cleanest, most consistent pattern. Purpose
                infinitive fragments into at least four coexisting
                strategies (bare li- fused proclitic, heavier likay,
                coordinated series sharing one marker via plain wa-, or
                purposive verb-serialization with no marker at all) —
                confirmed real variation. Subject/predicate articular
                infinitives nominalize into plain abstract nouns; temporal
                articular infinitives (meta to) instead become finite
                subordinate clauses, same lamma/fima pattern as
                circumstantial participles. Accusative+infinitive indirect
                discourse collapses onto the SAME anna/inna complementizer
                system as hoti content clauses (cross-reference HOTI_BLOCK)
                — but sometimes converts fully to a bare direct quotation
                with no complementizer at all, a genuine AVD/ONAV divergence
                point.
  HINA_BLOCK — NEW (was an eng.py import), after a 24-verse sample. Two
                genuinely distinct systems, not one: when hina functions as
                the direct-object/content clause of a matrix verb of
                wanting/urging/commanding (thelo, parakalo, or a command-
                sense eipon) — i.e. substituting for what would otherwise be
                an infinitive complement — Arabic uses bare an + subjunctive,
                NO purpose marker at all, confirmed by a clean minimal pair
                (Gal 4:17 vs. 1 Thess 4:13, same matrix-verb family, opposite
                syntactic role, opposite Arabic strategy). Genuine adverbial
                purpose hina uses a family of free-variant particles — li-
                (fused), likay (full), kay (bare) — confirmed genuinely
                interchangeable by a single verse (John 1:7) using two
                different ones for two structurally identical purpose
                clauses. hatta is a real fourth alternative leaning toward
                result/consecutive sense, but not strictly reserved for it.
                Negative purpose (hina me, "lest") has (at least) four to
                five live realizations (likay la, li'alla fused, kay la,
                hatta la, or a zero-marker outcome) — this REVISES an
                earlier single-verse-based claim that AVD and ONAV split
                predictably here; they don't, both use multiple variants.
  VERBAL_ASPECT_BLOCK — NEW (was an eng.py import), after a 20-verse sample.
                Arabic marks iterative/conative/ingressive nuances
                EXPLICITLY LESS OFTEN than Greek/English do — a plain
                perfective verb with the nuance left unmarked/implicit was
                the majority outcome (~60%), not the exception, a real
                departure from the general principle's implicit assumption.
                Iterative/habitual gets explicit kana+imperfect periphrasis
                when repetition is genuine, but collapses to plain
                perfective when negated or when the imperfect denotes a
                single/distributive event. Ingressive has at least four live
                auxiliaries (sara/qama/jaʿala/badaʾa) + imperfect, but a
                plain unmarked perfective was actually MORE common in this
                sample. Most notably: the project's own canonical conative
                example (Mark 15:23) gets NO conative marking in either
                Arabic translation — "tried to" is left entirely implicit
                unless the Greek verb's own lexeme literally means "try"
                (peirazo/epicheireo), in which case it's ordinary lexical
                translation (hawala + an + subjunctive), not a special
                aspect construction.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_nt_language
from .eng import (
    BLOCK_ORDER,
    FORCED_INCLUSIONS,
)


# ---------------------------------------------------------------------------
# Arabic-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT). The target translation is Arabic (Van Dyck).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include grammar-required fused proclitics (conjunction, preposition, article) and pronominal suffixes when a real Greek trigger exists. Do not restrict to strict lexical equivalents.
The target text tokenizes on WHITESPACE ONLY. Arabic orthography fuses conjunctions (وَ wa- "and", فَ fa- "so/then"), prepositions (بِ bi- "with/by", لِ li- "to/for", كَ ka- "like/as"), the definite article (ٱلْ al-), and pronominal suffixes (possessive on nouns, object on verbs) onto the adjacent word with NO space and NO separate token — in any combination. One target token routinely corresponds to 2-4 Greek tokens. This makes N:1 records (multiple Greek source tokens → one fused Arabic target token) the DOMINANT pattern for Arabic, not an occasional case.
When a fused element has a real Greek trigger (a conjunction, preposition, article, or pronoun token in the source), include that Greek token as an additional PRIMARY source token in the record for the Arabic token it is fused into. Do not try to mark part of a fused target token secondary — there is nothing to split at the token level; the primary/secondary distinction for these constructions lives on the source side.
Prefer one record per source token where the script allows a genuine split (Arabic is not glued to Greek word-for-word); combine into N:1 records when fusion forces it, or when tokens form an inseparable semantic unit (idiom).

## TOKEN ROLES

primary — direct lexical or semantic connection to the Greek token
secondary — exists only because of grammatical features in the Greek token's morphology (person, number, case, aspect, voice), or because Arabic's own grammar obligatorily requires a word/morpheme with no separate Greek word behind it
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse (a fused Arabic token used once, even when it corresponds to several Greek tokens).

Common cases:

- Fused conjunction (وَ wa-, occasionally فَ fa-) — when a Greek καί/δέ motivates it, include that Greek token as an additional PRIMARY source alongside the noun/verb.
  δέ + Ἰσαάκ → "وَإِسْحاقُ" (wa-Isḥāqu): source=[δέ, Ἰσαάκ], target=["وَإِسْحاقُ"] — both primary, one target token
  When wa- has no identifiable Greek trigger (ordinary clause-initial linking style with no καί/δέ present) — do not add an extra source token for it; it simply rides along with the noun/verb it's fused to.

- Fused article (ٱلْ/الْ al-) — a real definite article, closely paralleling Greek's, always bound. When a Greek article motivates it, include the article's Greek token as an additional PRIMARY source (not secondary the way English "the" is when absorbed — al- carries genuine definite-article meaning, just fused rather than free-standing).
  τόν + Ἰακώβ → "يَعْقُوبَ" WITHOUT al- (bare proper name; see below): τόν → NEQ, not primary
  ὁ Χριστός-type title → "ٱلْمَسِيحِ"/"الْمَسِيحِ" (al-Masih): noun primary; if Greek has no article here, this is a lexicalized/conventional al- with no extra Greek token to add — an ordinary 1:1 primary noun record
  An attributive adjective modifying a possessive-suffixed noun STILL takes its own al- (ordinary Arabic definiteness concord — the adjective agrees with the noun's definiteness independently of the noun's own inability to take al-): إِيمَانِكُمُ ٱلْأَقْدَسِ ("your most-holy faith") — ٱلْأَقْدَسِ keeps its article even though إِيمَانِكُمُ (possessive-suffixed) cannot. Do not read the possessive-noun NEQ-article rule as extending to its modifying adjective.

- Fused preposition (بِ/لِ/كَ/مِنْ etc.) — when a Greek preposition motivates it, include it as an additional PRIMARY source, same pattern as the conjunction case.

- Fused pronominal suffix (possessive on nouns, object on verbs: ـهُ -hu "his/him", ـهَا -ha "her", ـهُمْ -hum "their/them", ـنَا -na "our/us") — carries genuine pronominal meaning; include the corresponding Greek pronoun/pronominal-ending token as primary, same as any pronoun correspondence, just packaged inside the fused token.
  καί + τούς + ἀδελφούς + αὐτοῦ → "وَإِخْوَتَهُ" (wa-ikhwatahu, "and his brothers"): source=[καί, ἀδελφούς, αὐτοῦ], target=["وَإِخْوَتَهُ"] — all three primary; τούς → NEQ (a possessive-suffixed noun cannot also take al-, see NEQ)

- No indefinite article — bare noun is the default, same as Greek. Never a secondary token for Arabic indefiniteness.

- Construct-state (idafa) genitive chains — a sequence of nouns (noun1 possessed, no article even if definite, immediately followed by noun2 possessor) marks a genitive/possessive relationship through word order and morphology alone. NO preposition, NO clitic, NOTHING written for "of." When Greek's case-driven genitive is rendered this way, each noun aligns 1:1 primary to its Greek counterpart with NO secondary "of" token added anywhere — unlike English, there is no token to mark secondary.
  Βίβλος γενέσεως Ἰησοῦ χριστοῦ → "كِتَابُ مِيلَادِ يَسُوعَ ٱلْمَسِيحِ" (kitabu miladi Yasuʿa al-Masih, "book of [the] genealogy of Jesus Christ"):
    source=[Βίβλος], target=["كِتَابُ"] — primary 1:1, no secondary needed
    source=[γενέσεως], target=["مِيلَادِ"] — primary 1:1, no secondary needed
    source=[Ἰησοῦ], target=["يَسُوعَ"] — primary 1:1
    source=[χριστοῦ], target=["ٱلْمَسِيحِ"] — primary 1:1 (article fused, lexicalized title, no extra Greek token to add)
  When Arabic instead uses an explicit preposition (مِنْ min, لِ- li-) for a genitive relationship, treat it as an ordinary case-driven secondary/primary preposition token — there IS a real token to align in that case.
  A superlative can also be the construct-first term of an idafa chain (ἐλάχιστον-type "least of the matters" → أَصْغَرِ ٱلأُمُورِ) — same no-secondary-token rule; a translator-supplied generic completion noun with no Greek anchor (e.g. "the matters" when Greek's elative was used absolutely) is NEQ target, not secondary.

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek article before a BARE TRANSLITERATED PROPER NAME (τὸν Ἰσαάκ, τὸν Ἰακώβ) → NEQ. Arabic never attaches al- to a bare proper name — there is no candidate token to absorb it into, breaking from the article-before-proper-name-is-primary pattern used for English/Portuguese/Spanish/French.
Greek article on a noun that is ALSO POSSESSIVE-SUFFIXED in Arabic (a possessed noun is inherently definite and cannot take al-) → NEQ. Treat this as a general rule once confirmed against more examples, not re-derived case by case. (Its modifying adjective, if any, is unaffected — see BASE_BLOCK's definiteness-concord note.)
Fused conjunctions, articles, prepositions, and pronominal suffixes WITH a real Greek trigger are primary companions in the noun/verb's record (see ALIGNMENT PHILOSOPHY / TOKEN ROLES above) — NOT NEQ, even though they have no independent target token of their own.
Supplied copula with no Greek εἶναι token → NEQ target.
A translator-supplied noun completing an absolute/elliptical elative (see COMPARATIVE) → NEQ target.
Apodosis فَ- (fa-, "so/then") with no explicit Greek apodosis particle (τότε/ἄρα/οὖν) → simply unrepresented, not NEQ (it is a fused proclitic, not an independent token — same as any other untriggered fused conjunction).

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form. This explicitly includes Arabic dual number (no NT-era Greek dual exists) aligning to Greek plural with no special marking, and Arabic active-form derived-stem/intransitive verbs aligning to Greek passive-voice verbs (see PASSIVE VOICE). Note ONAV sometimes normalizes to Arabic's own natural-pairing default (dual for body parts) even against a Greek singular, while AVD tends to track Greek number literally — both are legitimate; align on lexical correspondence regardless of which translation's number choice you're looking at.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Arabic is VSO/SVO with rich verb agreement; word order divergence from Greek is real but generally milder than Hindi's SOV divergence. Token order in the TSV follows document (reading) order regardless of the right-to-left script.

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary.
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.
- Most conjunctions in Arabic are fused proclitics (وَ/فَ) — apply the fused-conjunction rule above rather than expecting a free-standing token.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — prefer the fused-token N:1 treatment above (which is normal and expected for Arabic, not a special case) over idiom marking whenever the construction is ordinary clitic fusion or an idafa chain rather than a genuinely non-compositional phrase. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

Six strategies coexist; identify which one a given verse uses rather than assuming — confirmed against a 26-verse sample spanning every major NT genre and Greek passive tense/mood.

### 1. True passive — finite internal-vowel passive (faʿala → fuʿila/yufʿalu) and true passive participle (mafʿūl/mufʿal pattern) — the single most common strategy overall
Same underlying morphological mechanism (participle vs. finite form of the same passive stem); treat as one family. Participle often takes a copula for a periphrastic "is/was X-ed" reading — copula secondary, participle primary, same pattern as English/Hindi.
  ἐγεννήθη → "وُلِدَ" (wulida, "was born"): primary 1:1
  γέγραπται → "مَكْتُوبٌ" (maktūbun, bare passive participle, zero-copula predicate — Arabic's own present copula is itself zero) or "هُوَ مَكْتُوبٌ" (with copula): primary "مَكْتُوبٌ"; secondary "هُوَ" when present
  τὸ ῥηθέν → "مَا قِيلَ" (mā qīla): "قِيلَ" primary (true internal-vowel passive of قال "to say"); "مَا" primary (substantivizing relativizer, corresponds to τό)
  λεγομένην/καλούμενος-type naming participle → "يُقَالُ لَهَا"/"تُسَمَّى" ("it-is-said-to-her"/"is-named" naming formula): primary — a stable Arabic equivalent for Greek naming participles

### 2. Dedicated intransitive/unaccusative verb — no voice marking at all, the verb's own lexical meaning is inherently intransitive
Very common and highly consistent (both translations converge on the identical verb, especially for πληρόω-passive "be fulfilled" → تَمَّ/يَتِمُّ). Primary alone — no periphrasis, no secondary tokens.
  πληρωθῇ → "يَتِمَّ" (from تَمَّ tamma, "to become complete"): primary alone
  σωθήσεται → "يَخْلُصُ" (from خَلَصَ khalaṣa, "to become free/saved"): primary alone
  ἐξηράνθη → "يَجِفُّ" (from جَفَّ jaffa, "to become dry"): primary alone

### 3. Active-form derived-stem verb (Form V/VII/VIII) with reflexive/middle/resultative semantics — real but narrower than a general passive strategy; clusters around verbs of the SUBJECT'S OWN physical/experiential change of state
Confirmed reliably for: βαπτίζω (baptize) specifically, and more broadly for deponent/middle-passive verbs of motion or bodily change (recline, cling/join, be taken up, be filled). For ordinary transitive passives (was caught, was written, was sent, was rejected), expect strategy 1 or 5 instead — do not present this as "the" default Arabic passive strategy.
  ἐβαπτίσθη → "ٱعْتَمَدَ" (iʿtamada, Form VIII) or "تَعَمَّدَ" (taʿammada, Form V): primary 1:1 despite being morphologically active
  ἀνελήμφθη → "ٱرْتَفَعَ" (irtafaʿa, Form VIII, "was taken up"): primary 1:1
  πληρωθῆτε → "تَمْتَلِئُوا" (tamtaliʾū, Form VIII, "may be filled"): primary — confirms this strategy isn't limited to motion verbs

### 4. Adjectival/stative predicate (negator + pronoun + active/agentive participle used predicatively) — narrow, single confirmed instance
  ὑποτάσσεται negated → "لَيْسَ هُوَ خَاضِعًا" (laysa huwa khāḍiʿan, "it is not submissive"): primary "خَاضِعًا"; secondary "لَيْسَ", "هُوَ" (negated copula construction). Low confidence — may be a participial variant of strategy 2 rather than a distinct strategy.

### 5. Active-voice conversion (agent promoted to subject) — a real translation-register tendency, confirmed almost exclusively in ONAV, not AVD
When an explicit agent phrase (ὑπό/παρά + genitive) is available, AVD consistently keeps a true-passive-plus-agent-preposition construction while ONAV converts to active. Expect AVD specifically to preserve Greek passive voice more reliably than a more dynamic translation would — when aligning AVD, active-conversion is the less likely outcome, not a coin-flip alternative.
  ῥηθὲν ὑπὸ κυρίου → AVD keeps "قِيلَ...مِنَ ٱلرَّبِّ" (true passive + min-agent); ONAV converts: "قَالَهُ ٱلرَّبُّ" ("the Lord said it" — full voice flip, agent promoted to subject, primary as an ordinary active-verb record)
Voice conversion is bidirectional — a Greek ACTIVE verb can render as an Arabic true passive too (e.g. John 15:6 συνάγουσιν/βάλλουσιν "they gather/cast" → ONAV تُجْمَعُ/وَتُطْرَحُ, true passives). Do not assume a Greek-active verse guarantees an Arabic-active rendering.

### 6. Nominalization — abstract/legal-register passive infinitives recast as a verbal-noun (maṣdar) phrase with no verb at all
Low confidence, single instance, likely limited to legal-formula/register-heavy passages (e.g. Heb 9:16).
  φέρεσθαι (legal-formula "to be established/proven") → "بَيَانُ مَوْتِ ٱلْمُوصِي" (bayānu mawti al-mūṣī, "a declaration of the death of the testator" — verbal noun + idafa chain, no finite/participial verb at all): the verbal noun aligns primary to the Greek infinitive

### Explicit agent (ὑπό/διά + case)
Never a literal "by" — align the Greek preposition primary to whichever the specific translation uses: مِنْ (min, "from" — AVD's most common choice), عَلَى يَدِ (ala yad, "at the hand of," a fixed idiom), بِ- (bi-, fused proclitic — interacts with the FUSED PROCLITICS rule in BASE_BLOCK exactly like any other fused preposition), لَدَى (ladā, "among/with"), بِلِسَانِ (bi-lisāni, "by the tongue of," another fixed idiom).
  ὑπὸ Ἰωάννου → "مِنْ يُوحَنَّا" (min Yūḥannā) or "عَلَى يَدِ يُوحَنَّا" (ala yad Yūḥannā): ὑπό primary to مِنْ/عَلَى يَدِ; Ἰωάννου primary to يُوحَنَّا\
"""

NEGATION_BLOCK = """\
## NEGATION

Particle choice is tense/aspect-conditioned, confirmed against a 24-verse sample:
- لا (la) — present/gnomic negation, AND all prohibitions (μή + imperative OR aorist subjunctive alike — Arabic does not grammaticalize that Greek mood distinction)
- لم (lam) + jussive — negates any event Greek presents as a completed/perfective whole: aorist AND perfect alike, not narrowly "simple past." لَمْ يَكُنْ ("was not") covers BOTH a negated continuous-past VERB (لم يكن + present-tense main verb) and a negated predicate NOUN/ADJECTIVE (لم يكن + noun) — one construction, two complement types.
- لن (lan) + subjunctive — future negation
- ما (ma) — attested as a real alternative to لم for negating a perfect-type verb (at least in ONAV); relative frequency vs. لم still unconfirmed
- لا النافية للجنس / ليس (laysa) — nominal/existential negation, genuinely translator-variable (see below)

  οὐκ ἐποίησεν (aorist) → "لَمْ يَصْنَعْ": primary 1:1 (لَمْ) + primary (verb)
  μὴ πεπίστευκεν (perfect) → "لَمْ يُؤْمِنْ": same pattern — لم is NOT limited to aorist
  μὴ μεριμνᾶτε (present imperative, prohibition) → "لَا تَهْتَمُّوا": primary 1:1
  μὴ φοβηθῇς (aorist subjunctive, prohibition) → "لَا تَخَفْ": same لا + jussive outcome — mood distinction doesn't change the Arabic particle
  οὐδὲν... ἐγένετο (existential "nothing was made") → "لَمْ يَكُنْ شَيْءٌ" (lam yakun + noun شَيْءٌ, not a verb): لَمْ يَكُنْ primary; شَيْءٌ (the negated predicate noun) primary in its own component

### Nominal/existential negation — لا-absolute vs. ليس, translator-variable
Both are valid, distinct Classical Arabic constructions, but no confirmed conditioning factor separates them — check per verse, do not assume one:
- لا النافية للجنس ("لا of absolute/categorical negation") — لا directly governing a bare (unarticled) noun, no copula token at all: φόβος οὐκ ἔστιν... → "لَا خَوْفَ فِي ٱلْمَحَبَّةِ" (literally "no-fear in-the-love") — ἔστιν has NO target token at all (NEQ, parallel to ordinary copula ellipsis); οὐ + the negated noun's Arabic word covered by the single لا-absolute construction.
- ليس (laysa) — a real verb-like negator taking subject+predicate: οὐκ ἔστιν... ἡ σωτηρία → "وَلَيْسَ بِأَحَدٍ غَيْرِهِ ٱلْخَلَاصُ": οὐ + ἔστιν together align primary to ليس as a single record (parallel to compound-negation-token treatment), since ليس is a real token realizing both the negation and (unlike لا-absolute) the copula's own force.

### Compound list negation (οὐδέ) — repeats لا with the ordinary wa- conjunction, no dedicated lexeme
  οὐ σπείρουσιν οὐδὲ θερίζουσιν οὐδὲ συνάγουσιν → "لَا تَزْرَعُ وَلَا تَحْصُدُ وَلَا تَجْمَعُ": first negator plain لا; each subsequent οὐδέ item primary to its own وَلَا repetition (wa- absorbed as the ordinary fused conjunction per BASE_BLOCK).

### Emphatic negation (οὐ μή) — NO single dedicated construction
Confirmed across 9 verses: لا and لن are BOTH attested for the identical Greek οὐ μή + aorist subjunctive pattern, sometimes differing between AVD and ONAV on the same verse — genuinely free variation, not a rule waiting to be discovered. Align both οὐ and μή as primary in a single record against whichever Arabic negation the translation used, contiguous with the verb.
An optional reinforcing intensifier (أَبَداً "never/ever", قَطُّ) is a stylistic choice — common in ONAV (6/9 sampled), almost never in AVD. When present with a clear motivating element (πώποτε "ever," or the emphatic force of οὐ μή itself), treat it as primary alongside the negation.
  οὐ μὴ ἀπόλωνται → AVD "لَنْ تَهْلِكَ"; ONAV "فَلا تَهْلِكُ" — different particle, same emphatic-negation family, both primary to οὐ+μή

### οὐκέτι/μηκέτι ("no longer") and οὔπω/μήπω ("not yet")
Render with لا/لم + a reinforcing adverb — بَعْدُ ("yet/anymore," the more standard "no longer" marker) or أَيْضًا ("again/also," a looser paraphrase) — check which per verse; both are primary alongside the negator.
  οὔπω πάρεστιν → "لَمْ يَحْضُرْ بَعْدُ" (لم + jussive + بَعْدُ): confirms لم (not لا) for οὔπω, consistent with the perfective-sense generalization above.

### Negative pronoun subjects (οὐδείς/μηδείς) — no dedicated Arabic negative pronoun
The negative-pronoun subject becomes a plain INDEFINITE noun (أَحَدٌ "someone/anyone"), with negation carried entirely by the verb's own particle (لم/لا/لن) — not by any special morphology on the indefinite noun itself.
  θεὸν οὐδεὶς ἑώρακεν πώποτε → "ٱللهُ لَمْ يَرَهُ أَحَدٌ قَطُّ": οὐδείς's negation-content aligns primary to لَمْ (the verb's own negator); أَحَدٌ aligns primary to the "someone" component of οὐδείς; πώποτε → قَطُّ, primary.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Substantive — three coexisting strategies, conditioned by referent type (not free variation), confirmed against a 25-verse sample

**(a) Genuine Arabic participle (ism al-fāʿil/ism al-mafʿūl)** — for attributive modification of an already-identified/concrete noun, or elevated/hymnic register. Primary, directly parallel to the Greek participle; a fused Greek article is a primary companion per BASE_BLOCK's definiteness rule, not secondary.
  ὁ λαὸς ὁ καθήμενος → "ٱلشَّعْبُ ٱلْجَالِسُ" (al-jālis, ism al-fāʿil from جلس "to sit"): primary
  ὁ σπείρων (specific referent, a parable's sower) → "ٱلزَّارِعُ" (al-zāriʿ): primary
  μορφὴν δούλου λαβών (elevated/hymnic, Phil 2:7) → "آخِذًا"/"مُتَّخِذاً" (accusative indefinite ḥāl-participle): primary

**(b) الَّذِي (al-ladhī, "who/which") + finite verb** — for a specific/deictic referent, often when no natural Arabic participle fits smoothly, or when discourse parallelism with neighboring clauses favors a uniform clause shape.
  ὁ ὀπίσω μου ἐρχόμενος (a specific referent, the forerunner formula) → AVD "ٱلَّذِي يَأْتِي بَعْدِي": primary "يَأْتِي"; secondary/primary companion "ٱلَّذِي" per the article-substantivizing pattern. Both (a) and (b) are live options for the same construction — ONAV independently uses a genuine participle (strategy a) for the identical Greek word in the same verse.

**(c) مَنْ (man, "whoever") + finite verb — the DOMINANT strategy for GENERIC/gnomic "whoever does X" formulaic refrains**
Confirmed across 6 independent instances/3 distinct lexemes, both translations consistent on structure — the single best-attested pattern in the sample, holding even where a corresponding Arabic participle exists and goes unused.
  ὁ ἔχων ὦτα ἀκουέτω → "مَنْ لَهُ أُذُنَانِ فَلْيَسْمَعْ": مَنْ (generic "whoever") primary to the substantivizing article/participle sense; لَهُ ("to him," existential-possessive for "he has") secondary, grammar-required with no independent Greek trigger, parallel to Hindi's existential-possessive pattern
  ὁ νικῶν → "مَنْ يَغْلِبُ" (identically at Rev 2:7 and 3:21, despite a perfectly good active participle غَالِب "conqueror" being available and unused): primary

**Default rule:** (c) مَنْ+finite-verb for generic/gnomic substantive participles; (a) genuine Arabic participle when the referent is attributive to an already-identified concrete noun or the register is elevated/hymnic; (b) الَّذِي+finite-verb as a fallback for a specific/deictic referent lacking a natural participle, or when discourse parallelism favors it.

### Adverbial (circumstantial) — finite subordinate clause is the DEFAULT for ordinary narrative aorist participles, NOT Arabic's own ḥāl-participle construction
Confirmed 4 independent times, both translations, 3 different Greek lexemes: لَمَّا/حِينَ ("when") + finite perfect verb.
  ἀκούσας δέ → "لَمَّا سَمِعَ"/"حِينَ سَمِعَ": primary "سَمِعَ"; لَمَّا/حِينَ secondary (introductory temporal conjunction), same pattern as English "when he heard"
A second common strategy collapses the participle + following main verb into TWO COORDINATE FINITE VERBS (وَ/ثُمَّ "and"/"then"), no subordinating conjunction at all, for a tight two-action sequence sharing a subject:
  ὁ δὲ ἀποκριθεὶς εἶπεν → "فَأَجَابَ وَقَالَ" ("so he-answered and he-said"): both verbs primary, each to its own Greek verb/participle, وَ absorbed as the ordinary fused conjunction
λέγων ("saying," introducing direct speech) has an extremely stable, near-universal formulaic rendering independent of either strategy: قَائِلًا/قَائِلاً (qāʾilan, accusative indefinite ism al-fāʿil from قال "to say," a fixed quotative ḥāl-marker) — primary 1:1 by default (confirmed 6+ times), UNLESS the translation collapses it into a coordinate finite verb (وَقَالَ) instead — both outcomes attested, participle form more common.

### Genitive absolute — no distinct treatment needed; same pattern as ordinary circumstantial participles
Punctual (aorist) genitive absolutes pattern with لَمَّا, same as ordinary circumstantial aorist participles. Durative (present) genitive absolutes use a DIFFERENT durative conjunction — فِيمَا/بَيْنَمَا ("while") — tracking Greek's aorist/present aspectual distinction via conjunction choice, not just lexically.
  Τελευτήσαντος δέ (aorist, punctual) → "لَمَّا مَاتَ": primary "مَاتَ"; لَمَّا secondary
  Ταῦτα αὐτοῦ λαλοῦντος (present, durative — "while he was saying these things") → "وَفِيمَا هُوَ يُكَلِّمُهُمْ": primary "يُكَلِّمُهُمْ"; فِيمَا secondary
An explicit genitive subject (αὐτοῦ) gets an explicit Arabic pronoun (هُوَ) when the translation keeps it — primary, per the main doc's §9.2.2 rule that an explicit genitive-absolute subject is primary, not grammatically implied. Some translations drop the explicit pronoun (relying on the verb's own agreement) — both are legitimate; align it primary only when present.\
"""

COMPARATIVE_BLOCK = """\
## COMPARATIVES AND SUPERLATIVES

Confirmed against a 20-verse sample. Arabic's أَفْعَل (afʿal) elative pattern is morphologically identical for comparative and superlative — disambiguation is purely syntactic via three co-occurring markers, and this maps cleanly onto Greek's own comparative/superlative distinction. But Greek's own suppletive "first"/"last" bypass the elative pattern entirely — check the specific Greek lemma, not just the COMPARATIVE tag, before applying these rules.

### 1. Bare elative + مِنْ (min) + comparandum → comparative ("greater than X")
  μείζων Ἰωάννου → "أَعْظَمُ مِنْ يُوحَنَّا": source=[μείζων], target=["أَعْظَمُ"] — primary 1:1; the case-driven "than" is realized as an explicit مِنْ TOKEN in Arabic (unlike English's case-implied "than") — مِنْ primary to whatever Greek token licenses the comparison (typically the genitive noun); source=[Ἰωάννου], target=["يُوحَنَّا"] — primary 1:1

### 2. Definite article + elative (al-elative) → superlative ("the greatest/least")
  ὁ μικρότερος → "ٱلْأَصْغَرَ": the article's Greek token is an additional primary source per BASE_BLOCK's fused-article rule; ٱلْأَصْغَرَ primary to μικρότερος. Holds across number (confirmed with a definite plural elative too).

### 3. Bare elative, no مِنْ, no article → implicit/absolute comparison ("does better," against an implicit discourse alternative)
  1 Cor 7:38-type (يَفْعَلُ أَحْسَنَ, "does better," no explicit comparandum) — primary alone; no secondary "than" token exists to add since none is present in the Arabic.

### First/last are NOT built on the elative — dedicated ordinal lexemes instead
πρῶτος/ἔσχατος (Greek's own lexically-suppletive superlatives, not synthetic -τερος/-τατος forms) map to Arabic's equally lexical ordinals أَوَّل (awwal, "first")/آخِر (ākhir, "last/other") — closed-class words with no comparative/superlative morphology, absolute by meaning. Do not expect elative marking here.
  πρῶτοι...ἔσχατοι (chiastic "first...last") → أَوَّلُونَ...آخِرِينَ: each Greek ordinal primary 1:1 to its Arabic counterpart in whatever case/number the sentence requires
"Last" has a second lexical strategy for attributive "the last/final [days/times]" collocations — ٱلْأَخِيرَة (al-akhīra, an ordinary attributive adjective) — a free lexical variant of آخِر for alignment purposes, not a distinct construction.
Watch for a Greek COMPARATIVE-tagged token that is really a frozen/lexicalized noun (e.g. πρεσβύτεροι "elders," morphologically a comparative of πρέσβυς but functioning as a plain noun) — Arabic uses an ordinary noun with no degree marking at all in that case; verify the Greek form is genuinely comparing degree before applying the rules above.

### A third superlative strategy — bare elative in an idafa chain with a definite plural noun ("least of the matters")
Functionally equivalent to English's "least of these" analytic-superlative pattern — the elative is the construct-first term (drops its own article per the idafa rule) followed by the possessed plural noun.
  ἐλάχιστον (used absolutely, no genitive complement in the Greek) → "أَصْغَرِ ٱلأُمُورِ" ("the-smallest-of-the-matters"): source=[ἐλάχιστον], target=["أَصْغَرِ"] — primary 1:1; the generic completion noun (ٱلأُمُورِ, "the matters") is translator-supplied with no source anchor → NEQ target, same as the main doc's "specific/generic noun supplied from context" case.

### Open caveats
μᾶλλον does not reliably get its own token — it can absorb into an adjacent conjunction (ἀλλὰ μᾶλλον → بَلْ alone, "rather," with the comparative sense carried entirely by the elative on the main adjective). πλείων/πλεῖον used as a loose quantifier ("many, several") sometimes renders as a plain positive-degree adjective (كَثِيرَةٍ) rather than the elative أَكْثَر — check whether the Greek comparative is a true degree comparison or a loose quantifier before assuming elative marking.\
"""

CONDITIONAL_BLOCK = """\
## CONDITIONAL CONSTRUCTIONS

Arabic has (at least) four particles in play, confirmed against a 19-verse sample — not a simple two-way or three-way split matching Greek's conditional classes.

### لَوْ (law) — dedicated to genuine contrary-to-fact conditions (2nd class: εἰ + past indicative + ἄν) — confirmed 3/3, no exceptions
Primary 1:1 to εἰ, but ONLY reachable for a genuine 2nd-class Greek condition — do not expect لَوْ for 1st- or 3rd-class conditions.
  εἰ ἦς ὧδε οὐκ ἄν ... ἀπέθανεν → "لَوْ كُنْتَ هَهُنَا لَمْ يَمُتْ أَخِي": لَوْ primary 1:1 to εἰ
The apodosis regularly takes a لَ- (la-) proclitic prefix on a كَانَ-periphrasis — the closest Arabic correspondent to ἄν in a counterfactual apodosis; primary to ἄν, fused into the apodosis verb's record per the ordinary fused-proclitic pattern. Negated counterfactual apodoses (οὐκ ἄν + verb) do NOT reliably carry an ἄν-correspondent — some translations drop it entirely (plain negated jussive, ἄν → NEQ); others fuse لَ- into the negator itself (لَمَا, a portmanteau where لَ- IS primary to ἄν). Check per instance.
Caution: a superficially similar لَ- prefix marks an unrelated construction — oath-emphasis (the "lam of the oath" combined with an energetic-mood verb, after e.g. ὤμοσεν "he swore") — do not conflate the two; only the counterfactual-apodosis لَ- is primary to ἄν.

### إِنْ (in) — the default particle for GENUINE open/hypothetical conditions of EITHER Greek 1st or 3rd class
Arabic does not preserve the Greek 1st-class/3rd-class distinction with a different particle — the real split is إِنْ (open) vs. لَوْ (counterfactual), not a 3-way match to Greek. Primary 1:1 to εἰ/ἐάν regardless of Greek mood (indicative or subjunctive).
  εἰ + indicative (1st class) → "إِنْ كَانَ..."; ἐάν + subjunctive (3rd class) → "إِنْ أَخْطَأَ..." — same Arabic particle both times
Correlative ἐάν τε...ἐάν τε ("whether...or") — each clause gets its own إِنْ, correlative structure preserved.

### إِذَا (idhā) — a third particle, for ἐάν when the condition is framed as likely/expected/habitual rather than genuinely open
Confirmed 2/8 in the 3rd-class sample — a real, live distinction (matches the traditional إِنْ=open vs. إِذَا=expected/habitual grammatical description), not yet confirmed at scale. Both align primary 1:1 to the Greek conditional particle regardless of which is chosen — the choice is a translator framing judgment, not a different Greek trigger.

### مَهْمَا (mahmā) and similar free-choice relatives — for ἐάν fused with an indefinite/relative pronoun ("whatever/whoever/wherever")
When ἐάν combines with a relative pronoun (ὅ τι ἐάν, ὃς ἐάν, ὅπου ἐάν) to form a generalizing "whatever/whoever" clause rather than a plain conditional, expect a dedicated Arabic free-choice particle (مَهْمَا, مَنْ, حَيْثُمَا) instead of إِنْ — a distinct construction from ordinary conditionals, closer to how substantive-participle "whoever" is handled (see PARTICIPIAL CONSTRUCTIONS) than to ordinary CONDITIONAL. Single instance confirmed — flag as provisional.

### εἰ μή = "except/only" — NOT a conditional sentence; a fixed exceptive idiom, high-frequency
Confirmed 4/4 (both translations): renders uniformly as إِلَّا (illā), Arabic's dedicated exceptive particle — never إِنْ, never لَوْ. Typically follows a negated main clause, restricting an otherwise universal/negative statement.
  οὐδένα ὑμῶν ἐβάπτισα εἰ μὴ Κρίσπον → "لَمْ أُعَمِّدْ أَحَدًا مِنْكُمْ إِلَّا كِرِيسْبُسَ": source=[εἰ, μή], target=["إِلَّا"] — both Greek particles primary as a single fused unit against إِلَّا, parallel to how μὴ γένοιτο is treated as an idiom-like fixed unit. Do NOT treat εἰ as ordinary conditional and μή as ordinary negation here — together they form one exceptive marker with no independent "if"/"not" meaning.

### εἰ as an indirect-question marker ("whether") — a Koine Hebraism, not conditional at all
After a verb of asking, εἰ introducing an embedded yes/no question renders as هَلْ (hal), the ordinary Arabic yes/no interrogative — align εἰ primary to هَلْ when the translation converts the embedded question to direct-question form (a natural, common move).
  ...ἠρώτων αὐτὸν λέγοντες..., εἰ ἐν τῷ χρόνῳ τούτῳ ἀποκαθιστάνεις... → "...هَلْ فِي هَذَا ٱلْوَقْتِ تَرُدُّ...": εἰ primary to هَلْ

### Apodosis فَ- (fa-) — no Greek trigger, unrepresented
Extremely common as a fused proclitic on the apodosis's first word, but no sampled Greek apodosis had its own particle (τότε/ἄρα/οὖν) to trigger it — Greek marks the apodosis by clause juxtaposition alone. Simply don't represent it (nothing to mark NEQ either — it's fused, not an independent token). Confirmed non-obligatory (absent in some apodoses), a stylistic default, not grammatically required the way the counterfactual لَ- is.\
"""


AUTOS_BLOCK = """\
## αὐτός

Confirmed against a 17-verse sample covering ordinary pronoun uses (all cases), intensive uses, "same" uses, and emphatic/contrastive subject uses.

### Ordinary pronoun (genitive/accusative) — almost always ZERO independent target token, absorbed as a fused suffix
This is the majority case, per BASE_BLOCK's fused-pronominal-suffix rule — stated explicitly here because it applies to nearly every ordinary αὐτός occurrence.
  τὸ ὄνομα αὐτοῦ → "ٱسْمَهُ" (ism-ahu, "his-name"): source=[ὄνομα, αὐτοῦ], target=["ٱسْمَهُ"] — both primary, one fused target token
  ἤγειρεν αὐτήν → "وَأَقَامَهَا" (wa-aqāma-hā): αὐτήν fused onto the verb as an object suffix, primary alongside the verb

### Dative pronoun — sometimes fuses onto a SEPARATE small preposition-carrier token, not the main verb
Some Arabic verbs take a bare object (dative pronoun fuses directly onto the verb, same as accusative above); others require a preposition, in which case the dative pronoun fuses onto that preposition's own token (لَهُ/لَهَا/لَهُمْ "to/for him/her/them", إِلَيْهِ/إِلَيْهَا/إِلَيْهِمْ "to him/her/them") — a separate whitespace token from the verb. Do not assume the dative pronoun's correspondent is always inside the verb's own token.
  λέγει αὐτῇ → "قَالَ" "لَهَا" (qāla / lahā, TWO tokens): αὐτῇ primary to "لَهَا" (itself a fused preposition+suffix, per BASE_BLOCK's fused-preposition rule), not to "قَالَ"
  διανεύων αὐτοῖς → "يُومِئُ" "إِلَيْهِمْ" (two tokens): same pattern

### Intensive ("himself/herself/itself") — نَفْس (nafs, "self") + possessive suffix, highly consistent
High confidence — both translations converge every time, agreement tracks Arabic's own grammatical gender (not always Greek's).
  αὐτὸς ἐγώ ("I myself") → "أَنَا" "نَفْسِي": source=[ἐγώ], target=["أَنَا"] primary 1:1; source=[αὐτός], target=["نَفْسِي"] primary 1:1
  αὐτὸ τὸ πνεῦμα ("the Spirit itself," neuter in Greek) → "ٱلرُّوحُ" "نَفْسُهُ" (masculine suffix, agreeing with Arabic's own gender for روح, not Greek's neuter): primary 1:1 regardless of the gender mismatch (surface-form difference, not a problem)
The intensified noun/pronoun always gets its own separate primary record — same as the main doc's AUTOS pattern (§9.5.1); only the target-side morphology differs (a noun+suffix construction, not a dedicated particle).

### "Same" — THREE distinct strategies by construction type, not one
Check which sub-construction is in play before assuming a single strategy:
1. **Identity-of-source/material** ("of the same lump") → وَاحِدَة ("one/single"), NOT نفس or عين: ἐκ τοῦ αὐτοῦ φυράματος → "مِنْ كُتْلَةٍ وَاحِدَةٍ": source=[αὐτοῦ], target=["وَاحِدَةٍ"] primary
2. **Adverbial "in the same way/likewise"** (τὸ αὐτό, adverbial) → عَيْن (ʿayn, "eye" → idiomatically "very/self") + possessive suffix: τὸ αὐτὸ καὶ ὑμεῖς χαίρετε → AVD "وَبِهَذَا" "عَيْنِهِ": primary. Some translations drop it entirely for a generic "likewise" (ONAV) — when dropped, αὐτό → NEQ target, no token realizes it.
3. **Predicate "is the same" (unchanging identity)** → a fixed doubled-pronoun idiom هُوَ هُوَ ("he [is] he"): ὁ αὐτός (substantivized article+αὐτός as a predicate, implied copula) → "هُوَ" "هُوَ" — not compositional, cannot cleanly assign "the" to one هُوَ and "same" to the other. Treat as a single N:1 record: source=[ὁ, αὐτός], target=["هُوَ","هُوَ"], both target tokens primary.

### Emphatic/contrastive subject use — LOW CONFIDENCE, translator-variable
Sometimes an independent هُوَ, sometimes zero token — only 5 instances sampled, flagged as a working hypothesis, not a rule. Tentative pattern: genuine CONTRASTIVE emphasis ("HE, not someone else," e.g. Matt 3:11's αὐτὸς ὑμᾶς βαπτίσει contrasting the Coming One with John) tends to get an independent هُوَ, primary to αὐτός. Mere topic-continuity/paragraph-transition use of fronted αὐτός (a common Greek narrative device with no real contrastive force, e.g. Luke 8:54's αὐτὸς δὲ κρατήσας) tends to be absorbed into the verb's own agreement with NO token at all. When zero token results, this is NOT NEQ — the pronoun's grammatical content is fully carried by the verb's own person/number agreement, so it is more naturally left unrecorded, parallel to ordinary pro-drop subject pronouns.\
"""

HOTI_BLOCK = """\
## ὅτι

Confirmed against a 24-verse sample covering causal, content-clause, and recitative uses. Causal and content-clause ὅτι get genuinely different Arabic renderings — they do not collapse to one particle. Content-clause "that" itself further splits by matrix-verb type, and recitative ὅτι is NOT uniformly NEQ — both are departures from a single-pattern default.

### Causal ("because/for") → لِأَنَّ (li-anna), a fused preposition+complementizer, often further fused with a pronominal-subject suffix
High confidence (8 instances, both translations converge every time). لِأَنَّ = لِ ("because of") + أَنَّ (complementizer). When the causal clause's subject is a supplied pronoun (from Greek verb agreement, no separate Greek token), it fuses onto لِأَنَّ as a suffix — the suffix is a secondary supplied-subject-pronoun, same as an ordinary supplied subject (main doc §9.2.1), just packaged into the fused token.
  ὅτι εἴδετε (καὶ ἐχορτάσθητε) → "لِأَنَّكُمْ رَأَيْتُمْ": ὅτι primary to لِأَنَّكُمْ; the -kum suffix is secondary (supplied 2pl subject)
  ὅτι τὸ μωρὸν τοῦ θεοῦ (subject is a full NOUN, not a pronoun) → "لِأَنَّ جَهَالَةَ ٱللهِ": لِأَنَّ appears bare, no suffix, since there's no pronoun to fuse
διότι (διά+ὅτι) triggers the identical لِأَنَّ strategy as bare causal ὅτι.
**Alternative causal strategy (single instance, both translations agree):** إِذْ (idh, "since/as," a lighter causal-temporal connective, NOT built on أَنَّ, takes no suffix) — attested once for a causal clause embedded in ongoing narrative description; needs more sampling to characterize when it's preferred over لِأَنَّ.

### Content-clause ("that") — TWO complementizers, chosen by matrix-verb type, not one primary-1:1 case
This is a genuine split, not free variation — check the governing verb:
- **أَنَّ (anna)** after verbs of knowing/believing/understanding/hoping/being-ignorant-of (γινώσκω, πιστεύω, οἶδα, ἐλπίζω, ἀγνοέω-type). High confidence, 6 confirmed instances, no exceptions.
  οἶδα ὅτι... ("I know that...") → "أَعْلَمُ أَنِّي أَمْكُثُ": ὅτι primary to أَنِّي (with fused 1sg suffix as secondary supplied subject)
- **إِنَّ (inna)** specifically after verbs of SAYING (λέγω/εἶπον-type), functioning almost as a quotative marker. Medium confidence, confirmed in minimal pairs within single verses (the deciding factor is the matrix verb, not clause structure — an embedded-object-clause structurally identical to the أَنَّ cases still gets إِنَّ when the matrix verb is "say").
  ὑμεῖς λέγετε ὅτι θεὸς ἡμῶν ἐστιν → "تَقُولُونَ أَنْتُمْ إِنَّهُ إِلَهُكُمْ": ὅτι primary to إِنَّهُ
Any pronominal-subject suffix fused onto either complementizer follows the same secondary-supplied-pronoun logic as the causal case above.

### Recitative (introducing direct speech, no "that" meaning) — check what the translation did; NOT uniformly NEQ
Two live outcomes, both attested — do not default to NEQ automatically:
(a) **Punctuation only** (colon/quotation marks, no opener word) → ὅτι NEQ, matching main doc §9.7.3, still a valid and common outcome.
(b) **A quotative-opener word is inserted at the boundary** (إِنَّ+optional pronoun suffix, or occasionally a different word like حَقّاً "truly") → ὅτι recitative aligns PRIMARY to that opener, since its presence tracks the Greek ὅτι rather than occurring independently — confirmed by a negative control (a Greek quote with NO ὅτι at all uses punctuation only, no إِنَّ inserted, showing the insertion isn't just free Arabic style).
  Μωϋσῆς ἔγραψεν ἡμῖν ὅτι ἐάν τινος ἀδελφὸς ἀποθάνῃ... → AVD "كَتَبَ لَنَا مُوسَى: إِنْ مَاتَ..." (colon only, no إِنَّ — outcome (a); the quoted content opens with its own particle إِنْ "if")
  ἔλεγον ὅτι Οὗτος ἔστιν... → AVD "قَالُوا: «إِنَّ هَذَا هُوَ...»" — outcome (b), ὅτι primary to إِنَّ; ONAV instead uses حَقّاً ("truly") in the same slot, a different lexical choice filling the same structural position
Check the specific translation's choice at each recitative ὅτι rather than assuming either outcome by default.\
"""

IMPERSONAL_BLOCK = """\
## IMPERSONAL VERBS

Confirmed against a 22-verse sample (of only 121 IMPERSONAL-tagged verses in the NT — δεῖ/ἔξεστιν/ἔξεστι/πρέπει/συμφέρει/δοκεῖ). Arabic impersonal verbs are bare 3rd-masculine-singular finite forms (or zero-copula adjectival predicates) with NO subject pronoun at all — never an explicit هُوَ ("it").

**Do NOT apply the English "dummy it → NEQ" rule.** NEQ asserts a positive claim that a word is untranslated — but there is no token slot for "it" in Arabic to begin with. Simply leave the dummy subject unrecorded, the same way ordinary pro-drop subjects are handled when fully recoverable from verb agreement.

### δεῖ ("it is necessary/must")
`يَنْبَغِي` (yanbaghi) is AVD's dominant strategy (8/9 sampled); ONAV instead consistently prefers `لَابُدَّ` (lā budda, "there is no escape from," a fixed idiom) — different lexical choices, identical mechanism (bare, no subject). `يَجِبُ` (yajibu) is attested once as an AVD alternative — treat all three as free lexical variants, primary 1:1 to δεῖ.
  δεῖ γενέσθαι → "يَنْبَغِي أَنْ يَكُونَ": δεῖ primary to يَنْبَغِي; γενέσθαι primary to يَكُونَ; أَنْ secondary (grammatical connector)

### ἔξεστιν/ἔξεστι ("it is lawful")
`يَحِلُّ` (yaḥillu) is the dominant AVD strategy, confirmed for Sabbath/purity-law contexts; `يَجُوزُ` (yajūzu, broader "permissible") attested once for a civil/political context (the tribute-to-Caesar question) — possibly domain-conditioned, only 1 instance. ONAV uses `يَحِلُّ` uniformly.

### συμφέρει ("it is better/profitable")
TWO distinct strategies, free variants: (a) a bare zero-copula adjectival predicate `خَيْرٌ` (khayrun, "[it is] better") — AVD's more common choice for comparative "better X than Y" senses, primary alone, no verb, no copula; (b) a genuine finite verb `يَنْفَعُ` (yanfaʿu, "profits"), with the person-affected as a fused OBJECT suffix directly on the verb (not via a separate preposition-carrier token the way AUTOS's dative pronouns often are — `نفع` takes a bare object in Arabic).

### Complementary clause — THREE strategies, not one
- **أَنْ + subjunctive** (bare infinitive-substitute, same logical subject) — the default: أَنْ is a pure grammatical connector, secondary (same treatment as English "to," main doc §8.4); the following verb is primary to the Greek infinitive.
- **أَنَّ + full clause with its own subject** (when the embedded clause's subject differs from/is more explicit than the matrix predicate implies) — أَنَّ is still secondary, but licenses its own case marking on the clause's subject (a purely Arabic-internal requirement, no Greek trigger).
- **Bare verbal noun (maṣdar)** — no أَنْ/أَنَّ at all (e.g. `يَنْبَغِي فِيهَا ٱلْعَمَلُ`, `هَلْ يَحِلُّ ٱلْإِبْرَاءُ`) — the maṣdar noun itself is primary to the Greek infinitive; no secondary connector token exists in this strategy, since the maṣdar nominalizes the verb directly.

Confirmed across all three impersonal-verb families (δεῖ, ἔξεστιν, ἀδύνατον-type) — a general property of Arabic impersonal-predicate complementation, not tied to one verb.

**Caution:** not every IMPERSONAL-tagged δοκέω instance is genuinely impersonal — Greek δοκέω is also used personally ("τις δοκεῖ..." = "if anyone thinks himself..."), which renders as an ordinary personal verb (`يَظُنُّ`/`ظَنَّ`, "thinks") with an explicit subject, no impersonal construction at all. Check context before assuming an impersonal reading for any δοκέω instance.\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

Confirmed against a 22-verse sample. Classical Arabic has NO true infinitive form — the strategy depends entirely on which of (at least) five Greek infinitive uses is in play. Treat each sub-case separately; a single "'to' secondary to the infinitive" rule does not work for Arabic.

### 1. Complementary infinitive (after θέλω/δύναμαι/ἄρχομαι/ἔξεστιν-type verbs) → أَنْ (an) + subjunctive finite verb — the cleanest, most consistent pattern
High confidence, both translations converge every time. أَνᾶ here is a real, standalone target token (not fused) that realizes the Greek infinitive's "to"-function — BOTH أَνᾶ and the following subjunctive verb are primary (unlike English's secondary "to" — أَنْ is the actual subordinator, doing more structural work).
  χρείαν ἔχω...βαπτισθῆναι ("I have need to be baptized") → "مُحْتَاجٌ أَنْ أَعْتَمِدَ": source=[βαπτισθῆναι], target=["أَنْ","أَعْتَمِدَ"] — both primary
When the Greek infinitive clause is negated, expect either an embedded لَا inside the أَنْ-clause (أَنْ + لَا + subjunctive), or a lexicalized negative matrix verb + nominalized complement — check per verse; both attested.

### 2. Purpose infinitive — MULTIPLE coexisting strategies depending on Greek form and coordination — check the whole series, not each infinitive independently
- **Bare purpose infinitive** (no τό/εἰς τό/πρός τό) → `لِ-` (li-, FUSED proclitic) + subjunctive. High confidence, rock-solid across both translations — treat لِ- like any other fused preposition/particle: primary alongside the verb.
- **Prepositional-articular purpose infinitive** (πρός τό/εἰς τό + inf) → `لِكَيْ` (li-kay, "in order that") + subjunctive — a heavier, free-standing two-word marker, primary 1:1.
- **Coordinated purpose-infinitive series** — the marker is often established once, with later members sharing it via plain `وَ` (wa-) + subjunctive and NO repeated purpose marker. Do not predict per-infinitive independently within a series; check what the whole series did.
- **Purposive verb-serialization** — no overt purpose marker at all: a motion verb followed directly by bare coordinated present-tense verb(s) (e.g. `ذَهَبَ يُعَلِّمُ` "went [and] taught," parallel to English "go teach"). When this strategy is used, align the infinitive primary to the bare finite verb with no secondary/primary marker token to add.

### 3. Articular infinitive as SUBJECT/PREDICATE (nominal use, no governing preposition) → a plain verbal noun (abstract noun), NOT a verb form
High confidence, both translations independently nominalize: τὸ ζῆν/τὸ ἀποθανεῖν ("to live"/"to die," as clause subjects) → `ٱلْحَيَاةَ`/`ٱلْمَوْتُ` (genuine lexical nouns, not verb forms at all) — the Greek article fuses as al- per BASE_BLOCK; the infinitive itself is primary to the noun despite the total word-class change.

### 4. Articular infinitive with a TEMPORAL preposition (μετά τό/ἐν τῷ) → a finite subordinate clause, NOT nominalization
Distinct from both §2 and §3 — matches the same `لَمَّا`/`فِيمَا`-type temporal-conjunction pattern as circumstantial participles and genitive absolutes (see PARTICIPIAL CONSTRUCTIONS): μετὰ τὸ παθεῖν αὐτόν ("after he suffered") → `بَعْدَ مَا تَأَلَّمَ`: μετά primary to `بَعْدَ`; τό primary to `مَا` (the subordinating particle of the fixed compound); παθεῖν primary to a FINITE verb, not a noun; the infinitive's own accusative subject (αὐτόν) has no separate token — folded into the finite verb's agreement.

### 5. Accusative + infinitive indirect discourse → the SAME أَنَّ/إِنَّ complementizer system as ὅτι content clauses (see HOTI) — but sometimes converts to a bare direct quotation instead
Medium-high confidence: accusative+infinitive after a verb of saying gets `إِنَّ` (e.g. τίνα με λέγουσιν...εἶναι → `مَنْ يَقُولُ ٱلنَّاسُ إِنِّي أَنَا؟`), matching HOTI's إِنَّ-after-λέγω finding exactly — this is not a structurally distinct alignment problem from ὅτι content clauses. The infinitive copula (εἶναι) itself has NO target token — zero-copula predicate. After a cognition/expectation verb, `أَنَّ` is used instead (matching HOTI's أَνᾶ-after-cognition-verbs rule), and a complementary infinitive can nest inside the أَنَّ-clause as its own أَنْ-clause (double-layering — check for this in complex verses).
**Alternative, confirmed AVD/ONAV divergence on the same verse:** the whole clause sometimes converts to a bare DIRECT quotation with no complementizer at all (the acc+inf equivalent of recitative ὅτι's punctuation-only strategy) — check per translation, do not assume either outcome.\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

Confirmed against a 24-verse sample. TWO genuinely distinct systems, not one — Arabic's purpose-marker choice tracks whether ἵνα is a VERBAL COMPLEMENT or a genuine ADVERBIAL PURPOSE/RESULT clause. Do not treat all ἵνα uniformly as "purpose conjunction, primary."

### 1. Complement-clause ἵνα (θέλω/παρακαλῶ/εἶπον-as-command + ἵνα, substituting for what would otherwise be an infinitive complement) → bare أَنْ (an) + subjunctive, NO purpose marker
High confidence — 5 instances, both translations converge every time. The trigger is the SYNTACTIC ROLE of the ἵνα-clause (direct object/content of the matrix verb), not a closed lexical list — confirmed extending beyond θέλω to παρακαλῶ and εἶπον-as-command.
  ὅσα ἐὰν θέλητε ἵνα ποιῶσιν ὑμῖν οἱ ἄνθρωποι (Golden Rule) → "تُرِيدُونَ أَنْ يَفْعَلَ ٱلنَّاسُ بِكُمُ": θέλητε primary to تُرِيدُونَ; ἵνα ποιῶσιν primary to أَنْ يَفْعَلَ — ἵνα itself is primary to أَنْ, a genuine correspondent, just not a "purpose marker" one
**Contrast — the SAME matrix-verb family with a GENUINE adverbial purpose clause attached does NOT collapse to أَنْ:** confirmed by a clean minimal pair — Gal 4:17's θέλω has its OWN infinitive complement, with a separate purpose ἵνα attached (→ full `لِكَيْ`, not أَنْ); 1 Thess 4:13 same pattern. Same verb, opposite syntactic role, opposite Arabic strategy — this is the clearest evidence the split is structural.

### 2. Adverbial purpose ἵνα → a FAMILY of free-variant particles: `لِ-` (fused), `لِكَيْ` (full), `كَيْ` (bare)
High confidence (13 instances) — genuinely interchangeable, confirmed by a single verse (John 1:7) using BOTH لِ- and لِكَيْ for two consecutive, structurally identical purpose clauses with no discernible conditioning factor. When `لِ-` (fused) is used, ἵνα's Greek token is pulled in as an additional primary source alongside the verb it's fused to, per BASE_BLOCK's fused-preposition rule; when `لِكَيْ`/`كَيْ` appear as their own standalone token (the norm), ἵνα aligns primary 1:1 directly.

### 3. Result/consecutive ἵνα and ὥστε → `حَتَّى` (ḥattā, "until/so that") — a real alternative, leaning result/consecutive but NOT strictly reserved for it
Medium-high confidence (4 instances), one clear counter-example (a translator uses `حَتَّى` for an ordinary purpose ἵνα too) — treat as a genuine alternative to the purpose family generally, with a lean toward result/consecutive contexts, not a hard categorical rule. `حَتَّى` primary 1:1 to ἵνα/ὥστε regardless of whether the specific instance reads as purpose or result.

### 4. Negative purpose (ἵνα μή, "lest") — (at least) FOUR-FIVE live realizations, genuinely free variation, NOT a fixed AVD-vs-ONAV split
Confirmed: `لِكَيْ لَا` (two words), `لِئَلَّا` (fused, li-+an+la), `كَيْ لَا` (bare kay+la), `حَتَّى لَا` (ḥattā+la), and a zero-marker outcome (clause simply coordinated with `فَلَا`, no purpose word at all). **Both AVD and ONAV use multiple variants each** — this is genuinely free variation across both translations, not a stable per-translation register difference. Align both ἵνα and μή as primary in a single record against whichever realization the translation used; for the zero-marker outcome, flag as an open question (NEQ vs. a looser primary link to the bare negator) rather than assuming either resolution.\
"""

VERBAL_ASPECT_BLOCK = """\
## VERBAL ASPECT

Confirmed against a 20-verse sample. Arabic marks these aspectual nuances EXPLICITLY LESS OFTEN than Greek/English do — a plain perfective verb with the nuance left unmarked/implicit was the majority outcome (~60% of sampled tokens in this pass), not the exception. Do not assume explicit marking by default; check per verse whether the translation supplied one.

### Iterative/habitual/durative imperfect
Explicit strategy when marked: `كَانَ` (kāna, "was") + imperfect verb (or + adjective/participle for a maintained STATE rather than repeated action) — both elements primary, matching main doc §9.1.3. High confidence, both translations converge on the periphrasis every time it's used.
  ἀπέλυεν ("he used to release") → "وَكَانَ يُطْلِقُ": source=[ἀπέλυεν], target=["كَانَ","يُطْلِقُ"] — both primary
**Collapses to a plain perfective verb, no periphrasis** when (a) the clause is negated, or (b) the Greek imperfect denotes a single/distributive event within one narrated episode rather than genuine repetition over time — primary alone, nothing extra to align, parallel to how a Greek historical present collapses to an ordinary past tense (main doc §9.1.2) with no special marking required.

### Ingressive imperfect/aorist ("began to X")
When marked explicitly, one of (at least) four attested auxiliaries — `صَارَ` (ṣāra), `قَامَ` (qāma), `جَعَلَ` (jaʿala), `بَدَأَ` (badaʾa) — + imperfect verb, both primary; auxiliary choice is inconsistent even within a single verse across translations (free lexical variation, not conditioned by anything found so far). **A plain perfective verb with NO ingressive marking is actually the MORE common outcome** in this sample — do not assume explicit marking; treat it as one live but non-guaranteed option to check for per verse.

### Conative imperfect ("tried to X but did not succeed")
**Genuinely UNMARKED when the Greek verb is an ordinary action verb** — the project's own canonical example (Mark 15:23, ἐδίδουν, "they offered him wine... but he did not take it") gets NO conative marking in either Arabic translation: a plain perfective verb (`أَعْطَوْهُ`/`قَدَّمُوا لَهُ`), primary alone, with the "attempted but refused" sense left entirely to the following negated clause — exactly as bare Greek itself leaves it to pragmatic inference, not grammatical marking.
**Only appears "marked" when the Greek verb's OWN LEXEME already means "try/attempt"** (πειράζω, ἐπιχειρέω) — Arabic then supplies `حَاوَلَ` (ḥāwala, "to try") + أَنْ + subjunctive complement, but this is ORDINARY LEXICAL correspondence (the Greek word's own meaning IS "try," main doc §3.4's practical test), not a special periphrastic aspect construction, even though the Greek form happens to be imperfect tense. `حَاوَلَ` primary 1:1 to the Greek "try"-lexeme; أَنْ secondary (infinitive/subjunctive-complement marker, parallel to "to").\
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

ARB_CONFIG = LanguagePromptConfig(
    language_code="arb",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(ARB_CONFIG)
