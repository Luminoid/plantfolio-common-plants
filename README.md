# plantfolio-common-plants

Common plants data source. **800 plants** across 28 categories in EN, ES, ZH-Hans—care info, watering intervals, localization.

**Edit `source/`** → merge builds `dist/` → release validates and audits. See `docs/DATASET.md` (schema, commands), `docs/AUDIT_*.md` (audit), `CHANGELOG.md` (history).

## Contents

| Directory | Contents |
|-----------|----------|
| `source/` | `common_plants_language_*.json` (EN, ES, ZH-Hans), `common_plants_metadata.json` |
| `scripts/` | `release.py` (before release), `merge_plant_data.py`, `validate_json.py`, audit scripts, `sort_plants.py`, `extract_by_category.py`, `reorganize_plants.py` |
| `dist/` | Generated `common_plants*.json` (do not edit) |

```bash
python3 scripts/release.py   # Build, validate, audit (before release)
```

## Usage

The merged files serve as a custom data source. Base URL (ending with `/`) or direct `.json` URL. See workspace root for integration details.

## Data Format

- **Source**: Language files = arrays; metadata = object keyed by plant ID.
- **Output**: Each `common_plants*.json` = merged array (typeName, description, careTips + intervals, category, lightPreference, etc.).

## Docs

| File | Description |
|------|-------------|
| `docs/DATASET.md` | Schema, categories, coverage |
| `docs/RELEASE.md` | Release checklist and steps |
| `docs/AUDIT_CHECKLIST_TEMPLATE.md` | Phase 1/2 audit checklists |
| `docs/AUDIT_METADATA.md` | Metadata audit spec (C1–C15) |
| `CHANGELOG.md` | Version history |

---

**AI context**: [.cursor/CONTEXT.md](.cursor/CONTEXT.md) | **Rules**: [.cursor/rules/](.cursor/rules/)
