"""Indonesian target-language prompt config for refine-alignment.

Examples grounded in Alkitab Terjemahan Baru (TBI) — checked against the
actual target TSV (Mark 1:2-9, John 1:1, John 3:16, Matthew 1:21), not
constructed from general knowledge alone.

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
                  without an explicit head noun ("orang(-orang)").
  INFINITIVE_BLOCK — no distinct infinitive form at all (bare verb primary);
                  no gérondif/participle either — the articular/temporal
                  infinitive renders as an ordinary finite clause with
                  "ketika"/"saat" instead.
  NEGATION_BLOCK — simple contiguous negation (tidak + verb), no discontiguous
                  structure; "belum" is a single lexeme for "not yet".

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

primary — direct lexical or semantic connection to the Greek token
secondary — exists only because of grammatical features in the Greek token's morphology (person, number, case, aspect, voice); no separate Greek word
other Greek token → separate record

Structural constraints: every record ≥1 primary per populated side; a lone token on a side cannot be secondary; each target token ID in exactly one record per verse.

Common secondary cases:

- Subject pronoun — Indonesian verbs never inflect for person/number, but pronoun use is discourse-driven rather than grammar-driven: a pronoun is typically supplied when a clause introduces or switches to a new subject, and dropped when a coordinate clause continues the same topic. When present with no explicit Greek pronoun backing it → secondary. When dropped (topic continuity) → none expected, leave unrecorded.
  ἦλθεν → "ia datang" (introducing/re-establishing the subject) — "datang" primary; "ia" secondary
  Coordinate continuation (same subject as prior clause, e.g. "...tampil...dan menyerukan"): no repeated pronoun — none expected.

- Aspect/tense particle — Indonesian marks tense/aspect with a separate particle rather than inflection: "akan" (future), "sudah"/"telah" (perfect), "sedang" (progressive). Secondary to the main verb when it reflects Greek's own tense/aspect morphology with no separate Greek word.
  ἐδίδασκεν → "sedang mengajar": "mengajar" primary; "sedang" secondary

- No infinitive marker — λαβεῖν → "mengambil": primary alone. Indonesian has no distinct infinitive form or marker (unlike English "to").

- No indefinite article — ἄνθρωπος → "orang": primary alone, no secondary needed (contrast Portuguese/Spanish/French's "un/una/un" secondary). Indonesian has no indefinite article by default. Only when the translation explicitly supplies "seorang"/"sebuah" (lit. "one [classifier]") for emphasis or specificity is it secondary.

- Fused possessive/object clitic — Indonesian's 1st/2nd/3rd-singular possessive and object pronouns (-ku, -mu, -nya) hyphenate directly onto the noun, preposition, or verb they attach to, forming ONE target token (rumah-Ku, kepada-Nya, mengasihi-nya). When Greek expresses this with a separate possessive pronoun or a pronoun governed by a preposition, BOTH Greek tokens are primary, sharing the single fused target token. Plural pronouns (kami, kita, kalian, mereka) never fuse — they stay separate words and align as a normal 1:1 pair.
  τοὺς ὀφθαλμούς σου → "matamu": source=[ὀφθαλμούς, σου], target=["matamu"] — both primary
  τοὺς ὀφθαλμοὺς αὐτῶν → "mata mereka" (plural — no fusion): source=[αὐτῶν], target=["mereka"] — primary 1:1; source=[τούς, ὀφθαλμούς], target=["mata"] — primary 1:1

- Periphrastic rendering — when a single Greek token is rendered by multiple Indonesian words, all words carrying lexical content are primary; purely grammatical connectors (relativizers, case markers) are secondary to the same token. Indonesian's rich verbal morphology (me-, memper-, ber-, ter-, di-) often does the reverse — rendering a Greek verb as a SINGLE Indonesian word where English/Romance needed a multi-word periphrasis; when that happens, align 1:1, no split needed.
  κυριεύει → "menguasai": primary 1:1 (compare English "exercises authority over," which needs three words)
  καρποφορέω → "berbuah": primary 1:1 (compare "bear fruit")
  γινώσκουσιν (dative substantive participle) → "kepada orang-orang yang mengenal": "mengenal" primary; "kepada", "orang-orang", "yang" secondary (see ARTICLES and PARTICIPIAL CONSTRUCTIONS)
  φιλαδελφία → "kasih persaudaraan": "kasih", "persaudaraan" both primary

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
DEFAULT (most common in Indonesian) → Branch B: no separate word at all — the noun stands bare, and the article is secondary to the noun's own record with no target word required. This is the majority case in Indonesian, unlike Portuguese/Spanish/French where an explicit article is nearly always present.
MINORITY case → Branch A: primary 1:1, when the translation does supply a distinct word.

### Branch A — article has a distinct Indonesian correspondent

- → "itu" (distal, anaphoric — referring to something already introduced) or "ini" (proximal): 1:1 primary; noun in its own record. Typically appears on a SECOND or later mention of a referent, not the first.
  ὁ λόγος (first mention) → "Firman" — no correspondent (Branch B, absorbed, no target word)
  ὁ λόγος (repeated/anaphoric mention) → "Firman itu": source=[ὁ], target=["itu"] — primary 1:1; source=[λόγος], target=["Firman"] — primary 1:1

- → "orang"/"orang-orang" (substantive participle, generic head noun supplied): article → primary 1:1; "yang" secondary to the participle (see PARTICIPIAL CONSTRUCTIONS).
  τοῖς πιστεύουσιν → "kepada orang-orang yang percaya":
    source=[τοῖς], target=["orang-orang"] — primary 1:1
    source=[πιστεύουσιν], target=["yang", "percaya"] — primary: "percaya"; secondary: "yang"
    "kepada" secondary to πιστεύουσιν (dative case-implied)

### Branch B — no distinct Indonesian correspondent → secondary, no target word

Apply to each article independently.
- Articular noun, bare in Indonesian: source=[τήν, χεῖρα], target=["tangan"] — primary: "tangan"; secondary.source: [τήν] (no target word needed)
- Attributive adjective (double article): Greek repeats the article before an attributive adjective; Indonesian instead links noun and adjective with "yang". First article (on the noun) → Branch A or B per the noun's own status; second article (before the adjective) → secondary to the adjective, and "yang" (if present) is ALSO secondary to the adjective — it is a real word but a grammatical linker, not a lexical correspondent (same treatment as qui/que/che in the other three configs).
  τὴν γῆν τὴν καλήν → "tanah yang baik":
    source=[τήν₁, γῆν], target=["tanah"] — primary: "tanah"; secondary.source: [τήν₁] (no target word)
    source=[τήν₂, καλήν], target=["yang", "baik"] — primary: "baik"; secondary: "yang"
- Article before proper name: Indonesian never uses one. ὁ Ἰησοῦς → "Yesus": source=[ὁ, Ἰησοῦς], target=["Yesus"] — primary: "Yesus"; secondary.source: [ὁ]

### Possessive pronoun
Do NOT use a separate Branch A rule here — see FUSED POSSESSIVE/OBJECT CLITIC in TOKEN ROLES above. Singular possessives fuse into one target token (both Greek tokens primary); plural possessives stay separate words (normal 1:1 pair, article/pronoun token primary to its own word).

### Anarthrous noun
No Greek article token exists, and Indonesian has no indefinite article — bare noun, no secondary needed. ἄνθρωπος → "orang": primary alone. (Contrast Portuguese/Spanish/French's obligatory "un/una/un" secondary.)

## CONJUNCTIONS AND PARTICLES
- Clear correspondent → primary. Multiple words rendering one: all primary (ὥστε → "sehingga": primary; or "sampai akhirnya": all primary if rendered periphrastically).
- No correspondent → NEQ.
- Content word vs. conjunction/particle ambiguity → content word takes priority.

## IDIOMS
meta.is_idiom: true when phrase-level correspondence has no token-level equivalent. All tokens implicitly primary; meta.secondary does not apply.
Last resort — always prefer standard records, even with loose primary matches. Use idiom only when no plausible token-level decomposition exists. Function-word-only source records (POS C-*, X-*, prepositions) are never idioms.

  μὴ γένοιτο — optative negation, typically rendered as a fixed idiom ("Sekali-kali tidak!" / "Tidak akan pernah!") with no token-level mapping — use is_idiom: true. Only prefer standard records if the translation is literal enough to allow granular alignment (μή → negation; γένοιτο → verb).
    source=[μή, γένοιτο], target=["Sekali-kali", "tidak"] — is_idiom: true\
"""

