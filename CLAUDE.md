# CLAUDE.md — text-align developer notes

## Project purpose

CLI toolchain for creating and refining word-level alignments between Bible translations
and their source texts (Greek NT / Hebrew OT). Alignment format is Scripture Burrito 0.4
with project-specific `meta` extensions (primary/secondary, NEQ, idiom).

## Key conventions

- **Alignment direction:** always translation → source. Records ask "what Greek/Hebrew
  word(s) are behind this translation word?"
- **Primary vs secondary:** primary = direct lexical/semantic connection; secondary =
  grammatically implied with no separate source token.
- **NEQ:** a positive claim of non-equivalence — never use as a fallback for uncertainty.
- See `docs/alignment-principles-nt.md` (NT/Greek) and `docs/alignment-principles-ot.md` (OT/Hebrew) for the full specification.

## Package layout

```
src/text_align/
├── burrito/       # SB 0.4 data model
├── migrate/       # diff-migrate, sim-migrate CLIs
├── align/         # acai-align CLI
├── refine/        # refine-alignment + fetch-batch + retry-alignment + score-alignment + clean-alignments CLIs
│   ├── prompt/          # language-aware prompt system (see below)
│   ├── llm.py           # LLMClient: OpenAI / Anthropic / Google / OpenRouter / Gloo / Ollama (sync)
│   ├── async_batch.py   # provider batch-API helpers (Google, OpenAI, Anthropic)
│   ├── coverage.py      # legacy per-verse source-token coverage evaluation
│   ├── scoring.py       # composite alignment quality scorer (five signals)
│   ├── scoring_stopwords.py # per-language stopword sets for scorer signal 2
│   ├── refine.py        # refine-alignment CLI entry point
│   ├── fetch_batch.py   # fetch-batch CLI entry point
│   ├── retry.py         # verse merge/retry core logic
│   ├── retry_cli.py     # retry-alignment CLI entry point
│   ├── clean.py             # core cleaning logic (CleanResult, clean_chapter_file, run_clean_pass)
│   ├── clean_cli.py         # clean-alignments CLI entry point
│   └── score_alignments.py  # score-alignment CLI entry point
└── render/        # render-alignment HTML visualizer
```

## Multi-language prompt system (`refine/prompt/`)

Prompts are assembled from a `LanguagePromptConfig` registered per ISO 639-3 code.
The directory has two testament subdirectories (`nt/`, `ot/`) plus shared infrastructure:

- `common.py` — `LanguagePromptConfig` dataclass, shared prompt assembly and verse
  formatting functions (including `_format_source_token`). No registry lives here.
- `nt/core.py` — NT registry (`register_language` / `get_language_config`), Greek NT
  phenomenon detection (`detect_phenomena`), and NT-specific prompt assembly.
- `ot/core.py` — OT registry and `detect_phenomena` for Hebrew OT phenomena.
- `nt/eng.py` — English block strings + `ENG_CONFIG`; calls `register_language` on import.
- `nt/por.py` — Portuguese. Pro-drop, contracted preposition+article forms (do/da/no/na/
  ao/à/pelo/pela), conditional proper-name articles (BP retains them), reflexive passive,
  personal infinitive. Unchanged blocks imported from `eng.py`.
- `nt/spa.py` — Latin American Spanish. Same pro-drop rules; contracted forms limited to
  `del` and `al` only; proper-name articles always Branch B (LA translations omit them);
  vos/tú regional note; ustedes for 2nd plural; no personal infinitive.
- `nt/fra.py` — French. NOT pro-drop (subject pronouns required; secondary when no Greek
  pronoun — inverse of Spanish/Portuguese). Contracted forms du/des/au/aux (non-contracting
  stay two words). Double-article attributive handled (first → Branch A, second → Branch B).
  Partitive du/de la/des secondary for anarthrous mass nouns. Reflexive passive (se + verb)
  and impersonal "on" as passive equivalent. Discontinuous ne…X negation; restrictive ne…que.
- `ot/eng.py` — OT English config.
- `__init__.py` — re-exports the public API and imports all language modules to trigger
  registration.

**To add a new target language:** create `prompt/<iso>.py`, define a `LanguagePromptConfig`
with the appropriate block content, and call `register_language()`. Then add the import
to `__init__.py`. Import unchanged blocks from `eng.py` rather than duplicating them.
Unknown language codes fall back to English automatically.

**Prompt style:** all prompt blocks are compressed (rules + examples; no motivating prose
or meta-commentary). Prose reference copies are preserved as `*.prose.py` siblings (not
imported, `register_*_language` call commented out) for each language file that has been
compressed. Approximate token budget (all blocks assembled):

| Config | ~tokens |
|--------|---------|
| NT eng | 3,274 |
| NT por | 3,614 |
| NT spa | 3,599 |
| NT fra | 4,488 |
| OT eng | 2,560 |

Current languages: eng, por, spa, fra.
Planned: Arabic, Chinese Simplified, Chinese Traditional, Hindi, Gujarati,
Nepali, Tok Pisin, Bislama, Lingala, Swahili.

