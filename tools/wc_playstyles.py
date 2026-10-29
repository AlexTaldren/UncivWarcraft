"""Race play styles, heroes, travel, Mana and faction tags (v0.12).

Everything here uses this mod's names (after renames). build.py applies it after the
race unique units (race_units.py) are in place.
"""

def _lore(*t):
    return [{"text": x} for x in t]


# ---------------------------------------------------------------- faction tags
# Untyped tag uniques: civilization and unit filters ("vs [Horde] units", "for [Undead]
# Civilizations") match them through Unciv's nation tag lookup.
TAGS = {
    "Humans": ["Alliance"], "Dwarves": ["Alliance"], "Gnomes": ["Alliance"], "Night Elves": ["Alliance"],
    "Draenei": ["Alliance"], "Worgen": ["Alliance"], "High Elves": ["Alliance"],
    "Orcs": ["Horde"], "Trolls": ["Horde"], "Tauren": ["Horde"], "Forsaken": ["Horde", "Undead"],
    "Blood Elves": ["Horde"], "Goblins": ["Horde"],
    "Pandaren": [], "Scourge": ["Undead"],
    "Dark Iron Dwarves": ["Alliance"], "Kul Tirans": ["Alliance"], "Zandalari Trolls": ["Horde"],
    "Naga": [], "Nightborne": ["Horde"], "Highmountain Tauren": ["Horde"],
}
RIVALRY = {   # old enemies fight a little harder against each other
    "Alliance": "[+10]% Strength <for [Military] units> <vs [Horde] units>",
    "Horde": "[+10]% Strength <for [Military] units> <vs [Alliance] units>",
}

