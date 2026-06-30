"""Shared utilities for ACAI-based alignment creation.

Consolidates code previously split across common.py and acai_align_mini_concord.py
in internal-Alignments.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import jellyfish
import regex as re
from biblelib.word import BCVWPID
from unidecode import unidecode

from text_align.stopwords import load_stopwordsiso_stopwords


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AcaiEntity:
    """An ACAI person, place, group, deity, fauna, flora, or realia entity."""

    id: str
    is_primary: bool
    acai_type: str
    label: str
    references: list
    explicit_instances: list


@dataclass
class TargetEntity:
    """A token or term from the translation side, used for ACAI matching."""

    id: str
    label: str
    references: list
    explicit_instances: list


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ACAI_TYPES: list[str] = ["people", "places", "groups", "deities", "keyterms",
                         "fauna", "flora", "realia"]
TYPE_TO_FOLDER_MAP: dict[str, str] = {
    "person": "people",
    "place": "places",
    "group": "groups",
    "deity": "deities",
    "fauna": "fauna",
    "flora": "flora",
    "realia": "realia",
    "keyterm": "keyterms",
}
MINIMUM_GOOD_SCORE: float = 0.70


# ---------------------------------------------------------------------------
# Corpus helpers
# ---------------------------------------------------------------------------

def remove_corpus(corpus: str, references: list[str]) -> list[str]:
    """Return only the references belonging to *corpus* ('ot' or 'nt')."""
    result = []
    for ref in references:
        book_num = int(ref[:2])
        if corpus == "ot" and book_num < 40:
            result.append(ref)
        elif corpus == "nt" and book_num >= 40:
            result.append(ref)
    return result


def is_generic_entity(acai_data: dict[str, Any]) -> bool:
    return bool(re.search(r"Generic", acai_data["id"]))


# ---------------------------------------------------------------------------
# ACAI entity loading
# ---------------------------------------------------------------------------

def load_acai_entities(
    acai_folder: Path,
    acai_types: list[str],
    corpus: str,
    include_secondaries: bool = False,
    include_pronominals: bool = False,
) -> dict[str, AcaiEntity]:
    """Load ACAI entities for *corpus* from *acai_folder*.

    Returns a dict of entity ID → AcaiEntity.

    *include_secondaries*: when True, non-primary entities are included and
    duplicate references are removed from the primary.
    *include_pronominals*: when True, pronominal referents are merged into
    explicit instances.
    """
    acai_entities: dict[str, AcaiEntity] = {}
    for acai_type in acai_types:
        type_folder = acai_folder / acai_type / "json/"
        if not type_folder.exists():
            print(f"ACAI type folder not found: {type_folder}")
            continue
        for acai_file in os.listdir(type_folder):
            with open(type_folder / acai_file, "r", encoding="utf-8") as f:
                acai_data = json.load(f)
            if acai_data.get("non_biblical"):
                continue
            if is_generic_entity(acai_data):
                continue

            entity_id = acai_data["id"]
            is_primary = entity_id == acai_data["primary_id"]

            if not is_primary and not include_secondaries:
                continue

            label = acai_data["localizations"]["eng"]["preferred_label"]
            references = list(acai_data.get("references", []))
            explicit_instances = dict(acai_data.get("explicit_instances", {}))

            if include_pronominals and "pronominal_referents" in acai_data:
                pronominals = acai_data["pronominal_referents"]
                if pronominals:
                    if not explicit_instances:
                        explicit_instances = pronominals
                    else:
                        for loc_corpus, instances in pronominals.items():
                            if loc_corpus in explicit_instances:
                                explicit_instances[loc_corpus].extend(instances)
                            else:
                                explicit_instances[loc_corpus] = instances

            if not explicit_instances and not references:
                print(f"No references or explicit instances for {entity_id} ({label})")
                continue

            if is_primary and include_secondaries and "referred_to_as" in acai_data:
                for secondary in acai_data["referred_to_as"]:
                    secondary_key, secondary_name = secondary.split(":", 1)
                    secondary_file = (
                        acai_folder
                        / TYPE_TO_FOLDER_MAP[secondary_key]
                        / f"json/acai/{secondary_name}.json"
                    )
                    if not secondary_file.exists():
                        print(f"Secondary file not found: {secondary_file}")
                        continue
                    with open(secondary_file, "r", encoding="utf-8") as f:
                        sec_data = json.load(f)
                    if sec_data["id"] == sec_data["primary_id"]:
                        continue
                    if "references" in sec_data:
                        references = list(set(references) - set(sec_data["references"]))
                    if "explicit_instances" in sec_data:
                        for loc_corpus, sec_instances_list in sec_data["explicit_instances"].items():
                            if loc_corpus not in explicit_instances:
                                continue
                            sec_flat = [inst for sublist in sec_instances_list for inst in sublist]
                            for primary_instances in explicit_instances[loc_corpus]:
                                for sec_inst in sec_flat:
                                    if sec_inst in primary_instances:
                                        primary_instances.remove(sec_inst)

            # filter to the requested corpus
            corpus_explicit_instances: list = []
            if corpus == "ot" and "wlc" in explicit_instances:
                corpus_explicit_instances = explicit_instances["wlc"]
            elif corpus == "nt" and "SBLGNT" in explicit_instances:
                corpus_explicit_instances = explicit_instances["SBLGNT"]

            corpus_references = remove_corpus(corpus, references)

            if corpus_references and corpus_explicit_instances:
                acai_entities[entity_id] = AcaiEntity(
                    entity_id, is_primary, acai_type, label,
                    corpus_references, corpus_explicit_instances,
                )

    return acai_entities


def build_word_entity_map(
    acai_entities: dict[str, AcaiEntity],
) -> dict[str, list[AcaiEntity]]:
    """Invert *acai_entities* into a word-ID → list[AcaiEntity] map.

    Used by the HTML renderer to annotate each source token with its entities.
    Strips the leading corpus-indicator prefix (``'o'`` / ``'n'``) from IDs.
    """
    word_map: dict[str, list[AcaiEntity]] = {}
    for entity in acai_entities.values():
        for explicit_instances in entity.explicit_instances:
            for raw_instance in explicit_instances:
                instance = re.sub(r"^[on]", "", raw_instance)
                word_map.setdefault(instance, []).append(entity)
    return word_map


# ---------------------------------------------------------------------------
# Matching / scoring
# ---------------------------------------------------------------------------

def compute_list_similarity(
    acai_references: list[str], target_references: list[str]
) -> float:
    """Return a [0, 1] similarity score based on reference-list overlap."""
    if not acai_references or not target_references:
        return 0.0
    common = set(acai_references).intersection(target_references)
    if not common:
        return 0.0
    diff = set(acai_references).symmetric_difference(target_references)
    if len(diff) >= len(common):
        if len(common) / len(diff) < 0.2:
            return 0.0
        if len(common) == len(diff) and len(common) > 1:
            return 0.0
    return len(common) / len(acai_references)


def get_similarly_occurring_targets(
    entity: AcaiEntity, target_entities: dict[str, TargetEntity]
) -> dict[float, list[str]]:
    """Return a score → [target_entity_id, ...] dict of positively-matching targets."""
    result: dict[float, list[str]] = {}
    for te_id, te in target_entities.items():
        score = compute_list_similarity(entity.references, te.references)
        if score > 0:
            result.setdefault(score, []).append(te_id)
    return result


def find_best_match(
    entity: AcaiEntity,
    similarly_occurring_targets: dict[float, list[str]],
    trabina_translations: dict[str, str],
) -> list[str]:
    """Return the best-matching target entity IDs (may be empty if below threshold)."""
    composite_scores: dict[float, list[str]] = {}
    english_name = re.sub(r"\s*\([^)]+\)\s*$", "", entity.label).lower()

    for list_score, targets in similarly_occurring_targets.items():
        for target in targets:
            if target in trabina_translations:
                string_score = jellyfish.jaro_winkler_similarity(
                    english_name, trabina_translations[target]
                )
            else:
                string_score = jellyfish.jaro_winkler_similarity(
                    english_name, unidecode(target)
                )
            composite = (string_score + list_score) / 2
            composite_scores.setdefault(composite, []).append(target)

    if not composite_scores:
        return []
    best_score = max(composite_scores)
    if best_score >= MINIMUM_GOOD_SCORE:
        return composite_scores[best_score]
    print(
        f"No usable match for {entity.label} ({entity.id}), "
        f"{composite_scores[best_score]} ({best_score:.2f}) below threshold {MINIMUM_GOOD_SCORE}"
    )
    return []


# ---------------------------------------------------------------------------
# Trabina translations
# ---------------------------------------------------------------------------

def load_trabina_translations(trabina_folder: Path, target_language: str) -> dict[str, str]:
    """Load trabina name-translation data for *target_language*.

    Returns a dict of translated-name → person-file-stem.
    *trabina_folder* should point to the ``data/weighted/`` directory.
    """
    translations: dict[str, str] = {}
    if not trabina_folder.exists():
        print(f"Trabina folder not found: {trabina_folder}")
        return translations
    for person_file in os.listdir(trabina_folder):
        with open(trabina_folder / person_file, "r", encoding="utf-8") as f:
            for line in f:
                cols = line.strip().split("\t")
                if len(cols) < 2:
                    continue
                lang = cols[0].split("_")[0]
                if lang == target_language:
                    translation = cols[1]
                    if translation != "-":
                        translations[translation] = person_file
    return translations


# ---------------------------------------------------------------------------
# Alignment template and population
# ---------------------------------------------------------------------------

def load_alignment_template(
    corpus: str, target_edition: str, creator: str = "text-align"
) -> dict[str, Any]:
    """Return an empty SB 0.4 groups alignment skeleton for *corpus* and *target_edition*."""
    corpus_edition = "WLCM" if corpus == "ot" else "SBLGNT"
    return {
        "format": "alignment",
        "version": "0.4",
        "groups": [{
            "type": "translation",
            "meta": {"conformsTo": "0.4", "creator": creator},
            "documents": [
                {"docid": corpus_edition, "scheme": "BCVWP"},
                {"docid": target_edition, "scheme": "BCVWP"},
            ],
            "roles": ["source", "target"],
            "records": [],
        }],
    }


def populate_alignment(
    alignment_data: dict[str, Any],
    matches: dict[str, TargetEntity],
    acai_entities: dict[str, AcaiEntity],
    target_source_map: dict[str, str],
) -> dict[str, Any]:
    """Populate *alignment_data* records from ACAI→target *matches*.

    *matches*: entity_id → TargetEntity (best match found by matching logic)
    *acai_entities*: entity_id → AcaiEntity (full entity data with explicit instances)
    *target_source_map*: target_token_id → source_verse BCV string
    """
    bcv_counts: dict[str, int] = {}
    all_used_source_ids: list[str] = []
    all_used_target_ids: list[str] = []
    records = alignment_data["groups"][0]["records"]

    for match_id, matched_target in matches.items():
        target_instances = list(matched_target.explicit_instances)
        used_explicit_instances: list[str] = []
        for explicit_instances in acai_entities[match_id].explicit_instances:
            used_target_instances: list[str] = []
            for explicit_instance in explicit_instances:
                bcv_explicit = BCVWPID(explicit_instance)
                for target_instance in target_instances:
                    if explicit_instance in used_explicit_instances:
                        continue
                    if target_instance in used_target_instances:
                        continue
                    if bcv_explicit.to_bcvid != target_source_map.get(target_instance):
                        continue
                    bcv_key = bcv_explicit.to_bcvid
                    bcv_counts[bcv_key] = bcv_counts.get(bcv_key, 0) + 1
                    if explicit_instance not in all_used_source_ids and target_instance not in all_used_target_ids:
                        records.append({
                            "source": [explicit_instance],
                            "target": [target_instance],
                        })
                        used_target_instances.append(target_instance)
                        all_used_target_ids.append(target_instance)
                        used_explicit_instances.append(explicit_instance)
                        all_used_source_ids.append(explicit_instance)
            for used in used_target_instances:
                if used in target_instances:
                    target_instances.remove(used)

    records.sort(key=lambda r: r["source"][0] if r.get("source") else "")
    return alignment_data