## LLM providers (`refine/llm.py`)

`LLMClient` supports six providers, selected by the `provider` argument:

| Provider | Env var | Notes |
|----------|---------|-------|
| `openai` | `OPENAI_API_KEY` | Uses Responses API for reasoning models |
| `anthropic` | `ANTHROPIC_API_KEY` | Extended thinking via `thinking` block |
| `google` | `GEMINI_API_KEY` | Gemini 3+ `thinkingLevel` via `ThinkingConfig` |
| `openrouter` | `OPENROUTER_API_KEY` | OpenAI-compatible proxy to 200+ models (Qwen, Kimi, GLM, …); sync-only; per-call cost tracked in `LLMClient.session_cost` |
| `gloo` | `GLOO_CLIENT_ID`, `GLOO_CLIENT_SECRET` | Gloo AI Studio; OAuth2 bearer token (1-hr TTL, auto-refreshed); SSE streaming via `requests`; routes to Anthropic/OpenAI/Google; sync-only; no reasoning_effort; model IDs like `gloo-anthropic-claude-sonnet-4.5` |
| `ollama` | `OLLAMA_BASE_URL` (optional) | Local inference via Ollama's OpenAI-compatible API; default base URL `http://localhost:11434/v1`; sync-only; no reasoning_effort; no async batch |

`reasoning_effort` (none/minimal/low/medium/high) maps to `reasoning_effort` for OpenAI
and `thinkingLevel` for Google. Omitting it sends no thinking config. Ignored for
`openrouter`, `gloo`, and `ollama` (always use the chat completions path).

`OLLAMA_BASE_URL` can be set in `.env` to point at any OpenAI-compatible local endpoint
(e.g. `http://localhost:8080/v1` for `mlx_lm.server`) without code changes.

## OpenRouter cost tracking (`refine/llm.py`)

`LLMClient.session_cost` accumulates the USD cost of all OpenRouter calls made during
the session. `_track_openrouter_cost(response)` reads `response.usage.model_extra["cost"]`
(Pydantic captures extra fields OpenRouter adds to the standard usage object) and prints
a per-call + running total after each API call. A session total is printed at the end of
`refine-alignment` and `retry-alignment` when `--llm-provider openrouter` is active.
Async batch mode is not supported for `openrouter` or `gloo`.

## OpenRouter DeepSeek provider ordering (`refine/llm.py`)

When the provider is `openrouter` and the model slug contains `deepseek` (case-insensitive),
`_call_openai` automatically adds `extra_body={"provider": {"order": ["DeepSeek", "deepseek"],
"allow_fallbacks": False}}` to the API call. This pins routing to DeepSeek's own
infrastructure (cheapest option) and disables silent fallback to other providers.
Any `:nitro` or `:exacto` variant suffix is stripped from the model name in the same
call, as those suffixes conflict with explicit provider ordering.

## Gloo AI provider (`refine/llm.py`)

`_GlooAuth` handles OAuth2 client-credentials auth for Gloo AI Studio.  Tokens have a
1-hour TTL; `_GlooAuth._token()` auto-refreshes 60 s before expiry so long-running jobs
never hit an expired-token error.  Credentials are read from `GLOO_CLIENT_ID` /
`GLOO_CLIENT_SECRET`.

`_call_gloo` uses the OpenAI-compatible chat completions format with SSE streaming
(`"stream": True`).  `_GlooAuth.post(payload, stream=True)` returns a raw
`requests.Response`; `_accumulate_gloo_stream(response)` consumes the SSE events and
concatenates `choices[0].delta.tool_calls[0].function.arguments` fragments into a
complete JSON string, then returns a dict matching the non-streaming response shape.
The entire accumulate call is wrapped in `_api_call_with_backoff` so
`ChunkedEncodingError` (server drops stream mid-generation) and `ConnectionError` are
retried with exponential backoff.  `reasoning_effort` is ignored (Gloo routes to the
underlying provider; no pass-through for thinking config).  Async batch mode is not
supported for Gloo.

Streaming is used because Gloo routes through Cloudflare, which enforces a ~100 s
timeout on the first response byte.  Non-streaming calls to slow models time out with
a 504 before generation begins; streaming bypasses this by delivering the first SSE
chunk as soon as the model starts.  `timeout=(30, None)` on the `requests` call sets
a 30 s connect timeout with no read timeout so long generations are not killed.

Gloo model IDs follow the pattern `gloo-{family}-{model}`, e.g.:
- `gloo-anthropic-claude-sonnet-4.5`
- `gloo-openai-gpt-4.1-mini`
- `gloo-google-gemini-2.5-flash`

`_status_code()` handles `requests.HTTPError` via the string-prefix fallback
(`"429 Client Error: …"` → 429), so `_api_call_with_backoff` retries correctly.

`_GlooAuth.post` catches `HTTPError` from `raise_for_status()` and re-raises it with
the full response body appended (`— {detail}`) so error messages include the server's
explanation rather than just the HTTP status line.

## Environment variable loading (`refine/llm.py`)

