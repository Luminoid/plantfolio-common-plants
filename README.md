# plantfolio-common-plants

Curated plant care dataset (864 plants, 28 categories, EN/ES/ZH-Hans) for [Plantfolio](https://apps.apple.com/us/app/plantfolio-plus/id6757148663) ([Mac](https://apps.apple.com/us/mac-app/plantfolio-plus/id6757148663)). Care intervals, preferences, toxicity, localization.

## Disclaimer

This dataset is provided for general informational purposes only. It is not maintained by horticultural or botanical professionals and may contain inaccuracies, omissions, or errors. Care recommendations, toxicity information, and plant identifiers are best-effort compilations — do not rely on them as a substitute for expert advice. For plant identification, toxicity concerns, or specialized care, consult a qualified horticulturist, botanist, or veterinarian.

## Background

**Plantfolio** is a plant care app for iPhone, iPad, and Mac. It helps users track watering schedules, care records, growth history, and photos. This dataset powers the app’s default common plants library — the built-in suggestions when adding a new plant.

**This dataset** — Each plant entry includes descriptions, care tips, seasonal watering intervals, light/humidity/temperature preferences, toxicity (ASPCA-aligned), soil pH, drainage, and optional USDA hardiness zones for outdoor plants. Scientific names follow botanical conventions (POWO/Kew). The dataset has been audited for metadata completeness, naming overlaps, and translation sync across EN, ES, and ZH-Hans.

Fork this repo to build your own data source — keep the same structure so Plantfolio can parse it. Found errors or have ideas? Open an issue or pull request.

## Quick Start

```bash
python3 scripts/release.py   # Build dist/, validate, run all audits (run before release)
```

**Workflow:** Edit `source/` → `sort_plants.py` → `merge_plant_data.py` → `dist/` → validate + audit. Run `audit_quality.py` for a quick summary of all checks.

## Repo Structure

| Path | Contents |
|------|----------|
| `source/` | **Metadata** (`common_plants_metadata.json`): intervals, preferences, category per plant. **Language** (`common_plants_language_*.json`): typeName, description, commonExamples, careTips per locale |
| `scripts/` | Merge, validate, audit, translate. Run from repo root |
| `dist/` | Generated merged JSON; do not edit |

Metadata is shared across locales; language is per-locale. `merge_plant_data.py` combines them. When adding or removing plants, update `_metadata.plantCount` in `common_plants_metadata.json` to match the number of plant entries; release validation will fail if it doesn’t.

**Language rules:** Each language file must contain only its target language (EN, ES, or ZH). Exceptions: scientific names, Latin, cultivar names, proper nouns. **Descriptions** must end with a period (`.`). **Also known as (aka):** Optional. When used, show complementary common-name aliases — nickname typeName → formal in aka; formal typeName → nickname(s). Remove if aka only repeats commonExamples names without adding value. **No scientific names** in aka (use common names only). **No subtypes** in aka (e.g., Fruit Trees should not aka Apple; Cacti should not aka Barrel cactus). **No aka that matches another plant's typeName** — if two entries share a common name, keep them separate without cross-referencing via aka. **No duplicate aka** — no two plants may share the same aka within a locale. **Category entries** should not use specific entries' names as aka (e.g., Pothos category should not aka "Devil's ivy" when Golden Pothos already has it). First-segment aliases only for category plants; do not duplicate typeName. **No duplicate typeNames** within a locale. Run `audit_target_language.py` and `audit_also_known_as.py` to verify.

## Data Conventions

Horticultural rules applied when setting or reviewing metadata. Use these when adding or auditing plants.

### Light preference

`lightPreference` represents the plant's **optimal** light, not just what it tolerates.

| Rule | Example |
|------|---------|
| Variegated/colored plants need more light than their all-green counterparts | Red Valentine Aglaonema → brightIndirect (not lowIndirect) |
| Snake plants (Dracaena trifasciata/angolensis) prefer bright indirect, only tolerate low | All snake plant varieties → brightIndirect |
| Plants that drop leaves in low light should not be lowIndirect | Weeping Fig, False Aralia, Ming Aralia → brightIndirect |
| Desert cacti need strong direct sun | Mammillaria, Echinopsis, Opuntia → strongDirect |
| Forest/jungle cacti prefer bright indirect (no direct sun) | Christmas Cactus, Rhipsalis, Epiphyllum → brightIndirect |
| Sun-loving flowering plants need strongDirect for blooming | Tropical Hibiscus, Mandevilla → strongDirect |
| Carnivorous bog plants (Venus flytrap, Sarracenia) need strong direct | Venus Flytrap, Sarracenia → strongDirect |
| Translucent/windowed succulents burn in strong direct | Haworthia Cooperi → brightIndirect |
| Outdoor plants use outdoor* values | outdoorFullSun, outdoorPartialSun, outdoorShade |

### Watering intervals

| Plant type | Spring | Summer | Fall | Winter | Notes |
|------------|--------|--------|------|--------|-------|
| Desert cacti (large) | 21 | 21 | 30 | 45 | Barrel, Prickly Pear, Star |
| Desert cacti (small globular) | 14 | 14 | 21 | 30 | Mammillaria, Echinopsis, Parodia |
| Forest/jungle cacti | 7 | 7 | 10 | 14 | Christmas, Rhipsalis, Epiphyllum |
| Summer-dormant succulents | longer intervals in summer | | | | Aeonium, Lithops |
| Mediterranean herbs | 7 | 10 | 14 | null | Drought-tolerant; longer in summer is correct |
| Sprouts & microgreens | 1–3 | 1–3 | 1–3 | 1–3 | Very frequent |
| Aquatic plants | null | null | null | null | No watering intervals |

### Toxicity

**Consistency rule:** All plants in the same genus sharing the same toxic compound must have the same `plantToxicity` value — do not mix mildlyToxic and toxic within a family.

| Family/compound | Level | Examples |
|----------------|-------|---------|
| Insoluble calcium oxalate aroids | mildlyToxic | Pothos, Monstera, Philodendron, Syngonium |
| Begonia (soluble calcium oxalates) | toxic | Tubers most toxic; potential kidney effects |
| Peace lilies (Spathiphyllum) | toxic | More severe irritation than typical calcium oxalate |
| Dracaena / Snake plants | toxic | ASPCA-listed toxic |
| Ficus (latex) | toxic | Rubber Plant, Fiddle-Leaf Fig, Weeping Fig |
| Kalanchoe (cardiac glycosides) | toxic | All Kalanchoe species |
| Peperomia, Hoya, Calathea/Maranta, Spider Plant, Palms, Ferns | nonToxic | ASPCA non-toxic |
| Edible plants with toxic parts | toxic | Avocado (persin), Elderberry (raw), Taro (raw oxalate) |

### Drainage

| Plant type | Drainage | Notes |
|------------|----------|-------|
| Succulents & desert cacti | excellentDrainage or wellDraining | Never moistureRetentive |
| Bog carnivorous (Venus flytrap, Sarracenia, Sundew) | moistureRetentive | Sit in water trays; null wateringMethod |
| Epiphytic carnivorous (Nepenthes) | excellentDrainage | Airy mix, not standing water |
| Aquatic plants | waterloggingTolerant | null wateringMethod |
| Alpine plants | excellentDrainage or wellDraining | Mountain drainage |

### Descriptions

| Rule | Notes |
|------|-------|
| Must end with a period (`.`) | All descriptions, all locales |
| "Also known as:" must be capitalized and at start of description | `Also known as: X. Actual description.` |
| No repeated/corrupted subspecies text | Check for `word. word. word.` patterns |
| Each plant must have a unique description | No placeholder or duplicate descriptions across plants |
| Category entries get brief genus/family overviews | Specific entries get species-level detail |
| Sprouts & microgreens need specific descriptions | Not generic "Microgreens" labels |
| commonExamples use species-specific common names | `Pisum sativum (Pea shoots)` not `Pisum sativum (Microgreens)` |

### Lifespan

`plantLifeSpan` is `[min_years, max_years]`. Both values should be concrete integers when possible. Use `null` only when a bound is truly unknown.

| Plant type | plantLifeSpan [min, max] | Notes |
|------------|-------------------------|-------|
| Trees | [20, 100] to [100, 500] | Species-specific; 3 is never correct for a tree |
| Shrubs | [5, 10] to [30, 100] | Long-lived shrubs (boxwood, lilac) can exceed 100 |
| Perennial houseplants | [3, 10] to [10, 50] | Varies by species; cacti and jade plants live longest |
| Annuals | [1, 1] | Single growing season |
| Sprouts & microgreens | [1, 1] | Very short lifecycle |
| Fruits & berries | [1, 6] to [60, 100] | Banana [1, 6] vs Coconut [60, 100] |
| Bulbs | [3, 8] to [10, 30] | Most naturalize and persist many years |

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
| Run all quality audits | `python3 scripts/audit_quality.py` |
| Audit toxicity vs care tips | `python3 scripts/audit_toxicity_care_tips.py` |
| List plants with unknown toxicity | `python3 scripts/audit_toxicity_unknown.py` (optionally `--category "Name"` or `--output file.json`) |
| Ensure complementary aka | `python3 scripts/ensure_complementary_aka.py --dry-run` first |
| Add aliases to new plants | `python3 scripts/add_common_alias_to_description.py --dry-run` first |
| Infer missing metadata | `python3 scripts/improve_plant_data.py` (soil pH, drainage, lifespan; `--dry-run` first) |
| Translate typeNames | `python3 scripts/translate_typenames.py --lang zh-Hans` or `--lang es` |
| Optimize duplicate typeNames | `python3 scripts/optimize_duplicate_typenames.py --dry-run` then `--fix` |

## Scripts

| Script | Purpose |
|-------|---------|
| `release.py` | Full build + validate + all audits |
| `audit_quality.py` | Run all quality audits and produce summary |
| `merge_plant_data.py` | Build dist/ from source |
| `sort_plants.py` | Sort source by category, canonical keys |
| `validate_json.py` | Schema & structure validation |
| `schema.py` | CATEGORY_ORDER, enums (imported by other scripts) |
| `audit_*.py` | Metadata, scientific names, duplicates, also known as, generic descriptions, translation sync, target language, toxicity vs care tips, toxicity unknown |
| `ensure_complementary_aka.py` | Ensure aka has complementary form (nickname→formal, formal→nickname) per locale |
| `add_common_alias_to_description.py` | Add formal names/aliases from commonExamples to description (`--dry-run` first) |
| `extract_by_category.py` | Extract category for audit sessions |
| `improve_plant_data.py` | Infer missing soilPhPreference, drainagePreference, plantLifeSpan; optimize open-ended `[xx, null]` lifespans to `[min, max]` (`--dry-run` first) |
| `reorganize_plants.py` | Apply REMOVE_IDS, CATEGORY_CHANGES |
| `translate_typenames.py` | Translate typeNames (EN→ZH or EN→ES via `--lang zh-Hans` / `--lang es`) |
| `optimize_duplicate_typenames.py` | Differentiate duplicate typeNames in each language file |
| `optimize_plants.py` | Comprehensive optimizer: merges, toxicity fixes, name corrections, new plants |

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
