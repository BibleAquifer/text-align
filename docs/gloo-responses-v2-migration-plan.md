# Gloo Responses v2 migration plan (2026-09-03)

## Status

**Not started.** Decision pending a spike (see "Phase 0"). The team intends to migrate a
different, lower-profile tool to the Responses v2 API first, to gain experience with the
event/response shape before touching `text-align`'s Gloo path — which is the most
fragile part of this stack (long history of Cloudflare stream-drop / silent-stall
tuning; see the "Gloo AI provider" section of `CLAUDE.md`).

Supersedes the "do not migrate" decision in
`docs/gloo-responses-endpoint-investigation.md` (that was v1; this is v2) — but only
conditionally: the migration proceeds only if Phase 0 shows v2 is at least as reliable
as the current chat/completions + `tool_choice="auto"` setup.

## Why revisit

1. **Reasoning pass-through.** Responses v2 exposes `reasoning: {effort}`. We currently
   send no thinking config to any Gloo model (`CLAUDE.md`: "`reasoning_effort` is
   ignored" for Gloo). The `GET /platform/v2/models` catalog confirms both production
   models advertise `supports_reasoning: true`:
   - `gloo-deepseek-v4-pro` (first pass) — tools ✓, reasoning ✓, max_output 384000
   - `gloo-google-gemini-3.1-pro` (retry) — tools ✓, reasoning ✓, max_output 65500

   This is the single biggest reason to migrate: the retry pass would gain a real
   quality lever it does not have today.
2. **Conceptual fit.** We always send exactly one system prompt + one user message +
   one tool call, no conversation history. Responses is built for single-shot
   structured tasks; chat/completions is a multi-turn abstraction we don't use.
3. **`response_format` / structured outputs** could replace tool-calling entirely,
   sidestepping the `INTERNAL_ERROR`-on-forced-`tool_choice` issue that forced us onto
   `tool_choice="auto"`.
4. **Less wasted output.** v1 test: deepseek narrated a discarded markdown reasoning
   trace as `content` on chat/completions; Responses `auto` returned only the function
   call.
5. **`tradition: "evangelical"`** param may reduce `content_filter` false positives on
   biblical text.

## Endpoints

| Purpose | Method + URL | Auth |
|---|---|---|
| Responses v2 | `POST https://platform.ai.gloo.com/ai/v2/responses` | `Authorization: Bearer $GLOO_API_KEY` |
| Model catalog | `GET https://platform.ai.gloo.com/platform/v2/models` | none |

Docs: https://docs.gloo.com/api-guides/responses

## Request/response shape differences (v2 Responses vs. v2 chat/completions)

| chat/completions | Responses v2 |
|---|---|
| `messages: [{role, content}]` | `input` (string or typed array); system → top-level `instructions` |
| `max_tokens` | `max_output_tokens` |
| tool schema `{type:"function", function:{name, parameters}}` | flattened `{type:"function", name, parameters}` |
| (no reasoning control) | `reasoning: {effort: minimal|low|medium|high}` |
| response `choices[0].message.tool_calls[]` | typed `output[]` array; `function_call` items carry `.name`, `.arguments`, `.call_id` |
| streaming: `choices[].delta` inside every `data:` payload | streaming: paired `event: <type>` / `data: <json>` lines. Relevant events: `response.created`, `response.output_item.added`, `response.function_call_arguments.delta`, `response.output_item.done`, `response.completed` (usage only, no `output[]`), error variants |
| `finish_reason` (`stop`/`tool_calls`/`length`/`content_filter`/`error`) | `response.status` + `incomplete_details.reason`; errors as SSE error events |
| usage: `prompt_tokens` / `completion_tokens` | usage: `input_tokens` / `output_tokens` |
| multi-turn retry: append `assistant` + `tool` role messages | append `function_call` + `function_call_output` items to `input`, or thread via `previous_response_id` |

## Phase 0 — spike (do this first, gates everything else)

Rebuild the July harness against v2. Mirror
`docs/gloo-responses-endpoint-investigation.md`'s method:

- Same-content payloads: identical system prompt, user message, tool schema
  (`_NEUTRAL_TOOL_SCHEMA`), model, `stream=True` — differing only in the field
  names/shapes each API requires.
- **Test matrix:** {`gloo-deepseek-v4-pro`, `gloo-google-gemini-3.1-pro`} ×
  {`tool_choice=auto`, `tool_choice=required`} × {chat/completions v2, Responses v2}
  × {NT batch (Matt 1:1–5), OT batch — v1 was NT-only, a real gap}.
- **Also test:** `reasoning: {effort: "medium"}` on Responses — does it pass through to
  the routed model (visible in usage / latency / output quality)? This is the deciding
  factor.
- **Record per run:** verse count returned vs. expected, duplicate/truncated verses,
  wasted `content` chars, token usage, stream-drop/stall behavior, error shapes.

**Proceed to Phase 1 only if:** v2 Responses on `tool_choice="auto"` is clean for both
models on both NT and OT batches, AND `reasoning` demonstrably passes through. If v2
just trades one rare failure mode for another (as v1 did), stop and keep chat/completions.

Harness lives as a local scratch script (not committed), like `test_gemini.py`.

## Phase 1 — model catalog helper (independently useful, low risk, do regardless)

- Add `refine/gloo_models.py` (or a function in `llm.py`): fetch + cache
  `GET /platform/v2/models`, expose `get_gloo_model(id) -> dict | None` with
  `supports_tools`, `supports_reasoning`, `max_output_tokens`, `is_deprecated`,
  `pricing`.
- Wire into `cost_estimate.py` / `gloo_usage_log` for authoritative per-token rates
  (currently hand-maintained).
- On `_call_gloo` startup, warn if the configured model is `is_deprecated` or unknown.

## Phase 2 — migrate `_call_gloo` to Responses v2

1. `_GlooAuth`: parametrize the URL (add `_GLOO_RESPONSES_URL`); keep `post()` otherwise
   intact (same auth, same `timeout=(30, 90)` streaming tuning, same HTTPError
   body-append behavior).
2. Rewrite `_accumulate_gloo_stream` → `_accumulate_gloo_responses_stream`: consume
   `event:`/`data:` pairs, accumulate `function_call` arguments from
   `response.function_call_arguments.delta` (or read the complete string off
   `response.output_item.done`), capture usage from `response.completed`, map error
   events. Keep the `ChunkedEncodingError` / `Timeout` catch + re-raise for
   `_api_call_with_backoff`.
3. Return a normalized dict so downstream parsing (`_process_tool_call_data`,
   `_try_parse_json`, `validate_records`) is unchanged — same strategy as today
   ("Assembles the same shape as a non-streaming Gloo response").
4. Payload builder: `input`/`instructions`/`max_output_tokens`, flattened tool schema,
   `reasoning: {effort}` when `self.reasoning_effort` is set and the model's catalog
   entry has `supports_reasoning: true`.
5. Rework the retry loop (`_call_gloo` lines ~1435–1441): append `function_call` +
   `function_call_output` items to `input` instead of `assistant`/`tool` role messages.
6. Error handling: map `response.status` / `incomplete_details.reason` /  error events
   onto the existing `content_filter` / `error` / `length` branches.
7. Usage: read `input_tokens` / `output_tokens`; update `append_usage` call sites and
   `gloo_usage_log` if its schema assumes the old keys.
8. Re-verify the Anthropic prompt-cache path: does `X-Cache-TTL: 1h` still apply on
   `/ai/v2/responses` for `gloo-anthropic-*` models? Test explicitly.
9. Update `CLAUDE.md` "Gloo AI provider" section and remove/supersede the "no
   reasoning_effort pass-through" caveat if Phase 0 confirmed it.
10. Keep `_call_gloo` as the only touched provider path — no shared changes with
    openai/anthropic/google/openrouter/ollama.

## Phase 3 — validate end to end

- Run a full NT chapter and a full OT chapter through `refine-alignment` +
  `retry-alignment` on Gloo, compare scores/coverage against a pre-migration baseline
  on the same chapters.
- Confirm split-batch fallback still triggers correctly on a forced stream drop.
- `poetry run pytest`.

## Out of scope

- Async batch mode — Gloo never supported it; no change.
- Other providers.
- `image_generation` / vision — not used by this codebase.

## Caveats carried from the v1 investigation

- Small sample sizes; LLM run-to-run variance is real — treat spike failure counts as
  suggestive, not proven rates.
- Gloo docs are thin; behavior is largely empirical.