`load_dotenv()` is called at module import time, so a `.env` file in the project root
is loaded automatically before any provider client is initialised. All provider env vars
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`,
`GLOO_CLIENT_ID`, `GLOO_CLIENT_SECRET`) can be set there. `.env.example` in the repo
root documents all supported variables. `.env` is gitignored.

## Model names

Never substitute a user-specified model name for a known one, even if the name looks
unfamiliar (e.g. `gpt-5.4-mini`, `gemini-3-flash-preview`). Trust the user.

## render-alignment (`render/html.py`)

- Multi-primary and idiom non-anchor cells render a directional triangle + subscript
  source index. The triangle (`▸` / `◂`) points toward the anchor cell.
- `_tri_toward(token_pos, anchor_pos, is_r2l)` computes the correct direction.
- CSS classes: `.tri` (triangle, 90% font-size), `.sub` (subscript, 60%).

## LLM robustness (`refine/llm.py`)

`_TOOL_CHOICE_INCOMPATIBLE` is a module-level `frozenset` of model names known to
reject `tool_choice`.  `_call_openai` and `_call_gloo` initialize
`_tool_choice_dropped = self.model in _TOOL_CHOICE_INCOMPATIBLE` so these models omit
`tool_choice` from the first call rather than trying-then-dropping on error.  Current
members: `deepseek/deepseek-v4-pro` (openrouter), `gloo-deepseek-v4-pro` (gloo).
The runtime catch-and-retry in `_call_openai` remains active for unknown models.

`_iter_verse_entries(data, errors)` is a helper used by all five provider call paths
(`_call_openai`, `_call_openai_responses`, `_call_anthropic`, `_call_gemini`, `_call_gloo`). It
iterates the `verses` array from a tool-call response, skipping and logging any entry
that is not a dict. This guards against malformed model output (e.g. a string element
in the array) that would otherwise crash with `AttributeError` on `.get()`.

`_api_call_with_backoff(fn, max_retries, provider)` wraps each provider's API call.
It retries on 408 (provider timeout), 429 (rate-limited), 500/502/503 (provider error),
504 (gateway timeout), 520/522/524 (Cloudflare transient) with exponential backoff (2s, 4s, 8s, …) up to
`max_retries` times, and on `requests.exceptions.Timeout`. Fails fast on non-retriable errors. `_status_code(exc)`
extracts the HTTP status code from any provider exception.
Exposed via `--max-api-retries` (default 4) in `refine-alignment`.

## render-alignment header (`render/html.py`)

Each chapter file opens with a styled `.file-meta` row below the `<h1>` showing:
edition abbreviation + full name, LLM provider/model/reasoning_effort (read from
`group_meta["llm"]` in the alignment JSON), and the render date.

- `_build_meta_row(meta_info)` assembles the HTML row; missing fields are omitted
  gracefully.
- `AlignmentsReader.group_meta` (added to `burrito/alignments.py`) exposes the full
  group-level JSON meta dict so render can read back whatever refine stored.
- `--target-edition-name` CLI arg (also `target_edition_name` in YAML) supplies the
  full translation name; the edition abbreviation comes from `--alignment-edition`.

## refine-alignment output granularity

Output is one JSON file per chapter, not one per corpus:

```
SBLGNT-OENGB-41-003-manual.json   ← Mark 3 (book 41, chapter 003)
SBLGNT-OENGB-41-004-manual.json
```

Format: `{corpus_id}-{edition}-{BB}-{CCC}-manual.json`.
The internal SB 0.4 JSON structure is identical to the old corpus-level file;
it just covers one chapter.

## refine-alignment range filtering

New args narrow which verses are processed. All are mutually exclusive with
each other and with `--verse` / `--verse-range`.

| Arg | Format | Example |
|-----|--------|---------|
| `--book BB` | 2-digit book number | `--book 41` |
| `--book-range BB BB` | inclusive book range | `--book-range 41 44` |
| `--chapter BBCCC` | 5-digit chapter | `--chapter 41003` |
| `--chapter-range BBCCC BBCCC` | inclusive chapter range | `--chapter-range 41001 41016` |

Filtering uses string-prefix comparison on 8-char `BBCCCVVV` verse IDs
(`vid[:2]` = book, `vid[:5]` = chapter); no extra biblelib imports needed.

## Async batch mode (`refine/async_batch.py`)

`refine-alignment --batch-mode async` submits all LLM calls to the provider's
batch API (all three providers implemented) and exits, writing a job metadata
JSON to `jobs/{provider}/{stem}.json`.

`fetch-batch <job-metadata-file>` retrieves completed results and writes
chapter JSON files. Flags: `--poll` (print status, exit), `--wait` (block
until done), `--cancel` (request cancellation).

## fetch-batch progress display (`fetch_batch.py`)

`--poll` and `--wait` show request-level progress counts for OpenAI and
Anthropic (Google exposes only a coarse state enum, so it stays state-only).

- `_openai_progress(batch)` — derives `done/total` from `request_counts.completed`
  + `request_counts.failed`; appends `, N failed` when non-zero.
- `_anthropic_progress(batch)` — sums `succeeded + errored + expired + canceled`
  for `done`; total includes `processing`; appends `, N errored` when non-zero.

Both helpers fall back to the bare status string if `request_counts` is absent
or all zeros (guards against API objects that omit the field).

Example output during `--wait`:
```
  Batch batch_abc123: in_progress  47/200 — waiting ...
  Batch batch_abc123: in_progress  118/200
  Batch batch_abc123: completed
