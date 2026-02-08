#!/usr/bin/env python3
"""
Audit alignment between plantToxicity metadata and care tips phrasing.

Per docs/AUDIT.md: care tips should mention toxicity for toxic/mildlyToxic plants.
nonToxic plants may optionally mention "Non-toxic to pets."
unknown plants: no requirement.

Usage:
    python3 scripts/audit_toxicity_care_tips.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Phrases that indicate toxicity in care tips (case-insensitive)
TOXIC_PHRASES = ["toxic to pets", "tóxico para mascotas", "对宠物有毒"]
MILDLY_TOXIC_PHRASES = ["mildly toxic", "ligeramente tóxico", "轻微有毒", "gi upset", "malestar gastrointestinal", "肠胃不适"]
NON_TOXIC_PHRASES = ["non-toxic", "non-toxic to pets", "not toxic", "no tóxico", "无毒"]


def has_phrase(text: str, phrases: list[str]) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(p.lower() in lower for p in phrases)


def main():
    with open(SOURCE_DIR / "common_plants_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    with open(SOURCE_DIR / "common_plants_language_en.json", "r", encoding="utf-8") as f:
        lang = json.load(f)

    lang_by_id = {e["id"]: e for e in lang if isinstance(e, dict) and "id" in e and e["id"] != "_metadata"}

    missing_toxic = []
    missing_mildly = []
    mismatch = []

    for plant_id, entry in meta.items():
        if plant_id == "_metadata" or not isinstance(entry, dict):
            continue
        toxicity = entry.get("plantToxicity")
        if toxicity not in ("toxic", "mildlyToxic", "nonToxic"):
            continue

        lang_entry = lang_by_id.get(plant_id, {})
        care_tips = (lang_entry.get("careTips") or "").strip()

        if toxicity == "toxic":
            if not has_phrase(care_tips, TOXIC_PHRASES):
                missing_toxic.append((plant_id, lang_entry.get("typeName", plant_id)))
        elif toxicity == "mildlyToxic":
            if not (has_phrase(care_tips, MILDLY_TOXIC_PHRASES) or has_phrase(care_tips, TOXIC_PHRASES)):
                missing_mildly.append((plant_id, lang_entry.get("typeName", plant_id)))
        elif toxicity == "nonToxic":
            # Exclude "Non-toxic to pets" — that correctly describes nonToxic
            has_nontoxic = has_phrase(care_tips, NON_TOXIC_PHRASES)
            has_toxic_claim = has_phrase(care_tips, TOXIC_PHRASES) or has_phrase(care_tips, MILDLY_TOXIC_PHRASES)
            if has_toxic_claim and not has_nontoxic:
                mismatch.append((plant_id, lang_entry.get("typeName", plant_id), "metadata=nonToxic but careTips mention toxicity"))

    if missing_toxic:
        print("=== toxic plants missing toxicity mention in care tips ===\n")
        for pid, name in missing_toxic[:20]:
            print(f"  {pid}: {name}")
        if len(missing_toxic) > 20:
            print(f"  ... and {len(missing_toxic) - 20} more")
        print()

    if missing_mildly:
        print("=== mildlyToxic plants missing toxicity mention in care tips ===\n")
        for pid, name in missing_mildly[:20]:
            print(f"  {pid}: {name}")
        if len(missing_mildly) > 20:
            print(f"  ... and {len(missing_mildly) - 20} more")
        print()

    if mismatch:
        print("=== Mismatch: nonToxic metadata but care tips mention toxicity ===\n")
        for pid, name, msg in mismatch:
            print(f"  {pid}: {name} — {msg}")
        print()

    if missing_toxic or missing_mildly or mismatch:
        print("Run with --fix not supported; update care tips manually.")
        return 1

    print("✅ All toxic/mildlyToxic plants have aligned care tips.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
