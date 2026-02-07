# Changelog

All notable changes to the plantfolio-common-plants dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Changed

- **N:** 38 outdoor plants: `brightIndirect` → `outdoorFullSun` or `outdoorPartialSun` (prairie grasses, wildflowers).
- **O:** bonsai, lemon-cypress: `outdoorPartialSun` → `brightIndirect` (indoor houseplant semantics).
- **P:** Rot-prone succulents: `wellDraining` → `excellentDrainage` (lithops, echeveria, haworthia, string-of-pearls, string-of-bananas, sedum-morganianum).
- **Q:** 14 plants: `plantToxicity` unknown → known (ASPCA: alyssum, begonia, peony, salvia, clematis, honeysuckle, morning-glory, foxglove, castor-bean, lupine, hops, sweet-potato-vine).

### Added

- `scripts/apply_metadata_fixes.py` — apply N, O, P, Q fixes.
- `scripts/audit_metadata_completeness.py` — line-by-line metadata check.
- `plan/PLANT_PROPERTIES_AUDIT.md`, `plan/METADATA_LINE_BY_LINE_CHECK.md`.

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
