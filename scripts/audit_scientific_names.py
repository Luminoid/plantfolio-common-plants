#!/usr/bin/env python3
"""
Audit commonExamples for scientific name correctness per plant-expert standards.

Checks for:
- Outdated genus names (Sansevieria, Senecio where Curio accepted, etc.)
- Missing hybrid × symbol (Alocasia amazonica → Alocasia × amazonica)
- Genus/species formatting issues

Usage: python3 scripts/audit_scientific_names.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Known reclassifications: old_pattern -> (suggestion, note)
REPORT_PATTERNS = [
    (r"Sansevieria ", "Use Dracaena (syn. Sansevieria) - Asparagaceae merger"),
    (r"S\. trifasciata", "OK if after Dracaena trifasciata; else use D. trifasciata"),
    (r"S\. cylindrica", "Use Dracaena angolensis (syn. Sansevieria cylindrica)"),
    (r"Alocasia amazonica[^×]", "Use Alocasia × amazonica for hybrid"),
    (r"Senecio rowleyanus(?![^,]*(?:syn\.|Curio))", "Consider Curio rowleyanus (syn. Senecio rowleyanus)"),
    (r"Senecio radicans(?![^,]*(?:syn\.|Curio))", "Consider Curio radicans (syn. Senecio radicans)"),
]

# Simple substring checks (case-sensitive)
OLD_NAMES = {
    "Sansevieria trifasciata": "Dracaena trifasciata (syn. Sansevieria trifasciata)",
    "Sansevieria cylindrica": "Dracaena angolensis (syn. Sansevieria cylindrica)",
    "Senecio rowleyanus": "Curio rowleyanus (syn. Senecio rowleyanus)",
    "Senecio radicans": "Curio radicans (syn. Senecio radicans)",
    "Senecio × peregrinus": "Curio × peregrinus (syn. Senecio × peregrinus)",
    "Senecio serpens": "Curio repens (syn. Senecio serpens)",
    "Senecio mandraliscae": "Curio talinoides subsp. mandraliscae (syn. Senecio mandraliscae)",
    "Alocasia amazonica ": "Alocasia × amazonica ",
    "Dracaena cylindrica": "Dracaena angolensis (syn. Sansevieria cylindrica)",
}


def audit_file(path: Path, locale: str) -> list[dict]:
    """Audit one language file. Returns list of findings."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    findings = []
    for entry in data:
        if "_metadata" in entry:
            continue
        pid = entry.get("id", "")
        examples = entry.get("commonExamples", "")
        if not examples:
            continue

        for old, suggested in OLD_NAMES.items():
            if old not in examples:
                continue
            # Skip if already correct form present
            correct_form = suggested.split("(")[0].strip()  # e.g. "Curio rowleyanus"
            if correct_form in examples or "× amazonica" in examples:
                continue
            # Skip if in synonym context
            if "syn." in examples and old in examples:
                idx = examples.find(old)
                if idx > 0 and "syn." in examples[max(0, idx - 50) : idx + len(old) + 20]:
                    continue
            findings.append({
                "id": pid,
                "typeName": entry.get("typeName", ""),
                "locale": locale,
                "issue": f"Contains '{old.strip()}'",
                "suggestion": suggested,
            })

    return findings


def main():
    files = [
        (SOURCE_DIR / "common_plants_language_en.json", "en"),
        (SOURCE_DIR / "common_plants_language_es.json", "es"),
        (SOURCE_DIR / "common_plants_language_zh-Hans.json", "zh-Hans"),
    ]

    all_findings = []
    for path, locale in files:
        if path.exists():
            all_findings.extend(audit_file(path, locale))

    # Dedupe by id+issue
    seen = set()
    unique = []
    for f in all_findings:
        key = (f["id"], f["issue"])
        if key not in seen:
            seen.add(key)
            unique.append(f)

    if not unique:
        print("✅ No scientific name issues found.")
        return 0

    print(f"⚠️  {len(unique)} potential scientific name issue(s):\n")
    for f in unique:
        print(f"  {f['id']} ({f['locale']}): {f['issue']}")
        print(f"    → {f['suggestion']}\n")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