PASSIVE_BLOCK = """\
## PASSIVE VOICE

### Direct/action passive (di- prefix)
Greek passive verb → Indonesian di- prefix fused directly onto the verb root: ONE token, primary 1:1 — no separate auxiliary needed at all (contrast Portuguese/Spanish/French, which require a separate auxiliary word like "foi"/"fue"/"a été").
  ἐβαπτίσθη → "dibaptis": source=[ἐβαπτίσθη], target=["dibaptis"] — primary 1:1
Agent phrase (ὑπό + genitive): "oleh" (by) primary to ὑπό when present.
  ἐβαπτίσθη ὑπὸ Ἰωάννου → "dibaptis oleh Yohanes": source=[ἐβαπτίσθη], target=["dibaptis"] — primary; source=[ὑπό], target=["oleh"] — primary; source=[Ἰωάννου], target=["Yohanes"] — primary

### Resultative/stative passive (ter- + "ada")
Greek perfect passive (γέγραπται-type, emphasizing a resulting state rather than the action itself) often renders with the ter- prefix plus the existential auxiliary "ada" (there is/exists), rather than di-: "ada" secondary; the ter-verb primary.
  γέγραπται → "ada tertulis": source=[γέγραπται], target=["ada", "tertulis"] — primary: "tertulis"; secondary: "ada"

### Supplied subject pronoun
Same rule as BASE_BLOCK: secondary when introducing/switching subject with no Greek pronoun; none expected when dropped for topic continuity.
  ἐβαπτίσθη (new subject) → "Ia dibaptis": source=[ἐβαπτίσθη], target=["Ia", "dibaptis"] — primary: "dibaptis"; secondary: "Ia"\
"""