# ---------------------------------------------------------------- per-race play styles
# Extra nation uniques, and the line added to the nation's description.
PLAYSTYLE = {
    "Forsaken": (["[+1 Food, +1 Production, +1 Science] from [Plagued Land] tiles [in all cities]",
                  "[+10] HP when healing <for [Land] units> <in [Plagued Land] tiles>"],
                 "Plague: Plagued Land feeds the Forsaken (+1 Food, +1 Production, +1 Science) and heals their units faster; Peasants can spread it."),
    "Night Elves": (["[+1 Food] from [Forest] tiles [in all cities]",
                     "[+1 Culture] from [Ancient Woods] tiles [in all cities]"],
                    "Guardians of the Forest: forests give +1 Food, and Night Elves never cut them down. Wisps tend the land."),
    "Orcs": (["[+10]% [Production] [in all cities] <when at war>",
              "[+10]% Strength <for [Military] units> <when at war>",
              "[-10]% [Culture] [in all cities] <when not at war>"],
             "The Horde Thrives on War: +10% Production and +10% Strength while at war, -10% Culture in peace."),
    "Trolls": (["[+1 Faith] from [Jungle] tiles [in all cities]",
                "May choose [1] additional [Follower] beliefs when [founding] a religion"],
               "Voodoo: +1 Faith from jungle tiles and one extra Follower belief for their religion."),
    "Tauren": (["[+1 Faith] from [Plains] tiles without [Farm] [in all cities]",
                "[+1 Culture] from [Hill] tiles without [Mine] [in all cities]"],
               "The Earth Mother's Gift: untouched land is sacred. Unfarmed plains give +1 Faith; hills without mines give +1 Culture."),
    "Dwarves": (["[+1 Science, +1 Culture] from [Titan Ruins] tiles [in all cities]"],
                "Explorers' League: Titan Ruins give +1 Science and +1 Culture, ancient ruins can hold Titan relics only dwarves can read, and Deep Mines replace Mines."),
    "Gnomes": ([], "Brilliant and Reckless: gnomish experiments can bring great breakthroughs, or explosions."),
    "Goblins": (["[Gold] cost of purchasing items in cities [-20]%",
                 "[-10]% [Production] [in all cities]",
                 "Upon capturing a city, receive [10] times its [Gold] production as [Gold] immediately"],
                "Everything Has a Price: buying costs 20% less Gold, captured cities pay out 10 turns of their Gold, but Production is 10% lower."),
    "Blood Elves": (["[-1 Happiness] [in all cities] <starting from the [Age of the Third War]> <if [Sunwell Plateau] is not constructed by anybody> <without [Arcane Crystals]>",
                     "[+1 Happiness] from every [Magisters' Sanctum]"],
                    "Mana Addiction: from the Age of the Third War, when the Sunwell fell, every city suffers -1 Happiness until the empire controls Arcane Crystals or someone restores the Sunwell (the Sunwell Plateau wonder). Each Magisters' Sanctum eases the craving (+1 Happiness)."),
    "High Elves": (["[+25]% Strength for cities", "[+10]% growth [in all cities]"],
                   "The Runestone Barrier: cities are 25% stronger. Blessed by the Sunwell, they grow 10% faster."),
    "Draenei": (["Free [Settler] appears <upon founding a city> <before turn number [4]>",
                 "[+25]% Strength <for [Military] units> <vs [Barbarian] units>",
                 "[+1] Movement <for [Religious] units>"],
                "Exiles: the survivors of the Exodar crash found a second city at once with a free Settler. +25% Strength against barbarians and demons; missionaries move faster."),
    "Worgen": ([], "The Curse: Worgen units shift between human and worgen form, and the worgen curse claims those they slay."),
    "Pandaren": (["Triggers a [The Wandering Isle's Choice] event <upon entering the [Age of the Dark Portal]> <hidden from users>",
                  "Enables embarkation for land units"],
                 "Riding Shen-zin Su: Pandaren can embark from the start of the game. The Wandering Isle's Choice: in the Age of the Dark Portal the Pandaren choose the Alliance's Tushui way, the Horde's Huojin way, or neutrality."),
    "Dark Iron Dwarves": (["[+1 Production] from [{Hill} {Mine}] tiles [in all cities]"],
                          "Children of the Mountain's Fire: mines dug into hills give +1 Production; Molten Fields give +1 Gold."),
    "Kul Tirans": (["[+1] Sight <for [Water] units>",
                    "[+25]% Production when constructing [Water] units [in all cities]"],
                   "Tidesages: ships see farther and are built 25% faster."),
    "Zandalari Trolls": (["[+1 Faith, +1 Culture] from [{Jungle} {Camp}] tiles [in all cities]",
                          "[+10]% Strength <for [Mounted] units>"],
                         "Children of the Loa: jungle camps give +1 Faith and +1 Culture, and their dinosaur riders fight 10% harder."),
    "Naga": (["[+1 Gold] from [Coast] tiles [in all cities]",
              "[+25]% Production when constructing [Water] units [in all cities]"],
             "Children of the Deep: the naga embark from the start and fight 15% harder on coasts; coast tiles give +1 Production and +1 Gold, and ships are built 25% faster."),
    "Nightborne": (["[+1 Science] from every [Arcway]",
                    "[+10]% Great Person generation [in all cities]"],
                   "Arcane Ingenuity: +15% Science, Arcane Crystals give +2 Science, and Great People come 10% faster. Arcways replace the Arcane Sanctum."),
    "Highmountain Tauren": (["[+10]% Strength <for [Mounted] units>",
                             "[+1 Production] from [{Hill} {Mine}] tiles [in all cities]"],
                            "Children of Huln: units fight 20% harder in hills, hills give +1 Food and mines on hills +1 Production; Thunderhoof riders fight 10% harder."),
    "Scourge": (["[-50]% Food consumption by [Population] [in all cities]",
                 "[+2 Production, +1 Science] from [Plagued Land] tiles [in all cities]",
                 "[1] population in a random city <upon defeating a [Military] unit> <with [50]% chance>",
                 "[+10] HP when healing <for [Land] units> <in [Plagued Land] tiles>"],
                "The Plague of Undeath: the undead eat half as much, Plagued Land gives +2 Production and +1 Science, fallen enemies rise to swell their cities, and key Scourge buildings need blight nearby. Acolytes spread the blight."),
}

