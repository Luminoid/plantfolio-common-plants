# plantfolio-common-plants – Agent context

Common plants dataset for Plantfolio Plus. 800 plants, 28 categories, EN/ES/ZH.

## Key files

- `source/common_plants_metadata.json` – Care metadata (intervals, light, toxicity, category)
- `source/common_plants_language_*.json` – Names, descriptions, care tips, commonExamples
- `docs/DATASET.md` – Schema, enums, categories
- `CHANGELOG.md` – Version history

## Commands

```bash
python3 scripts/release.py   # Build, validate, audit
```

## Rules

- Never run `git commit`
- plan/ is local; do not reference in commits or public docs
- Keep EN, ES, ZH-Hans in sync when changing plant data
