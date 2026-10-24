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
    # Ages of Tribes / Arathor
    "Agriculture": "Farming",
    "Animal Husbandry": "Beast Taming",
    "Calendar": "Herbalism",
    "Writing": "Runic Script",
    "Trapping": "Skinning",
    "Horseback Riding": "Riding",
    "Drama and Poetry": "Bardic Lore",
    "Currency": "Coinage",
    "Iron Working": "Iron Forged Swords",      # Warcraft III blacksmith upgrade
    "Theology": "Priesthood",
    # Age of the Dark Portal
    "Civil Service": "Arathi Law",
    "Guilds": "Trade Guilds",
    "Metal Casting": "Blacksmithing",
    "Compass": "Seafaring",
    "Education": "Scholarship",
    "Chivalry": "Animal War Training",         # Warcraft III knight upgrade
    "Machinery": "Clockwork",
    "Physics": "Siege Engineering",
    "Steel": "Steel Forged Swords",            # Warcraft III upgrade, tier 2
    "Acoustics": "Choral Hymns",
    "Printing Press": "Inscription",
    # Age of the Third War
    "Gunpowder": "Blackpowder",
    "Economics": "Auctioneering",
    "Metallurgy": "Mithril Forged Swords",     # Warcraft III upgrade, tier 3
    "Chemistry": "Alchemy",
    "Scientific Theory": "Arcane Science",
    # Age of the Lich King
    "Industrialization": "Steamworks",
    "Rifling": "Long Rifles",                  # Warcraft III rifleman upgrade
    "Military Science": "War Doctrine",
    "Fertilizer": "Soil Enrichment",
    "Biology": "Natural Lore",
    "Electricity": "Storm Hammers",            # Warcraft III gryphon upgrade
    "Dynamite": "Seaforium",
    # Age of the Cataclysm
    "Refrigeration": "Frost Enchantment",
    "Radio": "Communication Crystals",
    "Replaceable Parts": "Gnomish Gearworks",
    "Flight": "Gnomish Flight",
    "Railroads": "Tramways",
    "Plastics": "Arcanite Alloys",
    "Electronics": "Arcane Conduits",
    "Ballistics": "Fragmentation Shards",      # Warcraft III mortar upgrade
    "Combustion": "Liquid Fire",               # Warcraft III orc upgrade
    # Age of the Legion
    "Pharmaceuticals": "Elixir Mastery",
    "Atomic Theory": "Mana Theory",
    "Radar": "Scrying",
    "Combined Arms": "Battle Formations",
    "Ecology": "Nature's Blessing",            # Warcraft III night elf upgrade
    "Nuclear Fission": "Unstable Mana",
    "Rocketry": "Demolition",
    # Age of Azerite
    "Computers": "Titan Logic",
    "Telecommunications": "Portal Networks",
    "Mobile Tactics": "War Drums",             # Warcraft III orc upgrade
    "Advanced Ballistics": "Siege Barrage",    # Warcraft III siege upgrade "Barrage"
    "Satellites": "Eye of Kilrogg",            # Warcraft II/III scouting spell
    "Robotics": "Mechagnomics",
    "Lasers": "Focused Arcana",
    "Globalization": "Azerothian Unity",
    # Age of the Void
    "Particle Physics": "Azerite Refinement",
    "Nuclear Fusion": "Titanforging",
    "Nanotechnology": "Ethereal Technology",
    "Stealth": "Invisibility",                 # Warcraft II mage spell
    "Future Tech": "Secrets of the Void",      # only cosmetic engine code uses this name
}

