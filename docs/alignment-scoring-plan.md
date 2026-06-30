# Alignment Scoring Plan

*Working document — subject to revision.*

---

## 1. Purpose

The current retry trigger is a single threshold: re-run a verse if it has more than
`--min-unaligned-src` uncovered source tokens. This catches one failure mode (gaps)
but misses others: NEQ overuse, over-grouping of tokens into single records (smearing),
and translation-side gaps.

This plan describes a composite scoring function that assigns a **penalty score** to
each aligned verse and triggers a retry when the score exceeds a configurable threshold.
The scorer runs on existing JSON output — no LLM calls required.

Goals:
- Replace or supplement the single-threshold coverage check with a multi-signal penalty
- Enable a two-pass workflow: cheap model first → score → retry low-scoring verses with a
  better model
- Produce per-verse scores that can be stored for later analysis

---

## 2. Two-Tier Architecture

### Tier 1 — Structural Validity (pre-scoring, hard errors)

These checks are binary: any violation means the record is malformed output. They should
be caught before scoring and logged as errors rather than contributing to a penalty
gradient.

| Check | Condition |
|---|---|
| All-secondary source | `set(record["source"]) ⊆ set(meta.secondary.source)` |
| All-secondary target | `set(record["target"]) ⊆ set(meta.secondary.target)` |
| Empty source list | `len(record["source"]) == 0` |
| Empty target list | `len(record["target"]) == 0` |

Invalid records are skipped by the scorer and counted separately
(`structural_errors: N` in verse metadata).

### Tier 2 — Quality Scoring (penalty signals)

Five additive penalty signals, each normalized to [0, 1], combined with configurable
weights into a single verse penalty score. Higher = worse.

---

## 3. Scoring Signals

### Signal 1 — Weighted Source Coverage

**What it catches:** source tokens (Greek/Hebrew) left unaligned or un-NEQ'd.

**Why weighted:** an unaligned verb or noun is far more significant than an unaligned
article or particle.

**Computation:**

```
covered_src = tokens appearing in any record's source list OR in nonEquivalent.source
uncovered_src = all source tokens − covered_src

weighted_uncovered = Σ pos_weight(tok) for tok in uncovered_src
weighted_total     = Σ pos_weight(tok) for tok in all_src_tokens

signal_1 = weighted_uncovered / weighted_total  (0 if no source tokens)
```

POS weights (initial values — tune against gold data):

| POS class | Weight |
|---|---|
| Verb | 1.0 |
| Noun, proper noun | 1.0 |
| Adjective, adverb | 0.8 |
| Pronoun | 0.5 |
| Preposition (explicit) | 0.4 |
| Conjunction, particle | 0.2 |
| Article | 0.1 |

POS is available from MACULA/SBLGNT token metadata. If POS is unavailable for a token,
default weight = 0.6.

**Implementation note:** POS lookup requires the source token data already loaded during
`refine-alignment`. Store POS alongside token IDs in verse input so the scorer can
operate on JSON output alone without reloading the source corpus.

### Signal 2 — Translation Content-Word Coverage

**What it catches:** translation tokens left unaligned that aren't function words — the
source-side may look fine while the target side has gaps.

**Computation:**

```
content_tgt = translation tokens NOT in stop_words AND NOT in any record's target list
              AND NOT in nonEquivalent.target
total_content_tgt = translation tokens NOT in stop_words

signal_2 = len(content_tgt) / total_content_tgt  (0 if no content tokens)
```

Stop-word lists are per language (ISO 639-3). Source: **`stopwordsiso`** (PyPI) —
60+ languages, lightweight (74 KB), uses ISO 639-1 codes. A small lookup dict maps
ISO 639-3 → ISO 639-1 (`eng→en`, `por→pt`, `spa→es`, `fra→fr`, `swa→sw`, `guj→gu`,
`nep→ne`, etc.). For languages with no `stopwordsiso` coverage (Tok Pisin, Bislama,
Lingala, and any other uncovered language), fall back to an empty set — the safe
direction is to penalise gaps rather than hide them.

Because false positives (treating a content word as a stopword and suppressing a real
gap) are worse than false negatives, the raw `stopwordsiso` list is intersected with a
small curated core of unambiguously function words. Words that appear in stopword
packages but carry lexical content in some contexts ("say," "go," "come," "make,"
"know") are excluded from the intersection.

The curated intersection is defined in `refine/scoring_stopwords.py` as a
`frozenset[str]` per ISO 639-3 code, constructed at module load time from
`stopwordsiso` data.

### Signal 3 — NEQ Overuse

