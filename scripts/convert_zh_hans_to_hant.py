#!/usr/bin/env python3
"""
Convert Simplified Chinese (zh-Hans) plant data to Traditional Chinese (zh-Hant).

Uses OpenCC's s2twp profile (Simplified → Traditional with Taiwan phrases) on every
text field, including the Chinese common names inside commonExamples, then applies a
small post-map for terms where Taiwan usage differs from OpenCC's output.
Scientific names, cultivar names, and ids are ASCII and pass through unchanged.

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

# Taiwan-usage terms OpenCC leaves in mainland form (applied after conversion)
POST_MAP = [
    ("澳大利亞", "澳洲"), ("印度尼西亞", "印尼"), ("臺灣", "台灣"), ("索羅門", "所羅門"),
    ("沃勒米", "瓦勒邁"), ("獅子山", "塞拉利昂"), ("義大利", "意大利"),
    ("土豆", "馬鈴薯"), ("菠蘿", "鳳梨"), ("獼猴桃", "奇異果"), ("捲心菜", "高麗菜"), ("西蘭花", "青花菜"),
    ("郁金香", "鬱金香"), ("面包", "麵包"), ("幹燥", "乾燥"),
]


def convert_text(text: str) -> str:
    text = cc.convert(text)
    for simplified, taiwan in POST_MAP:
        text = text.replace(simplified, taiwan)
    return text


def convert_value(value):
    """Recursively convert string values from Simplified to Traditional Chinese."""
    if isinstance(value, str):
        return convert_text(value)
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
            converted.append({"_metadata": {key: (val if key in ("version", "totalPlants") else convert_value(val)) for key, val in meta.items()}})
        else:
            converted.append({key: (val if key == "id" else convert_value(val)) for key, val in entry.items()})

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
        f.write("\n")

    plant_count = sum(1 for e in converted if "_metadata" not in e and e.get("id"))
    print(f"✅ Converted {plant_count} plants from zh-Hans → zh-Hant")
    print(f"   Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
