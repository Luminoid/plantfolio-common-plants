#!/usr/bin/env python3
"""
Validate generated JSON files in dist/.

Checks JSON syntax and optionally structure of common_plants files.
Run after merge to verify built output.

Usage:
    python3 scripts/validate_json.py [FILE...]
    python3 scripts/validate_json.py --check-structure
    python3 scripts/validate_json.py --check-schema [SOURCE_METADATA]
"""

import json
import argparse
import sys
from pathlib import Path

# Valid enum values (Plantfolio app compatible)
VALID_LIGHT_PREFERENCES = {
    "brightIndirect", "deepShade", "gentleDirect", "lowIndirect",
    "mediumIndirect", "outdoorFullSun", "outdoorPartialSun", "outdoorShade",
    "strongDirect",
}
VALID_PLANT_TOXICITY = {
    "mildlyToxic", "nonToxic", "toxic", "unknown",
}
VALID_HUMIDITY_PREFERENCES = {"high", "low", "medium", "veryHigh"}
VALID_SOIL_PH = {"acidic", "adaptable", "alkaline", "neutral"}
VALID_DRAINAGE = {
    "excellentDrainage", "moistureRetentive",
    "waterloggingTolerant", "wellDraining",
}
VALID_WATERING_METHOD = {
    "bottomWatering", "immersion", "misting", "topWatering",
    None,  # aquatic/carnivorous plants
}
VALID_CATEGORIES = {
    "Bulbs", "Farm & Field Crops", "Fruits & Berries", "Herbs",
    "Houseplants - Aroids", "Houseplants - Cacti", "Houseplants - Ferns",
    "Houseplants - Flowering", "Houseplants - Low Maintenance",
    "Houseplants - Palms", "Houseplants - Prayer Plants",
    "Houseplants - Specialty", "Houseplants - Succulents",
    "Houseplants - Vines & Trailing",
    "Outdoor - Annuals", "Outdoor - Groundcovers & Grasses",
    "Outdoor - Perennials", "Outdoor - Shrubs", "Outdoor - Trees",
    "Outdoor - Vines & Climbers",
    "Specialty - Alpine", "Specialty - Aquatic & Bog",
    "Specialty - Carnivorous", "Specialty - Epiphytes & Moss",
    "Sprouts & Microgreens", "Vegetables - Fruiting",
    "Vegetables - Leafy Greens", "Vegetables - Root & Bulb",
}


