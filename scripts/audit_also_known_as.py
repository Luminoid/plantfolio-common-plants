#!/usr/bin/env python3
"""
Audit "also known as" (aka) in plant descriptions across all languages.
Aka is optional; remove when redundant (e.g. only repeats commonExamples names).

Checks:
1. Scientific names: No Latin binomials, cultivars, etc. in AKA
2. Duplicate typeName: AKA should not repeat or shorten typeName (EN/ES/ZH)
3. Subspecies: Category plants should use only first-segment aliases

Usage:
    python3 scripts/audit_also_known_as.py              # Run all audits
    python3 scripts/audit_also_known_as.py --fix        # Apply all fixes
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
EXCLUDE_GENERIC = {"variety", "speckled variety", "杂交", "various", "var.", "subsp.", "syn.", "hybrid"}

# Scientific name patterns
BINOMIAL_RE = re.compile(r"\b([A-Z][a-z]+)\s+([a-z]+(?:\s+[a-z]+)?)\b")
CULTIVAR_RE = re.compile(r"['\"]([^'\"]+)['\"]")
TAXON_INDICATORS = re.compile(r"\b(var\.|subsp\.|subspecies|syn\.|×)\b", re.I)
SCIENTIFIC_GENERA = {
    "lithops", "phalaenopsis", "graptopetalum", "echeveria", "sedum",
    "curio", "haworthia", "aloe", "crassula", "kalanchoe", "schlumbergera",
    "epiphyllum", "rhipsalis", "mammillaria", "opuntia", "astrophytum",
    "saintpaulia", "streptocarpus", "goeppertia", "maranta", "ficus",
}
COMMON_FIRST_WORDS = {
    "chinese", "black", "tree", "green", "medicinal", "sweet", "glossy", "red",
    "mirror", "zebra", "grey", "gray", "giant", "moss", "cushion", "pink",
    "african", "violet", "compact", "striped", "corn", "dragon", "madagascar",
    "song", "india", "jamaica", "false", "bamboo", "reed", "cast", "iron",
    "barroom", "variegated", "speckled", "maria", "silver", "bay", "janet",
    "craig", "limelight", "warneckii", "domino", "sensation", "spotted",
    "leopard", "fancy", "arrow", "leaf", "angel", "wing", "heart", "elephant",
    "ear", "taro", "fish", "bone", "hen", "chick", "mother", "baby", "ghost",
    "pearl", "string", "pearls", "banana", "dolphin", "burro", "tail",
    "bleeding", "wax", "golden", "confederate", "jasmine", "coral", "trumpet",
    "cape", "primrose", "flaming", "katy", "purple", "shamrock", "emerald",
    "ripple", "natal", "plum", "lacy", "split", "sword", "mini", "miniature",
    "watermelon", "oval", "allusion", "rabbit", "foot", "bird", "nest",
    "button", "fern", "kangaroo", "paw", "maidenhair", "staghorn", "crest",
    "flame", "pencil", "barrel", "bun", "easter", "lily", "christmas",
    "thanksgiving", "crab", "claw", "moon", "chin", "star", "mistletoe",
    "rainbow", "lady", "slipper", "painted", "tongue", "lipstick",
    "lucky", "arabian", "coffee", "peacock", "cathedral", "window", "medallion",
    "rattlesnake", "prayer", "nerve", "moselike", "cloud", "brasil", "inch",
    "wandering", "jew", "spider", "paradise", "juniper", "coleus", "croton",
    "money", "swiss", "cheese", "silver", "terciopelo", "planta",
    "espejo", "cobre", "negro", "verde", "polly", "máscara", "mask",
    "poppy", "summer", "duck", "garden", "lace", "plumosa", "reina",
    "flamingo", "flower", "flor", "flamenco", "tree", "houseleek",
    "frijol", "helecho", "palmera", "pluma", "cola", "serpiente",
    "cadena", "perlas", "plátanos", "delfines", "cactus", "navidad",
    "pascua", "nopal", "oreja", "elefante", "mascara", "azuki", "rojo",
    "blanco", "azul", "dorado",
    "new", "england", "airplane", "ribbon", "zonal", "wine", "curly", "fishbone",
    "arum", "moth", "white", "sweet", "genovesa", "dulce", "japonesa", "ocupada",
    "jardín", "inglesa", "europea", "manojo", "lengua", "suegra",
    "crane", "gloriosa", "lime", "wild", "elkhorn", "turtle", "zanzibar", "eternity",
    "hope",
    "listada", "margarita", "enredadera", "tortuga", "pachysandra",
    "english", "albahaca", "pimiento", "camelia", "impatiens", "lizzie", "lavanda",
    "cebolla", "nabo", "yucca", "pera", "dracaena",
    "pak", "mosaic", "oyster", "mexican", "breadfruit", "espada", "plateada",
    "amor", "hombre", "spiderwort", "blanket",
    "common", "small", "large", "great", "lenten", "pincushion", "bee",
    "rose", "rosa", "trailing", "wavyleaf", "cider", "nagoya", "broad", "night",
    "hoary", "ruby", "ornamental", "bearded", "yellow", "tulip",
    "amazon", "victoria", "albany", "devil", "hay", "old", "man",
}


def looks_like_scientific_name(value: str) -> bool:
    val = value.strip()
    if not val:
        return False
    # AKA must be common names only — no scientific synonyms
    if re.search(r"\bsyn\.\s", val, re.I) or "同义名" in val:
        return True
    for m in BINOMIAL_RE.finditer(val):
        if m.group(1).lower() not in COMMON_FIRST_WORDS:
            return True
    if CULTIVAR_RE.search(val) and any(c.islower() for c in val):
        return True
    if TAXON_INDICATORS.search(val) or "×" in val:
        return True
    words = val.split()
    if len(words) == 1 and words[0].lower() in SCIENTIFIC_GENERA:
        return True
    if re.search(r"\b[A-Z]\.\s*[a-z]+", val):
        return True
    return False


def normalize(s: str) -> str:
    return " ".join(s.lower().split())


def extract_aka(description: str, locale: str) -> str | None:
    phrase = ALIAS_PHRASES.get(locale, ALIAS_PHRASES["en"])
    suffix = ALIAS_SUFFIX.get(locale, ALIAS_SUFFIX["en"])
    if phrase not in description:
        return None
    start = description.index(phrase) + len(phrase)
    end = description.find(suffix, start)
    if end == -1:
        end = len(description)
    return description[start:end].strip()


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
        aliases = [a.strip() for a in paren.split(",") if a.strip() and a.lower() not in EXCLUDE_GENERIC and not a.lower().startswith("syn.")]
        if formal and aliases:
            segments.append((formal, aliases))
    return segments


def parse_common_examples_aliases_only(common_examples: str, first_segment_only: bool = False) -> list[str]:
    segments = parse_common_examples(common_examples)
    if not segments:
        return []
    result = []
    for i, (_, aliases) in enumerate(segments):
        if first_segment_only and i > 0:
            break
        result.extend(aliases)
    return result


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


def get_valid_aliases(type_name: str, common_examples: str) -> list[str]:
    segments = parse_common_examples(common_examples)
    if not segments:
        return []
    type_lower = type_name.lower()
    result = []
    for _, aliases in segments:
        for a in aliases:
            if a.lower() == type_lower:
                continue
            if looks_like_scientific_name(a):
                continue
            result.append(a)
    return result


def get_formal_name_for_nickname(type_name: str, common_examples: str) -> str | None:
    """If typeName matches an alias, return the formal name (allowed in aka)."""
    segments = parse_common_examples(common_examples)
    if not segments:
        return None
    type_lower = type_name.lower()
    for formal, aliases in segments:
        for a in aliases:
            if a.lower() == type_lower:
                return formal.strip()
    return None


# --- Check 1: Scientific names in AKA ---

def audit_scientific(path: Path, locale: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        parts = [p.strip() for p in aka.split(",")]
        scientific_parts = [p for p in parts if looks_like_scientific_name(p)]
        if scientific_parts:
            issues.append({
                "kind": "scientific",
                "id": entry.get("id"),
                "typeName": entry.get("typeName"),
                "locale": locale,
                "current_aka": aka,
                "scientific_parts": scientific_parts,
                "valid_parts": [p for p in parts if not looks_like_scientific_name(p)],
                "valid_alternatives": get_valid_aliases(entry.get("typeName", ""), entry.get("commonExamples", "")),
            })
    return issues


def fix_scientific(path: Path, locale: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        parts = [p.strip() for p in aka.split(",")]
        type_name = entry.get("typeName", "")
        common_examples = entry.get("commonExamples", "")
        scientific_parts = [p for p in parts if looks_like_scientific_name(p)]
        if not scientific_parts:
            continue
        valid_alternatives = get_valid_aliases(type_name, common_examples)
        valid_parts = [p for p in parts if not looks_like_scientific_name(p)]
        if valid_alternatives:
            new_value = ", ".join(valid_alternatives[:3])
        elif valid_parts:
            new_value = ", ".join(valid_parts)
        else:
            new_desc = strip_aka_block(entry["description"], locale)
            if new_desc and not new_desc.endswith((".", "。")):
                new_desc += "."
            entry["description"] = new_desc
            fixed += 1
            continue
        new_block = build_aka_block(new_value, locale)
        base_desc = strip_aka_block(entry["description"], locale)
        if base_desc and not base_desc.endswith((".", "。")):
            base_desc += "."
        new_desc = f"{new_block} {base_desc}" if base_desc else new_block
        if entry["description"] != new_desc:
            entry["description"] = new_desc
            fixed += 1
    if fixed > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return fixed


# --- Check 2: typeName redundant with AKA (ES/ZH only) ---

def is_redundant_part(type_name: str, aka_part: str) -> bool:
    tn = normalize(type_name)
    part = normalize(aka_part)
    if tn == part:
        return True
    if part in tn:
        return True
    return False


def looks_scientific_simple(name: str) -> bool:
    n = name.strip()
    if not n or " " in n:
        return False
    if re.match(r"^[A-Z][a-z]+$", n):
        return True
    return False


def get_valid_alternatives(type_name: str, common_examples: str, current_aka: str) -> list[str]:
    aliases = parse_common_examples_aliases_only(common_examples, first_segment_only=True)
    current_parts = {normalize(p.strip()) for p in current_aka.split(",")}
    result = []
    for a in aliases:
        if is_redundant_part(type_name, a):
            continue
        if normalize(a) in current_parts:
            continue
        if looks_scientific_simple(a):
            continue
        result.append(a)
    return result


def filter_redundant_aka(type_name: str, aka: str) -> tuple[str | None, bool]:
    parts = [p.strip() for p in aka.split(",")]
    kept = [p for p in parts if not is_redundant_part(type_name, p)]
    if not kept:
        return (None, True)
    return (", ".join(kept), ", ".join(kept) != aka)


def audit_duplicate_typename(path: Path, locale: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        new_aka, changed = filter_redundant_aka(entry.get("typeName", ""), aka)
        if not changed and new_aka:
            continue
        issues.append({
            "kind": "duplicate-typename",
            "id": entry.get("id"),
            "typeName": entry.get("typeName"),
            "aka": aka,
            "new_aka": new_aka,
            "alternatives": get_valid_alternatives(entry.get("typeName", ""), entry.get("commonExamples", ""), aka) if new_aka is None else [],
            "locale": locale,
        })
    return issues


def fix_duplicate_typename(path: Path, locale: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        new_aka, changed = filter_redundant_aka(entry.get("typeName", ""), aka)
        if not changed and new_aka:
            continue
        base_desc = strip_aka_block(entry["description"], locale)
        if base_desc and not base_desc.endswith((".", "。", "!")):
            base_desc += "."
        if new_aka:
            new_desc = f"{build_aka_block(new_aka, locale)} {base_desc}" if base_desc else build_aka_block(new_aka, locale)
        else:
            alternatives = get_valid_alternatives(entry.get("typeName", ""), entry.get("commonExamples", ""), aka)
            if alternatives:
                alt = ", ".join(alternatives[:3])
                new_desc = f"{build_aka_block(alt, locale)} {base_desc}" if base_desc else build_aka_block(alt, locale)
            else:
                new_desc = base_desc
        if entry["description"] != new_desc:
            entry["description"] = new_desc
            fixed += 1
    if fixed > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return fixed


# --- Check 3: Subspecies in AKA (use first-segment only for category plants) ---

def audit_subspecies(path: Path, locale: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        segments = parse_common_examples(entry.get("commonExamples", ""))
        if len(segments) < 2:
            continue
        other_aliases = {normalize(a) for _, aliases in segments[1:] for a in aliases}
        aka_parts = [p.strip() for p in aka.split(",")]
        subspecies_parts = [p for p in aka_parts if normalize(p) in other_aliases]
        if subspecies_parts:
            type_name = entry.get("typeName", "")
            valid_parts = [p for p in aka_parts if normalize(p) not in other_aliases]
            first_valid = [a for a in segments[0][1] if not (a.lower() == type_name.lower() or normalize(a) in normalize(type_name))]
            issues.append({
                "kind": "subspecies",
                "id": entry.get("id"),
                "typeName": type_name,
                "aka": aka,
                "subspecies_parts": subspecies_parts,
                "valid_parts": valid_parts,
                "first_segment_aliases": segments[0][1],
                "locale": locale,
            })
    return issues


def fix_subspecies(path: Path, locale: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    fixed = 0
    for entry in data:
        if "_metadata" in entry:
            continue
        aka = extract_aka(entry.get("description", ""), locale)
        if not aka:
            continue
        segments = parse_common_examples(entry.get("commonExamples", ""))
        if len(segments) < 2:
            continue
        other_aliases_set = {normalize(a) for _, aliases in segments[1:] for a in aliases}
        aka_parts = [p.strip() for p in aka.split(",")]
        subspecies_parts = [p for p in aka_parts if normalize(p) in other_aliases_set]
        if not subspecies_parts:
            continue
        type_name = entry.get("typeName", "")
        valid_parts = [p for p in aka_parts if normalize(p) not in other_aliases_set]
        first_aliases = segments[0][1]
        first_valid = [a for a in first_aliases if not (a.lower() == type_name.lower() or normalize(a) in normalize(type_name))]
        if valid_parts:
            new_value = ", ".join(valid_parts)
        elif first_valid:
            new_value = ", ".join(first_valid[:3])
        else:
            new_value = None
        base_desc = strip_aka_block(entry["description"], locale)
        if base_desc and not base_desc.endswith((".", "。", "!")):
            base_desc += "."
        if new_value:
            new_desc = f"{build_aka_block(new_value, locale)} {base_desc}" if base_desc else build_aka_block(new_value, locale)
        else:
            new_desc = base_desc
        if entry["description"] != new_desc:
            entry["description"] = new_desc
            fixed += 1
    if fixed > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return fixed


FILES = [
    ("en", SOURCE_DIR / "common_plants_language_en.json"),
    ("es", SOURCE_DIR / "common_plants_language_es.json"),
    ("zh-Hans", SOURCE_DIR / "common_plants_language_zh-Hans.json"),
]


def main():
    parser = argparse.ArgumentParser(description="Audit/fix 'also known as' (scientific, duplicate typeName, subspecies)")
    parser.add_argument("--fix", action="store_true", help="Apply fixes to source files")
    args = parser.parse_args()

    if args.fix:
        print("=== FIX: Also known as (all checks) ===\n")
        total = 0
        for locale, path in FILES:
            if not path.exists():
                continue
            n = fix_scientific(path, locale)
            if n:
                total += n
                print(f"  {path.name} [{locale}] scientific: {n} fixed")
        for locale, path in FILES:
            if not path.exists():
                continue
            n = fix_duplicate_typename(path, locale)
            if n:
                total += n
                print(f"  {path.name} [{locale}] duplicate-typename: {n} fixed")
        for locale, path in FILES:
            if not path.exists():
                continue
            n = fix_subspecies(path, locale)
            if n:
                total += n
                print(f"  {path.name} [{locale}] subspecies: {n} fixed")
        print(f"\nTotal: {total} plants fixed")
        return

    sci = []
    for locale, path in FILES:
        if path.exists():
            sci.extend(audit_scientific(path, locale))
    dup = []
    for locale, path in FILES:
        if path.exists():
            dup.extend(audit_duplicate_typename(path, locale))
    sub = []
    for locale, path in FILES:
        if path.exists():
            sub.extend(audit_subspecies(path, locale))

    ok = True
    if sci:
        ok = False
        print("=== Scientific names in 'also known as' ===\n")
        by_id = {}
        for i in sci:
            by_id.setdefault(i["id"], []).append(i)
        for pid in sorted(by_id.keys()):
            for item in by_id[pid]:
                print(f"  {item['id']} [{item['locale']}] {item['typeName']}")
                print(f"    Current: {item['current_aka']}")
                print(f"    Scientific (remove): {item['scientific_parts']}")
        print()
    if dup:
        ok = False
        print("=== typeName same as / redundant with also known as ===\n")
        for i in dup:
            print(f"  {i['id']} [{i['locale']}] {i['typeName']}")
            print(f"    current aka: {i['aka']}")
            print(f"    → new aka: {i['new_aka'] or '(remove)'}")
        print()
    if sub:
        ok = False
        print("=== Subspecies in also known as (use first-segment only) ===\n")
        for i in sub:
            print(f"  {i['id']} [{i['locale']}] {i['typeName']}")
            print(f"    current aka: {i['aka']}")
            print(f"    sub-species (remove): {i['subspecies_parts']}")
        print()

    if sci or dup or sub:
        print("Run with --fix to apply corrections.")
        return 1
    print("✅ All 'also known as' checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
