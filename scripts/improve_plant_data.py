#!/usr/bin/env python3
"""
Improve plant data by filling in missing optional metadata fields
based on plant knowledge and category patterns.

Reads source/common_plants_metadata.json and source/common_plants_language_en.json.
Modifies metadata in place. Run before merge.

Usage:
    python3 scripts/improve_plant_data.py
    python3 scripts/improve_plant_data.py --dry-run  # Show what would change without writing
"""

import json
import sys
from pathlib import Path


def load_json_file(file_path: Path):
    """Load JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        return None


def infer_soil_ph(plant_id: str, category: str, description: str, care_tips: str) -> str:
    """Infer soil pH preference based on plant characteristics."""
    text = f"{description} {care_tips}".lower()
    plant_id_lower = plant_id.lower()
    category_lower = category.lower()

    # Acid-loving plants (carnivorous, ericaceous, berries)
    if any(
        word in text
        for word in ["acid", "ericaceous", "azalea", "rhododendron", "blueberry", "cranberry", "carnivorous"]
    ):
        return "acidic"
    if "carnivorous" in category_lower:
        return "acidic"
    if any(word in plant_id_lower for word in ["blueberry", "cranberry", "azalea", "rhododendron"]):
        return "acidic"

    # Alkaline-loving plants
    if any(word in text for word in ["alkaline", "limestone", "chalk"]):
        return "alkaline"

    # Cacti and succulents often prefer neutral
    if "cactus" in plant_id_lower or "cacti" in plant_id_lower:
        return "neutral"
    if "succulent" in category_lower:
        return "neutral"

    # Most plants are adaptable to a range of pH
    return "adaptable"


def infer_drainage(plant_id: str, category: str, description: str, care_tips: str) -> str | None:
    """Infer drainage preference based on plant characteristics."""
    text = f"{description} {care_tips}".lower()
    plant_id_lower = plant_id.lower()
    category_lower = category.lower()

    # Soilless growing methods - don't set drainage
    if "hydroponic" in plant_id_lower or "aeroponic" in plant_id_lower:
        return None

    # Plants that need excellent drainage (cacti, succulents, carnivorous)
    if any(
        word in text for word in ["excellent drainage", "drainage essential", "cactus mix", "succulent mix"]
    ):
        return "excellentDrainage"
    if "cactus" in plant_id_lower or "cacti" in plant_id_lower:
        return "excellentDrainage"
    if "succulent" in category_lower:
        return "excellentDrainage"
    if "carnivorous" in category_lower:
        return "excellentDrainage"

    # Aquatic/bog plants
    if "aquatic" in category_lower or "bog" in category_lower:
        return "waterloggingTolerant"

    # Plants that prefer moisture-retentive soil
    if any(
        word in text
        for word in ["moisture-retentive", "keep moist", "consistently moist", "never dry", "evenly moist"]
    ):
        return "moistureRetentive"

    # Most plants prefer well-draining
    if any(
        word in text
        for word in ["well-draining", "well-drained", "drainage", "moist but well-drained"]
    ):
        return "wellDraining"

    return "wellDraining"


def _lifespan_needs_improvement(lifespan) -> bool:
    """Check if a plantLifeSpan value is missing or open-ended [xx, null]."""
    if not lifespan:
        return True
    return (
        isinstance(lifespan, list) and len(lifespan) == 2
        and lifespan[0] is not None and lifespan[1] is None
    )


def infer_lifespan(plant_id: str, category: str, description: str, care_tips: str) -> list:
    """Infer plant lifespan [min_years, max_years] based on botanical knowledge.

    Returns realistic min/max year ranges. None means unknown bound
    (e.g., [None, 1] = less than 1 year).
    """
    text = f"{description} {care_tips}".lower()
    pid = plant_id.lower()

    # --- Text-based override ---
    if "biennial" in text and "perennial" not in text:
        return [2, 2]

    # === Outdoor - Annuals ===
    if category == "Outdoor - Annuals":
        return [1, 1]

    # === Sprouts & Microgreens ===
    if category == "Sprouts & Microgreens":
        return [1, 1]

    # === Vegetables ===
    if "Vegetables" in category:
        if any(w in pid for w in ["asparagus"]):
            return [15, 25]
        if any(w in pid for w in ["artichoke"]):
            return [3, 10]
        if any(w in pid for w in ["rhubarb"]):
            return [10, 20]
        if any(w in pid for w in ["horseradish"]):
            return [5, 20]
        if any(w in pid for w in ["jerusalem-artichoke"]):
            return [5, 15]
        if any(w in pid for w in ["dandelion"]):
            return [3, 10]
        if "perennial" in text:
            return [3, 10]
        return [1, 1]

    # === Herbs ===
    if category == "Herbs":
        if any(w in pid for w in ["bay-laurel"]):
            return [20, 100]
        if any(w in pid for w in ["tea-plant"]):
            return [50, 100]
        if any(w in pid for w in ["cardamom"]):
            return [5, 15]
        if any(w in pid for w in ["rosemary", "thyme", "sage", "oregano"]):
            return [5, 15]
        if any(w in pid for w in ["mint", "chives", "chinese-chives", "lemongrass"]):
            return [3, 10]
        if any(w in pid for w in ["tarragon", "sorrel", "lovage", "comfrey"]):
            return [5, 15]
        if any(w in pid for w in ["lemon-balm", "catnip"]):
            return [3, 8]
        if any(w in pid for w in ["vietnamese-coriander"]):
            return [3, 8]
        if any(w in pid for w in ["savory", "marjoram"]):
            return [3, 5]
        if any(w in pid for w in ["indoor-herbs"]):
            return [1, 3]
        if "perennial" in text:
            return [3, 10]
        if any(w in pid for w in ["ginger", "turmeric", "parsley"]):
            return [1, 2]
        if any(w in pid for w in ["chamomile"]):
            return [1, 3]
        return [1, 1]

    # === Farm & Field Crops ===
    if category == "Farm & Field Crops":
        if any(w in pid for w in ["hops"]):
            return [10, 25]
        if any(w in pid for w in ["sugarcane"]):
            return [3, 8]
        if any(w in pid for w in ["alfalfa"]):
            return [3, 8]
        if any(w in pid for w in ["clover"]):
            return [2, 5]
        if any(w in pid for w in ["bahia-grass", "fescue", "timothy-grass"]):
            return [5, 15]
        if any(w in pid for w in ["cassava"]):
            return [1, 3]
        if any(w in pid for w in ["castor"]):
            return [1, 3]
        if any(w in pid for w in ["sugar-beet"]):
            return [1, 2]
        if any(w in pid for w in ["sweet-potato"]):
            return [1, 1]
        return [1, 1]

    # === Fruits & Berries ===
    if category == "Fruits & Berries":
        if any(w in pid for w in ["coconut"]):
            return [60, 100]
        if any(w in pid for w in ["dates"]):
            return [50, 100]
        if any(w in pid for w in ["fig"]):
            return [20, 200]
        if any(w in pid for w in ["olive"]):
            return [20, 200]
        if any(w in pid for w in ["grapes"]):
            return [20, 100]
        if any(w in pid for w in ["pomegranate"]):
            return [20, 100]
        if any(w in pid for w in ["avocado"]):
            return [20, 100]
        if any(w in pid for w in ["mango"]):
            return [10, 100]
        if any(w in pid for w in ["jujube", "longan", "lychee", "mulberry"]):
            return [20, 100]
        if any(w in pid for w in ["pear"]):
            return [20, 100]
        if any(w in pid for w in ["persimmon"]):
            return [20, 75]
        if any(w in pid for w in ["apple"]):
            return [15, 80]
        if any(w in pid for w in ["cherries", "cherry"]):
            return [20, 50]
        if any(w in pid for w in ["citrus", "kumquat", "pomelo", "loquat"]):
            return [15, 50]
        if any(w in pid for w in ["pawpaw", "quince"]):
            return [20, 50]
        if any(w in pid for w in ["apricot", "nectarine"]):
            return [15, 40]
        if any(w in pid for w in ["peach", "plum"]):
            return [15, 30]
        if any(w in pid for w in ["guava"]):
            return [10, 40]
        if any(w in pid for w in ["kiwi"]):
            return [15, 50]
        if any(w in pid for w in ["dragon-fruit"]):
            return [10, 30]
        if any(w in pid for w in ["blueberry"]):
            return [15, 30]
        if any(w in pid for w in ["elderberry", "goji", "cranberry"]):
            return [10, 30]
        if any(w in pid for w in ["raspberry", "blackberry", "boysenberry", "loganberry"]):
            return [8, 15]
        if any(w in pid for w in ["currant", "gooseberry"]):
            return [8, 15]
        if any(w in pid for w in ["strawberry"]):
            return [3, 5]
        if any(w in pid for w in ["banana"]):
            return [1, 6]
        if any(w in pid for w in ["papaya"]):
            return [1, 4]
        if any(w in pid for w in ["passion-fruit"]):
            return [1, 7]
        if any(w in pid for w in ["pineapple"]):
            return [1, 3]
        if any(w in pid for w in ["prickly-pear"]):
            return [10, 50]
        if any(w in pid for w in ["musk-melon", "watermelon"]):
            return [1, 1]
        return [10, 50]

    # === Bulbs ===
    if category == "Bulbs":
        if any(w in pid for w in ["daffodil", "narcissus", "snowdrop"]):
            return [10, 30]
        if any(w in pid for w in ["amaryllis"]):
            return [10, 25]
        if any(w in pid for w in ["muscari", "scilla", "chionodoxa"]):
            return [5, 20]
        if any(w in pid for w in ["iris"]):
            return [5, 20]
        if any(w in pid for w in ["dahlia", "canna", "calla", "fritillaria"]):
            return [5, 15]
        if any(w in pid for w in ["crocus"]):
            return [5, 15]
        if any(w in pid for w in ["cyclamen"]):
            return [5, 15]
        if any(w in pid for w in ["allium"]):
            return [5, 15]
        if any(w in pid for w in ["lily"]):
            return [5, 15]
        if any(w in pid for w in ["oxalis"]):
            return [5, 15]
        if any(w in pid for w in ["freesia"]):
            return [5, 10]
        if any(w in pid for w in ["ranunculus", "anemone"]):
            return [3, 8]
        if any(w in pid for w in ["tuberose"]):
            return [3, 10]
        return [5, 20]

    # === Outdoor - Trees ===
    if category == "Outdoor - Trees":
        if any(w in pid for w in ["oak", "ginkgo", "bald-cypress"]):
            return [100, 500]
        if any(w in pid for w in ["pine", "conifer"]):
            return [100, 300]
        if any(w in pid for w in ["magnolia"]):
            return [50, 200]
        if any(w in pid for w in ["maple", "birch", "hornbeam", "sweetgum"]):
            return [50, 200]
        if any(w in pid for w in ["deciduous", "evergreen", "desert"]):
            return [50, 200]
        if any(w in pid for w in ["redbud"]):
            return [50, 80]
        if any(w in pid for w in ["dogwood", "crabapple"]):
            return [30, 80]
        if any(w in pid for w in ["cherry"]):
            return [20, 50]
        if any(w in pid for w in ["crepe", "crape"]):
            return [20, 50]
        if any(w in pid for w in ["willow", "serviceberry"]):
            return [20, 50]
        if any(w in pid for w in ["citrus", "fruit-tree"]):
            return [20, 80]
        if any(w in pid for w in ["smoke"]):
            return [15, 40]
        return [20, 100]

    # === Outdoor - Shrubs ===
    if category == "Outdoor - Shrubs":
        if any(w in pid for w in ["boxwood", "holly", "yew", "osmanthus"]):
            return [20, 100]
        if any(w in pid for w in ["lilac"]):
            return [30, 100]
        if any(w in pid for w in ["camellia"]):
            return [20, 100]
        if any(w in pid for w in ["juniper", "forsythia", "viburnum"]):
            return [20, 50]
        if any(w in pid for w in ["cold-hardy", "evergreen"]):
            return [20, 50]
        if any(w in pid for w in ["rhododendron"]):
            return [15, 50]
        if any(w in pid for w in ["rose-of-sharon"]):
            return [20, 40]
        if any(w in pid for w in ["azalea"]):
            return [10, 40]
        if any(w in pid for w in ["roses", "flowering-shrub"]):
            return [10, 30]
        if any(w in pid for w in ["hydrangea"]):
            return [10, 25]
        if any(w in pid for w in ["barberry", "cotoneaster", "nandina", "loropetalum",
                                   "ninebark", "weigela", "leadplant"]):
            return [10, 25]
        if any(w in pid for w in ["butterfly-bush", "burning-bush", "abelia"]):
            return [10, 20]
        if any(w in pid for w in ["spirea"]):
            return [10, 20]
        if any(w in pid for w in ["russian-sage"]):
            return [5, 15]
        if any(w in pid for w in ["caryopteris"]):
            return [5, 10]
        return [10, 30]

    # === Outdoor - Perennials ===
    if category == "Outdoor - Perennials":
        if any(w in pid for w in ["peony"]):
            return [20, 100]
        if any(w in pid for w in ["hosta"]):
            return [10, 30]
        if any(w in pid for w in ["lily-of-the-valley"]):
            return [10, 25]
        if any(w in pid for w in ["daylil"]):
            return [10, 25]
        if any(w in pid for w in ["iris"]):
            return [5, 20]
        if any(w in pid for w in ["salvia", "sage"]):
            return [5, 15]
        if any(w in pid for w in ["coneflower", "echinacea"]):
            return [5, 15]
        if any(w in pid for w in ["sedum", "stonecrop"]):
            return [5, 20]
        if any(w in pid for w in ["bleeding-heart"]):
            return [5, 15]
        if any(w in pid for w in ["bee-balm", "bergamot"]):
            return [5, 10]
        if any(w in pid for w in ["catmint"]):
            return [5, 10]
        if any(w in pid for w in ["yarrow", "hardy-geranium", "cranesbill"]):
            return [5, 15]
        if any(w in pid for w in ["phlox"]):
            return [5, 10]
        if any(w in pid for w in ["astilbe"]):
            return [5, 10]
        if any(w in pid for w in ["lantana"]):
            return [5, 10]
        if any(w in pid for w in ["verbena", "heuchera", "dianthus",
                                   "painted-daisy", "shasta", "penstemon",
                                   "coreopsis", "columbine"]):
            return [3, 8]
        if any(w in pid for w in ["creeping-thyme"]):
            return [3, 8]
        if any(w in pid for w in ["delphinium", "lupine", "gaillardia", "blanket"]):
            return [3, 5]
        if any(w in pid for w in ["foxglove"]):
            return [2, 3]
        # Prairie and wildflower natives
        if any(w in pid for w in ["milkweed", "goldenrod", "joe-pye", "ironweed",
                                   "indigo", "blazing", "compass", "prairie",
                                   "rattlesnake", "mullein", "aster", "clover",
                                   "viper", "scabious", "culver", "maximilian",
                                   "oxeye", "dock", "yellow-coneflower"]):
            return [3, 15]
        return [3, 15]

    # === Outdoor - Groundcovers & Grasses ===
    if category == "Outdoor - Groundcovers & Grasses":
        if any(w in pid for w in ["miscanthus", "pachysandra", "vinca"]):
            return [10, 25]
        if any(w in pid for w in ["bamboo"]):
            return [10, 50]
        if any(w in pid for w in ["ajuga", "pennisetum", "panicum", "switchgrass",
                                   "bluestem", "grama", "indian-grass", "dropseed",
                                   "muhly", "japanese-forest", "sedum"]):
            return [5, 15]
        if any(w in pid for w in ["lambs-ear", "creeping-phlox", "sweet-woodruff"]):
            return [5, 10]
        if any(w in pid for w in ["fescue", "lawn"]):
            return [3, 10]
        return [5, 15]

    # === Outdoor - Vines & Climbers ===
    if category == "Outdoor - Vines & Climbers":
        if any(w in pid for w in ["wisteria"]):
            return [20, 100]
        if any(w in pid for w in ["climbing-hydrangea"]):
            return [15, 50]
        if any(w in pid for w in ["ivy", "boston-ivy", "virginia-creeper"]):
            return [10, 50]
        if any(w in pid for w in ["trumpet-vine", "crossvine"]):
            return [10, 30]
        if any(w in pid for w in ["clematis", "honeysuckle", "trumpet-honeysuckle"]):
            return [10, 25]
        if any(w in pid for w in ["climbing-rose", "carolina-jessamine", "jasmine"]):
            return [10, 25]
        if any(w in pid for w in ["passion"]):
            return [5, 15]
        return [5, 20]

    # === Houseplants ===
    if "Houseplants" in category:
        subcat = category.replace("Houseplants - ", "").lower()

        # --- Low Maintenance ---
        if "low maintenance" in subcat:
            if any(w in pid for w in ["cast-iron", "aspidistra"]):
                return [10, 50]
            if any(w in pid for w in ["snake", "sansevieria"]):
                return [10, 25]
            if any(w in pid for w in ["dracaena"]):
                return [10, 25]
            if any(w in pid for w in ["ficus"]):
                return [10, 25]
            if any(w in pid for w in ["yucca"]):
                return [10, 25]
            if any(w in pid for w in ["palm"]):
                return [10, 30]
            if any(w in pid for w in ["philodendron"]):
                return [10, 20]
            if any(w in pid for w in ["zz-plant"]):
                return [5, 20]
            if any(w in pid for w in ["spider"]):
                return [5, 20]
            if any(w in pid for w in ["pothos"]):
                return [5, 15]
            if any(w in pid for w in ["schefflera"]):
                return [5, 15]
            if any(w in pid for w in ["aglaonema", "chinese-evergreen"]):
                return [5, 15]
            if any(w in pid for w in ["aralia", "false-aralia"]):
                return [5, 15]
            if any(w in pid for w in ["dieffenbachia"]):
                return [5, 10]
            if any(w in pid for w in ["peace-lily", "spathiphyllum"]):
                return [5, 10]
            if any(w in pid for w in ["peperomia", "pilea", "syngonium"]):
                return [5, 10]
            return [5, 15]

        # --- Aroids ---
        if "aroid" in subcat:
            if any(w in pid for w in ["monstera"]):
                return [10, 40]
            if any(w in pid for w in ["philodendron"]):
                return [10, 20]
            if any(w in pid for w in ["anthurium"]):
                return [5, 15]
            if any(w in pid for w in ["alocasia"]):
                return [5, 15]
            if any(w in pid for w in ["syngonium", "arrowhead"]):
                return [5, 15]
            if any(w in pid for w in ["pothos", "epipremnum", "golden-pothos",
                                       "neon-pothos", "marble-queen"]):
                return [5, 15]
            if any(w in pid for w in ["rhaphidophora", "scindapsus"]):
                return [5, 15]
            if any(w in pid for w in ["aglaonema"]):
                return [5, 15]
            if any(w in pid for w in ["dieffenbachia"]):
                return [5, 10]
            if any(w in pid for w in ["colocasia", "xanthosoma"]):
                return [3, 10]
            if any(w in pid for w in ["caladium"]):
                return [2, 5]
            return [5, 20]

        # --- Ferns ---
        if "fern" in subcat:
            if any(w in pid for w in ["staghorn", "platycerium"]):
                return [10, 25]
            if any(w in pid for w in ["boston", "nephrolepis"]):
                return [5, 15]
            if any(w in pid for w in ["asparagus"]):
                return [5, 15]
            if any(w in pid for w in ["bird", "asplenium"]):
                return [5, 10]
            if any(w in pid for w in ["rabbit"]):
                return [5, 10]
            if any(w in pid for w in ["maidenhair"]):
                return [3, 8]
            return [3, 10]

        # --- Palms ---
        if "palm" in subcat:
            if any(w in pid for w in ["ponytail"]):
                return [10, 50]
            if any(w in pid for w in ["kentia"]):
                return [10, 40]
            if any(w in pid for w in ["lady-palm", "european-fan"]):
                return [10, 30]
            if any(w in pid for w in ["parlor", "chamaedorea", "neanthe"]):
                return [10, 25]
            if any(w in pid for w in ["phoenix"]):
                return [10, 25]
            if any(w in pid for w in ["areca", "majesty"]):
                return [10, 20]
            return [10, 30]

        # --- Succulents ---
        if "succulent" in subcat:
            if any(w in pid for w in ["jade", "crassula", "portulacaria"]):
                return [10, 50]
            if any(w in pid for w in ["lithops", "split-rock"]):
                return [10, 40]
            if any(w in pid for w in ["haworthia", "gasteria"]):
                return [10, 30]
            if any(w in pid for w in ["euphorbia"]):
                return [10, 30]
            if any(w in pid for w in ["aloe"]):
                return [5, 25]
            if any(w in pid for w in ["echeveria", "aeonium", "sempervivum",
                                       "sedum", "graptopetalum"]):
                return [5, 15]
            if any(w in pid for w in ["kalanchoe"]):
                return [3, 10]
            if any(w in pid for w in ["string-of", "senecio"]):
                return [3, 10]
            if any(w in pid for w in ["burro", "bears"]):
                return [5, 10]
            return [5, 25]

        # --- Cacti ---
        if "cact" in subcat:
            if any(w in pid for w in ["barrel", "star-cactus"]):
                return [20, 100]
            if any(w in pid for w in ["prickly", "opuntia"]):
                return [10, 50]
            if any(w in pid for w in ["christmas", "easter", "thanksgiving"]):
                return [10, 30]
            if any(w in pid for w in ["mammillaria", "old-lady",
                                       "gymnocalycium", "parodia", "echinopsis"]):
                return [10, 30]
            if any(w in pid for w in ["epiphyllum"]):
                return [10, 20]
            if any(w in pid for w in ["rhipsalis", "rat-tail", "forest"]):
                return [5, 15]
            return [10, 50]

        # --- Flowering ---
        if "flower" in subcat:
            if any(w in pid for w in ["hoya"]):
                return [10, 30]
            if any(w in pid for w in ["orchid", "phalaenopsis"]):
                return [10, 25]
            if any(w in pid for w in ["crown-of-thorns"]):
                return [10, 25]
            if any(w in pid for w in ["african-violet"]):
                return [5, 25]
            if any(w in pid for w in ["coffee"]):
                return [5, 15]
            if any(w in pid for w in ["hibiscus", "jasmine", "gardenia"]):
                return [5, 15]
            if any(w in pid for w in ["lipstick", "goldfish", "columnea",
                                       "mandevilla"]):
                return [5, 15]
            if any(w in pid for w in ["peace-lil"]):
                return [5, 10]
            if any(w in pid for w in ["kalanchoe"]):
                return [3, 10]
            if any(w in pid for w in ["begonia"]):
                return [3, 10]
            if any(w in pid for w in ["streptocarpus"]):
                return [3, 10]
            if any(w in pid for w in ["rex-begonia", "tuberous"]):
                return [3, 8]
            if any(w in pid for w in ["zebra-plant"]):
                return [3, 8]
            if any(w in pid for w in ["bromeliad"]):
                return [3, 5]
            if any(w in pid for w in ["sinningia"]):
                return [2, 5]
            return [3, 10]

        # --- Prayer Plants ---
        if "prayer" in subcat:
            if any(w in pid for w in ["maranta", "stromanthe", "ctenanthe"]):
                return [5, 10]
            if any(w in pid for w in ["nerve", "fittonia"]):
                return [3, 5]
            if any(w in pid for w in ["calathea"]):
                return [3, 10]
            return [3, 10]

        # --- Vines & Trailing ---
        if "vine" in subcat or "trailing" in subcat:
            if any(w in pid for w in ["english-ivy"]):
                return [10, 50]
            if any(w in pid for w in ["hoya"]):
                return [10, 30]
            if any(w in pid for w in ["philodendron"]):
                return [10, 20]
            if any(w in pid for w in ["scindapsus"]):
                return [5, 15]
            if any(w in pid for w in ["dischidia", "grape-ivy", "pilea"]):
                return [5, 10]
            if any(w in pid for w in ["tradescantia"]):
                return [3, 8]
            if any(w in pid for w in ["peperomia"]):
                return [3, 8]
            return [5, 15]

        # --- Specialty ---
        if "specialty" in subcat:
            if any(w in pid for w in ["cycad", "sago"]):
                return [20, 100]
            if any(w in pid for w in ["norfolk", "ponytail"]):
                return [10, 50]
            if any(w in pid for w in ["bamboo"]):
                return [10, 50]
            if any(w in pid for w in ["fiddle-leaf", "rubber-plant", "ficus"]):
                return [10, 25]
            if any(w in pid for w in ["bird-of-paradise"]):
                return [10, 25]
            if any(w in pid for w in ["croton", "money-tree", "lucky-bamboo",
                                       "schefflera", "lemon-cypress"]):
                return [5, 15]
            if any(w in pid for w in ["bonsai"]):
                return [5, 50]
            if any(w in pid for w in ["oxalis"]):
                return [5, 15]
            if any(w in pid for w in ["peperomia", "pilea"]):
                return [5, 10]
            return [5, 15]

        # Default houseplant
        return [5, 15]

    # === Specialty categories ===
    if "Specialty" in category:
        # --- Aquatic & Bog ---
        if "Aquatic" in category or "Bog" in category:
            if any(w in pid for w in ["lotus"]):
                return [10, 30]
            if any(w in pid for w in ["cattail"]):
                return [5, 20]
            if any(w in pid for w in ["water-lily", "water-iris", "papyrus",
                                       "water-hawthorn"]):
                return [5, 15]
            if any(w in pid for w in ["pickerelweed", "arrowhead"]):
                return [3, 10]
            if any(w in pid for w in ["duckweed", "water-lettuce",
                                       "water-hyacinth", "floating"]):
                return [1, 3]
            if any(w in pid for w in ["bamboo"]):
                return [5, 15]
            return [3, 15]

        # --- Carnivorous ---
        if "Carnivorous" in category:
            if any(w in pid for w in ["venus"]):
                return [5, 20]
            if any(w in pid for w in ["pitcher", "sarracenia", "cobra"]):
                return [5, 20]
            if any(w in pid for w in ["nepenthes", "mexican-pitcher"]):
                return [5, 15]
            if any(w in pid for w in ["sundew", "drosera", "butterwort"]):
                return [3, 10]
            return [3, 15]

        # --- Epiphytes & Moss ---
        if "Epiphyte" in category or "Moss" in category:
            if any(w in pid for w in ["orchid", "dendrobium", "oncidium", "vanda"]):
                return [10, 25]
            if any(w in pid for w in ["lichen"]):
                return [10, 50]
            if any(w in pid for w in ["resurrection"]):
                return [5, 20]
            if any(w in pid for w in ["moss", "spanish-moss"]):
                return [5, 20]
            if any(w in pid for w in ["xerographica"]):
                return [5, 15]
            if any(w in pid for w in ["tillandsia", "air-plant"]):
                return [3, 10]
            if any(w in pid for w in ["bromeliad", "neoregelia"]):
                return [3, 5]
            return [3, 15]

        # --- Alpine ---
        if "Alpine" in category:
            if any(w in pid for w in ["gentian", "saxifrage", "sempervivum"]):
                return [5, 15]
            if any(w in pid for w in ["edelweiss", "aubrieta", "lewisia"]):
                return [5, 10]
            if any(w in pid for w in ["alpine-aster", "campanula", "dianthus",
                                       "draba", "rock-jasmine", "catchfly"]):
                return [3, 8]
            if any(w in pid for w in ["alpine-poppy"]):
                return [3, 5]
            return [3, 10]

        return [3, 15]

    # Default fallback
    return [3, 15]


def improve_metadata(
    metadata: dict, lang_lookup: dict[str, dict]
) -> dict[str, int]:
    """Improve metadata by filling in missing fields. Returns count of improvements per field."""
    improvements = {"soilPhPreference": 0, "drainagePreference": 0, "plantLifeSpan": 0}

    for plant_id, plant_meta in metadata.items():
        if plant_id == "_metadata":
            continue

        lang_entry = lang_lookup.get(plant_id, {})
        description = lang_entry.get("description", "")
        care_tips = lang_entry.get("careTips", "")
        category = plant_meta.get("category", "")

        # Fill in missing soilPhPreference
        if not plant_meta.get("soilPhPreference") or plant_meta.get("soilPhPreference") == "unknown":
            inferred = infer_soil_ph(plant_id, category, description, care_tips)
            if inferred:
                plant_meta["soilPhPreference"] = inferred
                improvements["soilPhPreference"] += 1

        # Fill in missing drainagePreference
        if not plant_meta.get("drainagePreference") or plant_meta.get("drainagePreference") == "unknown":
            inferred = infer_drainage(plant_id, category, description, care_tips)
            if inferred is not None:
                plant_meta["drainagePreference"] = inferred
                improvements["drainagePreference"] += 1

        # Fill in missing or optimize open-ended plantLifeSpan [xx, null]
        current_ls = plant_meta.get("plantLifeSpan")
        if _lifespan_needs_improvement(current_ls):
            inferred = infer_lifespan(plant_id, category, description, care_tips)
            if inferred is not None:
                is_open_ended = (
                    isinstance(current_ls, list) and len(current_ls) == 2
                    and current_ls[0] is not None and current_ls[1] is None
                )
                if is_open_ended and inferred[1] is not None:
                    # Keep higher of existing/inferred min, use inferred max
                    final_min = max(current_ls[0], inferred[0]) if inferred[0] is not None else current_ls[0]
                    plant_meta["plantLifeSpan"] = [final_min, inferred[1]]
                else:
                    plant_meta["plantLifeSpan"] = inferred
                improvements["plantLifeSpan"] += 1

    return improvements


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Improve plant metadata by inferring missing fields")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    source_dir = repo_root / "source"
    metadata_file = source_dir / "common_plants_metadata.json"
    lang_file = source_dir / "common_plants_language_en.json"

    print("=" * 80)
    print("IMPROVING PLANT DATA")
    print("=" * 80)

    print("\n📂 Loading files...")
    metadata = load_json_file(metadata_file)
    lang_data = load_json_file(lang_file)

    if not metadata or not lang_data:
        print("Error: Could not load required files", file=sys.stderr)
        sys.exit(1)

    # Build id -> {description, careTips} lookup from language file
    lang_lookup = {}
    for entry in lang_data:
        if isinstance(entry, dict) and "_metadata" not in entry and entry.get("id"):
            lang_lookup[entry["id"]] = entry

    plant_entries = {k: v for k, v in metadata.items() if k != "_metadata" and isinstance(v, dict)}
    plant_count = len(plant_entries)
    print(f"  Loaded metadata for {plant_count} plants")
    print(f"  Loaded language for {len(lang_lookup)} plants")

    missing_before = {
        "soilPhPreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("soilPhPreference") or m.get("soilPhPreference") == "unknown"
        ),
        "drainagePreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("drainagePreference") or m.get("drainagePreference") == "unknown"
        ),
        "plantLifeSpan": sum(
            1 for m in plant_entries.values()
            if _lifespan_needs_improvement(m.get("plantLifeSpan"))
        ),
    }

    print(f"\n📊 Missing/open-ended fields before improvement:")
    for field, count in missing_before.items():
        print(f"  {field}: {count} plants")

    print("\n🔧 Improving metadata...")
    improvements = improve_metadata(metadata, lang_lookup)

    print(f"\n✅ Improvements made:")
    for field, count in improvements.items():
        print(f"  {field}: {count} plants updated")

    missing_after = {
        "soilPhPreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("soilPhPreference") or m.get("soilPhPreference") == "unknown"
        ),
        "drainagePreference": sum(
            1
            for m in plant_entries.values()
            if not m.get("drainagePreference") or m.get("drainagePreference") == "unknown"
        ),
        "plantLifeSpan": sum(
            1 for m in plant_entries.values()
            if _lifespan_needs_improvement(m.get("plantLifeSpan"))
        ),
    }

    print(f"\n📊 Missing/open-ended fields after improvement:")
    for field, count in missing_after.items():
        reduction = missing_before[field] - count
        suffix = f" (Reduced by {reduction})" if reduction > 0 else ""
        print(f"  {field}: {count} plants{suffix}")

    if not args.dry_run and any(improvements.values()):
        print("\n💾 Saving improved metadata...")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {metadata_file}")
    elif args.dry_run:
        print("\n🏃 Dry run: no files written")

    print("\n" + "=" * 80)
    print("Improvement complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
