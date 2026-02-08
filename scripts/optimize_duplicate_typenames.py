#!/usr/bin/env python3
"""
Find and fix duplicate typeNames within each language file.

When two or more plant entries share the same typeName, differentiate them using
aliases from commonExamples (e.g., "Florist's Cyclamen" vs "Cyclamen").

Usage:
    python3 scripts/optimize_duplicate_typenames.py --dry-run   # Preview changes
    python3 scripts/optimize_duplicate_typenames.py --fix      # Apply changes
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Per-locale overrides: plant_id -> new typeName (when duplicate exists)
# Format: (locale_suffix, {id: new_typeName})
# Locale suffixes: "" for en, "_es" for es, "_zh" for zh-Hans
OPTIMIZATIONS = {
    "en": {
        "neanthe-bella-palm": "Neanthe Bella Palm",
        "sedum-morganianum": "Donkey's Tail",
        "peperomia-prostrata": "Turtle Vine",
        "cyclamen-bulb": "Florist's Cyclamen",
        "sinningia": "Florist's Gloxinia",
        "clover-red": "Meadow Clover",
        "panicum": "Panicum",
        "mung-bean-field": "Green Gram",
        "soybean-field": "Soya Bean",
        # string-of-dolphins vs senecio-peregrinus: keep both distinct
        "senecio-peregrinus": "Dolphin Plant",
    },
    "es": {
        "neanthe-bella-palm": "Palmera Neanthe Bella",
        "sedum-morganianum": "Cola de Burro Sedum",
        "peperomia-prostrata": "Enredadera de Tortuga",
        "cyclamen-bulb": "Ciclamen de florista",
        "sinningia": "Gloxinia de florista",
        "clover-red": "Trébol púrpura",
        "panicum": "Panicum",
        "mung-bean-field": "Gramo verde",
        "soybean-field": "Soja (legumbre)",
        "senecio-peregrinus": "Planta delfín",
        # ES-specific (differentiate duplicate typeNames)
        "kalanchoe-blossfeldiana": "Kalanchoe Blossfeldiana",
        "blanket-flower": "Gaillardia común",
        "catmint": "Nepeta cataria",
        "irises": "Lirios (iridáceas)",
        "sage": "Salvia común",
        "switchgrass-prairie": "Panicum virgatum",
        "ground-cherry": "Tomatillo silvestre",
        "tomatillo": "Tomatillo (Physalis)",
        "pumpkin": "Calabaza común",
        "peppers": "Pimientos (género)",
    },
    "zh-Hans": {
        "neanthe-bella-palm": "贝拉袖珍椰",
        "philodendron-heartleaf": "心叶喜林芋攀爬型",
        "staghorn-fern": "二歧鹿角蕨",
        "cycads": "苏铁类",
        "sedum-morganianum": "墨西哥景天",
        "stonecrop": "景天属",
        "sempervivum-alpine": "高山长生草",
        "senecio-peregrinus": "海豚弦月",
        "prickly-pear-fruit": "仙人掌果实",
        "goldfish-plant": "金鱼吊兰",
        "cyclamen-bulb": "花店仙客来",
        "sinningia": "大岩桐花店型",
        "ivy": "常春藤属",
        "scindapsus-exotica": "银斑葛锦",
        "clover-red": "红三叶草",
        "sage": "鼠尾草属",
        "zinnia-elegans": "百日草",
        "panicum": "黍属",
        "mustard-field": "芥菜(大田)",
        "ground-cherry": "酸浆果",
        "luffa": "丝瓜(棱角)",
        "mung-bean-field": "绿豆(大田)",
        "squash": "南瓜属",
        "soybean-field": "大豆(大田)",
        "gooseberry": "鹅莓",
        "pawpaw": "番木瓜果",
        "floating-heart": "荇菜",
        "pitcher-plant": "猪笼草属",
        "tillandsia-xerographica": "空气凤梨(霸王)",
        # Additional ZH duplicates (philodendron-heartleaf keeps 心叶喜林芋攀爬型)
        "philodendron-hederaceum-scandal": "丑闻喜林芋",
        "maranta-leuconeura": "孔雀竹芋(绿叶)",
        "maranta-prayer-plant": "斑叶祈祷竹芋",
    },
}


def find_duplicate_typenames(data: list) -> dict[str, list[dict]]:
    """Return {typeName: [entries]} for typeNames that appear more than once."""
    by_tn = defaultdict(list)
    for e in data:
        if isinstance(e, dict) and "_metadata" not in e and "typeName" in e:
            tn = (e.get("typeName") or "").strip()
            if tn:
                by_tn[tn].append(e)
    return {k: v for k, v in by_tn.items() if len(v) > 1}


def get_optimization_for_locale(locale: str) -> dict[str, str]:
    if locale == "en":
        return OPTIMIZATIONS["en"]
    if locale == "es":
        return {**OPTIMIZATIONS["en"], **OPTIMIZATIONS["es"]}
    if locale == "zh-Hans":
        return {**OPTIMIZATIONS["en"], **OPTIMIZATIONS["zh-Hans"]}
    return {}


def apply_optimizations(path: Path, locale: str, dry_run: bool) -> tuple[int, list[str]]:
    """Apply optimizations; return (count of changes, list of change descriptions)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dupes = find_duplicate_typenames(data)
    overrides = get_optimization_for_locale(locale)
    changes = []
    changed_count = 0

    for tn, entries in dupes.items():
        for e in entries:
            pid = e.get("id", "")
            new_tn = overrides.get(pid)
            if new_tn and (e.get("typeName") or "").strip() == tn:
                if not dry_run:
                    e["typeName"] = new_tn
                changes.append(f"  {pid}: \"{tn}\" → \"{new_tn}\"")
                changed_count += 1

    if changed_count > 0 and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return changed_count, changes


def main():
    parser = argparse.ArgumentParser(description="Optimize duplicate typeNames in language files")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--fix", action="store_true", help="Apply changes to source files")
    args = parser.parse_args()

    if not args.dry_run and not args.fix:
        parser.error("Use --dry-run to preview or --fix to apply")

    files = [
        (SOURCE_DIR / "common_plants_language_en.json", "en"),
        (SOURCE_DIR / "common_plants_language_es.json", "es"),
        (SOURCE_DIR / "common_plants_language_zh-Hans.json", "zh-Hans"),
    ]

    total = 0
    for path, locale in files:
        dupes = find_duplicate_typenames(json.load(open(path, encoding="utf-8")))
        count, changes = apply_optimizations(path, locale, dry_run=args.dry_run)
        total += count

        if changes:
            print(f"\n{path.name} ({locale}):")
            for c in changes:
                print(c)

    mode = "Would apply" if args.dry_run else "Applied"
    print(f"\n{mode} {total} typeName optimization(s).")


if __name__ == "__main__":
    main()