**What it catches:** model using NEQ as a fallback for uncertainty rather than as a
positive non-equivalence claim.

**Computation:**

```
neq_src_count  = len(nonEquivalent.source)
total_src      = len(all source tokens in verse)

raw = neq_src_count / total_src
baseline = 0.10  (configurable; typical NEQ rate for well-aligned verses)

signal_3 = max(0, raw − baseline) / (1 − baseline)
```

This gives 0 penalty up to the baseline rate and scales to 1 only if every source token
is NEQ'd.

### Signal 4 — Token Smearing (N:M over-grouping)

**What it catches:** tokens that should be separate alignments grouped into a single
record — the Mistral/cheap-model failure mode where e.g. an adjective+noun phrase is
one record instead of two.

**Definition of a smeared record:**

```
primary_src = len(source) − len(meta.secondary.source)
primary_tgt = len(target) − len(meta.secondary.target)
smeared = primary_src > 1 AND primary_tgt > 1 AND NOT meta.is_idiom
```

**Computation:**

```
smear_mass = Σ (primary_src × primary_tgt) for each smeared record
total_mass  = Σ (len(source) × len(target)) for all records  [lower bound denominator]

signal_4 = smear_mass / max(total_mass, 1)
```

Weighting by `primary_src × primary_tgt` makes a 3×3 smear worse than a 2×2.

**Adjacency boost:** if both source token IDs and target token IDs in a smeared record
are consecutive (adjacent in document order), multiply that record's contribution by 1.5
— adjacent-on-both-sides smearing almost never reflects a legitimate complex alignment.

Adjacency check: parse the word-position field from BCVWP IDs and verify
`max_pos − min_pos == len(tokens) − 1`.

### Signal 5 — Per-Verse Deviation

**What it catches:** a single verse that is anomalously bad relative to the chapter,
even if no individual signal crosses a threshold alone.

**Computation:** run signals 1–4 for all verses in the chapter first, compute chapter
means and standard deviations, then:

```
composite_1_4(verse) = weighted sum of signals 1–4

chapter_mean = mean(composite_1_4 across all verses)
chapter_std  = std(composite_1_4 across all verses)

signal_5 = max(0, composite_1_4(verse) − (chapter_mean + k * chapter_std)) / chapter_std
```

Default `k = 1.5`. This contributes 0 for verses near or below the chapter mean and a
positive penalty for outliers. Signal 5 is computed in a second pass after signals 1–4
are known for all verses.

---

## 4. Composite Score

```
penalty(verse) = w1*s1 + w2*s2 + w3*s3 + w4*s4 + w5*s5
```

Initial weights (tune against gold data):

| Signal | Weight |
|---|---|
| s1 — weighted source coverage | 0.35 |
| s2 — translation content coverage | 0.20 |
| s3 — NEQ overuse | 0.15 |
| s4 — token smearing | 0.20 |
| s5 — per-verse deviation | 0.10 |

Retry threshold: `penalty > 0.25` (configurable via `--score-retry-threshold`).

The existing `--min-unaligned-src` check becomes a special case of signal 1 (unweighted,
flat threshold). Both checks can coexist during a transition period; the scorer threshold
should eventually supersede the raw count check.

---

## 5. Implementation Plan

### 5.1 New module: `refine/scoring.py`

```
VerseScore
  verse_id: str
  signal_1: float
  signal_2: float
  signal_3: float
  signal_4: float
  signal_5: float          # filled in second pass
  composite: float         # filled in second pass
  structural_errors: int
  needs_retry: bool

score_verse(verse_records, neq, src_tokens, tgt_tokens, lang, config) -> VerseScore
  # signals 1–4 only; signal 5 requires chapter context

score_chapter(verses: list[VerseScore], config) -> list[VerseScore]
  # second pass: computes signal 5, fills composite, sets needs_retry
```

`config` is a `ScoringConfig` dataclass with weights, baseline NEQ rate, adjacency
multiplier, stop-word lists, and retry threshold — all overridable via CLI flags or YAML.

### 5.2 POS weight lookup

Add `src_pos: dict[token_id, str]` to the verse input structure passed through
`refine-alignment`. Populate from MACULA/SBLGNT token metadata at load time (already
available). Fall back to weight 0.6 for unknown tokens.

### 5.3 Stop-word lists

`refine/scoring_stopwords.py` — dict keyed by ISO 639-3 code, value is a frozenset.
Seed with English. Import language-specific additions alongside prompt modules.

### 5.4 Integration points