# ---------------------------------------------------------------- improvements
IMPROVEMENTS = [
    {"name": "Spread Blight", "terrainsCanBeBuiltOn": ["Grassland", "Plains", "Tundra", "Snow"],
     "turnsToBuild": 4, "production": 2,
     "uniques": ["Only available <for [Undead] Civilizations>",
                 "Cannot be built on [Forest] tiles", "Cannot be built on [Jungle] tiles",
                 "Cannot be built on [Marsh] tiles", "Cannot be built on [Hill] tiles",
                 "Turn this tile into a [Plagued Land] tile",
                 "Remove [Spread Blight] improvements from this tile"],
     "civilopediaText": _lore("The undead spread their plague into the soil itself, turning it into Plagued Land. Only the Scourge and the Forsaken can do this; the improvement disappears once the blight takes hold.")},
]
# Dwarves' Deep Mine: copy of Mine with more
DEEP_MINE = {"name": "Deep Mine", "replaces": "Mine", "uniqueTo": "Dwarves", "addStats": {"gold": 1},
             "civilopediaText": _lore("Dwarven mines go deeper than anyone else's, down to the veins of the Titans' forge. +1 Gold over a normal Mine.")}

# improvements other races may not use: (improvement, unique)
RESTRICT_IMPROVEMENTS = [
    ("Remove Forest", "Unavailable <for [Night Elves] Civilizations>"),
    ("Remove Plagued Land", "Unavailable <for [Undead] Civilizations>"),
]

# ---------------------------------------------------------------- extra units
# (base (mod name), overrides) -- uniqueTo/replaces are explicit here
UNITS = [
    ("Peasant", {"name": "Wisp", "replaces": "Peasant", "uniqueTo": "Night Elves", "cost": 55,
                 "addUniques": ["Double movement in [Forest]"],
                 "civilopediaText": _lore("Wisps are the spirits of departed night elves. They tend the land for their people and drift through the forests with ease.",
                                          "Cheaper than a Peasant and moves at double speed through forests.")}),
    ("Ranger", {"name": "Gilnean Hunter", "uniqueTo": "Worgen", "strength": 8, "rangedStrength": 11,
                "addUniques": ["Can transform to [Worgen Stalker]", "Unbuildable"],
                "civilopediaText": _lore("A Worgen Stalker in human form: a Gilnean hunter with a longbow. Can shift back into worgen form.")}),
    ("Rifleman", {"name": "Worgen Ravager", "uniqueTo": "Worgen", "strength": 40,
                  "addUniques": ["Can transform to [Gilnean Rifleman]", "May capture killed [Military] units",
                                 "Unbuildable"],
                  "civilopediaText": _lore("A Gilnean Rifleman who has let the beast loose. The curse spreads to those it slays: it may capture the units it kills. Can shift back into human form.")}),
]
UNIT_EXTRA_UNIQUES = {   # added to existing unique units
    "Worgen Stalker": ["Can transform to [Gilnean Hunter]", "May capture killed [Military] units"],
    "Gilnean Rifleman": ["Can transform to [Worgen Ravager]"],
}

# ---------------------------------------------------------------- buildings
BUILDINGS = [
    {"name": "Tushui Monastery", "uniqueTo": "Pandaren", "culture": 2, "cost": 1,
     "uniques": ["Unbuildable", "[+15]% Strength <for [Military] units> <when defending>",
                 "[+10]% Strength <for [Military] units> <vs [Horde] units>"],
     "civilopediaText": _lore("The Tushui follow Aysa Cloudsinger's path of discipline and justice, and fight beside the Alliance. +15% Strength when defending, +10% against the Horde, +2 Culture.")},
    {"name": "Huojin Training Hall", "uniqueTo": "Pandaren", "production": 2, "cost": 1,
     "uniques": ["Unbuildable", "[+15]% Strength <for [Military] units> <when attacking>",
                 "[+10]% Strength <for [Military] units> <vs [Alliance] units>"],
     "civilopediaText": _lore("The Huojin follow Ji Firepaw's path of bold action, and fight beside the Horde. +15% Strength when attacking, +10% against the Alliance, +2 Production.")},
]
MAGE_TOWER_PORTALS = "All newly-trained [Military] units [in this city] receive the [Portal Adept] promotion"

