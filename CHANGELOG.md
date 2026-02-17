# Changelog

Plant list changes only (data changes to plants, metadata, translations). Not for scripts, docs, or tooling.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [1.8.0] - 2026-02-17

### Added

- **65 new plants** (810 → 864): Joshua Tree, Giant Sequoia, Coast Redwood, Bristlecone Pine, Baobab, Banyan, Ginkgo, Plumeria, Bougainvillea, Wisteria, Hellebore, Star Jasmine, Witch Hazel, Mountain Laurel, Medinilla, Ficus Audrey, Calathea Musaica, Philodendron Florida Ghost, Cacao, Arabica Coffee, Hemp, Jackfruit, Durian, Rambutan, Giant Water Lily, Cephalotus, Paphiopedilum, and more. Full metadata + EN/ES/ZH translations for all.
- **2 split entries:** Mexican Hat (Ratibida columnifera) and Deer Fern (Blechnum spicant) — separated from entries that conflated two different genera.

### Fixed

- **Toxicity (pet safety):** 7 plants corrected to nonToxic (portulacaria-afra, string-of-hearts, phoenix-roebelenii, hibiscus-tropical, pteris, pteris-cretica, gaillardia). 7 plants corrected to mildlyToxic (scindapsus ×3, tradescantia ×4) for consistency with calcium-oxalate aroid classification.
- **Scientific names:** 11 corrections — Monstera sp. 'Peru', Salvia yangii (was "may be reclassified"), Brassica rapa var. nipposinica (mizuna), Lilium Asiatic/Oriental hybrid divisions, Zantedeschia rehmannii, boysenberry binomial, Goeppertia references added to calathea-zebrina and calathea-white-star, Dracaena reflexa 'Song of India' cultivar name, gasteria family description.
- **Care tips:** Removed incorrect "prairie native" label from 6 European wildflowers (field-scabious, meadow-cranesbill, oxeye-daisy, great-mullein, red-clover, vipers-bugloss). Corrected "drought tolerant" to "prefers moist soil" for 4 moisture-loving species (joe-pye-weed, ironweed, swamp-milkweed, new-england-aster). Added missing toxicity warning to foxglove, mildew guidance to phlox, ant note to peony, pruning groups to clematis, frost-tender note to lantana. Fixed lithops growth period description.
- **Metadata:** crassula-ovata-minor watering 7→14 days; english-ivy temperature [16,21]→[10,27]; cast-iron-plant temperature [18,24]→[7,27]; bird-of-paradise humidity high→medium.
- **TypeNames:** Fixed echinopsis "Sea Urchin Cactus"→"Easter Lily Cactus"; blechnum "Deer Fern"→"Dwarf Tree Fern"; removed invalid "Also known as" from category entries (warm-season-annuals, root-vegetables, flowering-shrubs); fixed beet-greens, dandelion-greens, currant, catnip, sweet-potato-vine naming issues.

### Changed

- **Merged 11 duplicates** into their more common names: burros-tail ← sedum-morganianum, string-of-dolphins ← senecio-peregrinus, maranta-prayer-plant ← maranta-leuconeura, gloxinia ← sinningia, joe-pye-weed ← sweet-joe-pye, string-of-turtles ← peperomia-prostrata, switchgrass-prairie ← panicum, luffa ← loofah, parlor-palm ← neanthe-bella-palm, philodendron-heartleaf ← philodendron-scandens + philodendron-hederaceum-scandal. Alternate names preserved as "Also known as" in descriptions.
- **Renamed 5 IDs:** common-viper → vipers-bugloss, alocasia-mahorani → alocasia-maharani (spelling fix), purple-cone-prairie → prairie-coneflower, chinese-evergreen-maria → aglaonema-maria, chinese-evergreen-silver → aglaonema-silver-bay (Aglaonema naming standardized).
- **Differentiated 5 duplicate typeNames** across locales: coffee-arabica → "Arabica Coffee", lavender-herb → "Culinary Lavender", fennel-herb → "Herb Fennel", vanilla-crop → "Vanilla (Crop)", anthurium-flamingo ZH → "火烈鸟花".

## [1.7.3] - 2026-02-09

### Fixed

- **plantLifeSpan:** Enforce min ≤ max in schema validation; corrected 29 Farm & Field Crops from `[2, 1]` to `[1, 2]` years.

## [1.7.2] - 2026-02-09

### Changed

- **Metadata:** Dist output now includes `_metadata` (version, totalPlants, sorting) in merged JSON for custom URL consumers.

## [1.7.1] - 2026-02-09

