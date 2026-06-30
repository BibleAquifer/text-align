# refine-alignment — Design Document

*Working document — subject to revision.*

---

## Purpose

`refine-alignment` is Stage 2 of the alignment workflow. It takes the output of one or more
automated alignment tools (ACAI, SIM-MIGRATED, DIFF-MIGRATED, …) for a given target edition,
presents each verse's source tokens, target tokens, and all candidate alignment records to an
LLM, and produces a single refined alignment JSON that applies the principles in
`alignment-principles-nt.md` (NT) or `alignment-principles-ot.md` (OT).

Output lands in `exp/<trg_ed>/<output-suffix>/` — a new experimental folder alongside the
automated tool outputs.

---

## New files

```
src/text_align/refine/
    __init__.py     — package stub
    source.py       — load SBLGNT.tsv / WLCM.tsv into verse-keyed dicts
    prompt.py       — system prompt + per-batch message builder
    llm.py          — provider-agnostic LLM call, tool-use schema, validation, retry
    refine.py       — CLI entry point (refine-alignment)
```

---

## Changes to existing files

| File | Change |
|---|---|
| `pyproject.toml` | Add `openai` and `anthropic` dependencies; add `refine-alignment` script entry |

No changes to `config.py` are needed. `refine.py` derives the exp base directory
(`<alignments_root>/alignments-<target_language>/exp/<target_edition>`) inline from
identity keys already present in the config, rather than adding a new derived key.

---

## `source.py`

Loads `data/sources/SBLGNT.tsv` (NT) or `data/sources/WLCM.tsv` (OT).
Both files are already present at `SOURCES = ROOT / "data" / "sources"`.

**`SourceToken` dataclass:** `id`, `text`, `strongs`, `gloss`, `gloss2`, `pos`, `morph`,
`lemma` (empty for WLCM which has no lemma column).

**`load_source_tsv(sources_dir, corpus)`** → `dict[str, list[SourceToken]]`
Keys by `BCVWPID(id).to_bcvid` — same key format used by `process_usfm_tsv` for target
verses, so lookups across source and target are consistent.

---

## `prompt.py`

### System prompt

A condensed rendering of `alignment-principles-nt.md` (or the OT equivalent) covering:

- Alignment direction: translation → source
- Primary vs secondary definitions and the common cases (prepositions from case, helping
  verbs, supplied pronouns, articles)
- Article rules: all four cases from §6
- Idiom flag (`meta.is_idiom`)
- Instructions: may split/merge/restructure records, may add NEQ records for tokens
  definitively determined to have no correspondent; must only use token IDs present
  in the verse's token lists

### Per-verse block format (inside a batch message)

```
--- VERSE 41004003 ---

SOURCE TOKENS (SBLGNT):
  n41004003001  ἀκούετε   verb  V-PAM-2P   gloss:"Listen"
  n41004003002  ἰδοὺ      intj             gloss:"behold"
  n41004003003  ἐξῆλθεν   verb  V-AAI-3S   gloss:"went out"
  n41004003004  ὁ         art   T-NSM      gloss:"the"
  n41004003005  σπείρων   verb  V-PAP-NSM  gloss:"sower"

TARGET TOKENS (NIV11):
  t001  "Listen"
  t002  "!"
  t003  "A"
  t004  "farmer"
  t005  "went"
  t006  "out"
  t007  "to"
  t008  "sow"

ALIGNMENT CANDIDATES:

[ACAI]
  source: [n41004003005]  target: [t004]

[SIM-MIGRATED]
  source: [n41004003001]  target: [t001]
  source: [n41004003003]  target: [t005 t006]
  source: [n41004003005]  target: [t004]

[DIFF-MIGRATED]
  source: [n41004003001]  target: [t001]
  source: [n41004003003]  target: [t005]
```

Multiple verse blocks are concatenated into one batch message.

---

## `llm.py` — Provider-agnostic LLM layer

### Multi-provider support

Two providers are supported; the active provider and model are configured per alignment
(see Config section). The LLM layer abstracts provider differences so `refine.py` makes
a single call regardless of provider.

