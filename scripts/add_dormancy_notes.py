#!/usr/bin/env python3
"""
Add dormancy notes to careTips for plants with null winterInterval.

Explains why winter watering doesn't apply (dormant, deciduous, annual, etc.).
Run: python3 scripts/add_dormancy_notes.py [--dry-run]
"""

import json
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Dormancy note by plant type (suffix to add to careTips)
DORMANCY_SUFFIX = {
    "bulbs": " Bulbs go dormant after flowering; reduce watering when foliage dies back.",
    "deciduous_trees": " Deciduous; reduce or withhold watering when leaves drop in fall.",
    "deciduous_shrubs": " Deciduous varieties: reduce watering when dormant in winter.",
    "evergreen_outdoor": " Evergreen; reduce watering in winter when growth slows.",
    "annuals": " Annual; grown for one season; no winter watering needed.",
    "vegetables": " Seasonal crop; watering varies by growing zone and harvest timing.",
    "herbs": " Reduce watering in winter when growth slows.",
    "fruit_trees": " Reduce watering when dormant in winter.",
    "perennials": " Herbaceous perennials die back; reduce watering when dormant.",
    "ferns_deciduous": " Deciduous; reduce watering when fronds die back in fall.",
    "gloxinia": " Tuberous; goes dormant after flowering—reduce watering until new growth.",
    "aquatic": " Aquatic; winter care varies by Hardiness Zone.",
    "alpine": " Alpine; reduce watering when dormant; avoid winter wet.",
}

