#!/usr/bin/env python3
"""
Audit for potential duplicate or near-duplicate plant entries.

Checks for:
- Duplicate typeNames (same typeName across multiple entries in a locale)
- Genus vs species overlap (e.g., rhipsalis vs rhipsalis-baccifera)
- Similar typeNames (exact substring)
- Cultivar vs parent species redundancy

Usage: python3 scripts/audit_duplicates.py [--output overlap_report.json]
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

LANG_FILES = [
    ("common_plants_language_en.json", "en"),
    ("common_plants_language_es.json", "es"),
    ("common_plants_language_zh-Hans.json", "zh-Hans"),
]


def find_duplicate_typenames(data: list) -> dict[str, list[str]]:
    """Return {typeName: [id1, id2, ...]} for typeNames that appear more than once."""
    by_tn = defaultdict(list)
    for e in data:
        if isinstance(e, dict) and "_metadata" not in e and "typeName" in e:
            tn = (e.get("typeName") or "").strip()
            if tn:
                by_tn[tn].append(e.get("id", ""))
    return {k: v for k, v in by_tn.items() if len(v) > 1}


def main():
    parser = argparse.ArgumentParser(description="Audit for duplicate or near-duplicate plant entries")
    parser.add_argument("--output", "-o", metavar="FILE", help="Write JSON report to file")
    args = parser.parse_args()

    report = {
        "duplicateTypeNames": {},
        "genusSpeciesOverlaps": [],
        "knownPairs": [],
        "similarTypeNames": [],
    }

    # 0. Duplicate typeNames (exact same name across entries) in each locale
    print("Duplicate typeNames (same name across entries):")
    has_dup_tn = False
    for fname, locale in LANG_FILES:
        with open(SOURCE_DIR / fname, "r", encoding="utf-8") as f:
            data = json.load(f)
        dupes = find_duplicate_typenames(data)
        if dupes:
            has_dup_tn = True
            report["duplicateTypeNames"][locale] = dupes
            for tn, ids in sorted(dupes.items(), key=lambda x: -len(x[1])):
                print(f"  [{locale}] \"{tn}\" -> {ids}")
    if not has_dup_tn:
        print("  None")

    with open(SOURCE_DIR / "common_plants_language_en.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = [e for e in data if "_metadata" not in e and e.get("id")]

    # 1. Genus vs species: id contains another id as prefix
    print("Potential genus/species overlap:")
    overlaps = []
    for e in entries:
        pid = e["id"]
        for o in entries:
            if o["id"] == pid:
                continue
            if pid.startswith(o["id"] + "-") or o["id"].startswith(pid + "-"):
                pair = tuple(sorted([pid, o["id"]]))
                if pair not in overlaps:
                    overlaps.append(pair)

    for a, b in sorted(overlaps):
        ea = next(e for e in entries if e["id"] == a)
        eb = next(e for e in entries if e["id"] == b)
        line = f"  {a} ({ea.get('typeName')}) vs {b} ({eb.get('typeName')})"
        print(line)
        report["genusSpeciesOverlaps"].append({"id1": a, "id2": b, "typeName1": ea.get("typeName"), "typeName2": eb.get("typeName")})

    # 2. Known pairs to review
    print("\nKnown pairs to review:")
    known = [
        ("rhipsalis", "rhipsalis-baccifera"),
        ("philodendron-heartleaf", "philodendron-brasil"),
    ]
    for a, b in known:
        if any(e["id"] == a for e in entries) and any(e["id"] == b for e in entries):
            ea = next(e for e in entries if e["id"] == a)
            eb = next(e for e in entries if e["id"] == b)
            ex_a = ea.get("commonExamples", "")[:60]
            ex_b = eb.get("commonExamples", "")[:60]
            print(f"  {a}: {ex_a}...")
            print(f"  {b}: {ex_b}...")
            report["knownPairs"].append({"id1": a, "id2": b, "commonExamples1": ex_a, "commonExamples2": ex_b})

    # 3. Similar typeNames (simple check)
    print("\nSimilar typeNames (exact substring):")
    names = [(e["id"], e.get("typeName", "")) for e in entries]
    for i, (id1, n1) in enumerate(names):
        for id2, n2 in names[i + 1 :]:
            if n1 and n2 and (n1 in n2 or n2 in n1) and n1 != n2:
                line = f"  '{n1}' ({id1}) vs '{n2}' ({id2})"
                print(line)
                report["similarTypeNames"].append({"id1": id1, "id2": id2, "typeName1": n1, "typeName2": n2})

    print("\n✅ Audit complete. Review output for consolidation decisions.")

    if has_dup_tn:
        print("\nFix duplicate typeNames: python3 scripts/optimize_duplicate_typenames.py --dry-run then --fix")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report written to {out_path}")

    return 1 if has_dup_tn else 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
