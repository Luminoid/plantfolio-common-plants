# Metadata Audit Specification

Ensures every plant has complete, valid metadata. Run: `python3 scripts/audit_metadata_completeness.py`

---

## Required Fields (13)

Each plant in `common_plants_metadata.json` must have:

| Field | Type | Constraints |
|-------|------|-------------|
| springInterval, summerInterval, fallInterval, winterInterval | int or null | 1–90, or null (dormant/aquatic) |
| lightPreference | string | See docs/DATASET.md enums |
| humidityPreference | string | low, medium, high, veryHigh |
| temperaturePreference | [min, max] | °C, -10 to 45, min ≤ max |
| plantToxicity | string | nonToxic, mildlyToxic, toxic, unknown |
| soilPhPreference | string | acidic, neutral, alkaline, adaptable |
| drainagePreference | string | excellentDrainage, wellDraining, moistureRetentive, waterloggingTolerant |
| wateringMethod | string or null | topWatering, bottomWatering, misting, immersion, or null |
| plantLifeSpan | [min, max] | min ≥ 0; max is int or null |
| category | string | One of 28 valid categories |

**Optional:** `hardinessZones` [min, max] — outdoor plants only; USDA zones 1–11.

---

## Check Matrix (C1–C15)

| ID | Check | Pass Condition |
|----|-------|-----------------|
| C1 | Required fields | All 13 present |
| C2–C5 | spring/summer/fall/winterInterval | int 1–90 or null |
| C6 | lightPreference | Valid enum |
| C7 | humidityPreference | Valid enum |
| C8 | temperaturePreference | [min,max], min ≤ max, -10 to 45 |
| C9 | plantToxicity | Valid enum |
| C10 | soilPhPreference | Valid enum |
| C11 | drainagePreference | Valid enum |
| C12 | wateringMethod | Valid enum or null |
| C13 | plantLifeSpan | [min,max], min ≥ 0 |
| C14 | category | Valid category |
| C15 | hardinessZones (if present) | [min,max] 1–11, outdoor only |

---

## Cross-Reference

- **X1:** Every plant ID in metadata exists in language files
- **X2:** Every plant ID in language files exists in metadata

---

## Usage

```bash
python3 scripts/audit_metadata_completeness.py           # Full audit
python3 scripts/audit_metadata_completeness.py --verbose # Per-plant pass/fail
python3 scripts/audit_metadata_completeness.py --output report.txt
```

See docs/DATASET.md for schema, enums, and special cases (null patterns).