UNITS = {
    # Warcraft II/III and WoW names, each kept in its Unciv role
    "Worker": "Peasant",
    "Work Boats": "Fishing Skiff",
    "Warrior": "Militia",
    "Trireme": "Longboat",
    "Chariot Archer": "Mounted Archer",
    "Horseman": "Outrider",
    "Composite Bowman": "Ranger",
    "Galleass": "War Galley",
    "Trebuchet": "Ballista",
    "Longswordsman": "Vanguard",
    "Caravel": "Brigantine",
    "Musketman": "Musketeer",
    "Privateer": "Buccaneer",
    "Gatling Gun": "Mountaineer",
    "Artillery": "Mortar Team",
    "Submarine": "Gnomish Submarine",
    "Great War Infantry": "Fusilier",
    "Triplane": "Gyrocopter",
    "Great War Bomber": "Bomber Zeppelin",
    "Infantry": "Shock Trooper",
    "Carrier": "Airship Tender",
    "Battleship": "Dreadnought",
    "Marine": "Kul Tiran Marine",
    "Machine Gun": "Grenadier",
    "Anti-Aircraft Gun": "Flak Cannon",
    "Landship": "War Golem",
    "Fighter": "Gryphon Rider",
    "Bomber": "War Zeppelin",
    "Paratrooper": "Skyguard",
    "Tank": "Siege Engine",
    "Anti-Tank Gun": "Siegebreaker",
    "Atomic Bomb": "Mana Bomb",
    "Rocket Artillery": "Demolisher",
    "Mobile SAM": "Flak Wagon",
    "Guided Missile": "Arcane Missile",
    "Nuclear Missile": "Arcane Annihilator",
    "Helicopter Gunship": "Flying Machine",
    "Nuclear Submarine": "Giant Turtle",
    "Mechanized Infantry": "Mechagnome Trooper",
    "Missile Cruiser": "Juggernaught",
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

# Unit types (shown on every unit). Renamed everywhere they are used as a type:
# "unitType"/"unitTypes" fields, UnitTypes.json, and [bracketed] unit filters.
UNIT_TYPES = {
    "Gunpowder": "Firearm",
    "Ranged Gunpowder": "Ranged Firearm",
    "Armored": "War Machine",
    "Atomic Bomber": "Mana Bomber",
    "Missile": "Arcane Projectile",
    "Helicopter": "Gyro",
    "Aircraft Carrier": "Sky Carrier",
    "Fighter": "Sky Fighter",
    "Bomber": "Sky Bomber",
}

BUILDINGS = {
    # regular buildings (Warcraft II/III and WoW names)
    "Circus": "Fighting Pit",
    "Colosseum": "Arena",
    "Courthouse": "Magistrate's Hall",
    "University": "Arcane Sanctum",
    "Castle": "Keep",
    "Opera House": "Bardic Hall",
    "Constabulary": "City Watch",
    "Theatre": "Beastiary",
    "Forge": "Blacksmith",
    "Harbor": "Shipyard",
    "Seaport": "Docks",
    # v0.11: the remaining generic or real-world building names
    "Monument": "Town Hall",                # the first tier of a Warcraft town hall, before Keep and Castle
    "Aqueduct": "Waterworks",
    "Museum": "Hall of Relics",
    "Mint": "Coin Forge",
    "Amphitheater": "Storyteller's Circle",
    "Arsenal": "Siege Workshop",
    "Garden": "Herb Garden",
    "Public School": "Mage Tower",
    "Military Academy": "Training Grounds",
    "Factory": "Foundry",
    "Hospital": "House of Healing",
    "Stock Exchange": "Auction House",
    "Hydro Plant": "Tidal Works",
    "Police Station": "Guard Tower",
    "Stadium": "Grand Arena",
    "Broadcast Tower": "Arcane Beacon",
    "Military Base": "Fortress",
    "Research Lab": "Arcane Laboratory",
    "Medical Lab": "Alchemy Lab",
    "Solar Plant": "Sun Crystal Array",
    "Recycling Center": "Salvage Yard",
    "Nuclear Plant": "Mana Reactor",
    "Bomb Shelter": "Burrow",
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
    # v0.8: real-world exotics
    "Bananas": "Tel'Abim Bananas",
    "Citrus": "Sunfruit",
    "Sugar": "Honeycomb",
    "Ivory": "Mammoth Ivory",
    "Dyes": "Moonglow Ink",
    "Truffles": "Glowcap",
    "Whales": "Leviathans",
    "Salt": "Deeprock Salt",
    "Jewelry": "Jeweled Trinkets",
    "Porcelain": "Jade Carvings",
    # v0.11: Warcraft goods for the common resources
    "Cattle": "Kodo",                # herd beasts of Kalimdor
    "Deer": "Plainstriders",         # the big flightless birds every hunter in the Barrens knows
    "Gems": "Star Rubies",
    "Spices": "Hot Spices",
    "Pearls": "Black Pearls",
    "Crab": "Crawlers",
    "Copper": "Copper Ore",
}

IMPROVEMENTS = {
    "Oil well": "Azerite Drill",
    "Offshore Platform": "Tidal Drill",
    "Manufactory": "Great Workshop",
    # v0.10: Great Person improvements
    "Academy": "Arcane Academy",          # Great Scientist: a seat of arcane learning (Dalaran, the Violet Citadel)
    "Customs house": "Trade Company",     # Great Merchant: a chartered company like the Steamwheedle Cartel
    "Citadel": "Bastion",                 # Great General: a fortified bastion (Nethergarde, Theramore)
    "Landmark": "Hall of Heroes",         # Great Artist: a monument to legends (the Valley of Heroes)
    "Holy site": "Sacred Grounds",        # Great Prophet: holy ground (Light's Hope Chapel, a moonwell grove)
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
    # v0.8: Warcraft pantheons and beliefs in place of real-world ones
    "Ancestor Worship": "Ancestral Guidance",
    "Desert Folklore": "Tales of the Tol'vir",
    "Faith Healers": "Restorative Spirits",
    "Fertility Rites": "Earth Mother's Bounty",
    "God of craftsmen": "Khaz'goroth's Forge",     # Unciv spelled this "God of Craftsman" before late 2026
    "God of the Open Sky": "An'she's Light",
    "God of the Sea": "Neptulon's Tide",
    "God of War": "Rage of Agamaggan",
    "Goddess of Festivals": "Harvest Festival",
    "Goddess of Love": "Love Is in the Air",
    "Goddess of Protection": "Eonar's Ward",
    "Goddess of the Hunt": "Goldrinn's Hunt",
    "Messenger of the Gods": "Whispers of Elune",
    "Monument to the Gods": "Titan Monoliths",
    "One with Nature": "Cenarius's Embrace",
    "Oral Tradition": "Lorewalkers' Tales",
    "Religious Idols": "Spirit Totems",
    "Sacred Path": "Path of the Ancients",
    "Sacred Waters": "Moonwell Waters",
    "Choral Music": "Hymns of the Light",
    "Feed the World": "Pilgrim's Bounty",
    "Liturgical Drama": "Sacred Pageants",
    "Peace Gardens": "Gardens of Serenity",
    "Swords into Ploughshares": "Lay Down the Blade",
    "Church Property": "Temple Coffers",
    "Interfaith Dialogue": "Council of Faiths",
    "World Church": "Missions Across Azeroth",
    "Just War": "Holy Crusade",
    "Messiah": "Chosen Champion",
    "Religious Texts": "Sacred Tomes",
    # v0.11: the remaining generic beliefs
    "Dance of the Aurora": "Lights of Northrend",
    "Religious Settlements": "Pilgrim Villages",
    "Stone Circles": "Druid Circles",
    "Asceticism": "Path of Discipline",
    "Cathedrals": "Cathedrals of Faith",
    "Divine inspiration": "Inspiration of the Titans",
    "Holy Warriors": "Champions of the Faith",
    "Monasteries": "Cloisters",
    "Pagodas": "Shrines of the Celestials",
    "Religious Art": "Sacred Murals",
    "Religious Center": "Seat of the Faith",
    "Religious Community": "Brotherhood of the Faithful",
    "Ceremonial Burial": "Rites of the Fallen",
    "Initiation Rites": "Rites of Passage",
    "Peace Loving": "Ways of Harmony",
    "Pilgrimage": "Pilgrims' Road",
    "Tithe": "Tithes of the Faithful",
    "Defender of the Faith": "Wardens of the Faith",
    "Holy Order": "Sacred Order",
    "Itinerant Preachers": "Wandering Prophets",
    "Missionary Zeal": "Zeal of the Crusade",
    "Religious Unity": "One Faith, Many Peoples",
    "Reliquary": "Relic Vaults",
}

# Promotions: base name -> new base name; levels (I, II, III) follow automatically.
# Their icons are keyed by the base name.
PROMOTION_BASES = {
    "Dogfighting": "Aerial Combat",
    "Air Targeting": "Aerial Targeting",
    "Air Repair": "Field Repairs",
    "Armor Plating": "Iron Plating",            # Warcraft III armor upgrade
    "Anti-Armor": "Armor Piercing",
    "Operational Range": "Long Flight",
    "Flight Deck": "Aerie Deck",
    # v0.10: Warcraft names for the remaining generic promotions
    "Accuracy": "Deadeye",                  # ranged bonus in open terrain
    "Shock": "Heroic Strike",               # melee bonus in open terrain (the warrior's signature blow)
    "Drill": "Weapon Mastery",              # melee bonus in rough terrain
    "Cover": "Defend",                      # vs ranged attacks: the Warcraft III Footman's Defend
    "Formation": "Spear Wall",              # vs mounted units
    "Blitz": "Bloodlust",                   # an extra attack per turn: the shaman's Bloodlust
    "Logistics": "Rapid Fire",              # an extra ranged attack per turn
    "Targeting": "Broadsides",              # naval bonus vs ships
    "Wolfpack": "Depth Stalker",            # submarine attack bonus
    "Sortie": "Skyguard Patrol",            # extra air interceptions
    "Interception": "Sky Sentinel",         # stronger interceptions
    "Supply": "Ship's Carpenter",           # ships heal outside friendly waters
}
PROMOTIONS = {}
for _k, _v in PROMOTION_BASES.items():
    PROMOTIONS[_k] = _v
    for _lvl in (" I", " II", " III"):
        PROMOTIONS[_k + _lvl] = _v + _lvl

# Policy branches and policies with real-world or modern political names.
POLICIES = {
    "Rationalism": "Arcane Inquiry",
    "Freedom": "Free Peoples",
    "Autocracy": "Dominion",
    "Rationalism Complete": "Arcane Inquiry Complete",
    "Freedom Complete": "Free Peoples Complete",
    "Autocracy Complete": "Dominion Complete",
    "Mandate Of Heaven": "Divine Mandate",
    "Reformation": "Spiritual Renewal",
    "Trade Unions": "Merchant Guilds",
    "Secularism": "Apprentice Mages",
    "Scientific Revolution": "Arcane Revolution",
    "Constitution": "Charter of Kings",
    "Universal Suffrage": "Common Voice",
    "Civil Society": "Civic Guilds",
    "Free Speech": "Open Council",
    "Democracy": "House of Nobles",
    "Populism": "Rallying Cry",
    "Fascism": "Iron Will",
    "Police State": "Inquisition",
    "Nationalism": "Ancestral Pride",
    "Socialism": "Common Granaries",
    "Communism": "Collective Labor",
    "Planned Economy": "Grand Stewardship",
    # v0.9: full Warcraft policy tree
    "Tradition": "Old Kingdoms",
    "Aristocracy": "Noble Houses",
    "Legalism": "Strom's Legacy",
    "Oligarchy": "Keep and Garrison",
    "Landed Elite": "Crownlands",
    "Monarchy": "High Kingship",
    "Liberty": "Frontier",
    "Republic": "Free Towns",
    "Citizenship": "Ready to Work",
    "Collective Rule": "Pioneers' Charter",
    "Representation": "Town Councils",
    "Meritocracy": "Kingsroads",
    "Honor": "Blood and Thunder",
    "Warrior Code": "Lok'tar Ogar",
    "Discipline": "Shield Wall",
    "Military Tradition": "Veterans' Lore",
    "Military Caste": "Honor Guard",
    "Professional Army": "Kor'kron Regulars",
    "Piety": "Devotion",
    "Organized Religion": "Ordained Clergy",
    "Theocracy": "Temple Tithes",
    "Free Religion": "Many Paths",
    "Patronage": "Diplomacy",
    "Philantropy": "Gilded Gifts",
    "Aesthetics": "Courtly Grace",
    "Scholasticism": "Kirin Tor Exchange",
    "Cultural Diplomacy": "Embassies",
    "Educated Elite": "Heroes of Many Lands",
    "Commerce": "Trade Princes",
    "Naval Tradition": "Admiralty",
    "Merchant Navy": "Harbor Masters",
    "Mercantilism": "Steamwheedle Charter",
    "Protectionism": "Cartel Monopolies",
    "Humanism": "Wonders of the Arcane",
    "Free Thought": "Open Libraries",
    "Sovereignty": "Patrons of Dalaran",
    "Militarism": "Warchief's Coffers",
    "Total War": "Iron Horde Doctrine",
    "Order": "Unity",
    "United Front": "Brothers in Arms",
    "Tradition Complete": "Old Kingdoms Complete",
    "Liberty Complete": "Frontier Complete",
    "Honor Complete": "Blood and Thunder Complete",
    "Piety Complete": "Devotion Complete",
    "Patronage Complete": "Diplomacy Complete",
    "Commerce Complete": "Trade Princes Complete",
    "Order Complete": "Unity Complete",
}

ALL = {}
for _m in (ERAS, TECHS, UNITS, BUILDINGS, RESOURCES, IMPROVEMENTS, NATURAL_WONDERS,
           TERRAIN_FEATURES, BELIEFS, PROMOTIONS, POLICIES):
    for _k, _v in _m.items():
        if _k != _v:
            assert _k not in ALL, _k
            ALL[_k] = _v
assert len(set(ALL.values())) == len(ALL), "duplicate new names"
assert not set(UNIT_TYPES.values()) & set(ALL.values()), "type name clashes with another name"

# Folders whose images are keyed by entity name and must follow a rename.
IMAGE_FOLDERS = ["UnitIcons", "BuildingIcons", "TechIcons", "ResourceIcons",
                 "ImprovementIcons", "TileSets/AbsoluteUnits/Units",
                 "TileSets/HexaRealm/Units", "TileSets/FantasyHex/Units",
                 "TileSets/HexaRealm/Tiles", "TileSets/FantasyHex/Tiles",
                 "TileSets/Minimal/Tiles", "UnitPromotionIcons", "PolicyIcons",
                 "PolicyBranchIcons"]
