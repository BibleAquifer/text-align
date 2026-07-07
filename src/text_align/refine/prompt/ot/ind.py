"""Indonesian target-language prompt config for OT (Hebrew) refine-alignment.

Examples grounded in Alkitab Terjemahan Baru (TBI) — checked against the
actual target TSV (Genesis 1:1-2, Genesis 2:23, Joshua 1:1, Judges 21:25,
Psalm 23:1, Genesis 3:1), not constructed from general knowledge alone.

Key differences from OT English (eng.py):
  BASE_BLOCK           — no articles at all (Hebrew article word-part is
                         overwhelmingly Branch B, absorbed with no target
                         word — the majority case, unlike English's
                         near-obligatory "the"); "itu"/"ini" only for the
                         minority anaphoric/demonstrative case, parallel to
                         NT Indonesian. Fused possessive/object clitics
                         (-ku/-mu/-nya) attach directly to noun, preposition,
                         or verb as ONE target token — both the head token
                         and the pronominal-suffix word-part are primary,
                         sharing that one token (see nt/ind.py precedent).
                         No indefinite article (bare noun default).
  CONSTRUCT CHAINS     — the standout structural difference: Indonesian forms
                         possession/genitive by bare noun-noun juxtaposition
                         in the SAME head-then-modifier order Hebrew already
                         uses (rumah Tuhan = "house LORD" = בֵּית יְהוָה) — no
                         linking word is needed at all, unlike English "of"
                         or French "de". "dari" only appears when it
                         corresponds to an actual Hebrew מִן ("from")
                         preposition token (source/partitive sense, e.g.
                         Genesis 2:23's "tulang dari tulangku"), never as a
                         supplied construct-chain marker.
  PRONOMINAL_SUFFIX_BLOCK — fused-clitic pattern from nt/ind.py: singular
                         suffixes (-ku/-mu/-nya) fuse onto the noun,
                         preposition, or verb they attach to as ONE
                         Indonesian word; both Hebrew word-parts are primary
                         to that single fused token. Plural pronouns
                         (kami/kita/mereka) never fuse — normal 1:1.
  NEGATION_BLOCK       — simple contiguous negation (tidak/jangan + verb),
                         no discontiguous structure (contrast French's
                         ne...X); existential אֵין renders as the fixed
                         "tidak ada" phrase.
  PARTICIPLE_BLOCK     — "yang" pattern for substantive participles, with or
                         without an explicit head noun ("orang(-orang)"),
                         matching NT Indonesian exactly.
  INFINITIVE_BLOCK     — no distinct infinitive marker (bare verb primary,
                         unlike English "to"); the בְּ+infinitive temporal
                         construction renders as an ordinary finite clause
                         with "ketika"/"saat", not a nonfinite form — same
                         mechanism NT Indonesian uses for ἐν τῷ + infinitive.
"""

from text_align.refine.prompt.common import LanguagePromptConfig
from .core import register_ot_language
from .eng import BLOCK_ORDER, FORCED_INCLUSIONS


# ---------------------------------------------------------------------------
# Prompt blocks
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

Word-part present → align Indonesian correspondent primary to that token.
No word-part (morpheme merged into main token) → align correspondent primary to the main token.

## TOKEN ROLES

primary — direct lexical or semantic connection to the Hebrew token
secondary — exists because of Hebrew grammar with no separate source token (construct relation, verbal morphology, merged definiteness)
other Hebrew token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:
- Subject pronoun — Indonesian verbs never inflect for person/number, but pronoun use is discourse-driven rather than grammar-driven: a pronoun is typically supplied when a clause introduces or switches to a new subject (common at waw-consecutive narrative transitions), and dropped when a coordinate clause continues the same topic. When present with no separate Hebrew pronoun token → secondary. When dropped (topic continuity) → none expected, leave unrecorded.
  וַיֹּאמֶר → "lalu berkatalah" (introducing a new speech act, no repeated subject because context already establishes it): "lalu" primary (waw word-part); "berkatalah" primary (verb token). If a distinct subject noun follows, it gets its own record.
  Coordinate continuation (same subject as prior clause): no supplied pronoun — none expected.
- No linking word for construct chain — Indonesian juxtaposes head noun + modifier noun directly, matching Hebrew's own construct word order; no secondary "of"-equivalent is needed (see CONSTRUCT CHAINS).
- No Indonesian article when merged — no article word-part; the noun stands bare, no secondary needed (majority case, see ARTICLES).
- Auxiliary verbs for participles ("sedang duduk", "ada duduk") — main verb primary; auxiliary secondary.