INFINITIVE_BLOCK = """\
## INFINITIVAL CONSTRUCTIONS

### Complementary infinitive
Indonesian has no distinct infinitive form — the ordinary verb is primary alone, no separate marker (unlike English "to").
  θέλω ἐλθεῖν → "mau datang": source=[ἐλθεῖν], target=["datang"] — primary 1:1

### Purpose infinitive with "untuk"
"untuk" carries purpose force → secondary to the infinitive when purpose is already in the Greek verb; primary to ἵνα when ἵνα is present (see ἵνα CLAUSES).
  ἦλθεν σῴζειν → "datang untuk menyelamatkan": source=[σῴζειν], target=["untuk", "menyelamatkan"] — primary: "menyelamatkan"; secondary: "untuk"

### Articular/temporal infinitive → finite clause, not a nonfinite form
Indonesian has no participle or gérondif-like nonfinite form for this construction. Greek's ἐν τῷ + infinitive ("while/when X-ing") instead renders as an ordinary finite clause introduced by "ketika"/"saat"/"waktu" (when/while). Treat ἐν and τῷ together as a fused correspondent to the conjunction, both primary (parallel to the fused-clitic pattern in TOKEN ROLES) — no separate secondary is needed for the article once it is folded into the conjunction.
  ἐν τῷ σπείρειν αὐτόν → "ketika ia menabur":
    source=[ἐν, τῷ], target=["ketika"] — both primary
    source=[αὐτόν], target=["ia"] — primary
    source=[σπείρειν], target=["menabur"] — primary

### Indirect discourse
Supplied "bahwa" (that) introducing an indirect statement → secondary to the governing verb — not to the infinitive.
  λέγει αὐτὸν εἶναι → "berkata bahwa ia adalah":
    source=[λέγει], target=["berkata"]; source=[αὐτόν], target=["ia"]
    source=[εἶναι], target=["bahwa", "adalah"] — primary: "adalah"; secondary: "bahwa"\
"""

