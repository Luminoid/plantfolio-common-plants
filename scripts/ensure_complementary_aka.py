#!/usr/bin/env python3
"""
Add complementary "also known as" (aka) when missing. Aka is optional;
remove if it only repeats commonExamples names (run audit_also_known_as.py --fix).

- Plants using nickname as typeName → aka shows formal name
- Plants using formal name as typeName → aka shows nickname(s)

Processes EN, ES, ZH-Hans separately. Uses first-segment from commonExamples.
Per docs/DATASET.md: no scientific names in aka except when typeName is nickname.

Usage:
    python3 scripts/ensure_complementary_aka.py          # Update all language files
    python3 scripts/ensure_complementary_aka.py --dry-run  # Preview changes only
"""

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

ALIAS_PHRASES = {
    "en": "Also known as: ",
    "es": "También conocida como: ",
    "zh-Hans": "也称：",
}
ALIAS_SUFFIX = {"en": ".", "es": ".", "zh-Hans": "。"}
EXCLUDE_GENERIC = {
    "variety", "speckled variety", "杂交", "various", "var.", "subsp.", "syn.", "hybrid",
    "híbrido",
}


def normalize(s: str) -> str:
    return " ".join(s.lower().split())


def parse_common_examples(common_examples: str) -> list[tuple[str, list[str]]]:
    if not common_examples or not isinstance(common_examples, str):
        return []
    pattern = re.compile(r"([^(]+)\s*\(([^)]+)\)")
    segments = []
    for m in pattern.finditer(common_examples):
        formal = m.group(1).strip()
        paren = m.group(2).strip()
        if ";" in paren:
            paren = paren.split(";")[-1].strip()
        aliases = [
            a.strip()
            for a in paren.split(",")
            if a.strip() and a.lower() not in EXCLUDE_GENERIC and not a.lower().startswith("syn.")
        ]
        if formal and aliases:
            segments.append((formal, aliases))
    return segments


def looks_like_scientific_name(value: str) -> bool:
    """Check if value looks like a Latin/scientific name."""
    val = value.strip()
    if not val:
        return False
    # Binomial: Genus species
    if re.match(r"^[A-Z][a-z]+\s+[a-z]", val):
        return True
    # Cultivar in quotes
    if re.search(r"['\"][^'\"]+['\"]", val):
        return True
    if re.search(r"\b(var\.|subsp\.|×)\b", val, re.I):
        return True
    return False


def strip_aka_block(description: str, locale: str) -> str:
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    suffix = ALIAS_SUFFIX.get(locale, ALIAS_SUFFIX["en"])
    if phrase not in description:
        return description
    if suffix == "。":
        pattern = re.compile(re.escape(phrase) + r"([^。]*)" + re.escape(suffix))
    else:
        pattern = re.compile(re.escape(phrase) + r"([^.]*)\.")
    desc = pattern.sub("", description)
    desc = re.sub(r"\.\s*\.", ".", desc)
    desc = re.sub(r"^\s*\.\s*", "", desc)
    return re.sub(r"\s+", " ", desc).strip()


def build_aka_block(value: str, locale: str) -> str:
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    suffix = ALIAS_SUFFIX.get(locale, ALIAS_SUFFIX["en"])
    return f"{phrase}{value}{suffix}"


def get_complementary_value(
    type_name: str, segments: list[tuple[str, list[str]]], use_first_only: bool = True
) -> tuple[str | None, bool]:
    """
    Get the complementary value for aka.
    Returns (value, is_nickname_type) - value is formal if nickname, aliases if formal.
    """
    if not segments:
        return (None, False)

    if use_first_only:
        segments = segments[:1]

    all_formals = []
    all_aliases = []
    for formal, aliases in segments:
        all_formals.append(formal)
        all_aliases.extend(aliases)

    type_lower = type_name.lower()
    aliases_lower = [a.lower() for a in all_aliases]

    # typeName matches an alias → nickname → complementary is formal
    if type_lower in aliases_lower:
        return (", ".join(all_formals), True)

    # typeName matches formal (exact or genus)
    for formal in all_formals:
        formal_lower = formal.lower()
        if type_lower == formal_lower:
            break
        genus = formal.split()[0].lower() if formal else ""
        if genus and type_lower == genus:
            break
    else:
        formal = None

    # typeName is formal or unknown → complementary is aliases (exclude typeName)
    def is_redundant(alias: str) -> bool:
        al = alias.lower()
        if al == type_lower:
            return True
        if al in type_lower or type_lower in al:
            return True
        return False

    filtered = [
        a for a in all_aliases
        if not is_redundant(a)
        and not looks_like_scientific_name(a)
        and a.lower() not in EXCLUDE_GENERIC
    ]
    return (", ".join(filtered) if filtered else None, False)


def process_file(path: Path, locale: str, dry_run: bool) -> int:
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

        complementary, is_nickname = get_complementary_value(type_name, segments)
        if not complementary:
            continue

        base_desc = strip_aka_block(description, locale)
        if base_desc and not base_desc.endswith((".", "。", "!")):
            base_desc += "."
        new_desc = f"{build_aka_block(complementary, locale)} {base_desc}" if base_desc else build_aka_block(complementary, locale)

        if new_desc == description:
            continue

        if dry_run:
            kind = "formal" if is_nickname else "nickname"
            print(f"  {plant_id} [{locale}] ({kind}): → {complementary[:60]}{'...' if len(complementary) > 60 else ''}")
        else:
            entry["description"] = new_desc
        updated += 1

    if not dry_run and updated > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return updated


def main():
    parser = argparse.ArgumentParser(description="Ensure aka has complementary formal/nickname")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    files = [
        ("en", SOURCE_DIR / "common_plants_language_en.json"),
        ("es", SOURCE_DIR / "common_plants_language_es.json"),
        ("zh-Hans", SOURCE_DIR / "common_plants_language_zh-Hans.json"),
    ]

    mode = "dry-run" if args.dry_run else "write"
    print(f"Mode: {mode}\n")

    total = 0
    for locale, path in files:
        if not path.exists():
            print(f"  ⚠️  Skipping {path.name} (not found)")
            continue
        n = process_file(path, locale, args.dry_run)
        total += n
        print(f"  {path.name}: {n} plants updated")

    print(f"\nTotal: {total} plants")
    if args.dry_run and total > 0:
        print("\nRun without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
