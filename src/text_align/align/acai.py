"""acai-align: create entity alignments using ACAI data and a mini-concordance approach.

Given ACAI person/place/group/etc. entities with word-level references, and a
kathairo target TSV, this tool attempts to align each entity to the precise
target tokens that represent it.  Matching uses reference-list overlap scoring
plus Jaro-Winkler string similarity (with trabina translations where available).

CLI entry point: ``acai-align``
"""

import argparse
import os
from pathlib import Path

import regex as re
from biblelib.word import BCVWPID

from text_align.config import load_config_from_args, require
from text_align.migrate.alignment_io import write_alignment_json
from text_align.stopwords import load_stopwordsiso_stopwords

from .acai_common import (
    ACAI_TYPES,
    AcaiEntity,
    TargetEntity,
    find_best_match,
    get_similarly_occurring_targets,
    load_acai_entities,
    load_alignment_template,
    populate_alignment,
    load_trabina_translations,
)


# ---------------------------------------------------------------------------
# Target-verse loading
# ---------------------------------------------------------------------------

def load_target_verses(
    targets_folder: Path,
    target_edition: str,
    corpus: str,
    target_language: str,
) -> tuple[dict[str, list[TargetEntity]], dict[str, str]]:
    """Read a kathairo TSV and return (target_verses, target_source_map).

    *target_verses*: source-BCV → list of TargetEntity (one per non-excluded, non-stop token)
    *target_source_map*: token_id → source_verse BCV string
    """
    stopwords = load_stopwordsiso_stopwords(target_language)
    target_verses: dict[str, list[TargetEntity]] = {}
    target_source_map: dict[str, str] = {}

    tsv_path = targets_folder / f"{corpus}_{target_edition}.tsv"
    with open(tsv_path, "r", encoding="utf-8") as f:
        for line in f:
            cols = line.strip().split("\t")
            token_id = cols[0]
            if token_id.startswith("id"):
                continue
            source_reference = cols[1] if cols[1] else BCVWPID(token_id).to_bcvid
            label = cols[2]
            target_source_map[token_id] = source_reference

            label_key = label.lower()
            if label_key in stopwords:
                continue
            if len(label_key) <= 1:
                continue
            if re.search(r"^\p{P}$", label_key):
                continue
            if re.search(r"^ $", label_key):  # non-breaking space
                continue
            if re.search(r"^\d+", label_key):
                continue

            entity = TargetEntity(label_key, label, [source_reference], [token_id])
            target_verses.setdefault(source_reference, []).append(entity)

    return target_verses, target_source_map


# ---------------------------------------------------------------------------
# Mini-concordance matching
# ---------------------------------------------------------------------------

def get_target_entity_verses(
    acai_entity_references: list[str],
    target_verses: dict[str, list[TargetEntity]],
) -> list[list[TargetEntity]]:
    verses = []
    for ref in acai_entity_references:
        if ref in target_verses:
            verses.append(target_verses[ref])
        else:
            print(f"Missing reference: {ref}")
    return verses


def build_target_entities(
    target_entity_verses: list[list[TargetEntity]],
) -> dict[str, TargetEntity]:
    target_entities: dict[str, TargetEntity] = {}
    for verse in target_entity_verses:
        for entity in verse:
            token_id = entity.explicit_instances[0]
            source_ref = str(entity.references[0])
            if entity.id not in target_entities:
                target_entities[entity.id] = TargetEntity(entity.id, entity.label, [source_ref], [token_id])
            else:
                if source_ref not in target_entities[entity.id].references:
                    target_entities[entity.id].references.append(source_ref)
                target_entities[entity.id].explicit_instances.append(token_id)
    return target_entities


def load_references_from_instances(explicit_instances: list, corpus: str) -> list[str]:
    refs = []
    for instances in explicit_instances:
        for instance in instances:
            bcv = BCVWPID(instance).to_bcvid
            if bcv not in refs:
                refs.append(bcv)
    return refs


