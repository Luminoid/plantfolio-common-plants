#!/usr/bin/env python3
"""
Merge common plants metadata and language data into usable JSON files.

Reads source from source/ and outputs to dist/ for distribution (custom URL).
Each output file contains plant entries with both language fields and metadata merged.
Category is translated from the language file's _metadata.sorting.categories header.

Usage:
    python3 scripts/merge_plant_data.py

Output: dist/common_plants.json, common_plants_es.json, common_plants_zh-Hans.json (merged; no metadata file)
"""

import json
import sys
from pathlib import Path

# English category order (index matches _metadata.sorting.categories across locales)
CATEGORY_ORDER = [
    "Houseplants - Low Maintenance", "Houseplants - Aroids", "Houseplants - Ferns",
    "Houseplants - Palms", "Houseplants - Succulents", "Houseplants - Cacti",
    "Houseplants - Flowering", "Houseplants - Prayer Plants", "Houseplants - Vines & Trailing",
    "Houseplants - Specialty", "Outdoor - Trees", "Outdoor - Shrubs", "Outdoor - Perennials",
    "Outdoor - Annuals", "Outdoor - Vines & Climbers", "Outdoor - Groundcovers & Grasses",
    "Vegetables - Leafy Greens", "Vegetables - Fruiting", "Vegetables - Root & Bulb",
    "Fruits & Berries", "Herbs", "Bulbs", "Specialty - Aquatic & Bog", "Specialty - Carnivorous",
    "Specialty - Epiphytes & Moss", "Specialty - Alpine",
]

# Locale code -> (source language filename, output resource name)
LOCALES = [
    ("en", "common_plants_language_en.json", "common_plants"),
    ("es", "common_plants_language_es.json", "common_plants_es"),
    ("zh-Hans", "common_plants_language_zh-Hans.json", "common_plants_zh-Hans"),
]


def translate_category(en_category: str, category_translations: list[str]) -> str:
    """Translate category using header translations. Falls back to English if not found."""
    try:
        idx = CATEGORY_ORDER.index(en_category)
        if idx < len(category_translations):
            return category_translations[idx]
    except ValueError:
        pass
    return en_category


def merge_plant_entry(lang_entry: dict, metadata: dict, category_translations: list[str] | None) -> dict | None:
    """Merge a language entry with its metadata. Skips _metadata entries (not needed in output)."""
    if "_metadata" in lang_entry:
        return None  # Skip _metadata block
    plant_id = lang_entry.get("id")
    if not plant_id:
        return None
    meta = metadata.get(plant_id)
    if not meta:
        return None
    merged = {**lang_entry}
    for key, value in meta.items():
        merged[key] = value
    # Translate category from header; add categoryIndex for sorting
    if "category" in meta:
        en_cat = meta["category"]
        if category_translations:
            merged["category"] = translate_category(en_cat, category_translations)
        idx = CATEGORY_ORDER.index(en_cat) if en_cat in CATEGORY_ORDER else len(CATEGORY_ORDER)
        merged["categoryIndex"] = idx
    return merged


def merge_locale(source_dir: Path, output_dir: Path, lang_filename: str, output_filename: str, metadata: dict) -> int:
    """Merge one locale file. Returns count of merged plant entries."""
    lang_path = source_dir / lang_filename
    if not lang_path.exists():
        print(f"  ⚠️  Skipping {lang_filename} (not found)")
        return 0
    with open(lang_path, "r", encoding="utf-8") as f:
        lang_data = json.load(f)
    # Extract category translations from _metadata.sorting.categories
    category_translations = None
    for entry in lang_data:
        if "_metadata" in entry:
            category_translations = entry["_metadata"].get("sorting", {}).get("categories")
            break
    merged = []
    count = 0
    for entry in lang_data:
        result = merge_plant_entry(entry, metadata, category_translations)
        if result is not None:
            merged.append(result)
            if "id" in result:
                count += 1
    output_path = output_dir / f"{output_filename}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"  ✅ {output_filename}.json ({count} plants)")
    return count


def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    source_dir = repo_root / "source"
    output_dir = repo_root / "dist"

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    metadata_path = source_dir / "common_plants_metadata.json"
    if not metadata_path.exists():
        print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("MERGING PLANT DATA (metadata + language)")
    print("=" * 60)
    print(f"\n📂 Source: {source_dir}")
    print(f"📂 Output: {output_dir}\n")

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"  Loaded metadata for {len(metadata)} plants\n")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("🔧 Merging...")
    total = 0
    for _locale, lang_filename, output_name in LOCALES:
        total += merge_locale(source_dir, output_dir, lang_filename, output_name, metadata)

    print(f"\n✅ Done. Merged {total} plant entries across {len(LOCALES)} locales.")
    print("=" * 60)


if __name__ == "__main__":
    main()