```

Job metadata format: see `docs/batch-api-plan.md`.

Google batch API: `client.batches.create(src=types.BatchJobSource(inlined_requests=[...]))`.
Each `InlinedRequest` carries `metadata={"request_index": "N"}` for result
matching; responses come back as `job.dest.inlined_responses`.

OpenAI batch API: JSONL file uploaded via `files.create`, then submitted with
`batches.create(input_file_id=..., endpoint=..., completion_window="24h")`.
Uses `/v1/responses` when `reasoning_effort` is set, `/v1/chat/completions`
otherwise.

Anthropic batch API: `client.messages.batches.create(requests=[...])` where
each request carries a `custom_id` (the request index as a string) and `params`
matching the `messages.create` schema. Terminal state: `processing_status ==
"ended"`. Individual result types: `"succeeded"`, `"errored"`, `"expired"`,
`"canceled"`. Results retrieved via `client.messages.batches.results(batch_id)`.

## Sync/async generation parameter parity (`refine/llm.py`, `async_batch.py`)

Batch API infrastructure may apply different defaults than the sync path
(different temperature, lower token limits), causing consistent quality
degradation on the async path. Fix: `LLMClient` now always sends `temperature`
and `max_output_tokens` explicitly on every call — both sync and async.

Defaults: `temperature=1`, `max_output_tokens=4000`. Temperature is not sent for
OpenAI reasoning models (it is fixed by the API). Overridable via `--temperature` and
`--max-output-tokens` CLI flags (also settable in YAML config files).

**`max_output_tokens` guidance by corpus and provider:**

| Scenario | Recommended `max_output_tokens` |
|----------|--------------------------------|
| NT, any provider | 4 000 (default) |
| OT, Gloo/DeepSeek (thinking disabled) | 8 000 — OT verses are larger; 4 000 risks `finish_reason=length` truncation on complex verses |
| OT or NT, Anthropic thinking retry | 32 000 — thinking tokens come *out of* `max_tokens`; too low truncates thinking + output together |
| OT or NT, OpenAI o-series reasoning | 32 000 — `max_completion_tokens` covers reasoning + output combined (same behaviour as Anthropic) |

The claim that "OpenAI/Google reasoning tokens are separate from the output budget" is
**incorrect for OpenAI o-series models** (`o1`, `o3`, `o4-mini`, etc.): their
`max_completion_tokens` is a combined budget, just like Anthropic `max_tokens`. Google
Gemini thinking tokens are genuinely separate. Empirically, 8 000 is insufficient for
OpenAI reasoning models on OT alignment; 32 000 resolves it.

Use `retry_max_output_tokens` (see below) to set a higher budget for the retry pass
while keeping a leaner budget for the first pass.

## Split-batch fallback (`refine/refine.py`, `refine/retry.py`)

In `_process_corpus_sync` (refine) and `retry_chapter_sync` (retry), `call_batch` is
wrapped in `try/except RuntimeError`.  When a batch exhausts all API retries
(exponential backoff × `max_api_retries`), the exception is caught, the missed verse
IDs are logged, and `results={}` is returned rather than crashing.  Multi-verse
batches then fall through to the existing "missing verses" resubmit loop, which
resubmits each verse individually (shorter output → less chance of a mid-stream drop).
If even an individual verse call raises `RuntimeError`, it is logged and skipped; the
verse gets no records and scores 100% uncovered (signal_1 = 1.0), guaranteeing it is
flagged for the retry pass.

This is the primary resilience mechanism for Gloo streaming: the Cloudflare proxy can
drop a long SSE stream mid-generation; streaming retries handle transient drops, and
the split-batch fallback ensures a persistent drop on one batch does not abort the
entire chapter.

## `retry_max_output_tokens` (`refine/retry_cli.py`)

Separate `max_output_tokens` budget for the retry pass.  Follows the same save/apply/
restore pattern as `retry_llm_provider` / `retry_llm_model` / `retry_reasoning_effort`:

- Saved as `args._refine_max_output_tokens` before retry overrides are applied.
- `retry_max_output_tokens` (YAML) or `--retry-max-output-tokens` (CLI) overrides
  `args.max_output_tokens` for the retry pass.
- If the fallback threshold triggers and `retry-alignment` reverts to the refine model,
  `args.max_output_tokens` is also restored to `args._refine_max_output_tokens`.

Typical config:
```yaml
# NT config
max_output_tokens: 4000          # sufficient for NT verses
retry_max_output_tokens: 32000   # full budget for Anthropic/OpenAI reasoning retry pass

