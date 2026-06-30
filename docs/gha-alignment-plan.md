# GitHub Actions Alignment Pipeline — Implementation Plan

## Goal

Run `refine-alignment` + `retry-alignment` for the full NT either locally or via
GitHub Actions, with parallel execution at chapter granularity and a simple
progress/status story.  OT alignment will use a similar approach but is deferred;
the design should not preclude it.

---

## Architecture decisions

- **From-scratch only** — no diff-migrate, sim-migrate, or ACAI-align support needed.
  `alignment_sources` and migration tooling are irrelevant for this workflow.
- **ACAI** — only needed for HTML visualization, not for alignment itself. Not checked
  out in the alignment workflow.
- **Async batch mode by default** — `--batch-mode async` submits all LLM calls for a
  chapter to the provider's batch API, then immediately blocks on `fetch-batch --wait`
  internally. The caller sees the same blocking behaviour as sync, but uses batch-API
  pricing (typically 50% cheaper for Anthropic/OpenAI) and avoids per-request rate
  limits. No separate `fetch-batch` step is needed in GHA.
- **OpenRouter is sync-only** — it raises an error on `--batch-mode async`. Pass
  `batch-mode: sync` in the workflow input when using an OpenRouter config.
- **Single repo** — all data (source TSVs, target TSVs, output JSON, HTML) lives in
  `text-align`. The Clear repo is no longer needed for alignment runs.
- **`refine-alignment` is provider-agnostic** — the GHA workflow calls the same CLI
  you'd run locally. API keys come from GHA secrets or local shell environment.
- **Chapter = unit of parallelism** — one GHA matrix job per chapter. This is the
  natural boundary: it matches the output file, `--skip-existing` skips at exactly
  the right granularity, and a timed-out job wastes at most one chapter's work.
- **refine + retry in the same matrix job** — retry depends directly on refine output
  for the same chapter, so doing both in one job avoids artifact hand-off and keeps
  per-chapter work self-contained.

---

## Per-chapter job sequence

Each matrix job runs this sequence end-to-end for its chapter:

```
1. refine-alignment  (initial pass, cheap model)
         │
         ▼
2. retry-alignment   (loop while exit code 2 — fallback model active)
   ├── exit 2 → loop back (flagged rate ≥ fallback-threshold; cheap model used)
   └── exit 0 → done   (flagged rate < fallback-threshold; retry_llm_* model used
                         for this final pass — or nothing needed)
         │
         ▼
3. upload artifact
```

The final expensive `retry_llm_*` pass happens naturally as the **last** loop iteration
that exits 0.  No explicit "one final run" step is needed.

---

## Data layout (within text-align repo)

Mirrors the Clear repo hierarchy, with `alignments_root` changed from
`C:/git/Clear` to `./data/alignments` (relative to the project root):

```
data/
  alignments/
    alignments-eng/
      data/
        targets/
          BSB/
            nt_BSB.tsv        ← copied from Clear repo
            ot_BSB.tsv
          OENGB/
            nt_OENGB.tsv
            ...
      exp/
        BSB/
          LLM-REFINED/        ← chapter JSON output (committed to git)
            SBLGNT-BSB-40-001-manual.json
            SBLGNT-BSB-40-002-manual.json
            ...
        OENGB/
          LLM-REFINED/
            ...
```

TSV files and chapter JSON files are committed directly to git — they are small text
files and don't warrant LFS.

---

## Seeding data from the Clear repo (`scripts/sync_clear_data.ps1`)

