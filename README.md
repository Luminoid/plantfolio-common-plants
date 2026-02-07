# plantfolio-common-plants

Common plants data source for [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663). Provides plant type suggestions with care information, watering intervals, and localization support.

**800 plants** across 28 categories (EN, ZH, ES). See `docs/DATASET.md` for structure and `CHANGELOG.md` for version history.

**Source + generated**: This repo holds **source** (`source/`), **scripts** (`scripts/`), and **generated** (`dist/`) files. Edit source directly; merge builds dist; release validates and audits.

## Contents

**Source** (`source/`):

| File | Description |
|------|--------------|
| `source/common_plants_language_en.json` | English plant data |
| `source/common_plants_language_es.json` | Spanish plant data |
| `source/common_plants_language_zh-Hans.json` | Simplified Chinese plant data |
| `source/common_plants_metadata.json` | Metadata (watering intervals, categories, hardinessZones for outdoor plants, etc.) |

**Scripts** (`scripts/`):

| Script | Purpose |
|--------|---------|
| `release.py` | **Before release:** build dist, validate, run audits |
| `merge_plant_data.py` | Build dist/ from source |
| `validate_json.py` | Validate structure and schema |
| `audit_scientific_names.py` | Check commonExamples for accepted scientific names |
| `audit_duplicates.py` | Check for genus/species overlap, similar typeNames |
| `reorganize_plants.py` | Apply removals/category changes (edit REMOVE_IDS, CATEGORY_CHANGES) |
| `improve_care_tips.py` | Apply care tips for new plants with generic template |
| `add_dormancy_notes.py` | Add dormancy notes for new plants with null winterInterval |

**Generated** (`dist/`): `common_plants.json`, `common_plants_es.json`, `common_plants_zh-Hans.json` (merged; no metadata file). Before release:

```bash
python3 scripts/release.py
```

## Usage with Plantfolio

In Plantfolio Settings → **Custom Common Plants Source**, enter a URL and tap **Download Now** to fetch the data.

### Default source (this repo)

**Base folder URL** (recommended): The app appends the locale filename automatically.

```
https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/
```

**Full file URLs** (per locale):

| Locale | URL |
|--------|-----|
| English | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants.json` |
| Spanish | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants_es.json` |
| Chinese (Simplified) | `https://raw.githubusercontent.com/Luminoid/plantfolio-common-plants/main/dist/common_plants_zh-Hans.json` |

### Custom fork or hosting

- **Base folder**: URL ending with `/` (e.g. `https://raw.githubusercontent.com/your-org/plantfolio-common-plants/main/dist/` or `https://yoursite.com/plantfolio-common-plants/dist/`). The app appends the filename for the current language.
- **Full file**: Direct URL to a `.json` file (e.g. `https://yoursite.com/common_plants_es.json`). Use as-is; no filename is appended.

## Data Format

**Source** (`source/`): Language files are arrays; metadata is a separate object keyed by plant ID. Edit these for maintenance.

**Output** (`dist/`): Each `common_plants*.json` is an array of plant entries with all fields merged—language (`typeName`, `description`, `careTips`) plus metadata (`springInterval`, `category`, `lightPreference`, etc.). Category is translated from the language file's `_metadata.sorting.categories` header.

## Locales

Supported locale codes: `en`, `es`, `zh-Hans`. Add new locale files as `common_plants_{locale}.json` when expanding language support.

## Docs

| File | Description |
|------|--------------|
| `docs/DATASET.md` | Category structure, schema reference, coverage summary |
| `CHANGELOG.md` | Version history and breaking changes |
