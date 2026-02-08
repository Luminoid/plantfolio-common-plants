#!/usr/bin/env python3
"""
Audit that all three locales (EN, ES, ZH) have complete entries for each plant.

Checks:
- Every plant in EN exists in ES and ZH
- No empty typeName, description, or careTips in any locale
- Optionally: flag typeNames that are identical to EN (possible untranslated)

Usage:
    python3 scripts/audit_translation_sync.py
    python3 scripts/audit_translation_sync.py --check-typeNames
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "source"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit translation sync across locales")
    parser.add_argument(
        "--check-typeNames",
        action="store_true",
        help="Report typeNames in ES/ZH that match EN (possible untranslated)",
    )
    args = parser.parse_args()

    en_path = SOURCE_DIR / "common_plants_language_en.json"
    es_path = SOURCE_DIR / "common_plants_language_es.json"
    zh_path = SOURCE_DIR / "common_plants_language_zh-Hans.json"

    en = json.load(en_path.open(encoding="utf-8"))
    es = json.load(es_path.open(encoding="utf-8"))
    zh = json.load(zh_path.open(encoding="utf-8"))

    en_entries = [e for e in en if "_metadata" not in e and e.get("id")]
    es_entries = [e for e in es if "_metadata" not in e and e.get("id")]
    zh_entries = [e for e in zh if "_metadata" not in e and e.get("id")]

    en_ids = {e["id"] for e in en_entries}
    es_ids = {e["id"] for e in es_entries}
    zh_ids = {e["id"] for e in zh_entries}

    en_by_id = {e["id"]: e for e in en_entries}
    es_by_id = {e["id"]: e for e in es_entries}
    zh_by_id = {e["id"]: e for e in zh_entries}

    ok = True

    # Check ID coverage
    missing_es = en_ids - es_ids
    missing_zh = en_ids - zh_ids
    if missing_es:
        print(f"❌ Missing in ES: {missing_es}")
        ok = False
    if missing_zh:
        print(f"❌ Missing in ZH: {missing_zh}")
        ok = False
    if not missing_es and not missing_zh:
        print(f"✅ All {len(en_ids)} plants present in EN, ES, ZH")

    # Check for empty critical fields
    empty_issues = []
    for pid in en_ids:
        for loc, d in [("en", en_by_id), ("es", es_by_id), ("zh", zh_by_id)]:
            if pid not in d:
                continue
            e = d[pid]
            if not (e.get("typeName") or "").strip():
                empty_issues.append((pid, loc, "typeName"))
            if not (e.get("description") or "").strip():
                empty_issues.append((pid, loc, "description"))
            if not (e.get("careTips") or "").strip():
                empty_issues.append((pid, loc, "careTips"))

    if empty_issues:
        print(f"❌ Empty fields: {len(empty_issues)}")
        for pid, loc, field in empty_issues[:10]:
            print(f"   {pid} ({loc}): {field}")
        ok = False
    else:
        print("✅ No empty typeName, description, or careTips")

    # Optional: typeNames identical to EN
    if args.check_typeNames:
        es_same = [(pid, en_by_id[pid].get("typeName", "")) for pid in en_ids if pid in es_by_id and es_by_id[pid].get("typeName") == en_by_id[pid].get("typeName")]
        zh_same = [(pid, en_by_id[pid].get("typeName", "")) for pid in en_ids if pid in zh_by_id and zh_by_id[pid].get("typeName") == en_by_id[pid].get("typeName")]
        print(f"\nTypeNames matching EN (possible untranslated): ES {len(es_same)}, ZH {len(zh_same)}")
        if es_same:
            print("  ES sample:", es_same[:5])
        if zh_same:
            print("  ZH sample:", zh_same[:5])

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