PORTAL_MANA = 10
# A paradrop can't carry a resource cost itself, so the portal is two steps: units trained
# in a Mage Tower city are Portal Adepts and can, from one of your cities, spend Mana to
# open a portal (a one-turn Portal Attunement status that allows the jump).
TRAVEL_PROMOTIONS = [
    {"name": "Portal Adept",
     "uniques": ["[This Unit] gains the [Portal Attunement] status for [1] turn(s) <in [City center] tiles> <for [0] movement> <costs [%d] [Mana]>" % PORTAL_MANA],
     "civilopediaText": _lore("Trained near a Mage Tower: from one of your cities, this unit can open a portal for %d Mana, then step through it to another of your cities up to 20 tiles away on the same turn." % PORTAL_MANA)},
    {"name": "Portal Attunement",
     "uniques": ["May Paradrop to [{your} {City center}] tiles up to [20] tiles away <in [City center] tiles>"],
     "civilopediaText": _lore("A portal stands open for this unit: it can step through to one of your cities up to 20 tiles away.")},
]

# ---------------------------------------------------------------- cleansing (v0.13)
# Corrupted land (Plagued Land, Fel-Scorched Land) can only be cleansed by a priestly unit,
# bought with Faith. Peasants and other workers can no longer remove it.
CLEANSE = ["Remove Plagued Land", "Remove Fel-Scorched Land"]
CORRUPT_TILES = ["Plagued Land", "Fel-Scorched Land"]
CLERIC = {"name": "Cleric", "unitType": "Civilian", "movement": 2, "cost": 80, "requiredTech": "Priesthood",
          "uniques": ["Can build [Remove Plagued Land] improvements on tiles",
                      "Can build [Remove Fel-Scorched Land] improvements on tiles",
                      "Can build [Remove Plagued Land] improvements at a [+50]% rate",
                      "Can build [Remove Fel-Scorched Land] improvements at a [+50]% rate",
                      "Unbuildable", "Can be purchased with [Faith] [in all cities]",
                      "Unavailable <for [Undead] Civilizations>", "Automation is a primary action"],
          "civilopediaText": _lore("Priests, druids and shamans who cleanse land corrupted by the Scourge's plague or the Legion's fel fire, restoring it to its natural state.",
                                   "Bought with Faith. Only they can cleanse Plagued Land and Fel-Scorched Land, and they do it 50% faster than a worker could. The undead have no use for them.")}
