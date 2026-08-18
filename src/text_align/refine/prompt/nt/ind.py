"""Indonesian target-language prompt config for refine-alignment.

Examples grounded in Alkitab Terjemahan Baru (TBI) — checked against the
actual target TSV, initially on a handful of verses (Mark 1:2-9, John 1:1,
John 3:16, Matthew 1:21) and later re-verified at full-corpus scale
(ARTICLES, NEGATION, PARTICIPIAL) cross-checked against KKHv0 — see
docs/alignment-principles-nt.ind.md's Cross-translation methodology note.

Key differences from the Romance-language configs (por.py/spa.py/fra.py):
  BASE_BLOCK    — fused possessive/object clitics: singular Greek possessive
                  pronouns (μου/σου/αὐτοῦ) fuse onto their head noun/preposition
                  as ONE Indonesian token (rumah-Ku, kepada-Nya) — both Greek
                  tokens primary, sharing the single target token (N:1), unlike
                  Portuguese/Spanish's occasional preposition+pronoun fusion.
                  Plural possessives (kami/kita/mereka) never fuse — normal 1:1.
                  No indefinite article at all (bare noun default, no
                  secondary needed). Articles overwhelmingly have NO target
                  correspondent (Branch B is the default, not the exception);
                  Branch A ("itu"/"ini") is the minority anaphoric/demonstrative
                  case. "yang" is the universal relativizer/linker (substantive
                  participles, attributive adjectives, relative clauses) —
                  always secondary to what it introduces, per the qui/que/che
                  precedent from French/Spanish/Portuguese.
  PASSIVE_BLOCK — TWO distinct passive strategies: di- prefix (direct/action
                  passive, ONE fused word, no auxiliary at all — simpler than
                  every Romance config) vs. ter- + "ada" (resultative/stative
                  passive, used for perfect-type Greek passives like γέγραπται).
  PARTICIPLE_BLOCK — "yang" pattern for substantive participles, with or
                  without an explicit head noun ("orang(-orang)"); a third
                  strategy, "barangsiapa"/"siapa", for generic/gnomic
                  reference ("whoever does X") — confirmed against KKHv0,
                  which uses different lexemes for the same slot.
  INFINITIVE_BLOCK — no distinct infinitive form at all (bare verb primary);
                  no gérondif/participle either — the articular/temporal
                  infinitive renders as an ordinary finite clause with
                  "ketika"/"saat" instead.
  NEGATION_BLOCK — ordinary clausal negation is contiguous (tidak/jangan +
                  verb), but οὐκέτι/μηκέτι ("no longer") is a real exception:
                  the verb regularly separates "tidak"/"bukan" from "lagi".
                  "bukan" (not "tidak") negates nominal/copular predicates.
                  "belum" is a single lexeme for "not yet".

AUTOS_BLOCK, COMPARATIVE_BLOCK, CONDITIONAL_BLOCK, HOTI_BLOCK, IMPERSONAL_BLOCK,
and VERBAL_ASPECT_BLOCK are imported unchanged from eng.py, matching the
precedent set by por.py/spa.py/fra.py for blocks with no real language-specific
mechanics to encode.
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
# Indonesian-specific prompt blocks
# ---------------------------------------------------------------------------

BASE_BLOCK = """\
You are refining word-level alignments between a Bible translation and its Greek source
text (SBLGNT).

## ALIGNMENT DIRECTION
Alignments map translation → source: each record asks what Greek word(s) are behind this translation word.

## ALIGNMENT PHILOSOPHY
Alignments are generous: include case-implied prepositions, morphologically-implied pronouns, and context-implied articles. Do not restrict to strict lexical equivalents.
Prefer one record per source token — split rather than group. Create separate records whenever source tokens can each independently map to distinct target tokens. Combine into N:M records only when tokens form an inseparable semantic unit (idiom) or target words cannot be individually assigned to separate source tokens. When in doubt, split.
Grammar-required translation words (implied pronoun, aspect particle, modal helpers ["bisa," "mungkin," "akan"], reinstated demonstrative) are secondary to the source token whose grammar requires them — not NEQ. NEQ is for words with no source-language grammatical anchor.

## TOKEN ROLES

primary — direct lexical/semantic connection to the Greek token
secondary — exists only because of the Greek token's morphology (person, number, case, aspect, voice); no separate Greek word
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- Subject pronoun — Indonesian verbs don't inflect for person/number; pronoun use is discourse-driven, not grammar-driven: supplied when a clause introduces/switches subject, dropped on topic continuity (no Greek pronoun needed either way).
  ἦλθεν → "ia datang" (new subject): "datang" primary; "ia" secondary
  Coordinate continuation ("...tampil...dan menyerukan"): no repeated pronoun — none expected.

