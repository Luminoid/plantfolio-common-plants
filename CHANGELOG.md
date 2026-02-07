# Changelog

All notable changes to the plantfolio-common-plants dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.2.0] - 2025-02-07

### Added

- **800 plants** across 28 categories (EN, ZH, ES).
- Care metadata: watering intervals, light preference, toxicity, categories.
- Dormancy notes for plants with null winterInterval.
- Scientific name corrections (Dracaena trifasciata, Curio, Alocasia × amazonica).
- Care tips for prairie/meadow plants and sprouts/microgreens.
- Schema validation for lightPreference, plantToxicity, category enums.
- Audit scripts: scientific names, duplicates, care tips, dormancy.

### Changed

- **plantToxicity (expert redesign):** Migrated to standard horticultural terminology: `safe`→`nonToxic`, `mildlyToxicToPets`→`mildlyToxic`, `toxicToPets`→`toxic`. Aligns with ASPCA/veterinary severity scale.
- **Scientific names:** Updated Senecio genus examples: `Senecio serpens`→`Curio repens (syn. Senecio serpens)`, `S. mandraliscae`→`Curio talinoides subsp. mandraliscae (syn. Senecio mandraliscae)` per Kew POWO.

## [1.1.0] - 2025-02-07

### Changed

- **Plant list cleanup:** Growing methods and redundant entries removed.

## [1.0.0] - 2025-02

### Added

- Initial dataset: first version of plant data.
