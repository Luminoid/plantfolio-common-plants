#!/usr/bin/env python3
"""
Convert Simplified Chinese (zh-Hans) plant data to Traditional Chinese (zh-Hant).

Uses OpenCC s2twp profile (Simplified → Traditional with Taiwan idioms/phrases).

Usage: python3 scripts/convert_zh_hans_to_hant.py
"""

import json
from pathlib import Path

from opencc import OpenCC

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

INPUT_FILE = SOURCE_DIR / "common_plants_language_zh-Hans.json"
OUTPUT_FILE = SOURCE_DIR / "common_plants_language_zh-Hant.json"

# s2twp = Simplified to Traditional (Taiwan standard + phrases)
cc = OpenCC("s2twp")


def convert_value(value):
    """Recursively convert string values from Simplified to Traditional Chinese."""
    if isinstance(value, str):
        return cc.convert(value)
    if isinstance(value, list):
        return [convert_value(item) for item in value]
    if isinstance(value, dict):
        return {key: convert_value(val) for key, val in value.items()}
    return value


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    converted = []
    for entry in data:
        if "_metadata" in entry:
            # Convert metadata (categories, sorting method, etc.) but keep version/counts
            meta = entry["_metadata"]
            new_meta = {}
            for key, val in meta.items():
                if key in ("version", "totalPlants"):
                    new_meta[key] = val
                else:
                    new_meta[key] = convert_value(val)
            converted.append({"_metadata": new_meta})
        else:
            # Convert plant entry — keep id and commonExamples unchanged
            new_entry = {}
            for key, val in entry.items():
                if key in ("id", "commonExamples"):
                    new_entry[key] = val  # IDs and scientific names are locale-agnostic
                else:
                    new_entry[key] = convert_value(val)
            converted.append(new_entry)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)

    plant_count = sum(1 for e in converted if "_metadata" not in e and e.get("id"))
    print(f"✅ Converted {plant_count} plants from zh-Hans → zh-Hant")
    print(f"   Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
