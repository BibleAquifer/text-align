"""Provider batch-API helpers for refine-alignment async mode.

Google Gemini, OpenAI, and Anthropic are fully implemented.

A "chapter batch" is a list of dicts, one per LLM call:
    {
        "chapter_id":  "41003",         # BBCCC
        "batch_index": 0,               # 0-based within the chapter
        "verse_ids":   [...],           # BBCCCVVV strings in the call
        "system_prompt": "...",
        "user_message":  "...",
    }

Job metadata files live at  jobs/{provider}/{safe_job_id}.json.
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any

from .llm import (
    TOOL_NAME,
    _NEUTRAL_TOOL_SCHEMA,
    _anthropic_tool_schema,
    _gemini_tool_schema,
    _openai_tool_schema,
    _openai_responses_tool_schema,
    _iter_verse_entries,
    validate_records,
)
from .prompt import reverse_map_records


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _safe_filename(name: str) -> str:
    """Convert a job name like 'batches/abc123' to a safe filename stem."""
    return name.replace("/", "_").replace(":", "_")


def save_job_metadata(jobs_dir: Path, provider: str, stem: str, metadata: dict) -> Path:
    """Write job metadata JSON to jobs/{provider}/{stem}.json and return the path."""
    provider_dir = jobs_dir / provider
    provider_dir.mkdir(parents=True, exist_ok=True)
    path = provider_dir / f"{stem}.json"
    if path.exists():
        raise FileExistsError(
            f"Job metadata file already exists: {path}\n"
            f"This should not happen — check for a duplicate job submission."
        )
    with path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return path


def load_job_metadata(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _process_function_call_data(
    data: dict,
    chapter_id: str,
    chapter_results: dict[str, dict[str, list[dict]]],
    verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
    verse_source_ids: dict[str, set[str]],
    verse_target_ids: dict[str, set[str]],
    all_errors: list[str],
    all_san: list[str],
) -> None:
    """Process one function-call data dict: map tokens, validate, accumulate results."""
    block_errors: list[str] = []
    for verse_id, records in _iter_verse_entries(data, block_errors):
        if verse_token_maps:
            src_map, tgt_map = verse_token_maps.get(verse_id, ({}, {}))
            records, map_errors = reverse_map_records(records, src_map, tgt_map)
            all_errors.extend(f"VERSE {verse_id}: {e}" for e in map_errors)
        valid, errs, san = validate_records(
            records,
            verse_source_ids.get(verse_id, set()),
            verse_target_ids.get(verse_id, set()),
        )
        all_san.extend(f"VERSE {verse_id}: {d}" for d in san)
        if valid:
            chapter_results.setdefault(chapter_id, {})[verse_id] = valid
        if errs:
            all_errors.extend(f"VERSE {verse_id}: {e}" for e in errs)
    all_errors.extend(block_errors)


# ---------------------------------------------------------------------------
# Google (Gemini) batch API
# ---------------------------------------------------------------------------

def _build_gemini_gen_config(
    reasoning_effort: str | None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
):
    """Build a GenerateContentConfig for use in InlinedRequest.config."""
    from google.genai import types

    tool = _gemini_tool_schema(_NEUTRAL_TOOL_SCHEMA)
    thinking_config = None
    if reasoning_effort and reasoning_effort != "none":
        thinking_config = types.ThinkingConfig(thinking_level=reasoning_effort)
    cfg: dict = dict(
        tools=[tool],
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="ANY",
                allowed_function_names=[TOOL_NAME],
            )
        ),
        thinking_config=thinking_config,
    )
    if temperature is not None:
        cfg["temperature"] = temperature
    if max_output_tokens is not None:
        cfg["max_output_tokens"] = max_output_tokens
    return types.GenerateContentConfig(**cfg)


def _build_google_inlined_requests(
    chapter_batches: list[dict],
    reasoning_effort: str | None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
) -> list[Any]:
    """Convert chapter_batches to a list of InlinedRequest objects."""
    from google.genai import types

    base_config = _build_gemini_gen_config(reasoning_effort, temperature, max_output_tokens)
    requests = []
    for idx, cb in enumerate(chapter_batches):
        per_request_config = types.GenerateContentConfig(
            system_instruction=cb["system_prompt"],
            tools=base_config.tools,
            tool_config=base_config.tool_config,
            thinking_config=base_config.thinking_config,
            **({"temperature": temperature} if temperature is not None else {}),
            **({"max_output_tokens": max_output_tokens} if max_output_tokens is not None else {}),
        )
        requests.append(types.InlinedRequest(
            contents=[types.Content(role="user", parts=[types.Part(text=cb["user_message"])])],
            config=per_request_config,
            metadata={"request_index": str(idx)},
        ))
    return requests


def submit_google(
    genai_client: Any,
    model: str,
    reasoning_effort: str | None,
    chapter_batches: list[dict],
    jobs_dir: Path,
    job_metadata_base: dict,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
) -> tuple[str, Path]:
    """Submit chapter_batches to Google's batch API.

    Returns (job_name, metadata_file_path).
    ``job_metadata_base`` must already contain: target_edition, target_language,
    corpus, corpus_id, output_dir, creator, sources_dir, target_tsv_dir.
    """
    from google.genai import types

    inlined = _build_google_inlined_requests(
        chapter_batches, reasoning_effort, temperature, max_output_tokens
    )

    batch_job = genai_client.batches.create(
        model=model,
        src=types.BatchJobSource(inlined_requests=inlined),
    )
    job_name: str = batch_job.name

    # Build a human-readable filename: EDITION-corpus-YYYYMMDD-SHORTID
    edition = job_metadata_base.get("target_edition", "unknown")
    corpus = job_metadata_base.get("corpus", "")
    date_str = datetime.date.today().strftime("%Y%m%d")
    short_id = job_name.split("/")[-1][-8:]
    stem = f"{edition}-{corpus}-{date_str}-{short_id}"

    request_meta = [
        {
            "request_index": idx,
            "chapter_id": cb["chapter_id"],
            "batch_index": cb["batch_index"],
            "verse_ids": cb["verse_ids"],
        }
        for idx, cb in enumerate(chapter_batches)
    ]

    metadata = {
        **job_metadata_base,
        "provider": "google",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "job_name": job_name,
        "submitted_at": datetime.datetime.now().isoformat(),
        "requests": request_meta,
    }

    path = save_job_metadata(jobs_dir, "google", stem, metadata)
    return job_name, path


def poll_google(genai_client: Any, job_name: str) -> str:
    """Return the current state string for a Google batch job."""
    job = genai_client.batches.get(name=job_name)
    return job.state.name


def retrieve_google(
    genai_client: Any,
    job_name: str,
    requests_meta: list[dict],
    verse_source_ids: dict[str, set[str]],
    verse_target_ids: dict[str, set[str]],
    verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None = None,
) -> tuple[dict[str, dict[str, list[dict]]], list[str], list[str]]:
    """Fetch completed Google batch results and validate alignment records.

    Returns:
        ({chapter_id: {verse_id: [records]}}, error_messages, san_details)
    """
    job = genai_client.batches.get(name=job_name)
    inlined_responses = (job.dest.inlined_responses or []) if job.dest else []

    # Build index → request_meta map for matching (API may not preserve order)
    index_map: dict[int, dict] = {r["request_index"]: r for r in requests_meta}

    chapter_results: dict[str, dict[str, list[dict]]] = {}
    all_errors: list[str] = []
    all_san: list[str] = []

    for resp in inlined_responses:
        # Determine which request this response belongs to
        meta = resp.metadata or {}
        try:
            req_idx = int(meta.get("request_index", -1))
        except (TypeError, ValueError):
            req_idx = -1
        req = index_map.get(req_idx)
        if req is None:
            all_errors.append(
                f"Response has unknown request_index {req_idx!r} — skipping"
            )
            continue

        chapter_id = req["chapter_id"]
        verse_ids = req["verse_ids"]

        if resp.error:
            all_errors.append(
                f"Chapter {chapter_id} batch {req['batch_index']}: "
                f"request error: {resp.error}"
            )
            continue

        gen_response = resp.response
        if gen_response is None or not gen_response.candidates:
            all_errors.append(
                f"Chapter {chapter_id} batch {req['batch_index']}: empty response"
            )
            continue

        candidate = gen_response.candidates[0]
        finish_reason = getattr(candidate, "finish_reason", None)
        if finish_reason is not None and "MAX_TOKENS" in str(finish_reason):
            print(
                f"  WARNING: Chapter {chapter_id} batch {req['batch_index']} truncated "
                f"(finish_reason=MAX_TOKENS) — some verses may be missing."
            )

        function_calls = [
            part.function_call
            for part in (candidate.content.parts if candidate.content else [])
            if getattr(part, "function_call", None)
        ]

        for fc in function_calls:
            try:
                data = fc.args if isinstance(fc.args, dict) else dict(fc.args)
            except Exception as exc:
                all_errors.append(
                    f"Chapter {chapter_id} batch {req['batch_index']}: "
                    f"could not read function call args: {exc}"
                )
                continue
            _process_function_call_data(
                data, chapter_id, chapter_results,
                verse_token_maps, verse_source_ids, verse_target_ids,
                all_errors, all_san,
            )

    return chapter_results, all_errors, all_san


# ---------------------------------------------------------------------------
# Terminal batch-job states (re-exported for fetch_batch.py)
# ---------------------------------------------------------------------------

_GOOGLE_SUCCEEDED = "JOB_STATE_SUCCEEDED"
_GOOGLE_FAILED = "JOB_STATE_FAILED"
_GOOGLE_CANCELLED = "JOB_STATE_CANCELLED"
_GOOGLE_TERMINAL = frozenset({_GOOGLE_SUCCEEDED, _GOOGLE_FAILED, _GOOGLE_CANCELLED})

_OPENAI_SUCCEEDED = "completed"
_OPENAI_FAILED = "failed"
_OPENAI_EXPIRED = "expired"
_OPENAI_CANCELLED = "cancelled"
_OPENAI_TERMINAL = frozenset({_OPENAI_SUCCEEDED, _OPENAI_FAILED, _OPENAI_EXPIRED, _OPENAI_CANCELLED})

_ANTHROPIC_ENDED = "ended"


# ---------------------------------------------------------------------------
# OpenAI batch API
# ---------------------------------------------------------------------------


def submit_openai(
    openai_client: Any,
    model: str,
    reasoning_effort: str | None,
    chapter_batches: list[dict],
    jobs_dir: Path,
    job_metadata_base: dict,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
) -> tuple[str, Path]:
    """Submit chapter_batches to OpenAI's batch API.

    Uses /v1/responses when reasoning_effort is set, /v1/chat/completions otherwise.
    Returns (batch_id, metadata_file_path).
    """
    import io

    use_responses = reasoning_effort is not None
    endpoint = "/v1/responses" if use_responses else "/v1/chat/completions"

    lines: list[str] = []
    for idx, cb in enumerate(chapter_batches):
        if use_responses:
            body: dict = {
                "model": model,
                "input": [
                    {"role": "system", "content": cb["system_prompt"]},
                    {"role": "user", "content": cb["user_message"]},
                ],
                "tools": [_openai_responses_tool_schema(_NEUTRAL_TOOL_SCHEMA)],
                "tool_choice": {"type": "function", "name": TOOL_NAME},
                "reasoning": {"effort": reasoning_effort},
            }
            # temperature is fixed for reasoning models; only pass max_output_tokens
            if max_output_tokens is not None:
                body["max_output_tokens"] = max_output_tokens
        else:
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": cb["system_prompt"]},
                    {"role": "user", "content": cb["user_message"]},
                ],
                "tools": [_openai_tool_schema(_NEUTRAL_TOOL_SCHEMA)],
                "tool_choice": {"type": "function", "function": {"name": TOOL_NAME}},
            }
            if temperature is not None:
                body["temperature"] = temperature
            if max_output_tokens is not None:
                body["max_completion_tokens"] = max_output_tokens
        lines.append(json.dumps({
            "custom_id": str(idx),
            "method": "POST",
            "url": endpoint,
            "body": body,
        }))

    jsonl_bytes = ("\n".join(lines) + "\n").encode("utf-8")

    upload = openai_client.files.create(
        file=("batch.jsonl", io.BytesIO(jsonl_bytes), "application/jsonl"),
        purpose="batch",
    )
    input_file_id: str = upload.id

    batch = openai_client.batches.create(
        input_file_id=input_file_id,
        endpoint=endpoint,
        completion_window="24h",
    )
    batch_id: str = batch.id

    edition = job_metadata_base.get("target_edition", "unknown")
    corpus = job_metadata_base.get("corpus", "")
    date_str = datetime.date.today().strftime("%Y%m%d")
    short_id = batch_id[-8:]
    stem = f"{edition}-{corpus}-{date_str}-{short_id}"

    request_meta = [
        {
            "request_index": idx,
            "chapter_id": cb["chapter_id"],
            "batch_index": cb["batch_index"],
            "verse_ids": cb["verse_ids"],
        }
        for idx, cb in enumerate(chapter_batches)
    ]

    metadata = {
        **job_metadata_base,
        "provider": "openai",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "use_responses_api": use_responses,
        "batch_id": batch_id,
        "input_file_id": input_file_id,
        "submitted_at": datetime.datetime.now().isoformat(),
        "requests": request_meta,
    }

    path = save_job_metadata(jobs_dir, "openai", stem, metadata)
    return batch_id, path


def poll_openai(openai_client: Any, batch_id: str) -> str:
    """Return the current status string for an OpenAI batch job."""
    batch = openai_client.batches.retrieve(batch_id)
    return batch.status


def retrieve_openai(
    openai_client: Any,
    batch_id: str,
    requests_meta: list[dict],
    verse_source_ids: dict[str, set[str]],
    verse_target_ids: dict[str, set[str]],
    verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None = None,
    use_responses_api: bool = False,
) -> tuple[dict[str, dict[str, list[dict]]], list[str], list[str]]:
    """Fetch completed OpenAI batch results and validate alignment records.

    Returns:
        ({chapter_id: {verse_id: [records]}}, error_messages, san_details)
    """
    batch = openai_client.batches.retrieve(batch_id)
    if not batch.output_file_id:
        return {}, [f"Batch {batch_id} has no output file (status: {batch.status})"], []

    content = openai_client.files.content(batch.output_file_id).text

    index_map: dict[int, dict] = {r["request_index"]: r for r in requests_meta}

    chapter_results: dict[str, dict[str, list[dict]]] = {}
    all_errors: list[str] = []
    all_san: list[str] = []

    for line in content.strip().splitlines():
        if not line.strip():
            continue
        try:
            result = json.loads(line)
        except json.JSONDecodeError as exc:
            all_errors.append(f"JSONL parse error: {exc}")
            continue

        custom_id = result.get("custom_id", "")
        try:
            req_idx = int(custom_id)
        except (TypeError, ValueError):
            all_errors.append(f"Cannot parse custom_id {custom_id!r} — skipping")
            continue

        req = index_map.get(req_idx)
        if req is None:
            all_errors.append(f"Response has unknown request_index {req_idx!r} — skipping")
            continue

        chapter_id = req["chapter_id"]

        if result.get("error"):
            all_errors.append(
                f"Chapter {chapter_id} batch {req['batch_index']}: "
                f"request error: {result['error']}"
            )
            continue

        response = result.get("response") or {}
        status_code = response.get("status_code")
        if status_code != 200:
            all_errors.append(
                f"Chapter {chapter_id} batch {req['batch_index']}: HTTP {status_code}"
            )
            continue

        body = response.get("body") or {}

        # Extract function call argument dicts from the response body
        function_args_list: list[dict] = []
        if use_responses_api:
            for item in body.get("output", []):
                if item.get("type") == "function_call":
                    try:
                        function_args_list.append(json.loads(item.get("arguments", "{}")))
                    except json.JSONDecodeError as exc:
                        all_errors.append(
                            f"Chapter {chapter_id} batch {req['batch_index']}: "
                            f"JSON parse error in function call: {exc}"
                        )
        else:
            choices = body.get("choices") or []
            if not choices:
                all_errors.append(
                    f"Chapter {chapter_id} batch {req['batch_index']}: empty choices"
                )
                continue
            if choices[0].get("finish_reason") == "length":
                print(
                    f"  WARNING: Chapter {chapter_id} batch {req['batch_index']} truncated "
                    f"(finish_reason=length) — some verses may be missing."
                )
            tool_calls = (choices[0].get("message") or {}).get("tool_calls") or []
            for tc in tool_calls:
                try:
                    function_args_list.append(
                        json.loads((tc.get("function") or {}).get("arguments", "{}"))
                    )
                except json.JSONDecodeError as exc:
                    all_errors.append(
                        f"Chapter {chapter_id} batch {req['batch_index']}: "
                        f"JSON parse error: {exc}"
                    )

        for data in function_args_list:
            _process_function_call_data(
                data, chapter_id, chapter_results,
                verse_token_maps, verse_source_ids, verse_target_ids,
                all_errors, all_san,
            )

    return chapter_results, all_errors, all_san


# ---------------------------------------------------------------------------
# Anthropic batch API
# ---------------------------------------------------------------------------


def submit_anthropic(
    anthropic_client: Any,
    model: str,
    reasoning_effort: str | None,
    chapter_batches: list[dict],
    jobs_dir: Path,
    job_metadata_base: dict,
    temperature: float | None = None,
    max_output_tokens: int = 32000,
) -> tuple[str, Path]:
    """Submit chapter_batches to Anthropic's Message Batches API.

    Returns (batch_id, metadata_file_path).
    """
    tool_schema = [_anthropic_tool_schema(_NEUTRAL_TOOL_SCHEMA)]

    requests = []
    for idx, cb in enumerate(chapter_batches):
        params: dict = {
            "model": model,
            "max_tokens": max_output_tokens,
            "system": cb["system_prompt"],
            "messages": [{"role": "user", "content": cb["user_message"]}],
            "tools": tool_schema,
            "tool_choice": {"type": "tool", "name": TOOL_NAME},
        }
        if temperature is not None:
            params["temperature"] = temperature
        requests.append({"custom_id": str(idx), "params": params})

    batch = anthropic_client.messages.batches.create(requests=requests)
    batch_id: str = batch.id

    edition = job_metadata_base.get("target_edition", "unknown")
    corpus = job_metadata_base.get("corpus", "")
    date_str = datetime.date.today().strftime("%Y%m%d")
    short_id = batch_id[-8:]
    stem = f"{edition}-{corpus}-{date_str}-{short_id}"

    request_meta = [
        {
            "request_index": idx,
            "chapter_id": cb["chapter_id"],
            "batch_index": cb["batch_index"],
            "verse_ids": cb["verse_ids"],
        }
        for idx, cb in enumerate(chapter_batches)
    ]

    metadata = {
        **job_metadata_base,
        "provider": "anthropic",
        "model": model,
        "reasoning_effort": reasoning_effort,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "batch_id": batch_id,
        "submitted_at": datetime.datetime.now().isoformat(),
        "requests": request_meta,
    }

    path = save_job_metadata(jobs_dir, "anthropic", stem, metadata)
    return batch_id, path


def poll_anthropic(anthropic_client: Any, batch_id: str) -> str:
    """Return the current processing_status for an Anthropic batch job."""
    batch = anthropic_client.messages.batches.retrieve(batch_id)
    return batch.processing_status


def retrieve_anthropic(
    anthropic_client: Any,
    batch_id: str,
    requests_meta: list[dict],
    verse_source_ids: dict[str, set[str]],
    verse_target_ids: dict[str, set[str]],
    verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None = None,
) -> tuple[dict[str, dict[str, list[dict]]], list[str], list[str]]:
    """Fetch completed Anthropic batch results and validate alignment records.

    Returns:
        ({chapter_id: {verse_id: [records]}}, error_messages, san_details)
    """
    index_map: dict[int, dict] = {r["request_index"]: r for r in requests_meta}

    chapter_results: dict[str, dict[str, list[dict]]] = {}
    all_errors: list[str] = []
    all_san: list[str] = []

    for result in anthropic_client.messages.batches.results(batch_id):
        try:
            req_idx = int(result.custom_id)
        except (TypeError, ValueError):
            all_errors.append(f"Cannot parse custom_id {result.custom_id!r} — skipping")
            continue

        req = index_map.get(req_idx)
        if req is None:
            all_errors.append(f"Response has unknown request_index {req_idx!r} — skipping")
            continue

        chapter_id = req["chapter_id"]

        result_type = result.result.type
        if result_type != "succeeded":
            all_errors.append(
                f"Chapter {chapter_id} batch {req['batch_index']}: "
                f"result type {result_type!r}"
            )
            continue

        message = result.result.message

        if message.stop_reason == "max_tokens":
            print(
                f"  WARNING: Chapter {chapter_id} batch {req['batch_index']} truncated "
                f"(stop_reason=max_tokens) — some verses may be missing."
            )

        tool_use_blocks = [b for b in message.content if b.type == "tool_use"]

        for block in tool_use_blocks:
            _process_function_call_data(
                block.input, chapter_id, chapter_results,
                verse_token_maps, verse_source_ids, verse_target_ids,
                all_errors, all_san,
            )

    return chapter_results, all_errors, all_san


# ---------------------------------------------------------------------------
# Provider dispatcher
# ---------------------------------------------------------------------------

def submit_batch_job(
    provider: str,
    model: str,
    reasoning_effort: str | None,
    chapter_batches: list[dict],
    jobs_dir: Path,
    job_metadata_base: dict,
    temperature: float | None,
    max_output_tokens: int | None,
) -> tuple[str, Path]:
    """Dispatch chapter_batches to the appropriate provider's batch API.

    Returns (job_id, metadata_file_path).
    """
    if provider == "google":
        from google import genai as _genai
        client = _genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        return submit_google(
            genai_client=client, model=model, reasoning_effort=reasoning_effort,
            chapter_batches=chapter_batches, jobs_dir=jobs_dir,
            job_metadata_base=job_metadata_base,
            temperature=temperature, max_output_tokens=max_output_tokens,
        )
    elif provider == "openai":
        import openai as _openai
        client = _openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        return submit_openai(
            openai_client=client, model=model, reasoning_effort=reasoning_effort,
            chapter_batches=chapter_batches, jobs_dir=jobs_dir,
            job_metadata_base=job_metadata_base,
            temperature=temperature, max_output_tokens=max_output_tokens,
        )
    elif provider == "anthropic":
        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        return submit_anthropic(
            anthropic_client=client, model=model, reasoning_effort=reasoning_effort,
            chapter_batches=chapter_batches, jobs_dir=jobs_dir,
            job_metadata_base=job_metadata_base,
            temperature=temperature, max_output_tokens=max_output_tokens,
        )
    else:
        raise ValueError(
            f"Async batch mode not supported for provider {provider!r}. "
            f"Use google, openai, or anthropic."
        )