- Fused possessive/object clitic — Indonesian's 1st/2nd/3rd-singular possessive and object pronouns (-ku, -mu, -nya) hyphenate directly onto the noun, preposition, or verb they attach to, forming ONE target token. When Hebrew expresses this with a pronominal-suffix word-part, BOTH the head token and the suffix word-part are primary, sharing the single fused target token. Plural suffixes (kami, kita, mereka) never fuse — they stay separate words and align as a normal 1:1 pair.
  רֹעִי → "gembalaku": source=[רֹעִי-noun, sufPart], target=["gembalaku"] — both primary
  אֵלָיו → "kepadanya": source=[elPart, sufPart], target=["kepadanya"] — both primary

- Periphrastic rendering — when a single Hebrew token is rendered by multiple Indonesian words, all words carrying lexical content are primary; purely grammatical connectors (relativizers, case markers) are secondary to the same token. Indonesian's rich verbal morphology (me-, memper-, ber-, ter-, di-) often does the reverse — rendering a Hebrew verb as a SINGLE Indonesian word where English needed a multi-word periphrasis; when that happens, align 1:1, no split needed.
  מָשַׁל → "menguasai": primary 1:1 (compare English "exercises dominion over," which needs three words)
  שֹׁמֵר (substantive participle) → "yang menjaga": "menjaga" primary; "yang" secondary (see PARTICIPIAL CONSTRUCTIONS)
  הוֹדוּ → "mengucap syukur": "mengucap", "syukur" both primary
  הֵיטִיב → "berbuat baik": "berbuat", "baik" both primary
  Hebrew niphal/pual/hophal (passive-voice stems) rendered with di-/ter- prefixes → single fused Indonesian token, primary 1:1, no separate auxiliary needed (contrast English "was created").

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Hebrew direct object marker (אֶת/אֵת, pos=particle) → NEQ source in virtually all cases (marks definite direct objects; no Indonesian equivalent). Rare exception: when explicitly rendered "adapun" or similar topic-marking word.
Supplied copula ("adalah"/"ialah") with no Hebrew verb token → NEQ target (verbless clause).
  יְהוָה רֹעִי → "Tuhan adalah gembalaku":
    source=[יְהוָה], target=["Tuhan"] — primary
    source=[רֹעִי-noun, sufPart], target=["gembalaku"] — both primary (fused suffix)
    "adalah" → NEQ target
Waw conjunction + Indonesian asyndeton → waw word-part NEQ source.
Indonesian conjunction with no Hebrew conjunction token → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, aspect, and verbal stem (binyan) differences do not prevent alignment. Align on lexical/semantic correspondence.

## GRANULARITY
Prefer one record per source token — split rather than group. Create separate records whenever source tokens (or word-parts) can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Leaving tokens unrecorded when no genuine correspondence exists is deliberate — not a failure.
Grammar-required translation words (fused pronominal suffix, modal helpers for verbal morphology ["bisa," "mungkin," "akan"], reinstated demonstrative) are secondary to the source token or word-part whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## ARTICLES
Hebrew article (הַ/הָ/הֶ) appears as a separate word-part token (pos=particle). Never NEQ.
DEFAULT (most common in Indonesian) → Branch B: no separate word at all — the noun stands bare, and the article is secondary to the noun's own record with no target word required. This is the majority case in Indonesian, unlike English's near-obligatory "the".
MINORITY case → Branch A: primary 1:1, when the translation does supply a distinct word.

### Branch A — article has a distinct Indonesian correspondent
- → "itu" (distal, anaphoric — referring to something already introduced) or "ini" (proximal): primary 1:1; noun in its own record. Typically appears on a SECOND or later mention of a referent, not the first.
  הָאָרֶץ (first mention) → "bumi" — no correspondent (Branch B, absorbed, no target word)
  הָאָרֶץ (repeated/anaphoric mention) → "bumi itu": source=[articlePart], target=["itu"] — primary 1:1; source=[אָרֶץ], target=["bumi"] — primary 1:1
- → "orang"/"orang-orang" (substantive participle, generic head noun supplied): article → primary 1:1; "yang" secondary to the participle (see PARTICIPIAL CONSTRUCTIONS).

### Branch B — no distinct Indonesian correspondent → secondary, no target word
- Articular noun, bare in Indonesian: source=[articlePart, אָרֶץ], target=["bumi"] — primary: "bumi"; secondary.source: [articlePart] (no target word needed)
- Construct-chain absolute noun with article: Indonesian juxtaposition already carries the construct-chain semantics; the article stays secondary with no separate word (see CONSTRUCT CHAINS).

### Anarthrous noun
No Hebrew article token exists, and Indonesian has no indefinite article — bare noun, no secondary needed. אִישׁ → "orang": primary alone.

