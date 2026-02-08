# Release Checklist

Steps for a new minor/major release (e.g. 1.4.0 → 1.5.0).

## 1. Pre-release

```bash
python3 scripts/release.py
```

Runs: sort → merge → validate → metadata audit → scientific names → duplicates → generic descriptions → translation sync. Fix any failures.

## 2. Update version

| File | Change |
|------|--------|
| `VERSION` | Set to new version (e.g. `1.3.0`) |
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
git add VERSION CHANGELOG.md docs/ README.md source/
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push && git push --tags
```

Replace `X.Y.Z` with the version (e.g. `1.3.0`).
