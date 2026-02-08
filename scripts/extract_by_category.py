#!/usr/bin/env python3
"""Extract plant language entries by category for audit sessions.

Usage:
    python3 scripts/extract_by_category.py "Houseplants - Succulents"
    python3 scripts/extract_by_category.py "Outdoor - Trees" --locale es

Defaults: source/common_plants_metadata.json and source/common_plants_language_*.json.
See docs/AUDIT.md for workflow.
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_META = REPO_ROOT / "source" / "common_plants_metadata.json"
DEFAULT_LANG = REPO_ROOT / "source" / "common_plants_language_en.json"
LOCALE_SUFFIX = {"en": "en", "es": "es", "zh": "zh-Hans"}


def main():
    parser = argparse.ArgumentParser(
        description="Extract plant language entries by category for audit sessions"
    )
    parser.add_argument(
        "category",
        help='Category name (e.g. "Houseplants - Succulents")',
    )
    parser.add_argument(
        "--locale",
        "-l",
        choices=["en", "es", "zh"],
        default="en",
        help="Language locale (default: en)",
    )
    parser.add_argument(
        "--metadata",
        "-m",
        type=Path,
        default=DEFAULT_META,
        help=f"Path to metadata JSON (default: {DEFAULT_META})",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Write output to file instead of stdout",
    )
    args = parser.parse_args()

    meta_path = args.metadata if args.metadata.is_absolute() else REPO_ROOT / args.metadata
    if not meta_path.exists():
        print(f"Error: metadata file not found: {meta_path}", file=sys.stderr)
        sys.exit(1)

    lang_suffix = LOCALE_SUFFIX[args.locale]
    lang_path = REPO_ROOT / "source" / f"common_plants_language_{lang_suffix}.json"
    if not lang_path.exists():
        print(f"Error: language file not found: {lang_path}", file=sys.stderr)
        sys.exit(1)

    meta = json.load(meta_path.open(encoding="utf-8"))
    lang = json.load(lang_path.open(encoding="utf-8"))

    pids = [p for p, d in meta.items() if p != "_metadata" and d.get("category") == args.category]
    if not pids:
        print(
            f"No plants found in category: {args.category!r}",
            file=sys.stderr,
        )
        print("Valid categories: see docs/DATASET.md", file=sys.stderr)
        sys.exit(1)

    entries = []
    for entry in lang:
        if isinstance(entry, dict) and entry.get("id") in pids:
            entries.append(entry)

    out = json.dumps(entries, indent=2, ensure_ascii=False)
    if args.output:
        out_path = args.output if args.output.is_absolute() else REPO_ROOT / args.output
        out_path.write_text(out, encoding="utf-8")
        print(f"Wrote {len(entries)} entries to {out_path}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
