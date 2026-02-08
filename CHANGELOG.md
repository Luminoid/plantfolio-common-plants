# Changelog

All notable changes to the plantfolio-common-plants dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.3.0] - 2025-02-07

### Changed

- **38 outdoor plants lightPreference:** `brightIndirect` → `outdoorFullSun` or `outdoorPartialSun` (prairie grasses, wildflowers).
- **Bonsai, lemon-cypress lightPreference:** `outdoorPartialSun` → `brightIndirect` (indoor houseplant semantics).
- **Rot-prone succulents drainagePreference:** `wellDraining` → `excellentDrainage` (lithops, echeveria, haworthia, string-of-pearls, string-of-bananas, sedum-morganianum).
- **14 plants plantToxicity:** unknown → known (ASPCA: alyssum, begonia, peony, salvia, clematis, honeysuckle, morning-glory, foxglove, castor-bean, lupine, hops, sweet-potato-vine).
- **Houseplant metadata audit:** 37 corrections for 270 houseplants: (1) Toxicity: `platycerium-bifurcatum`, `rhipsalis`, `rhipsalis-baccifera` toxic→nonToxic (ASPCA); 23 unknown→known for Dracaena, Philodendron, Sansevieria, Pothos, Peace lily, Ficus, etc. (2) Humidity: Alocasia & Anthurium cultivars medium→high (60–80% for tropical aroids).

## [1.2.0] - 2025-02-07

### Added

- **800 plants** across 28 categories (EN, ZH, ES).
- Care metadata: watering intervals, light preference, toxicity, categories.
- Dormancy notes for plants with null winterInterval.
- Scientific name corrections (Dracaena trifasciata, Curio, Alocasia × amazonica).
- Care tips for prairie/meadow plants and sprouts/microgreens.

### Changed

- **plantToxicity (expert redesign):** Migrated to standard horticultural terminology: `safe`→`nonToxic`, `mildlyToxicToPets`→`mildlyToxic`, `toxicToPets`→`toxic`. Aligns with ASPCA/veterinary severity scale.
- **Scientific names:** Updated Senecio genus examples: `Senecio serpens`→`Curio repens (syn. Senecio serpens)`, `S. mandraliscae`→`Curio talinoides subsp. mandraliscae (syn. Senecio mandraliscae)` per Kew POWO.

## [1.1.0] - 2025-02-07

### Changed

- **Plant list cleanup:** Growing methods and redundant entries removed.

## [1.0.0] - 2025-02

### Added

- Initial dataset: first version of plant data.