One-time (and re-runnable) sync from `C:\git\Clear` into `.\data\alignments\`:

```powershell
pwsh scripts\sync_clear_data.ps1
```

The script:
- Iterates every `alignments-???` directory in `C:\git\Clear`, skipping
  `alignments-cookiecutter` and `alignments-from-Randall`
- For each repo, robocopy copies only the files the toolchain needs:
  - `data\targets\**\nt_*.tsv`, `ot_*.tsv` — translation token TSVs
  - `data\alignments\**\SBLGNT-*-manual.json`, `WLCM-*-manual.json` — existing
    manual alignment JSONs (reference / migration source)
- Fails fast if robocopy returns exit code ≥ 8 (actual error; codes 0–7 are
  informational)
- Rewrites every `configs/*.yaml` that still contains
  `alignments_root: C:/git/Clear` → `alignments_root: ./data/alignments`

The script is idempotent: re-running it skips unchanged files and leaves
already-updated configs alone.

---

## Config change (BSB.yaml and others)

`sync_clear_data.ps1` handles this automatically. The manual equivalent is to
replace:
```yaml
alignments_root: C:/git/Clear
```
With:
```yaml
alignments_root: ./data/alignments
```

Running `refine-alignment` from the project root (`C:/git/BN-Content/text-align`
locally, or `$GITHUB_WORKSPACE` in GHA) resolves all derived paths correctly via the
existing `load_config_from_args` path derivation logic.

---

## Pieces to build

### A. `--skip-existing` in `refine-alignment`

New flag, default `false`. At the top of the chapter loop in `_process_corpus_sync`
(refine.py line 379), check whether the output file already exists:

```python
book_id, chap_num = chapter_id[:2], chapter_id[2:]
out_path = output_dir / f"{corpus_id}-{target_edition}-{book_id}-{chap_num}-manual.json"
if skip_existing and out_path.exists():
    print(f"  Chapter {chapter_id}: skipping (output exists)")
    continue
```

Also needs to thread through: `parse_args()` → `process_corpus()` →
`_process_corpus_sync()` and `_process_corpus_async()`.

Default is `false` so existing behavior is unchanged unless the flag is passed.
In GHA, always pass `--skip-existing` so a re-triggered job doesn't redo a chapter
that completed before a timeout.

### B. Exit codes for `retry-alignment`

`retry-alignment` must communicate whether the fallback model was active so that the
GHA loop knows whether to iterate again.

New exit code contract (add to `retry_cli.py:main()`):

| Exit code | Meaning |
|-----------|---------|
| 0 | No retries needed, **or** retry_llm_* model was used — done |
| 1 | Unhandled exception (Python default) |
| 2 | Fallback triggered: flagged rate ≥ `--fallback-threshold`; cheap model used — run again |

Implementation: after the fallback decision block (around line 259 of `retry_cli.py`),
stash whether the fallback was used:

```python
used_fallback = False
if retry_differs and flagged_rate >= args.fallback_threshold:
    args.llm_provider     = args._refine_llm_provider
    args.llm_model        = args._refine_llm_model
    args.reasoning_effort = args._refine_reasoning_effort
    used_fallback = True
    print(...)
```

Then at the end of `main()`, after the sync/async call returns:

```python
if used_fallback:
    sys.exit(2)
```

When `retry_differs` is `False` (only one model configured), `used_fallback` stays
`False` and the loop runs once and exits 0 — correct behavior.

### C. `scripts/nt_chapters.py` — chapter matrix and status

Reads `data/sources/SBLGNT.tsv`, counts unique verse IDs per chapter, and produces
the GHA matrix or a human-readable status report.

**Modes:**

| Invocation | Output |
|------------|--------|
| `python scripts/nt_chapters.py` | Human-readable table: book name, chapter ID, verse count, completion status |
| `python scripts/nt_chapters.py --json` | JSON array for GHA matrix input |
| `python scripts/nt_chapters.py --status --edition BSB` | Per-chapter DONE / PENDING, summary line |

**`--json` output shape** (one element per chapter or bundled entry):
```json
[
  {"id": "40001", "chapter": "40001", "label": "Matt 1 (25v)"},
  {"id": "40002", "chapter": "40002", "label": "Matt 2 (23v)"},
  ...
]
```

**`--status` logic**: check whether
`alignments-eng/exp/{edition}/LLM-REFINED/SBLGNT-{edition}-{BB}-{CCC}-manual.json`
exists for each chapter. Print a summary line:
`187/261 chapters complete, 4890/7957 verses done`.

Options:
- `--edition NAME` — required for `--status`
- `--output-dir PATH` — override the default output path derivation

### D. GHA matrix ceiling and short-chapter bundling

The NT has ~261 chapters; GHA's matrix limit is **256 jobs**. The fix is to bundle
the shortest chapters (those under ~30 verses) with an adjacent chapter into a single
job. There are enough short chapters (2 John=13v, 3 John=15v, Philemon=25v, Jude=25v,
and others) that bundling ~6–8 of them collapses the count to ≤256 comfortably.

Bundled jobs pass `--chapter-range START END` covering two adjacent chapters.
`--skip-existing` still handles re-runs correctly because it checks per output file.

`nt_chapters.py --json` encapsulates this logic: it emits 256 or fewer matrix
entries, bundling short chapters automatically.

### F. `retry-alignment` retry sidecar

After each chapter's retry pass, `retry_cli.py:main()` writes a small JSON sidecar
alongside the chapter alignment file:

```
SBLGNT-BSB-46-001-manual.retries.json
```

Content:
```json
{
  "edition": "BSB",
  "chapter_id": "46001",
  "passes": 2,
  "retried_verses": ["46001003", "46001007", "46001012"]
}
```

Written only when at least one verse was retried; skipped when `retry-alignment` finds
nothing to do.  The file is committed alongside the chapter JSON so the retry history
is available for post-hoc analysis as well as in GHA.

### G. `scripts/alignment_summary.py` — whole-run summary

Reads all chapter JSONs (and `.retries.json` sidecars when present) from the
`LLM-REFINED` directory, compares verse coverage against the source TSV, and emits a
summary.

**Usage:**

```bash
python scripts/alignment_summary.py --config BSB --corpus nt [--markdown]
```

`--markdown` emits GitHub-flavoured markdown for piping to `$GITHUB_STEP_SUMMARY`;
default is plain text for local use.

**Output (example):**

```
## Alignment Summary — BSB NT

| Metric | Value |
|--------|-------|
| Chapters complete | 258 / 261 |
| Failed chapters   | 3 |
| Verses aligned    | 7,841 / 7,957 |
| Failed verses     | 116 |
| Verses retried    | 432 |

### Failed chapters
- 40028  Matt 28
- 66020  Rev 20
- 66021  Rev 21

### Failed verses (first 20 of 116)
40001003  40003007  40005019  ...
```

Failed chapters are those where the output JSON is absent or contains zero records.
Failed verses are verses present in the source TSV but absent from (or having zero
records in) the chapter JSON.  Retried verses are the union of all `retried_verses`
arrays across `.retries.json` sidecars.

In GHA the summary renders as a formatted table directly on the workflow run page
(no log-digging required).  Run locally after `git pull` to audit a completed run.

### E. `.github/workflows/align-nt.yml`

Four-job pipeline:

```
plan ──→ warmup (cache LaBSE) ──→ refine+retry (matrix, up to 256 parallel chapter jobs) ──→ collect (commit back)
```

**Workflow inputs** (`workflow_dispatch`):

| Input | Required | Default | Purpose |
|-------|----------|---------|---------|
| `config` | yes | — | Edition config name (e.g. `BSB`) |
| `chapter` | no | — | Re-run a single chapter or range, e.g. `40013` or `40001 40002` |
| `model` | no | — | Override the model in the config YAML |
| `batch-mode` | no | `async` | `async` (batch API, cheaper) or `sync` (required for OpenRouter) |
| `max-retry-passes` | no | `5` | Max retry loop iterations before giving up |

**`plan` job**: runs `nt_chapters.py --json`. If `chapter` input is provided, emits
a single-element matrix instead of the full list.

**`warmup` job** (`needs: plan`): pre-downloads `sentence-transformers/LaBSE` (~470 MB)
into the GHA model cache so all 256 matrix jobs can restore from it rather than each
downloading the model independently.  `retry-alignment` defaults to LaBSE for its
semantic similarity check (`--semantic-model sentence-transformers/LaBSE`), so without
this step every chapter job would pay the download cost on a cold runner.

```yaml
# warmup job steps (abbreviated)
- uses: actions/cache@v4
  id: hf-cache
  with:
    path: ~/.cache/huggingface/hub
    key: hf-labse-v1
- name: Download LaBSE
  if: steps.hf-cache.outputs.cache-hit != 'true'
  run: |
    poetry run python -c "
    from sentence_transformers import SentenceTransformer
    SentenceTransformer('sentence-transformers/LaBSE')
    print('LaBSE ready')
    "
```

**`refine+retry` job** (matrix, `needs: warmup`, `fail-fast: false`, `max-parallel: 20`,
`timeout-minutes: 360`):

Each matrix job restores LaBSE from the warmup cache before running `retry-alignment`:

```yaml
- uses: actions/cache/restore@v4
  with:
    path: ~/.cache/huggingface/hub
    key: hf-labse-v1
    fail-on-cache-miss: true
```

```bash
BATCH_FLAG="--batch-mode ${{ inputs.batch-mode || 'async' }}"

# Step 1 — initial alignment
# --batch-mode async submits to provider batch API then blocks internally until
# results are fetched; no separate fetch-batch step is needed.
# --batch-mode sync can be used for OpenRouter (no batch API).
poetry run refine-alignment \
  --config ${{ inputs.config }} \
  --corpus nt \
  --chapter ${{ matrix.chunk.chapter }} \
  --skip-existing \
  $BATCH_FLAG

# Step 2 — retry loop
MAX_PASSES=${{ inputs.max-retry-passes || 5 }}
for i in $(seq 1 $MAX_PASSES); do
  poetry run retry-alignment \
    --config ${{ inputs.config }} \
    --corpus nt \
    --chapter ${{ matrix.chunk.chapter }} \
    $BATCH_FLAG
  rc=$?
  [ $rc -eq 0 ] && break           # retry model used (or nothing needed) — done
  [ $rc -ne 2 ] && exit $rc        # unexpected error — fail the job
  echo "Pass $i: fallback model used, looping..."
done
```

The `timeout-minutes: 360` cap (6 hours) gives a chapter enough time for refine +
up to 5 retry passes. Async batch processing adds latency per pass (typically minutes
to ~1 hour per pass vs. seconds per verse for sync), but trades that for cheaper API
pricing and no per-request rate-limit pressure. In practice, NT chapter batch jobs
complete well within the 6-hour window.

`retry-alignment` requires `--target-tsv-dir`; the config YAML's `alignments_root: ./data/alignments`
causes `load_config_from_args` to derive this path automatically, so no explicit flag
is needed in the workflow.  It resolves to `data/alignments/alignments-eng/data/targets/{edition}/`
relative to the checkout root.

API keys injected via env from repo secrets (`OPENROUTER_API_KEY`,
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`). Each job uploads its
output file(s) — the chapter JSON and the `.retries.json` sidecar if one was written —
as a GHA artifact named `align-{chunk.id}`.

**`collect` job** (runs after all refine+retry jobs, `permissions: contents: write`):
Downloads all per-chapter artifacts (each named `align-{chunk.id}`, containing the
chapter JSON written by that matrix job) into a single staging directory:

```yaml
- uses: actions/download-artifact@v4
  with:
    pattern: align-*
    merge-multiple: true
    path: staging/
```

Copies files from `staging/` into `data/alignments/alignments-eng/exp/{config}/LLM-REFINED/`, commits
and pushes with `github-actions[bot]` identity. Skips commit if no files changed
(idempotent).

After committing, runs `alignment_summary.py` and writes the output to
`$GITHUB_STEP_SUMMARY` so the table appears directly on the workflow run page:

```yaml
- name: Summarise results
  run: |
    poetry run python scripts/alignment_summary.py \
      --config ${{ inputs.config }} --corpus nt --markdown \
      >> $GITHUB_STEP_SUMMARY
```

The summary covers: chapters complete vs. total, failed chapters (list), verses
aligned vs. total, failed verses (count + first 20), and verses retried (from
`.retries.json` sidecars).  Failed chapters and failed verses are also visible in
the GHA log; `alignment_summary.py` can be re-run locally after `git pull` for the
same view.

---

## Execution model

```
Local (single chapter, development/testing):
  cd C:/git/BN-Content/text-align
  poetry run refine-alignment --config BSB --corpus nt --chapter 40001
  poetry run retry-alignment  --config BSB --corpus nt --chapter 40001

Local (full NT, sequential):
  poetry run refine-alignment --config BSB --corpus nt
  # then retry loop manually or via script

GHA (full NT, parallel):
  → trigger align-nt workflow with config=BSB
  → up to 256 chapter jobs run simultaneously; each does refine + retry loop
  → collect job commits results back to repo

GHA (re-run one failed/timed-out chapter):
  → trigger with config=BSB, chapter=40013
```

---

## Not in scope (for now)

- OT alignment — deferred; the same workflow structure will apply when the time comes
- `score-alignment` standalone reporting in GHA (run locally after pulling output)
- HTML visualization in GHA
- diff-migrate, sim-migrate, acai-align paths
