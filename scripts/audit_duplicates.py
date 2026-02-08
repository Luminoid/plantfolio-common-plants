#!/usr/bin/env python3
"""
Audit for potential duplicate or near-duplicate plant entries.

Checks for:
- Genus vs species overlap (e.g., rhipsalis vs rhipsalis-baccifera)
- Similar typeNames
- Cultivar vs parent species redundancy

Usage: python3 scripts/audit_duplicates.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"


def normalize(s: str) -> str:
    """Normalize for comparison."""
    return "".join(c for c in s.lower() if c.isalnum())


def main():
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
        print(f"  {a} ({ea.get('typeName')}) vs {b} ({eb.get('typeName')})")

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

    # 3. Similar typeNames (simple check)
    print("\nSimilar typeNames (exact substring):")
    names = [(e["id"], e.get("typeName", "")) for e in entries]
    for i, (id1, n1) in enumerate(names):
        for id2, n2 in names[i + 1 :]:
            if n1 and n2 and (n1 in n2 or n2 in n1) and n1 != n2:
                print(f"  '{n1}' ({id1}) vs '{n2}' ({id2})")

    print("\n✅ Audit complete. Review output for consolidation decisions.")


if __name__ == "__main__":
    main()
