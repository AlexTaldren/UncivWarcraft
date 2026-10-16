"""Warcraft renames applied on top of Unciv's Gods & Kings ruleset.

Each map is old name -> new name. Anything not listed keeps its Unciv name
(generic things like Library, Iron, Farm are fine as they are).
"""

ERAS = {
    "Ancient era": "Age of Tribes",
    "Classical era": "Age of Arathor",
    "Medieval era": "Age of the Dark Portal",
    "Renaissance era": "Age of the Third War",
    "Industrial era": "Age of the Lich King",
    "Modern era": "Age of the Cataclysm",
    "Atomic era": "Age of the Legion",
    "Information era": "Age of Azerite",
    "Future era": "Age of the Void",
}

TECHS = {
    "Animal Husbandry": "Beast Taming",
    "Calendar": "Herbalism",
    "Writing": "Runic Script",
    "Trapping": "Skinning",
    "Horseback Riding": "Riding",
    "Philosophy": "Philosophy",
    "Drama and Poetry": "Bardic Lore",
    "Currency": "Coinage",
    "Iron Working": "Blacksmithing",
    "Civil Service": "Arathi Law",
    "Guilds": "Trade Guilds",
    "Compass": "Seafaring",
    "Education": "Scholarship",
    "Physics": "Natural Philosophy",
    "Printing Press": "Inscription",
    "Gunpowder": "Blackpowder",
    "Economics": "Mercantilism",
    "Chemistry": "Alchemy",
    "Scientific Theory": "Arcane Science",
    "Industrialization": "Steamworks",
    "Military Science": "War Doctrine",
    "Fertilizer": "Soil Enrichment",
    "Dynamite": "Seaforium",
    "Refrigeration": "Frost Enchantment",
    "Radio": "Communication Crystals",
    "Replaceable Parts": "Interchangeable Cogs",
    "Plastics": "Synthetic Alloys",
    "Electronics": "Arcane Circuitry",
    "Pharmaceuticals": "Elixir Mastery",
    "Atomic Theory": "Mana Theory",
    "Radar": "Scrying",
    "Ecology": "Druidic Ecology",
    "Nuclear Fission": "Mana Fission",
    "Computers": "Titan Logic",
    "Telecommunications": "Portal Networks",
    "Satellites": "Orbital Constructs",
    "Robotics": "Mechagnomics",
    "Lasers": "Focused Arcana",
    "Globalization": "Azerothian Unity",
    "Particle Physics": "Azerite Refinement",
    "Nuclear Fusion": "Titanforging",
    "Nanotechnology": "Ethereal Technology",
    "Stealth": "Cloaking Fields",
    # "Future Tech" is hard-coded in the engine and keeps its name.
}

UNITS = {
    "Worker": "Peasant",
    "Work Boats": "Fishing Skiff",
    "Trireme": "Longboat",
    "Chariot Archer": "Mounted Archer",
    "Horseman": "Outrider",
    "Composite Bowman": "Ranger",
    "Galleass": "Battle Galley",
    "Longswordsman": "Vanguard",
    "Caravel": "Brigantine",
    "Musketman": "Musketeer",
    "Privateer": "Buccaneer",
    "Gatling Gun": "Steam Gatling",
    "Artillery": "Mortar Team",
    "Submarine": "Submersible",
    "Great War Infantry": "Fusilier",
    "Triplane": "Gyrocopter",
    "Great War Bomber": "Bomber Zeppelin",
    "Infantry": "Shock Trooper",
    "Carrier": "Airship Tender",
    "Battleship": "Dreadnought",
    "Machine Gun": "Gun Nest",
    "Anti-Aircraft Gun": "Flak Cannon",
    "Landship": "Steam Tank",
    "Fighter": "Strike Gyro",
    "Bomber": "War Zeppelin",
    "Paratrooper": "Rocketeer",
    "Tank": "Siege Tank",
    "Anti-Tank Gun": "Tankbuster Cannon",
    "Atomic Bomb": "Mana Bomb",
    "Rocket Artillery": "Rocket Battery",
    "Mobile SAM": "Mobile Flak",
    "Guided Missile": "Arcane Missile",
    "Nuclear Missile": "Mana Missile",
    "Helicopter Gunship": "Gunship Gyro",
    "Nuclear Submarine": "Arcane Submersible",
    "Mechanized Infantry": "Mechano-Trooper",
    "Missile Cruiser": "Arcane Cruiser",
    "Modern Armor": "Mechano-Tank",
    "Jet Fighter": "Sky Golem",
    "Giant Death Robot": "Iron Colossus",
    "Stealth Bomber": "Void Bomber",
    "SS Booster": "Arcane Thruster",
    "SS Cockpit": "Navigation Crystal",
    "SS Engine": "Titan Engine",
    "SS Stasis Chamber": "Stasis Vault",
    # Settler, Great People, Missionary and Inquisitor keep their names
    # (the engine looks some of them up by name).
}

# Unit names that are ALSO unit-type names. Only the unit itself is renamed;
# "[Submarine]"-style filters in uniques keep meaning the unit type.
TYPE_COLLISIONS = {"Submarine", "Fighter", "Bomber"}

