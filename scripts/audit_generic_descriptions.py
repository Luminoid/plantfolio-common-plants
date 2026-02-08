#!/usr/bin/env python3
"""
Flag plants with generic descriptions that should be replaced with species-specific text.

Generic patterns from expert audit (Feb 2025). See docs/AUDIT_CHECKLIST_TEMPLATE.md.

Usage:
    python3 scripts/audit_generic_descriptions.py
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Generic description patterns to flag (exact or substring)
# Keys: en, es, zh (zh matches zh-Hans)
GENERIC_PATTERNS = [
    ("en", "Common plant for gardens, farms, or indoor spaces."),
    ("en", "Edible plant for kitchen gardens."),
    ("en", "Specialty plant for gardens or collections."),
    ("es", "Planta especial para jardines o colecciones"),
    ("zh", "园艺或收藏用特色植物"),
]


def load_lang_file(path: Path) -> list[dict]:
    """Load language file, skip _metadata entries."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [e for e in data if "_metadata" not in e]


def main() -> int:
    locale_files = [
        ("en", SOURCE_DIR / "common_plants_language_en.json"),
        ("es", SOURCE_DIR / "common_plants_language_es.json"),
        ("zh-Hans", SOURCE_DIR / "common_plants_language_zh-Hans.json"),
    ]

    found = []
    for locale, path in locale_files:
        if not path.exists():
            continue
        entries = load_lang_file(path)
        locale_key = "zh" if locale == "zh-Hans" else locale
        for e in entries:
            desc = e.get("description") or ""
            for pattern_locale, pattern in GENERIC_PATTERNS:
                if pattern_locale == locale_key and pattern in desc:
                    found.append((e["id"], locale, desc[:60] + "..." if len(desc) > 60 else desc))

    if not found:
        print("✅ No generic descriptions found.")
        return 0

    print(f"⚠️  {len(found)} plant(s) with generic descriptions:\n")
    for plant_id, locale, desc in found:
        print(f"  {plant_id} ({locale}): {desc}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
