"""The unit roster: twelve buckets, three tiers, one line per faction (Nov 2026 redesign).

ROSTER[faction][bucket] = [tier I, tier II, tier III]; None = no unit; "A"/"H" = the shared
Alliance or Horde line for that bucket. A name used by several factions is one shared unit.
The Humans' line doubles as the generic line of city-states and barbarians.
"""
BUCKETS = ["aggressive", "defensive", "scout", "ranged", "magic", "mounted", "heavy", "siege", "naval", "aerial", "healer"]
LABEL = {"aggressive": "Melee, aggressive", "defensive": "Melee, defensive", "scout": "Scout / ambush", "ranged": "Ranged, physical",
         "magic": "Ranged, magical", "mounted": "Mounted cavalry", "heavy": "Heavy / beast", "siege": "Siege", "naval": "Naval",
         "aerial": "Aerial", "healer": "Healer / support"}
POOL = {
    "A": {"heavy": [None, "Steam Tank", "Siege Engine"], "siege": ["Catapult", "Ballista", "Cannon"],
          "naval": ["Galley", "Frigate", "Battleship"], "aerial": [None, "Gyrocopter", "Gunship"]},
    "H": {"heavy": [None, "Ogre Brute", "Ogre Mauler"], "siege": ["Catapult", "Demolisher", "Horde Siege Engine"],
          "naval": ["Raider Longboat", "Destroyer", "Juggernaught"], "aerial": [None, "Wind Rider", "Zeppelin"]},
}
_ = None


def R(*rows):
    return dict(zip(BUCKETS, rows))