## CONSTRUCT CHAINS
A construct chain expresses genitive by word order and construct form — no preposition token. Indonesian forms possession the same way: bare noun-noun juxtaposition, head noun first, exactly matching Hebrew's own construct order. No linking word is needed — this differs from every Indo-European target config, which requires an explicit "of"/"de"/"do" secondary.
  בֵּית יְהוָה → "rumah Tuhan":
    source=[בֵּית], target=["rumah"] — primary 1:1 (no secondary needed)
    source=[יְהוָה], target=["Tuhan"] — primary 1:1
  מֹשֶׁה עֶבֶד־יְהוָה → "Musa hamba Tuhan":
    source=[מֹשֶׁה], target=["Musa"] — primary 1:1
    source=[עֶבֶד], target=["hamba"] — primary 1:1 (no secondary needed)
    source=[יְהוָה], target=["Tuhan"] — primary 1:1
Do NOT expect or supply a secondary "dari" for a bare construct relationship. "dari" is reserved for an actual Hebrew מִן ("from") preposition token expressing source or partitive sense — never a supplied construct-chain marker.
  עֶצֶם מֵעֲצָמַי → "tulang dari tulangku" (מִן preposition present, not a bare construct):
    source=[עֶצֶם], target=["tulang"] — primary 1:1
    source=[minPrepPart], target=["dari"] — primary 1:1
    source=[עֶצֶם, sufPart], target=["tulangku"] — both primary (fused suffix)
Construct definiteness: Hebrew article word-part on the absolute noun stays secondary per ARTICLES Branch B — Indonesian's own juxtaposition already signals the relationship, so no extra word is needed even when the article marks the whole chain as definite.

## INSEPARABLE PREPOSITIONS
Preposition word-part → Indonesian preposition (di/ke/dari/dengan/seperti): primary 1:1. Merged article in the same token has no separate Indonesian correspondent (Indonesian has no article) — no secondary needed beyond the ordinary Branch B treatment.
  בַּשָּׁמַיִם "di langit" (single merged token, article absorbed): source=[bashamayimId], target=["di", "langit"] — primary: "di", "langit"

## CONJUNCTIONS AND PARTICLES
Align content words first; conjunctions and particles are residual.
- Waw word-part (pos=conjunction) → "dan"/"tetapi"/"lalu"/"maka"/"sebab": primary. Asyndeton → NEQ source.
- כִּי — polyfunctional; align to whichever Indonesian word carries its force in context ("bahwa", "sebab", "karena"). Introducing direct speech with only punctuation → NEQ source.
- אֲשֶׁר/שֶׁ — "yang" (universal relativizer): primary. Absorbed without correspondent → NEQ source.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source units are never idioms — they have individual correspondences or NEQ determinations.\
"""

PRONOMINAL_SUFFIX_BLOCK = """\
## PRONOMINAL SUFFIXES

