# Audit Guide

Unified procedures for category audits, metadata validation, naming overlap, and toxicity. One category per session.

---

## 1. Extract & run

```bash
python3 scripts/extract_by_category.py "Category Name" -o path/to/extract.json
# After edits: python3 scripts/release.py
```

**Suggested order (by audit focus + risk):**

| Priority | Category | Focus | Effort |
|----------|----------|-------|--------|
| 1 | Houseplants - Aroids | Light, humidity, toxicity | High |
| 2 | Houseplants - Prayer Plants | Humidity, watering method | Medium |
| 3 | Houseplants - Ferns | High humidity, moisture | Medium |
| 4 | Houseplants - Succulents | Drainage, intervals | Medium |
| 5 | Houseplants - Vines & Trailing | Light, toxicity | Medium |
| 6 | Outdoor - Perennials | Largest; hardiness, light | High |
| 7 | Outdoor - Trees | hardinessZones, dormancy | Medium |
| 8 | Outdoor - Shrubs | hardinessZones, soil pH | Medium |
| ... | See docs/DATASET.md | Per category | ... |

---

## 2. Phase 1: Metadata checklist

```
## Category: [Category Name] — [N] plants

### Pre-extract
- [ ] Run: python3 scripts/extract_by_category.py "[Category Name]"
- [ ] Open relevant botany references for species in this category

### Per-plant verification (one plant at a time)
For each plant ID:
- [ ] springInterval: correct for species? (1–90 or null)
- [ ] summerInterval: correct? (null for dormant bulbs)
- [ ] fallInterval: correct?
- [ ] winterInterval: correct? (null for outdoor dormancy)
- [ ] lightPreference: indoor vs outdoor semantics correct?
- [ ] humidityPreference: matches species needs?
- [ ] temperaturePreference: min ≤ max, realistic range?
- [ ] plantToxicity: accurate? (reduce unknown if possible)
- [ ] soilPhPreference: correct for species?
- [ ] drainagePreference: correct for root type?
- [ ] wateringMethod: correct? (null for aquatic/carnivorous)
- [ ] plantLifeSpan: realistic?
- [ ] category: correct?
- [ ] hardinessZones (if outdoor): accurate USDA zones?

### Issues log
| Plant ID | Field | Current | Corrected | Notes |
|----------|-------|---------|-----------|-------|
| ... | ... | ... | ... | ... |

### Post-session
- [ ] Apply corrections to common_plants_metadata.json
- [ ] Run: python3 scripts/validate_json.py --check-schema
- [ ] Run: python3 scripts/audit_metadata_completeness.py
```

---

## 3. Phase 2: Language checklist

```
## Category: [Category Name] — [N] plants

### Pre-extract
- [ ] Extract language entries for this category from all 3 locale files
- [ ] Cross-reference with metadata for this category (consistency check)

### Per-plant verification (one plant at a time)

#### EN (source of truth)
For each plant ID:
- [ ] typeName: Correct common name?
- [ ] description: 
  - [ ] Accurate and species-specific? (flag generic descriptions — see Notes below)
  - [ ] No factual errors?
  - [ ] Informative for users?
- [ ] commonExamples: 
  - [ ] Scientific names correct? (Genus species, cultivar in 'quotes')
  - [ ] Follow docs/DATASET.md nomenclature (Dracaena not Sansevieria, etc.)?
  - [ ] Common names in parentheses where helpful?
- [ ] careTips: 
  - [ ] Matches metadata (watering interval, light, humidity)?
  - [ ] Actionable and specific?
  - [ ] No contradictions with metadata?
  - [ ] Covers: water, light, humidity, fertilizer, repot, pests?

#### ES & ZH (translations)
- [ ] typeName: Correct translation?
- [ ] description: Accurate translation of EN; no mistranslations?
- [ ] commonExamples: Scientific names unchanged; common names translated?
- [ ] careTips: Accurate translation; care advice preserved?

### Issues log
| Plant ID | Locale | Field | Issue | Correction |
|----------|--------|-------|-------|------------|
| ... | ... | ... | ... | ... |

### Post-session
- [ ] Apply corrections to common_plants_language_en.json
- [ ] Apply corrections to common_plants_language_es.json
- [ ] Apply corrections to common_plants_language_zh-Hans.json
- [ ] Run: python3 scripts/merge_plant_data.py
- [ ] Run: python3 scripts/validate_json.py --check-schema --check-structure
```

---

## 4. Metadata schema (C1–C15)

Ensures every plant has complete, valid metadata. Run: `python3 scripts/audit_metadata_completeness.py`

### Required fields (13)

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

### Check matrix

| ID | Check | Pass Condition |
|----|-------|----------------|
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

### Cross-reference

- **X1:** Every plant ID in metadata exists in language files
- **X2:** Every plant ID in language files exists in metadata

### Usage

```bash
python3 scripts/audit_metadata_completeness.py           # Full audit
python3 scripts/audit_metadata_completeness.py --verbose # Per-plant pass/fail
python3 scripts/audit_metadata_completeness.py --output report.txt
```

---

## 5. Naming overlap

Run `python3 scripts/release.py` or `python3 scripts/audit_duplicates.py` to see overlap data.

### Source of overlap data

1. **Potential genus/species overlap** — IDs where one is a prefix of another (e.g. `pothos` vs `pothos-cebu-blue`)
2. **Similar typeNames** — One typeName is exact substring of another (e.g. `'Pothos'` vs `'Cebu Blue Pothos'`)
3. **Known pairs to review** — Hardcoded in `audit_duplicates.py` (rhipsalis, philodendron-heartleaf/brasil)