HINA_BLOCK = """\
## ἵνα CLAUSES

- → "supaya"/"agar" (purpose/result conjunction): conjunction primary; verbs/content words align normally.
- → bare "untuk" + verb (purpose infinitive rendering): "untuk" primary to ἵνα — not secondary to the verb.
- No correspondent → NEQ source (only when certain no element expresses purpose/result force).

  ἵνα σωθῇ → "supaya diselamatkan": source=[ἵνα], target=["supaya"] — primary 1:1
  ἵνα σῴζῃ → "untuk menyelamatkan":
    source=[ἵνα], target=["untuk"] — primary (purpose marker)
    source=[σῴζῃ], target=["menyelamatkan"] — primary\
"""

NEGATION_BLOCK = """\
## NEGATION

Indonesian negation is simple and contiguous (tidak + verb) — unlike French's discontinuous ne…pas structure, and there is usually no separate auxiliary to secondary-mark.

- οὐ/οὐκ/οὐχ/μή → "tidak" (indicative) / "jangan" (prohibitive/imperative): primary 1:1. Verb gets its own record.
  οὐκ ἔρχεται → "tidak datang": source=[οὐκ], target=["tidak"] — primary 1:1; source=[ἔρχεται], target=["datang"] — primary 1:1

### Compound negation
- οὐκέτι/μηκέτι ("no longer") → "tidak lagi": both words primary — Indonesian expresses this with two words, unlike English's fused "no longer".
- οὔπω/μήπω ("not yet") → "belum": primary 1:1 — a single dedicated lexeme, no periphrasis needed.
- οὐδέ/μηδέ ("and not"/"neither"/"nor") → "dan tidak"/"pun tidak": primary
- οὐδείς/μηδείς ("nobody"/"no one"/"nothing") → "tidak seorang pun"/"tiada": primary

### Emphatic negation (οὐ μή)
Both particles primary to the single emphatic expression.
  οὐ μή + subjunctive → "sekali-kali tidak"/"tidak akan pernah": source=[οὐ, μή], target=["sekali-kali", "tidak"] — both primary\
"""

PARTICIPLE_BLOCK = """\
## PARTICIPIAL CONSTRUCTIONS

### Adverbial (circumstantial)
Introductory conjunction/adverb secondary; supplied subject pronoun secondary (see BASE_BLOCK).
  ἀκούσας → "ketika ia mendengar": source=[ἀκούσας], target=["ketika", "ia", "mendengar"] — primary: "mendengar"; secondary: "ketika", "ia"

### Genitive absolute
Align each element to its correspondent; introduced conjunctions/adverbs secondary to the participle; supplied subject pronoun secondary.
  αὐτοῦ λαλοῦντος → "ketika ia sedang berbicara":
    source=[αὐτοῦ], target=["ia"] — primary
    source=[λαλοῦντος], target=["ketika", "sedang", "berbicara"] — primary: "berbicara"; secondary: "ketika", "sedang"

### Substantive — "yang" pattern
Article → generic head noun "orang"/"orang-orang" (person/people) primary 1:1 WHEN the translation supplies an explicit head noun; "yang" secondary to the participle. When the translation uses bare "yang" with no separate head noun, the article has no target correspondent at all (Branch B, absorbed) — "yang" remains secondary to the participle regardless.
  τοῖς πιστεύουσιν → "kepada orang-orang yang percaya":
    source=[τοῖς], target=["orang-orang"] — primary 1:1
    source=[πιστεύουσιν], target=["yang", "percaya"] — primary: "percaya"; secondary: "yang"
  Bare form, no head noun: ὁ πιστεύων → "yang percaya": source=[ὁ] — no target correspondent (Branch B); source=[πιστεύων], target=["yang", "percaya"] — primary: "percaya"; secondary: "yang"

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
