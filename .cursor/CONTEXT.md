# plantfolio-common-plants

> [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663) dataset. Rules: [.cursor/rules/](.cursor/rules/)

**873 plants**, 29 categories, EN/ES/ZH-Hans. Edit `source/` → `release.py` builds and validates.

## Structure

```
source/    # Edit language + metadata JSON
dist/      # Generated (do not edit)
scripts/   # release.py, audit_quality.py, merge, sort_plants, validate, audit_*.py
docs/      # DATASET.md, AUDIT.md, RELEASE.md
```

## Commands

```bash
python3 scripts/release.py               # Before release
python3 scripts/audit_quality.py         # Summary of all quality audits
python3 scripts/extract_by_category.py "Category Name"  # Audit session
```

## Conventions

- **plantToxicity:** nonToxic, unknown, mildlyToxic, toxic
- **Scientific names:** Accepted first; synonyms in parentheses
- **Locales:** Keep EN, ES, ZH-Hans in sync