ROSTER = {
    "Humans": R(["Militia", "Footman", "Champion"], ["Spearman", "Man-at-Arms", "Royal Guard"], ["Scout", "Pathfinder", "SI:7 Agent"],
                ["Archer", "Crossbowman", "Rifleman"], ["Conjurer", "Mage", "Kirin Tor Magus"], ["Outrider", "Knight", "Paladin"],
                "A", "A", "A", "A", ["Cleric", "Priest of the Light", "High Priest"]),
    "Dwarves": R(["Brawler", "Axeman", "Mountain King's Guard"], ["Shieldbearer", "Ironforge Guard", "Thane's Guard"],
                 ["Prospector", "Mountaineer", "Explorer's League Scout"], ["Crossbow Dwarf", "Ironforge Rifleman", "Sharpshooter"],
                 ["Runecaster", "Rune Priest", "Stormcaller"], ["Ram Rider", "Ram Lancer", "Paladin"], [_, "Steam Armor", "Siege Engine"],
                 ["Catapult", "Mortar Team", "Flame Cannon"], "A", [_, "Gryphon Rider", "Stormhammer Rider"],
                 ["Hearthkeeper", "Dwarven Priest", "High Priest of the Mountain"]),
    "Dark Iron Dwarves": R(["Slaver", "Dark Iron Warrior", "Anvilrage Reaver"], ["Sentry", "Fireguard", "Anvilrage Guardsman"],
                           ["Tunneler", "Dark Iron Saboteur", "Shadowforge Assassin"], ["Crossbow Dwarf", "Dark Iron Rifleman", "Blackrock Marksman"],
                           ["Ember Seer", "Pyromancer", "Twilight Flamecaller"], ["Core Hound Handler", "Core Hound Rider", "Molten Charger"],
                           [_, "Dark Iron Golem", "Molten Colossus"], ["Catapult", "Flame Mortar", "Magma Cannon"], "A", "A",
                           ["Ashtender", "Flamekeeper", "Shadowforge Priest"]),
    "Gnomes": R(["Tinker Brawler", "Gnomeregan Infantry", "Mechagnome Trooper"], ["Wrench Guard", "Shieldbot", "Gnomeregan Sentinel"],
                ["Surveyor", "Covert Ops Agent", "Cloaked Infiltrator"], ["Slingshot Tinker", "Gnomish Rifleman", "Death Ray Gunner"],
                ["Illusionist", "Gnome Mage", "Arcanomancer"], [_, "Mechanostrider Rider", "Mechanostrider Lancer"], [_, "Spider Tank", "Mechano-Tank"],
                ["Catapult", "Gnomish Bombardier", "Rocket Battery"], "A", [_, "Flying Machine", "Gnomish Bomber"],
                ["Field Medic", "Decontaminator", "Chief Surgeon"]),
    "Night Elves": R(["Glaive Initiate", "Sentinel", "Warden"], ["Grove Keeper", "Grove Guardian", "Watcher"],
                     ["Shadowmeld Scout", "Sentinel Stalker", "Shadowleaf Assassin"], ["Archer", "Moon Archer", "Sentinel Marksman"],
                     ["Druid of the Talon", "Moon Adept", "Keeper of the Grove"], ["Nightsaber Rider", "Huntress", "Moonguard Huntress"],
                     ["Druid of the Claw", "Ancient of War", "Mountain Giant"], [_, "Glaive Thrower", "Ancient Stone Thrower"],
                     ["Elven Skiff", "Night Elf Destroyer", "Moonwing Warship"], [_, "Hippogryph Rider", "Chimaera"],
                     ["Dryad", "Cenarion Druid", "Priestess of the Moon"]),
    "High Elves": R(["Swordsman", "Elven Blade", "Silver Covenant Champion"], ["Spearguard", "Quel'Thalas Guardian", "Sunwell Guard"],
                    ["Forest Scout", "Farstrider", "Farstrider Pathstalker"], ["Elven Archer", "Ranger", "Ranger-Lord"],
                    ["Apprentice", "Sorceress", "Magister"], ["Horse Archer", "Elven Knight", "Silver Covenant Lancer"], "A",
                    [_, "Elven Ballista", "Arcane Ballista"], ["Elven Skiff", "Elven Destroyer", "Silver Covenant Warship"],
                    [_, "Dragonhawk Scout", "Silver Covenant Hippogryph"], ["Novice Priest", "Lightwarden", "Sunwell High Priest"]),
    "Draenei": R(["Defender", "Vindicator Initiate", "Vindicator"], ["Shieldbearer", "Peacekeeper", "Exarch's Guard"],
                 ["Wayfinder", "Rangari", "Rangari Shadowstalker"], ["Crossbow Defender", "Rangari Archer", "Lightforged Marksman"],
                 ["Crystal Adept", "Arcanist", "Artificer Mage"], ["Talbuk Rider", "Elekk Rider", "Elekk Lancer"],
                 [_, "Crystal Golem", "Lightforged Warframe"], [_, "Crystal Lance", "Lightforged Cannon"], "A",
                 [_, "Nether Ray Rider", "Vindicaar Skiff"], ["Novice", "Anchorite", "Exarch"]),
    "Worgen": R(["Gilnean Militia", "Worgen Stalker", "Worgen Ravager"], ["Town Guard", "Gilnean Royal Guard", "Greyguard"],
                ["Gamekeeper", "Bloodfang Scout", "Bloodfang Stalker"], ["Gilnean Hunter", "Gilnean Rifleman", "Gilnean Marksman"],
                ["Hedge Witch", "Gilnean Mage", "Harvest Arcanist"], ["Gilnean Horseman", "Gilnean Lancer", "Greymane Cavalier"],
                [_, "Harvest Golem", "Dire Worgen"], "A", "A", "A", ["Herbalist", "Harvest Witch", "Druid of the Scythe"]),
    "Kul Tirans": R(["Deckhand", "Kul Tiran Marine", "Proudmoore Guard"], ["Harbor Watch", "Kul Tiran Halberdier", "Admiralty Shieldbearer"],
                    ["Lookout", "Outrigger Scout", "Privateer"], ["Harpooner", "Admiralty Gunner", "Sharpshooter"],
                    ["Seacaller", "Hydromancer", "Storm's Wake Tidecaller"], ["Outrider", "Kul Tiran Cavalier", "Norwington Lancer"],
                    [_, "Thornspeaker Bear", "Azerite War Machine"], ["Catapult", "Deck Cannon", "Azerite Cannon"],
                    ["Cutter", "Frigate", "Kul Tiran Man-o'-War"], "A", ["Ship's Mender", "Tidesage", "Thornspeaker"]),
    "Orcs": R(["Brawler", "Grunt", "Warsong Reaver"], ["Burrow Watcher", "Orgrimmar Guard", "Kor'kron Guard"], ["Scout", "Wolf Scout", "Blademaster"],
              ["Spear Thrower", "Axe Thrower", "Orc Hunter"], ["Necrolyte", "Warlock", "Shadow Council Warlock"],
              ["Wolf Rider", "Raider", "Warsong Outrider"], "H", "H", "H", "H", ["Apprentice Shaman", "Earthen Shaman", "Far Seer"]),
    "Tauren": R(["Brave", "Tauren Warrior", "Bloodhoof Champion"], ["Totem Guard", "Bluffwatcher", "Thunder Bluff Protector"],
                ["Longwalker", "Plainsrunner", "Grimtotem Stalker"], ["Spear Hunter", "Tauren Hunter", "Longrifle Hunter"],
                ["Mystic", "Spirit Walker", "Elder Shaman"], [_, "Kodo Rider", "Kodo War Rider"], ["Kodo Beast", "War Kodo", "Chieftain's Guard"],
                "H", "H", [_, "Wind Rider", "Thunder Wyvern"], ["Herbwalker", "Druid of the Plains", "Sunwalker"]),
    "Highmountain Tauren": R(["Brave", "Highmountain Warbrave", "Thunder Totem Champion"], ["Totem Guard", "Skyhorn Sentinel", "Highmountain Protector"],
                             ["Tracker", "Skyhorn Tracker", "Rivermane Stalker"], ["Spear Hunter", "Highmountain Hunter", "Eagle-Eye Marksman"],
                             ["Mystic", "Rivermane Shaman", "Highmountain Stormcaller"], [_, "Thunderhoof Rider", "Moose Lancer"],
                             ["Kodo Beast", "War Kodo", "Bloodtotem Brute"], "H", "H", [_, "Skyhorn Eagle Rider", "Great Eagle Warrior"],
                             ["Herbwalker", "Spiritwalker", "Rivermane Elder"]),
    "Trolls": R(["Jungle Fighter", "Troll Berserker", "Darkspear Champion"], ["Spear Guard", "Darkspear Warrior", "Darkspear Guardian"],
                ["Jungle Scout", "Shadow Stalker", "Shadow Hunter"], ["Spear Thrower", "Headhunter", "Darkspear Axe Thrower"],
                ["Hexer", "Hex Priest", "Voodoo Master"], [_, "Raptor Rider", "Darkspear Raptor Lancer"], [_, "War Bear", "Dire Troll"], "H",
                ["Troll Canoe", "Destroyer", "Juggernaught"], [_, "Batrider", "Bat Lord"], ["Herb Doctor", "Witch Doctor", "Loa Priest"]),
    "Zandalari Trolls": R(["Zandalari Warrior", "Blood Guard", "Zandalari Champion"], ["Temple Guard", "Rastari Enforcer", "Golden Guard"],
                          ["Jungle Scout", "Shadow Stalker", "Zanchuli Assassin"], ["Spear Thrower", "Headhunter", "Rastari Marksman"],
                          ["Hexer", "Hexlord", "Zanchuli Witch Doctor"], ["Raptor Skirmisher", "Ravasaur Rider", "Zandalari Beastcaller"],
                          [_, "Direhorn Rider", "Brutosaur"], [_, "Zandalari Ballista", "Devilsaur Siege Beast"],
                          ["Zandalari Canoe", "Zandalari Warship", "Golden Fleet Dreadnought"], [_, "Pterrordax Rider", "Pa'ku's Windrider"],
                          ["Loa Speaker", "Loa Herald", "Prelate"]),
    "Blood Elves": R(["Swordsman", "Spellbreaker", "Sunfury Blade"], ["Spearguard", "Silvermoon Guardian", "Quel'Thalas Royal Guard"],
                     ["Forest Scout", "Farstrider", "Reliquary Shadowstalker"], ["Elven Archer", "Blood Elf Ranger", "Sunfury Marksman"],
                     ["Apprentice", "Blood Mage", "Magister"], ["Hawkstrider Rider", "Hawkstrider Lancer", "Blood Knight"],
                     [_, "Arcane Golem", "Fel Reaver"], [_, "Elven Ballista", "Mana Bomb Launcher"],
                     ["Elven Skiff", "Sunreaver Destroyer", "Sunreaver Warship"], [_, "Dragonhawk Rider", "Phoenix"],
                     ["Novice Priest", "Sunfury Priest", "Sunwell Priest"]),
    "Nightborne": R(["Duskwatch Recruit", "Spellblade", "Felsworn Blade"], ["Gate Warden", "Duskwatch Sentinel", "Suramar Royal Guard"],
                    ["Courier", "Duskwatch Spy", "Shadowblade"], ["Duskwatch Archer", "Arcane Archer", "Nightglaive Thrower"],
                    ["Arcanist Adept", "Spellweaver", "Chronomancer"], [_, "Manasaber Rider", "Duskwatch Lancer"],
                    [_, "Arcane Construct", "Felbound Construct"], [_, "Suramar Ballista", "Leyline Cannon"], "H", [_, "Arcane Skiff", "Manaray Rider"],
                    ["Vintner", "Shal'dorei Mender", "Nightwell Priest"]),
    "Forsaken": R(["Risen Soldier", "Deathguard", "Dreadguard"], ["Bone Guard", "Deathguard Sentry", "Royal Dreadguard"],
                  ["Deathstalker Recruit", "Deathstalker", "Dark Ranger"], ["Skeletal Archer", "Forsaken Crossbowman", "Dark Ranger Marksman"],
                  ["Apprentice Necromancer", "Shadow Mage", "Banshee"], [_, "Skeletal Horseman", "Deathguard Rider"],
                  [_, "Abomination", "Flesh Giant"], [_, "Meat Wagon", "Blight Thrower"], "H", [_, "Bat Rider", "Plague Bat Bomber"],
                  ["Gravedigger", "Apothecary", "Royal Apothecary"]),
    "Goblins": R(["Bruiser", "Goblin Mercenary", "Bilgewater Bruiser"], ["Bouncer", "Cartel Enforcer", "Steamwheedle Guard"],
                 ["Goblin Prospector", "Goblin Scout", "Undermine Assassin"], ["Dynamite Tosser", "Goblin Rifleman", "Rocket Gunner"],
                 ["Alchemist", "Goblin Hexer", "Tinker Mage"], [_, "Trike Rider", "Rocket Trike"], [_, "Iron Lumberjack", "Iron Shredder"],
                 [_, "Goblin Sapper", "Rocket Battery"], ["Tug", "Goblin Gunboat", "Bilgewater Dreadnought"], [_, "Goblin Zeppelin", "Rocket Bomber"],
                 ["Barker", "Hazmat Crew", "Chief Medic"]),
    "Pandaren": R(["Pandaren Brawler", "Brewmaster", "Shado-Pan Warrior"], ["Village Guard", "Shado-Pan Monk", "Shado-Pan Wall Guard"],
                  ["Lorewalker", "Wu Kao Scout", "Wu Kao Assassin"], ["Bamboo Archer", "Shado-Pan Archer", "Blackguard Marksman"],
                  ["Waterspeaker", "Jade Stormcaller", "Jade Sorcerer"], ["Yak Rider", "Tiger Rider", "Shado-Pan Tiger Lancer"],
                  [_, "Mushan Beast", "Jade Serpent Guardian"], [_, "Fireworks Launcher", "Keg Catapult"],
                  ["Junk", "War Junk", "Jade Fleet Flagship"], [_, "Kite Scout", "Cloud Serpent Rider"], ["Brewer", "Mistweaver", "Elder Mistweaver"]),
    "Scourge": R(["Skeleton Warrior", "Ghoul", "Vrykul Deathbringer"], ["Skeletal Guard", "Crypt Guard", "Ymirjar Sentinel"],
                 ["Shade", "Geist", "Crypt Stalker"], ["Skeletal Archer", "Crypt Fiend", "Nerubian Spitter"],
                 ["Cultist", "Necromancer", "Lich"], [_, "Skeletal Rider", "Death Knight"], [_, "Abomination", "Flesh Titan"],
                 [_, "Meat Wagon", "Plague Catapult"], [_, "Ghost Ship", "Scourge Dreadnought"], [_, "Gargoyle", "Frost Wyrm"],
                 ["Cult Initiate", "Priest of the Damned", "Obsidian Statue"]),
    "Naga": R(["Mur'gul Reaver", "Myrmidon", "Azshara's Royal Guard"], ["Tidewarden", "Naga Sentinel", "Coilfang Defender"],
              ["Mur'gul Scout", "Naga Stalker", "Deepsea Assassin"], ["Trident Thrower", "Snap Dragon", "Coilfang Harpooner"],
              ["Siren", "Sea Witch", "Tidemistress"], [_, "Seahorse Rider", "Sea Serpent Rider"], [_, "Dragon Turtle", "Sea Giant"],
              [_, "Tidal Guardian", "Kraken Caller"], [_, _, _], [_, "Couatl", "Storm Couatl"], ["Tidecaller", "Tidepriestess", "High Tidepriestess"]),
}
SIDE = {"A": ["Humans", "Dwarves", "Dark Iron Dwarves", "Gnomes", "Night Elves", "High Elves", "Draenei", "Worgen", "Kul Tirans"],
        "H": ["Orcs", "Tauren", "Highmountain Tauren", "Trolls", "Zandalari Trolls", "Blood Elves", "Nightborne", "Forsaken", "Goblins"]}


def line(nation, bucket):
    v = ROSTER[nation][bucket]
    return list(POOL[v][bucket]) if isinstance(v, str) else list(v)


def slots():
    """name -> (bucket, tier index, [nations]) for every roster unit."""
    out = {}
    for nation in ROSTER:
        for b in BUCKETS:
            for t, name in enumerate(line(nation, b)):
                if name is None:
                    continue
                if name in out:
                    assert out[name][:2] == (b, t), (name, out[name][:2], b, t, nation)
                    out[name][2].append(nation)
                else:
                    out[name] = (b, t, [nation])
    return out


if __name__ == "__main__":
    s = slots()
    print(len(s), "units;", sum(1 for v in s.values() if len(v[2]) > 1), "shared")