### Changed

- **_metadata.plantCount:** Added `plantCount: 810` to metadata.

## [1.7.0] - 2026-02-09

### Changed

- **plantLifeSpan:** Replaced 602 open-ended `[xx, null]` lifespans with concrete `[min, max]` ranges; all 810 plants now have both values (species-level inference across 28 categories).
- **Watering:** Desert cacti (5 species) corrected to less frequent intervals (14/14/21/30).
- **Tree lifespans:** 9 trees corrected from [3, null] to accurate min/max values.
- **Toxicity:** Standardized aroids (Pothos, Monstera, Philodendron) → mildlyToxic; Begonia and Spathiphyllum Domino → toxic.
- **Drainage:** 7 carnivorous/bog species corrected from excellentDrainage → moistureRetentive.
- **Light:** 21 corrections (snake plants, variegated houseplants → brightIndirect; desert cacti → strongDirect; Haworthia Cooperi → brightIndirect).
- **Also known as:** Removed 28 conflicting aka entries; resolved all duplicate/conflicting akas across EN/ES/ZH (10 EN, 14 ES, 34 ZH).
- **Descriptions:** Fixed corrupted repeated text (20 EN + 19 ES); replaced 12 EN + 9 ZH placeholder perennials text with unique descriptions; added trailing periods and fixed formatting (EN/ES/ZH).
- **ES typeNames:** Differentiated 2 duplicates (clover-red, mung-bean-field).

## [1.6.0] - 2025-02-08

### Changed

- **Descriptions:** Removed redundant "also known as" blocks (sedum-morganianum, cyclamen-bulb, neanthe-bella-palm, floating-heart).
- **Descriptions:** Removed scientific synonyms from AKA blocks (string-of-pearls, peperomia-watermelon, string-of-bananas, string-of-dolphins, easter-cactus, calathea-rattlesnake); AKA must use common names only.
- **Descriptions (ZH/ES):** Replaced English in AKA with target-language equivalents (serviceberry→唐棣, Pinks→石竹, Johnny-jump-up→三色堇, greens→叶菜, Wax gourd→冬瓜, currant→红醋栗/黑醋栗, Snake's head→棋盘花, VFT→捕蝇草; Golden hahnii→Hahnii dorado, moonshine→luz de luna, Flapjack→Planta tortita, Mini jade→Jade miniatura).
- **commonExamples (ZH):** Replaced "同义名" with "syn."; translated English common names to Chinese.
- **commonExamples (ES):** Translated English aliases (Golden hahnii, moonshine, Mini jade, Flapjack).
- **careTips:** Added toxicity mention to aglaonema, dracaena-fragrans, snake-plants, zz-plant (EN/ES/ZH) for metadata alignment.

## [1.5.0] - 2025-02-08

### Changed

- **Descriptions:** Expanded "also known as" blocks in descriptions across EN/ES/ZH.
- **commonExamples:** Per-locale translation of aliases (EN/ES/ZH). Scientific names retained; parenthetical aliases localized.
- **typeNames:** Differentiated duplicate typeNames across EN/ES/ZH (56 entries) for clarity.

## [1.4.0] - 2025-02-07

### Changed

- **Toxicity audit:** 160+ plants updated per ASPCA—houseplants, outdoor perennials, trees & shrubs, bulbs, aquatic, alpine, carnivorous, epiphytes. Generic categories kept unknown. EN/ES/ZH careTips updated for toxic/mildly toxic plants.
- **Category audits:** Metadata corrections across houseplant categories—temperature, humidity, drainage, wateringMethod. Descriptions clarified for naming overlaps.
- **Translations:** TypeName and careTips fixes (EN/ES/ZH).

## [1.3.0] - 2025-02-07

### Changed

- **Light preference:** Outdoor plants → outdoorFullSun/outdoorPartialSun; indoor houseplants → brightIndirect.
- **Drainage:** Rot-prone species → excellentDrainage.
- **Toxicity:** 14 plants unknown→known; 37 houseplant corrections (toxicity, humidity).

## [1.2.0] - 2025-02-07

### Added

- **800 plants** across 28 categories (EN, ZH, ES). Care metadata, dormancy notes, scientific name corrections.

### Changed

- **plantToxicity:** Migrated to expert terminology (nonToxic, mildlyToxic, toxic). Senecio→Curio per Kew POWO.

## [1.1.0] - 2025-02-07

### Changed

- Plant list cleanup: redundant entries removed.

## [1.0.0] - 2025-02

### Added

- Initial dataset.