# Plant ID -> suffix key
PLANT_DORMANCY = {
    # Bulbs
    "allium": "bulbs",
    "crocus": "bulbs",
    "daffodils": "bulbs",
    "gladiolus": "bulbs",
    "hyacinth": "bulbs",
    "lilies": "bulbs",
    "tulips": "bulbs",
    # Deciduous trees
    "birch": "deciduous_trees",
    "deciduous-trees": "deciduous_trees",
    "dogwood": "deciduous_trees",
    "ginkgo": "deciduous_trees",
    "magnolia": "deciduous_trees",
    "maple": "deciduous_trees",
    "oak": "deciduous_trees",
    # Evergreen trees (reduce in winter)
    "citrus-trees": "evergreen_outdoor",
    "conifers": "evergreen_outdoor",
    "desert-trees": "evergreen_outdoor",
    "evergreen-trees": "evergreen_outdoor",
    "fruit-trees": "fruit_trees",
    # Shrubs
    "azaleas": "deciduous_shrubs",
    "forsythia": "deciduous_shrubs",
    "hydrangeas": "deciduous_shrubs",
    "lilac": "deciduous_shrubs",
    "rhododendrons": "deciduous_shrubs",
    "viburnum": "deciduous_shrubs",
    "boxwood": "evergreen_outdoor",
    "camellia": "evergreen_outdoor",
    "evergreen-shrubs": "evergreen_outdoor",
    "flowering-shrubs": "evergreen_outdoor",
    "juniper": "evergreen_outdoor",
    "lavender": "evergreen_outdoor",
    "osmanthus": "evergreen_outdoor",
    "rosemary": "evergreen_outdoor",
    "roses": "evergreen_outdoor",
    # Perennials
    "asters": "perennials",
    "black-eyed-susan": "perennials",
    "chrysanthemums": "perennials",
    "coneflower": "perennials",
    "daisies": "perennials",
    "daylilies": "perennials",
    "herbaceous-perennials": "perennials",
    "hostas": "perennials",
    "irises": "perennials",
    "peony": "perennials",
    "salvia": "perennials",
    "sedum-perennials": "perennials",
    "shade-perennials": "perennials",
    # Annuals
    "begonia": "annuals",
    "cool-season-annuals": "annuals",
    "cosmos": "annuals",
    "geraniums": "annuals",
    "impatiens": "annuals",
    "marigolds": "annuals",
    "nasturtium": "annuals",
    "petunias": "annuals",
    "sunflower": "annuals",
    "warm-season-annuals": "annuals",
    "zinnia": "annuals",
    # Vines
    "clematis": "deciduous_shrubs",
    "climbers": "evergreen_outdoor",
    "honeysuckle": "evergreen_outdoor",
    "ivy": "evergreen_outdoor",
    "morning-glory": "annuals",
    "wisteria": "deciduous_shrubs",
    # Groundcovers
    "creeping-phlox": "perennials",
    "grasses": "perennials",
    "groundcovers": "evergreen_outdoor",
    "lawn-turf": "evergreen_outdoor",
    "pachysandra": "evergreen_outdoor",
    "vinca": "evergreen_outdoor",
    # Vegetables
    "arugula": "vegetables",
    "bok-choy": "vegetables",
    "broccoli": "vegetables",
    "brussels-sprouts": "vegetables",
    "cabbage": "vegetables",
    "cauliflower": "vegetables",
    "celery": "vegetables",
    "choy-sum": "vegetables",
    "collard-greens": "vegetables",
    "gai-lan": "vegetables",
    "kale": "vegetables",
    "kohlrabi": "vegetables",
    "lettuce": "vegetables",
    "mustard-greens": "vegetables",
    "napa-cabbage": "vegetables",
    "spinach": "vegetables",
    "swiss-chard": "vegetables",
    "adzuki-bean": "vegetables",
    "beans": "vegetables",
    "bell-peppers": "vegetables",
    "butternut-squash": "vegetables",
    "cantaloupe": "vegetables",
    "corn": "vegetables",
    "cucumbers": "vegetables",
    "edamame": "vegetables",
    "eggplant": "vegetables",
    "green-beans": "vegetables",
    "habanero": "vegetables",
    "jalapeno": "vegetables",
    "mung-bean": "vegetables",
    "okra": "vegetables",
    "peas": "vegetables",
    "peppers": "vegetables",
    "pumpkin": "vegetables",
    "snap-peas": "vegetables",
    "snow-peas": "vegetables",
    "soybean": "vegetables",
    "squash": "vegetables",
    "tomatoes": "vegetables",
    "watermelon": "vegetables",
    "zucchini": "vegetables",
    "beets": "vegetables",
    "carrots": "vegetables",
    "daikon": "vegetables",
    "fennel": "vegetables",
    "onions-garlic": "vegetables",
    "parsnip": "vegetables",
    "potatoes": "vegetables",
    "radishes": "vegetables",
    "root-vegetables": "vegetables",
    "rutabaga": "vegetables",
    "sweet-potatoes": "vegetables",
    "turnips": "vegetables",
    # Fruits
    "apples": "fruit_trees",
    "apricot": "fruit_trees",
    "avocado": "evergreen_outdoor",
    "blackberries": "deciduous_shrubs",
    "blueberries": "deciduous_shrubs",
    "cherries": "fruit_trees",
    "cranberry": "evergreen_outdoor",
    "dragon-fruit": "evergreen_outdoor",
    "elderberry": "deciduous_shrubs",
    "fig": "deciduous_trees",
    "goji-berry": "deciduous_shrubs",
    "grapes": "deciduous_shrubs",
    "jujube": "deciduous_trees",
    "kumquat": "evergreen_outdoor",
    "longan": "evergreen_outdoor",
    "loquat": "evergreen_outdoor",
    "lychee": "evergreen_outdoor",
    "nectarine": "fruit_trees",
    "peach": "fruit_trees",
    "pear": "fruit_trees",
    "persimmon": "deciduous_trees",
    "plum": "fruit_trees",
    "pomegranate": "deciduous_trees",
    "pomelo": "evergreen_outdoor",
    "raspberries": "deciduous_shrubs",
    "strawberries": "vegetables",
    # Herbs
    "basil": "annuals",
    "chinese-chives": "perennials",
    "chives": "herbs",
    "cilantro": "annuals",
    "dill": "annuals",
    "ginger": "herbs",
    "lemongrass": "herbs",
    "mint": "herbs",
    "oregano": "herbs",
    "parsley": "herbs",
    "sage": "herbs",
    "thyme": "herbs",
    "turmeric": "herbs",
    # Aquatic
    "aquatic-plants": "aquatic",
    "bog-plants": "aquatic",
    "cattails": "aquatic",
    "indoor-aquatics": "aquatic",
    "lotus": "aquatic",
    "lotus-root": "vegetables",
    "pickerelweed": "aquatic",
    "water-iris": "aquatic",
    # Alpine
    "alpine-plants": "alpine",
    "aubrieta": "alpine",
    "edelweiss": "alpine",
    "gentian": "alpine",
    # Special
    "japanese-painted-fern": "ferns_deciduous",
    "gloxinia": "gloxinia",
    "asparagus": "perennials",
    "scallion": "vegetables",
    "chayote": "vegetables",
    "taro": "vegetables",
    "loofah": "vegetables",
}