**`refine/coverage.py`:** `score_verse()` subsumes and extends the existing
`uncovered_tokens()` logic. Keep `uncovered_tokens()` as a thin wrapper during
transition.

**`refine/retry.py`:** Replace the `len(uncovered) > min_unaligned_src` guard with
`VerseScore.needs_retry`. Expose `--score-retry-threshold` and retain
`--min-unaligned-src` as a fallback flag (deprecated).

**`refine/retry_cli.py` / `refine/refine.py`:** Pass `ScoringConfig` through; surface
new CLI flags.

**Output JSON:** Optionally write `"score"` metadata per verse into the chapter JSON
(behind a `--write-scores` flag) for offline analysis.

### 5.5 New CLI: `score-alignment`

Standalone command that reads existing chapter JSON files and emits a TSV or JSON
report of per-verse scores — useful for auditing already-completed batches without
re-running alignment.

```
score-alignment \
  --alignment-dir output/SBLGNT-OENGB/ \
  --lang eng \
  --score-retry-threshold 0.25 \
  [--write-scores]
```

### 5.6 YAML config changes

The config loader (`config.py`) is flat — YAML keys map directly to argparse dest names.
No structural changes to the loader are needed; the two-pass workflow is handled by
adding retry-specific key variants with fallback logic in `retry_cli.py`.

**Key convention:**

| YAML key | Used by | Notes |
|---|---|---|
| `llm_provider` | `refine-alignment` | existing |
| `llm_model` | `refine-alignment` | existing |
| `reasoning_effort` | `refine-alignment` | existing |
| `retry_llm_provider` | `retry-alignment` | new; falls back to `llm_provider` if absent |
| `retry_llm_model` | `retry-alignment` | new; falls back to `llm_model` if absent |
| `retry_reasoning_effort` | `retry-alignment` | new; falls back to `reasoning_effort` if absent |
| `score_retry_threshold` | `retry-alignment`, `score-alignment` | new; default 0.25 |
| `min_unaligned_src` | `retry-alignment` | existing; deprecated once scorer is trusted |

**Fallback logic in `retry_cli.py`:** after `p.set_defaults(**config_defaults)`, resolve
the active retry model settings:

```python
# In retry_cli.py parse_args(), after p.set_defaults():
# If retry-specific keys are absent, fall back to the refine model keys.
args.llm_provider = getattr(args, "retry_llm_provider", None) or args.llm_provider
args.llm_model    = getattr(args, "retry_llm_model",    None) or args.llm_model
args.reasoning_effort = getattr(args, "retry_reasoning_effort", None) or args.reasoning_effort
```

This preserves backwards compatibility: configs that set only `llm_*` continue to work
unchanged for both refine and retry. Configs that set `retry_llm_*` override only the
retry step.

**Example config snippet (two-pass workflow):**

```yaml
# First pass — cheap model for refine-alignment
llm_provider: openrouter
llm_model: deepseek/deepseek-v4-pro

# Second pass — better model for retry-alignment
retry_llm_provider: anthropic
retry_llm_model: claude-sonnet-4-6
retry_reasoning_effort: high

# Scoring
score_retry_threshold: 0.25
```

`example.yaml` is updated to document all new keys.

---

## 6. Tuning and Validation

Before deploying the scorer as a retry gate:

1. Run `score-alignment` against a set of manually reviewed chapters (gold standard).
2. Compare `needs_retry` predictions to known-bad verses identified by human review.
3. Adjust per-signal weights and the retry threshold to maximize recall of genuinely bad
   verses while keeping false-positive rate low (false positives = wasted retry calls).
4. Per-language baselines (especially stop-word lists and NEQ baseline rates) may need
   separate tuning for minority languages with different translation styles.

---

## 7. Open Questions

- **POS storage in output JSON:** decide whether to embed POS in chapter output at
  refinement time, or re-derive from corpus at scoring time. Embedding is faster and
  avoids a corpus dependency in `score-alignment`; re-derivation keeps the output
  leaner.
- **Signal 5 across chapters:** deviation is currently intra-chapter. Consider whether a
  cross-chapter baseline (e.g., per-book mean) would improve detection of books with
  uniformly poor alignment (where all verses look similar but all are bad).
- **Smearing threshold:** the `primary_src × primary_tgt` weighting is a first guess.
  Real data from known smeared chapters should inform whether a simpler count suffices.
- **Language-specific NEQ baselines:** the 10% baseline for signal 3 was set for English
  NT. Hebrew OT (with אֶת, waw-consecutive, particles) will have a higher natural NEQ
  rate; minority-language dynamic translations will have a higher target-side NEQ rate.
