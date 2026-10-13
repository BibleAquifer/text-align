# Design: `review-alignment` CLI (LLM-driven chapter review)

Status: **draft plan** — nothing implemented; build is gated on Phase 0 below. A `review-alignment` Claude Code skill and
`scripts/dump_chapter.py` already exist (interactive use); this document plans a CLI
equivalent that runs on a configurable LLM.

## Goal

A pipeline step beside `score-alignment` and `retry-alignment`. `score-alignment` catches
mechanical signals; this step catches semantic errors — wrong links, unjustified NEQs,
unaligned content words. It runs on a configurable LLM, so the reviewer can be a different
model family from the aligner, and it makes no data edits.

## Where it fits, and what it costs

Review is a **detector for errors the scorer cannot see**, not a way to improve
alignments — `retry-alignment` does that. Today only score-flagged verses are retried, so a
wrong link that is fully covered, uses no NEQ, and is not smeared is never looked at.

| Verse set | What to do | LLM calls |
|---|---|---|
| Score-flagged | Retry directly. **Do not review first** — it only adds cost. | 1 (same as today) |
| Score-passed | Review (all, or a sample) | 1 review call, small output |
| Retried | Do not re-review routinely; sample only to measure retry quality | 0 normally |

Consequences:

- **Do not chain review → retry → review by default.** That triples LLM calls on the verses
  that matter most and buys no information the score + retry loop does not already give.
- **"Just re-run everything" is not the alternative.** It costs a full refine pass,
  a blank-slate re-alignment gives no signal about which output is better, and it can
  regress verses that were already right.
- **Review should be cheaper per verse than an alignment call:** it is mostly input tokens
  (dump + rubric) with a small structured output, whereas alignment must emit every record.
  *Unmeasured — verify with `--dry-run` / usage logs before relying on it.*
- **The scarcest resource is human reviewer time**, not tokens. The real value is
  pre-triage: pointing Greek/Hebrew-literate and native-speaker reviewers at the verses
  worth reading.
- **Review also audits the scorer:** reviewing a sample of *passed* verses gives a measured
  false-negative rate for `score_retry_threshold`, and recurring findings that can be
  detected mechanically should graduate into deterministic score signals (as `article_neq`
  and `acai_unaligned` did), so the expensive step shrinks over time.
- **Do not feed review notes into the retry prompt.** Retry is blank-slate on purpose;
  passing prior output or suggestions risks the same over-weighting as the candidates path.
  Review output may select verses for retry, not steer it.

It is only worth building if review's precision is decent. If it mostly flags defensible
links it costs tokens and adds noise; that is currently unknown.

## What the code looks like today

- **`LLMClient.call_batch` is hard-wired to the alignment tool schema**
  (`_NEUTRAL_TOOL_SCHEMA`) and validates token IDs. It cannot be reused as-is for review
  output.
- **Reusable pieces:**
  - config/path derivation (`config.py`)
  - language prompt lookup (`get_nt_language_config` / `get_ot_language_config`)
  - chapter discovery and source/target loading (as in `score_alignments.py`)
  - cost estimate and usage logging (`cost_estimate.py`, `gloo_usage_log.py`)
  - Gloo streaming and backoff
- **Naming:** the `review-alignment` entry point and the existing skill share a name. Fine,
  but the skill's role has to be decided (see open questions).

## Design

### Module / entry point
- `src/text_align/refine/review_alignments.py` with `main()`.
- A `review-alignment` entry in `pyproject.toml`, mirroring `score_alignments.py`.

### Inputs
- `--config`, `--corpus`, and the same range flags as refine: `--book`, `--book-range`,
  `--chapter`, `--chapter-range`, plus `--verse-range`.
- Reviewer model keys follow the existing `retry_*` pattern: `review_llm_provider`,
  `review_llm_model`, `review_reasoning_effort`, `review_max_output_tokens`.
- `--dry-run` prints a cost estimate and makes no calls.

### Shared dump logic
- Move the formatting out of `scripts/dump_chapter.py` into an importable function
  (e.g. `refine/review_dump.py`). Both the script and the CLI use it — one source of truth.

### LLM layer
- Add `LLMClient.call_structured(system, user, schema)`: a generic forced-tool call
  returning parsed JSON, reusing the provider schema converters and backoff. The alignment
  path stays untouched.
- Response schema uses token IDs rather than free text, so results are machine-usable:
  - per verse: `verdict` (`ok` | `issues`)
  - `issues[]`: `{source_ids, target_ids, kind: wrong_link | unjustified_neq |
    unaligned_content | bad_primary, note, suggestion}`
  - `arguable[]` (capped)

### Prompt
- The rubric from `.claude/skills/review-alignment/SKILL.md` ("defensible, not
  prompt-exact", with its exclusion list) becomes its own constant in the system prompt.
- The language's base block is included for conventions only, with an explicit
  instruction not to use it as a checklist.
- Conditional blocks are included only for phenomena detected in the batch, reusing
  `detect_phenomena`.

### Batching
- N verses per call (like refine's `batch-size`). Sync only in v1; async batch is out of
  scope.

### Output
- TSV at `output/<edition>/review_YYYY-MM-DD.tsv`:
  `verse_id, verdict, kind, source_ids, target_ids, note, suggestion`.
- Terminal summary in the style of `score-alignment`: chapters reviewed, verses with
  issues, session cost.

## Phases

0. **Go / no-go (before building anything)** — use the existing skill on a handful of
   chapters that have already been hand-checked, restricted to *score-passed* verses. Does
   it find real errors the scorer missed, and at what false-positive rate? If it finds
   none, stop here. Titus 1–3 manual reviews are the first baseline.
1. **Refactor** — shared dump module, `call_structured`, tests with a fake client.
2. **CLI and report** — prompt, batching, TSV and summary, `--dry-run` cost. Default scope
   is score-passed verses, not the whole chapter.
3. **Retry hook (optional)** — `retry-alignment --from-review <tsv>` adds review-flagged
   verses to the retry set (selection only; see above).
4. **Calibration** — tune the rubric against the Phase 0 baselines; measure per-verse cost
   against an alignment call.

## Tests and docs

- **Tests** (no live API calls): dump formatting, schema and ID validation, report merge,
  a fake-client end-to-end run.
- **Docs:** README Review section, a CLAUDE.md section, the `pyproject.toml` entry.

## Open questions

1. **Retry integration in v1,** or report-only first?
2. **Default reviewer model:** per the Gloo preference, a different family than the
   first-pass model (currently `gloo-google-gemini-3.7-flash`) — e.g. a Claude or GPT model
   on Gloo?
3. **Skill's fate:** keep it for interactive reviews, or make it a thin wrapper around the
   CLI?
4. **Strictness:** severity levels, or only "report / don't report"? Severity helps triage
   but invites nitpicks.
5. **Scope per run:** whole book by default, or require an explicit chapter range to avoid
   surprise spend?

Recommendation: run Phase 0 first and build only if it finds real errors; then
report-only for v1, a different-family reviewer, and decide on the retry hook after
calibration shows how noisy the reviewer is.