| Provider | Key | Example models |
|---|---|---|
| OpenAI | `openai` | `gpt-5.2`, `gpt-5.4-mini` |
| Anthropic | `anthropic` | `claude-opus-4-6`, `claude-sonnet-4-6` |

Provider API keys are read from environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

### Tool: `submit_verse_alignments`

The model is forced to use this tool (`tool_choice` = forced). One tool call is made
**per verse** — the model returns a separate call for each verse in the batch. This maps
naturally to parallel tool calls (OpenAI) and multi-tool-use blocks (Anthropic).

**Tool input schema:**

```json
{
  "verse_id": "<BCV string>",
  "records": [
    {
      "source": ["<source_token_id>", "..."],
      "target": ["<target_token_id>", "..."],
      "meta": {
        "secondary": {
          "source": ["<id>", "..."],
          "target": ["<id>", "..."]
        },
        "is_idiom": true,
        "rel": "NEQ"
      }
    }
  ]
}
```

`meta` is optional. `meta.secondary` subkeys are optional. `meta.is_idiom` is optional. `meta.rel` is optional; the only current value is `"NEQ"`.

**NEQ records:** when `meta.rel` is `"NEQ"`, exactly one of `source` or `target` is a single-element list and the other is an empty list. `meta.secondary` is not applicable on NEQ records.

> **Internal representation only.** The per-record `meta.rel: "NEQ"` format is used within the tool schema and processing pipeline for convenience — the model emits a uniform list of records and some may be NEQ. Before writing the output file, NEQ records are separated out and their token IDs are written into `meta.nonEquivalent` at the group level (see Output format). The output file contains no `meta.rel` fields.

### Tool schema differences by provider

OpenAI wraps the schema in `{"type": "function", "function": {..., "parameters": ...}}`;
Anthropic uses `{"name": ..., "input_schema": ...}` directly. The `llm.py` layer handles
this translation internally — callers always see the same interface.

### Validation

After each batch response, every verse's records are validated:

- All `source` IDs must exist in the verse's source token set
- All `target` IDs must exist in the verse's target token set
- `meta.secondary.source` IDs must be a subset of `source`
- `meta.secondary.target` IDs must be a subset of `target`
- NEQ records (`meta.rel: "NEQ"`) must have exactly one non-empty array and one empty array; a NEQ record with two non-empty or two empty arrays is invalid and dropped
- A non-NEQ record with neither `source` nor `target` is dropped

Invalid records are removed from that verse's result. If a verse has *any* invalid records
the whole verse is flagged for retry.

### Retry logic

On validation failure the failed verses are retried using the same conversation thread —
the validation errors are appended as a follow-up user message:

```
The following verses had validation errors in your previous response.
Please resubmit corrected records for each.

VERSE 41004003:
  - record 2: unknown target ID: tXXX (not in this verse's target tokens)

Resubmit only the corrected verses.
```

- Maximum retries: configurable (`--max-retries`, default `2`)
- After exhausting retries, the last set of *valid* records for that verse is kept and
  the remaining errors are logged in a summary at the end

---

## `refine.py` — CLI

### Known alignment source types

```python
ALIGNMENT_SOURCE_TYPES = ["ACAI", "SIM-MIGRATED", "DIFF-MIGRATED"]
```

Expandable as new automated tools are added. Passed via `--alignment-sources`; validated
against this list.

### Source type → file path

```
<exp_dir> / <TYPE> / <corpus_id>-<target_edition>-manual.json
```

e.g. `exp/NIV11/ACAI/SBLGNT-NIV11-manual.json`

### Alignment JSON structure handling

Both flat (`alignment["records"]`) and SB 0.4 grouped
(`alignment["groups"][0]["records"]`) structures are read transparently, since ACAI
output uses groups and diff/sim-migrate use the flat form.

### CLI arguments