Pronominal suffixes are separate word-part tokens (pos=suffix). Singular suffixes (-ku, -mu, -nya) fuse directly onto the noun, preposition, or verb they attach to, forming ONE Indonesian token — BOTH the head token and the suffix word-part are primary, sharing that single fused token (same mechanism as NT Indonesian's fused-clitic rule). Plural suffixes (kami, kita, kalian, mereka) never fuse — they stay separate words and align as a normal 1:1 pair.

- Possessive suffix on noun (singular, fused): both tokens primary to the one fused word.
  דְּבָרוֹ "firman-Nya"/"perkataannya": source=[davarPart], target=["perkataannya"] — primary; source=[sufPart], target=["perkataannya"] — primary (same token, both primary)
  Plural possessive (no fusion): source=[sufPart], target=["mereka"] — primary 1:1; source=[davarPart], target=["perkataan"] — primary 1:1

- Object suffix on verb (singular, fused): both tokens primary to the one fused word.
  שְׁמָרַנִי "menjagaku": source=[shamarPart], target=["menjagaku"] — primary; source=[niPart], target=["menjagaku"] — primary (same token, both primary)
  Plural object (no fusion): שְׁמָרֵנוּ "menjaga kami": source=[shamarPart], target=["menjaga"] — primary 1:1; source=[nuPart], target=["kami"] — primary 1:1

- Suffix on preposition (singular, fused): both tokens primary to the one fused word.
  אֵלָיו "kepadanya": source=[elPart], target=["kepadanya"] — primary; source=[sufPart], target=["kepadanya"] — primary (same token, both primary)\
"""

NEGATION_BLOCK = """\
## NEGATION

Indonesian negation is simple and contiguous (tidak/jangan + verb) — unlike languages with discontinuous negation, and there is usually no separate auxiliary to secondary-mark.

- לֹא/לוֹא → "tidak" (indicative): primary 1:1. Verb gets its own record.
  לֹא יֵדַע → "tidak tahu": source=[loId], target=["tidak"] — primary 1:1; source=[verbId], target=["tahu"] — primary 1:1
- אַל (jussive/imperative) → "jangan": primary 1:1.
  אַל תֹּאכְלוּ → "jangan kamu makan": source=[alId], target=["jangan"] — primary 1:1; source=[verbId], target=["kamu", "makan"] — primary: "makan"; secondary: "kamu" (supplied subject pronoun)
- אֵין/אַיִן (existential) → "tidak ada": fixed phrase, both words primary 1:N.
  אֵין מֶלֶךְ → "tidak ada raja": source=[einId], target=["tidak", "ada"] — both primary; source=[melekId], target=["raja"] — primary 1:1
  Pronominal suffixes on אֵין (e.g., אֵינֶנּוּ) → suffix word-part fuses per PRONOMINAL SUFFIXES.

No discontiguous-verb caveat is needed — Indonesian "tidak"/"jangan" always sits directly before the verb, so the negation record and the verb record never interleave the way French's ne...pas does.\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

- Adjectival: align to Indonesian adjective or participial modifier — primary.
- Substantive with article word-part: article → generic head noun "orang"/"orang-orang" primary 1:1 WHEN the translation supplies an explicit head noun; "yang" secondary to the participle. When the translation uses bare "yang" with no separate head noun, the article has no target correspondent at all (Branch B, absorbed) — "yang" remains secondary to the participle regardless.
  הַשֹּׁמֵר "orang yang menjaga": source=[articlePart], target=["orang"] — primary 1:1; source=[participleId], target=["yang", "menjaga"] — primary: "menjaga"; secondary: "yang"
  Bare form, no head noun: שֹׁמֵר (anarthrous) "yang menjaga": source has no article token; source=[participleId], target=["yang", "menjaga"] — primary: "menjaga"; secondary: "yang"
- Verbal (predicative): Indonesian aspect auxiliary ("sedang"/"telah"/"sudah") secondary; main verbal element primary.
  יֹשֵׁב "sedang duduk": source=[participleId], target=["sedang", "duduk"] — primary: "duduk"; secondary: "sedang"
- Periphrastic (participle + explicit הָיָה): הָיָה → Indonesian existential/copula auxiliary ("ada"/"telah"), separate primary record; participle → main verb, primary.
  source=[hayahId], target=["telah"] — primary 1:1
  source=[participleId], target=["duduk"] — primary 1:1\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Infinitive construct with לְ
Indonesian has no distinct infinitive form or marker (unlike English "to") — the ordinary verb is primary alone, whether or not לְ is present as a separate word-part.
  רָצָה לָלֶכֶת → "ingin pergi": source=[verbPart], target=["pergi"] — primary 1:1 (no "to"-equivalent secondary)
Purposive לְ with a distinct correspondent → "untuk" primary to the preposition word-part; infinitive primary to the verb.
  הֵחֵל לְדַבֵּר → "mulai untuk berbicara": source=[lePrepPart], target=["untuk"] — primary; source=[verbPart], target=["berbicara"] — primary

### Purpose/temporal constructions (בְּ/לְ + infinitive) → finite clause, not a nonfinite form
Indonesian has no participle or gerund-like nonfinite form for this construction. Hebrew's בְּ + infinitive ("while/when X-ing") instead renders as an ordinary finite clause introduced by "ketika"/"saat"/"waktu" (when/while) — the same mechanism NT Indonesian uses for ἐν τῷ + infinitive. Treat the preposition word-part as the correspondent to the conjunction, primary; supplied subject pronoun secondary to the verb per BASE_BLOCK.
  בְּשָׁמְעוֹ → "ketika ia mendengar":
    source=[bePrepPart], target=["ketika"] — primary
    source=[sufPart], target=["ia"] — primary (suffix marks the subject; fuses only when attached directly to a noun/preposition/verb as a clitic — here it surfaces as an independent pronoun since Indonesian finite clauses take a free-standing subject)
    source=[verbPart], target=["mendengar"] — primary

### Infinitive absolute (cognate emphasis)
Infinitive absolute → Indonesian emphasis word ("sungguh"/"pasti"): primary 1:1. Finite verb → main Indonesian verb: primary.
  מוֹת תָּמוּת → "engkau pasti akan mati":
    source=[infAbsId], target=["pasti"] — primary 1:1
    source=[verbId], target=["engkau", "akan", "mati"] — primary: "mati"; secondary: "engkau", "akan"
  Absorbed without separate Indonesian word → infinitive absolute secondary to finite verb, or NEQ if definitively untranslated.\
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

IND_OT_CONFIG = LanguagePromptConfig(
    language_code="ind",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_ot_language(IND_OT_CONFIG)
