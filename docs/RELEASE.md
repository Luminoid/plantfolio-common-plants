# Release Checklist

Steps for a new minor/major release (e.g. 1.5.0 → 1.6.0).

## 1. Pre-release

```bash
python3 scripts/release.py
```

Runs: sort → merge → validate → metadata audit → scientific names → duplicates → also known as → generic descriptions → translation sync → target language. Fix any failures.

**Optional:** Run `python3 scripts/audit_quality.py` for a summary of all quality audits. If `audit_duplicates.py` reports duplicate typeNames (same name across entries), run `python3 scripts/optimize_duplicate_typenames.py --dry-run` then `--fix`.

## 2. Update version

| File | Change |
|------|--------|
| `VERSION` | Set to new version (e.g. `1.6.0`) |
| `CHANGELOG.md` | Move `[Unreleased]` content to `[X.Y.Z] - YYYY-MM-DD` |
| `docs/DATASET.md` | Update version reference in header |
| `source/common_plants_metadata.json` | `_metadata.version` → new version |
| `source/common_plants_language_*.json` | `_metadata.version` → new version (EN, ES, ZH) |

## 3. Final check

```bash
python3 scripts/release.py
```

## 4. Tag and push

```bash
git add VERSION CHANGELOG.md docs/ README.md source/ dist/ scripts/
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push && git push --tags
```

Replace `X.Y.Z` with the version (e.g. `1.6.0`).
