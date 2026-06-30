# Async Batch API Plan

## Goal

Add an async batch mode to `refine-alignment` that submits LLM requests to
provider batch APIs (starting with Google Gemini) instead of blocking on
synchronous calls. Batch APIs typically offer 50% cost reduction at the cost
of multi-hour turnaround.

Simultaneously, change output granularity from one-file-per-corpus to
one-file-per-chapter, and add book/chapter range filtering arguments.

---

## Output file naming

Chapter-based files replace the existing corpus-level files:

```
SBLGNT-OENGB-41-003-manual.json   ← book 41 (Mark), chapter 003
SBLGNT-OENGB-41-004-manual.json
WLCM-OENGB-01-001-manual.json
```

Format: `{corpus_id}-{edition}-{BB}-{CCC}-manual.json`
where `BB` is the 2-digit book number and `CCC` is the zero-padded 3-digit chapter.

The internal JSON structure is identical to the current corpus-level SB 0.4
format; it just contains records for only one chapter.

---

## New range-filtering arguments

All mutually exclusive with each other and with the existing `--verse` /
`--verse-range` args.

| Arg | Format | Example |
|-----|--------|---------|
| `--book BB` | 2-digit book | `--book 41` |
| `--book-range BB BB` | 2-digit book start/end | `--book-range 41 44` |
| `--chapter BBCCC` | 5-digit chapter | `--chapter 41003` |
| `--chapter-range BBCCC BBCCC` | 5-digit chapter start/end | `--chapter-range 41001 41016` |

Filtering is implemented by string-prefix comparison on the 8-char
`BBCCCVVV` verse IDs already used throughout the codebase (no new biblelib
imports needed — `vid[:2]` = book, `vid[:5]` = chapter).

---

## Batch mode arguments

```
--batch-mode  sync (default) | async
--jobs-dir    PATH   default: {repo_root}/jobs/
```

`sync` is the existing behavior: call LLM synchronously for each
batch-of-verses, write chapter files as results arrive.

`async` submits all chapter LLM calls to the provider's batch API, saves
job metadata, and exits. A separate `fetch-batch` command retrieves results
and writes the chapter files.

---

## Jobs directory layout

```
jobs/
  google/
    {job_name_escaped}.json     ← one file per submitted batch job
  anthropic/
    {batch_id}.json
  openai/
    {batch_id}.json
```

Each metadata file contains everything needed for `fetch-batch` to retrieve
and write results independently:

```json
{
  "provider": "google",
  "model": "gemini-2.0-flash-001",
  "reasoning_effort": null,
  "job_name": "batches/abc123",
  "submitted_at": "2026-04-22T14:30:00",
  "target_edition": "OENGB",
  "target_language": "eng",
  "corpus": "nt",
  "corpus_id": "SBLGNT",
  "output_dir": "/path/to/exp/OENGB/LLM-REFINED",
  "creator": "text-align",
  "requests": [
    {
      "request_index": 0,
      "chapter_id": "41003",
      "batch_index": 0,
      "verse_ids": ["41003001", "41003002", "41003003", "41003004", "41003005"]
    },
    ...
  ]
}
```

`request_index` maps to the position of the `InlinedResponse` in Google's
response array. `chapter_id` + `batch_index` identify which chunk of which
chapter the request covers; multiple requests may cover the same chapter when
the chapter has more verses than `--batch-size`.

---

## Files to create or modify

### New: `src/text_align/refine/async_batch.py`

Provider-specific batch submission and retrieval helpers.

**Google (implemented first):**
- `build_google_requests(chapter_batches, gen_config) -> list[InlinedRequest]`
  Converts pre-built `(system_prompt, user_message, verse_ids)` tuples to
  `types.InlinedRequest` objects. Uses `InlinedRequest.metadata` (a
  `dict[str, str]`) to embed `request_index` for result matching.
- `submit_google(client, model, gen_config, requests, jobs_dir, job_metadata) -> str`
  Calls `client.batches.create(...)`, saves metadata JSON, returns `job_name`.
- `poll_google(client, job_name) -> str`
  Returns job state string (e.g. `JOB_STATE_SUCCEEDED`).
- `retrieve_google(client, job_name, job_metadata) -> dict[str, dict[str, list[dict]]]`
  Fetches the completed batch, maps `InlinedResponse` objects back to verse
  results using `request_index` from metadata, validates records, returns
  `{chapter_id: {verse_id: records}}`.

