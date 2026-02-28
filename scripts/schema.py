"""
Shared schema constants for plantfolio-common-plants.

Category order, enums, and metadata field order. Single source of truth.
"""

# Category order (Houseplants → Outdoor → Edibles → Farm/Sprouts → Bulbs → Specialty)
CATEGORY_ORDER = [
    "Houseplants - Low Maintenance", "Houseplants - Aroids", "Houseplants - Ferns",
    "Houseplants - Palms", "Houseplants - Succulents", "Houseplants - Cacti",
    "Houseplants - Flowering", "Houseplants - Prayer Plants", "Houseplants - Vines & Trailing",
    "Houseplants - Ficus & Fig", "Houseplants - Specialty",
    "Outdoor - Trees", "Outdoor - Shrubs", "Outdoor - Perennials",
    "Outdoor - Annuals", "Outdoor - Vines & Climbers", "Outdoor - Groundcovers & Grasses",
    "Vegetables - Leafy Greens", "Vegetables - Fruiting", "Vegetables - Root & Bulb",
    "Fruits & Berries", "Herbs",
    "Farm & Field Crops", "Sprouts & Microgreens",
    "Bulbs",
    "Specialty - Aquatic & Bog", "Specialty - Carnivorous",
    "Specialty - Epiphytes & Moss", "Specialty - Alpine",
]

VALID_CATEGORIES = frozenset(CATEGORY_ORDER)

# Enums (Plantfolio app compatible)
VALID_LIGHT_PREFERENCES = frozenset({
    "brightIndirect", "lowIndirect", "mediumIndirect",
    "outdoorFullSun", "outdoorPartialSun", "outdoorShade",
    "strongDirect",
})
VALID_PLANT_TOXICITY = frozenset({"mildlyToxic", "nonToxic", "toxic", "unknown"})
VALID_HUMIDITY_PREFERENCES = frozenset({"high", "low", "medium", "veryHigh"})
VALID_SOIL_PH = frozenset({"acidic", "adaptable", "alkaline", "neutral"})
VALID_DRAINAGE = frozenset({
    "excellentDrainage", "moistureRetentive",
    "waterloggingTolerant", "wellDraining",
})
VALID_WATERING_METHOD = frozenset({
    "bottomWatering", "immersion", "misting", "topWatering",
    None,  # aquatic/carnivorous
})

# Metadata key order (for consistent output, git diffs)
METADATA_KEY_ORDER = [
    "springInterval", "summerInterval", "fallInterval", "winterInterval",
    "lightPreference", "humidityPreference", "temperaturePreference",
    "plantToxicity", "soilPhPreference", "drainagePreference", "wateringMethod",
    "plantLifeSpan", "category", "hardinessZones",
]

LANG_ENTRY_KEY_ORDER = ["id", "typeName", "description", "commonExamples", "careTips"]

REQUIRED_METADATA_FIELDS = [
    "springInterval", "summerInterval", "fallInterval", "winterInterval",
    "lightPreference", "humidityPreference", "temperaturePreference",
    "plantToxicity", "soilPhPreference", "drainagePreference", "wateringMethod",
    "plantLifeSpan", "category",
]
