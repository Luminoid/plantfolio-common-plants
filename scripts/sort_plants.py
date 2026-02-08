#!/usr/bin/env python3
"""
Sort plants in metadata and language files: by category, then alphabetically by id.

Usage: python3 scripts/sort_plants.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Category order (must match merge_plant_data.py and language _metadata.sorting.categories)
CATEGORY_ORDER = [
    "Houseplants - Low Maintenance",
    "Houseplants - Aroids",
    "Houseplants - Ferns",
    "Houseplants - Palms",
    "Houseplants - Succulents",
    "Houseplants - Cacti",
    "Houseplants - Flowering",
    "Houseplants - Prayer Plants",
    "Houseplants - Vines & Trailing",
    "Houseplants - Specialty",
    "Outdoor - Trees",
    "Outdoor - Shrubs",
    "Outdoor - Perennials",
    "Outdoor - Annuals",
    "Outdoor - Vines & Climbers",
    "Outdoor - Groundcovers & Grasses",
    "Vegetables - Leafy Greens",
    "Vegetables - Fruiting",
    "Vegetables - Root & Bulb",
    "Fruits & Berries",
    "Herbs",
    "Farm & Field Crops",
    "Sprouts & Microgreens",
    "Bulbs",
    "Specialty - Aquatic & Bog",
    "Specialty - Carnivorous",
    "Specialty - Epiphytes & Moss",
    "Specialty - Alpine",
]


def sort_key(plant_id: str, category: str) -> tuple:
    """Sort by category index, then alphabetically by id."""
    try:
        cat_idx = CATEGORY_ORDER.index(category)
    except ValueError:
        cat_idx = len(CATEGORY_ORDER)
    return (cat_idx, plant_id.lower())


def main():
    meta_path = SOURCE_DIR / "common_plants_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Build sorted order: (category_index, id) -> sort
    sorted_ids = sorted(
        meta.keys(),
        key=lambda pid: sort_key(pid, meta[pid].get("category", ""))
    )

    # Rebuild metadata dict in sorted order (Python 3.7+ preserves insertion order)
    sorted_meta = {pid: meta[pid] for pid in sorted_ids}

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(sorted_meta, f, indent=2, ensure_ascii=False)

    print(f"  ✅ common_plants_metadata.json: {len(sorted_meta)} plants sorted by category, then id")

    # Build id -> index for lookup
    id_to_order = {pid: i for i, pid in enumerate(sorted_ids)}

    # Sort language files
    for filename in ["common_plants_language_en.json", "common_plants_language_zh-Hans.json", "common_plants_language_es.json"]:
        path = SOURCE_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Separate metadata (first element with _metadata) from plant entries
        metadata_block = None
        plant_entries = []
        for entry in data:
            if "_metadata" in entry:
                metadata_block = entry
            elif entry.get("id"):
                plant_entries.append(entry)

        # Sort plant entries by our id order; unknown ids go at end
        def entry_order(e):
            pid = e.get("id", "")
            return id_to_order.get(pid, len(sorted_ids))

        plant_entries.sort(key=entry_order)

        # Rebuild: metadata first, then sorted plants
        result = []
        if metadata_block is not None:
            result.append(metadata_block)
        result.extend(plant_entries)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"  ✅ {filename}: {len(plant_entries)} plants reordered")

    print("\nDone. Run: python3 scripts/validate_json.py --check-schema")


if __name__ == "__main__":
    main()
