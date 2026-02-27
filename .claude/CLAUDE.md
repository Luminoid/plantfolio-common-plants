# plantfolio-common-plants — Claude Code Guide

> Common plants dataset for [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663)
> **Inherits cross-project rules from [workspace CLAUDE.md](../../.claude/CLAUDE.md).** This file contains data-specific rules only.

**873 plants**, 29 categories, EN/ES/ZH-Hans. Edit `source/` -> `release.py` builds and validates.

---

## Structure

```
source/    # Edit language + metadata JSON here
dist/      # Generated (DO NOT EDIT)
scripts/   # release.py, audit_quality.py, merge, sort_plants, validate, audit_*.py
docs/      # DATASET.md, AUDIT.md, RELEASE.md
```

---

## Key Files

| File | Purpose |
|------|---------|
| `source/common_plants_language_en.json` | English plant data (EDIT THIS) |
| `source/common_plants_language_es.json` | Spanish translations |
| `source/common_plants_language_zh-Hans.json` | Simplified Chinese translations |
| `source/common_plants_metadata.json` | Watering intervals, categories |
| `dist/*` | Generated merged files (DO NOT EDIT) |

**Use Glob**: `source/*.json` to find all source files
**Use Grep**: Search within source files for specific plants or fields

---

## Workflow

### 1. Editing Data
- **ONLY edit** files in `source/`
- **NEVER edit** files in `dist/` (auto-generated)
- Keep all three locales (EN/ES/ZH-Hans) in sync when adding/removing plants

### 2. Building & Validation
```bash
python3 scripts/release.py               # Before release (sorts, merges, validates)
python3 scripts/audit_quality.py         # Summary of all quality audits
```

### 3. Quality Audits
```bash
python3 scripts/extract_by_category.py "Category Name"  # Extract plants by category
python3 scripts/audit_*.py               # Various quality checks
```

---

## Rules

### Source Data Standards

**Plant Structure:**
```json
{
  "plantID": "unique-lowercase-dash-id",
  "plantName": "Display Name",
  "plantScientificName": "Genus species (Synonyms if applicable)",
  "plantToxicity": "nonToxic | unknown | mildlyToxic | toxic",
  "category": "english-category-key",
  ...
}
```

**Key conventions:**
- **plantToxicity**: Must be one of: `nonToxic`, `unknown`, `mildlyToxic`, `toxic`
- **Scientific names**: Accepted name first; synonyms in parentheses
- **plantID**: Lowercase, hyphenated, unique across all locales
- **Locales**: Keep EN, ES, ZH-Hans synchronized
- **Descriptions**: Must end with period. "Also known as:" capitalized, at start of description. Each plant unique — no placeholders or duplicates
- **aka rules**: No scientific names. No aka matching another plant's typeName. No duplicate aka within a locale. Category entries must not use specific entries' names as aka. No duplicate typeNames within a locale
- **commonExamples**: Use species-specific common names (not generic labels like "Microgreens")

### Script Standards

**Edit scripts (sort, improve):**
- Modify **source files** only
- Never touch `dist/` files

**Merge script:**
- Builds `dist/` from `source/`
- Creates merged files (one per locale)

**Validate script:**
- Validates generated `dist/` files
- Checks schema, required fields, toxicity values

---

## Cross-Project Alignment

**See workspace rule**: [.claude/rules/common-plants.RULE.md](../.claude/rules/common-plants.RULE.md)

When changing schema or scripts here, also update:
- `Plantfolio/Plantfolio/Resources/` (bundle files)
- `Plantfolio/Scripts/` (corresponding scripts)

**Structure must align** — field names, types, locale codes, output format
**Data content may diverge** — this is expected (no auto-sync needed)

---

## Common Tasks

### Add a new plant
1. Edit `source/common_plants_language_en.json`
2. Add equivalent entries in ES and ZH-Hans
3. Run `python3 scripts/release.py`
4. Verify in `dist/`

### Update toxicity info
1. Find plant in `source/common_plants_language_*.json` (use Grep)
2. Update `plantToxicity` field
3. Run `python3 scripts/release.py`

### Add new category
1. Update metadata in `source/common_plants_metadata.json`
2. Add translations in each language file's `_metadata.sorting.categories`
3. Run `python3 scripts/release.py`

---

## File Locations (for Glob/Grep)

- Source data: `source/common_plants_*.json`
- Generated data: `dist/common_plants_*.json`
- Scripts: `scripts/*.py`
- Documentation: `docs/*.md`

---

*Optimized for Claude Code • Last updated: 2026-02-17*
