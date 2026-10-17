"""Warcraft terrain features and natural landmarks added to the ruleset.

Features are placed by the Azeroth map builder (azeroth.py); none of them generate on
random maps. Fel and plague can be cleansed by Clerics ("Remove ..." improvements).
"""
NO_RANDOM = "Doesn't generate naturally"
LAND = ["Grassland", "Plains", "Desert", "Tundra", "Snow", "Hill"]

FEATURES = [
    {"name": "Fel-Scorched Land", "type": "TerrainFeature", "food": -1, "production": 2,
     "movementCost": 1, "defenceBonus": -0.1, "unbuildable": True,
     "occursOn": ["Grassland", "Plains", "Desert", "Tundra", "Hill"],
     "uniques": [NO_RANDOM, "Units ending their turn on this terrain take [10] damage"],
     "civilopediaText": [{"text": "Earth scarred by the Burning Legion's fel magic, where green fire still smoulders in the cracks. Rich in raw power but poisonous to crops, and it burns any unit that lingers. Clerics (bought with Faith once your people have learned Priesthood) can cleanse it."}]},
    {"name": "Plagued Land", "type": "TerrainFeature", "food": -1, "production": -1,
     "movementCost": 1, "defenceBonus": -0.1, "unbuildable": True,
     "occursOn": ["Grassland", "Plains", "Tundra", "Snow", "Hill"],
     "uniques": [NO_RANDOM],
     "civilopediaText": [{"text": "Ground blighted by the Scourge's plague of undeath: grey soil, bones and bubbling slime. Little grows here until it is cleansed. Clerics (bought with Faith once your people have learned Priesthood) can cleanse it."}]},
    {"name": "Ancient Woods", "type": "TerrainFeature", "food": 1, "production": 1, "culture": 1,
     "overrideStats": True, "movementCost": 2, "defenceBonus": 0.25, "unbuildable": True,
     "occursOn": ["Grassland", "Plains", "Tundra", "Hill"],
     "uniques": [NO_RANDOM, "Rough terrain", "Vegetation", "Blocks line-of-sight from tiles at same elevation"],
     "civilopediaText": [{"text": "The old forests of the night elves, tall violet trees watched over by wisps and ancients. They cannot be cut down, and they inspire those who live beside them."}]},
    {"name": "Bamboo Grove", "type": "TerrainFeature", "food": 2, "production": 1,
     "overrideStats": True, "movementCost": 2, "defenceBonus": 0.25, "unbuildable": True,
     "occursOn": ["Grassland", "Plains", "Hill"],
     "uniques": [NO_RANDOM, "Rough terrain", "Vegetation", "Blocks line-of-sight from tiles at same elevation"],
     "civilopediaText": [{"text": "Swaying stands of bamboo, as on the back of Shen-zin Su, the Wandering Isle. Feeds people and builds their homes alike."}]},
    {"name": "Molten Fields", "type": "TerrainFeature", "food": -1, "production": 2,
     "movementCost": 2, "defenceBonus": -0.1,
     "occursOn": ["Desert", "Plains", "Tundra", "Hill"],
     "uniques": [NO_RANDOM, "Rough terrain"],
     "civilopediaText": [{"text": "Black volcanic rock split by rivers of lava, as in the Burning Steppes and the Searing Gorge. Hard to cross and hard to farm, but full of ore and heat for the forge."}]},
    {"name": "Crystal Grove", "type": "TerrainFeature", "production": 1, "science": 2,
     "overrideStats": True, "movementCost": 2, "defenceBonus": 0.15, "unbuildable": True,
     "occursOn": ["Grassland", "Plains", "Tundra", "Snow", "Hill"],
     "uniques": [NO_RANDOM, "Rough terrain", "Blocks line-of-sight from tiles at same elevation"],
     "civilopediaText": [{"text": "Trees and spires turned to singing crystal by arcane power, as in Crystalsong Forest. Scholars come from far away to study them."}]},
    {"name": "Titan Ruins", "type": "TerrainFeature", "science": 1, "culture": 1,
     "movementCost": 1, "defenceBonus": 0.25,
     "occursOn": ["Grassland", "Plains", "Desert", "Tundra", "Snow", "Hill"],
     "uniques": [NO_RANDOM],
     "civilopediaText": [{"text": "Broken pillars and rune-carved stone left by the titans who shaped Azeroth, as at Uldaman, Uldum and Ulduar. Their secrets reward the curious."}]},
]

# Clerics can cleanse fel and plague. Copied from "Remove Blighted Land" in build.py.
CLEANSE = {"Fel-Scorched Land": ("Priesthood", 5), "Plagued Land": ("Priesthood", 4)}

