# Audit Checklist Template

Reusable checklists for Phase 1 (metadata) and Phase 2 (language) audits. One category per session.

**Extract plants for a session:** `python3 scripts/extract_by_category.py "Category Name"`

---

## Phase 1: Metadata Per-Session Checklist

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

## Phase 2: Language Per-Session Checklist

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

## Notes for Future Audits

- **Generic descriptions to flag:** Replace with species-specific descriptions where possible.
  - EN: "Common plant for gardens, farms, or indoor spaces.", "Edible plant for kitchen gardens.", "Specialty plant for gardens or collections."
  - ES: "Planta especial para jardines o colecciones"
  - ZH: "园艺或收藏用特色植物"
- **Scientific names:** Follow docs/DATASET.md reclassifications (Dracaena, Curio, Alocasia ×).
- **Consistency:** Metadata and language must align — e.g., if metadata says "high humidity," careTips should mention humidity.
- **Toxicity:** Use [ASPCA Toxic and Non-Toxic Plants](https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants) as primary reference. Reduce unknown where possible.
- **Humidity:** Alocasia cultivars and foliage Anthuriums (velvet): high (60–80%). Generic alocasias have high; cultivars should match.
- **Temperature:** Tropical aroids: min 16–18°C, not 10°C (dangerous). Prefer [16, 29] or [18, 27].
- **Light:** Pothos variants: brightIndirect for consistency with base pothos (they tolerate low but grow better in bright). Outdoor plants: use outdoorFullSun, outdoorPartialSun, or outdoorShade — not brightIndirect (indoor semantics).
- **Drainage:** Succulents/cacti: excellentDrainage for rot-prone species (lithops, echeveria, haworthia, string-of-pearls, etc.).
- **Watering method:** null for aquatic/carnivorous; immersion for epiphytes; bottom for lithops, african-violets, cyclamen, gloxinia, rex-begonias; misting for air-plants, epiphytes, mosses.
- **Humidity:** Ferns high/veryHigh; prayer plants high; succulents/cacti low/medium.