def validate_json_file(file_path):
    """Validate a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, str(e)
    except FileNotFoundError:
        return False, None, "File not found"
    except Exception as e:
        return False, None, str(e)


def validate_metadata_schema(metadata_path):
    """Validate source metadata against full schema (enums, required fields, ranges)."""
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return False, [str(e)]

    errors = []
    for plant_id, entry in meta.items():
        if not isinstance(entry, dict):
            continue

        # Enums
        if "lightPreference" in entry and entry["lightPreference"] not in VALID_LIGHT_PREFERENCES:
            errors.append(f"{plant_id}: invalid lightPreference '{entry['lightPreference']}'")
        if "plantToxicity" in entry and entry["plantToxicity"] not in VALID_PLANT_TOXICITY:
            errors.append(f"{plant_id}: invalid plantToxicity '{entry['plantToxicity']}'")
        if "humidityPreference" in entry and entry["humidityPreference"] not in VALID_HUMIDITY_PREFERENCES:
            errors.append(f"{plant_id}: invalid humidityPreference '{entry['humidityPreference']}'")
        if "soilPhPreference" in entry and entry["soilPhPreference"] not in VALID_SOIL_PH:
            errors.append(f"{plant_id}: invalid soilPhPreference '{entry['soilPhPreference']}'")
        if "drainagePreference" in entry and entry["drainagePreference"] not in VALID_DRAINAGE:
            errors.append(f"{plant_id}: invalid drainagePreference '{entry['drainagePreference']}'")
        if "wateringMethod" in entry and entry["wateringMethod"] not in VALID_WATERING_METHOD:
            errors.append(f"{plant_id}: invalid wateringMethod '{entry['wateringMethod']}'")

        # Required: category
        if "category" not in entry:
            errors.append(f"{plant_id}: missing category")
        elif entry["category"] not in VALID_CATEGORIES:
            errors.append(f"{plant_id}: invalid category '{entry['category']}'")

        # Intervals: int in 1-90 or null
        for field in ("springInterval", "summerInterval", "fallInterval", "winterInterval"):
            if field in entry:
                v = entry[field]
                if v is not None and (not isinstance(v, int) or v < 1 or v > 90):
                    errors.append(f"{plant_id}: invalid {field} {v!r} (expected 1-90 or null)")

        # temperaturePreference: [min, max] where min <= max, -10 to 45
        if "temperaturePreference" in entry:
            tp = entry["temperaturePreference"]
            if not isinstance(tp, list) or len(tp) != 2:
                errors.append(f"{plant_id}: invalid temperaturePreference {tp!r}")
            elif tp[0] is not None and tp[1] is not None:
                if tp[0] > tp[1]:
                    errors.append(f"{plant_id}: temperaturePreference min > max")
                elif tp[0] < -10 or tp[1] > 45:
                    errors.append(f"{plant_id}: temperaturePreference out of range (-10 to 45°C)")

        # plantLifeSpan: [min, max] or [min, null], min >= 0
        if "plantLifeSpan" in entry:
            pls = entry["plantLifeSpan"]
            if not isinstance(pls, list) or len(pls) != 2:
                errors.append(f"{plant_id}: invalid plantLifeSpan {pls!r}")
            elif pls[0] is not None and pls[0] < 0:
                errors.append(f"{plant_id}: plantLifeSpan min < 0")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Validate generated JSON files in dist/")
    parser.add_argument("files", nargs="*", help="JSON files (default: dist/common_plants*.json)")
    parser.add_argument("--check-structure", action="store_true", help="Check common_plants structure")
    parser.add_argument("--check-schema", metavar="METADATA", nargs="?", const="source/common_plants_metadata.json",
                        help="Validate metadata schema (lightPreference, plantToxicity, category enums)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    dist_dir = repo_root / "dist"
    source_dir = repo_root / "source"

    # Schema validation for metadata
    if args.check_schema is not None:
        meta_path = Path(args.check_schema) if args.check_schema else source_dir / "common_plants_metadata.json"
        if not meta_path.is_absolute():
            meta_path = repo_root / meta_path
        valid, errs = validate_metadata_schema(meta_path)
        if valid:
            print(f"✅ Schema valid: {meta_path}")
        else:
            print(f"❌ Schema errors in {meta_path}:")
            for e in errs[:20]:
                print(f"   {e}")
            if len(errs) > 20:
                print(f"   ... and {len(errs) - 20} more")
            sys.exit(1)
        if not args.files and not args.check_structure:
            sys.exit(0)

    if not args.files:
        default_files = [
            dist_dir / "common_plants.json",
            dist_dir / "common_plants_es.json",
            dist_dir / "common_plants_zh-Hans.json",
        ]
        files_to_check = [str(f) for f in default_files if f.exists()]
    else:
        files_to_check = args.files

    if not files_to_check:
        print("No JSON files found to validate")
        sys.exit(1)

    all_valid = True
    for file_path in files_to_check:
        is_valid, data, error = validate_json_file(file_path)
        if is_valid:
            print(f"✅ {file_path}: Valid JSON")
            if args.check_structure and "common_plants" in file_path:
                if isinstance(data, list) and len(data) > 0:
                    required_keys = ["id", "typeName", "description", "commonExamples"]
                    first_entry = data[0]
                    missing_keys = [k for k in required_keys if k not in first_entry]
                    if missing_keys:
                        print(f"  ⚠️  Missing required keys: {', '.join(missing_keys)}")
                    else:
                        print(f"  ✅ Structure valid ({len(data)} entries)")
                else:
                    print(f"  ⚠️  Expected a non-empty array")
        else:
            print(f"❌ {file_path}: {error}")
            all_valid = False

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