# race -> (name, lore); each replaces the Cleric for that race
CLERICS = {
    "Humans": ("Northshire Cleric", "Clerics of Northshire Abbey, who carry the Holy Light into blighted fields."),
    "Dwarves": ("Dwarven Priest", "Priests of Ironforge who call on the Light and the earth to heal the land."),
    "Gnomes": ("Decontaminator", "Gnomish specialists in radiation suits, veterans of cleaning up Gnomeregan. They treat plague like any other contamination."),
    "Night Elves": ("Cenarion Druid", "Druids of the Cenarion Circle who coax life back into dead soil."),
    "Draenei": ("Anchorite", "Draenei anchorites who channel the Light of the naaru to purify corrupted ground."),
    "Worgen": ("Harvest Witch", "Gilnean harvest witches who know the old ways of the land and its healing."),
    "High Elves": ("Lightwarden", "Lightwardens of Quel'Thalas who burn away corruption with holy light."),
    "Blood Elves": ("Sunfury Priest", "Priests of the sun who purify the land with the Light of the Sunwell."),
    "Orcs": ("Earthen Shaman", "Shamans who beg the elements to forgive the land and heal it."),
    "Trolls": ("Witch Doctor", "Troll witch doctors whose voodoo can drive the sickness out of the soil."),
    "Tauren": ("Sunwalker", "Tauren paladins of An'she, the Sun, who scour corruption from the Earth Mother's body."),
    "Pandaren": ("Mistweaver", "Pandaren monks whose healing mists restore balance to the land."),
    "Goblins": ("Hazmat Crew", "Goblin cleanup crews in rubber suits. They'll scrub anything off the ground, for a fee."),
    "Dark Iron Dwarves": ("Flamekeeper", "Dark Iron priests who burn the corruption out of the land with forge-fire."),
    "Kul Tirans": ("Tidesage", "Tidesages of the Storm, who wash blight and fel from the land with the power of the sea."),
    "Zandalari Trolls": ("Loa Speaker", "Zandalari priests who call on the loa to drive the sickness from the earth."),
    "Naga": ("Tidepriestess", "Naga priestesses who wash corruption from the shore with the power of the tides."),
    "Nightborne": ("Shal'dorei Mender", "Nightborne healers who burn blight and fel from the land with pure arcane light."),
    "Highmountain Tauren": ("Spiritwalker", "Highmountain spiritwalkers who ask the ancestors to heal the wounded land."),
}
ICONS_CLERIC = "hand_light"

# ---------------------------------------------------------------- Mana
MANA = {"name": "Mana", "resourceType": "Strategic",
        "uniques": ["Stockpiled", "Cannot be traded"],
        "civilopediaText": _lore("Arcane energy gathered by your mages and stored for spellcraft. Every capital gathers a little each turn, and each race has its own sources (Moonwells, Voodoo Lounges, Great Totems, Necropolises, Arcane Sanctums, Mage Towers, Arcane Crystals...). Spellcasters, heroes, magical buildings and wonders, Mage Tower portals and some event choices spend it.")}
MANA_SOURCES = {
    "Palace": 1,                                   # every capital gathers a little
    "Arcane Sanctum": 1, "Mage Tower": 2, "Magisters' Sanctum": 2,
    # v0.14: a source for every race, in a building it already has
    "Chapel of the Light": 1, "Altar of Storms": 1, "Voodoo Lounge": 1, "Great Totem": 1,
    "Moonwell": 1, "Dwarven Forge": 1, "Tinker's Workshop": 1, "Goblin Bazaar": 1,
    "Crystal Sanctum": 1, "Gilnean Bulwark": 1, "Runestone": 1, "Brewery": 1,
    "Apothecarium": 1, "Necropolis": 1, "Ziggurat": 1,
    # v0.17
    "Mana Forge": 1, "Elven Spire": 1, "Loa Shrine": 1, "Spirit Lodge": 1, "Crystal Hall": 1,
    "Shadowforge Furnace": 1, "Admiralty Drydock": 1, "Golden Pyramid": 1, "Cathedral of Light": 1,
    # content pass (Oct 2026)
    "Coral Spawning Pool": 1, "Arcway": 2, "Ironhorn Lodge": 1,
}
# Arcane Crystals deposits feed the arcane schools
MANA_WITH_CRYSTALS = {"Arcane Sanctum": 1, "Mage Tower": 1}
MANA_COSTS = {"Mage": 10, "Arcane Missile": 15, "Mana Bomb": 40, "Arcane Annihilator": 60,
              # v0.14: each race's spellcasters and magic-touched units
              "Spellbreaker": 6, "Blood Knight": 10, "Batrider": 15, "Death Knight": 12, "Frost Wyrm": 20,
              "Abomination": 8, "Meat Wagon": 8, "Glaive Thrower": 8, "Gnomish Bombardier": 10,
              "Vindicator": 10, "Kodo Beast": 6, "Headhunter": 4, "Worgen Stalker": 4,
              "Farstrider": 6, "Brewmaster": 8, "Goblin Sapper": 6, "Ram Rider": 6,
              # v0.17
              "Knight of the Silver Hand": 10, "Lightforged Warframe": 15, "Ranger-Lord": 8, "Dragonhawk Rider": 10,
              "Cloud Serpent Rider": 12, "Crypt Fiend": 10, "Mountain Giant": 12, "Troll Berserker": 6,
              "Fireguard": 6, "Direhorn Rider": 8,
              # content pass (Oct 2026)
              "Snap Dragon": 6, "Spellblade": 8, "Duskwatch Sentinel": 6}
