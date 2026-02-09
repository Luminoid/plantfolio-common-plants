#!/usr/bin/env python3
"""
Improve plant data by filling in missing optional metadata fields
based on plant knowledge and category patterns.

Reads source/common_plants_metadata.json and source/common_plants_language_en.json.
Modifies metadata in place. Run before merge.

Usage:
    python3 scripts/improve_plant_data.py
    python3 scripts/improve_plant_data.py --dry-run  # Show what would change without writing
"""

import json
import sys
from pathlib import Path


def load_json_file(file_path: Path):
    """Load JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return None


def infer_soil_ph(plant_id: str, category: str, description: str, care_tips: str) -> str:
    """Infer soil pH preference based on plant characteristics."""
    text = f"{description} {care_tips}".lower()
    plant_id_lower = plant_id.lower()
    category_lower = category.lower()

    # Acid-loving plants (carnivorous, ericaceous, berries)
    if any(
        word in text
        for word in ["acid", "ericaceous", "azalea", "rhododendron", "blueberry", "cranberry", "carnivorous"]
    ):
        return "acidic"
    if "carnivorous" in category_lower:
        return "acidic"
    if any(word in plant_id_lower for word in ["blueberry", "cranberry", "azalea", "rhododendron"]):
        return "acidic"

    # Alkaline-loving plants
    if any(word in text for word in ["alkaline", "limestone", "chalk"]):
        return "alkaline"

    # Cacti and succulents often prefer neutral
    if "cactus" in plant_id_lower or "cacti" in plant_id_lower:
        return "neutral"
    if "succulent" in category_lower:
        return "neutral"

    # Most plants are adaptable to a range of pH
    return "adaptable"


def infer_drainage(plant_id: str, category: str, description: str, care_tips: str) -> str | None:
    """Infer drainage preference based on plant characteristics."""
    text = f"{description} {care_tips}".lower()
    plant_id_lower = plant_id.lower()
    category_lower = category.lower()

    # Soilless growing methods - don't set drainage
    if "hydroponic" in plant_id_lower or "aeroponic" in plant_id_lower:
        return None

    # Plants that need excellent drainage (cacti, succulents, carnivorous)
    if any(
        word in text for word in ["excellent drainage", "drainage essential", "cactus mix", "succulent mix"]
    ):
        return "excellentDrainage"
    if "cactus" in plant_id_lower or "cacti" in plant_id_lower:
        return "excellentDrainage"
    if "succulent" in category_lower:
        return "excellentDrainage"
    if "carnivorous" in category_lower:
        return "excellentDrainage"

    # Aquatic/bog plants
    if "aquatic" in category_lower or "bog" in category_lower:
        return "waterloggingTolerant"

    # Plants that prefer moisture-retentive soil
    if any(
        word in text
        for word in ["moisture-retentive", "keep moist", "consistently moist", "never dry", "evenly moist"]
    ):
        return "moistureRetentive"

    # Most plants prefer well-draining
    if any(
        word in text
        for word in ["well-draining", "well-drained", "drainage", "moist but well-drained"]
    ):
        return "wellDraining"

    return "wellDraining"


def infer_lifespan(plant_id: str, category: str, description: str, care_tips: str) -> list:
    """Infer plant lifespan based on plant type."""
    text = f"{description} {care_tips}".lower()
    plant_id_lower = plant_id.lower()
    category_lower = category.lower()

    # Annuals - less than 1 year
    if "annual" in category_lower:
        return [None, 1]

    # Biennials - 2 years
    if "biennial" in text:
        return [2, 2]

    # Perennials - 3+ years
    if "perennial" in category_lower:
        return [3, None]

    # Trees - 20+ years
    if "tree" in category_lower:
        return [20, None]

    # Shrubs - 10+ years
    if "shrub" in category_lower:
        return [10, None]

    # Houseplants - typically 3+ years with proper care
    if "houseplant" in category_lower:
        if any(word in plant_id_lower for word in ["palm", "ficus", "dracaena", "yucca"]):
            return [5, None]
        return [3, None]

    # Vegetables - typically annuals or perennials
    if "vegetable" in category_lower:
        if "perennial" in text:
            return [3, None]
        return [None, 1]

    # Herbs - can be annual or perennial
    if "herb" in category_lower:
        if "perennial" in text:
            return [3, None]
        return [None, 1]

    # Bulbs - perennial, 3+ years
    if "bulb" in category_lower:
        return [3, None]

    # Specialty plants
    if "specialty" in category_lower:
        return [3, None]

    return [3, None]


def improve_metadata(
    metadata: dict, lang_lookup: dict[str, dict]
) -> dict[str, int]:
    """Improve metadata by filling in missing fields. Returns count of improvements per field."""
    improvements = {"soilPhPreference": 0, "drainagePreference": 0, "plantLifeSpan": 0}

    for plant_id, plant_meta in metadata.items():
        if plant_id == "_metadata":
            continue

        lang_entry = lang_lookup.get(plant_id, {})
        description = lang_entry.get("description", "")
        care_tips = lang_entry.get("careTips", "")
        category = plant_meta.get("category", "")

        # Fill in missing soilPhPreference
        if not plant_meta.get("soilPhPreference") or plant_meta.get("soilPhPreference") == "unknown":
            inferred = infer_soil_ph(plant_id, category, description, care_tips)
            if inferred:
                plant_meta["soilPhPreference"] = inferred
                improvements["soilPhPreference"] += 1

        # Fill in missing drainagePreference
        if not plant_meta.get("drainagePreference") or plant_meta.get("drainagePreference") == "unknown":
            inferred = infer_drainage(plant_id, category, description, care_tips)
            if inferred is not None:
                plant_meta["drainagePreference"] = inferred
                improvements["drainagePreference"] += 1

        # Fill in missing plantLifeSpan
        if not plant_meta.get("plantLifeSpan"):
            inferred = infer_lifespan(plant_id, category, description, care_tips)
            if inferred is not None:
                plant_meta["plantLifeSpan"] = inferred
                improvements["plantLifeSpan"] += 1

    return improvements


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Improve plant metadata by inferring missing fields")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    source_dir = repo_root / "source"
    metadata_file = source_dir / "common_plants_metadata.json"
    lang_file = source_dir / "common_plants_language_en.json"

    print("=" * 80)
    print("IMPROVING PLANT DATA")
    print("=" * 80)

    print("\n📂 Loading files...")
    metadata = load_json_file(metadata_file)
    lang_data = load_json_file(lang_file)

    if not metadata or not lang_data:
        print("Error: Could not load required files", file=sys.stderr)
        sys.exit(1)

    # Build id -> {description, careTips} lookup from language file
    lang_lookup = {}
    for entry in lang_data:
        if isinstance(entry, dict) and "_metadata" not in entry and entry.get("id"):
            lang_lookup[entry["id"]] = entry

    plant_entries = {k: v for k, v in metadata.items() if k != "_metadata" and isinstance(v, dict)}
    plant_count = len(plant_entries)
    print(f"  Loaded metadata for {plant_count} plants")
    print(f"  Loaded language for {len(lang_lookup)} plants")

    missing_before = {
        "soilPhPreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("soilPhPreference") or m.get("soilPhPreference") == "unknown"
        ),
        "drainagePreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("drainagePreference") or m.get("drainagePreference") == "unknown"
        ),
        "plantLifeSpan": sum(1 for m in plant_entries.values() if not m.get("plantLifeSpan")),
    }

    print(f"\n📊 Missing fields before improvement:")
    for field, count in missing_before.items():
        print(f"  {field}: {count} plants")

    print("\n🔧 Improving metadata...")
    improvements = improve_metadata(metadata, lang_lookup)

    print(f"\n✅ Improvements made:")
    for field, count in improvements.items():
        print(f"  {field}: {count} plants updated")

    missing_after = {
        "soilPhPreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("soilPhPreference") or m.get("soilPhPreference") == "unknown"
        ),
        "drainagePreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("drainagePreference") or m.get("drainagePreference") == "unknown"
        ),
        "plantLifeSpan": sum(1 for m in plant_entries.values() if not m.get("plantLifeSpan")),
    }

    print(f"\n📊 Missing fields after improvement:")
    for field, count in missing_after.items():
        reduction = missing_before[field] - count
        suffix = f" (Reduced by {reduction})" if reduction > 0 else ""
        print(f"  {field}: {count} plants{suffix}")

    if not args.dry_run and any(improvements.values()):
        print("\n💾 Saving improved metadata...")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {metadata_file}")
    elif args.dry_run:
        print("\n🏃 Dry run: no files written")

    print("\n" + "=" * 80)
    print("Improvement complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
