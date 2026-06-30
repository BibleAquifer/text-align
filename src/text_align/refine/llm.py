"""Provider-agnostic LLM call layer for refine-alignment.

Supports OpenAI, Anthropic, Google (Gemini), OpenRouter, Gloo, and Ollama.
Provider packages are imported lazily so only the package for the active
provider needs to be installed.

Environment variables:
    OPENAI_API_KEY        — required when provider is "openai"
    ANTHROPIC_API_KEY     — required when provider is "anthropic"
    GEMINI_API_KEY        — required when provider is "google"
    OPENROUTER_API_KEY    — required when provider is "openrouter"
    GLOO_CLIENT_ID        — required when provider is "gloo"
    GLOO_CLIENT_SECRET    — required when provider is "gloo"
    OLLAMA_BASE_URL       — base URL for provider "ollama" (default: http://localhost:11434/v1)
"""

import base64
import json
import os
import random
import time

import requests
from dotenv import load_dotenv

from .prompt import reverse_map_records

load_dotenv()

# ---------------------------------------------------------------------------
# Tool schema
# ---------------------------------------------------------------------------

TOOL_NAME = "submit_verse_alignments"

# Models known to reject tool_choice; omit it from the first call rather than
# trying and catching the error.
_TOOL_CHOICE_INCOMPATIBLE: frozenset[str] = frozenset({
    "deepseek/deepseek-v4-pro",   # openrouter
    # "gloo-deepseek-v4-pro",     # gloo
    "gloo/gloo-qwen-3.7-plus",    # gloo
})

# Neutral tool schema; translated to provider-specific format before each call.
# The tool accepts ALL verses in the batch in a single call so that providers
# which only make one forced tool call per turn still return every verse.
_NEUTRAL_TOOL_SCHEMA: dict = {
    "name": TOOL_NAME,
    "description": (
        "Submit refined alignment records for every verse in the batch. "
        "Include one entry per verse — do not omit any verse from the batch."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "verses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "verse_id": {"type": "string"},
                        "records": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "description": "Source token IDs (integers from the token list — not word strings).",
                                    },
                                    "target": {
                                        "type": "array",
                                        "items": {"type": "integer"},
                                        "description": "Target token IDs (integers from the token list — not word strings).",
                                    },
                                    "meta": {
                                        "type": "object",
                                        "properties": {
                                            "secondary": {
                                                "type": "object",
                                                "properties": {
                                                    "source": {
                                                        "type": "array",
                                                        "items": {"type": "integer"},
                                                        "description": "Source token IDs (integers — not word strings).",
                                                    },
                                                    "target": {
                                                        "type": "array",
                                                        "items": {"type": "integer"},
                                                        "description": "Target token IDs (integers — not word strings).",
                                                    },
                                                },
                                            },
                                            "is_idiom": {"type": "boolean"},
                                            "rel": {
                                                "type": "string",
                                                "enum": ["NEQ"],
                                            },
                                        },
                                    },
                                },
                                "required": ["source", "target"],
                            },
                        },
                    },
                    "required": ["verse_id", "records"],
                },
            },
        },
        "required": ["verses"],
    },
}


def _openai_tool_schema(neutral: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": neutral["name"],
            "description": neutral["description"],
            "parameters": neutral["parameters"],
        },
    }


def _openai_responses_tool_schema(neutral: dict) -> dict:
    return {
        "type": "function",
        "name": neutral["name"],
        "description": neutral["description"],
        "parameters": neutral["parameters"],
    }


def _anthropic_tool_schema(neutral: dict) -> dict:
    return {
        "name": neutral["name"],
        "description": neutral["description"],
        "input_schema": neutral["parameters"],
    }


def _gemini_tool_schema(neutral: dict):
    """Return a google.genai types.Tool for the neutral schema."""
    from google.genai import types
    return types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name=neutral["name"],
            description=neutral["description"],
            parameters=neutral["parameters"],
        )
    ])


# ---------------------------------------------------------------------------
# Gloo OAuth2 auth
# ---------------------------------------------------------------------------

_GLOO_TOKEN_URL = "https://platform.ai.gloo.com/oauth2/token"
_GLOO_COMPLETIONS_URL = "https://platform.ai.gloo.com/ai/v2/chat/completions"