HERO_MANA = 30          # every hero costs this to recruit
# magical buildings and wonders
BUILDING_MANA_COSTS = {"Mage Tower": 20, "Arcane Laboratory": 40, "Mana Reactor": 60, "Runestone": 10,
                       "The Violet Citadel": 15, "Caverns of Time": 30, "College of Magi": 30,
                       "Karazhan": 50, "Tower of Azora": 40, "Sunwell Plateau": 60, "Wyrmrest Temple": 40,
                       "Mana Bomb Project": 80, "The Nighthold": 60, "Great Arcane Ward": 80,
                       "Celestial Planetarium": 60}

# ---------------------------------------------------------------- Dwarf-only ruins
RUINS = [
    {"name": "Titan relics", "notification": "Our dwarves read the Titan runes in the ruins and recover ancient knowledge! (+[scienceAmount] Science)",
     "uniques": ["Gain [60] [Science] <(modified by game speed)>", "Only available <for [Dwarves] Civilizations>"]},
    {"name": "an Explorers' League survey", "notification": "An Explorers' League survey cache: maps of the whole region!",
     "uniques": ["From a randomly chosen tile [6] tiles away from the ruins, reveal tiles up to [6] tiles away with [90]% chance",
                 "Only available <for [Dwarves] Civilizations>"]},
]

# ---------------------------------------------------------------- heroes
# One per race, limited to one per empire. Hero type: own promotion line. Strength grows
# with the eras, as a Warcraft III hero levels up.
HERO_TYPE = {"name": "Hero", "movementType": "Land"}
HERO_SCALING = ["[+40]% Strength <starting from the [Age of the Dark Portal]>",
                "[+40]% Strength <starting from the [Age of the Lich King]>",
                "[+60]% Strength <starting from the [Age of the Legion]>"]
HERO_COMMON = ["Limited to [1] per Civilization", "[+15]% Strength bonus for [Military] units within [2] tiles",
               "Heals [10] damage if it kills a unit", "Never appears as a Barbarian unit", "Cannot be purchased"]
