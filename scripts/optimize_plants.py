#!/usr/bin/env python3
"""
Optimize all 4 source JSON files: remove duplicates, fix toxicity, rename IDs,
fix scientific names, fix care tips, fix metadata, add new plants, sort, and update counts.

Idempotent -- safe to run multiple times.

Usage: python3 scripts/optimize_plants.py
"""

import json
import re
import sys
from pathlib import Path

from schema import (
    CATEGORY_ORDER,
    METADATA_KEY_ORDER,
    LANG_ENTRY_KEY_ORDER,
)

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"
NEW_PLANTS_PATH = Path(__file__).parent / "new_plants.json"

LANG_FILES = {
    "en": SOURCE_DIR / "common_plants_language_en.json",
    "es": SOURCE_DIR / "common_plants_language_es.json",
    "zh": SOURCE_DIR / "common_plants_language_zh-Hans.json",
}
META_PATH = SOURCE_DIR / "common_plants_metadata.json"

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

changes_log: list[str] = []


def log(msg: str):
    changes_log.append(msg)
    print(f"  {msg}")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_entry(entries: list[dict], plant_id: str) -> dict | None:
    """Find a language entry by id."""
    for e in entries:
        if e.get("id") == plant_id:
            return e
    return None


def remove_entry(entries: list[dict], plant_id: str) -> bool:
    """Remove entry by id; returns True if found."""
    for i, e in enumerate(entries):
        if e.get("id") == plant_id:
            entries.pop(i)
            return True
    return False


def reorder_lang_entry(entry: dict) -> dict:
    ordered = {}
    for key in LANG_ENTRY_KEY_ORDER:
        if key in entry:
            ordered[key] = entry[key]
    for key in entry:
        if key not in ordered:
            ordered[key] = entry[key]
    return ordered


def reorder_meta_entry(entry: dict) -> dict:
    ordered = {}
    for key in METADATA_KEY_ORDER:
        if key in entry:
            ordered[key] = entry[key]
    for key in entry:
        if key not in ordered:
            ordered[key] = entry[key]
    return ordered


def sort_key(plant_id: str, category: str) -> tuple:
    try:
        cat_idx = CATEGORY_ORDER.index(category)
    except ValueError:
        cat_idx = len(CATEGORY_ORDER)
    return (cat_idx, plant_id.lower())


def replace_in_field(entry: dict, field: str, old: str, new: str) -> bool:
    """Replace text in a field. Returns True if replacement happened."""
    if not entry or field not in entry:
        return False
    val = entry[field]
    if old in val:
        entry[field] = val.replace(old, new)
        return True
    return False


def replace_re_in_field(entry: dict, field: str, pattern: str, replacement: str) -> bool:
    """Regex replace in a field. Returns True if replacement happened."""
    if not entry or field not in entry:
        return False
    new_val, n = re.subn(pattern, replacement, entry[field])
    if n > 0:
        entry[field] = new_val
        return True
    return False