WONDERS = [
    {"name": "The Dark Portal", "type": "NaturalWonder", "production": 3, "culture": 2,
     "occursOn": ["Desert", "Plains"], "turnsInto": "Mountain", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [0] [Coast] tiles", "Must be adjacent to [2] to [6] [Desert] tiles"],
     "civilopediaText": [{"text": "The great stone gate in the Blasted Lands through which the Horde first came to Azeroth from Draenor. Fel energy still crackles across its arch."}]},
    {"name": "The Nexus", "type": "NaturalWonder", "science": 4,
     "occursOn": ["Tundra", "Snow"], "turnsInto": "Mountain", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [1] to [6] [Coast] tiles"],
     "civilopediaText": [{"text": "The blue dragonflight's citadel of arcane magic on Coldarra, its crystal spires floating above the frozen shore."}]},
    {"name": "Galakrond's Rest", "type": "NaturalWonder", "production": 2, "faith": 3,
     "occursOn": ["Snow", "Tundra"], "turnsInto": "Mountain", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [0] [Coast] tiles"],
     "civilopediaText": [{"text": "The vast bones of Galakrond, the primal proto-dragon, lying in the snows of Dragonblight where the dragons come to die."}]},
    {"name": "Sunken Temple", "type": "NaturalWonder", "faith": 2, "gold": 2, "culture": 1,
     "occursOn": ["Grassland"], "turnsInto": "Lakes", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [0] [Coast] tiles", "Must be adjacent to [1] to [6] [Marsh] tiles"],
     "civilopediaText": [{"text": "The Temple of Atal'Hakkar, drowned in the Swamp of Sorrows by the green dragons to stop the Atal'ai trolls summoning their blood god."}]},
    {"name": "Maraudon", "type": "NaturalWonder", "food": 2, "production": 2, "faith": 2,
     "occursOn": ["Desert", "Plains"], "turnsInto": "Mountain", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [0] [Coast] tiles", "Must be adjacent to [1] to [6] [Hill] tiles"],
     "civilopediaText": [{"text": "The great caverns beneath Desolace, resting place of Zaetar, son of Cenarius, and of Princess Theradras of the earth."}]},
    {"name": "The Lifeblood Pillar", "type": "NaturalWonder", "food": 3, "science": 2,
     "occursOn": ["Grassland", "Plains"], "turnsInto": "Mountain", "impassable": True, "unbuildable": True,
     "weight": 5, "uniques": ["Must be adjacent to [0] [Coast] tiles", "Must be adjacent to [1] to [6] [Jungle] tiles"],
     "civilopediaText": [{"text": "A titan pillar in Sholazar Basin, the titans' garden in Northrend, from which life-giving waters pour."}]},
]

# Flavour text for the existing (renamed) natural wonders, which had real-world texts.
WONDER_TEXT = {
    "The Maelstrom": "The endless whirlpool where the Well of Eternity imploded and the night elf empire sank beneath the sea.",
    "Mount Hyjal": "The sacred mountain crowned by Nordrassil, the World Tree, where the Burning Legion was turned back.",
    "Teldrassil": "The second World Tree, raised by the night elves off the coast of Darkshore, its roots in the sea.",
    "Moonglade": "A peaceful vale of moonwells and druids, sacred to Cenarius and neutral ground for all.",
    "Lake Elune'ara": "The silver lake at the heart of Moonglade, blessed by the moon goddess Elune.",
    "Stonetalon Peak": "The highest summit of the Stonetalon Mountains, crowned by a great tree of the druids.",
    "Red Rocks of Mulgore": "The sacred burial ground of the tauren, where their ancestors' spirits are honored.",
    "Thousand Needles": "A canyon of towering stone needles where the centaur and the tauren have long fought.",
    "Un'Goro Crater": "A crater full of primeval jungle, dinosaurs and the titans' strange machines.",
    "Lakkari Tar Pits": "Bubbling tar pits in Un'Goro, full of the bones of ancient beasts.",
    "Lost City of the Tol'vir": "The sandstone city of the cat-like tol'vir in Uldum, guardians of the titans' secrets.",
    "Blackrock Mountain": "The volcano of the Dark Iron dwarves, scarred by Thaurissan's summoning of Ragnaros.",
    "Cape of Stranglethorn": "The jungle cape at the southern tip of the Eastern Kingdoms, home of Booty Bay's pirates.",
    "Kelp'thar Forest": "A sunken kelp forest off the coast of the Eastern Kingdoms, realm of the naga and murlocs.",
}
