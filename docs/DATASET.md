# Dataset Reference

**872 plants** across **29 categories** (EN, ZH, ES).
**Version:** 1.8.0 · See [CHANGELOG.md](../CHANGELOG.md) for history.

---

## Disclaimer

This dataset is for informational use only. It is not maintained by horticultural or botanical professionals and may contain errors or omissions. For plant identification, toxicity concerns, or specialized care, consult a qualified expert.

---

## 1. Scientific Nomenclature

Format `commonExamples` per botanical conventions: genus species; cultivar in single quotes; hybrid with ×; synonym in parentheses. Lead with accepted name (POWO/Kew).

**Key reclassifications:** *Sansevieria trifasciata* → *Dracaena trifasciata*; *S. cylindrica* → *Dracaena angolensis*; *Alocasia amazonica* → *A. × amazonica*; *Senecio serpens* → *Curio repens*; *S. mandraliscae* → *Curio talinoides* subsp. *mandraliscae*.

### commonExamples format

- **Base:** `Scientific name (alias1, alias2)`
- **Multiple species:** `Species A (alias A), Species B (alias B)`
- **Synonym prefix:** `Species (syn. OldName; alias1, alias2)` — aliases appear after `;`
- **Cultivar-only:** `Aglaonema 'Red Valentine'` — no parenthetical aliases
- **Sub-types only:** `Echeveria, Sedum, Graptopetalum` — no parenthetical content

### Description: "also known as"

- **typeName** = informal alias (e.g., "String of Pearls") or formal name (e.g., "Aglaonema")
- **description** = may include "also known as" to reveal the formal name or additional aliases
- **aka is optional.** When used, show the complementary form using **common names only**. Remove if aka only repeats commonExamples names without adding value.

| typeName is... | "also known as" shows |
|----------------|-----------------------|
| Alias / nickname (e.g., String of Pearls) | Alternate common name(s) from commonExamples |
| Formal (e.g., Aglaonema) | Aliases / nicknames (e.g., Chinese evergreen) |

**Rules:** Use only common-name aliases — **no scientific names** (Latin binomials, genus names, cultivars). **No subtypes** (e.g., Fruit Trees should not aka Apple; Cacti should not aka Barrel cactus). For category plants (multiple species in commonExamples), use only aliases from the first segment. Do not duplicate typeName. Remove aka if it only repeats commonExamples names. Run `ensure_complementary_aka.py` to add missing complementary; `audit_also_known_as.py --fix` to remove redundant aka.

| Locale | Phrase |
|--------|--------|
| EN | Also known as: {value}. |
| ES | También conocida como: {value}. |
| ZH | 也称：{value}。 |

---

## 2. Completed Milestones

| Milestone | Notes |
|-----------|-------|
| 810 plants | 28 categories, EN/ES/ZH |
| Reorganization | 12 duplicates removed; category reassignments |
| Hardiness zones | 91 outdoor plants (USDA zones) |
| Dormancy notes | Entries with null winterInterval |
| Scientific names | Dracaena, Curio, Alocasia × accepted |
| plantToxicity | nonToxic, mildlyToxic, toxic (expert schema) |
| Expert audit (Feb 2025) | Phase 1 metadata + Phase 2 language verified for all 28 categories; 46 plants had generic descriptions replaced |
| 872 plants (v1.8.0) | 106 added, 47 merged; 29 categories; 34 toxicity fixes; full EN/ES/ZH translation quality pass |

---

## 3. Category Structure

**Order:** Houseplants → Outdoor → Edibles → Farm/Sprouts → Bulbs → Specialty