| Argument | Default | Notes |
|---|---|---|
| `--config` | — | YAML config name (existing system) |
| `--target-language` | — | ISO 639-3, e.g. `por` |
| `--target-edition` | — | e.g. `JFA11` |
| `--target-tsv-dir` | derived | kathairo TSVs for the target |
| `--output-dir` | derived | where to write refined JSON |
| `--output-suffix` | `LLM-REFINED` | names the output subdir under `exp/` |
| `--sources-dir` | `data/sources/` | SBLGNT.tsv / WLCM.tsv |
| `--alignment-sources` | all three types | subset of `ALIGNMENT_SOURCE_TYPES` |
| `--corpora` | `ot nt` | which corpora to process |
| `--llm-provider` | `openai` | `openai` or `anthropic` |
| `--llm-model` | `gpt-5.4-mini` | model name for the chosen provider |
| `--batch-size` | `5` | verses per API call |
| `--max-retries` | `2` | retry attempts on validation failure |
| `--verse` | — | single verse BCV for testing, e.g. `41004003` |
| `--creator` | `text-align` | alignment meta creator string |

`--output-suffix` is pre-parsed (before the main argparse run) so that
`load_config_from_args` can derive `output_dir = exp_dir / output_suffix` correctly,
consistent with the existing config derivation pattern.

### Processing loop

```
for each corpus (ot, nt):
    load source tokens (SBLGNT / WLCM)
    load target tokens (process_usfm_tsv)
    load each alignment source type → group records by verse
    collect union of verse IDs across all sources

    for each batch of N verses:
        build batch message (N verse blocks)
        call LLM → N tool-call responses
        validate each verse's records
        retry failed verses (up to max_retries)
        collect valid records (regular + NEQ)

    separate NEQ records (meta.rel: "NEQ") from regular records
    collect NEQ source/target token IDs → nonEquivalent lists
    write output alignment JSON
        records = regular records only
        meta.nonEquivalent = accumulated NEQ token ID lists
    print summary (total records, NEQ tokens, validation errors, retries)
```

### Output format

SB 0.4 `groups` structure, written via `write_alignment_json`. NEQ token IDs are stored in `meta.nonEquivalent` at the group level; `records` contains genuine correspondences only.

```json
{
  "format": "alignment",
  "version": "0.4",
  "groups": [{
    "type": "translation",
    "meta": {
      "creator": "text-align",
      "conformsTo": "0.4",
      "nonEquivalent": {
        "source": ["<source_token_id>", "..."],
        "target": ["<target_token_id>", "..."]
      }
    },
    "documents": [
      { "scheme": "BCVWP", "docid": "SBLGNT" },
      { "scheme": "BCVWP", "docid": "NIV11" }
    ],
    "roles": ["source", "target"],
    "records": [ ... ]
  }]
}
```

`meta.nonEquivalent` is omitted if no NEQ tokens were identified. Either subkey (`source`, `target`) may be omitted if empty.

---

## Config YAML additions

```yaml
# LLM provider and model — configurable per alignment project
llm_provider: openai
llm_model: gpt-5.4-mini

# Refinement settings
batch_size: 5
max_retries: 2
output_suffix: LLM-REFINED

# Which automated alignment sources to draw from
alignment_sources:
  - ACAI
  - SIM-MIGRATED
  - DIFF-MIGRATED
```

With `alignments_root` set, `exp_dir` and `output_dir` are derived automatically.

---

## Notes on glosses and non-English targets

The `gloss` column in SBLGNT.tsv/WLCM.tsv is an *English* gloss. It is useful context
when aligning an English translation, but irrelevant (and potentially misleading) when
aligning Portuguese, Tok Pisin, Bislama, or any other non-English language.

The system prompt and source token display therefore treat glosses as optional context:
glosses are shown in the prompt when the target language is English (`target_language:
eng`), and omitted otherwise. The LLM's knowledge of Greek and Hebrew morphology —
available from the `pos` and `morph` fields regardless of target language — is the
primary tool for applying case-driven and article rules.

Hebrew (`morph` in WLCM) is sparsely populated; the system prompt notes this and
instructs the LLM to rely on `pos` and surface form when morph is absent.

---

## Open questions

- **Batch size tuning**: Default of 5 verses per call is a starting estimate. May need
  adjustment based on context window usage and observed quality.
