"""Core retry logic for retry-alignment.

Finds chapter JSON files, evaluates source-token coverage, re-aligns flagged
verses from a blank slate, and merges the results back into the chapter files.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from text_align.migrate.alignment_io import load_alignment_json, write_alignment_json

from .coverage import VerseRetrySpec
from .llm import LLMClient
from .prompt import build_batch_message, build_system_prompt, detect_phenomena, infer_testament
from .refine import build_output_alignment
from .source import collect_source_verse_range
from .util import _chapter_id_from_path, _CORPUS_TESTAMENT


_CHAPTER_GLOB = "*-*-??-???-manual.json"


def discover_chapter_files(alignment_dir: Path) -> list[Path]:
    """Return all chapter JSON files in alignment_dir, sorted by path."""
    return sorted(alignment_dir.glob(_CHAPTER_GLOB))


def merge_verse_results(
    chapter_json_path: Path,
    new_records_by_verse: dict[str, list[dict]],
    corpus_id: str,
    target_edition: str,
    creator: str,
    llm_provider: str | None,
    llm_model: str | None,
    reasoning_effort: str | None,
) -> int:
    """Merge LLM results for flagged verses into an existing chapter JSON file.

    Replaces all records (and NEQ entries) belonging to each verse in
    new_records_by_verse; all other verses are preserved unchanged.

    Returns the number of verses replaced.
    """
    data = load_alignment_json(chapter_json_path)
    groups = data.get("groups", [])
    if not groups:
        return 0

    group = groups[0]
    old_records: list[dict] = group.get("records", [])
    old_group_meta: dict = group.get("meta", {})
    neq_meta: dict = old_group_meta.get("nonEquivalent", {})
    old_neq_source: list[str] = neq_meta.get("source", [])
    old_neq_target: list[str] = neq_meta.get("target", [])
    prior_llm: dict | None = old_group_meta.get("llm") or None

    replaced_verse_ids = set(new_records_by_verse.keys())

    # Build the set of source verse IDs (WLCM/SBLGNT) covered by new records.
    # Do NOT seed with replaced_verse_ids — for OT, those are BSB IDs that
    # collide with WLCM source-verse prefixes of adjacent verses (e.g. BSB
    # "32002006" == WLCM source prefix of BSB 32002005's records) and cause
    # adjacent-verse records to be silently dropped.
    replaced_source_verses: set[str] = set()
    for recs in new_records_by_verse.values():
        for rec in recs:
            for sid in rec.get("source") or []:
                if len(sid) >= 8:
                    replaced_source_verses.add(sid[:8])

    # Keep regular records for non-replaced verses.
    # Drop if source token prefix (WLCM/SBLGNT) matches a replaced source verse,
    # OR if target token prefix (BSB) is in replaced_verse_ids — the latter handles
    # target-only records and merged-verse stubs (e.g. BSB 3JN 1:14 = SBLGNT 1:14-15).
    kept: list[dict] = []
    for rec in old_records:
        src_ids = rec.get("source") or []
        tgt_ids = rec.get("target") or []
        src_vid = src_ids[0][:8] if src_ids else None
        tgt_vid = tgt_ids[0][:8] if tgt_ids else None
        if src_vid in replaced_source_verses or tgt_vid in replaced_verse_ids:
            continue
        kept.append(rec)

    # Re-inflate NEQ entries for non-replaced verses so build_output_alignment
    # can reprocess them uniformly (it separates NEQ from regular records).
    for sid in old_neq_source:
        if sid[:8] not in replaced_source_verses:
            kept.append({"source": [sid], "target": [], "meta": {"rel": "NEQ"}})
    for tid in old_neq_target:
        if tid[:8] not in replaced_verse_ids:
            kept.append({"source": [], "target": [tid], "meta": {"rel": "NEQ"}})

    # Add fresh LLM records for replaced verses
    for recs in new_records_by_verse.values():
        kept.extend(recs)

    output = build_output_alignment(
        kept, corpus_id, target_edition, creator,
        llm_provider=llm_provider,
        llm_model=llm_model,
        reasoning_effort=reasoning_effort,
        prior_llm=prior_llm,
    )
    write_alignment_json(output, chapter_json_path)
    return len(replaced_verse_ids)


def retry_chapter_sync(
    chapter_json_path: Path,
    retry_specs: list[VerseRetrySpec],
    source_verses: dict[str, list],
    target_verses: dict,
    target_language: str,
    llm_client: LLMClient,
    batch_size: int,
    max_retries: int,
    corpus_id: str,
    target_edition: str,
    creator: str,
    llm_provider: str | None,
    llm_model: str | None,
    reasoning_effort: str | None,
) -> tuple[int, list[str]]:
    """Re-align flagged verses in one chapter file via the sync LLM path.

    Each verse is sent from a blank slate (no candidates). Returns
    (n_verses_replaced, error_messages).
    """
    verse_ids = [spec.verse_id for spec in retry_specs]
    new_records_by_verse: dict[str, list[dict]] = {}
    all_errors: list[str] = []
    missed: dict[str, list[str]] = {}

    for batch_start in range(0, len(verse_ids), batch_size):
        batch_ids = verse_ids[batch_start:batch_start + batch_size]

        verse_batch = []
        verse_source_ids: dict[str, set[str]] = {}
        verse_target_ids: dict[str, set[str]] = {}

        for verse_id in batch_ids:
            tgt_verse = target_verses.get(verse_id)
            tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
            if tgt_verse and tgt_verse.words:
                src_start = next(iter(tgt_verse.words.values())).source_verse
                src_end = tgt_verse.source_verse_range_end
                if src_end and src_end > src_start:
                    src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                else:
                    src_tokens = source_verses.get(src_start, [])
            else:
                src_tokens = []
            verse_source_ids[verse_id] = {t.id for t in src_tokens}
            verse_target_ids[verse_id] = {t.id for t in tgt_tokens}
            verse_batch.append((verse_id, src_tokens, tgt_tokens, {}))  # blank-slate cands

        all_src = [t for _, src, _, _ in verse_batch for t in src]
        testament = infer_testament(all_src)
        phenomena = detect_phenomena(all_src)
        system_msg = build_system_prompt(phenomena, target_language, testament=testament)
        user_msg, batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)

        try:
            results, errors, _san = llm_client.call_batch(
                system_prompt=system_msg,
                user_message=user_msg,
                verse_source_ids=verse_source_ids,
                verse_target_ids=verse_target_ids,
                verse_token_maps=batch_maps,
                max_retries=max_retries,
            )
        except RuntimeError as exc:
            verse_list = ", ".join(batch_ids)
            print(f"  Retry batch failed ({exc}) — missed: {verse_list}")
            results, errors = {}, []
            for vid in batch_ids:
                missed.setdefault(vid, []).append(f"API error: {exc}")

        for vid in batch_ids:
            if vid not in results and vid not in missed:
                reason = next(
                    (e for e in errors if "no tool call" in e or "no records" in e),
                    errors[0] if errors else "no records returned",
                )
                missed.setdefault(vid, []).append(reason)

        new_records_by_verse.update(results)
        all_errors.extend(errors)

    if missed:
        print(f"  Resubmitting {len(missed)} verse(s) individually ...")
        for verse_id in list(missed.keys()):
            tgt_verse = target_verses.get(verse_id)
            tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
            if tgt_verse and tgt_verse.words:
                src_start = next(iter(tgt_verse.words.values())).source_verse
                src_end = tgt_verse.source_verse_range_end
                if src_end and src_end > src_start:
                    src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                else:
                    src_tokens = source_verses.get(src_start, [])
            else:
                src_tokens = []
            verse_batch = [(verse_id, src_tokens, tgt_tokens, {})]
            all_src = [t for _, src, _, _ in verse_batch for t in src]
            testament = infer_testament(all_src)
            phenomena = detect_phenomena(all_src)
            system_msg = build_system_prompt(phenomena, target_language, testament=testament)
            user_msg, batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)
            try:
                r_results, r_errors, _san = llm_client.call_batch(
                    system_prompt=system_msg,
                    user_message=user_msg,
                    verse_source_ids={verse_id: {t.id for t in src_tokens}},
                    verse_target_ids={verse_id: {t.id for t in tgt_tokens}},
                    verse_token_maps=batch_maps,
                    max_retries=max_retries,
                )
            except RuntimeError as exc:
                missed[verse_id].append(f"individual retry: API error: {exc}")
                print(f"  Resubmit {verse_id}: all retries exhausted — {exc}")
                continue
            if verse_id not in r_results:
                reason = next(
                    (e for e in r_errors if "no tool call" in e or "no records" in e),
                    r_errors[0] if r_errors else "no records returned",
                )
                missed[verse_id].append(f"individual retry: {reason}")
                n_r = 0
                status = "0/1 verses, 0 records"
                if r_errors:
                    status += f", {len(r_errors)} error(s)"
                print(f"  Resubmit {verse_id}: {status}")
                all_errors.extend(r_errors)
                continue
            del missed[verse_id]
            n_r = sum(len(v) for v in r_results.values())
            status = f"{len(r_results)}/1 verses, {n_r} records"
            if r_errors:
                status += f", {len(r_errors)} error(s)"
            print(f"  Resubmit {verse_id}: {status}")
            new_records_by_verse.update(r_results)
            all_errors.extend(r_errors)
        if missed:
            print(f"  {len(missed)} verse(s) permanently unresolved:")
            for vid, reasons in missed.items():
                print(f"    {vid}: {' → '.join(reasons)}")

    if not new_records_by_verse:
        return 0, all_errors

    n = merge_verse_results(
        chapter_json_path, new_records_by_verse,
        corpus_id, target_edition, creator,
        llm_provider, llm_model, reasoning_effort,
    )
    return n, all_errors


def build_retry_chapter_batches(
    retry_specs_by_chapter: dict[str, list[VerseRetrySpec]],
    source_verses: dict[str, list],
    target_verses: dict,
    target_language: str,
    batch_size: int,
    corpus_id: str = "SBLGNT",
) -> list[dict]:
    """Build chapter_batches payload for async submission of retry verses."""
    chapter_batches: list[dict] = []

    for chapter_id, specs in sorted(retry_specs_by_chapter.items()):
        verse_ids = [spec.verse_id for spec in specs]
        for batch_index, batch_start in enumerate(range(0, len(verse_ids), batch_size)):
            batch_ids = verse_ids[batch_start:batch_start + batch_size]

            verse_batch = []
            for verse_id in batch_ids:
                tgt_verse = target_verses.get(verse_id)
                tgt_tokens = list(tgt_verse.words.values()) if tgt_verse else []
                if tgt_verse and tgt_verse.words:
                    src_start = next(iter(tgt_verse.words.values())).source_verse
                    src_end = tgt_verse.source_verse_range_end
                    if src_end and src_end > src_start:
                        src_tokens = collect_source_verse_range(source_verses, src_start, src_end)
                    else:
                        src_tokens = source_verses.get(src_start, [])
                else:
                    src_tokens = []
                verse_batch.append((verse_id, src_tokens, tgt_tokens, {}))

            all_src = [t for _, src, _, _ in verse_batch for t in src]
            testament = _CORPUS_TESTAMENT.get(corpus_id, "nt")
            phenomena = detect_phenomena(all_src)
            system_msg = build_system_prompt(phenomena, target_language, testament=testament)
            user_msg, _batch_maps = build_batch_message(verse_batch, target_language, source_corpus=corpus_id)

            chapter_batches.append({
                "chapter_id": chapter_id,
                "batch_index": batch_index,
                "verse_ids": batch_ids,
                "system_prompt": system_msg,
                "user_message": user_msg,
            })

    return chapter_batches


def _filter_chapter_files(
    chapter_files: list[Path],
    args: argparse.Namespace,
    forced_verse_set: frozenset[str] | None = None,
) -> list[Path]:
    """Filter chapter files by the active range arg on args.

    Handles: --verse, --verse-range, --verse-list/--verse-list-file (via
    forced_verse_set), --book, --book-range, --chapter, --chapter-range.
    Unknown args are read via getattr so this works for any args namespace.
    """
    verse = getattr(args, "verse", None)
    verse_range = getattr(args, "verse_range", None)
    book = getattr(args, "book", None)
    book_range = getattr(args, "book_range", None)
    chapter = getattr(args, "chapter", None)
    chapter_range = getattr(args, "chapter_range", None)

    if not any([verse, verse_range, forced_verse_set, book, book_range, chapter, chapter_range]):
        return chapter_files

    result = []
    for f in chapter_files:
        cid = _chapter_id_from_path(f)
        if verse:
            if cid == str(verse).zfill(8)[:5]:
                result.append(f)
        elif verse_range:
            start_cid = str(verse_range[0]).zfill(8)[:5]
            end_cid = str(verse_range[1]).zfill(8)[:5]
            if start_cid <= cid <= end_cid:
                result.append(f)
        elif forced_verse_set:
            if any(vid[:5] == cid for vid in forced_verse_set):
                result.append(f)
        elif book:
            if cid[:2] == str(book).zfill(2):
                result.append(f)
        elif book_range:
            start, end = str(book_range[0]).zfill(2), str(book_range[1]).zfill(2)
            if start <= cid[:2] <= end:
                result.append(f)
        elif chapter:
            if cid == str(chapter).zfill(5):
                result.append(f)
        elif chapter_range:
            start, end = str(chapter_range[0]).zfill(5), str(chapter_range[1]).zfill(5)
            if start <= cid <= end:
                result.append(f)
    return result