| # | Category | Plant Count | Audit Focus |
|---|----------|-------------|-------------|
| 1 | Houseplants - Low Maintenance | 37 | Low-light tolerance, watering intervals, toxicity |
| 2 | Houseplants - Aroids | 59 | Light, humidity, drainage; toxic vs non-toxic |
| 3 | Houseplants - Ferns | 16 | High humidity, moisture-retentive soil, watering frequency |
| 4 | Houseplants - Palms | 12 | Light, humidity, drainage consistency |
| 5 | Houseplants - Succulents | 35 | Drainage (excellent/well), long intervals, low humidity |
| 6 | Houseplants - Cacti | 18 | Excellent drainage, long intervals, temperature ranges |
| 7 | Houseplants - Flowering | 34 | Blooming-specific needs, watering method |
| 8 | Houseplants - Prayer Plants | 15 | High humidity, moisture-retentive, bottom watering where applicable |
| 9 | Houseplants - Vines & Trailing | 23 | Light, watering, toxicity for pothos/philodendron |
| 10 | Houseplants - Ficus & Rubber Trees | 7 | Light, latex toxicity, humidity |
| 11 | Houseplants - Specialty | 29 | Bonsai, bromeliads, croton — special houseplant cases |
| 12 | Outdoor - Trees | 40 | hardinessZones, light, dormancy (null winterInterval) |
| 13 | Outdoor - Shrubs | 37 | hardinessZones, light, soil pH |
| 14 | Outdoor - Perennials | 74 | Largest; hardiness, light, watering intervals |
| 15 | Outdoor - Annuals | 38 | Short lifespan, frequent watering |
| 16 | Outdoor - Vines & Climbers | 17 | Light, support, hardiness |
| 17 | Outdoor - Groundcovers & Grasses | 24 | Light, drainage, hardiness |
| 18 | Vegetables - Leafy Greens | 25 | Watering, light, soil |
| 19 | Vegetables - Fruiting | 51 | Watering, light, temperature |
| 20 | Vegetables - Root & Bulb | 21 | Soil, drainage, harvesting |
| 21 | Fruits & Berries | 49 | hardinessZones, soil pH, pollination |
| 22 | Herbs | 36 | Light, watering, lifespan |
| 23 | Farm & Field Crops | 44 | Hardiness, soil, growing season |
| 24 | Sprouts & Microgreens | 43 | Very short intervals, moisture |
| 25 | Bulbs | 31 | Dormancy (null summer/fall), watering method |
| 26 | Specialty - Aquatic & Bog | 18 | null watering, waterloggingTolerant |
| 27 | Specialty - Carnivorous | 10 | null watering, acidic soil, immersion |
| 28 | Specialty - Epiphytes & Moss | 14 | misting/immersion, high humidity |
| 29 | Specialty - Alpine | 15 | Cold-tolerant, drainage, light |

**Rationale:** Generic types (succulents, cacti, aroids) kept as parent categories. Farm crops separate from garden vegetables. Sprouts & Microgreens separate for distinct care. Ficus & Rubber Trees split from Specialty for better organization.

---

## 4. Reorganization History

### Removed (12 duplicates)

| ID | Reason |
|----|--------|
| golden-pothos-office, marble-queen-office, philodendron-xanadu-office | Office variants |
| kentia-palm-office, areca-palm-office, bromeliad-office | Office variants |
| schefflera-arboricola | = schefflera-dwarf |
| butterfly-weed-native, yarrow-meadow | Duplicates |
| satin-pothos, silver-philodendron | = scindapsus |
| nephthytis | = arrowhead-plant (Syngonium, old name) |

### Category Reassignments

| ID | To |
|----|-----|
| rubber-plant-burgundy, croton-mammy | Houseplants - Specialty |

### Scripts

| Script | Purpose |
|--------|---------|
| `reorganize_plants.py` | Apply REMOVE_IDS, CATEGORY_CHANGES (edit in file first) |
| `optimize_duplicate_typenames.py` | Differentiate duplicate typeNames per locale (`--dry-run` then `--fix`) |
| `schema.py` | Shared constants (CATEGORY_ORDER, enums) — single source of truth |

---

## 5. Coverage Summary

