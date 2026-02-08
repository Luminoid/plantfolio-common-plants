#!/usr/bin/env python3
"""
Add "also known as" (formal name or aliases) to plant descriptions from commonExamples.

Per docs/DATASET.md and docs/AUDIT.md:
- Extract from commonExamples format: Scientific name (alias1, alias2)
- If typeName matches an alias → add formal name; else → add aliases
- Only use first/primary segment (species must match current plant)
- Skip plants with no parenthetical content

Usage:
    python3 scripts/add_common_alias_to_description.py          # Update all language files
    python3 scripts/add_common_alias_to_description.py --dry-run  # Preview changes only
"""

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

# Per-language "also known as" phrases (no leading space; used at start of description)
ALIAS_PHRASES = {
    "en": "Also known as: ",
    "es": "También conocida como: ",
    "zh-Hans": "也称：",
}
ALIAS_SUFFIX = {
    "en": ".",
    "es": ".",
    "zh-Hans": "。",
}

# Generic terms to exclude from alias list
EXCLUDE_GENERIC = {"variety", "speckled variety", "杂交", "various", "var.", "subsp.", "syn.", "hybrid"}


def build_species_to_plant_map(source_dir: Path) -> dict[str, str]:
    """
    Build mapping: first-segment formal name -> plant_id.
    Prefer specific plants (fewer segments) over category plants (many segments).
    """
    en_path = source_dir / "common_plants_language_en.json"
    if not en_path.exists():
        return {}
    with open(en_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    candidates: list[tuple[str, str, int]] = []  # (formal, plant_id, num_segments)
    for entry in data:
        if "_metadata" in entry:
            continue
        plant_id = entry.get("id")
        if not plant_id:
            continue
        segments = parse_common_examples(entry.get("commonExamples") or "")
        if segments:
            formal = segments[0][0].strip()
            if formal:
                candidates.append((formal, plant_id, len(segments)))
    # Prefer plants with fewer segments (specific > category)
    candidates.sort(key=lambda x: (x[0], x[2]))
    mapping = {}
    for formal, plant_id, _ in candidates:
        if formal not in mapping:
            mapping[formal] = plant_id
    return mapping


def parse_common_examples(common_examples: str) -> list[tuple[str, list[str]]]:
    """
    Parse commonExamples for segments: (formal_name, [alias1, alias2, ...]).
    Returns list of (species, aliases) tuples.
    """
    if not common_examples or not isinstance(common_examples, str):
        return []

    # Match: Scientific name (alias1, alias2) -- content before ( and inside (...)
    pattern = re.compile(r"([^(]+)\s*\(([^)]+)\)")
    segments = []
    for m in pattern.finditer(common_examples):
        formal = m.group(1).strip()
        paren_content = m.group(2).strip()

        # Handle synonym prefix: syn. X; alias1, alias2 → use only alias part after ;
        if ";" in paren_content:
            parts = paren_content.split(";")
            paren_content = parts[-1].strip()

        aliases = [a.strip() for a in paren_content.split(",")]
        aliases = [
            a for a in aliases
            if a and a.lower() not in EXCLUDE_GENERIC and not a.lower().startswith("syn.")
        ]

        if formal and aliases:
            segments.append((formal, aliases))

    return segments


def get_value_to_add(
    type_name: str, segments: list[tuple[str, list[str]]], use_first_only: bool = True
) -> tuple[str | None, list[str]]:
    """
    Determine what to add: formal name or aliases.
    Returns (formal_name_if_used, alias_list_if_used) - one will be non-empty.
    """
    if not segments:
        return (None, [])

    # Use first segment only (primary species for this plant)
    if use_first_only:
        segments = segments[:1]

    all_formals = []
    all_aliases = []
    for formal, aliases in segments:
        all_formals.append(formal)
        all_aliases.extend(aliases)

    type_lower = type_name.lower()
    aliases_lower = [a.lower() for a in all_aliases]

    # If typeName matches an alias, use formal name(s)
    if type_lower in aliases_lower:
        return (", ".join(all_formals), [])

    # Otherwise use aliases, excluding typeName and near-duplicates
    def is_redundant(alias: str) -> bool:
        al = alias.lower()
        if al == type_lower:
            return True
        # Exclude if alias is substring of typeName (e.g. "aaa" in "aaas") or vice versa
        if al in type_lower or type_lower in al:
            return True
        return False

    filtered = [a for a in all_aliases if not is_redundant(a)]
    return (None, filtered)


def build_alias_string(value: str, locale: str) -> str:
    """Build the 'Also known as: X.' string (for prepending)."""
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    suffix = ALIAS_SUFFIX.get(locale, ALIAS_SUFFIX["en"])
    return f"{phrase}{value}{suffix}"


def strip_existing_alias(description: str, locale: str) -> str:
    """Remove existing 'Also known as' block from description (end or start)."""
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    suffix = ALIAS_SUFFIX.get(locale, ALIAS_SUFFIX["en"])
    # Match: phrase + value + suffix (value has no period/。)
    if suffix == "。":
        pattern = re.compile(re.escape(phrase) + r"([^。]*)" + re.escape(suffix))
    else:
        pattern = re.compile(re.escape(phrase) + r"([^.]*)\.")
    desc = pattern.sub("", description)
    # Clean up: ".." or " ." or trailing/leading spaces
    desc = re.sub(r"\.\s*\.", ".", desc)
    desc = re.sub(r"^\s*\.\s*", "", desc)
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


def already_has_alias_phrase(description: str, locale: str) -> bool:
    """Check if description already contains the alias phrase."""
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    return phrase in description


def process_file(
    path: Path, locale: str, dry_run: bool, species_to_plant: dict[str, str]
) -> int:
    """Process one language file. Returns count of updated plants."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for entry in data:
        if "_metadata" in entry:
            continue
        plant_id = entry.get("id")
        if not plant_id:
            continue

        type_name = entry.get("typeName") or ""
        description = entry.get("description") or ""
        common_examples = entry.get("commonExamples") or ""

        segments = parse_common_examples(common_examples)
        if not segments:
            continue

        # Only use segment if species maps to current plant (plan constraint)
        first_formal = segments[0][0].strip()
        if species_to_plant.get(first_formal) != plant_id:
            continue
        # Skip category plants (many sub-types): only add for specific plants (<=3 segments)
        if len(segments) > 3:
            continue

        formal, aliases = get_value_to_add(type_name, segments)

        if formal:
            value = formal
        elif aliases:
            value = ", ".join(aliases)
        else:
            continue

        if not value:
            continue

        alias_str = build_alias_string(value, locale)
        base_desc = strip_existing_alias(description, locale) if already_has_alias_phrase(description, locale) else description.rstrip()
        if not base_desc:
            base_desc = description.rstrip()
        if base_desc and not base_desc.endswith((".", "。", "!")):
            base_desc += "."
        new_desc = f"{alias_str} {base_desc}" if base_desc else alias_str

        if description == new_desc:
            continue

        if dry_run:
            print(f"  {plant_id} ({locale}): {alias_str.strip()} first")
        else:
            entry["description"] = new_desc
        updated += 1

    if not dry_run and updated > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return updated


def main():
    parser = argparse.ArgumentParser(description="Add 'also known as' to plant descriptions")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    files = [
        ("en", SOURCE_DIR / "common_plants_language_en.json"),
        ("es", SOURCE_DIR / "common_plants_language_es.json"),
        ("zh-Hans", SOURCE_DIR / "common_plants_language_zh-Hans.json"),
    ]

    mode = "dry-run" if args.dry_run else "write"
    print(f"Mode: {mode}\n")

    species_to_plant = build_species_to_plant_map(SOURCE_DIR)
    total = 0
    for locale, path in files:
        if not path.exists():
            print(f"  ⚠️  Skipping {path.name} (not found)")
            continue
        n = process_file(path, locale, args.dry_run, species_to_plant)
        total += n
        print(f"  {path.name}: {n} plants updated")

    print(f"\nTotal: {total} plants")
    if args.dry_run and total > 0:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