# race -> (name, title, signature uniques, lore)
HEROES = {
    "Humans": ("Uther the Lightbringer", "Paladin", ["All adjacent units heal [+10] HP when healing"],
               "The first paladin of the Order of the Silver Hand. The Light heals those who fight beside him."),
    "Orcs": ("Grom Hellscream", "Blademaster", ["[+25]% Strength <when attacking>"],
             "Chieftain of the Warsong clan, whose blade and fury broke the demigod Cenarius."),
    "Night Elves": ("Malfurion Stormrage", "Keeper of the Grove", ["[+25]% Strength <when fighting in [Forest] tiles>", "Double movement in [Forest]"],
                    "The first druid of the night elves, master of the Emerald Dream and the wild."),
    "Dwarves": ("Muradin Bronzebeard", "Mountain King", ["[+25]% Strength <when fighting in [Hill] tiles>", "[+25]% Strength <when defending>"],
                "Brother of King Magni, a mountain king who hurls storm hammers at his foes."),
    "Gnomes": ("Kelsey Steelspark", "Infiltrator", ["Ignores Zone of Control", "[+1] Movement"],
               "SI:7's finest gnome, who led the fight to retake Gnomeregan."),
    "Tauren": ("Baine Bloodhoof", "Tauren Chieftain", ["[+25]% Strength <when defending>", "All adjacent units heal [+5] HP when healing"],
               "High Chieftain of the tauren after his father, steady as the earth itself."),
    "Trolls": ("Rokhan", "Shadow Hunter", ["All adjacent units heal [+10] HP when healing", "[+25]% Strength <when fighting in [Jungle] tiles>"],
               "Darkspear shadow hunter and voice of the loa at Vol'jin's side."),
    "Blood Elves": ("Kael'thas Sunstrider", "Blood Mage", ["[+25]% Strength <vs [Archery] units>", "[+25]% Strength <when attacking>"],
                    "Prince of Quel'Thalas and master of fire and arcane, who renamed his people the sin'dorei."),
    "High Elves": ("Alleria Windrunner", "Ranger", ["[+2] Sight", "[+25]% Strength <when fighting in [Forest] tiles>"],
                   "Eldest of the Windrunner sisters, the finest archer of Quel'Thalas."),
    "Pandaren": ("Chen Stormstout", "Brewmaster", ["[+25]% Strength <when defending>", "[+15] HP when healing"],
                 "The wandering brewmaster who first brought word of the pandaren to the Horde and the Alliance."),
    "Forsaken": ("Nathanos Blightcaller", "Champion of the Banshee Queen", ["[+25]% Strength <vs [Alliance] units>", "[+10] HP when healing"],
                 "Once the only human ranger lord of Quel'Thalas, now Sylvanas's undead champion."),
    "Draenei": ("Maraad", "Vindicator", ["[+50]% Strength <vs [Barbarian] units>", "All adjacent units heal [+5] HP when healing"],
                "A vindicator of the draenei, sworn enemy of the Burning Legion."),
    "Goblins": ("Gazlowe", "Tinker", ["[+50]% Strength <vs cities>", "[+1] Movement"],
                "Boss of Ratchet, the goblin who built Orgrimmar for Thrall, for a reasonable fee."),
    "Worgen": ("Darius Crowley", "Lord of the Gilneas Liberation Front", ["[+25]% Strength <when fighting in [Forest] tiles>", "May capture killed [Military] units"],
               "The rebel lord who held the Greymane Wall against his own king, then fought for Gilneas as a worgen."),
    "Dark Iron Dwarves": ("Dagran Thaurissan", "Emperor of the Dark Irons", ["[+25]% Strength <when defending>", "[+25]% Strength <vs cities>"],
                          "The Dark Iron emperor who ruled from Shadowforge City and dared to make a Bronzebeard princess his queen."),
    "Kul Tirans": ("Daelin Proudmoore", "Grand Admiral", ["[+25]% Strength <when attacking>", "[+1] Movement"],
                   "Lord Admiral of Kul Tiras and hero of the Second War, father of Jaina."),
    "Zandalari Trolls": ("Rastakhan", "King of the Zandalari", ["[+25]% Strength <when defending>", "All adjacent units heal [+10] HP when healing"],
                         "The long-reigning king of Zandalar, who bargained with the loa of death to keep his empire alive."),
    "Naga": ("Lady Vashj", "Sea Witch", ["[+25]% Strength <when fighting in [Coast] tiles>", "May attack when embarked", "[+1] Movement"],
             "Azshara's most powerful handmaiden, who led the naga out of the depths and served Illidan at Coilfang Reservoir."),
    "Nightborne": ("Grand Magistrix Elisande", "Chronomancer", ["[+25]% Strength <when attacking>", "[+1] Movement"],
                   "The ruler of Suramar for ten thousand years, a mistress of time magic who bent the flow of battle to her will."),
    "Highmountain Tauren": ("Huln Highmountain", "Hero of the Tribes", ["[+25]% Strength <when fighting in [Hill] tiles>", "All adjacent units heal [+5] HP when healing"],
                            "The legendary chieftain who united the tribes of Highmountain against the Legion ten thousand years ago."),
    "Scourge": ("Kel'Thuzad", "Lich", ["[+25]% Strength <vs [Alliance] units>", "[+25]% Strength <when attacking>"],
                "Archmage of Dalaran turned necromancer, founder of the Cult of the Damned and the Lich King's first lieutenant."),
}
HERO_BASE = "Vanguard"     # stats template (copied, then given the Hero type)
HERO_STATS = {"strength": 20, "cost": 160, "movement": 2, "requiredTech": "Bronze Working", "requiredResource": None}

