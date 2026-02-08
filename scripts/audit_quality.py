#!/usr/bin/env python3
"""
Run all quality audits and produce a summary report.

Usage:
    python3 scripts/audit_quality.py           # Run all, print summary
    python3 scripts/audit_quality.py --full    # Run all with full output
    python3 scripts/audit_quality.py --output report.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

AUDITS = [
    ("validate_json", "Schema & structure validation", ["python3", "scripts/validate_json.py", "--check-schema", "--check-structure"]),
    ("metadata_completeness", "Metadata completeness", ["python3", "scripts/audit_metadata_completeness.py"]),
    ("scientific_names", "Scientific names", ["python3", "scripts/audit_scientific_names.py"]),
    ("duplicates", "Duplicate/overlap audit", ["python3", "scripts/audit_duplicates.py"]),
    ("also_known_as", "Also known as", ["python3", "scripts/audit_also_known_as.py"]),
    ("generic_descriptions", "Generic descriptions", ["python3", "scripts/audit_generic_descriptions.py"]),
    ("translation_sync", "Translation sync", ["python3", "scripts/audit_translation_sync.py"]),
    ("target_language", "Target language", ["python3", "scripts/audit_target_language.py"]),
    ("toxicity_unknown", "Toxicity unknown (info)", ["python3", "scripts/audit_toxicity_unknown.py"]),
]


def run_audit(cmd: list[str], full: bool) -> tuple[bool, str]:
    """Run audit; return (success, output)."""
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    out = result.stdout + result.stderr
    return result.returncode == 0, out


def main():
    parser = argparse.ArgumentParser(description="Run all quality audits and produce summary")
    parser.add_argument("--full", "-f", action="store_true", help="Print full output from each audit")
    parser.add_argument("--output", "-o", metavar="FILE", help="Write report to file")
    args = parser.parse_args()

    lines = []
    failed = []

    def out(s: str = ""):
        lines.append(s)
        print(s)

    out("=" * 60)
    out("PLANTFOLIO COMMON PLANTS — QUALITY AUDIT")
    out("=" * 60)
    out()

    for key, desc, cmd in AUDITS:
        success, output = run_audit(cmd, args.full)
        status = "✅" if success else "❌"
        out(f"{status} {desc}")
        if args.full and output.strip():
            for line in output.strip().split("\n"):
                out(f"   {line}")
        elif not success and output.strip():
            # Show first few lines of failure
            for line in output.strip().split("\n")[:15]:
                out(f"   {line}")
        if not success:
            failed.append(desc)
        out()

    out("-" * 60)
    if failed:
        out(f"❌ {len(failed)} audit(s) failed: {', '.join(failed)}")
        out()
        out("Run individual scripts for details. Fix before release.")
        exit_code = 1
    else:
        out("✅ All quality audits passed")
        exit_code = 0

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        out(f"\nReport written to {out_path}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