# OT config
max_output_tokens: 8000          # OT verses are larger; 4000 risks truncation with Gloo/DeepSeek
retry_max_output_tokens: 32000   # full budget for Anthropic/OpenAI reasoning retry pass
```

## render-alignment chapter-file detection (`render/html.py`)

The renderer auto-detects chapter files. When `--alignment-dir` contains files
matching `{sourceid}-{edition}-??-???-manual.json`, it merges them via
`AlignmentsReader.from_chapter_files()` and skips the single-file load path.
Falls back to the single-file behavior when no chapter files are found.

Implementation details:
- `AlignmentsReader.from_chapter_files(paths, alignmentset)` — class method in
  `burrito/alignments.py`. Merges `groups[0].records` and `nonEquivalent` sets
  from all chapter files; takes `group_meta` from the first. Accepts an optional
  `_preloaded_data` dict via the regular constructor to bypass the file read.
- `AlignmentSet.__post_init__` — assertion `alignmentpath.exists()` now only
  fires when no `alignmentpath_override` is given. When chapter files are used,
  `alignmentpath_override` is set to the first chapter file (a real existing
  file), so the assertion still passes.
- `Manager.__init__` — accepts optional `preloaded_reader: AlignmentsReader`.
  When supplied, it skips creating its own reader and uses the provided one
  (still calls `clean_alignments` on it).

Full design: `docs/batch-api-plan.md`.

## Alignment quality scoring (`refine/scoring.py`, `refine/scoring_stopwords.py`)

`score_chapter_file(path, source_verses, lang, config, target_verses=None)` scores all
verses in a chapter JSON file and returns `list[VerseScore]`. Each `VerseScore` carries
five penalty signals (0–1 each) and a composite score; verses above `config.retry_threshold`
have `needs_retry=True`.

**Five signals:**

| # | Signal | What it catches |
|---|--------|----------------|
| 1 | Weighted source coverage | Unaligned source tokens, weighted by POS (verb/noun=1.0 … article=0.1) |
| 2 | Translation content-word coverage | Target words not in any record and not NEQ (stop-words excluded) |
| 3 | NEQ overuse | NEQ rate above a per-language baseline (default 10%) |
| 4 | Token smearing | N:M records where both sides have >1 independent primary and no `is_idiom` flag |
| 5 | Per-verse deviation | Verses anomalously worse than the chapter mean (second pass) |

Signals 1–4 are computed per verse; signal 5 requires a second pass over all verses in the
chapter. `score_chapter()` handles the two-pass logic and sets `needs_retry`.

**Signal 4 (smearing):** catches the cheap-model failure mode where tokens that should be
separate records (e.g. two nouns, or a preposition + noun) are grouped into one N:M record.
Weighted by `independent_p_src × p_tgt`; a 1.5× adjacency boost applies when source and
target token IDs are both consecutive, which is the strongest indicator of over-grouping.

*Bound-morpheme exclusion:* articles, conjunctions, particles, and Hebrew pronominal suffixes
(`_BOUND_SRC_POS`) are excluded from the independent-primary count. A `det`+noun grouping
is legitimate; a `prep`+noun grouping is not. A `prep`+`det`+noun record still fires because
`prep` and `noun` both count as independent (the `det` is dropped from the count but the two
remaining tokens keep `independent_p_src = 2`). This removes systematic false positives from
article+noun and conjunction-phrase groupings while preserving the signal for preposition+noun
over-grouping.

*Standalone retry gate:* `signal_4 > config.smear_forced_retry_threshold` (default 0.22)
forces `needs_retry=True` regardless of composite score. This catches verses where smearing
is the only quality problem (coverage is clean, no NEQ issues) — in those cases the composite
alone cannot reach the retry threshold even with a high signal_4 value.

**Stop-word lists (`scoring_stopwords.py`):** uses `stopwordsiso` (already a project
dependency) intersected with a small curated core per language to keep lists minimal.
Languages without coverage (Tok Pisin, Bislama, Lingala, …) return an empty frozenset —
the safe direction is to penalise gaps rather than suppress content words.

**`ScoringConfig`** holds signal weights (w1–w5), NEQ baseline, adjacency multiplier,
smear forced-retry threshold, deviation k, and retry threshold. All overridable; defaults
work for NT English. Default weights: w1=0.25, w2=0.20, w3=0.15, w4=0.40, w5=0.00.

YAML config keys: `score_retry_threshold` (default 0.25), `smear_forced_retry_threshold`
(default 0.22). Weights are code defaults; adjust via `ScoringConfig` if needed.

## clean-alignments (`refine/clean.py`, `refine/clean_cli.py`)

Validates and repairs chapter JSON alignment files in place so that scoring and
`render-alignment` see the same data. `score-alignment` and `retry-alignment` call
`run_clean_pass()` automatically before scoring; `clean-alignments` can also be
run standalone.

Three-pass algorithm in `clean_chapter_file(path, source_ids, target_ids)`:

1. **Per-record validity** — drops records with empty source/target, source tokens
   absent from the corpus TSV (`MISSINGSOURCE`), or target tokens absent from the
   edition TSV (`MISSINGTARGETALL` / `MISSINGTARGETSOME`).
2. **Secondary-primary conflict repair** — if a token is secondary in one record
   but primary in another, it is removed from the secondary record's `source` and
   `meta.secondary.source`. If this empties the source array the record is dropped
   (`SECONDARYCONFLICT_DROP`); otherwise the record is kept as repaired
   (`SECONDARYCONFLICT`).
3. **Cross-record duplicate detection** — any source or target token still appearing
   in multiple records after pass 2 causes all offending records to be dropped
   (`DUPLICATESOURCE` / `DUPLICATETARGET`).

`run_clean_pass(chapter_files, source_verses, target_verses)` drives the loop and
returns `(files_changed, total_dropped, total_repaired)`.

## score-alignment (`refine/score_alignments.py`)

Standalone audit tool. Reads chapter JSON files and writes a per-verse TSV report (columns:
`verse_id`, `composite`, `signal_1`–`signal_5`, `needs_retry`, `coverage_flagged`,
`structural_errors`, `article_neq`, `semantic_low_sim`) to stdout or `--output`. Does **not** call the LLM.

Uses the same dual flagging logic as `retry-alignment`: a verse is flagged when either
(a) composite score > `--score-retry-threshold`, or (b) `find_low_coverage_verses()`
finds ≥ `--min-unaligned-src` uncovered source tokens. The `needs_retry` column reflects
the combined result; `coverage_flagged` indicates which verses were flagged by (b).

```bash
score-alignment \
  --config OENGB --corpus nt \
  --alignment-dir path/to/LLM-REFINED \
  [--target-tsv-dir path/to/targets/OENGB]   # enables signal 2 and semantic check
  [--score-retry-threshold 0.25] \
  [--min-unaligned-src 2] \
  [--semantic-model sentence-transformers/LaBSE] \   # default; pass "" to disable
  [--semantic-threshold 0.35] \
  [--semantic-detail-output] \                        # write per-record similarity TSV to output/semantic_detail_YYYY-MM-DD.tsv
  [--flagged-only] \
  [--output scores.tsv]
