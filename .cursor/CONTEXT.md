# plantfolio-common-plants — Cursor Context

> For AI assistants. Enforceable rules: [.cursor/rules/](.cursor/rules/)

---

## Overview

Common plants dataset for [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663). ~800 plants, 28 categories, EN/ES/ZH-Hans. Edit `source/`; merge builds `dist/`; release validates and audits.

## Structure

```
plantfolio-common-plants/
├── source/    # Edit: common_plants_language_*.json, common_plants_metadata.json
├── dist/      # Generated (do not edit)
├── scripts/   # release.py, merge_plant_data.py, validate_json.py, audit_*.py, sort_plants.py, extract_by_category.py, reorganize_plants.py
├── docs/      # DATASET.md (schema), audit docs
└── .cursor/
    ├── CONTEXT.md
    └── rules/  # project.mdc, scripts.mdc, source-data.mdc
```

## Key Files

| File | Purpose |
|------|---------|
| `source/common_plants_metadata.json` | Care metadata (intervals, light, toxicity, category) |
| `source/common_plants_language_*.json` | Names, descriptions, care tips, commonExamples |
| `docs/DATASET.md` | Schema, enums, categories |

## Commands

```bash
python3 scripts/release.py               # Build, validate, audit (before release)
python3 scripts/merge_plant_data.py      # Build dist/ from source
python3 scripts/validate_json.py         # Schema validation (--check-schema --check-structure)
python3 scripts/extract_by_category.py "Category Name"  # Extract for audit session
python3 scripts/audit_metadata_completeness.py        # Full metadata audit
```

## Conventions

- **plantToxicity**: `nonToxic`, `unknown`, `mildlyToxic`, `toxic`
- **Scientific names**: Accepted name first; synonyms in parentheses
- **Locales**: Keep EN, ES, ZH-Hans in sync
- **plan/**: Local only—do not reference in commits or public docs
