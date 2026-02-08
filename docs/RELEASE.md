# Release Checklist

Steps to cut a new minor/major release (e.g. 1.2.0 → 1.3.0).

## 1. Pre-release

```bash
python3 scripts/release.py
```

Fix any failures before proceeding.

## 2. Update version

| File | Change |
|------|--------|
| `VERSION` | Set to new version (e.g. `1.3.0`) |
| `CHANGELOG.md` | Move `[Unreleased]` content to `[X.Y.Z] - YYYY-MM-DD` |
| `docs/DATASET.md` | Update version reference in header |

## 3. Final check

```bash
python3 scripts/release.py
```

## 4. Tag and push

```bash
git add VERSION CHANGELOG.md docs/
git commit -m "Release v1.3.0"
git tag v1.3.0
git push && git push --tags
```