- Aspect/tense particle — a separate particle, not inflection: "akan" (future), "sudah"/"telah" (perfect), "sedang" (progressive). Secondary to the verb when it reflects Greek's own tense/aspect with no separate Greek word.
  ἐδίδασκεν → "sedang mengajar": "mengajar" primary; "sedang" secondary

- No infinitive marker — λαβεῖν → "mengambil": primary alone; no distinct infinitive form or marker.

- No indefinite article — ἄνθρωπος → "orang": primary alone. Only "seorang"/"sebuah" (lit. "one [classifier]"), when supplied for emphasis/specificity, is secondary.

- Fused possessive/object clitic — singular possessive/object pronouns (-ku, -mu, -nya) hyphenate onto the noun/preposition/verb as ONE target token (rumah-Ku, kepada-Nya, mengasihi-nya); both Greek tokens primary, sharing it. Plural (kami, kita, kalian, mereka) never fuses — normal 1:1.
  τοὺς ὀφθαλμούς σου → "matamu": [ὀφθαλμούς, σου]→["matamu"] — both primary
  τοὺς ὀφθαλμοὺς αὐτῶν → "mata mereka" (plural, no fusion): [αὐτῶν]→["mereka"] primary 1:1; [τούς, ὀφθαλμούς]→["mata"] primary 1:1

- Periphrastic rendering — 1 Greek token → several Indonesian words: lexical words primary, grammatical connectors secondary. Often reverses for Indonesian's rich verbal morphology (me-, memper-, ber-, ter-, di-): one Indonesian word covers what needed a periphrasis in English/Romance — align 1:1.
  κυριεύει → "menguasai": primary 1:1
  καρποφορέω → "berbuah": primary 1:1
  γινώσκουσιν (dative substantive participle) → "kepada orang-orang yang mengenal": "mengenal" primary; "kepada", "orang-orang", "yang" secondary (see ARTICLES/PARTICIPIAL CONSTRUCTIONS)
  φιλαδελφία → "kasih persaudaraan": both primary

## NEQ (NON-EQUIVALENT)

NEQ = positive claim that no correspondence exists. Never use as fallback for uncertainty.
Unrecorded = correspondence not determined (normal). NEQ records must not include meta.secondary.

- Certain no correspondent → NEQ (source or target empty, meta.rel: "NEQ")
- Uncertain → leave unrecorded

Greek articles (POS T-*): NEVER NEQ — either secondary to head, or absorbed with no target word at all. See ARTICLES → Branch B (the default for Indonesian).
Supplied copula ("adalah"/"ialah") with no Greek εἶναι → NEQ target.

## SURFACE FORM DIFFERENCES
Tense, voice, number, and aspect differences do not prevent alignment. Align on lexical/semantic correspondence, not surface form.

## CANDIDATES
Automated suggestions — no secondary classification, no idiom flags, some wrong. Restructure, split, merge, or discard freely. Word order does not constrain alignment.

## ARTICLES

For every Greek article (POS T-*): does the translation supply a distinct correspondent ("itu"/"ini", or a generic head noun for a substantive participle)?
DEFAULT → Branch B: no separate word — article secondary to the noun's own record, no target word required.
MINORITY → Branch A: primary 1:1, when the translation does supply a distinct word.

### Branch A — distinct Indonesian correspondent

- "itu" (distal/anaphoric) or "ini" (proximal): 1:1 primary; noun its own record. Typically a SECOND+ mention, not the first.
  ὁ λόγος (first mention) → "Firman" (Branch B, no target word)
  ὁ λόγος (anaphoric) → "Firman itu": [ὁ]→["itu"] primary 1:1; [λόγος]→["Firman"] primary 1:1

- "orang"/"orang-orang" (substantive participle, explicit head noun): article primary 1:1; "yang" secondary to the participle (see PARTICIPIAL CONSTRUCTIONS).
  τοῖς πιστεύουσιν → "kepada orang-orang yang percaya": [τοῖς]→["orang-orang"] primary 1:1; [πιστεύουσιν]→["yang", "percaya"] primary "percaya", secondary "yang"; "kepada" secondary (dative case-implied)

### Branch B — no correspondent → secondary, no target word

