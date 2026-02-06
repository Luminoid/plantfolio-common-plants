#!/usr/bin/env python3
"""
Validate generated JSON files in dist/.

Checks JSON syntax and optionally structure of common_plants files.
Run after merge to verify built output.

Usage:
    python3 scripts/validate_json.py [FILE...]
    python3 scripts/validate_json.py --check-structure
"""

import json
import argparse
import sys
from pathlib import Path


def validate_json_file(file_path):
    """Validate a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, str(e)
    except FileNotFoundError:
        return False, None, "File not found"
    except Exception as e:
        return False, None, str(e)


def main():
    parser = argparse.ArgumentParser(description="Validate generated JSON files in dist/")
    parser.add_argument("files", nargs="*", help="JSON files (default: dist/common_plants*.json)")
    parser.add_argument("--check-structure", action="store_true", help="Check common_plants structure")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    dist_dir = repo_root / "dist"

    if not args.files:
        default_files = [
            dist_dir / "common_plants.json",
            dist_dir / "common_plants_es.json",
            dist_dir / "common_plants_zh-Hans.json",
        ]
        files_to_check = [str(f) for f in default_files if f.exists()]
    else:
        files_to_check = args.files

    if not files_to_check:
        print("No JSON files found to validate")
        sys.exit(1)

    all_valid = True
    for file_path in files_to_check:
        is_valid, data, error = validate_json_file(file_path)
        if is_valid:
            print(f"✅ {file_path}: Valid JSON")
            if args.check_structure and "common_plants" in file_path:
                if isinstance(data, list) and len(data) > 0:
                    required_keys = ["id", "typeName", "description", "commonExamples"]
                    first_entry = data[0]
                    missing_keys = [k for k in required_keys if k not in first_entry]
                    if missing_keys:
                        print(f"  ⚠️  Missing required keys: {', '.join(missing_keys)}")
                    else:
                        print(f"  ✅ Structure valid ({len(data)} entries)")
                else:
                    print(f"  ⚠️  Expected a non-empty array")
        else:
            print(f"❌ {file_path}: {error}")
            all_valid = False

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
