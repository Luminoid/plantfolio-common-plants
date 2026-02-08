#!/usr/bin/env python3
"""
Line-by-line audit of common_plants_metadata.json.

Ensures every plant has complete, valid metadata.

Usage:
    python3 scripts/audit_metadata_completeness.py
    python3 scripts/audit_metadata_completeness.py --verbose
    python3 scripts/audit_metadata_completeness.py --output report.txt

See docs/AUDIT_METADATA.md for spec (C1–C15, X1–X2).
"""

import json
import argparse
import sys
from pathlib import Path

# Reuse validate_json constants (Plantfolio app compatible)
VALID_LIGHT_PREFERENCES = {
    "brightIndirect", "deepShade", "gentleDirect", "lowIndirect",
    "mediumIndirect", "outdoorFullSun", "outdoorPartialSun", "outdoorShade",
    "strongDirect",
}
VALID_PLANT_TOXICITY = {"mildlyToxic", "nonToxic", "toxic", "unknown"}
VALID_HUMIDITY_PREFERENCES = {"high", "low", "medium", "veryHigh"}
VALID_SOIL_PH = {"acidic", "adaptable", "alkaline", "neutral"}
VALID_DRAINAGE = {
    "excellentDrainage", "moistureRetentive",
    "waterloggingTolerant", "wellDraining",
}
VALID_WATERING_METHOD = {
    "bottomWatering", "immersion", "misting", "topWatering", None
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

REQUIRED_FIELDS = [
    "springInterval", "summerInterval", "fallInterval", "winterInterval",
    "lightPreference", "humidityPreference", "temperaturePreference",
    "plantToxicity", "soilPhPreference", "drainagePreference", "wateringMethod",
    "plantLifeSpan", "category",
]


def check_plant(plant_id: str, entry: dict) -> list[tuple[str, str]]:
    """Run all checks for one plant. Returns list of (check_id, error_message)."""
    errors = []

    # C1: All required fields present
    missing = [f for f in REQUIRED_FIELDS if f not in entry]
    if missing:
        errors.append(("C1", f"missing fields: {', '.join(missing)}"))
        # If critical fields missing, skip further checks for structure
        if "category" not in entry:
            return errors

    # C2–C5: Intervals
    for field in ("springInterval", "summerInterval", "fallInterval", "winterInterval"):
        if field in entry:
            v = entry[field]
            if v is not None and (not isinstance(v, int) or v < 1 or v > 90):
                errors.append((field, f"invalid {field} {v!r} (expected 1–90 or null)"))

    # C6: lightPreference
    if "lightPreference" in entry and entry["lightPreference"] not in VALID_LIGHT_PREFERENCES:
        errors.append(("C6", f"invalid lightPreference '{entry['lightPreference']}'"))

    # C7: humidityPreference
    if "humidityPreference" in entry and entry["humidityPreference"] not in VALID_HUMIDITY_PREFERENCES:
        errors.append(("C7", f"invalid humidityPreference '{entry['humidityPreference']}'"))

    # C8: temperaturePreference
    if "temperaturePreference" in entry:
        tp = entry["temperaturePreference"]
        if not isinstance(tp, list) or len(tp) != 2:
            errors.append(("C8", f"invalid temperaturePreference {tp!r}"))
        elif tp[0] is not None and tp[1] is not None:
            if tp[0] > tp[1]:
                errors.append(("C8", "temperaturePreference min > max"))
            elif tp[0] < -10 or tp[1] > 45:
                errors.append(("C8", "temperaturePreference out of range (-10 to 45°C)"))

    # C9: plantToxicity
    if "plantToxicity" in entry and entry["plantToxicity"] not in VALID_PLANT_TOXICITY:
        errors.append(("C9", f"invalid plantToxicity '{entry['plantToxicity']}'"))

    # C10: soilPhPreference
    if "soilPhPreference" in entry and entry["soilPhPreference"] not in VALID_SOIL_PH:
        errors.append(("C10", f"invalid soilPhPreference '{entry['soilPhPreference']}'"))

    # C11: drainagePreference
    if "drainagePreference" in entry and entry["drainagePreference"] not in VALID_DRAINAGE:
        errors.append(("C11", f"invalid drainagePreference '{entry['drainagePreference']}'"))

    # C12: wateringMethod
    if "wateringMethod" in entry and entry["wateringMethod"] not in VALID_WATERING_METHOD:
        errors.append(("C12", f"invalid wateringMethod '{entry['wateringMethod']!r}'"))

    # C13: plantLifeSpan
    if "plantLifeSpan" in entry:
        pls = entry["plantLifeSpan"]
        if not isinstance(pls, list) or len(pls) != 2:
            errors.append(("C13", f"invalid plantLifeSpan {pls!r}"))
        elif pls[0] is not None and pls[0] < 0:
            errors.append(("C13", "plantLifeSpan min < 0"))

    # C14: category
    if "category" in entry and entry["category"] not in VALID_CATEGORIES:
        errors.append(("C14", f"invalid category '{entry['category']}'"))

    # C15: hardinessZones (optional)
    if "hardinessZones" in entry:
        hz = entry["hardinessZones"]
        if not isinstance(hz, list) or len(hz) != 2:
            errors.append(("C15", f"invalid hardinessZones {hz!r}"))
        elif any(not isinstance(z, int) or z < 1 or z > 11 for z in hz):
            errors.append(("C15", "hardinessZones must be int 1–11"))
        elif hz[0] > hz[1]:
            errors.append(("C15", "hardinessZones min > max"))

    return errors


def load_language_ids(path: Path) -> set[str]:
    """Extract plant IDs from a language file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {e["id"] for e in data if isinstance(e, dict) and "id" in e}
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def main():
    parser = argparse.ArgumentParser(
        description="Line-by-line audit of plant metadata completeness"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print every plant's check result (pass or fail)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write report to file",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    source_dir = repo_root / "source"
    meta_path = source_dir / "common_plants_metadata.json"

    # Load metadata
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Cannot load metadata: {e}", file=sys.stderr)
        sys.exit(1)

    lines = []
    failed_plants = []

    def out(s: str = ""):
        lines.append(s)
        print(s)

    out("METADATA LINE-BY-LINE AUDIT")
    out("=" * 50)
    out(f"Plants in metadata: {len(meta)}")
    out()

    # Per-plant checks
    for plant_id in sorted(meta.keys()):
        entry = meta[plant_id]
        if not isinstance(entry, dict):
            out(f"❌ {plant_id}: entry is not a dict")
            failed_plants.append((plant_id, [("structure", "not a dict")]))
            continue

        errors = check_plant(plant_id, entry)
        if errors:
            failed_plants.append((plant_id, errors))
            out(f"❌ {plant_id}:")
            for check_id, msg in errors:
                out(f"     [{check_id}] {msg}")
        elif args.verbose:
            out(f"✅ {plant_id}: pass")

    out()
    out("SUMMARY")
    out("-" * 50)
    out(f"Total plants: {len(meta)}")
    out(f"Passed: {len(meta) - len(failed_plants)}")
    out(f"Failed: {len(failed_plants)}")
    out()

    # Cross-reference: metadata ↔ language
    lang_path = source_dir / "common_plants_language_en.json"
    lang_ids = load_language_ids(lang_path)
    meta_ids = set(meta.keys())

    in_lang_not_meta = lang_ids - meta_ids
    in_meta_not_lang = meta_ids - lang_ids

    out("CROSS-REFERENCE (metadata ↔ language)")
    out("-" * 50)
    if in_lang_not_meta:
        out(f"⚠️  In language but NOT in metadata: {len(in_lang_not_meta)}")
        for pid in sorted(in_lang_not_meta)[:10]:
            out(f"    - {pid}")
        if len(in_lang_not_meta) > 10:
            out(f"    ... and {len(in_lang_not_meta) - 10} more")
    else:
        out("✅ All language plants have metadata")
    if in_meta_not_lang:
        out(f"⚠️  In metadata but NOT in language: {len(in_meta_not_lang)}")
        for pid in sorted(in_meta_not_lang)[:10]:
            out(f"    - {pid}")
        if len(in_meta_not_lang) > 10:
            out(f"    ... and {len(in_meta_not_lang) - 10} more")
    else:
        out("✅ All metadata plants have language entries")
    out()

    # Final status
    if failed_plants or in_lang_not_meta or in_meta_not_lang:
        out("❌ AUDIT FAILED")
        exit_code = 1
    else:
        out("✅ AUDIT PASSED — all plants have complete metadata")
        exit_code = 0

    # Write output file if requested
    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\nReport written to {out_path}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