BUILDINGS = {
    # regular buildings
    "Circus": "Fighting Pit",
    "Colosseum": "Arena",
    "Courthouse": "Magistrate's Hall",
    "University": "Arcane Academy",
    "Castle": "Keep",
    "Opera House": "Bardic Hall",
    "Constabulary": "City Watch",
    "Theatre": "Menagerie",
    "Factory": "Foundry",
    "Hospital": "House of Healing",
    "Stock Exchange": "Auction House",
    "Hydro Plant": "Hydroworks",
    "Police Station": "Guard Post",
    "Stadium": "Grand Arena",
    "Broadcast Tower": "Arcane Beacon",
    "Military Base": "Fortress",
    "Research Lab": "Arcane Laboratory",
    "Medical Lab": "Alchemy Lab",
    "Solar Plant": "Sun Crystal Array",
    "Recycling Center": "Salvage Yard",
    "Nuclear Plant": "Mana Reactor",
    "Bomb Shelter": "Warded Bunker",
    "Spaceship Factory": "Skyship Foundry",
    "Mosque": "Sanctuary",
    # national wonders
    "National College": "Grand Library",
    "National Epic": "Hall of Legends",
    "Heroic Epic": "Hall of Champions",
    "National Treasury": "Royal Vault",
    "Circus Maximus": "Grand Coliseum",
    "Oxford University": "College of Magi",
    "Hermitage": "Royal Gallery",
    "Ironworks": "Great Foundry",
    "Grand Temple": "High Temple",
    "National Intelligence Agency": "Spymaster's Guild",
    # world wonders
    "Temple of Artemis": "Temple of Elune",
    "Stonehenge": "Circle of Binding",
    "The Great Library": "The Violet Citadel",
    "The Pyramids": "Halls of Origination",
    "Mausoleum of Halicarnassus": "Uther's Tomb",
    "Statue of Zeus": "Valley of Heroes",
    "The Great Lighthouse": "Westfall Lighthouse",
    "Hanging Gardens": "Vale of Eternal Blossoms",
    "Terracotta Army": "Mogu'shan Vaults",
    "The Oracle": "Sanctum of the Oracles",
    "Petra": "Caverns of Time",
    "Great Wall": "The Greymane Wall",
    "Colossus": "Admiralty of Boralus",
    "Hagia Sophia": "Cathedral of Light",
    "Great Mosque of Djenne": "Shrine of Seven Stars",
    "Chichen Itza": "Zul'Gurub",
    "Machu Picchu": "Thunder Totem",
    "Angkor Wat": "Temple of the White Tiger",
    "Alhambra": "Sunfury Spire",
    "Notre Dame": "Northshire Abbey",
    "Sistine Chapel": "Karazhan",
    "Forbidden Palace": "Mogu'shan Palace",
    "Leaning Tower of Pisa": "Tower of Azora",
    "Himeji Castle": "Grim Batol",
    "Taj Mahal": "Sunwell Plateau",
    "Porcelain Tower": "Ulduar",
    "Kremlin": "Icecrown Citadel",
    "The Louvre": "Hall of Explorers",
    "Big Ben": "Undermine Exchange",
    "Brandenburg Gate": "Gates of Ahn'Qiraj",
    "Eiffel Tower": "Wyrmrest Temple",
    "Statue of Liberty": "Lion's Rest",
    "Neuschwanstein": "Shadowfang Keep",
    "Cristo Redentor": "Seat of the Naaru",
    "Manhattan Project": "Mana Bomb Project",
    "Pentagon": "Grommash Hold",
    "Sydney Opera House": "The Nighthold",
    "Great Firewall": "Great Arcane Ward",
    "CN Tower": "Mechagon Spire",
    "Hubble Space Telescope": "Celestial Planetarium",
    "United Nations": "Grand Council of Azeroth",
    "Utopia Project": "Well of Eternity",
    "Apollo Program": "Titan Ascension Project",
}

RESOURCES = {
    "Coal": "Thorium",
    "Oil": "Azerite",
    "Aluminum": "Elementium",
    "Uranium": "Arcane Crystals",
    "Silver": "Truesilver",
    "Silk": "Mageweave",
    "Wine": "Ale",
    "Furs": "Rugged Leather",
    "Cotton": "Peacebloom",
    "Incense": "Mageroyal",
}

IMPROVEMENTS = {
    "Oil well": "Azerite Drill",
    "Remove Fallout": "Remove Blighted Land",
}

NATURAL_WONDERS = {
    "Great Barrier Reef": "Kelp'thar Forest",
    "Old Faithful": "Lakkari Tar Pits",
    "El Dorado": "Lost City of the Tol'vir",
    "Fountain of Youth": "Lake Elune'ara",
    "Grand Mesa": "Thousand Needles",
    "Mount Fuji": "Mount Hyjal",
    "Krakatoa": "The Maelstrom",
    "Rock of Gibraltar": "Cape of Stranglethorn",
    "Cerro de Potosi": "Blackrock Mountain",
    "Barringer Crater": "Un'Goro Crater",
    "Mount Kailash": "Moonglade",
    "Mount Sinai": "Stonetalon Peak",
    "Sri Pada": "Teldrassil",
    "Uluru": "Red Rocks of Mulgore",
}

TERRAIN_FEATURES = {
    "Fallout": "Blighted Land",
}

BELIEFS = {
    "Mosques": "Sanctuaries",
    "Papal Primacy": "Archbishop's Primacy",
    "Guruship": "Mentorship",
}

ALL = {}
for _m in (ERAS, TECHS, UNITS, BUILDINGS, RESOURCES, IMPROVEMENTS, NATURAL_WONDERS,
           TERRAIN_FEATURES, BELIEFS):
    for _k, _v in _m.items():
        if _k != _v:
            assert _k not in ALL, _k
            ALL[_k] = _v
assert len(set(ALL.values())) == len(ALL), "duplicate new names"

# Folders whose images are keyed by entity name and must follow a rename.
IMAGE_FOLDERS = ["UnitIcons", "BuildingIcons", "TechIcons", "ResourceIcons",
                 "ImprovementIcons", "TileSets/AbsoluteUnits/Units",
                 "TileSets/HexaRealm/Units", "TileSets/FantasyHex/Units",
                 "TileSets/HexaRealm/Tiles", "TileSets/FantasyHex/Tiles",
                 "TileSets/Minimal/Tiles"]
