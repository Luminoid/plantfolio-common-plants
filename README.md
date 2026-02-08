# plantfolio-common-plants

Curated plant care dataset (800 plants, 28 categories, EN/ES/ZH-Hans) for [Plantfolio](https://apps.apple.com/us/app/plantfolio-plus/id6757148663) ([Mac](https://apps.apple.com/us/mac-app/plantfolio-plus/id6757148663)). Care intervals, preferences, toxicity, localization.

## Background

**Plantfolio** is a plant care app for iPhone, iPad, and Mac. It helps users track watering schedules, care records, growth history, and photos. This dataset powers the app’s default common plants library — the built-in suggestions when adding a new plant.

**This dataset** — Each plant entry includes descriptions, care tips, seasonal watering intervals, light/humidity/temperature preferences, toxicity (ASPCA-aligned), soil pH, drainage, and optional USDA hardiness zones for outdoor plants. Scientific names follow botanical conventions (POWO/Kew). The dataset has been audited for metadata completeness, naming overlaps, and translation sync across EN, ES, and ZH-Hans.

Fork this repo to build your own data source — keep the same structure so Plantfolio can parse it. Found errors or have ideas? Open an issue or pull request.

## Quick Start

```bash
python3 scripts/release.py   # Build dist/, validate, run all audits (run before release)
```

**Workflow:** Edit `source/` → `merge_plant_data.py` → `dist/` → validate + audit.

## Repo Structure

| Path | Contents |
|------|----------|
| `source/` | **Metadata** (`common_plants_metadata.json`): intervals, preferences, category per plant. **Language** (`common_plants_language_*.json`): typeName, description, commonExamples, careTips per locale |
| `scripts/` | Merge, validate, audit, translate. Run from repo root |
| `dist/` | Generated merged JSON; do not edit |

Metadata is shared across locales; language is per-locale. `merge_plant_data.py` combines them.

## Common Tasks

| Task | Command |
|------|---------|
| Build dist only | `python3 scripts/merge_plant_data.py` |
| Validate dist | `python3 scripts/validate_json.py --check-structure` |
| Validate source metadata | `python3 scripts/validate_json.py --check-schema` |
| Extract category for audit | `python3 scripts/extract_by_category.py "Category Name"` |
| Audit metadata completeness | `python3 scripts/audit_metadata_completeness.py` |

## Scripts

| Script | Purpose |
|-------|---------|
| `release.py` | Full build + validate + all audits |
| `merge_plant_data.py` | Build dist/ from source |
| `validate_json.py` | Schema & structure validation |
| `schema.py` | CATEGORY_ORDER, enums (imported by other scripts) |
| `audit_*.py` | Duplicates, generic descriptions, translation sync, toxicity |
| `extract_by_category.py` | Extract category for audit sessions |
| `reorganize_plants.py` | Apply REMOVE_IDS, CATEGORY_CHANGES |
| `translate_typenames*.py` | Translate typeNames (EN→ZH, EN→ES) |

## Schema (quick reference)

**Required per plant:** `id`, `typeName`, `description`, `commonExamples`, `category`, `categoryIndex`, `springInterval`–`winterInterval` (1–90 or null), `lightPreference`, `humidityPreference`, `plantToxicity`, `soilPhPreference`, `drainagePreference`, `wateringMethod`, `temperaturePreference` [min,max] °C, `plantLifeSpan` [min,max|null].

**Enums:** [docs/DATASET.md#7-schema-reference](docs/DATASET.md#7-schema-reference) • **Categories:** [docs/DATASET.md#3-category-structure](docs/DATASET.md#3-category-structure)

## Custom Data Source

**Fork & edit:** Edit `source/`, run `merge_plant_data.py`, host dist JSON, use URLs in app.

**Raw JSON:** Output array of plant objects with schema above. Validate with `--check-structure` or `--check-schema`. See [docs/DATASET.md](docs/DATASET.md) for full spec.

## Pre-built data URLs

To use the default dataset without forking, copy the URLs below into your app config.

**Folder:** `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/`

| Locale | File | URL |
|--------|------|-----|
| EN | common_plants.json | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants.json` |
| ES | common_plants_es.json | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants_es.json` |
| ZH | common_plants_zh-Hans.json | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants_zh-Hans.json` |

## Docs

| Doc | Content |
|-----|---------|
| [docs/DATASET.md](docs/DATASET.md) | Schema, categories, enums, scientific nomenclature |
| [docs/AUDIT.md](docs/AUDIT.md) | Phase 1/2 checklists, toxicity, naming overlap |
| [docs/RELEASE.md](docs/RELEASE.md) | Release checklist |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

**AI:** [.cursor/CONTEXT.md](.cursor/CONTEXT.md) | [.cursor/rules/](.cursor/rules/)
