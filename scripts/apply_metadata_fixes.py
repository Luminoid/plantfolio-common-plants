#!/usr/bin/env python3
"""
Apply metadata fixes for steps N, O, P, Q from NEXT_STEPS.md.

N: 38 outdoor plants brightIndirect → outdoorFullSun (or outdoorPartialSun)
O: bonsai, lemon-cypress outdoorPartialSun → brightIndirect
P: Rot-prone succulents wellDraining → excellentDrainage
Q: plantToxicity unknown → known (ASPCA/vet sources)
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
META_PATH = REPO_ROOT / "source" / "common_plants_metadata.json"

# N: Outdoor plants to change from brightIndirect
OUTDOOR_BRIGHT_TO_FULLSUN = {
    "prairie-dropseed", "little-bluestem", "big-bluestem", "indian-grass",
    "switchgrass-prairie", "purple-cone-prairie", "compass-plant", "prairie-dock",
    "culvers-root", "leadplant", "new-england-aster", "smooth-aster",
    "wild-bergamot", "pink-muhly", "blue-grama", "side-oats-grama",
    "european-cornflower", "meadow-cranesbill", "oxeye-daisy", "meadow-sage",
    "field-scabious", "great-mullein", "common-viper", "red-clover",
    "wild-indigo", "false-indigo", "blazing-star", "goldenrod",
    "maximilian-sunflower", "showy-goldenrod", "common-milkweed",
    "swamp-milkweed", "yellow-coneflower", "pale-purple-coneflower",
}
# Joe-pye-weed and ironweed prefer moist areas, can tolerate partial shade
OUTDOOR_BRIGHT_TO_PARTIALSUN = {
    "joe-pye-weed", "ironweed", "sweet-joe-pye", "rattlesnake-master",
}

# O: Houseplants with outdoor light → brightIndirect
HOUSEPLANT_OUTDOOR_TO_BRIGHT = {"bonsai", "lemon-cypress"}

# P: Succulents/cacti to upgrade to excellentDrainage (rot-prone)
SUCCULENTS_EXCELLENT_DRAINAGE = {
    "lithops", "echeveria", "haworthia", "sedum-morganianum",
    "string-of-pearls", "string-of-bananas",
}

# Q: plantToxicity from ASPCA/vet sources (only plants with unknown → known)
TOXICITY_UPDATES = {
    # Non-toxic (ASPCA)
    "alyssum": "nonToxic",
    # Mildly toxic (mouth irritation, GI upset)
    "begonia": "mildlyToxic",
    "peony": "mildlyToxic",
    "salvia": "mildlyToxic",
    "clematis": "mildlyToxic",
    "honeysuckle": "mildlyToxic",
    # Toxic (veterinary attention recommended)
    "morning-glory": "toxic",
    "foxglove": "toxic",
    "castor-bean": "toxic",
    "lupine": "toxic",
    "hops": "toxic",
    "sweet-potato-vine": "toxic",
}


def main():
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    changes = []

    for plant_id, entry in meta.items():
        if not isinstance(entry, dict):
            continue

        # N: Outdoor brightIndirect → outdoorFullSun or outdoorPartialSun
        if plant_id in OUTDOOR_BRIGHT_TO_FULLSUN and entry.get("lightPreference") == "brightIndirect":
            entry["lightPreference"] = "outdoorFullSun"
            changes.append((plant_id, "lightPreference", "brightIndirect → outdoorFullSun"))
        elif plant_id in OUTDOOR_BRIGHT_TO_PARTIALSUN and entry.get("lightPreference") == "brightIndirect":
            entry["lightPreference"] = "outdoorPartialSun"
            changes.append((plant_id, "lightPreference", "brightIndirect → outdoorPartialSun"))

        # O: Bonsai, lemon-cypress outdoorPartialSun → brightIndirect
        if plant_id in HOUSEPLANT_OUTDOOR_TO_BRIGHT and entry.get("lightPreference") == "outdoorPartialSun":
            entry["lightPreference"] = "brightIndirect"
            changes.append((plant_id, "lightPreference", "outdoorPartialSun → brightIndirect"))

        # P: Succulents wellDraining → excellentDrainage
        if plant_id in SUCCULENTS_EXCELLENT_DRAINAGE and entry.get("drainagePreference") == "wellDraining":
            entry["drainagePreference"] = "excellentDrainage"
            changes.append((plant_id, "drainagePreference", "wellDraining → excellentDrainage"))

        # Q: plantToxicity unknown → known (only if current is unknown and we have update)
        if plant_id in TOXICITY_UPDATES and entry.get("plantToxicity") == "unknown":
            new_tox = TOXICITY_UPDATES[plant_id]
            entry["plantToxicity"] = new_tox
            changes.append((plant_id, "plantToxicity", f"unknown → {new_tox}"))

    # Filter Q updates: only apply if plant exists and has unknown
    applied = 0
    for plant_id, field, msg in changes:
        if plant_id in meta:
            applied += 1
            print(f"  {plant_id}: {msg}")

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"\nApplied {len(changes)} changes to {META_PATH}")


if __name__ == "__main__":
    main()
