#!/usr/bin/env python3
"""
Run everything required before release: build dist, validate, and run all audits.

Usage: python3 scripts/release.py
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent


def run(cmd: list[str], desc: str) -> bool:
    """Run command; return True if success."""
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"\n❌ {desc} failed")
        return False
    return True


def main():
    print("\n" + "=" * 50)
    print("PRE-RELEASE CHECKS")
    print("=" * 50 + "\n")

    ok = True
    ok &= run(["python3", "scripts/sort_plants.py"], "Sort source (category, canonical keys)")
    ok &= run(["python3", "scripts/merge_plant_data.py"], "Build dist from source")
    ok &= run(
        ["python3", "scripts/validate_json.py", "--check-schema", "--check-structure"],
        "Schema & structure validation",
    )
    ok &= run(["python3", "scripts/audit_metadata_completeness.py"], "Metadata completeness audit")
    ok &= run(["python3", "scripts/audit_scientific_names.py"], "Scientific name audit")
    ok &= run(["python3", "scripts/audit_duplicates.py"], "Duplicate audit")
    ok &= run(["python3", "scripts/audit_also_known_as.py"], "Also known as audit")
    ok &= run(["python3", "scripts/audit_generic_descriptions.py"], "Generic descriptions audit")
    ok &= run(["python3", "scripts/audit_translation_sync.py"], "Translation sync audit")
    ok &= run(["python3", "scripts/audit_target_language.py"], "Target language audit")

    print("\n" + "=" * 50)
    print("✅ Ready for release" if ok else "❌ Fix issues above before release")
    print("=" * 50)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
