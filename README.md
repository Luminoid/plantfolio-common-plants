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

**Language rules:** Each language file must contain only its target language (EN, ES, or ZH). Exceptions: scientific names, Latin, cultivar names, proper nouns. **Also known as (aka):** Optional. When used, show complementary common-name aliases — nickname typeName → formal in aka; formal typeName → nickname(s). Remove if aka only repeats commonExamples names without adding value. **No scientific names** in aka (use common names only). **No subtypes** in aka (e.g., Fruit Trees should not aka Apple; Cacti should not aka Barrel cactus). First-segment aliases only for category plants; do not duplicate typeName. Run `audit_target_language.py` to verify.

## Common Tasks

| Task | Command |
|------|---------|
| Build dist only | `python3 scripts/merge_plant_data.py` |
| Validate dist | `python3 scripts/validate_json.py --check-structure` |
| Validate source metadata | `python3 scripts/validate_json.py --check-schema` |
| Extract category for audit | `python3 scripts/extract_by_category.py "Category Name"` |
| Audit metadata completeness | `python3 scripts/audit_metadata_completeness.py` |
| Audit target language | `python3 scripts/audit_target_language.py` |
| Audit also known as | `python3 scripts/audit_also_known_as.py` (use `--fix` to apply) |
| Ensure complementary aka | `python3 scripts/ensure_complementary_aka.py --dry-run` first |
| Add aliases to new plants | `python3 scripts/add_common_alias_to_description.py --dry-run` first |
| Translate typeNames | `python3 scripts/translate_typenames.py --lang zh-Hans` or `--lang es` |
| Optimize duplicate typeNames | `python3 scripts/optimize_duplicate_typenames.py --dry-run` then `--fix` |

## Scripts

| Script | Purpose |
|-------|---------|
| `release.py` | Full build + validate + all audits |
| `merge_plant_data.py` | Build dist/ from source |
| `validate_json.py` | Schema & structure validation |
| `schema.py` | CATEGORY_ORDER, enums (imported by other scripts) |
| `audit_*.py` | Duplicates, generic descriptions, translation sync, target language, also known as, toxicity |
| `ensure_complementary_aka.py` | Ensure aka has complementary form (nickname→formal, formal→nickname) per locale |
| `add_common_alias_to_description.py` | Add formal names/aliases from commonExamples to description (`--dry-run` first) |
| `extract_by_category.py` | Extract category for audit sessions |
| `reorganize_plants.py` | Apply REMOVE_IDS, CATEGORY_CHANGES |
| `translate_typenames.py` | Translate typeNames (EN→ZH or EN→ES via `--lang zh-Hans` / `--lang es`) |
| `optimize_duplicate_typenames.py` | Differentiate duplicate typeNames in each language file |

## Schema (quick reference)

**Required per plant:** `id`, `typeName`, `description`, `commonExamples`, `category`, `categoryIndex`, `springInterval`–`winterInterval` (1–90 or null), `lightPreference`, `humidityPreference`, `plantToxicity`, `soilPhPreference`, `drainagePreference`, `wateringMethod`, `temperaturePreference` [min,max] °C, `plantLifeSpan` [min,max|null].

**Enums:** [docs/DATASET.md#8-schema-reference](docs/DATASET.md#8-schema-reference) • **Categories:** [docs/DATASET.md#3-category-structure](docs/DATASET.md#3-category-structure)

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
| [docs/DATASET.md](docs/DATASET.md) | Schema, categories, enums, commonExamples format, description "also known as" |
| [docs/AUDIT.md](docs/AUDIT.md) | Phase 1/2 checklists, toxicity, naming overlap |
| [docs/RELEASE.md](docs/RELEASE.md) | Release checklist |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

**AI:** [.cursor/CONTEXT.md](.cursor/CONTEXT.md) | [.cursor/rules/](.cursor/rules/)
