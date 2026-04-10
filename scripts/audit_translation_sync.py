#!/usr/bin/env python3
"""
Audit that all four locales (EN, ES, ZH-Hans, ZH-Hant) have complete entries for each plant.

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
    zh_hans_path = SOURCE_DIR / "common_plants_language_zh-Hans.json"
    zh_hant_path = SOURCE_DIR / "common_plants_language_zh-Hant.json"

    en = json.load(en_path.open(encoding="utf-8"))
    es = json.load(es_path.open(encoding="utf-8"))
    zh_hans = json.load(zh_hans_path.open(encoding="utf-8"))
    zh_hant = json.load(zh_hant_path.open(encoding="utf-8"))

    en_entries = [e for e in en if "_metadata" not in e and e.get("id")]
    es_entries = [e for e in es if "_metadata" not in e and e.get("id")]
    zh_hans_entries = [e for e in zh_hans if "_metadata" not in e and e.get("id")]
    zh_hant_entries = [e for e in zh_hant if "_metadata" not in e and e.get("id")]

    en_ids = {e["id"] for e in en_entries}
    es_ids = {e["id"] for e in es_entries}
    zh_hans_ids = {e["id"] for e in zh_hans_entries}
    zh_hant_ids = {e["id"] for e in zh_hant_entries}

    en_by_id = {e["id"]: e for e in en_entries}
    es_by_id = {e["id"]: e for e in es_entries}
    zh_hans_by_id = {e["id"]: e for e in zh_hans_entries}
    zh_hant_by_id = {e["id"]: e for e in zh_hant_entries}

    ok = True

    # Check ID coverage
    missing_es = en_ids - es_ids
    missing_zh_hans = en_ids - zh_hans_ids
    missing_zh_hant = en_ids - zh_hant_ids
    if missing_es:
        print(f"❌ Missing in ES: {missing_es}")
        ok = False
    if missing_zh_hans:
        print(f"❌ Missing in ZH-Hans: {missing_zh_hans}")
        ok = False
    if missing_zh_hant:
        print(f"❌ Missing in ZH-Hant: {missing_zh_hant}")
        ok = False
    if not missing_es and not missing_zh_hans and not missing_zh_hant:
        print(f"✅ All {len(en_ids)} plants present in EN, ES, ZH-Hans, ZH-Hant")

    # Check for empty critical fields
    empty_issues = []
    for pid in en_ids:
        for loc, d in [("en", en_by_id), ("es", es_by_id), ("zh-Hans", zh_hans_by_id), ("zh-Hant", zh_hant_by_id)]:
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
        zh_hans_same = [(pid, en_by_id[pid].get("typeName", "")) for pid in en_ids if pid in zh_hans_by_id and zh_hans_by_id[pid].get("typeName") == en_by_id[pid].get("typeName")]
        zh_hant_same = [(pid, en_by_id[pid].get("typeName", "")) for pid in en_ids if pid in zh_hant_by_id and zh_hant_by_id[pid].get("typeName") == en_by_id[pid].get("typeName")]
        print(f"\nTypeNames matching EN (possible untranslated): ES {len(es_same)}, ZH-Hans {len(zh_hans_same)}, ZH-Hant {len(zh_hant_same)}")
        if es_same:
            print("  ES sample:", es_same[:5])
        if zh_hans_same:
            print("  ZH-Hans sample:", zh_hans_same[:5])
        if zh_hant_same:
            print("  ZH-Hant sample:", zh_hant_same[:5])

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
