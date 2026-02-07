# Dataset Reference

**800 plants** across **28 categories** (EN, ZH, ES).  
**Version:** 1.2.0 · See [CHANGELOG.md](../CHANGELOG.md) for history.

---

## 1. Scientific Nomenclature

Format `commonExamples` per botanical conventions: genus species; cultivar in single quotes; hybrid with ×; synonym in parentheses. Lead with accepted name (POWO/Kew).

**Key reclassifications:** *Sansevieria trifasciata* → *Dracaena trifasciata*; *S. cylindrica* → *Dracaena angolensis*; *Alocasia amazonica* → *A. × amazonica*; *Senecio serpens* → *Curio repens*; *S. mandraliscae* → *Curio talinoides* subsp. *mandraliscae*.

---

## 2. Completed Milestones

| Milestone | Notes |
|-----------|-------|
| 800 plants | 28 categories, EN/ES/ZH |
| Reorganization | 12 duplicates removed; category reassignments |
| Hardiness zones | 91 outdoor plants (USDA zones) |
| Dormancy notes | Entries with null winterInterval |
| Scientific names | Dracaena, Curio, Alocasia × accepted |
| plantToxicity | nonToxic, mildlyToxic, toxic (expert schema) |

---

## 3. Category Structure

**Order:** Houseplants → Outdoor → Edibles → Farm/Sprouts → Bulbs → Specialty

| # | Category |
|---|----------|
| 1–10 | Houseplants - Low Maintenance, Aroids, Ferns, Palms, Succulents, Cacti, Flowering, Prayer Plants, Vines & Trailing, Specialty |
| 11–16 | Outdoor - Trees, Shrubs, Perennials, Annuals, Vines & Climbers, Groundcovers & Grasses |
| 17–21 | Vegetables - Leafy Greens, Fruiting, Root & Bulb; Fruits & Berries; Herbs |
| 22–23 | Farm & Field Crops; Sprouts & Microgreens |
| 24–28 | Bulbs; Specialty - Aquatic & Bog, Carnivorous, Epiphytes & Moss, Alpine |

**Rationale:** Generic types (succulents, cacti, aroids) kept as parent categories. Farm crops separate from garden vegetables. Sprouts & Microgreens separate for distinct care.

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

### Script

`python3 scripts/reorganize_plants.py` — applies removals and category changes. Run only when modifying REMOVE_IDS or CATEGORY_CHANGES.

---

## 5. Coverage Summary

- **Global:** Monstera, Pothos, Snake plant, ZZ, Peace lily, Philodendron, Calathea, Succulents, Cacti, etc.
- **China:** 绿萝, 虎皮兰, 发财树, 君子兰, 多肉, 芦荟, 丝瓜, 空心菜, etc.
- **US:** Tomatoes, Basil, Hostas, Hydrangeas, Roses, Lavender, etc.
- **Locales:** EN, ZH, ES with `commonExamples` including binomials where applicable.

---

## 6. Decision Log

| Decision | Rationale |
|----------|-----------|
| Keep 28 categories | Balance of granularity vs. simplicity |
| Farm & Field Crops separate | Distinct from garden vegetables |
| Sprouts & Microgreens separate | Fast-growing niche with distinct care |
| Generic types kept | Parent categories (succulents, cacti, aroids) aid UX |

---

## 7. Schema Reference

`validate_json.py --check-schema` validates: all enums, category required, intervals 1–90 or null, temperature and plantLifeSpan structure.

### Enums

| Field | Values |
|-------|--------|
| **lightPreference** | outdoorFullSun, brightIndirect, lowIndirect, outdoorPartialSun, mediumIndirect, strongDirect, outdoorShade, gentleDirect, deepShade |
| **plantToxicity** | nonToxic, unknown, mildlyToxic, toxic |
| **humidityPreference** | low, medium, high, veryHigh |
| **soilPhPreference** | acidic, neutral, alkaline, adaptable |
| **drainagePreference** | excellentDrainage, wellDraining, moistureRetentive, waterloggingTolerant |
| **wateringMethod** | topWatering, bottomWatering, immersion, misting (null for aquatic/carnivorous) |

### Quick Commands

```bash
python3 scripts/release.py   # Build, validate, audit
python3 -c "import json; m=json.load(open('source/common_plants_metadata.json')); print(len(m))"  # Count plants
```