**Anthropic and OpenAI:** stub functions with `NotImplementedError` and TODO
comments. Wire up later.

**Shared:**
- `save_job_metadata(jobs_dir, provider, job_id, metadata) -> Path`
- `load_job_metadata(path) -> dict`

### Modified: `src/text_align/refine/refine.py`

1. Add `--book`, `--book-range`, `--chapter`, `--chapter-range` to `parse_args()`.
2. Extract `_filter_verse_ids(verse_ids, args) -> list[str]` helper that
   applies whichever range filter is active.
3. Refactor `process_corpus` to group LLM results by chapter and write one
   output file per chapter (both in sync and async submission paths).
4. Add `--batch-mode` and `--jobs-dir` args.
5. In `async` mode: collect all chapter-batch payloads first, then call
   `async_batch.submit_*()` instead of `llm_client.call_batch()`.

### New: `src/text_align/refine/fetch_batch.py` (CLI: `fetch-batch`)

```
fetch-batch <job-metadata-file> [--poll] [--wait] [--wait-interval SECONDS]
```

- `(no flag)` — fetch once; error if not done yet.
- `--poll` — print status and exit (no error if still running).
- `--wait` — block, sleeping `--wait-interval` seconds between checks, until
  done or failed.

On success: validates responses, writes chapter JSON files, prints summary.
On failure: prints error state, exits non-zero.

### Modified: `src/text_align/burrito/AlignmentSet.py`

Relax `assert self.alignmentpath.exists()` so it only fires when
`alignmentpath_override` is `None`. When an override is supplied, trust the
caller (the chapter-file path is a sentinel; the reader will use pre-merged
data).

### Modified: `src/text_align/burrito/alignments.py`

Add `AlignmentsReader.from_chapter_files(paths, alignmentset, ...)` class
method. It merges `groups[0].records` from each chapter file (preserving
`neq_source`, `neq_target`, and `group_meta` from the first file), then
calls `read_alignments(data=merged_data)`. The `read_alignments` method gains
an optional `data` parameter to accept pre-merged dicts.

### Modified: `src/text_align/render/html.py`

At the start of `main()`, after resolving `adir`, check whether the alignment
dir contains chapter files matching `{sourceid}-{edition}-??-???-manual.json`.
If yes, call `AlignmentsReader.from_chapter_files(...)` directly and skip the
normal `AlignmentSet`-based load path. If no chapter files are found, continue
with the existing single-file path.

### Modified: `pyproject.toml`

Add `fetch-batch = "text_align.refine.fetch_batch:main"` to
`[tool.poetry.scripts]`.

---

## Provider batch API notes

### Google Gemini (`google-genai` SDK)

```python
# Submit
batch_job = client.batches.create(
    model=model,
    src=types.BatchJobSource(inlined_requests=requests),
)
job_name = batch_job.name   # e.g. "batches/abc123"

# Poll
job = client.batches.get(name=job_name)
job.state  # "JOB_STATE_PENDING" | "JOB_STATE_RUNNING" | "JOB_STATE_SUCCEEDED" | ...

# Retrieve (when state == JOB_STATE_SUCCEEDED)
responses = job.dest.inlined_responses  # list[InlinedResponse]
# Each InlinedResponse: .response (GenerateContentResponse), .metadata (dict), .error
```

Each `InlinedRequest` carries `metadata={"request_index": "0"}` so that
response ordering can be matched back to verse chunk metadata (the API does
not guarantee output order).

### Anthropic (planned, not implemented yet)

`client.messages.batches.create(requests=[...])` → `batch_id`

### OpenAI (planned, not implemented yet)

`client.batches.create(input_file_id=..., ...)` → `batch_id` (requires
uploading a JSONL file first)

---

## Render-alignment backward compatibility

The visualizer continues to work with existing corpus-level files unchanged.
Chapter-file detection is additive: if `{sourceid}-{edition}-??-???-manual.json`
files exist in the alignment dir, they are used; otherwise the tool falls back
to the single-file path.

When chapter files are present, `group_meta` (containing LLM provider/model
info for the header row) is taken from the first file loaded. If chapters were
processed with different models (unlikely but possible), only the first is
reflected in the header.