Apply per article.
- Bare articular noun: [τήν, χεῖρα]→["tangan"] — "tangan" primary; [τήν] secondary, no target word
- Attributive adjective (double article): Indonesian links noun+adjective with "yang" instead of repeating the article. First article → Branch A/B per the noun; second article AND "yang" (if present) both secondary to the adjective — "yang" is a grammatical linker, not lexical.
  τὴν γῆν τὴν καλήν → "tanah yang baik": [τήν₁, γῆν]→["tanah"] primary, [τήν₁] secondary no target word; [τήν₂, καλήν]→["yang", "baik"] primary "baik", secondary "yang"
- Proper name: Indonesian never uses an article. ὁ Ἰησοῦς → "Yesus": [Ἰησοῦς]→["Yesus"] primary; [ὁ] secondary, no target word

### Possessive pronoun
See FUSED POSSESSIVE/OBJECT CLITIC in TOKEN ROLES — singular fuses (both primary); plural stays 1:1.

### Anarthrous noun
See TOKEN ROLES → "No indefinite article".

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "sehingga": primary; or "sampai akhirnya": all primary if rendered periphrastically).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  μὴ γένοιτο — optative negation, typically a fixed idiom ("Sekali-kali tidak!" / "Tidak akan pernah!") with no token-level mapping — use is_idiom: true. Prefer standard records only if the translation is literal enough for granular alignment (μή → negation; γένοιτο → verb).
    [μή, γένοιτο]→["Sekali-kali", "tidak"] — is_idiom: true\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

### Direct/action passive (di- prefix)
Greek passive verb → Indonesian di- prefix fused directly onto the verb root: ONE token, primary 1:1 — no separate auxiliary needed at all.
  ἐβαπτίσθη → "dibaptis": [ἐβαπτίσθη]→["dibaptis"] primary 1:1
Agent phrase (ὑπό + genitive): "oleh" (by) primary to ὑπό when present.
  ἐβαπτίσθη ὑπὸ Ἰωάννου → "dibaptis oleh Yohanes": [ἐβαπτίσθη]→["dibaptis"] primary; [ὑπό]→["oleh"] primary; [Ἰωάννου]→["Yohanes"] primary

### Resultative/stative passive (ter- + "ada")
Greek perfect passive (γέγραπται-type, a resulting state rather than the action itself) often renders with ter- + the existential auxiliary "ada" (there is/exists), rather than di-: "ada" secondary; the ter-verb primary.
  γέγραπται → "ada tertulis": [γέγραπται]→["ada", "tertulis"] primary "tertulis", secondary "ada"

### Supplied subject pronoun
Same rule as TOKEN ROLES: secondary when introducing/switching subject with no Greek pronoun; none expected on topic continuity.
  ἐβαπτίσθη (new subject) → "Ia dibaptis": [ἐβαπτίσθη]→["Ia", "dibaptis"] primary "dibaptis", secondary "Ia"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Indonesian has no distinct infinitive form — the ordinary verb is primary alone, no separate marker.
  θέλω ἐλθεῖν → "mau datang": source=[ἐλθεῖν], target=["datang"] — primary 1:1

### Purpose infinitive with "untuk"
"untuk" carries purpose force → secondary to the infinitive when purpose is already in the Greek verb; primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
  ἦλθεν σῴζειν → "datang untuk menyelamatkan": source=[σῴζειν], target=["untuk", "menyelamatkan"] — primary: "menyelamatkan"; secondary: "untuk"

### Articular/temporal infinitive → finite clause, not a nonfinite form
No participle/gérondif-like form for this construction. Greek's ἐν τῷ + infinitive ("while/when X-ing") renders as a finite clause with "ketika"/"saat"/"waktu". ἐν+τῷ fuse as one correspondent to the conjunction, both primary (parallel to the fused-clitic pattern in TOKEN ROLES) — no separate secondary needed for the article.
  ἐν τῷ σπείρειν αὐτόν → "ketika ia menabur": [ἐν, τῷ]→["ketika"] both primary; [αὐτόν]→["ia"] primary; [σπείρειν]→["menabur"] primary

### Indirect discourse
Supplied "bahwa" (that) introducing an indirect statement → secondary to the governing verb, not the infinitive.
  λέγει αὐτὸν εἶναι → "berkata bahwa ia adalah": [λέγει]→["berkata"]; [αὐτόν]→["ia"]; [εἶναι]→["bahwa", "adalah"] primary "adalah", secondary "bahwa"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- → "supaya"/"agar" (purpose/result conjunction): conjunction primary; verbs/content words align normally.
