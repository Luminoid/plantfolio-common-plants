# plantfolio-common-plants

**800 plants** across 28 categories (EN, ES, ZH-Hans). Care info, watering intervals, localization.

## Quick Start

```bash
python3 scripts/release.py   # Build, validate, audit (before release)
```

**Workflow:** Edit `source/` → merge builds `dist/` → release validates and audits.

## Structure

| Path | Contents |
|------|----------|
| `source/` | Language JSON (EN, ES, ZH), metadata JSON |
| `scripts/` | `release.py`, `merge_plant_data.py`, `validate_json.py`, `schema.py`, audit scripts |
| `dist/` | Generated merged JSON (do not edit) |

## Scripts

| Script | Purpose |
|-------|---------|
| `release.py` | Build + validate + all audits (run before release) |
| `merge_plant_data.py` | Build dist/ from source |
| `validate_json.py` | Schema & structure validation |
| `schema.py` | Shared constants (CATEGORY_ORDER, enums) |
| `audit_*.py` | Metadata, duplicates, generic descriptions, translation sync, toxicity |
| `extract_by_category.py` | Extract category for audit sessions |
| `reorganize_plants.py` | Apply REMOVE_IDS, CATEGORY_CHANGES |
| `translate_typenames*.py` | Translate typeNames (EN→ZH, EN→ES) |

## Docs

| Doc | Content |
|-----|---------|
| [docs/DATASET.md](docs/DATASET.md) | Schema, categories, enums |
| [docs/AUDIT.md](docs/AUDIT.md) | Phase 1/2 checklists, toxicity, naming overlap |
| [docs/RELEASE.md](docs/RELEASE.md) | Release checklist |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

**AI:** [.cursor/CONTEXT.md](.cursor/CONTEXT.md) | [.cursor/rules/](.cursor/rules/)