```

TSV includes an `article_neq` column (integer count). Any verse with `article_neq > 0`
is unconditionally flagged `needs_retry=True` regardless of the composite score —
NEQ'd articles are always a mistake (articles must be primary to "the"/pronoun/reinstated
proper noun, or secondary to their head noun/adjective/participle).

TSV also includes a `semantic_low_sim` column (integer count of records below threshold).
Any verse with `semantic_low_sim > 0` is unconditionally flagged `needs_retry=True`.
Requires `--target-tsv-dir`; silently skips if target text is unavailable.

`--semantic-detail-output` (boolean flag, no value) writes a per-record TSV to
`output/semantic_detail_YYYY-MM-DD.tsv` (columns: `verse_id`, `src_ids`, `src_lemmas`,
`src_gloss`, `tgt_ids`, `tgt_text`, `similarity`, `below_threshold`). Primary use:
filter by `src_lemmas` to inspect the similarity distribution for specific lemmas and
calibrate the threshold.

Primary use: run between `refine-alignment` and `retry-alignment` to inspect quality
before committing to a retry spend, and to tune the threshold against manually reviewed
chapters.

## Semantic similarity scoring (`refine/semantic.py`)

Post-hoc check (runs automatically when `--target-tsv-dir` is provided): for each
eligible alignment record, embeds the source gloss and target word text using
`sentence-transformers/LaBSE` and computes cosine similarity. Records below
`--semantic-threshold` (default 0.35) contribute to a per-verse `semantic_low_sim_count`;
any verse with count > 0 is flagged `needs_retry=True`.

**Eligible records:** only records where at least one primary source token is a
content-bearing POS: `noun`, `verb`, `adj` (NT), `adjective` (OT). Function words
(articles, conjunctions, prepositions, pronouns) are excluded — they are too flexible
in translation to produce reliable similarity signals. Idiom records (`meta.is_idiom`)
are also excluded.

**Source-side text:** `gloss2` when non-empty (bare core meaning, no contextual syntax
markers), falling back to `gloss`. Dots in `gloss2` are replaced with spaces to handle
OT forms like `"he.created"` → `"he created"`. English glosses are used rather than
source-language lemmas because LaBSE's ancient-language embedding spaces (Koine Greek,
Biblical Hebrew) are dominated by Modern Greek / Modern Hebrew web text and are not
reliable for biblical vocabulary. POS names differ between corpora: NT uses `adj`, OT
uses `adjective`; both are included in `_CONTENT_POS`.

**Model:** any `sentence-transformers`-compatible model; default is
`sentence-transformers/LaBSE` (109 languages, ~470 MB). Model is lazy-loaded and
cached at module level — first call downloads and loads it; subsequent calls reuse it.
Swap via `--semantic-model` to any HuggingFace model if LaBSE coverage is insufficient
for a target language. Pass `--semantic-model ""` to disable the check entirely.

**Batching:** all records across the chapter are collected into a single encoder call
for efficiency. A per-chapter diagnostic line is printed to stderr:
`Semantic [BBCCC] N pairs, sim min=X mean=Y max=Z, N record(s) below T`

**Per-record detail output:** `--semantic-detail-output` (boolean flag) on `score-alignment`
writes a TSV to `output/semantic_detail_YYYY-MM-DD.tsv` with `verse_id`, `src_ids`,
`src_lemmas`, `src_gloss`, `tgt_ids`, `tgt_text`, `similarity`, `below_threshold` for
every scored record. Filter by `src_lemmas` to inspect the similarity distribution for
any specific lemma.

**Implementation:** `apply_semantic_scores(verse_scores, records_by_verse, src_by_id,
tgt_text_by_id, model_name, threshold, chapter_id, record_details)` in `semantic.py`.
`score_chapter_file` in `scoring.py` threads `record_details` through. Both
`score-alignment` and `retry-alignment` pass `target_verses` to `score_chapter_file`
so the semantic check has target text available.

**YAML config keys:** `semantic_model`, `semantic_threshold`.

Available on `score-alignment` and `retry-alignment`; not on `refine-alignment`.

## Two-pass workflow (cheap model → clean → score → retry)

```bash
# 1. First pass — cheap/fast model
refine-alignment --config MYEDITION --corpus nt \
  --llm-provider openrouter --llm-model deepseek/deepseek-v4-pro