class _GlooAuth:
    """OAuth2 client-credentials token manager for the Gloo AI platform.

    Tokens have a 1-hour TTL; the token is refreshed automatically 60 s before
    expiry so long-running alignment jobs never hit an expired-token error.
    """

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._expires_at: float = 0.0
        self._session = requests.Session()

    def _fetch_token(self) -> None:
        auth = base64.b64encode(
            f"{self._client_id}:{self._client_secret}".encode()
        ).decode()
        resp = self._session.post(
            _GLOO_TOKEN_URL,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth}",
            },
            data={"grant_type": "client_credentials", "scope": "api/access"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._expires_at = time.time() + data["expires_in"]

    def _token(self) -> str:
        if not self._access_token or time.time() > (self._expires_at - 60):
            self._fetch_token()
        return self._access_token  # type: ignore[return-value]

    def post(
        self,
        payload: dict,
        timeout: int = 240,
        stream: bool = False,
        extra_headers: dict | None = None,
    ):
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token()}",
        }
        if extra_headers:
            headers.update(extra_headers)
        resp = self._session.post(
            _GLOO_COMPLETIONS_URL,
            headers=headers,
            json=payload,
            timeout=(30, None) if stream else timeout,
            stream=stream,
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            trace_id = None
            if isinstance(detail, dict):
                trace_id = detail.get("trace_id") or (detail.get("error") or {}).get("trace_id")
            trace_note = f" [trace_id={trace_id}]" if trace_id else ""
            raise requests.exceptions.HTTPError(
                f"{exc}{trace_note} — {detail}", response=resp
            ) from exc
        if stream:
            return resp
        return resp.json()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_records(
    records: list[dict],
    source_ids: set[str],
    target_ids: set[str],
) -> tuple[list[dict], list[str], list[str]]:
    """Validate alignment records against the known token ID sets for a verse.

    Invalid records are dropped.  Records where secondary exhausts all tokens on
    one side are silently sanitized (secondary stripped) rather than dropped —
    the alignment correspondence is valid; only the classification is wrong.

    Returns ``(valid_records, error_messages, san_details)`` where
    ``san_details`` is a list of human-readable strings describing each
    sanitization event (useful for prompt diagnostics).
    """
    valid: list[dict] = []
    errors: list[str] = []
    san_details: list[str] = []

    # Build a map from bare ID → prefixed source ID for normalization.
    # Some models (reasoning mode) strip the canon prefix from source token IDs.
    bare_to_src: dict[str, str] = {
        sid[1:]: sid for sid in source_ids if sid and sid[0].isalpha()
    }

    for i, rec in enumerate(records):
        label = f"record {i + 1}"
        src = rec.get("source") or []
        tgt = rec.get("target") or []
        meta = rec.get("meta") or {}
        is_neq = meta.get("rel") == "NEQ"

        # Normalize bare source IDs: add canon prefix when the bare form matches a
        # known source token and is not itself a target token.
        normalized_src = [
            bare_to_src[s] if (s not in source_ids and s in bare_to_src and s not in target_ids)
            else s
            for s in src
        ]
        if normalized_src != src:
            san_details.append(
                f"{label}: source IDs normalized (canon prefix added): "
                f"{[s for s, n in zip(src, normalized_src) if s != n]!r}"
            )
            src = normalized_src
            rec = {**rec, "source": src}

        # If a record is flagged NEQ but has both source and target tokens, the model
        # confused NEQ with a regular alignment — strip the NEQ flag and continue as
        # a regular record.
        if is_neq and src and tgt:
            clean_meta = {k: v for k, v in meta.items() if k != "rel"}
            rec = {**rec, "meta": clean_meta} if clean_meta else {
                k: v for k, v in rec.items() if k != "meta"
            }
            meta = clean_meta
            is_neq = False
            san_details.append(
                f"{label}: NEQ flag removed — both source and target present; "
                f"treating as regular alignment"
            )

        if is_neq:
            # secondary is meaningless on a NEQ record — strip it silently
            if meta.get("secondary"):
                clean_meta = {k: v for k, v in meta.items() if k != "secondary"}
                rec = {**rec, "meta": clean_meta} if clean_meta else {
                    k: v for k, v in rec.items() if k != "meta"
                }
                meta = clean_meta
                san_details.append(
                    f"{label} (NEQ): secondary stripped — source={src!r} target={tgt!r}"
                )
            # Exactly one non-empty array
            if bool(src) == bool(tgt):
                errors.append(
                    f"{label}: NEQ record must have exactly one non-empty array "
                    f"(source={src!r}, target={tgt!r})"
                )
                continue
            bad = [s for s in src if s not in source_ids] + \
                  [t for t in tgt if t not in target_ids]
            if bad:
                errors.append(f"{label}: unknown token ID(s): {', '.join(bad)}")
                continue

        else:
            if not src and not tgt:
                errors.append(f"{label}: non-NEQ record has neither source nor target")
                continue

            rec_errors: list[str] = []
            bad_src = [s for s in src if s not in source_ids]
            bad_tgt = [t for t in tgt if t not in target_ids]
            secondary = meta.get("secondary") or {}
            bad_sec_src = [s for s in (secondary.get("source") or []) if s not in set(src)]
            bad_sec_tgt = [t for t in (secondary.get("target") or []) if t not in set(tgt)]

            if bad_src:
                rec_errors.append(f"unknown source ID(s): {', '.join(bad_src)}")
            if bad_tgt:
                rec_errors.append(f"unknown target ID(s): {', '.join(bad_tgt)}")
            if bad_sec_src:
                rec_errors.append(f"secondary.source not subset of source: {', '.join(bad_sec_src)}")
            if bad_sec_tgt:
                rec_errors.append(f"secondary.target not subset of target: {', '.join(bad_sec_tgt)}")

            if rec_errors:
                errors.extend(f"{label}: {e}" for e in rec_errors)
                continue

            # Sanitize: strip secondary lists that exhaust all tokens on one side.
            # A record with no primary tokens on a side is invalid, but the
            # alignment itself is correct — strip the bad classification only.
            sec_src = list(secondary.get("source") or [])
            sec_tgt = list(secondary.get("target") or [])
            sides_stripped: list[str] = []
            if src and set(sec_src) >= set(src):
                sides_stripped.append(f"secondary.source exhausted source={src!r}")
                sec_src = []
            if tgt and set(sec_tgt) >= set(tgt):
                sides_stripped.append(f"secondary.target exhausted target={tgt!r}")
                sec_tgt = []

            if sides_stripped:
                san_details.append(f"{label}: {'; '.join(sides_stripped)}")
                clean_secondary = {}
                if sec_src:
                    clean_secondary["source"] = sec_src
                if sec_tgt:
                    clean_secondary["target"] = sec_tgt
                clean_meta = {k: v for k, v in meta.items() if k != "secondary"}
                if clean_secondary:
                    clean_meta["secondary"] = clean_secondary
                rec = {**rec, "meta": clean_meta} if clean_meta else {
                    k: v for k, v in rec.items() if k != "meta"
                }

        valid.append(rec)

    # Cross-record: deduplicate target IDs (non-NEQ only — each target token
    # should appear in exactly one alignment record per verse).
    seen_targets: set[str] = set()
    deduped: list[dict] = []
    for rec in valid:
        if (rec.get("meta") or {}).get("rel") == "NEQ":
            deduped.append(rec)
            continue
        tgts = list(rec.get("target") or [])
        dup = [t for t in tgts if t in seen_targets]
        if dup:
            clean = [t for t in tgts if t not in seen_targets]
            src_ids = rec.get("source") or []
            if not clean:
                errors.append(
                    f"record dropped: all target ID(s) already used in this verse: "
                    f"{', '.join(dup)}"
                )
                continue
            rec = {**rec, "target": clean}
            san_details.append(
                f"record: duplicate target(s) removed {dup!r} "
                f"— source={src_ids!r} kept={clean!r}"
            )
            tgts = clean
        seen_targets.update(tgts)
        deduped.append(rec)

    return deduped, errors, san_details


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iter_verse_entries(
    data: dict,
    errors: list[str],
) -> list[tuple[str, list[dict]]]:
    """Return (verse_id, records) pairs from a tool-call data dict.

    Skips and logs any entry that is not a dict (malformed model output).
    Recovers from double-encoding where the model returns verses as a
    JSON-encoded string instead of a parsed array.
    """
    verses = data.get("verses", [])
    if isinstance(verses, str):
        try:
            verses = json.loads(verses)
        except json.JSONDecodeError as exc:
            errors.append(f"verses field is a JSON-encoded string that could not be decoded: {exc}")
            return []
    out: list[tuple[str, list[dict]]] = []
    for entry in verses:
        if not isinstance(entry, dict):
            errors.append(
                f"Malformed entry in verses array (expected object, got "
                f"{type(entry).__name__!r}): {str(entry)[:80]!r}"
            )
            continue
        out.append((entry.get("verse_id", ""), entry.get("records", [])))
    return out


# ---------------------------------------------------------------------------
# API-level backoff retry
# ---------------------------------------------------------------------------

_RETRIABLE_STATUS_CODES: frozenset[int] = frozenset({408, 429, 500, 502, 503, 504, 520, 522, 524})

# Transient network/decode errors that warrant a retry regardless of HTTP status.
_RETRIABLE_EXC_TYPES: tuple[type, ...] = (
    json.JSONDecodeError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.ConnectionError,
)


def _status_code(exc: Exception) -> int | None:
    """Return the HTTP status code from a provider exception, or None."""
    if hasattr(exc, "status_code"):
        try:
            return int(exc.status_code)
        except (TypeError, ValueError):
            pass
    # requests.exceptions.HTTPError stores the response on exc.response
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        try:
            return int(exc.response.status_code)
        except (TypeError, ValueError):
            pass
    # Fallback: the Google SDK (and re-raised requests errors) embed the code
    # at the start of the str repr — cover all retriable codes.
    s = str(exc)
    for code in _RETRIABLE_STATUS_CODES:
        if s.startswith(str(code)):
            return code
    # SDK-level timeout exceptions (e.g. openai.APITimeoutError) don't carry an
    # HTTP status code but are always transient — treat them as 408.
    if type(exc).__name__ in ("APITimeoutError", "ReadTimeout", "ConnectTimeout"):
        return 408
    return None


def _api_call_with_backoff(fn, max_retries: int, provider: str):
    """Call fn(), retrying on transient API errors with exponential backoff.

    Retries on 408 (provider timeout), 429 (rate-limited), 500/502/503 (provider
    error), 504 (gateway timeout), 520/522/524 (Cloudflare transient), and malformed-JSON responses
    up to *max_retries* times.  Raises RuntimeError immediately on
    non-retriable errors or after exhausting retries.  Delays: 2s, 4s, 8s, …
    """
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as exc:
            code = _status_code(exc)
            retriable = code in _RETRIABLE_STATUS_CODES or isinstance(exc, _RETRIABLE_EXC_TYPES)
            if not retriable or attempt == max_retries:
                raise RuntimeError(
                    f"{provider} API error (attempt {attempt + 1}): {exc}"
                ) from exc
            reason = str(code) if code else type(exc).__name__
            delay = 2 ** (attempt + 1)
            print(
                f"  {provider} API {reason} — retrying in {delay}s "
                f"(attempt {attempt + 1}/{max_retries + 1}) ...",
                flush=True,
            )
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Retry message builder
# ---------------------------------------------------------------------------

def _process_tool_call_data(
    data: dict,
    results: dict[str, list[dict]],
    verse_errors: dict[str, list[str]],
    all_errors: list[str],
    all_san_details: list[str],
    verse_source_ids: dict[str, set[str]],
    verse_target_ids: dict[str, set[str]],
    verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
) -> list[str]:
    """Validate records from one tool-call data dict and update result accumulators.

    Returns per-call error strings (used to construct the tool response feedback).
    Mutates results, verse_errors, all_errors, and all_san_details in place.
    """
    call_errors: list[str] = []
    for verse_id, records in _iter_verse_entries(data, all_errors):
        if verse_token_maps:
            src_map, tgt_map = verse_token_maps.get(verse_id, ({}, {}))
            records, map_errors = reverse_map_records(records, src_map, tgt_map)
            all_errors.extend(f"VERSE {verse_id}: {e}" for e in map_errors)
        valid, errs, san_details = validate_records(
            records,
            verse_source_ids.get(verse_id, set()),
            verse_target_ids.get(verse_id, set()),
        )
        all_san_details.extend(f"VERSE {verse_id}: {d}" for d in san_details)
        if valid:
            results[verse_id] = valid
        if errs:
            verse_errors[verse_id] = errs
            call_errors.extend(f"VERSE {verse_id}: {e}" for e in errs)
    return call_errors


def _try_parse_json(s: str) -> dict:
    """Parse JSON, recovering from 'Extra data' by ignoring trailing garbage."""
    try:
        return json.loads(s)
    except json.JSONDecodeError as exc:
        if "Extra data" in str(exc):
            obj, _ = json.JSONDecoder().raw_decode(s)
            return obj
        raise


def _build_retry_message(verse_errors: dict[str, list[str]]) -> str:
    lines = [
        "The following verses had validation errors in your previous response.",
        "Please resubmit corrected records for each.",
        "",
    ]
    for verse_id, errs in verse_errors.items():
        lines.append(f"VERSE {verse_id}:")
        lines.extend(f"  - {e}" for e in errs)
        lines.append("")
    lines.append("Resubmit only the corrected verses.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM client
# ---------------------------------------------------------------------------

class LLMClient:
    """Provider-agnostic client for refine-alignment LLM calls.

    Args:
        provider: ``"openai"``, ``"anthropic"``, ``"google"``, ``"openrouter"``,
            or ``"gloo"``.
        model: Model name, e.g. ``"gpt-5.4-mini"``, ``"claude-sonnet-4-6"``,
            ``"gemini-3.1-flash"``, any OpenRouter model slug, or a Gloo model
            ID such as ``"gloo-anthropic-claude-sonnet-4.5"``.
        temperature: Sampling temperature passed explicitly to the provider.
            ``None`` (default) lets the provider use its own default.  Set this
            to match the value you use in sync calls so async batch requests
            receive identical generation parameters.
        max_output_tokens: Hard cap on response tokens.  ``None`` uses the
            provider default.  Align this with batch submissions to avoid
            silent truncation differences.
    """

    #: Anthropic max_tokens for alignment batch calls.
    #: 32 000 gives Opus 4.7 headroom for thinking tokens before the tool call.
    ANTHROPIC_MAX_TOKENS = 32000

    def __init__(
        self,
        provider: str,
        model: str,
        reasoning_effort: str | None = None,
        max_api_retries: int = 4,
        temperature: float = 1,
        max_output_tokens: int = 4000,
    ) -> None:
        if provider not in ("openai", "anthropic", "google", "openrouter", "gloo", "ollama"):
            raise ValueError(
                f"Unknown provider {provider!r}. "
                f"Use 'openai', 'anthropic', 'google', 'openrouter', 'gloo', or 'ollama'."
            )
        self.provider = provider
        self.model = model
        self.reasoning_effort = reasoning_effort  # OpenAI only; None = use model default
        self.max_api_retries = max_api_retries
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self._client = self._init_client()
        self.session_cost: float = 0.0

    def _init_client(self):
        if self.provider == "openai":
            try:
                import openai
            except ImportError:
                raise ImportError("Install the openai package: poetry add openai")
            return openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            try:
                import anthropic
            except ImportError:
                raise ImportError("Install the anthropic package: poetry add anthropic")
            return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        elif self.provider == "openrouter":
            try:
                import openai
            except ImportError:
                raise ImportError("Install the openai package: poetry add openai")
            return openai.OpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
        elif self.provider == "gloo":
            try:
                import requests  # noqa: F401 — verify requests is available
            except ImportError:
                raise ImportError("Install the requests package: poetry add requests")
            client_id = os.environ.get("GLOO_CLIENT_ID", "")
            client_secret = os.environ.get("GLOO_CLIENT_SECRET", "")
            if not client_id or not client_secret:
                raise EnvironmentError(
                    "GLOO_CLIENT_ID and GLOO_CLIENT_SECRET must be set for provider 'gloo'."
                )
            return _GlooAuth(client_id, client_secret)
        elif self.provider == "ollama":
            try:
                import openai
            except ImportError:
                raise ImportError("Install the openai package: poetry add openai")
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            return openai.OpenAI(base_url=base_url, api_key="ollama")
        else:
            try:
                from google import genai
            except ImportError:
                raise ImportError("Install the google-genai package: poetry add google-genai")
            return genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    def _is_deepseek_openrouter(self) -> bool:
        return self.provider == "openrouter" and "deepseek" in self.model.lower()

    def _track_openrouter_cost(self, response) -> None:
        """Accumulate per-call cost from an OpenRouter response and print running total."""
        usage = getattr(response, "usage", None)
        if usage is None:
            return
        extra = getattr(usage, "model_extra", None) or {}
        cost = extra.get("cost") or extra.get("total_cost")
        if cost is None:
            return
        try:
            cost = float(cost)
        except (TypeError, ValueError):
            return
        self.session_cost += cost
        print(
            f"  [OpenRouter cost: ${cost:.4f} | session: ${self.session_cost:.4f}]",
            flush=True,
        )

    def call_batch(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None = None,
        max_retries: int = 2,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        """Call the LLM for a verse batch with forced tool use, validate, and retry.

        Args:
            system_prompt: Assembled system prompt from ``prompt.build_system_prompt()``.
            user_message: Batch message from ``prompt.build_batch_message()``.
            verse_source_ids: ``verse_id → set`` of valid source token IDs.
            verse_target_ids: ``verse_id → set`` of valid target token IDs.
            verse_token_maps: ``verse_id → (source_map, target_map)`` for converting
                local token numbers back to full IDs (from build_batch_message).
            max_retries: Maximum retry attempts on validation failure.

        Returns:
            ``(results, unresolved_errors, san_details)`` where ``results`` maps
            ``verse_id → list[record_dict]``, ``unresolved_errors`` lists errors
            that remained after all retries, and ``san_details`` is a list of
            human-readable strings describing each sanitization event.
        """
        if self.provider in ("openai", "openrouter", "ollama"):
            return self._call_openai(
                system_prompt, user_message, verse_source_ids, verse_target_ids,
                verse_token_maps, max_retries
            )
        elif self.provider == "anthropic":
            return self._call_anthropic(
                system_prompt, user_message, verse_source_ids, verse_target_ids,
                verse_token_maps, max_retries
            )
        elif self.provider == "gloo":
            return self._call_gloo(
                system_prompt, user_message, verse_source_ids, verse_target_ids,
                verse_token_maps, max_retries
            )
        else:
            return self._call_gemini(
                system_prompt, user_message, verse_source_ids, verse_target_ids,
                verse_token_maps, max_retries
            )

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------

    def _call_openai(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
        max_retries: int,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        if self.reasoning_effort is not None and self.provider not in ("openrouter", "ollama"):
            return self._call_openai_responses(
                system_prompt, user_message, verse_source_ids, verse_target_ids,
                verse_token_maps, max_retries
            )

        if self.provider == "ollama":
            user_message = "/no_think\n" + user_message
        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
        _original_messages = list(messages)
        tool_schema = [_openai_tool_schema(_NEUTRAL_TOOL_SCHEMA)]
        tool_choice = {"type": "function", "function": {"name": TOOL_NAME}}

        results: dict[str, list[dict]] = {}
        all_errors: list[str] = []
        all_san_details: list[str] = []
        _tool_choice_dropped = self.model in _TOOL_CHOICE_INCOMPATIBLE

        for attempt in range(max_retries + 1):
            _oa_kwargs: dict = dict(
                model=self.model,
                messages=messages,
                tools=tool_schema,
            )
            if not _tool_choice_dropped:
                _oa_kwargs["tool_choice"] = tool_choice
            if self.temperature is not None:
                _oa_kwargs["temperature"] = self.temperature
            if self.max_output_tokens is not None:
                _oa_kwargs["max_completion_tokens"] = self.max_output_tokens
            if self._is_deepseek_openrouter():
                model = _oa_kwargs["model"]
                for _sfx in (":nitro", ":exacto"):
                    if model.endswith(_sfx):
                        _oa_kwargs["model"] = model[: -len(_sfx)]
                        break
                _oa_kwargs["extra_body"] = {"provider": {"order": ["DeepSeek", "deepseek"], "allow_fallbacks": False}}
            try:
                response = _api_call_with_backoff(
                    lambda: self._client.chat.completions.create(**_oa_kwargs),
                    self.max_api_retries,
                    "OpenAI",
                )
            except RuntimeError as exc:
                msg = str(exc)
                if not _tool_choice_dropped and "tool_choice" in msg:
                    print("  NOTE: model/provider rejected tool_choice — retrying without it")
                    _tool_choice_dropped = True
                    continue
                raise

            if self.provider == "openrouter":
                self._track_openrouter_cost(response)

            if response.usage:
                print(f"  tokens: in={response.usage.prompt_tokens}, out={response.usage.completion_tokens}")

            choice = response.choices[0]
            if choice.finish_reason == "length":
                print(
                    f"  WARNING: response truncated (finish_reason=length) — "
                    f"some verses may be missing. Reduce --batch-size."
                )
            assistant_msg = choice.message
            tool_calls = assistant_msg.tool_calls or []

            if not tool_calls:
                _content = assistant_msg.content or ""
                print(
                    f"  DEBUG no-tool-call: finish_reason={choice.finish_reason!r}, "
                    f"content={_content[:200]!r}"
                )
                if attempt < max_retries:
                    print("  NOTE: model returned no tool call — nudging to retry")
                    messages = list(_original_messages)
                    messages.append({"role": "user", "content": "You did not call the alignment tool. You must call it now to provide the verse alignments."})
                    continue
                else:
                    all_errors.append("model returned no tool call after all retries")
                    break

            verse_errors: dict[str, list[str]] = {}
            tool_results: list[dict] = []

            for tc in tool_calls:
                try:
                    data = _try_parse_json(tc.function.arguments)
                except json.JSONDecodeError as exc:
                    all_errors.append(f"JSON parse error in tool call: {exc}")
                    tool_results.append({
                        "role": "tool",
                        "content": f"parse error: {exc}",
                        "tool_call_id": tc.id,
                    })
                    continue

                tc_errors = _process_tool_call_data(
                    data, results, verse_errors, all_errors, all_san_details,
                    verse_source_ids, verse_target_ids, verse_token_maps,
                )
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": (
                        "Validation errors:\n" + "\n".join(f"  - {e}" for e in tc_errors)
                        if tc_errors else "ok"
                    ),
                })

            if not verse_errors or attempt == max_retries:
                if verse_errors:
                    for vid, errs in verse_errors.items():
                        all_errors.extend(f"VERSE {vid} (unresolved): {e}" for e in errs)
                break

            # Extend conversation for retry
            messages.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            })
            messages.extend(tool_results)
            messages.append({"role": "user", "content": _build_retry_message(verse_errors)})

        return results, all_errors, all_san_details

    def _call_openai_responses(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
        max_retries: int,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        """Use /v1/responses API — required when reasoning_effort is set."""
        initial_input: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
        tool_schema = [_openai_responses_tool_schema(_NEUTRAL_TOOL_SCHEMA)]
        tool_choice = {"type": "function", "name": TOOL_NAME}

        results: dict[str, list[dict]] = {}
        all_errors: list[str] = []
        all_san_details: list[str] = []
        previous_response_id: str | None = None
        retry_input: list[dict] = []

        for attempt in range(max_retries + 1):
            input_items = initial_input if previous_response_id is None else retry_input
            kwargs: dict = dict(
                model=self.model,
                input=input_items,
                tools=tool_schema,
                tool_choice=tool_choice,
                reasoning={"effort": self.reasoning_effort},
            )
            if previous_response_id is not None:
                kwargs["previous_response_id"] = previous_response_id
            if self.max_output_tokens is not None:
                kwargs["max_output_tokens"] = self.max_output_tokens
            response = _api_call_with_backoff(
                lambda: self._client.responses.create(**kwargs),
                self.max_api_retries,
                "OpenAI",
            )

            previous_response_id = response.id

            if getattr(response, "status", None) == "incomplete":
                print(
                    f"  WARNING: response incomplete — "
                    f"some verses may be missing. Reduce --batch-size."
                )

            tool_calls = [
                item for item in response.output
                if getattr(item, "type", None) == "function_call"
            ]

            verse_errors: dict[str, list[str]] = {}
            tool_results: list[dict] = []

            for tc in tool_calls:
                try:
                    data = _try_parse_json(tc.arguments)
                except json.JSONDecodeError as exc:
                    all_errors.append(f"JSON parse error in tool call: {exc}")
                    tool_results.append({
                        "type": "function_call_output",
                        "call_id": tc.call_id,
                        "output": f"parse error: {exc}",
                    })
                    continue

                tc_errors = _process_tool_call_data(
                    data, results, verse_errors, all_errors, all_san_details,
                    verse_source_ids, verse_target_ids, verse_token_maps,
                )
                tool_results.append({
                    "type": "function_call_output",
                    "call_id": tc.call_id,
                    "output": (
                        "Validation errors:\n" + "\n".join(f"  - {e}" for e in tc_errors)
                        if tc_errors else "ok"
                    ),
                })

            if not verse_errors or attempt == max_retries:
                if verse_errors:
                    for vid, errs in verse_errors.items():
                        all_errors.extend(f"VERSE {vid} (unresolved): {e}" for e in errs)
                break

            # For retry: tool results + new user message become the next input;
            # previous_response_id chains the conversation context.
            retry_input = tool_results + [
                {"role": "user", "content": _build_retry_message(verse_errors)},
            ]

        return results, all_errors, all_san_details

    # ------------------------------------------------------------------
    # Anthropic
    # ------------------------------------------------------------------

    def _call_anthropic(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
        max_retries: int,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        messages: list[dict] = [{"role": "user", "content": user_message}]
        tool_schema = [_anthropic_tool_schema(_NEUTRAL_TOOL_SCHEMA)]
        tool_choice = {"type": "tool", "name": TOOL_NAME}

        results: dict[str, list[dict]] = {}
        all_errors: list[str] = []
        all_san_details: list[str] = []

        for attempt in range(max_retries + 1):
            def _do_anthropic():
                with self._client.messages.stream(
                    model=self.model,
                    max_tokens=self.max_output_tokens,
                    system=system_prompt,
                    messages=messages,
                    tools=tool_schema,
                    tool_choice=tool_choice,
                ) as stream:
                    return stream.get_final_message()

            response = _api_call_with_backoff(_do_anthropic, self.max_api_retries, "Anthropic")

            if response.usage:
                print(f"  tokens: in={response.usage.input_tokens}, out={response.usage.output_tokens}")

            if response.stop_reason == "max_tokens":
                print(
                    f"  WARNING: response truncated (stop_reason=max_tokens, "
                    f"limit={self.ANTHROPIC_MAX_TOKENS}) — "
                    f"some verses may be missing. Reduce --batch-size."
                )

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            if not tool_use_blocks:
                text = "".join(b.text for b in response.content if b.type == "text")
                print(
                    f"  DEBUG no-tool-call: stop_reason={response.stop_reason!r}, "
                    f"content={text[:200]!r}"
                )
            verse_errors: dict[str, list[str]] = {}
            tool_results: list[dict] = []

            for block in tool_use_blocks:
                block_errors = _process_tool_call_data(
                    block.input, results, verse_errors, all_errors, all_san_details,
                    verse_source_ids, verse_target_ids, verse_token_maps,
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": (
                        "Validation errors:\n" + "\n".join(f"  - {e}" for e in block_errors)
                        if block_errors else "ok"
                    ),
                })

            if not verse_errors or attempt == max_retries:
                if verse_errors:
                    for vid, errs in verse_errors.items():
                        all_errors.extend(f"VERSE {vid} (unresolved): {e}" for e in errs)
                break

            # Extend conversation for retry — tool_results must accompany tool_use blocks
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": tool_results + [
                    {"type": "text", "text": _build_retry_message(verse_errors)},
                ],
            })

        return results, all_errors, all_san_details

    # ------------------------------------------------------------------
    # Google (Gemini)
    # ------------------------------------------------------------------

    def _call_gemini(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
        max_retries: int,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        from google.genai import types

        tool = _gemini_tool_schema(_NEUTRAL_TOOL_SCHEMA)
        thinking_config = None
        if self.reasoning_effort and self.reasoning_effort != "none":
            thinking_config = types.ThinkingConfig(thinking_level=self.reasoning_effort)
        _gemini_cfg: dict = dict(
            system_instruction=system_prompt,
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY",
                    allowed_function_names=[TOOL_NAME],
                )
            ),
            thinking_config=thinking_config,
        )
        if self.temperature is not None:
            _gemini_cfg["temperature"] = self.temperature
        if self.max_output_tokens is not None:
            _gemini_cfg["max_output_tokens"] = self.max_output_tokens
        gen_config = types.GenerateContentConfig(**_gemini_cfg)

        contents: list = [
            types.Content(role="user", parts=[types.Part(text=user_message)])
        ]

        results: dict[str, list[dict]] = {}
        all_errors: list[str] = []
        all_san_details: list[str] = []

        for attempt in range(max_retries + 1):
            response = _api_call_with_backoff(
                lambda: self._client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=gen_config,
                ),
                self.max_api_retries,
                "Google",
            )

            if getattr(response, "usage_metadata", None):
                um = response.usage_metadata
                print(f"  tokens: in={um.prompt_token_count}, out={um.candidates_token_count}")

            candidate = response.candidates[0]
            finish_reason = getattr(candidate, "finish_reason", None)
            if finish_reason is not None and "MAX_TOKENS" in str(finish_reason):
                print(
                    f"  WARNING: response truncated (finish_reason=MAX_TOKENS) — "
                    f"some verses may be missing. Reduce --batch-size."
                )

            function_calls = [
                part.function_call
                for part in candidate.content.parts
                if getattr(part, "function_call", None)
            ]
            if not function_calls:
                text = "".join(
                    p.text for p in candidate.content.parts if getattr(p, "text", None)
                )
                print(
                    f"  DEBUG no-tool-call: finish_reason={finish_reason!r}, "
                    f"content={text[:200]!r}"
                )
            verse_errors: dict[str, list[str]] = {}
            response_parts: list = []

            for fc in function_calls:
                try:
                    # fc.args is a dict in google-genai 1.x
                    data = fc.args if isinstance(fc.args, dict) else dict(fc.args)
                except Exception as exc:
                    all_errors.append(f"Could not read function call args: {exc}")
                    response_parts.append(types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response={"output": f"parse error: {exc}"},
                        )
                    ))
                    continue

                fc_errors = _process_tool_call_data(
                    data, results, verse_errors, all_errors, all_san_details,
                    verse_source_ids, verse_target_ids, verse_token_maps,
                )
                response_parts.append(types.Part(
                    function_response=types.FunctionResponse(
                        name=fc.name,
                        response={
                            "output": (
                                "Validation errors:\n" + "\n".join(f"  - {e}" for e in fc_errors)
                                if fc_errors else "ok"
                            )
                        },
                    )
                ))

            if not verse_errors or attempt == max_retries:
                if verse_errors:
                    for vid, errs in verse_errors.items():
                        all_errors.extend(f"VERSE {vid} (unresolved): {e}" for e in errs)
                break

            # Extend contents for retry: model turn then user function results + message
            contents.append(candidate.content)
            contents.append(types.Content(
                role="user",
                parts=response_parts + [
                    types.Part(text=_build_retry_message(verse_errors))
                ],
            ))

        return results, all_errors, all_san_details

    # ------------------------------------------------------------------
    # Gloo AI
    # ------------------------------------------------------------------

    @staticmethod
    def _accumulate_gloo_stream(resp) -> dict:
        """Consume an OpenAI-compatible SSE stream and return a response dict.

        Assembles the same shape as a non-streaming Gloo response so the
        existing tool-call parsing logic needs no changes.
        """
        tool_call_id = ""
        tool_call_name = ""
        accumulated_args = ""
        accumulated_text = ""
        finish_reason: str | None = None
        response_id = ""
        usage: dict | None = None
        gloo_error: dict | None = None

        try:
            for line in resp.iter_lines():
                if not line:
                    continue
                if isinstance(line, bytes):
                    line = line.decode("utf-8")
                if line == "data: [DONE]":
                    break
                if not line.startswith("data: "):
                    continue
                try:
                    chunk = json.loads(line[6:])
                except json.JSONDecodeError:
                    continue

                if not response_id:
                    response_id = chunk.get("id", "")
                if chunk.get("usage"):
                    usage = chunk["usage"]
                if chunk.get("error"):
                    gloo_error = chunk["error"]
                choices = chunk.get("choices", [])
                if not choices:
                    continue
                choice = choices[0]
                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]
                delta = choice.get("delta", {})
                if delta.get("content"):
                    accumulated_text += delta["content"]
                for tc in delta.get("tool_calls") or []:
                    if not tool_call_id and tc.get("id"):
                        tool_call_id = tc["id"]
                    fn = tc.get("function", {})
                    if not tool_call_name and fn.get("name"):
                        tool_call_name = fn["name"]
                    accumulated_args += fn.get("arguments", "")
        except requests.exceptions.ChunkedEncodingError:
            print(
                f"  DEBUG stream-drop: tool_call_name={tool_call_name!r}, "
                f"args_chars={len(accumulated_args)}, finish_reason={finish_reason!r}, "
                f"text={accumulated_text[:100]!r}"
            )
            raise

        tool_calls = (
            [{"id": tool_call_id, "type": "function",
              "function": {"name": tool_call_name, "arguments": accumulated_args}}]
            if accumulated_args else []
        )
        return {
            "id": response_id,
            "choices": [{
                "finish_reason": finish_reason,
                "message": {
                    "role": "assistant",
                    "content": accumulated_text or None,
                    "tool_calls": tool_calls,
                },
            }],
            "usage": usage,
            "error": gloo_error,
        }

    def _call_gloo(
        self,
        system_prompt: str,
        user_message: str,
        verse_source_ids: dict[str, set[str]],
        verse_target_ids: dict[str, set[str]],
        verse_token_maps: dict[str, tuple[dict[int, str], dict[int, str]]] | None,
        max_retries: int,
    ) -> tuple[dict[str, list[dict]], list[str], list[str]]:
        """Gloo AI completions — OpenAI-compatible format, OAuth2 auth via _GlooAuth."""
        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ]
        _original_messages = list(messages)
        tool_schema = [_openai_tool_schema(_NEUTRAL_TOOL_SCHEMA)]
        # "auto" rather than "required" — Gloo Studio has reported INTERNAL_ERROR on
        # some underlying models when tool_choice is forced; the no-tool-call path
        # below already nudges/retries if the model skips the tool call.
        tool_choice = "auto"

        results: dict[str, list[dict]] = {}
        all_errors: list[str] = []
        all_san_details: list[str] = []
        _tool_choice_dropped = self.model in _TOOL_CHOICE_INCOMPATIBLE
        # Anthropic routes via Gloo require an explicit header to enable prompt caching;
        # Gloo then places the cache_control breakpoint on the system message automatically.
        _gloo_extra_headers = (
            {"X-Cache-TTL": "1h"} if self.model.startswith("gloo-anthropic-") else None
        )

        for attempt in range(max_retries + 1):
            payload: dict = {
                "model": self.model,
                "messages": messages,
                "tools": tool_schema,
                "stream": True,
            }
            if not _tool_choice_dropped:
                payload["tool_choice"] = tool_choice
            if self.temperature is not None:
                payload["temperature"] = self.temperature
            if self.max_output_tokens is not None:
                payload["max_tokens"] = self.max_output_tokens
            if "deepseek" in self.model.lower():
                payload["enable_thinking"] = False

            try:
                response = _api_call_with_backoff(
                    lambda: self._accumulate_gloo_stream(
                        self._client.post(payload, stream=True, extra_headers=_gloo_extra_headers)
                    ),
                    self.max_api_retries,
                    "Gloo",
                )
            except RuntimeError as exc:
                msg = str(exc)
                if not _tool_choice_dropped and "tool_choice" in msg:
                    print("  NOTE: model/provider rejected tool_choice — retrying without it")
                    _tool_choice_dropped = True
                    continue
                raise

            if response.get("usage"):
                u = response["usage"]
                print(f"  tokens: in={u.get('prompt_tokens')}, out={u.get('completion_tokens')}")

            choice = response["choices"][0]
            _finish_reason = choice.get("finish_reason")
            if _finish_reason == "content_filter":
                all_errors.append("Gloo content_filter — response blocked by content moderation")
                print("  NOTE: Gloo content_filter — not retrying")
                break
            if _finish_reason == "error":
                err = response.get("error") or {}
                err_name = err.get("name") or err.get("code") or "unknown"
                err_retryable = err.get("retryable")
                err_trace_id = err.get("trace_id")
                trace_note = f", trace_id={err_trace_id}" if err_trace_id else ""
                print(f"  NOTE: Gloo error — name={err_name!r}, retryable={err_retryable!r}{trace_note}")
                if err_retryable is False:
                    all_errors.append(f"Gloo non-retryable error: {err_name}{trace_note}")
                    break
                if attempt < max_retries:
                    time.sleep(random.random() * min(30, 2 ** attempt))
                    continue
                else:
                    all_errors.append(f"Gloo error after all retries: {err_name}{trace_note}")
                    break
            if _finish_reason == "length":
                print(
                    "  WARNING: response truncated (finish_reason=length) — "
                    "some verses may be missing. Reduce --batch-size."
                )

            assistant_msg = choice["message"]
            tool_calls = assistant_msg.get("tool_calls") or []

            if not tool_calls:
                _content = assistant_msg.get("content") or ""
                print(
                    f"  DEBUG no-tool-call: finish_reason={_finish_reason!r}, "
                    f"content={_content[:200]!r}"
                )
                if _finish_reason is None and not _content:
                    # Empty stream with no finish_reason — treat as retryable server error
                    if attempt < max_retries:
                        print("  NOTE: empty response (no finish_reason, no content) — retrying")
                        time.sleep(random.random() * min(30, 2 ** attempt))
                        continue
                    else:
                        all_errors.append("empty response after all retries")
                        break
                if attempt < max_retries:
                    print("  NOTE: model returned no tool call — nudging to retry")
                    messages = list(_original_messages)
                    messages.append({"role": "user", "content": "You did not call the alignment tool. You must call it now to provide the verse alignments."})
                    continue
                else:
                    all_errors.append("model returned no tool call after all retries")
                    break

            verse_errors: dict[str, list[str]] = {}
            tool_results: list[dict] = []

            for tc in tool_calls:
                try:
                    data = _try_parse_json(tc["function"]["arguments"])
                except json.JSONDecodeError as exc:
                    all_errors.append(f"JSON parse error in tool call: {exc}")
                    tool_results.append({
                        "role": "tool",
                        "content": f"parse error: {exc}",
                        "tool_call_id": tc["id"],
                    })
                    continue

                tc_errors = _process_tool_call_data(
                    data, results, verse_errors, all_errors, all_san_details,
                    verse_source_ids, verse_target_ids, verse_token_maps,
                )
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": (
                        "Validation errors:\n" + "\n".join(f"  - {e}" for e in tc_errors)
                        if tc_errors else "ok"
                    ),
                })

            if not verse_errors or attempt == max_retries:
                if verse_errors:
                    for vid, errs in verse_errors.items():
                        all_errors.extend(f"VERSE {vid} (unresolved): {e}" for e in errs)
                break

            messages.append({
                "role": "assistant",
                "content": assistant_msg.get("content"),
                "tool_calls": tool_calls,
            })
            messages.extend(tool_results)
            messages.append({"role": "user", "content": _build_retry_message(verse_errors)})

        return results, all_errors, all_san_details
