# plantfolio-common-plants

Common plants data source for [Plantfolio](https://apps.apple.com/us/app/plantfolio-plus/id6757148663). Provides plant type suggestions with care information, watering intervals, and localization support.

## Contents

| File | Description |
|------|--------------|
| `common_plants.json` | English plant data |
| `common_plants_es.json` | Spanish plant data |
| `common_plants_zh-Hans.json` | Simplified Chinese plant data |
| `common_plants_metadata.json` | Metadata (watering intervals, categories, etc.) |

## Usage with Plantfolio

In Plantfolio Settings → Custom Common Plants Source, set the base URL to this data source. The URL must end with a slash, e.g.:

```
https://raw.githubusercontent.com/your-org/plantfolio-common-plants/main/
```

Or when served from a custom domain:

```
https://yoursite.com/plantfolio-common-plants/
```

Then tap **Download Now** to fetch the data.

## Data Format

- **Plants files** (`common_plants*.json`): Array of plant entries. First element contains `_metadata`; subsequent elements are plant objects with `id`, `typeName`, `description`, `careTips`, etc.
- **Metadata file** (`common_plants_metadata.json`): Object keyed by plant ID with `springInterval`, `summerInterval`, `fallInterval`, `winterInterval`, `category`, `lightPreference`, and other care attributes.

## Locales

Supported locale codes: `en`, `es`, `zh-Hans`. Add new locale files as `common_plants_{locale}.json` when expanding language support.