# 2. Clean alignment files in place (optional standalone; also runs inside score/retry)
clean-alignments --config MYEDITION --corpus nt

# 3. Audit scores — clean pass runs automatically before scoring
score-alignment --config MYEDITION --corpus nt --flagged-only --output scores.tsv

# 4. Retry flagged verses — clean pass runs automatically before scoring
retry-alignment --config MYEDITION --corpus nt \
  --llm-provider anthropic --llm-model claude-sonnet-4-6 --reasoning-effort high
```

The YAML config supports separate model keys per pass — `retry_llm_provider`,
`retry_llm_model`, `retry_reasoning_effort` — that override the refine-phase `llm_*`
keys in `retry-alignment`. If absent, the retry pass falls back to the refine keys.

## retry-alignment (`refine/retry_cli.py`, `refine/retry.py`, `refine/scoring.py`)

Post-batch quality pass: identifies verses that scored above the retry threshold
and re-aligns them from scratch.

**Detection** (`scoring.py`, `coverage.py`): a verse is flagged when either condition
holds: (a) `score_chapter_file()` returns `composite > --score-retry-threshold`
(default 0.25), or (b) `find_low_coverage_verses()` finds at least
`--min-unaligned-src` (default 2) unaligned source tokens. Both checks run for every
chapter; a verse needs only one to trigger.

**Remedy**: flagged verses are sent to the LLM **blank-slate** — no prior
alignment is passed as a candidate. Passing existing records as candidates caused
the LLM to over-weight them and perpetuate bad alignments (including wrong
token-swap errors, not just gaps). Blank-slate lets the LLM produce a clean
realignment of the entire verse.

**Merge** (`retry.py:merge_verse_results`): replaces only the flagged verse
records in the existing chapter JSON. For non-replaced verses, regular records
are kept as-is; NEQ entries are re-inflated into `{"meta": {"rel": "NEQ"}}`
records so `build_output_alignment` can reprocess them uniformly. The resulting
file is written in place.

**Fallback threshold** (`--fallback-threshold`, default 0.25): if
`total_flagged / total_verses >= threshold` and a separate retry model is configured,
`retry-alignment` reverts to the refine-phase model instead. Rationale: a high flagged
rate indicates systemic quality issues better addressed by a cheap re-pass than targeted
expensive retries. The model actually used is always printed before the verse list.
Saved in `args._refine_llm_provider/model/reasoning_effort` before retry overrides are
applied; decision is made after scoring completes.

**Async support**: `--batch-mode async` submits retry verses to the provider
batch API (same three providers as `refine-alignment`). Job metadata carries
`"job_type": "retry"`. `fetch-batch` detects this and calls `merge_verse_results`
instead of writing fresh chapter files.

## GHA transitory data workflow (`scripts/copy-to-gha.py`, `scripts/copy-from-gha.py`)

Alignment runs on GHA need only the translation TSV for a specific config — not the full
contents of the Clear `alignments-*` repos. These two scripts implement a transitory
strategy: stage the minimum data in, run GHA, copy results back out.

**`copy-to-gha.py`** — run before triggering a GHA alignment job:
1. Copies all `*.tsv` files from `C:/git/Clear/alignments-<lang>/data/targets/<edition>/`
   into `./data/alignments/alignments-<lang>/data/targets/<edition>/`
2. If `C:/git/Clear/alignments-<lang>/exp/<edition>/<alignment_suffix>/` exists, copies
   its JSON files into the matching staging path (enables incremental GHA runs).
3. Patches `alignments_root:` in `configs/<edition>.yaml` to `./data/alignments`

After running: `git add` the TSV(s), any staged JSONs, and the patched YAML, commit,
push, then trigger the appropriate GHA workflow (`align-nt` or `align-ot`).

**`copy-from-gha.py`** — run after `git pull` brings GHA-committed results into the repo:
1. Copies `./data/alignments/alignments-<lang>/exp/<edition>/<alignment_suffix>/*.json`
   to `<clear_root>/alignments-<lang>/exp/<edition>/<alignment_suffix>/`
2. Copies `./data/alignments/alignments-<lang>/viz/<edition>/` into the Clear viz dir
   (silently skipped if not present)
3. Patches `alignments_root:` in `configs/<edition>.yaml` back to `<clear_root>`
4. Removes the edition-specific staged data from `./data/alignments/`:
   `alignments-<lang>/data/targets/<edition>/`, `exp/<edition>/`, `viz/<edition>/`

The `alignment_suffix` is read from the config YAML; defaults to `LLM-REFINED`.

Both scripts accept `--config <NAME>` (required), `--clear-root <path>` (default
`~/git/Clear-Bible`), and `--dry-run`. Neither script invokes git or GHA.

```bash
python scripts/copy-to-gha.py  --config JFA11
# ... git add / commit / push / trigger GHA ...
# ... git pull after GHA completes ...
python scripts/copy-from-gha.py --config JFA11
```

## OT GHA workflow (`scripts/ot_chapters.py`, `.github/workflows/align-ot.yml`)

The OT has 929 chapters (books 01–39), exceeding the 256-job GHA matrix limit. It is
split into four canonical sections, each triggered as a separate `workflow_dispatch` run:

| Section | Books | Chapters |
|---------|-------|----------|
| law | Gen–Deut (01–05) | 187 |
| history | Josh–Esth (06–17) | 249 |
| poetry | Job–Song (18–22) | 243 |
| prophets | Isa–Mal (23–39) | 250 |

All four sections fit under 256 with zero chapter bundling — every chapter gets its own
job (one-to-one with NT approach).

**`scripts/ot_chapters.py`** — parallel to `nt_chapters.py`:
- `--json --section <law|history|poetry|prophets>` — emit GHA matrix JSON for that section
- `--json --chapter BBCCC` or `--book BB` — single-chapter or single-book override
- `--status --config <NAME>` — per-chapter DONE/PENDING report
- `--table` — human-readable chapter list (omit `--section` to see all 929)

**`align-ot.yml`** workflow inputs:
- `config` (required) — edition config name, e.g. `BSB`
- `section` (required) — `law` / `history` / `poetry` / `prophets`
- `chapter` / `book` — optional single-chapter or single-book override
- `model`, `batch-mode`, `max-retry-passes` — same as `align-nt.yml`

Workflows can be triggered from the CLI without going to github.com:

```bash
gh workflow run align-ot.yml \
  --field config=BSB \
  --field section=law

gh workflow run align-nt.yml \
  --field config=BSB
```

**`scripts/alignment_summary.py`** now supports `--corpus ot --section <section>` to
produce a section-scoped step summary at the end of each `align-ot` run.

## OT versification handling (`refine/refine.py`, `refine/retry.py`)

Hebrew OT and English translation Bibles often differ in verse numbering (e.g. Jonah:
Hebrew 2:1 = English 1:17). WLCM source tokens are keyed by Hebrew verse IDs; BSB
target tokens are keyed by English verse IDs. Intersecting the two sets directly
produces mismatched source/target pairings and all-NEQ output.

**Fix**: `verse_ids` is determined by iterating BSB `target_verses` keys. For each
BSB verse, the source verse is resolved via `MigrateTarget.source_verse` — a field
stored in the target TSV that carries the WLCM verse ID for each BSB token.
Multi-source-verse cases (one BSB verse spanning multiple WLCM verses) use
`MigrateVerse.source_verse_range_end`. Output chapter files are keyed by BSB
(translation) verse IDs throughout.

This pattern is applied at 7 sites: `verse_ids` determination and two src_tokens
lookups each in `_process_corpus_sync` and `_process_corpus_async` in `refine.py`,
and three lookups in `retry.py` (`retry_chapter_sync` main loop, missing-verse
resubmit, `build_retry_chapter_batches`).

Source token lookup pattern:
```python
if tgt_verse and tgt_verse.words:
    src_start = next(iter(tgt_verse.words.values())).source_verse
    src_end = tgt_verse.source_verse_range_end
    if src_end and src_end > src_start:
        src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
    else:
        src_tokens = source_verses.get(src_start, [])
else:
    src_tokens = []
```

## OT source token display (`refine/prompt/common.py`)

WLCM source tokens have no `morph` field (always empty). `_format_source_token` falls
back to `pos` + `gloss` when `morph` is absent, giving the LLM part-of-speech context
and an English gloss for each Hebrew token. When proper WLCM morph data becomes
available, the `if token.morph:` branch takes priority automatically — no code change
needed.

## Testing

Run tests with:
```bash
poetry run pytest
```

For a quick smoke test of a specific LLM provider, use `test_gemini.py` (not committed —
local scratch file) or pass `--verse 41004003` or `--chapter 41004` to `refine-alignment`
to limit scope. `--chapter` is the natural unit for both sync and async modes.