def append_to_care_tips(entry: dict, text: str) -> bool:
    """Append text to careTips if not already present."""
    if not entry or "careTips" not in entry:
        return False
    if text in entry["careTips"]:
        return False  # idempotent
    entry["careTips"] = entry["careTips"].rstrip()
    if not entry["careTips"].endswith("."):
        entry["careTips"] += "."
    entry["careTips"] += " " + text
    return True


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("OPTIMIZE PLANTS -- Source Data Optimizer")
    print("=" * 60)

    # Load all files
    meta = load_json(META_PATH)
    meta_block = meta.pop("_metadata", None)

    lang_data = {}
    lang_meta = {}
    lang_entries = {}

    for locale, path in LANG_FILES.items():
        data = load_json(path)
        lang_data[locale] = data
        metadata_entry = None
        entries = []
        for item in data:
            if "_metadata" in item:
                metadata_entry = item
            elif item.get("id"):
                entries.append(item)
        lang_meta[locale] = metadata_entry
        lang_entries[locale] = entries

    print(f"\nLoaded metadata: {len(meta)} plant entries")
    for locale in lang_entries:
        print(f"Loaded {locale}: {len(lang_entries[locale])} plant entries")

    # ─────────────────────────────────────────────
    # 1. REMOVE DUPLICATES (merge pairs)
    # ─────────────────────────────────────────────
    print("\n--- Step 1: Remove duplicates ---")

    # Merge spec: (keep_id, remove_ids, aka_en, aka_es, aka_zh)
    MERGE_PAIRS = [
        ("burros-tail", ["sedum-morganianum"],
         "Donkey's Tail",
         "Cola de asno",
         "\u9a74\u5c3e"),
        ("string-of-dolphins", ["senecio-peregrinus"],
         "Dolphin Plant, Dolphin Succulent",
         "Planta delf\u00edn, Suculenta delf\u00edn",
         "\u6d77\u8c5a\u5f26\u6708"),
        ("maranta-prayer-plant", ["maranta-leuconeura"],
         "Maranta Leuconeura",
         "Maranta Leuconeura",
         "\u5b54\u96c0\u7af9\u828b"),
        ("gloxinia", ["sinningia"],
         "Florist's Gloxinia, Sinningia",
         "Gloxinia de florista, Sinningia",
         "\u5927\u5ca9\u6850\u82b1\u5e97\u578b"),
        ("joe-pye-weed", ["sweet-joe-pye"],
         "Sweet Joe Pye",
         "Sweet Joe Pye",
         "\u751c\u6cfd\u5170"),
        ("string-of-turtles", ["peperomia-prostrata"],
         "Turtle Vine, Peperomia Prostrata",
         "Enredadera de Tortuga, Peperomia Prostrata",
         "\u9f9f\u80cc\u6912\u8349"),
        ("switchgrass-prairie", ["panicum"],
         "Panicum",
         "Panicum",
         "\u9ecd\u5c5e"),
        ("luffa", ["loofah"],
         "Loofah",
         "Lufa, Esponja Vegetal",
         "\u4e1d\u74dc"),
        ("parlor-palm", ["neanthe-bella-palm"],
         "Neanthe Bella Palm, Bella Palm",
         "Palmera Neanthe Bella",
         "\u8d1d\u62c9\u8896\u73cd\u6930"),
        ("philodendron-heartleaf", ["philodendron-scandens", "philodendron-hederaceum-scandal"],
         "Philodendron Scandens",
         "Philodendron Scandens",
         "\u5fc3\u53f6\u559c\u6797\u828b"),
    ]

    aka_prefixes = {
        "en": "Also known as: ",
        "es": "Tambi\u00e9n conocida como: ",
        "zh": "\u4e5f\u79f0\uff1a",
    }
    aka_suffixes = {
        "en": ". ",
        "es": ". ",
        "zh": "\u3002",
    }

    for keep_id, remove_ids, aka_en, aka_es, aka_zh in MERGE_PAIRS:
        aka_map = {"en": aka_en, "es": aka_es, "zh": aka_zh}

        for locale in lang_entries:
            kept = find_entry(lang_entries[locale], keep_id)
            if not kept:
                log(f"WARNING: {keep_id} not found in {locale}")
                continue

            # Add AKA to description if not already present (idempotent)
            prefix = aka_prefixes[locale]
            aka_text = aka_map[locale]
            suffix = aka_suffixes[locale]

            if aka_text not in kept.get("description", ""):
                aka_str = f"{prefix}{aka_text}{suffix}"
                kept["description"] = aka_str + kept["description"]

            for rid in remove_ids:
                if remove_entry(lang_entries[locale], rid):
                    log(f"Removed {rid} from {locale} (merged into {keep_id})")

        # Remove from metadata
        for rid in remove_ids:
            if rid in meta:
                del meta[rid]
                log(f"Removed {rid} from metadata")

    # ─────────────────────────────────────────────
    # 2. FIX TOXICITY
    # ─────────────────────────────────────────────
    print("\n--- Step 2: Fix toxicity ---")

    # Change to nonToxic
    NON_TOXIC_IDS = [
        "portulacaria-afra", "string-of-hearts", "phoenix-roebelenii",
        "hibiscus-tropical", "pteris", "pteris-cretica", "gaillardia",
    ]

    for pid in NON_TOXIC_IDS:
        # Fix metadata
        if pid in meta:
            if meta[pid].get("plantToxicity") != "nonToxic":
                meta[pid]["plantToxicity"] = "nonToxic"
                log(f"Fixed {pid} toxicity to nonToxic in metadata")

        # Fix care tips in all languages
        for locale in lang_entries:
            entry = find_entry(lang_entries[locale], pid)
            if not entry:
                continue

            if locale == "en":
                replace_re_in_field(entry, "careTips",
                                    r"Toxic to pets[^.]*\.", "Non-toxic to pets.")
                replace_re_in_field(entry, "careTips",
                                    r"Toxic to pets", "Non-toxic to pets")
                replace_re_in_field(entry, "careTips",
                                    r"Mildly toxic to pets[^.]*\.", "Non-toxic to pets.")
            elif locale == "es":
                replace_re_in_field(entry, "careTips",
                                    r"T\u00f3xic[oa] para mascotas[^.]*\.",
                                    "No t\u00f3xica para mascotas.")
                replace_re_in_field(entry, "careTips",
                                    r"T\u00f3xic[oa] para mascotas",
                                    "No t\u00f3xica para mascotas")
                replace_re_in_field(entry, "careTips",
                                    r"Ligeramente t\u00f3xic[oa] para mascotas[^.]*\.",
                                    "No t\u00f3xica para mascotas.")
                replace_re_in_field(entry, "careTips",
                                    r"T\u00f3xico para mascotas[^.]*\.",
                                    "No t\u00f3xica para mascotas.")
            elif locale == "zh":
                replace_in_field(entry, "careTips",
                                 "\u5bf9\u5ba0\u7269\u6709\u6bd2",
                                 "\u5bf9\u5ba0\u7269\u65e0\u6bd2")
                replace_in_field(entry, "careTips",
                                 "\u5bf9\u5ba0\u7269\u6709\u8f7b\u5ea6\u6bd2\u6027",
                                 "\u5bf9\u5ba0\u7269\u65e0\u6bd2")
                replace_in_field(entry, "careTips",
                                 "\u5bf9\u5ba0\u7269\u8f7b\u5fae\u6709\u6bd2",
                                 "\u5bf9\u5ba0\u7269\u65e0\u6bd2")

    # Fix phoenix-roebelenii description about toxicity
    for locale in lang_entries:
        entry = find_entry(lang_entries[locale], "phoenix-roebelenii")
        if entry:
            if locale == "en":
                replace_in_field(entry, "description",
                                 "Fruits and leaves contain compounds toxic to pets.",
                                 "Non-toxic to pets.")
            elif locale == "es":
                replace_in_field(entry, "description",
                                 "Frutos y hojas contienen compuestos t\u00f3xicos para mascotas.",
                                 "No t\u00f3xica para mascotas.")
            elif locale == "zh":
                replace_in_field(entry, "description",
                                 "\u679c\u5b9e\u548c\u53f6\u7247\u542b\u5bf9\u5ba0\u7269\u6709\u6bd2\u7269\u8d28\u3002",
                                 "\u5bf9\u5ba0\u7269\u65e0\u6bd2\u3002")

    # Fix pteris and pteris-cretica description about toxicity
    for pid in ["pteris", "pteris-cretica"]:
        for locale in lang_entries:
            entry = find_entry(lang_entries[locale], pid)
            if not entry:
                continue
            if locale == "en":
                replace_in_field(entry, "description",
                                 "Toxic to pets\u2014contains compounds that can cause irritation.",
                                 "Non-toxic to pets.")
                replace_in_field(entry, "description",
                                 "Toxic to pets.",
                                 "Non-toxic to pets.")
            elif locale == "es":
                replace_in_field(entry, "description",
                                 "T\u00f3xico para mascotas.",
                                 "No t\u00f3xica para mascotas.")
            elif locale == "zh":
                replace_in_field(entry, "description",
                                 "\u5bf9\u5ba0\u7269\u6709\u6bd2\u3002",
                                 "\u5bf9\u5ba0\u7269\u65e0\u6bd2\u3002")

    # Change to mildlyToxic
    MILDLY_TOXIC_IDS = [
        "scindapsus", "scindapsus-exotica", "scindapsus-treubii",
        "tradescantia", "tradescantia-nanouk", "tradescantia-purple-heart",
        "tradescantia-zebrina",
    ]

    for pid in MILDLY_TOXIC_IDS:
        if pid in meta:
            if meta[pid].get("plantToxicity") != "mildlyToxic":
                meta[pid]["plantToxicity"] = "mildlyToxic"
                log(f"Fixed {pid} toxicity to mildlyToxic in metadata")

        for locale in lang_entries:
            entry = find_entry(lang_entries[locale], pid)
            if not entry:
                continue
            ct = entry.get("careTips", "")

            if locale == "en":
                if "Mildly toxic to pets" not in ct:
                    replace_re_in_field(entry, "careTips",
                                        r"Toxic to pets\.",
                                        "Mildly toxic to pets -- causes mouth and skin irritation.")
                    replace_re_in_field(entry, "careTips",
                                        r"Toxic to pets(?![\s\-])",
                                        "Mildly toxic to pets -- causes mouth and skin irritation")
                    replace_re_in_field(entry, "careTips",
                                        r"Toxic if ingested by pets\.",
                                        "Mildly toxic to pets -- causes mouth and skin irritation.")
            elif locale == "es":
                if "Ligeramente t\u00f3xica" not in ct:
                    replace_re_in_field(entry, "careTips",
                                        r"T\u00f3xic[oa] para mascotas\.",
                                        "Ligeramente t\u00f3xica para mascotas -- causa irritaci\u00f3n en boca y piel.")
                    replace_re_in_field(entry, "careTips",
                                        r"T\u00f3xic[oa] para mascotas",
                                        "Ligeramente t\u00f3xica para mascotas -- causa irritaci\u00f3n en boca y piel")
                    replace_re_in_field(entry, "careTips",
                                        r"T\u00f3xico para mascotas\.",
                                        "Ligeramente t\u00f3xica para mascotas -- causa irritaci\u00f3n en boca y piel.")
            elif locale == "zh":
                if "\u8f7b\u5ea6\u6709\u6bd2" not in ct:
                    replace_in_field(entry, "careTips",
                                     "\u5bf9\u5ba0\u7269\u6709\u6bd2",
                                     "\u5bf9\u5ba0\u7269\u8f7b\u5ea6\u6709\u6bd2\u2014\u2014\u53ef\u80fd\u5f15\u8d77\u53e3\u8154\u548c\u76ae\u80a4\u523a\u6fc0")

    log("Toxicity fixes applied")

    # ─────────────────────────────────────────────
    # 3. FIX SCIENTIFIC NAMES (EN file)
    # ─────────────────────────────────────────────
    print("\n--- Step 3: Fix scientific names ---")

    en = lang_entries["en"]

    # monstera-peru
    e = find_entry(en, "monstera-peru")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Monstera karstenianum (Monstera peru)",
                            "Monstera sp. 'Peru' (Monstera peru)"):
            log("Fixed monstera-peru scientific name")

    # russian-sage
    e = find_entry(en, "russian-sage")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Perovskia atriplicifolia",
                            "Salvia yangii (syn. Perovskia atriplicifolia)"):
            log("Fixed russian-sage commonExamples")
        replace_in_field(e, "careTips",
                         " May be reclassified as Salvia yangii.", "")
        replace_in_field(e, "careTips",
                         "May be reclassified as Salvia yangii.", "")

    # boysenberry
    e = find_entry(en, "boysenberry")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Rubus \u00d7 loganobaccus",
                            "Rubus ursinus \u00d7 R. idaeus (Boysenberry)"):
            log("Fixed boysenberry scientific name")

    # lily-asiatic
    e = find_entry(en, "lily-asiatic")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Lilium asiaticum (Asiatic lily)",
                            "Lilium (Asiatic hybrids)"):
            log("Fixed lily-asiatic scientific name")

    # lily-oriental
    e = find_entry(en, "lily-oriental")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Lilium orientalis (Oriental lily)",
                            "Lilium (Oriental hybrids)"):
            log("Fixed lily-oriental scientific name")

    # lily-calla-mini
    e = find_entry(en, "lily-calla-mini")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Zantedeschia minor (Compact calla)",
                            "Zantedeschia rehmannii (Compact calla)"):
            log("Fixed lily-calla-mini scientific name")

    # mizuna
    e = find_entry(en, "mizuna")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Brassica juncea var. japonica",
                            "Brassica rapa var. nipposinica"):
            log("Fixed mizuna scientific name")

    # calathea-zebrina: Add Goeppertia reference
    e = find_entry(en, "calathea-zebrina")
    if e:
        if "Goeppertia" not in e.get("commonExamples", ""):
            if replace_in_field(e, "commonExamples",
                                "Calathea zebrina (Zebra plant)",
                                "Calathea zebrina (syn. Goeppertia zebrina; Zebra plant)"):
                log("Added Goeppertia reference to calathea-zebrina")

    # calathea-white-star: Add Goeppertia reference
    e = find_entry(en, "calathea-white-star")
    if e:
        if "Goeppertia" not in e.get("commonExamples", ""):
            if replace_in_field(e, "commonExamples",
                                "Calathea 'White Star'",
                                "Calathea 'White Star' (syn. Goeppertia 'White Star')"):
                log("Added Goeppertia reference to calathea-white-star")

    # dracaena-song-of-india
    e = find_entry(en, "dracaena-song-of-india")
    if e:
        if "'Song of India'" not in e.get("commonExamples", ""):
            if replace_in_field(e, "commonExamples",
                                "Dracaena reflexa (Song of India, Song of Jamaica)",
                                "Dracaena reflexa 'Song of India' (Song of India, Song of Jamaica)"):
                log("Fixed dracaena-song-of-india cultivar name")

    # gasteria
    e = find_entry(en, "gasteria")
    if e:
        if "Asphodelaceae" not in e.get("description", ""):
            if replace_in_field(e, "description",
                                "Tongue-shaped succulents related to Haworthia, shade-tolerant and easy-care.",
                                "Tongue-shaped succulents closely related to Haworthia and Aloe in the family Asphodelaceae; shade-tolerant and easy-care."):
                log("Fixed gasteria description")

    # ─────────────────────────────────────────────
    # 4. RENAME IDs
    # ─────────────────────────────────────────────
    print("\n--- Step 4: Rename IDs ---")

    # (old_id, new_id, new_typeName_en, new_typeName_es, new_typeName_zh)
    # None means keep existing typeName for that locale
    ID_RENAMES = [
        ("common-viper", "vipers-bugloss",
         "Viper's Bugloss", "Viborera", "\u84dd\u84df"),
        ("alocasia-mahorani", "alocasia-maharani",
         "Alocasia Maharani", "Alocasia Maharani", "\u7070\u9f99\u6d77\u828b"),
        ("purple-cone-prairie", "prairie-coneflower",
         "Prairie Coneflower", "Equin\u00e1cea de Pradera", None),
        ("chinese-evergreen-maria", "aglaonema-maria",
         None, None, None),
        ("chinese-evergreen-silver", "aglaonema-silver-bay",
         None, None, None),
    ]

    for old_id, new_id, new_name_en, new_name_es, new_name_zh in ID_RENAMES:
        new_names = {"en": new_name_en, "es": new_name_es, "zh": new_name_zh}

        # Rename in metadata
        if old_id in meta and new_id not in meta:
            meta[new_id] = meta.pop(old_id)
            log(f"Renamed {old_id} -> {new_id} in metadata")
        elif old_id not in meta:
            log(f"WARNING: {old_id} not found in metadata for rename")

        # Rename in language files
        for locale in lang_entries:
            entry = find_entry(lang_entries[locale], old_id)
            if entry:
                entry["id"] = new_id
                nn = new_names.get(locale)
                if nn:
                    entry["typeName"] = nn
                log(f"Renamed {old_id} -> {new_id} in {locale}")
            else:
                # Check if already renamed (idempotent)
                already = find_entry(lang_entries[locale], new_id)
                if already:
                    nn = new_names.get(locale)
                    if nn and already.get("typeName") != nn:
                        already["typeName"] = nn
                else:
                    log(f"WARNING: {old_id} not found in {locale} for rename")

    # ─────────────────────────────────────────────
    # 5. FIX typeNames/descriptions (EN)
    # ─────────────────────────────────────────────
    print("\n--- Step 5: Fix typeNames/descriptions ---")

    # echinopsis
    e = find_entry(en, "echinopsis")
    if e and e.get("typeName") == "Sea Urchin Cactus":
        e["typeName"] = "Easter Lily Cactus"
        log("Fixed echinopsis typeName to Easter Lily Cactus")

    # warm-season-annuals: Remove "Also known as: Petunia." from description
    e = find_entry(en, "warm-season-annuals")
    if e:
        if replace_in_field(e, "description",
                            "Also known as: Petunia. ", ""):
            log("Fixed warm-season-annuals description")

    # root-vegetables
    e = find_entry(en, "root-vegetables")
    if e:
        if replace_in_field(e, "description",
                            "Also known as: Carrot. ", ""):
            log("Fixed root-vegetables description")

    # flowering-shrubs
    e = find_entry(en, "flowering-shrubs")
    if e:
        if replace_in_field(e, "description",
                            "Also known as: Bigleaf, Panicle, Oakleaf. ", ""):
            log("Fixed flowering-shrubs description")

    # beet-greens
    e = find_entry(en, "beet-greens")
    if e:
        replace_in_field(e, "description",
                         "Also known as: leaf and stem. ",
                         "Also known as: Beet tops. ")
        replace_in_field(e, "commonExamples",
                         "Beta vulgaris (leaf and stem)",
                         "Beta vulgaris (Beet greens, Beet tops)")
        log("Fixed beet-greens description and commonExamples")

    # dandelion-greens
    e = find_entry(en, "dandelion-greens")
    if e:
        replace_in_field(e, "description",
                         "Also known as: edible greens. ",
                         "Also known as: Dandelion leaves. ")
        replace_in_field(e, "commonExamples",
                         "Taraxacum officinale (edible greens)",
                         "Taraxacum officinale (Dandelion leaves)")
        log("Fixed dandelion-greens description and commonExamples")

    # currant
    e = find_entry(en, "currant")
    if e:
        if replace_in_field(e, "description",
                            "Also known as: Red. ",
                            "Also known as: Redcurrant, Blackcurrant. "):
            log("Fixed currant description")

    # catnip
    e = find_entry(en, "catnip")
    if e:
        if replace_in_field(e, "commonExamples",
                            "Nepeta cataria (Catmint herb)",
                            "Nepeta cataria (Catnip)"):
            log("Fixed catnip commonExamples")

    # sweet-potato-vine
    e = find_entry(en, "sweet-potato-vine")
    if e:
        replace_in_field(e, "description",
                         "Also known as: ornamental cultivar.",
                         "Also known as: Ornamental sweet potato.")
        replace_in_field(e, "commonExamples",
                         "Ipomoea batatas (ornamental cultivar)",
                         "Ipomoea batatas (Ornamental sweet potato)")
        log("Fixed sweet-potato-vine description and commonExamples")

    # yellow-coneflower: Remove Ratibida reference
    e = find_entry(en, "yellow-coneflower")
    if e:
        if replace_in_field(e, "description",
                            "Native Ratibida with drooping yellow petals; drought tolerant; prairie wildflower.",
                            "Yellow-petaled Echinacea species native to the Ozarks; drought tolerant prairie wildflower."):
            log("Fixed yellow-coneflower description")

    # blechnum: Change typeName to Dwarf Tree Fern
    e = find_entry(en, "blechnum")
    if e:
        if e.get("typeName") != "Dwarf Tree Fern":
            e["typeName"] = "Dwarf Tree Fern"
            replace_in_field(e, "description",
                             "Tree fern with upright fronds; dwarf species form a trunk-like base. Tolerates slightly drier air than many ferns.",
                             "Silver Lady Fern with upright fronds forming a trunk-like base. Tolerates slightly drier air than many ferns.")
            log("Fixed blechnum typeName and description")

    # ─────────────────────────────────────────────
    # 6. FIX CARE TIPS
    # ─────────────────────────────────────────────
    print("\n--- Step 6: Fix care tips ---")

    # European plants with "prairie native" text
    # Note: common-viper was renamed to vipers-bugloss
    EUROPEAN_PLANTS = [
        "field-scabious", "meadow-cranesbill", "oxeye-daisy",
        "great-mullein", "red-clover", "vipers-bugloss",
    ]

    for pid in EUROPEAN_PLANTS:
        e = find_entry(en, pid)
        if e:
            if replace_in_field(e, "careTips",
                                "many prairie natives prefer lean soil",
                                "tolerates lean soil; European wildflower"):
                log(f"Fixed {pid} care tips (European wildflower)")

    # Moisture-loving plants: fix drought tolerant claim
    MOIST_PLANTS = [
        "joe-pye-weed", "ironweed", "swamp-milkweed", "new-england-aster",
    ]

    for pid in MOIST_PLANTS:
        e = find_entry(en, pid)
        if e:
            if replace_in_field(e, "careTips",
                                "drought tolerant once established",
                                "prefers consistently moist soil"):
                log(f"Fixed {pid} care tips (moist soil)")

    # foxglove: Add toxicity warning
    e = find_entry(en, "foxglove")
    if e:
        toxicity_text = "All parts highly toxic to humans and pets. Contains cardiac glycosides."
        if append_to_care_tips(e, toxicity_text):
            log("Added toxicity warning to foxglove care tips")

    # phlox: Add mildew guidance
    e = find_entry(en, "phlox")
    if e:
        mildew_text = "Choose mildew-resistant cultivars. Space for air circulation. Avoid overhead watering."
        if append_to_care_tips(e, mildew_text):
            log("Added mildew guidance to phlox care tips")

    # peony: Add ant note
    e = find_entry(en, "peony")
    if e:
        ant_text = "Ants on buds are normal and harmless\u2014they feed on bud nectar."
        if append_to_care_tips(e, ant_text):
            log("Added ant note to peony care tips")

    # clematis: Add pruning groups
    e = find_entry(en, "clematis")
    if e:
        pruning_text = ("Pruning varies by group: Group 1 (spring bloomers) minimal pruning; "
                        "Group 2 (repeat bloomers) light pruning after first flush; "
                        "Group 3 (summer/fall bloomers) hard prune in late winter.")
        if append_to_care_tips(e, pruning_text):
            log("Added pruning groups to clematis care tips")

    # lantana: Add frost-tender note
    e = find_entry(en, "lantana")
    if e:
        frost_text = "Perennial in frost-free zones (USDA 9-11); grown as annual in cooler climates."
        if append_to_care_tips(e, frost_text):
            log("Added frost-tender note to lantana care tips")

    # lithops: Fix growth period info
    e = find_entry(en, "lithops")
    if e:
        old_care = ("Water ONLY during growth periods (spring and fall) when new leaves appear. "
                    "Keep completely dry during summer and winter dormancy - "
                    "even minimal watering during dormancy causes rot.")
        new_care = ("Water sparingly in fall when new leaves emerge. "
                    "Keep dry in summer dormancy and during winter/spring splitting.")
        if replace_in_field(e, "careTips", old_care, new_care):
            log("Fixed lithops care tips growth period")

    # ─────────────────────────────────────────────
    # 7. FIX METADATA VALUES
    # ─────────────────────────────────────────────
    print("\n--- Step 7: Fix metadata values ---")

    # crassula-ovata-minor: springInterval=14, summerInterval=14
    if "crassula-ovata-minor" in meta:
        m = meta["crassula-ovata-minor"]
        if m.get("springInterval") != 14 or m.get("summerInterval") != 14:
            m["springInterval"] = 14
            m["summerInterval"] = 14
            log("Fixed crassula-ovata-minor watering intervals to 14/14")

    # english-ivy: temperaturePreference=[10,27]
    if "english-ivy" in meta:
        m = meta["english-ivy"]
        if m.get("temperaturePreference") != [10, 27]:
            m["temperaturePreference"] = [10, 27]
            log("Fixed english-ivy temperaturePreference to [10,27]")

    # bird-of-paradise: humidityPreference="medium"
    if "bird-of-paradise" in meta:
        m = meta["bird-of-paradise"]
        if m.get("humidityPreference") != "medium":
            m["humidityPreference"] = "medium"
            log("Fixed bird-of-paradise humidityPreference to medium")

    # cast-iron-plant: temperaturePreference=[7,27]
    if "cast-iron-plant" in meta:
        m = meta["cast-iron-plant"]
        if m.get("temperaturePreference") != [7, 27]:
            m["temperaturePreference"] = [7, 27]
            log("Fixed cast-iron-plant temperaturePreference to [7,27]")

    # ─────────────────────────────────────────────
    # 8. LOAD NEW PLANTS
    # ─────────────────────────────────────────────
    print("\n--- Step 8: Load new plants ---")

    if NEW_PLANTS_PATH.exists():
        new_plants = load_json(NEW_PLANTS_PATH)

        # Format: list of {id, meta, en, es, zh} objects
        added_count = 0
        existing_meta_ids = set(meta.keys())

        for plant in new_plants:
            pid = plant.get("id")
            if not pid or pid in existing_meta_ids:
                continue

            # Add metadata
            if "meta" in plant:
                meta[pid] = plant["meta"]

            # Add language entries
            for locale in ("en", "es", "zh"):
                if locale in plant:
                    entry = {"id": pid, **plant[locale]}
                    existing_ids = {e.get("id") for e in lang_entries[locale]}
                    if pid not in existing_ids:
                        lang_entries[locale].append(entry)

            added_count += 1

        log(f"Added {added_count} new plants from new_plants.json")
    else:
        log("No new_plants.json found -- skipping new plant additions")

    # ─────────────────────────────────────────────
    # 9. SORT ALL FILES
    # ─────────────────────────────────────────────
    print("\n--- Step 9: Sort all files ---")

    # Sort metadata by category, then alphabetically by plant ID
    plant_ids = [k for k in meta.keys()]
    sorted_ids = sorted(
        plant_ids,
        key=lambda pid: sort_key(pid, meta[pid].get("category", ""))
    )

    sorted_meta = {}
    if meta_block is not None:
        sorted_meta["_metadata"] = meta_block
    for pid in sorted_ids:
        sorted_meta[pid] = reorder_meta_entry(meta[pid])

    log(f"Sorted metadata: {len(sorted_ids)} plants")

    # Build id -> order for language file sorting
    id_to_order = {pid: i for i, pid in enumerate(sorted_ids)}

    for locale in lang_entries:
        entries = lang_entries[locale]
        entries.sort(
            key=lambda e: id_to_order.get(e.get("id", ""), len(sorted_ids))
        )
        lang_entries[locale] = [reorder_lang_entry(e) for e in entries]
        log(f"Sorted {locale}: {len(entries)} plants")

    # ─────────────────────────────────────────────
    # 10. UPDATE COUNTS
    # ─────────────────────────────────────────────
    print("\n--- Step 10: Update counts ---")

    plant_count = len(sorted_ids)

    # Metadata _metadata.plantCount
    if meta_block is not None:
        old_count = meta_block.get("plantCount", 0)
        meta_block["plantCount"] = plant_count
        sorted_meta["_metadata"] = meta_block
        log(f"Updated metadata plantCount: {old_count} -> {plant_count}")

    # Language files _metadata.totalPlants
    for locale in lang_entries:
        lm = lang_meta[locale]
        if lm and "_metadata" in lm:
            old_count = lm["_metadata"].get("totalPlants", 0)
            lm["_metadata"]["totalPlants"] = plant_count
            log(f"Updated {locale} totalPlants: {old_count} -> {plant_count}")

    # ─────────────────────────────────────────────
    # 11. WRITE ALL FILES
    # ─────────────────────────────────────────────
    print("\n--- Step 11: Write files ---")

    save_json(META_PATH, sorted_meta)
    log(f"Wrote {META_PATH.name}")

    for locale, path in LANG_FILES.items():
        result = []
        if lang_meta[locale] is not None:
            result.append(lang_meta[locale])
        result.extend(lang_entries[locale])
        save_json(path, result)
        log(f"Wrote {path.name} ({len(lang_entries[locale])} plants)")

    # ─────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total plants in metadata: {plant_count}")
    for locale in lang_entries:
        print(f"  Total plants in {locale}: {len(lang_entries[locale])}")
    print(f"  Total changes logged: {len(changes_log)}")
    print("\nDone. Run: python3 scripts/release.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