- **Global:** Monstera, Pothos, Snake plant, ZZ, Peace lily, Philodendron, Calathea, Succulents, Cacti, etc.
- **China:** 绿萝, 虎皮兰, 发财树, 君子兰, 多肉, 芦荟, 丝瓜, 空心菜, etc.
- **US:** Tomatoes, Basil, Hostas, Hydrangeas, Roses, Lavender, etc.
- **Locales:** EN, ZH, ES with `commonExamples` including binomials where applicable.

---

## 6. typeName: Plural vs Singular

| Use | Examples |
|-----|----------|
| **Plural** | Category/generic types that encompass multiple species or cultivars |
| **Singular** | Specific species or cultivars |

**Plural:** Snake Plants, Peace Lilies, Spider Plants, Succulents, Ferns, Aroids, African Violets, Tomatoes, Beans, Grapes — entries describing a plant *type* or produce category.

**Singular:** Domino Peace Lily, Cylindrical Snake Plant, ZZ Plant, Golden Pothos, Swiss Cheese Plant — entries for a specific species or named cultivar.

**Latin genus names** (Pothos, Philodendron, Scindapsus, Lithops) remain singular when used as common names.

---

## 7. Decision Log

| Decision | Rationale |
|----------|-----------|
| Keep 29 categories | Balance of granularity vs. simplicity; Ficus split from Specialty |
| Farm & Field Crops separate | Distinct from garden vegetables |
| Sprouts & Microgreens separate | Fast-growing niche with distinct care |
| Generic types kept | Parent categories (succulents, cacti, aroids) aid UX |

---

## 8. Schema Reference

`validate_json.py` validates dist JSON structure. `schema.py` defines all enums, category order, intervals 1–90 or null, temperature and plantLifeSpan structure.

### Enums

| Field | Values | Notes |
|-------|--------|-------|
| **lightPreference** | outdoorFullSun, brightIndirect, lowIndirect, outdoorPartialSun, mediumIndirect, strongDirect, outdoorShade | Use outdoor\* for outdoor plants; indoor semantics for houseplants |
| **plantToxicity** | nonToxic, unknown, mildlyToxic, toxic | ASPCA-aligned severity |
| **humidityPreference** | low, medium, high, veryHigh | ~30–40%, 40–60%, 60–80%, 80%+ |
| **soilPhPreference** | acidic, neutral, alkaline, adaptable | pH &lt;6.5, 6.5–7.5, &gt;7.5, wide range |
| **drainagePreference** | excellentDrainage, wellDraining, moistureRetentive, waterloggingTolerant | |
| **wateringMethod** | topWatering, bottomWatering, immersion, misting | null for aquatic/carnivorous |

**Required:** category, spring/summer/fall/winterInterval (1–90 or null), temperaturePreference [min,max] °C, plantLifeSpan. **Optional:** hardinessZones for outdoor plants.

### Special Cases (null patterns)

| Plant Type | spring | summer | fall | winter | wateringMethod |
|------------|--------|--------|------|--------|----------------|
| Aquatic | null | null | null | null | null |
| Carnivorous | varies | varies | varies | null | null |
| Bulbs (dormant) | int | null | null | null | topWatering |
| Cyclamen/Gloxinia | int | null | null | int | bottomWatering |
| Outdoor (dormant) | int | int | int | null | topWatering |

### Quick Commands

```bash
python3 scripts/release.py                               # Build, validate, audit (before release)
python3 scripts/audit_quality.py                         # Run all quality audits (summary)
python3 scripts/merge_plant_data.py                      # Build dist/ from source
python3 scripts/validate_json.py                           # Validate dist JSON
python3 scripts/extract_by_category.py "Category Name"    # Extract category for audit session
python3 scripts/audit_metadata_completeness.py            # Full metadata audit (C1–C15, X1–X2)
python3 scripts/audit_toxicity_care_tips.py              # Toxicity vs care tips alignment
python3 -c "import json; m=json.load(open('source/common_plants_metadata.json')); print(len([k for k in m if k!='_metadata']))"  # Count plants
```
