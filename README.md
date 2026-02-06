# plantfolio-common-plants

Common plants data source for [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663). Provides plant type suggestions with care information, watering intervals, and localization support.

**Source + generated**: This repo holds **source** (`source/`), **scripts** (`scripts/`), and **generated** (`dist/`) files. Edit scripts modify source; merge builds dist; validate checks dist.

## Contents

**Source** (`source/`):

| File | Description |
|------|--------------|
| `source/common_plants_language_en.json` | English plant data |
| `source/common_plants_language_es.json` | Spanish plant data |
| `source/common_plants_language_zh-Hans.json` | Simplified Chinese plant data |
| `source/common_plants_metadata.json` | Metadata (watering intervals, categories, etc.) |

**Scripts** (`scripts/`):

| Script | Purpose |
|--------|---------|
| `scripts/merge_plant_data.py` | Build dist/ from source |
| `scripts/validate_json.py` | Validate generated files in dist/ |

**Generated** (`dist/`): `common_plants.json`, `common_plants_es.json`, `common_plants_zh-Hans.json` (merged; no metadata file). Build with:

```bash
python3 scripts/merge_plant_data.py
python3 scripts/validate_json.py --check-structure
```

## Usage with Plantfolio

In Plantfolio Settings → Custom Common Plants Source, set the base URL to the **dist/** folder. The URL must end with a slash, e.g.:

```
https://raw.githubusercontent.com/your-org/plantfolio-common-plants/main/dist/
```

Or when served from a custom domain:

```
https://yoursite.com/plantfolio-common-plants/dist/
```

Then tap **Download Now** to fetch the data.

## Data Format

**Source** (`source/`): Language files are arrays; metadata is a separate object keyed by plant ID. Edit these for maintenance.

**Output** (`dist/`): Each `common_plants*.json` is an array of plant entries with all fields merged—language (`typeName`, `description`, `careTips`) plus metadata (`springInterval`, `category`, `lightPreference`, etc.).

## Locales

Supported locale codes: `en`, `es`, `zh-Hans`. Add new locale files as `common_plants_{locale}.json` when expanding language support.
