# text-align

Tools to create and improve word-level textual alignments of Bible translations.

Alignments map tokens in a translation to tokens in the source text (Greek NT or Hebrew OT). The direction is always **translation → source**. The format is [Scripture Burrito alignment spec v0.4](https://github.com/bible-technology/alignment-spec/blob/main/spec.md) with project-specific extensions documented in [docs/alignment-principles-nt.md](docs/alignment-principles-nt.md) (NT/Greek) and [docs/alignment-principles-ot.md](docs/alignment-principles-ot.md) (OT/Hebrew).

## The alignment workflow in a nutshell

Here is the end-to-end picture for aligning a new translation. Each step is described in detail further below.

### Step 1 — Prepare your translation TSV

The alignment tools work from word-level TSV files, not USFM directly. Use [kathairo](https://pypi.org/project/kathairo/) to convert your translation's USFM into two TSV files — one for OT, one for NT — and place them under `data/targets/<edition>/`:

```
data/targets/MYBIBLE/
    ot_MYBIBLE.tsv
    nt_MYBIBLE.tsv
```

### Step 2 — Create a config file

Copy `configs/example.yaml` to `configs/MYBIBLE.yaml` and fill in your edition ID, paths, and model choices. Almost every CLI flag can be set in this file so you don't have to repeat it on every command. At minimum you need:

```yaml
target_language: eng          # ISO 639-3 code
target_edition: MYBIBLE
alignments_root: /path/to/alignments-repo   # parent of alignments-eng/, alignments-spa/, etc.
from_scratch: true            # align without pre-existing candidates
llm_provider: gloo            # or openai / anthropic / google / openrouter / ollama
llm_model: gloo-anthropic-claude-sonnet-4.5
```

Put your API credentials in a `.env` file in the project root (copy `.env.example` as a starting point). Keys needed depend on which provider you use.

### Step 3 — First pass: refine-alignment

Run `refine-alignment` to align each chapter using an LLM. For cost reasons the first pass typically uses a fast, cheap model. Output is one JSON file per chapter in `exp/<edition>/LLM-REFINED/`.

```bash
refine-alignment --config MYBIBLE --corpus nt   # New Testament
refine-alignment --config MYBIBLE --corpus ot   # Old Testament
```

You can limit scope during testing with `--chapter 41003` (Mark 3) or `--book 41` (all of Mark).

**Choosing a model for the first pass:** Any provider works. A cheap reasoning-capable model (e.g. DeepSeek V4 Pro via OpenRouter or Gloo, or Gemini 2.5 Flash via Google) gives good coverage at low cost. Frontier models (Claude Opus, GPT-4.1) are better saved for the retry pass.

### Step 4 — Score and retry

Run `score-alignment` to audit quality without making any LLM calls. It produces a TSV report showing which verses scored poorly. Then run `retry-alignment` to re-align only the flagged verses from scratch using a higher-quality model.

```bash
# Inspect quality (no LLM cost)
score-alignment --config MYBIBLE --corpus nt --flagged-only --output scores.tsv

# Re-align flagged verses with a better model
retry-alignment --config MYBIBLE --corpus nt
```

`retry-alignment` reads `retry_llm_provider` / `retry_llm_model` from the config (if set) so the retry pass can use a different, higher-quality model than the first pass. Use `--dry-run` to preview which verses would be retried before spending any API budget.

You can loop: score → retry → score → retry until quality is satisfactory, or accept first-pass results for low-priority sections.

### Step 5 — Visualize

`render-alignment` generates per-chapter HTML files showing the alignment in a Text Alignment layout so you can browse and review the results:

```bash
render-alignment --config MYBIBLE
```

Open the generated HTML files in any browser. Each verse is a row of cells showing translation tokens above their aligned source tokens.

---

## Source texts

| Canon | Corpus | File |
|-------|--------|------|
| NT | MACULA Greek (SBLGNT) | `data/sources/SBLGNT.tsv` |
| OT | MACULA Hebrew (WLCM) | `data/sources/WLCM.tsv` |

**MACULA Greek (SBLGNT)** — The SBL Greek New Testament is copyright © 2010 Society of Biblical Literature and Logos Bible Software. Licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). The source data used here is the [MACULA Greek Linguistic Datasets](https://github.com/Clear-Bible/macula-greek) (copyright © Clear Bible, Inc.), which augment the SBLGNT with morphology, lemmas, and glosses.

**MACULA Hebrew (WLCM)** — The MACULA Hebrew Linguistic Datasets are copyright © Clear Bible, Inc. Licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). Source: [github.com/Clear-Bible/macula-hebrew](https://github.com/Clear-Bible/macula-hebrew).

## Target translation TSVs

Each target translation is represented as a pair of word-level TSV files (one for OT, one for NT) under `data/targets/<edition>/`. These files are produced by Biblica's [kathairo](https://pypi.org/project/kathairo/) library, which reads USFM or USX and produces the token-per-row TSV format the alignment tools expect.

```
data/targets/<edition>/
    nt_<edition>.tsv
    ot_<edition>.tsv
```

To add a new target translation, run kathairo against the translation's USFM source. Kathairo produces a single TSV for the whole translation; you will need to split it into OT and NT portions and place them in the appropriate directory, then create a config YAML under `configs/`.

## Installation

Requires Python ≥ 3.10. Dependencies are managed with [Poetry](https://python-poetry.org/).

```bash
poetry install
```

## Testing

```bash
poetry run pytest
```

The test suite covers the cleaner (`tests/test_clean.py`) and quality scorer (`tests/test_scoring.py`). For a quick smoke test of a specific LLM provider, pass `--chapter 41003` to `refine-alignment` to limit scope to a single chapter.

## Credentials / `.env` file

API credentials are read from environment variables. You can set them in a `.env` file in the project root — it is loaded automatically at startup.

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# then fill in the keys you need
```

`.env` is gitignored. See `.env.example` for all supported variables.

## Project config files

Each alignment project (source → target translation pair) can be described in a YAML file under `configs/`. All CLI tools accept `--config <name>` (`.yaml` extension assumed), which loads that file as argument defaults. Any argument can still be overridden on the command line.

```bash
# Run with everything from the config file
refine-alignment --config OENGB

# Override one setting on the fly
refine-alignment --config OENGB --output-dir C:/tmp/test-run
```

Copy `configs/example.yaml` as a starting point — it documents every key with comments. Keys use underscores matching argparse dest names. Path values should be absolute.

## Package layout

```
src/text_align/
├── __init__.py          # ROOT, DATAPATH, SourceidEnum, normalize_strongs, …
├── strongs.py           # Strong's number normalisation
├── stopwords.py         # Shared stopword loaders (stopwordsiso + NLTK)
├── burrito/             # Scripture Burrito data model
│   ├── AlignmentGroup.py
│   ├── AlignmentRecord.py
│   ├── AlignmentSet.py
│   ├── AlignmentType.py
│   ├── BadRecord.py
│   ├── BaseToken.py
│   ├── Manager.py
│   ├── Source.py / SourceReader
│   ├── Target.py / TargetReader
│   ├── VerseData.py
│   └── alignments.py    # AlignmentsReader, write_alignment_group
├── migrate/             # Alignment migration (see Appendix)
│   ├── models.py        # MigrateTarget, MigrateVerse
│   ├── tsv.py           # process_usfm_tsv, dump_verse_text, get_wordlist
│   ├── alignment_io.py  # load/write alignment JSON, create_new_alignments
│   ├── diff.py          # diff-migrate CLI
│   └── sim.py           # sim-migrate CLI
├── align/               # Alignment creation (see Appendix)
│   ├── acai_common.py   # AcaiEntity, matching logic, trabina, populate_alignment
│   └── acai.py          # acai-align CLI
├── refine/              # LLM-assisted alignment refinement
│   ├── source.py        # Source token loader
│   ├── prompt/          # Language-aware prompt assembly
│   │   ├── common.py    #   LanguagePromptConfig dataclass, shared assembly functions
│   │   ├── nt/          #   NT (Greek) language configs
│   │   │   ├── core.py  #     Registry, phenomenon detection, NT prompt assembly
│   │   │   ├── eng.py   #     English (auto-registered)
│   │   │   ├── por.py   #     Portuguese (auto-registered)
│   │   │   ├── spa.py   #     Latin American Spanish (auto-registered)
│   │   │   └── fra.py   #     French (auto-registered)
│   │   ├── ot/          #   OT (Hebrew) language configs
│   │   │   ├── core.py  #     Registry, phenomenon detection, OT prompt assembly
│   │   │   └── eng.py   #     English (auto-registered)
│   │   └── __init__.py  #   Public API re-export
│   ├── llm.py           # Provider-agnostic LLM call layer (OpenAI / Anthropic / Google / OpenRouter / Gloo / Ollama)
│   ├── async_batch.py   # Provider batch-API helpers (Google, OpenAI, Anthropic)
│   ├── coverage.py      # Per-verse source-token coverage evaluation (legacy)
│   ├── scoring.py       # Composite alignment quality scorer (five signals + semantic flag)
│   ├── scoring_stopwords.py  # Per-language stopword sets for scorer
│   ├── semantic.py      # Semantic similarity check (sentence-transformers/LaBSE)
│   ├── refine.py        # refine-alignment CLI
│   ├── fetch_batch.py   # fetch-batch CLI
│   ├── retry.py         # Verse merge/retry core logic
│   ├── retry_cli.py     # retry-alignment CLI
│   ├── clean.py         # Core cleaning logic (CleanResult, clean_chapter_file, run_clean_pass)
│   ├── clean_cli.py     # clean-alignments CLI
│   └── score_alignments.py  # score-alignment CLI
└── render/
    └── html.py          # render-alignment CLI
```

## Recommended workflow

The primary workflow runs a cheap/fast model over the corpus first, cleans and audits quality without any LLM calls, then re-aligns only the verses that scored below the threshold with a better model:

```bash
# 1. First pass — cheap/fast model
refine-alignment --config OENGB --corpus nt \
  --llm-provider openrouter --llm-model deepseek/deepseek-v4-pro

# 2. Clean alignment files in place (also runs automatically inside score/retry)
clean-alignments --config OENGB --corpus nt

# 3. Audit scores (no LLM call; runs clean pass internally before scoring)
score-alignment --config OENGB --corpus nt --flagged-only --output scores.tsv

# 4. Re-align flagged verses with a better model (runs clean pass internally)
retry-alignment --config OENGB --corpus nt \
  --llm-provider anthropic --llm-model claude-sonnet-4-6 --reasoning-effort high
```

The YAML config supports separate model keys for the retry pass (`retry_llm_provider`, `retry_llm_model`, `retry_reasoning_effort`, `retry_max_output_tokens`) that override the refine-phase keys in `retry-alignment`. See `configs/example.yaml`.

`retry_max_output_tokens` is particularly important when the retry pass uses an Anthropic model with extended thinking: Anthropic's `max_tokens` budget covers both thinking tokens and output tokens together, so the retry pass needs a larger budget (e.g. 16000–32000) even if the first pass uses a lean value (e.g. 4000) for cost control.

`clean-alignments` can also be run standalone at any point to inspect what the cleaner finds and fixes without triggering any LLM spend.

Use `--dry-run` with `retry-alignment` to inspect which verses would be flagged before committing to any LLM spend. Use `--batch-mode async` with any of the three frontier providers (Anthropic, OpenAI, Google) for ~50% cost reduction on `refine-alignment` and `retry-alignment`.

Two GitHub Actions workflows run the alignment pipeline in parallel — one job per chapter — with automatic LaBSE cache warm-up and result collection back to the repository:

- **`.github/workflows/align-nt.yml`** — full NT pipeline (27 books, ~260 chapters). Inputs: `config`, `model`, `batch-mode`, `max-retry-passes`. Chapter matrix is built by `scripts/nt_chapters.py`.
- **`.github/workflows/align-ot.yml`** — OT pipeline, split into four canonical sections to stay under the 256-job matrix limit. Required inputs: `config`, `section` (`law` / `history` / `poetry` / `prophets`). Chapter matrix is built by `scripts/ot_chapters.py --section <section>`. Section sizes: law 187ch, history 249ch, poetry 243ch, prophets 250ch.

Workflows can be triggered from the command line without going to github.com:

```bash
gh workflow run align-nt.yml --field config=BSB
gh workflow run align-ot.yml --field config=BSB --field section=law
```

Two helper scripts support a transitory data strategy for GHA runs, where only the minimum data needed for a given config is staged into this repo, the GHA run executes, and results are copied back out to the source alignments repo:

- **`scripts/copy-to-gha.py --config <NAME>`** — copies all target TSVs for the config's edition from the Clear alignments repo into `data/alignments/`, and patches `alignments_root` in the config YAML to `./data/alignments`.
- **`scripts/copy-from-gha.py --config <NAME>`** — copies the generated chapter JSON files (and viz, if present) from `data/alignments/` back to the Clear alignments repo, and restores `alignments_root` in the config YAML to `C:/git/Clear`.

> **Note:** These scripts are specific to the [Bible Aquifer](https://github.com/BibleAquifer) internal workflow and depend on paths and repositories (`C:/git/Clear/alignments-*`) that are not publicly available. They are not intended for general use.

## CLI tools

### Refinement pipeline

#### `refine-alignment`

Refine alignment candidates using an LLM (OpenAI, Anthropic, Google, OpenRouter, Gloo, or Ollama). Reads candidate files from the `exp/` directory, assembles a structured prompt with source and target tokens, and writes refined SB 0.4 alignment JSON applying the alignment-principles guidelines (primary/secondary, idiom flags, NEQ).

Output is **one file per chapter**: `SBLGNT-<edition>-<BB>-<CCC>-manual.json` (NT) or `WLCM-<edition>-<BB>-<CCC>-manual.json` (OT). For example, Mark 3 produces `SBLGNT-OENGB-41-003-manual.json`.

Requires the appropriate credentials in the environment:
- `OPENAI_API_KEY` for OpenAI models
- `ANTHROPIC_API_KEY` for Anthropic models
- `GEMINI_API_KEY` for Google Gemini models
- `OPENROUTER_API_KEY` for OpenRouter (access to Qwen, Kimi, GLM, Mistral, and 200+ other models via a single account)
- `GLOO_CLIENT_ID` + `GLOO_CLIENT_SECRET` for Gloo AI Studio (routes to Anthropic/OpenAI/Google)
- No credentials required for Ollama (local); set `OLLAMA_BASE_URL` to override the default `http://localhost:11434/v1`

```
refine-alignment \
  --target-language eng \
  --target-edition OENGB \
  --target-tsv-dir  path/to/alignments-eng/data/targets/OENGB \
  --output-dir      path/to/alignments-eng/exp/OENGB/LLM-REFINED \
  [--alignment-sources ACAI SIM-MIGRATED DIFF-MIGRATED MERGED FASTALIGN] \
  [--from-scratch]               # align without candidates
  [--corpora ot nt] \            # --corpus is accepted as an alias
  [--llm-provider openai]        # openai | anthropic | google | openrouter | gloo | ollama
  [--llm-model gpt-5.4-mini] \  #   openrouter: any model slug, e.g. qwen/qwen3-235b-a22b
                                 #   gloo: model ID, e.g. gloo-anthropic-claude-sonnet-4.5
                                 #   ollama: any model tag installed locally, e.g. qwen3:30b-a3b
  [--reasoning-effort high]      # none/minimal/low/medium/high
                                 #   OpenAI gpt-5.x → reasoning_effort (Responses API)
                                 #   Google gemini-3+ → thinkingLevel (ThinkingConfig)
                                 #   ignored for openrouter, gloo, and ollama (always uses chat completions)
  [--batch-size 5] \
  [--max-retries 2] \
  [--max-api-retries 4]          # retries on 429/503/ChunkedEncodingError with exponential backoff
  [--temperature 1]              # sampling temperature (default: 1); explicit value
                                 #   ensures sync and async batch calls are identical
                                 #   not applied to OpenAI reasoning models
  [--max-output-tokens 4000]     # token budget per call (default: 4000; sufficient for NT);
                                 #   use 8000 for OT with Gloo/DeepSeek (larger verses);
                                 #   use 32000 for Anthropic/OpenAI reasoning retry pass
                                 #   (both combine reasoning + output in one shared budget)
  [--batch-mode sync]            # sync (default) | async (google/openai/anthropic only)
  [--jobs-dir jobs/]             # where async job metadata is stored
```

Range filtering — all mutually exclusive:

| Flag | Format | Example |
|------|--------|---------|
| `--verse BCV` | 8-digit BBCCCVVV | `--verse 41004003` |
| `--verse-range START END` | BCV pair | `--verse-range 41004001 41004020` |
| `--book BB` | 2-digit book number | `--book 41` |
| `--book-range START END` | book pair | `--book-range 41 44` |
| `--chapter BBCCC` | 5-digit chapter | `--chapter 41003` |
| `--chapter-range START END` | chapter pair | `--chapter-range 41001 41016` |

Candidate source types (default: all — ACAI, SIM-MIGRATED, DIFF-MIGRATED, MERGED, FASTALIGN, REVISED):
- `ACAI` — entity alignments from `acai-align`
- `SIM-MIGRATED` — similarity-migrated alignments from `sim-migrate`
- `DIFF-MIGRATED` — diff-migrated alignments from `diff-migrate`
- `MERGED` — a pre-merged candidate file
- `FASTALIGN` — fast_align output
- `REVISED` — manually revised alignments

Candidates are read from `<output-dir>/../<SOURCE-TYPE>/`. Use `--from-scratch` to skip candidate loading entirely.

##### OpenRouter (sync only)

[OpenRouter](https://openrouter.ai/) provides a single OpenAI-compatible API that routes to 200+ models — DeepSeek, Qwen, Kimi, GLM, Mistral, Llama, and more — without requiring separate accounts. Set `OPENROUTER_API_KEY` and pass `--llm-provider openrouter` with any OpenRouter model slug.

Per-call cost (USD) is printed after each verse batch and a session total is printed at the end of the run.

Some models (e.g. `deepseek/deepseek-v4-pro`) do not support `tool_choice`; these are detected automatically and called without it.

```bash
# DeepSeek V4 Pro via OpenRouter (good cheap first-pass model)
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider openrouter --llm-model deepseek/deepseek-v4-pro

# Qwen 3 235B via OpenRouter
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider openrouter --llm-model qwen/qwen3-235b-a22b

# Kimi K2 via OpenRouter
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider openrouter --llm-model moonshotai/kimi-k2
```

##### Gloo AI Studio (sync only)

[Gloo AI Studio](https://studio.ai.gloo.com) is a faith-oriented AI platform that routes to Anthropic, OpenAI, and Google models through a single API. Authentication uses OAuth2 client credentials (1-hour token, auto-refreshed). Set `GLOO_CLIENT_ID` and `GLOO_CLIENT_SECRET` and pass `--llm-provider gloo` with a full Gloo model ID.

Gloo routes through Cloudflare, which enforces a ~100 s timeout on the first response byte. To avoid 504 gateway errors on longer generations, the Gloo provider uses **SSE streaming** — responses are received as a stream of chunks rather than a single response, so the connection stays alive throughout generation. `ChunkedEncodingError` (server drops stream mid-generation) is retried automatically with exponential backoff. If a multi-verse batch exhausts all retries, the tool falls back to submitting each verse individually rather than aborting the chapter.

```bash
# DeepSeek V4 Pro via Gloo (good cheap first-pass model)
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider gloo --llm-model gloo-deepseek-v4-pro

# Claude Sonnet via Gloo
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider gloo --llm-model gloo-anthropic-claude-sonnet-4.5

# GPT-4.1 Mini via Gloo
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider gloo --llm-model gloo-openai-gpt-4.1-mini

# Gemini 2.5 Flash via Gloo
refine-alignment --config OENGB --chapter 41003 \
  --llm-provider gloo --llm-model gloo-google-gemini-2.5-flash
```

Credentials are available from the [Gloo AI Studio dashboard](https://studio.ai.gloo.com).

##### Ollama (local, sync only)

[Ollama](https://ollama.com) runs models locally and exposes an OpenAI-compatible API. No API credentials are required. Install Ollama, pull a model, and pass `--llm-provider ollama` with the model tag.

The default base URL is `http://localhost:11434/v1`. To point at a different OpenAI-compatible local server (e.g. `mlx_lm.server` for faster Apple Silicon inference), set `OLLAMA_BASE_URL` in your `.env` file — no code changes needed.

Validate tool-call reliability with a single-verse smoke test before committing to a full chapter run:

```bash
# Pull a model (one-time setup)
ollama pull qwen3.6:35b

# Smoke test: Mark 4:3
refine-alignment --config OENGB --verse 41004003 \
  --llm-provider ollama --llm-model qwen3.6:35b
```

Async batch mode is not supported for Ollama — use `--batch-mode sync` (the default).

##### Async batch mode

Pass `--batch-mode async` to submit all LLM calls to the provider's Batch API (~50% cost reduction, up to 24h turnaround) instead of making synchronous requests. The job is submitted and a metadata file is written to `--jobs-dir` (default `jobs/{provider}/`); the process then exits. Retrieve results with `fetch-batch`.

Supported for: `google`, `openai`, `anthropic`. **Not supported for `openrouter`, `gloo`, or `ollama`** — use `--batch-mode sync` with those providers.

```bash
# Submit (Google)
refine-alignment --config OENGB --book 41 \
  --llm-provider google --llm-model gemini-2.0-flash-001 \
  --batch-mode async

# Submit (OpenAI)
refine-alignment --config OENGB --book 41 \
  --llm-provider openai --llm-model gpt-5.4-mini \
  --batch-mode async

# Submit (Anthropic)
refine-alignment --config OENGB --book 41 \
  --llm-provider anthropic --llm-model claude-haiku-4-5-20251001 \
  --batch-mode async
```

#### `fetch-batch`

Retrieve results from an async `refine-alignment` or `retry-alignment` batch job and write the chapter output files.

```
fetch-batch <job-metadata-file> [--poll] [--wait] [--wait-interval SECONDS]
```

| Flag | Behaviour |
|------|-----------|
| *(none)* | Fetch once; exit with error if job not yet complete |
| `--poll` | Print current status (with request counts for OpenAI/Anthropic) and exit |
| `--wait` | Block, printing progress each `--wait-interval` seconds (default 60) |
| `--cancel` | Request cancellation of the job and exit |

For OpenAI and Anthropic, `--poll` and `--wait` display request-level progress derived from the batch object's `request_counts`, e.g.:

```
Batch batch_abc123: in_progress  47/200
Batch batch_abc123: in_progress  118/200, 2 failed
Batch batch_abc123: completed
```

Google exposes only a coarse state enum (`JOB_STATE_PENDING` / `JOB_STATE_RUNNING` / `JOB_STATE_SUCCEEDED`), so its output remains state-only.

For retry jobs (submitted by `retry-alignment --batch-mode async`), `fetch-batch` merges the new verse records into existing chapter files rather than writing fresh ones. The job metadata file identifies retry jobs via `"job_type": "retry"`.

#### `clean-alignments`

Validates and repairs chapter JSON alignment files **in place**. Run after `refine-alignment` (or `fetch-batch`) to ensure that what scoring evaluates and what `render-alignment` displays are the same data. `score-alignment` and `retry-alignment` run this pass automatically before scoring; `clean-alignments` can also be run standalone for inspection.

Checks performed:

| Check | Action |
|-------|--------|
| Empty source or target array | Drop record |
| Source token not in corpus TSV | Drop record |
| Target token not in edition TSV | Drop record |
| Token is secondary in one record but primary in another | Drop from secondary (repair); drop record if source becomes empty |
| Same source token in ≥2 records after repair | Drop all offending records |
| Same target token in ≥2 records | Drop all offending records |

```
clean-alignments \
  --alignment-dir path/to/alignments-eng/exp/OENGB/LLM-REFINED \
  --corpus nt \
  --target-edition OENGB \
  --target-tsv-dir path/to/alignments-eng/data/targets/OENGB \
  [--sources-dir data/sources/] \
  [--config OENGB]
```

Range filtering (`--book`, `--book-range`, `--chapter`, `--chapter-range`) works the same as the other tools.

#### `score-alignment`

Scores alignment quality for existing chapter JSON files and writes a per-verse TSV report. Does **not** call the LLM — use this between `refine-alignment` and `retry-alignment` to inspect quality and tune the retry threshold before committing to API spend.

Each verse receives a composite penalty score (0–1, higher = worse) from five signals: weighted source-token coverage, translation content-word coverage, NEQ overuse, token smearing, and per-verse deviation from chapter mean.

**Token smearing (signal 4):** flags N:M records where both sides have more than one *independent* primary token and no `is_idiom` marker. Articles, conjunctions, particles, and Hebrew pronominal suffixes are excluded from the independent-primary count — grouping a determiner with its noun is expected, but grouping a preposition with a noun (or two nouns together) is not. A `prep`+`det`+`noun` record still fires because the preposition and noun remain independent after the determiner is excluded.

In addition to the composite score, three post-hoc checks flag verses unconditionally:
- **`article_neq`** — articles (Greek definite article, Hebrew article) that appear in the NEQ list are always a mistake and force `needs_retry=True`.
- **`smear_forced_retry`** — when signal 4 exceeds `--smear-forced-retry-threshold` (default 0.22), the verse is forced `needs_retry=True` regardless of composite score. This catches verses where smearing is the only quality problem and coverage is otherwise clean.
- **`semantic_low_sim`** — for content-word (noun/verb/adjective) alignment records, embeds the source English gloss and target word text using LaBSE and flags records below `--semantic-threshold` (default 0.35). Any verse with at least one such record is forced `needs_retry=True`. Requires `--target-tsv-dir`.

Flagging uses the same dual logic as `retry-alignment`: a verse is marked `needs_retry=True` when either (a) composite score > `--score-retry-threshold`, or (b) the verse has ≥ `--min-unaligned-src` uncovered source tokens. The `coverage_flagged` column distinguishes which verses were caught by condition (b).

```
score-alignment \
  --alignment-dir path/to/alignments-eng/exp/OENGB/LLM-REFINED \
  --corpus nt \
  --target-language eng \
  [--target-edition OENGB] \
  [--target-tsv-dir path/to/alignments-eng/data/targets/OENGB]  # enables signal 2 + semantic
  [--sources-dir data/sources/] \
  [--score-retry-threshold 0.25] \
  [--min-unaligned-src 2] \
  [--semantic-model sentence-transformers/LaBSE]  # default; pass "" to disable
  [--semantic-threshold 0.35] \
  [--semantic-detail-output] \                     # write per-record similarity TSV to output/semantic_detail_YYYY-MM-DD.tsv
  [--flagged-only] \
  [--output scores.tsv] \
  [--config OENGB]
```

Output columns: `verse_id`, `composite`, `signal_1`–`signal_5`, `needs_retry`, `coverage_flagged`, `structural_errors`, `article_neq`, `semantic_low_sim`.

`--semantic-detail-output` (boolean flag, no value) writes a separate per-record TSV to `output/semantic_detail_YYYY-MM-DD.tsv` with columns `verse_id`, `src_ids`, `src_lemmas`, `src_gloss`, `tgt_ids`, `tgt_text`, `similarity`, `below_threshold`. Use this to inspect the similarity distribution for specific lemmas (e.g. filter `src_lemmas` for εἰμί) and calibrate the threshold.

#### `retry-alignment`

After `refine-alignment` (or `fetch-batch`) writes chapter JSON files, `retry-alignment` scores each verse using the composite quality scorer and re-aligns flagged verses from a **blank slate** — no prior alignment is passed as a candidate (to avoid the LLM perpetuating bad alignments).

Use `--dry-run` first to inspect which verses would be flagged before making any LLM calls.

```
retry-alignment \
  --alignment-dir path/to/alignments-eng/exp/OENGB/LLM-REFINED \
  --corpus nt \
  --target-language eng \
  --target-edition OENGB \
  --target-tsv-dir path/to/alignments-eng/data/targets/OENGB \
  [--sources-dir data/sources/] \
  [--llm-provider anthropic]          # openai | anthropic | google | openrouter | gloo | ollama (default: anthropic)
  [--llm-model claude-opus-4-7] \
  [--reasoning-effort high] \
  [--score-retry-threshold 0.25] \    # composite penalty threshold (default: 0.25)
  [--min-unaligned-src 2] \          # retry if N or more source tokens are unaligned (default: 2)
  [--semantic-model sentence-transformers/LaBSE]  # default; pass "" to disable
  [--semantic-threshold 0.35] \
  [--fallback-threshold 0.25] \       # if flagged% >= this, use refine model instead of retry model
  [--batch-size 5] \
  [--max-retries 2] \
  [--max-api-retries 4] \
  [--temperature 1] \
  [--max-output-tokens 4000] \        # overridden by retry_max_output_tokens if set in config
  [--batch-mode sync]                 # sync (default) | async
  [--jobs-dir jobs/] \
  [--dry-run]                         # report flagged verses without calling the LLM
  [--config OENGB]
```

The YAML config supports a separate `retry_max_output_tokens` key for the retry pass (mirrors `retry_llm_provider` / `retry_llm_model`). Use this when the retry model is an Anthropic thinking model that needs a larger token budget than the first-pass model:

```yaml
# NT config
max_output_tokens: 4000          # sufficient for NT verses
retry_max_output_tokens: 32000   # full budget for Anthropic/OpenAI reasoning retry pass

# OT config
max_output_tokens: 8000          # OT verses are larger; 4000 risks truncation with Gloo/DeepSeek
retry_max_output_tokens: 32000   # full budget for Anthropic/OpenAI reasoning retry pass
```

If the fallback threshold triggers and `retry-alignment` reverts to the refine-phase model, `max_output_tokens` is also restored to the refine-phase value.

`--fallback-threshold`: if the fraction of flagged verses across the run meets or exceeds this value (default 0.25), `retry-alignment` uses the refine-phase model instead of the configured retry model. Rationale: a high flagged rate suggests systemic quality issues better addressed by a fresh cheap pass than targeted expensive retries. Only takes effect when a separate retry model is configured (via `retry_llm_model` in the YAML or `--llm-model` after retry override). The model actually used is always printed before the verse list.

Range and verse filtering:

| Flag | Example | Notes |
|------|---------|-------|
| `--book BB` | `--book 66` | All chapters in a book |
| `--book-range START END` | `--book-range 65 66` | Inclusive book range |
| `--chapter BBCCC` | `--chapter 66007` | Single chapter |
| `--chapter-range START END` | `--chapter-range 66001 66022` | Inclusive chapter range |
| `--verse BBCCCVVV` | `--verse 41004003` | Force-retry one verse regardless of score |
| `--verse-range START END` | `--verse-range 41004001 41004020` | Force-retry a verse range regardless of score |
| `--verse-list VIDS` | `--verse-list 62002002,62003010` | Comma-separated verse IDs to force-retry |
| `--verse-list-file FILE` | `--verse-list-file bad_verses.txt` | File of verse IDs (one per line) to force-retry |

The `--verse*` flags bypass the quality scorer — the named verses are always retried. The chapter-level flags (`--book`, `--chapter`, etc.) still apply score filtering within the specified range. All flags in the table are mutually exclusive.

##### Async retry

```bash
retry-alignment --config OENGB --corpus nt --book 66 \
  --llm-provider anthropic --llm-model claude-opus-4-7 --reasoning-effort high \
  --batch-mode async

fetch-batch jobs/anthropic/OENGB-nt-20260424-abc12345.json --wait
```

### Visualization

#### `render-alignment`

Generate per-chapter HTML alignment visualizations in SBL Reverse Interlinear style. Each verse is a row of inline-block cells (translation order). Each cell shows the target token above its aligned source token(s) with subscript word-position indices. Relationship symbols follow the SBL RI convention:

| Symbol | Meaning |
|--------|---------|
| → / ← | Non-anchor token; source shown in the adjacent anchor cell |
| ▸N / ◂N | Token separated from its anchor; triangle points toward anchor cell; N = source word index |
| • | Target token with no source correspondent |
| ≠ | Token positively confirmed as non-equivalent (NEQ) |
| ‹ … › | Multiple source tokens behind one target token/phrase |

Secondary (grammatically implied) tokens are rendered in italic grey. Idiomatic records are rendered in italic. [ACAI](https://github.com/BibleAquifer/ACAI) entity tokens are highlighted.

```
render-alignment \
  --alignment-lang spa \
  --alignment-edition BONBV \
  --lang-data-path path/to/alignments-spa/data \
  --output-dir path/to/alignments-spa/viz \
  [--alignment-dir path/to/exp/BONBV/LLM-REFINED]  # override default alignments/ path
  [--target-edition-name "Biblia de Nuestra Familia Versión Breve"] \
  [--acai-data-dir PATH]  # default derived from git-root (https://github.com/BibleAquifer/ACAI); set null in config to disable
  [--r2l]
```

## Data layout

The tools expect kathairo-produced target TSVs split by canon:

```
data/targets/<edition>/
    ot_<edition>.tsv
    nt_<edition>.tsv

data/alignments/<edition>/
    WLCM-<edition>-manual.json      # OT (legacy single-file or hand-curated)
    SBLGNT-<edition>-manual.json    # NT (legacy single-file or hand-curated)

exp/<edition>/LLM-REFINED/
    SBLGNT-<edition>-41-001-manual.json   # NT chapter files from refine-alignment
    SBLGNT-<edition>-41-002-manual.json
    ...
    WLCM-<edition>-01-001-manual.json     # OT chapter files
    ...

jobs/
    google/<stem>.json      # async batch job metadata (from --batch-mode async)
    openai/<stem>.json      # stem = {edition}-{corpus}-{YYYYMMDD}-{short_id}
    anthropic/<stem>.json
```

Source TSVs (`SBLGNT.tsv`, `WLCM.tsv`) live in `data/sources/`.

`render-alignment` auto-detects chapter files when `--alignment-dir` is pointed at the `LLM-REFINED` (or similar) directory. If `{sourceid}-{edition}-??-???-manual.json` files are present they are merged on the fly; otherwise the tool falls back to the single-file path.

## Alignment format extensions

The base [Scripture Burrito alignment spec v0.4](https://github.com/bible-technology/alignment-spec/blob/main/spec.md) is used without modification for the core `source`/`target` token lists. Project extensions live in the `meta` object (which the spec explicitly leaves open):

Record-level extensions (in `meta` on each record):

| Field | Type | Meaning |
|-------|------|---------|
| `meta.secondary.source` | `string[]` | Source token IDs that are secondary (grammatically implied, not direct lexical equivalent) |
| `meta.secondary.target` | `string[]` | Target token IDs that are secondary |
| `meta.is_idiom` | `bool` | Marks a phrase-to-phrase idiomatic alignment |

Group-level extensions (in `meta` on the group, alongside `creator` and `conformsTo`):

| Field | Type | Meaning |
|-------|------|---------|
| `meta.nonEquivalent.source` | `string[]` | Source token IDs positively determined to have no translation equivalent |
| `meta.nonEquivalent.target` | `string[]` | Target token IDs positively determined to have no source correspondent |
| `meta.llm.provider` | `string` | LLM provider used by `refine-alignment` (`openai`, `anthropic`, `google`, `openrouter`, `gloo`, `ollama`) |
| `meta.llm.model` | `string` | Model name, e.g. `gpt-5.4-mini` |
| `meta.llm.reasoning_effort` | `string` | Reasoning effort level if set, e.g. `high` |
| `meta.retry_llm.provider` | `string` | Provider used by `retry-alignment` (only present when a retry pass has run) |
| `meta.retry_llm.model` | `string` | Retry model name |
| `meta.retry_llm.reasoning_effort` | `string` | Reasoning effort for the retry pass |

`AlignmentsReader.group_meta` exposes the full raw group meta dict so downstream tools (e.g. `render-alignment`) can read back fields like `llm` and `retry_llm` without re-parsing the JSON.

All tokens not listed in `meta.secondary` are assumed primary. `meta.nonEquivalent` tokens are distinct from simply unrecorded tokens — they represent a positive determination of non-equivalence (see §3.5 of alignment-principles). See [docs/alignment-principles-nt.md](docs/alignment-principles-nt.md) for full specification.

## Alignment principles

See [docs/alignment-principles-nt.md](docs/alignment-principles-nt.md) (NT/Greek) and [docs/alignment-principles-ot.md](docs/alignment-principles-ot.md) (OT/Hebrew) for the complete alignment specification, including:

- Generous alignment philosophy
- Three-state model: aligned / NEQ (non-equivalent) / unrecorded
- Primary vs. secondary link types
- Discontiguous token alignment
- Article alignment rules (Greek definite article vs. English "the"/"a")
- Idiom handling
- Grammatical construction cases (§9): finite verbs, participials, infinitivals, adjectives/adverbs, pronouns, prepositions, conjunctions/particles, discourse restructuring
- Mounce Reverse Interlinear guidelines reference cases
- Automated → LLM sharpening workflow

## Contributing

Bug reports and pull requests are welcome. Please open an issue first to discuss significant changes. All PRs require review and approval before merging.

## Licensing

### Alignment data

Alignment data produced by this project will be published at [Bible Aquifer](https://github.com/BibleAquifer) under a [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/) (CC BY-SA 4.0). Alignment files present in this repository are works in progress and are not the canonical release.

### Code

The code in this repository is licensed under the [MIT License](LICENSE).

## Appendix: Migration and seeding tools

These tools create initial alignment candidates by migrating from an existing aligned translation. They are not needed when aligning from scratch (`--from-scratch` on the command line, or `from_scratch: true` in the config).

### `diff-migrate`

Migrate alignments from a reference translation to a similar translation using word-level text diffs ([diff_match_patch](https://github.com/google/diff-match-patch)).

```
diff-migrate \
  --source-edition NIV11 \
  --target-edition NIrV \
  --source-tsv-dir  path/to/alignments-eng/data/targets/NIV11 \
  --target-tsv-dir  path/to/alignments-eng/data/targets/NIrV \
  --source-alignment-dir path/to/alignments-eng/data/alignments/NIV11 \
  --output-dir path/to/alignments-eng/exp/NIrV/DIFF-MIGRATED
```

### `sim-migrate`

Migrate alignments using multilingual sentence similarity. Supports [LaBSE](https://huggingface.co/sentence-transformers/LaBSE) (default, broad language coverage) and [SONAR_200](https://huggingface.co/cointegrated/SONAR_200_text_encoder) (useful for languages LaBSE does not cover, e.g. Lingala).

```
sim-migrate \
  --source-edition NIV11 --source-language eng \
  --target-edition BONBV --target-language spa \
  --source-tsv-dir  path/to/alignments-eng/data/targets/NIV11 \
  --target-tsv-dir  path/to/alignments-spa/data/targets/BONBV \
  --source-alignment-dir path/to/alignments-eng/data/alignments/NIV11 \
  --output-dir path/to/alignments-spa/exp/BONBV/SIM-MIGRATED \
  [--model sentence-transformers/LaBSE] \
  [--min-similarity 0.7] [--max-word-distance 8] \
  [--no-stopword-filter]
```

### `acai-align`

Create entity alignments (persons, places, groups, etc.) using [ACAI](https://github.com/BibleAquifer/ACAI) data. Matches entities to translation tokens via reference-list overlap and Jaro-Winkler string similarity, with [trabina](https://github.com/RickBrannan/trabina) name-translation data to improve cross-language matching.

```
acai-align \
  --target-language spa \
  --target-edition BONBV \
  --targets-dir  path/to/alignments-spa/data/targets/BONBV \
  [--acai-data-dir PATH]   # derived automatically; see https://github.com/BibleAquifer/ACAI
  [--trabina-dir PATH]     # derived automatically; see https://github.com/RickBrannan/trabina
  --output-dir   path/to/alignments-spa/exp/BONBV/ACAI \
  [--include-secondaries] \
  [--acai-types people places groups deities]
```
