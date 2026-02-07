#!/usr/bin/env python3
"""
Improve generic care tips for plants with placeholder text.

Replaces "Water when top inch of soil is dry. Light and care vary by species. Fertilize during growing season."
with category-appropriate care tips following structure: watering → light → soil → fertilize.

Run: python3 scripts/improve_care_tips.py [--dry-run]
"""

import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

GENERIC_TIP = "Water when top inch of soil is dry. Light and care vary by species. Fertilize during growing season."

# Category-specific care tips (outdoor prairie/meadow, sprouts/microgreens)
PRAIRIE_TIP_EN = "Water when top 1-2 inches of soil is dry. Full sun preferred; drought tolerant once established. Well-draining soil. Fertilize lightly in spring if needed; many prairie natives prefer lean soil."
PRAIRIE_TIP_ES = "Regar cuando los primeros 2-5 cm de suelo estén secos. Sol pleno preferido; tolerante a la sequía una vez establecida. Suelo bien drenado. Fertilizar ligeramente en primavera si es necesario; muchas nativas de pradera prefieren suelo pobre."
PRAIRIE_TIP_ZH = "当表层2-5厘米土壤干燥时浇水。偏好全日照；一旦扎根后耐旱。排水良好的土壤。春季可轻施肥料；许多草原原生植物偏好贫瘠土壤。"

SPROUTS_TIP_EN = "Keep growing medium moist but not waterlogged. Bright indirect light. Harvest when first true leaves appear (typically 7-14 days). No fertilizer needed for typical growth cycle."
SPROUTS_TIP_ES = "Mantener el medio de cultivo húmedo pero no encharcado. Luz indirecta brillante. Cosechar cuando aparezcan las primeras hojas verdaderas (típicamente 7-14 días). No se necesita fertilizante para el ciclo de crecimiento típico."
SPROUTS_TIP_ZH = "保持培养基湿润但不积水。明亮间接光。当真叶出现时采收（通常7-14天）。典型生长周期无需施肥。"

# Plant IDs by category (from metadata)
def load_metadata():
    with open(SOURCE_DIR / "common_plants_metadata.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_generic_ids(lang_path):
    """Find plant IDs with generic care tips."""
    with open(lang_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ids = []
    for e in data:
        if "_metadata" in e:
            continue
        if e.get("careTips") == GENERIC_TIP:
            ids.append(e["id"])
    return ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    meta = load_metadata()

    # Categorize generic-tip plants
    prairie_cats = {"Outdoor - Groundcovers & Grasses", "Specialty - Alpine"}
    sprouts_cats = {"Sprouts & Microgreens", "Farm & Field Crops"}

    # Prairie/meadow native IDs (from category or name patterns)
    prairie_ids = set()
    sprout_ids = set()

    for pid, m in meta.items():
        if not isinstance(m, dict):
            continue
        cat = m.get("category", "")
        if cat in prairie_cats:
            prairie_ids.add(pid)
        if cat in sprouts_cats:
            sprout_ids.add(pid)

    # Refine: prairie plants from the generic list (grass, prairie, aster, etc.)
    with open(SOURCE_DIR / "common_plants_language_en.json", "r", encoding="utf-8") as f:
        en_data = json.load(f)

    generic_ids = set()
    for e in en_data:
        if "_metadata" in e:
            continue
        if e.get("careTips") == GENERIC_TIP:
            generic_ids.add(e["id"])

    # Apply sprouts tip first (priority over prairie)
    sprout_keywords = ["sprouts", "microgreens", "shoots", "wheatgrass"]
    sprout_targets = generic_ids & sprout_ids
    for pid in generic_ids:
        if any(kw in pid for kw in sprout_keywords):
            sprout_targets.add(pid)

    # Apply prairie tip to outdoor grasses/wildflowers (exclude sprouts)
    prairie_keywords = ["bluestem", "grama", "prairie", "aster", "goldenrod", "milkweed", "coneflower", "muhly", "bergamot", "mullein", "clover", "indigo", "blazing", "joe-pye", "ironweed", "rattlesnake", "maximilian", "cranesbill", "scabious", "viper", "bugloss", "cornflower", "culvers", "leadplant", "compass", "dock", "switchgrass", "indian-grass", "dropseed", "meadow-sage", "oxeye-daisy", "field-scabious", "showy-goldenrod", "fountain-grass", "blue-grama", "side-oats-grama"]
    prairie_targets = (generic_ids & prairie_ids) | {p for p in generic_ids if any(kw in p for kw in prairie_keywords)}
    prairie_targets -= sprout_targets  # Sprouts take priority

    updates = []  # (file, id, old, new)
    locales = [
        ("common_plants_language_en.json", "en", PRAIRIE_TIP_EN, SPROUTS_TIP_EN),
        ("common_plants_language_es.json", "es", PRAIRIE_TIP_ES, SPROUTS_TIP_ES),
        ("common_plants_language_zh-Hans.json", "zh", PRAIRIE_TIP_ZH, SPROUTS_TIP_ZH),
    ]

    for filename, locale, prairie_tip, sprout_tip in locales:
        path = SOURCE_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        modified = False
        for e in data:
            if "_metadata" in e or e.get("careTips") != GENERIC_TIP:
                continue
            pid = e.get("id", "")
            if pid in prairie_targets:
                e["careTips"] = prairie_tip
                modified = True
                updates.append((filename, pid, "prairie"))
            elif pid in sprout_targets:
                e["careTips"] = sprout_tip
                modified = True
                updates.append((filename, pid, "sprouts"))

        if modified and not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    prairie_count = len(set(u[1] for u in updates if u[2] == "prairie"))
    sprout_count = len(set(u[1] for u in updates if u[2] == "sprouts"))
    print(f"Would update: {prairie_count} prairie/meadow plants, {sprout_count} sprouts/microgreens")
    if args.dry_run:
        print("Dry run - no files modified.")
    else:
        print(f"Updated {len(set((u[0], u[1]) for u in updates))} entries across 3 locale files.")
    return 0


if __name__ == "__main__":
    main()