HERO_PROMOTIONS = [
    {"name": "Hero's Might I", "uniques": ["[+15]% Strength"]},
    {"name": "Hero's Might II", "prerequisites": ["Hero's Might I"], "uniques": ["[+15]% Strength"]},
    {"name": "Commanding Presence", "prerequisites": ["Hero's Might I"], "uniques": ["[+10]% Strength bonus for [Military] units within [2] tiles"]},
    {"name": "Second Wind", "uniques": ["[+15] HP when healing"]},
    {"name": "Battle-Hardened", "prerequisites": ["Second Wind"], "uniques": ["[+20]% Strength <when defending>"]},
    {"name": "Swift Strider", "prerequisites": ["Second Wind"], "uniques": ["[+1] Movement"]},
    {"name": "Legend of Azeroth", "prerequisites": ["Hero's Might II", "Battle-Hardened"],
     "uniques": ["[+15]% Strength", "Heals [25] damage if it kills a unit"]},
]
HERO_PROMO_LORE = {
    "Hero's Might": "The hero grows stronger with every battle.",
    "Commanding Presence": "Armies rally around the hero's banner.",
    "Second Wind": "The hero shrugs off wounds that would fell a lesser warrior.",
    "Battle-Hardened": "Veteran of a hundred battles, the hero is hard to bring down.",
    "Swift Strider": "The hero moves across the battlefield with uncanny speed.",
    "Legend of Azeroth": "Songs are sung of this hero across all of Azeroth.",
}

# ---------------------------------------------------------------- icons
ICONS_UNITS = {"Wisp": ("sparkle", "leaf"), "Gilnean Hunter": ("bow", "wolf"), "Worgen Ravager": ("wolf", "fist")}
ICONS_BUILDINGS = {"Tushui Monastery": ("pagoda", "shield"), "Huojin Training Hall": ("pagoda", "flame")}
ICONS_IMPROVEMENTS = {"Spread Blight": ("skull", "wave"), "Deep Mine": ("pick", "gem")}
ICONS_RESOURCES = {"Mana": ("orb", "sparkle")}
ICONS_PROMOTIONS = {"Hero's Might": ("crown", "sword"), "Commanding Presence": ("crown", "banner"),
                    "Second Wind": ("crown", "heart"), "Battle-Hardened": ("crown", "shield"),
                    "Swift Strider": ("crown", "boot"), "Legend of Azeroth": ("crown", "star"),
                    "Portal Attunement": ("portal", "orb"), "Portal Adept": ("portal", "sparkle")}
HERO_ICON_BADGE = {"Humans": "hammer", "Orcs": "axe", "Night Elves": "leaf", "Dwarves": "hammer", "Gnomes": "gear",
                   "Tauren": "totem", "Trolls": "mask", "Blood Elves": "flame", "High Elves": "bow",
                   "Pandaren": "chalice", "Forsaken": "skull", "Draenei": "naaru", "Goblins": "bomb",
                   "Worgen": "wolf", "Scourge": "skull", "Dark Iron Dwarves": "flame", "Kul Tirans": "anchor",
                   "Zandalari Trolls": "coins", "Naga": "wave", "Nightborne": "orb", "Highmountain Tauren": "totem"}