# Locale-specific suffixes (EN = key, ES/ZH = value)
DORMANCY_ES = {
    "bulbs": " Los bulbos entran en latencia tras la floración; reducir el riego cuando el follaje se marchite.",
    "deciduous_trees": " Caducifolio; reducir o suspender el riego cuando caigan las hojas en otoño.",
    "deciduous_shrubs": " Variedades caducifolias: reducir el riego cuando estén latentes en invierno.",
    "evergreen_outdoor": " Perenne; reducir el riego en invierno cuando el crecimiento se ralentice.",
    "annuals": " Anual; cultivada una temporada; no requiere riego invernal.",
    "vegetables": " Cultivo estacional; el riego varía según la zona y el momento de cosecha.",
    "herbs": " Reducir el riego en invierno cuando el crecimiento se ralentice.",
    "fruit_trees": " Reducir el riego cuando estén latentes en invierno.",
    "perennials": " Las herbáceas perennes se marchitan; reducir el riego cuando estén latentes.",
    "ferns_deciduous": " Caducifolio; reducir el riego cuando las frondas se marchiten en otoño.",
    "gloxinia": " Tuberosa; entra en latencia tras la floración—reducir el riego hasta que haya nuevo crecimiento.",
    "aquatic": " Acuática; el cuidado invernal varía según la zona de rusticidad.",
    "alpine": " Alpina; reducir el riego cuando esté latente; evitar humedad invernal.",
}

DORMANCY_ZH = {
    "bulbs": " 球根开花后休眠；叶片枯萎时减少浇水。",
    "deciduous_trees": " 落叶树种；秋季落叶后减少或停止浇水。",
    "deciduous_shrubs": " 落叶品种：冬季休眠时减少浇水。",
    "evergreen_outdoor": " 常绿；冬季生长放缓时减少浇水。",
    "annuals": " 一年生；单季种植；冬季无需浇水。",
    "vegetables": " 季节性作物；浇水因种植区和收获时间而异。",
    "herbs": " 冬季生长放缓时减少浇水。",
    "fruit_trees": " 冬季休眠时减少浇水。",
    "perennials": " 多年生草本枯萎；休眠时减少浇水。",
    "ferns_deciduous": " 落叶；秋季叶片枯萎时减少浇水。",
    "gloxinia": " 块茎；开花后休眠—减少浇水直至新芽生长。",
    "aquatic": " 水生；冬季养护因耐寒区而异。",
    "alpine": " 高山植物；休眠时减少浇水；避免冬季积水。",
}


def add_dormancy_note(tips: str, suffix: str) -> str:
    """Add dormancy note if not already present."""
    if not tips or not suffix:
        return tips
    # Avoid duplicate
    if "dormant" in tips.lower() or "dormancy" in tips.lower() or "休眠" in tips or "latencia" in tips or "latente" in tips:
        return tips
    if "Deciduous" in tips or "落叶" in tips or "caducifolio" in tips:
        return tips
    if "Annual" in tips or "一年生" in tips or "Anual" in tips:
        return tips
    if "Seasonal crop" in tips or "季节性作物" in tips or "Cultivo estacional" in tips:
        return tips
    return tips.rstrip() + suffix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    meta = json.load(open(SOURCE_DIR / "common_plants_metadata.json"))
    null_ids = {pid for pid, v in meta.items() if isinstance(v, dict) and v.get("winterInterval") is None}

    locales = [
        ("common_plants_language_en.json", DORMANCY_SUFFIX),
        ("common_plants_language_es.json", DORMANCY_ES),
        ("common_plants_language_zh-Hans.json", DORMANCY_ZH),
    ]

    count = 0
    for filename, suffix_map in locales:
        path = SOURCE_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        modified = False
        for e in data:
            if "_metadata" in e:
                continue
            pid = e.get("id", "")
            if pid not in null_ids or pid not in PLANT_DORMANCY:
                continue
            key = PLANT_DORMANCY[pid]
            suffix = suffix_map.get(key, suffix_map.get("evergreen_outdoor", ""))
            if not suffix:
                continue
            tips = e.get("careTips", "")
            new_tips = add_dormancy_note(tips, suffix)
            if new_tips != tips:
                e["careTips"] = new_tips
                modified = True
                count += 1

        if modified and not args.dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added dormancy notes to {count} plant entries across 3 locales")
    if args.dry_run:
        print("(Dry run - no files modified)")
    return 0


if __name__ == "__main__":
    main()
