#!/usr/bin/env python3
"""
Audit that each translation file contains only its target language.

Exceptions: scientific names (Latin binomials), cultivar names in 'quotes',
proper nouns with no translation (e.g. Tulsi, Kangkong).

Detects:
- Chinese characters in EN/ES files
- Non-Chinese common names in ZH commonExamples (where scientific name is given)
- English phrases in ZH/ES (untranslated content)
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SOURCE_DIR = REPO_ROOT / "source"

CJK = re.compile(r'[\u4e00-\u9fff]')

# English phrases that shouldn't appear in ZH/ES (case-insensitive)
EN_PHRASES_ZH = [
    "also known as", "common indoor plant", "common houseplant",
    "water when", "bright indirect", "low light", "medium humidity",
    "toxic to pets", "non-toxic", "fertilize monthly", "spring through fall",
    "black velvet", "purple shamrock", "baby rubber",
    "pink allusion", "string of", "mother-in-law", "peace lily",
]
EN_PHRASES_ES = [
    "also known as", "common indoor plant", "popular indoor plant",
    "black velvet", "purple shamrock", "baby rubber",
    "sweet basil", "genovese basil", "thai basil", "holy basil",
    "chinese spinach", "japanese mustard", "ceylon spinach",
    "common purslane", "chinese varieties", "rosette bok choy",
]


def audit_en(path: Path) -> list[dict]:
    """EN file should have no Chinese."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        for field in ["typeName", "description", "commonExamples", "careTips"]:
            val = entry.get(field, "") or ""
            for m in CJK.finditer(val):
                issues.append({
                    "kind": "cjk",
                    "id": entry.get("id"),
                    "field": field,
                    "char": m.group(),
                    "snippet": val[max(0, m.start() - 20) : m.end() + 20],
                })
                break
    return issues


def audit_es(path: Path) -> list[dict]:
    """ES file should have no Chinese."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        for field in ["typeName", "description", "commonExamples", "careTips"]:
            val = entry.get(field, "") or ""
            for m in CJK.finditer(val):
                issues.append({
                    "kind": "cjk",
                    "id": entry.get("id"),
                    "field": field,
                    "char": m.group(),
                    "snippet": val[max(0, m.start() - 20) : m.end() + 20],
                })
                break
    return issues


def audit_zh_common_examples(path: Path) -> list[dict]:
    """ZH file: commonExamples should not have English common names in parens (except cultivar 'X')."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    eng_common = re.compile(r'\([A-Z][a-z]+(?:\s+[a-z]+)*\)')
    for entry in data:
        if "_metadata" in entry:
            continue
        val = entry.get("commonExamples", "") or ""
        if "'" in val and "(" in val:
            continue
        for m in eng_common.finditer(val):
            snippet = m.group()
            if not CJK.search(snippet):
                if snippet.lower() in ("(leaf and stem)", "(edible greens)"):
                    continue
                if snippet.lower() in ("(goeppertia)",):
                    continue
                issues.append({
                    "kind": "eng-common",
                    "id": entry.get("id"),
                    "field": "commonExamples",
                    "snippet": val[:120],
                })
                break
    return issues


def audit_phrases(path: Path, locale: str, phrases: list[str]) -> list[dict]:
    """Find English phrases in ZH/ES files (untranslated content)."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    issues = []
    for entry in data:
        if "_metadata" in entry:
            continue
        for field in ["typeName", "description", "commonExamples", "careTips"]:
            val = entry.get(field, "") or ""
            if not val:
                continue
            val_lower = val.lower()
            for phrase in phrases:
                if phrase.lower() in val_lower:
                    issues.append({
                        "kind": "phrase",
                        "id": entry.get("id"),
                        "field": field,
                        "phrase": phrase,
                        "snippet": val[:100] + "..." if len(val) > 100 else val,
                    })
                    break
    return issues


def main() -> int:
    en_path = SOURCE_DIR / "common_plants_language_en.json"
    es_path = SOURCE_DIR / "common_plants_language_es.json"
    zh_path = SOURCE_DIR / "common_plants_language_zh-Hans.json"

    en_issues = audit_en(en_path) if en_path.exists() else []
    es_issues = audit_es(es_path) if es_path.exists() else []
    zh_common = audit_zh_common_examples(zh_path) if zh_path.exists() else []
    zh_phrases = audit_phrases(zh_path, "zh-Hans", EN_PHRASES_ZH) if zh_path.exists() else []
    es_phrases = audit_phrases(es_path, "es", EN_PHRASES_ES) if es_path.exists() else []

    ok = True
    print("=== Target language audit ===\n")

    if en_issues:
        ok = False
        print(f"EN (no Chinese): {len(en_issues)} issues")
        for i in en_issues[:10]:
            print(f"  {i['id']} [{i['field']}]: ...{i['snippet']}...")
        if len(en_issues) > 10:
            print(f"  ... and {len(en_issues) - 10} more")
        print()

    if es_issues:
        ok = False
        print(f"ES (no Chinese): {len(es_issues)} issues")
        for i in es_issues[:10]:
            print(f"  {i['id']} [{i['field']}]: ...{i['snippet']}...")
        if len(es_issues) > 10:
            print(f"  ... and {len(es_issues) - 10} more")
        print()

    if zh_common:
        ok = False
        print(f"ZH (no English common names in commonExamples): {len(zh_common)} issues")
        for i in zh_common[:10]:
            print(f"  {i['id']}: {i['snippet'][:80]}...")
        if len(zh_common) > 10:
            print(f"  ... and {len(zh_common) - 10} more")
        print()

    if zh_phrases:
        ok = False
        print(f"ZH (English phrases): {len(zh_phrases)} potential issues")
        for i in zh_phrases[:10]:
            print(f"  {i['id']} [{i['field']}]: '{i['phrase']}'")
        if len(zh_phrases) > 10:
            print(f"  ... and {len(zh_phrases) - 10} more")
        print()

    if es_phrases:
        ok = False
        print(f"ES (English phrases): {len(es_phrases)} potential issues")
        for i in es_phrases[:10]:
            print(f"  {i['id']} [{i['field']}]: '{i['phrase']}'")
        if len(es_phrases) > 10:
            print(f"  ... and {len(es_phrases) - 10} more")
        print()

    if ok:
        print("✅ All files pass target-language audit.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