def find_matches_in_subset(
    acai_entity: AcaiEntity,
    target_entities: dict[str, TargetEntity],
    trabina_translations: dict[str, str],
) -> TargetEntity | None:
    similar = get_similarly_occurring_targets(acai_entity, target_entities)
    if not similar:
        return None
    best = find_best_match(acai_entity, similar, trabina_translations)
    if len(best) > 1:
        print(f"Multiple matches for {acai_entity.label} ({acai_entity.id}): {best}")
    return target_entities[best[0]] if best else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    config_defaults = load_config_from_args(output_suffix="ACAI")

    p = argparse.ArgumentParser(
        description=(
            "Create entity alignments using ACAI data and a mini-concordance approach."
        )
    )
    p.add_argument("--config", metavar="NAME",
                   help="Load defaults from configs/<NAME>.yaml (CLI args override)")
    p.add_argument("--target-language", default=None,
                   help="ISO 639-3 language code for the target translation, e.g. spa")
    p.add_argument("--target-edition", default=None,
                   help="Target edition ID, e.g. BONBV")
    p.add_argument("--targets-dir", default=None, type=Path,
                   help="Directory containing ot_<edition>.tsv and nt_<edition>.tsv")
    p.add_argument("--acai-data-dir", default=None, type=Path,
                   help="Path to the ACAI root directory (e.g. C:/git/BibleAquifer/ACAI)")
    p.add_argument("--trabina-dir", default=None, type=Path,
                   help="Path to the trabina data/weighted/ directory")
    p.add_argument("--output-dir", default=None, type=Path,
                   help="Directory to write ACAI alignment JSON files")
    p.add_argument("--corpora", nargs="+", default=["ot", "nt"],
                   choices=["ot", "nt"],
                   help="Which corpora to process (default: ot nt)")
    p.add_argument("--acai-types", nargs="+", default=ACAI_TYPES,
                   help=f"ACAI entity types to include (default: {ACAI_TYPES})")
    p.add_argument("--include-secondaries", action="store_true",
                   help="Include non-primary ACAI entities")
    p.add_argument("--creator", default="text-align",
                   help="Creator string written into alignment meta (default: text-align)")
    p.set_defaults(**config_defaults)
    args = p.parse_args()
    require(args, "target_language", "target_edition",
            "targets_dir", "acai_data_dir", "trabina_dir", "output_dir")
    return args


def main() -> None:
    args = parse_args()

    print(f"Loading trabina translations for {args.target_language} ...")
    trabina = load_trabina_translations(args.trabina_dir, args.target_language)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for corpus in args.corpora:
        print(f"\n--- {corpus.upper()} ---")
        acai_entities = load_acai_entities(
            args.acai_data_dir, args.acai_types, corpus,
            include_secondaries=args.include_secondaries,
        )
        print(f"Loaded {len(acai_entities)} ACAI entities.")

        tsv_path = args.targets_dir / f"{corpus}_{args.target_edition}.tsv"
        if not tsv_path.exists():
            print(f"Target TSV not found, skipping: {tsv_path}")
            continue
        target_verses, target_source_map = load_target_verses(
            args.targets_dir, args.target_edition, corpus, args.target_language
        )

        matches: dict[str, TargetEntity] = {}
        for entity_id, entity in acai_entities.items():
            entity_refs = load_references_from_instances(entity.explicit_instances, corpus)
            entity_refs.sort()
            verse_list = get_target_entity_verses(entity_refs, target_verses)
            target_ents = build_target_entities(verse_list)
            best = find_matches_in_subset(entity, target_ents, trabina)
            if best is not None:
                print(f"  {entity.label} ({entity_id}) → {best.label} ({best.id})")
                matches[entity_id] = best
            else:
                print(f"  No match: {entity.label} ({entity_id})")

        corpus_edition = "WLCM" if corpus == "ot" else "SBLGNT"
        alignment = populate_alignment(
            load_alignment_template(corpus, args.target_edition, creator=args.creator),
            matches, acai_entities, target_source_map,
        )

        out_path = args.output_dir / f"{corpus_edition}-{args.target_edition}-manual.json"
        write_alignment_json(alignment, out_path)
        n_records = len(alignment["groups"][0]["records"])
        print(f"  → {out_path}  ({n_records} records)")


if __name__ == "__main__":
    main()
