#!/usr/bin/env python3
"""
Reorganize plant categories and remove duplicates.

Edit REMOVE_IDS and CATEGORY_CHANGES in this file before running.
Applied removals are already in the data; add new IDs when duplicates are found.

Usage: python3 scripts/reorganize_plants.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# 1. IDs to REMOVE (true duplicates or incorrect)
REMOVE_IDS = [
    "golden-pothos-office",       # = golden-pothos
    "marble-queen-office",       # = marble-queen-pothos
    "philodendron-xanadu-office",  # = philodendron-xanadu
    "kentia-palm-office",        # = kentia-palm
    "areca-palm-office",         # = areca-palm
    "bromeliad-office",          # = bromeliads
    "schefflera-arboricola",     # = schefflera-dwarf
    "butterfly-weed-native",     # = butterfly-weed
    "yarrow-meadow",             # = yarrow
    "satin-pothos",              # = scindapsus (Scindapsus pictus)
    "silver-philodendron",       # = scindapsus (Scindapsus pictus 'Argyraeus')
    "nephthytis",                # = arrowhead-plant (Syngonium, old name)
]

# 2. Category reassignments (id -> new_category)
CATEGORY_CHANGES = {
    "rubber-plant-burgundy": "Houseplants - Specialty",  # cultivar - with rubber plant
    "croton-mammy": "Houseplants - Specialty",  # cultivar - with croton
}

# 3. New category order (reorganized for clarity)
NEW_CATEGORY_ORDER = [
    # Houseplants
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
    # Outdoor
    "Outdoor - Trees",
    "Outdoor - Shrubs",
    "Outdoor - Perennials",
    "Outdoor - Annuals",
    "Outdoor - Vines & Climbers",
    "Outdoor - Groundcovers & Grasses",
    # Edibles
    "Vegetables - Leafy Greens",
    "Vegetables - Fruiting",
    "Vegetables - Root & Bulb",
    "Fruits & Berries",
    "Herbs",
    # Farm & micro
    "Farm & Field Crops",
    "Sprouts & Microgreens",
    # Bulbs & Specialty
    "Bulbs",
    "Specialty - Aquatic & Bog",
    "Specialty - Carnivorous",
    "Specialty - Epiphytes & Moss",
    "Specialty - Alpine",
]

# 4. Category renames (old -> new) - optional, for clarity
# Using same names for now to avoid breaking translations


def main():
    # Load metadata
    meta_path = SOURCE_DIR / "common_plants_metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Remove duplicates
    removed = 0
    for pid in REMOVE_IDS:
        if pid in meta:
            del meta[pid]
            removed += 1
            print(f"  Removed: {pid}")

    # Apply category changes
    for pid, new_cat in CATEGORY_CHANGES.items():
        if pid in meta and new_cat in NEW_CATEGORY_ORDER:
            meta[pid]["category"] = new_cat
            print(f"  Reassigned: {pid} -> {new_cat}")

    # Save metadata
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata: removed {removed}, total={len(meta)}")

    # Load and update language files
    new_total = len(meta)
    for filename in ["common_plants_language_en.json", "common_plants_language_zh-Hans.json", "common_plants_language_es.json"]:
        path = SOURCE_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Remove entries for REMOVE_IDS
        kept = [e for e in data if e.get("id") not in REMOVE_IDS]

        # Update totalPlants
        for e in kept:
            if "_metadata" in e:
                e["_metadata"]["totalPlants"] = new_total
                break

        with open(path, "w", encoding="utf-8") as f:
            json.dump(kept, f, indent=2, ensure_ascii=False)

        print(f"  {filename}: removed {len(data) - len(kept)}, totalPlants={new_total}")

    print("\nDone. Run: python3 scripts/merge_plant_data.py && python3 scripts/validate_json.py --check-schema --check-structure")


if __name__ == "__main__":
    main()
