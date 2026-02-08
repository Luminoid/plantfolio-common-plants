#!/usr/bin/env python3
"""
List plants with plantToxicity: unknown, grouped by category.

Outputs id + commonExamples for ASPCA search. Useful for toxicity research per
docs/AUDIT.md section 6.

Usage:
    python3 scripts/audit_toxicity_unknown.py
    python3 scripts/audit_toxicity_unknown.py --category "Outdoor - Perennials"
    python3 scripts/audit_toxicity_unknown.py --output toxicity_unknown.json
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"


def main():
    parser = argparse.ArgumentParser(
        description="List plants with unknown toxicity by category for ASPCA search"
    )
    parser.add_argument(
        "--category", "-c",
        metavar="NAME",
        help="Filter to a specific category",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write JSON report to file",
    )
    args = parser.parse_args()

    # Load metadata
    with open(SOURCE_DIR / "common_plants_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Load language for commonExamples
    with open(SOURCE_DIR / "common_plants_language_en.json", "r", encoding="utf-8") as f:
        lang_data = json.load(f)

    lang_by_id = {
        e["id"]: e.get("commonExamples", "")
        for e in lang_data
        if isinstance(e, dict) and "id" in e and "_metadata" not in str(e.get("id", ""))
    }

    # Find unknown plants
    unknown = []
    for plant_id, entry in meta.items():
        if plant_id == "_metadata" or entry.get("plantToxicity") != "unknown":
            continue
        category = entry.get("category", "")
        if args.category and category != args.category:
            continue
        common_examples = lang_by_id.get(plant_id, "")
        unknown.append({
            "id": plant_id,
            "category": category,
            "commonExamples": common_examples,
        })

    # Group by category for output
    by_category = {}
    for item in unknown:
        cat = item["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append({
            "id": item["id"],
            "commonExamples": item["commonExamples"],
        })

    # Sort categories, then ids within each
    for cat in by_category:
        by_category[cat] = sorted(by_category[cat], key=lambda x: x["id"])

    report = {
        "totalUnknown": len(unknown),
        "byCategory": dict(sorted(by_category.items())),
    }

    # Print human-readable summary
    print("Plants with plantToxicity: unknown")
    print("=" * 50)
    print(f"Total: {len(unknown)}")
    print()
    for cat in sorted(by_category.keys()):
        items = by_category[cat]
        print(f"\n{cat} ({len(items)})")
        print("-" * 40)
        for item in items:
            ex = (item["commonExamples"] or "(no commonExamples)")[:70]
            if len(item["commonExamples"] or "") > 70:
                ex += "..."
            print(f"  {item['id']}")
            print(f"    → {ex}")
    print()
    print("Reference: https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants")
    print("See docs/AUDIT.md section 6 for workflow.")

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nReport written to {out_path}")


if __name__ == "__main__":
    main()
