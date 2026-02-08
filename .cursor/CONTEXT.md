# plantfolio-common-plants

> [Plantfolio Plus](https://apps.apple.com/us/app/plantfolio-plus/id6757148663) dataset. Rules: [.cursor/rules/](.cursor/rules/)

**800 plants**, 28 categories, EN/ES/ZH-Hans. Edit `source/` → `release.py` builds and validates.

## Structure

```
source/    # Edit language + metadata JSON
dist/      # Generated (do not edit)
scripts/   # release.py, merge, validate, schema.py, audit_*.py, add_common_alias_to_description.py
docs/      # DATASET.md, AUDIT.md, RELEASE.md
```

## Commands

```bash
python3 scripts/release.py               # Before release
python3 scripts/extract_by_category.py "Category Name"  # Audit session
```

## Conventions

- **plantToxicity:** nonToxic, unknown, mildlyToxic, toxic
- **Scientific names:** Accepted first; synonyms in parentheses
- **Locales:** Keep EN, ES, ZH-Hans in sync