- → bare "untuk" + verb (purpose infinitive rendering): "untuk" primary to ἵνα — not secondary to the verb.
- No correspondent → NEQ source (only when certain no element expresses purpose/result force).

  ἵνα σωθῇ → "supaya diselamatkan": [ἵνα]→["supaya"] primary 1:1
  ἵνα σῴζῃ → "untuk menyelamatkan": [ἵνα]→["untuk"] primary (purpose marker); [σῴζῃ]→["menyelamatkan"] primary\
"""

NEGATION_BLOCK = """\
## NEGATION

Ordinary clausal negation is contiguous (tidak/jangan immediately before the verb).

- οὐ/οὐκ/οὐχ/μή → "tidak" (indicative) / "jangan" (prohibitive/imperative): primary 1:1. Verb gets its own record.
  οὐκ ἔρχεται → "tidak datang": [οὐκ]→["tidak"] primary 1:1; [ἔρχεται]→["datang"] primary 1:1
- Nominal/copular predicate negated → "bukan" instead of "tidak" (lexical choice by predicate type, not a different Greek construction), still primary 1:1.
  οὐκέτι εἰσὶν δύο → "mereka bukan lagi dua": "bukan" chosen because the predicate ("dua") is nominal — see Compound negation for the "lagi" split.

### Compound negation
- οὐκέτι/μηκέτι ("no longer") is DISCONTINUOUS, not "tidak lagi" as one unit: the verb/predicate regularly separates "tidak"(or "bukan") from "lagi" — both still primary to the single Greek token, not necessarily adjacent.
  οὐκέτι δύναται...εἰσελθεῖν → "tidak dapat lagi ... masuk": [οὐκέτι]→["tidak", "lagi"] both primary, non-adjacent.
- οὔπω/μήπω ("not yet") → "belum": primary 1:1 — a single dedicated lexeme, no periphrasis needed.
- οὐδέ/μηδέ ("and not"/"neither"/"nor") → "dan tidak"/"pun tidak": primary
- οὐδείς/μηδείς ("nobody"/"no one"/"nothing") → "tidak seorang pun"/"tiada": primary

### Emphatic negation (οὐ μή)
Both particles primary to the single emphatic expression.
  οὐ μή + subjunctive → "sekali-kali tidak"/"tidak akan pernah": [οὐ, μή]→["sekali-kali", "tidak"] both primary\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adverbial (circumstantial)
Introductory conjunction/adverb secondary; supplied subject pronoun secondary (see TOKEN ROLES).
  ἀκούσας → "ketika ia mendengar": [ἀκούσας]→["ketika", "ia", "mendengar"] primary "mendengar", secondary "ketika", "ia"

### Genitive absolute
Align each element to its correspondent; introduced conjunctions/adverbs and supplied subject pronoun secondary to the participle.
  αὐτοῦ λαλοῦντος → "ketika ia sedang berbicara": [αὐτοῦ]→["ia"] primary; [λαλοῦντος]→["ketika", "sedang", "berbicara"] primary "berbicara", secondary "ketika", "sedang"

### Substantive — "yang" pattern
Explicit head noun ("orang"/"orang-orang") supplied → article primary 1:1, "yang" secondary to the participle — see ARTICLES → Branch A for the worked example. Bare "yang" with no head noun → article absorbed (Branch B), "yang" still secondary.
  ὁ πιστεύων → "yang percaya": [ὁ] no target correspondent; [πιστεύων]→["yang", "percaya"] primary "percaya", secondary "yang"

### Substantive, generic/gnomic — "barangsiapa"/"siapa" pattern
Generic/gnomic referent ("whoever does X," not a specific individual) → "barangsiapa"/"siapa"/"siapa pun" (or "orang yang"/"siapa yang") instead of "yang" — same slot, lexical variant not a different construction. Article absorbed (Branch B).
  ὁ φιλῶν πατέρα → "Barangsiapa mengasihi bapa": [ὁ] no target correspondent; [φιλῶν]→["Barangsiapa", "mengasihi"] primary "mengasihi", secondary "Barangsiapa"
  ὁ ἔχων ὦτα → "Siapa bertelinga": [ὁ] no target correspondent; [ἔχων]→["Siapa", "bertelinga"] primary "bertelinga", secondary "Siapa"

### Discourse particle adjacent to participle
δέ/καί/οὖν near participle with no correspondent → NEQ source (only when certain).\
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

IND_CONFIG = LanguagePromptConfig(
    language_code="ind",
    base_block=BASE_BLOCK,
    conditional_blocks=CONDITIONAL_BLOCKS,
    block_order=BLOCK_ORDER,
    forced_inclusions=FORCED_INCLUSIONS,
)

register_nt_language(IND_CONFIG)
