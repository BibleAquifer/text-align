"""fetch-batch: retrieve and write results from an async refine-alignment batch job.

Usage:
    fetch-batch <job-metadata-file>          # fetch once; error if not complete
    fetch-batch <job-metadata-file> --poll   # print status and exit
    fetch-batch <job-metadata-file> --wait   # block until done (with sleep loop)

CLI entry point: fetch-batch
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from text_align.migrate.alignment_io import write_alignment_json
from text_align.migrate.tsv import process_usfm_tsv

from .async_batch import (
    _ANTHROPIC_ENDED,
    _GOOGLE_FAILED,
    _GOOGLE_CANCELLED,
    _GOOGLE_TERMINAL,
    _OPENAI_FAILED,
    _OPENAI_EXPIRED,
    _OPENAI_CANCELLED,
    _OPENAI_TERMINAL,
    load_job_metadata,
    retrieve_anthropic,
    retrieve_google,
    retrieve_openai,
)
from .refine import build_output_alignment
from .source import load_source_verses


def _write_chapter_results(
    chapter_results: dict[str, dict[str, list[dict]]],
    job_meta: dict,
    output_dir: Path,
    target_edition: str,
) -> int:
    """Write chapter results to disk, returning total record count.

    For retry jobs (job_meta["job_type"] == "retry"), merges new verse records
    into existing chapter files instead of writing fresh ones.
    """
    corpus_id = job_meta["corpus_id"]
    creator = job_meta.get("creator", "text-align")
    llm_provider = job_meta.get("provider")
    llm_model = job_meta.get("model")
    reasoning_effort = job_meta.get("reasoning_effort")
    is_retry = job_meta.get("job_type") == "retry"

    total_records = 0
    for chapter_id in sorted(chapter_results):
        verse_results = chapter_results[chapter_id]
        records = [rec for recs in verse_results.values() for rec in recs]

        book_id = chapter_id[:2]
        chap_num = chapter_id[2:]
        chapter_path = output_dir / f"{corpus_id}-{target_edition}-{book_id}-{chap_num}-manual.json"
        n_neq = sum(1 for r in records if (r.get("meta") or {}).get("rel") == "NEQ")

        if is_retry and chapter_path.exists():
            from .retry import merge_verse_results
            n_replaced = merge_verse_results(
                chapter_path, verse_results,
                corpus_id, target_edition, creator,
                llm_provider, llm_model, reasoning_effort,
            )
            print(
                f"  → {chapter_path.name}  "
                f"({n_replaced} verse(s) replaced, {len(records)} new records, {n_neq} NEQ)"
            )
        else:
            output = build_output_alignment(
                records, corpus_id, target_edition, creator,
                llm_provider=llm_provider,
                llm_model=llm_model,
                reasoning_effort=reasoning_effort,
            )
            write_alignment_json(output, chapter_path)
            print(f"  → {chapter_path.name}  ({len(records)} records, {n_neq} NEQ)")

        total_records += len(records)

    return total_records

def _build_verse_id_sets(
    requests_meta: list[dict],
    source_verses: dict,
    target_verses: dict,
) -> tuple[
    dict[str, set[str]],
    dict[str, set[str]],
    dict[str, tuple[dict[int, str], dict[int, str]]],
]:
    """Build verse_source_ids, verse_target_ids, and verse_token_maps from job requests."""
    all_verse_ids: set[str] = set()
    for req in requests_meta:
        all_verse_ids.update(req["verse_ids"])

    verse_source_ids = {
        vid: {t.id for t in source_verses.get(vid, [])}
        for vid in all_verse_ids
    }
    verse_target_ids = {
        vid: {t.id for t in (
            list(target_verses[vid].words.values()) if vid in target_verses else []
        )}
        for vid in all_verse_ids
    }
    verse_token_maps = {
        vid: (
            {i + 1: t.id for i, t in enumerate(source_verses.get(vid, []))},
            {i + 1: t.id for i, t in enumerate(
                list(target_verses[vid].words.values()) if vid in target_verses else []
            )},
        )
        for vid in all_verse_ids
    }
    return verse_source_ids, verse_target_ids, verse_token_maps


def _format_progress(status: str, done: int, total: int, bad: int, bad_label: str) -> str:
    """Format a batch progress string: 'status  done/total[, N bad_label]'."""
    if total:
        suffix = f", {bad} {bad_label}" if bad else ""
        return f"{status}  {done}/{total}{suffix}"
    return status


def _openai_progress(batch) -> str:
    rc = getattr(batch, "request_counts", None)
    if rc and getattr(rc, "total", 0):
        done = getattr(rc, "completed", 0) + getattr(rc, "failed", 0)
        return _format_progress(batch.status, done, rc.total, getattr(rc, "failed", 0), "failed")
    return batch.status


def _anthropic_progress(batch) -> str:
    rc = getattr(batch, "request_counts", None)
    if rc:
        succeeded = getattr(rc, "succeeded", 0)
        errored = getattr(rc, "errored", 0)
        expired = getattr(rc, "expired", 0)
        canceled = getattr(rc, "canceled", 0)
        processing = getattr(rc, "processing", 0)
        total = succeeded + errored + expired + canceled + processing
        done = succeeded + errored + expired + canceled
        return _format_progress(batch.processing_status, done, total, errored, "errored")
    return batch.processing_status


def _load_tokens(job_meta: dict) -> tuple[dict, dict]:
    """Load source and target verse tokens from the paths stored in job_meta."""
    sources_dir = Path(job_meta["sources_dir"])
    target_tsv_dir = Path(job_meta["target_tsv_dir"])
    target_edition = job_meta["target_edition"]
    corpus = job_meta["corpus"]
    print(f"  Loading source tokens ({job_meta['corpus_id']}) ...")
    source_verses = load_source_verses(sources_dir, corpus)
    print(f"  Loading target tokens ({target_edition}) ...")
    target_verses = process_usfm_tsv(target_tsv_dir, target_edition)
    return source_verses, target_verses


def _report_results(
    chapter_results: dict,
    errors: list[str],
    san_details: list[str],
    job_meta: dict,
    output_dir: Path,
    target_edition: str,
) -> None:
    """Write chapter results and print summary/error lines."""
    total_records = _write_chapter_results(chapter_results, job_meta, output_dir, target_edition)
    n_chapters = len(chapter_results)
    print(f"\n  {total_records} records across {n_chapters} chapter(s) written to {output_dir}")

    if san_details:
        print(f"  {len(san_details)} record(s) sanitized:")
        for detail in san_details[:20]:
            print(f"    {detail}")
        if len(san_details) > 20:
            print(f"    ... and {len(san_details) - 20} more")

    if errors:
        print(f"  {len(errors)} validation error(s):")
        for err in errors[:20]:
            print(f"    {err}")
        if len(errors) > 20:
            print(f"    ... and {len(errors) - 20} more")


def _cancel_google(job_meta: dict) -> None:
    from google import genai

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    job_name = job_meta["job_name"]
    client.batches.cancel(name=job_name)
    print(f"Job {job_name}: cancel requested.")


def _fetch_google(job_meta: dict, poll_only: bool, wait: bool, wait_interval: int) -> None:
    from google import genai

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    job_name = job_meta["job_name"]

    job = client.batches.get(name=job_name)
    state = job.state.name

    if poll_only:
        print(f"Job {job_name}: {state}")
        return

    if state not in _GOOGLE_TERMINAL:
        if wait:
            print(f"  Job {job_name}: {state} — waiting ...")
            while state not in _GOOGLE_TERMINAL:
                time.sleep(wait_interval)
                job = client.batches.get(name=job_name)
                state = job.state.name
                print(f"  Job {job_name}: {state}")
        else:
            raise SystemExit(
                f"Job {job_name} is not complete (state: {state}). "
                f"Use --wait to block or --poll to check status."
            )

    if state in {_GOOGLE_FAILED, _GOOGLE_CANCELLED}:
        raise SystemExit(f"Job {job_name} ended with state: {state}")

    print(f"Job {job_name}: {state} — retrieving results ...")

    source_verses, target_verses = _load_tokens(job_meta)
    verse_source_ids, verse_target_ids, verse_token_maps = _build_verse_id_sets(
        job_meta["requests"], source_verses, target_verses
    )

    chapter_results, errors, san_details = retrieve_google(
        genai_client=client,
        job_name=job_name,
        requests_meta=job_meta["requests"],
        verse_source_ids=verse_source_ids,
        verse_target_ids=verse_target_ids,
        verse_token_maps=verse_token_maps,
    )

    output_dir = Path(job_meta["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    _report_results(chapter_results, errors, san_details, job_meta, output_dir, job_meta["target_edition"])


def _cancel_openai(job_meta: dict) -> None:
    import openai

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    batch_id = job_meta["batch_id"]
    client.batches.cancel(batch_id)
    print(f"Batch {batch_id}: cancel requested.")


def _fetch_openai(job_meta: dict, poll_only: bool, wait: bool, wait_interval: int) -> None:
    import openai

    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    batch_id = job_meta["batch_id"]

    batch = client.batches.retrieve(batch_id)
    state = batch.status

    if poll_only:
        print(f"Batch {batch_id}: {_openai_progress(batch)}")
        return

    if state not in _OPENAI_TERMINAL:
        if wait:
            print(f"  Batch {batch_id}: {_openai_progress(batch)} — waiting ...")
            while state not in _OPENAI_TERMINAL:
                time.sleep(wait_interval)
                batch = client.batches.retrieve(batch_id)
                state = batch.status
                print(f"  Batch {batch_id}: {_openai_progress(batch)}")
        else:
            raise SystemExit(
                f"Batch {batch_id} is not complete (status: {state}). "
                f"Use --wait to block or --poll to check status."
            )

    if state in {_OPENAI_FAILED, _OPENAI_EXPIRED, _OPENAI_CANCELLED}:
        raise SystemExit(f"Batch {batch_id} ended with status: {state}")

    print(f"Batch {batch_id}: {state} — retrieving results ...")

    source_verses, target_verses = _load_tokens(job_meta)
    verse_source_ids, verse_target_ids, verse_token_maps = _build_verse_id_sets(
        job_meta["requests"], source_verses, target_verses
    )

    chapter_results, errors, san_details = retrieve_openai(
        openai_client=client,
        batch_id=batch_id,
        requests_meta=job_meta["requests"],
        verse_source_ids=verse_source_ids,
        verse_target_ids=verse_target_ids,
        verse_token_maps=verse_token_maps,
        use_responses_api=job_meta.get("use_responses_api", False),
    )

    output_dir = Path(job_meta["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    _report_results(chapter_results, errors, san_details, job_meta, output_dir, job_meta["target_edition"])


def _cancel_anthropic(job_meta: dict) -> None:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch_id = job_meta["batch_id"]
    client.messages.batches.cancel(batch_id)
    print(f"Batch {batch_id}: cancel requested.")


def _fetch_anthropic(job_meta: dict, poll_only: bool, wait: bool, wait_interval: int) -> None:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    batch_id = job_meta["batch_id"]

    batch = client.messages.batches.retrieve(batch_id)
    state = batch.processing_status

    if poll_only:
        print(f"Batch {batch_id}: {_anthropic_progress(batch)}")
        return

    if state != _ANTHROPIC_ENDED:
        if wait:
            print(f"  Batch {batch_id}: {_anthropic_progress(batch)} — waiting ...")
            while state != _ANTHROPIC_ENDED:
                time.sleep(wait_interval)
                batch = client.messages.batches.retrieve(batch_id)
                state = batch.processing_status
                print(f"  Batch {batch_id}: {_anthropic_progress(batch)}")
        else:
            raise SystemExit(
                f"Batch {batch_id} is not complete (status: {state}). "
                f"Use --wait to block or --poll to check status."
            )

    print(f"Batch {batch_id}: {state} — retrieving results ...")

    source_verses, target_verses = _load_tokens(job_meta)
    verse_source_ids, verse_target_ids, verse_token_maps = _build_verse_id_sets(
        job_meta["requests"], source_verses, target_verses
    )

    chapter_results, errors, san_details = retrieve_anthropic(
        anthropic_client=client,
        batch_id=batch_id,
        requests_meta=job_meta["requests"],
        verse_source_ids=verse_source_ids,
        verse_target_ids=verse_target_ids,
        verse_token_maps=verse_token_maps,
    )

    output_dir = Path(job_meta["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    _report_results(chapter_results, errors, san_details, job_meta, output_dir, job_meta["target_edition"])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Retrieve and write results from an async refine-alignment batch job."
    )
    p.add_argument("job_file", type=Path,
                   help="Path to the job metadata JSON file written by refine-alignment "
                        "(e.g. jobs/google/batches_abc123.json)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--poll", action="store_true",
                      help="Print job status and exit (no-op if not yet done)")
    mode.add_argument("--wait", action="store_true",
                      help="Block until the job is complete, polling periodically")
    mode.add_argument("--cancel", action="store_true",
                      help="Request cancellation of the job and exit")
    p.add_argument("--wait-interval", type=int, default=60, metavar="SECONDS",
                   help="Seconds between status checks when --wait is active (default: 60)")
    return p.parse_args()


def fetch_wait(meta_path: Path, wait_interval: int = 60) -> None:
    """Fetch batch results with --wait; called programmatically after async submission."""
    job_meta = load_job_metadata(meta_path)
    provider = job_meta.get("provider", "")
    if provider == "google":
        _fetch_google(job_meta, poll_only=False, wait=True, wait_interval=wait_interval)
    elif provider == "openai":
        _fetch_openai(job_meta, poll_only=False, wait=True, wait_interval=wait_interval)
    elif provider == "anthropic":
        _fetch_anthropic(job_meta, poll_only=False, wait=True, wait_interval=wait_interval)
    else:
        raise SystemExit(
            f"Provider {provider!r} is not supported. "
            f"Supported providers: 'google', 'openai', 'anthropic'."
        )


def main() -> None:
    args = parse_args()

    if not args.job_file.exists():
        raise SystemExit(f"Job metadata file not found: {args.job_file}")

    job_meta = load_job_metadata(args.job_file)
    provider = job_meta.get("provider", "")

    if provider == "google":
        if args.cancel:
            _cancel_google(job_meta)
        else:
            _fetch_google(job_meta, poll_only=args.poll, wait=args.wait, wait_interval=args.wait_interval)
    elif provider == "openai":
        if args.cancel:
            _cancel_openai(job_meta)
        else:
            _fetch_openai(job_meta, poll_only=args.poll, wait=args.wait, wait_interval=args.wait_interval)
    elif provider == "anthropic":
        if args.cancel:
            _cancel_anthropic(job_meta)
        else:
            _fetch_anthropic(job_meta, poll_only=args.poll, wait=args.wait, wait_interval=args.wait_interval)
    else:
        raise SystemExit(
            f"Provider {provider!r} is not supported. "
            f"Supported providers: 'google', 'openai', 'anthropic'."
        )


if __name__ == "__main__":
    main()