### Review strategy

| Type | Example | Action |
|------|---------|--------|
| Parent + cultivar | `pothos` + `pothos-cebu-blue` | Usually OK — keep both |
| Generic + specific | `aglaonema` + `aglaonema-pink-star` | Usually OK — generic is parent |
| Duplicate risk | `rhipsalis` vs `rhipsalis-baccifera` | Review — may need consolidation |
| Confusing | `arrowhead` vs `arrowhead-plant` | Review — may need rename/clarify |

### Workflow

1. **Export:** `python3 scripts/audit_duplicates.py --output overlap_report.json` or `2>&1 | tee overlap_report.txt`
2. **Categorize:** Mark each pair as Keep / Rename / Consolidate / Investigate
3. **Rename:** Update `typeName` in language files to disambiguate
4. **Consolidate:** Only if true duplicates — use `scripts/reorganize_plants.py` (REMOVE_IDS) after confirming
5. **Re-run audit** to confirm no new issues

### Known pairs

| Pair | Recommendation |
|------|----------------|
| rhipsalis / rhipsalis-baccifera | Both *R. baccifera* — consider consolidating or clarifying scope |
| philodendron-heartleaf / philodendron-brasil | Both *P. hederaceum* cultivars — keep both; ensure descriptions distinguish |

---

## 6. Toxicity

Procedures for reducing `plantToxicity: "unknown"` via ASPCA and other sources.

### References

- **Primary:** [ASPCA Toxic and Non-Toxic Plants](https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants)
- **Secondary:** [Pet Poison Helpline](https://www.petpoisonhelpline.com/), university extension sites

### Workflow per plant

1. **Identify:** Get scientific name from `commonExamples` in language file
2. **Search ASPCA:** Look up genus/species
3. **Classify:** `nonToxic` | `mildlyToxic` | `toxic` | keep `unknown` if no data
4. **Update:** Edit `source/common_plants_metadata.json` → `plantToxicity` field
5. **Batch:** Process by category to reuse context

### Batch workflow

```bash
# List unknown plants by category (or use: python3 scripts/audit_toxicity_unknown.py --category "Outdoor - Perennials")
python3 -c "
import json
m = json.load(open('source/common_plants_metadata.json'))
unknown = [(pid, d.get('category','')) for pid, d in m.items() 
           if pid != '_metadata' and isinstance(d, dict) and d.get('plantToxicity') == 'unknown']
for pid, cat in unknown:
    if cat == 'Outdoor - Perennials': print(pid)
"

# Get commonExamples (from language file)
python3 -c "
import json
lang = json.load(open('source/common_plants_language_en.json'))
ids = ['example-id1', 'example-id2']  # replace with IDs from above
for e in lang:
    if 'id' in e and e['id'] in ids:
        print(e['id'], e.get('commonExamples',''))
"
```

### Care tips phrasing (EN/ES/ZH)

| Severity | EN | ES | ZH |
|----------|----|----|-----|
| toxic | Toxic to pets | Tóxico para mascotas | 对宠物有毒 |
| mildlyToxic | Mildly toxic to pets—may cause GI upset | Ligeramente tóxico para mascotas—puede causar malestar gastrointestinal | 对宠物轻微有毒，可能引起肠胃不适 |

### Generic categories

Generic entries (bonsai, succulents, deciduous-trees, grasses, etc.) should remain `unknown` — they cover many species with different toxicity profiles.

---

## 7. Notes for future audits

### Content improvement (descriptions & care tips)

**Care tips structure (order):** Watering → Light → Humidity → Fertilizing → Repotting → Maintenance → Special notes (toxicity, dormancy, pests).

**Quality checklist per plant:** Description plant-specific; 15–80 words; care tips align with metadata; all 3 locales updated.

### General

- **Generic descriptions to flag:** Replace with species-specific descriptions where possible.
  - EN: "Common plant for gardens, farms, or indoor spaces.", "Edible plant for kitchen gardens.", "Specialty plant for gardens or collections."
  - ES: "Planta especial para jardines o colecciones"
  - ZH: "园艺或收藏用特色植物"
- **Scientific names:** Follow docs/DATASET.md reclassifications (Dracaena, Curio, Alocasia ×).
- **Consistency:** Metadata and language must align — e.g., if metadata says "high humidity," careTips should mention humidity.
- **Toxicity:** Use ASPCA as primary reference. See section 6 above.
- **Humidity:** Alocasia cultivars and foliage Anthuriums (velvet): high (60–80%). Generic alocasias have high; cultivars should match.
- **Temperature:** Tropical aroids: min 16–18°C, not 10°C (dangerous). Prefer [16, 29] or [18, 27].
- **Light:** Pothos variants: brightIndirect. Outdoor plants: use outdoorFullSun, outdoorPartialSun, or outdoorShade — not brightIndirect (indoor semantics).
- **Drainage:** Succulents/cacti: excellentDrainage for rot-prone species (lithops, echeveria, haworthia, string-of-pearls, etc.).
- **Watering method:** null for aquatic/carnivorous; immersion for epiphytes; bottom for lithops, african-violets, cyclamen, gloxinia, rex-begonias; misting for air-plants, epiphytes, mosses.
- **Humidity:** Ferns high/veryHigh; prayer plants high; succulents/cacti low/medium.
