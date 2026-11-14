"""Civilopedia text for the roster units that had only a placeholder line.

Each entry says who fields the unit, what it is for, what its faction's troops are like, and where it
sits in its upgrade line. A set of signature units also opens with a line of lore.
"""
import roster_data as RD

ROLE = {
    "aggressive": ("front-line infantry", "Built to attack: it carries the fight to the enemy and takes ground."),
    "defensive": ("line-holding infantry", "Built to hold: it is at its best fortified or standing against a charge."),
    "scout": ("scouts and ambushers", "Fast and far-sighted, it finds the enemy first and strikes where he is weak."),
    "ranged": ("missile troops", "Strikes from a distance with bow, thrown weapon or shot, and should be kept behind the line."),
    "magic": ("spellcasters", "Fights with magic from a distance; deadly against armour, fragile in melee."),
    "mounted": ("cavalry", "Fast and hard-hitting on open ground; it flanks, raids and runs down the wounded, but breaks on a spear line."),
    "heavy": ("heavy shock unit", "Slow, tough and costly: a beast, giant or machine that anchors an assault."),
    "siege": ("siege weapon", "Made to break cities and fortifications; it must be set up before it can fire and needs an escort."),
    "naval": ("warship", "Controls the coast and the sea lanes, and supports landings."),
    "aerial": ("flyers", "Strikes from the air well beyond the front, but cannot hold ground and dies quickly to anything that can reach it."),
    "healer": ("healers", "Does not fight; units next to it recover faster, and it can be bought with Faith."),
}
STAGE = ["of the early ages", "of the middle game", "of the late game"]
TRAIT = {
    "Orcs": "Orc warriors hit harder than most, above all on the attack.",
    "Tauren": "Tauren are larger and stronger than other peoples and cost more to raise; they recover quickly and fight best on open plains.",
    "Highmountain Tauren": "Highmountain Tauren are big, strong and costly to raise; they recover quickly and fight best in the hills.",
    "Trolls": "Trolls regenerate their wounds and move freely through jungle; their throwers and hexers outmatch their line infantry.",
    "Zandalari Trolls": "The Zandalari are the strongest of the trolls: they regenerate, move freely through jungle and field great war beasts, at a price.",
    "Night Elves": "Night Elves are at home in the forest, where they move fast and fight harder; their archers are among the best.",
    "High Elves": "The High Elves rely on archery and magic; their infantry is thin.",
    "Blood Elves": "The Blood Elves lean on magic; their casters are strong and their infantry light.",
    "Nightborne": "The Nightborne field the strongest magic of any people and the weakest shield wall.",
    "Dwarves": "Dwarves are stubborn in defence and at their best in the hills, with good guns.",
    "Dark Iron Dwarves": "The Dark Iron are stubborn in defence and at home in the hills, with fearsome fire magic and siege craft.",
    "Gnomes": "Gnomes make poor foot soldiers and excellent machines; their troops are cheap.",
    "Goblins": "Goblins fight cheaply and badly on foot and let explosives and machines do the work.",
    "Draenei": "The Draenei hold a line well and trust in the Light and in crystal constructs.",
    "Worgen": "Worgen are fast and savage in the attack and less steady in defence.",
    "Kul Tirans": "Kul Tiras is a sea power: its ships are the best afloat and its marines are solid.",
    "Forsaken": "The Forsaken are cheap to raise and rely on blight, dark arts and stitched horrors more than on their line.",
    "Scourge": "The Scourge fights as a swarm: its dead are cheap and individually weak, backed by a few monsters.",
    "Pandaren": "Pandaren are patient defenders who recover quickly.",
    "Naga": "The Naga are a little stronger than most across the board and fight best along the coast.",
    "Humans": "Human troops are the yardstick the others are measured against: balanced, with no great weakness.",
}
LORE = {
    "Royal Guard": "Hand-picked veterans who stand watch over kings.", "Champion": "Knights' sergeants and tournament winners, the best foot soldiers a kingdom can field.",
    "SI:7 Agent": "Stormwind's intelligence service works where armies cannot go.", "Conjurer": "The first human mages, self-taught and dangerous to stand near.",
    "Kor'kron Guard": "The Warchief's own guard, chosen for size, skill and loyalty.", "Blademaster": "Swordsmen of the Burning Blade who strike from nowhere and vanish again.",
    "Axe Thrower": "A thrown axe needs no bowstring and no arrow, only an arm.", "Raider": "Wolf riders who burn farms and are gone before the garrison wakes.",
    "Far Seer": "Elder shamans who read the winds and speak for the spirits.", "Necrolyte": "Early orcish warlocks who dealt in death long before the Horde had a name for it.",
    "Bluffwatcher": "The guards of the high mesas, who have never let an enemy climb the lifts.", "Brave": "A young Tauren proves himself with a totem log and a long walk.",
    "Kodo Beast": "A kodo carries the war drums, and the drums carry the army.", "Spirit Walker": "Pale Tauren who walk with the ancestors and bring their strength back.",
    "Sunwalker": "Tauren who follow the sun as the druids follow the moon.", "Longwalker": "Tauren who walk the whole land and remember every path.",
    "Headhunter": "A troll with a spear can kill what he cannot reach.", "Shadow Hunter": "Chosen of the loa, half priest and half killer.",
    "Batrider": "Darkspear riders who throw fire from the backs of giant bats.", "Dire Troll": "A troll grown monstrous on blood rites, used as a living ram.",
    "Witch Doctor": "Healers, poisoners and keepers of the old bargains with the loa.", "Prelate": "Zandalari holy warriors sworn to the loa of kings.",
    "Brutosaur": "A walking hill with a howdah; whole markets have been run from its back.", "Golden Guard": "The palace guard of the Zandalari kings, armoured in gold.",
    "Sentinel": "The standing army of the Night Elves, sworn to ten thousand years of watch.", "Warden": "Jailers and hunters of the Night Elves who never lose a quarry.",
    "Huntress": "Riders of the great nightsabers, with a glaive that returns to the hand.", "Mountain Giant": "The living bones of the hills, woken to defend the forest.",
    "Ancient of War": "A tree old enough to remember the last war, and willing to fight this one.", "Druid of the Talon": "Druids who take the shape of the storm crow and call the wind.",
    "Druid of the Claw": "Druids who fight in the shape of the great bear.", "Chimaera": "A two-headed beast of the deep forest whose breath eats stone.",
    "Hippogryph Rider": "Archers mounted on the stag-headed fliers of the high forest.", "Priestess of the Moon": "The sisterhood that has led the Night Elves in war since the Sundering.",
    "Keeper of the Grove": "Sons of the forest god, half stag and half elf.", "Glaive Thrower": "A ballista that hurls a spinning three-bladed glaive.",
    "Farstrider": "Rangers who keep the forest borders of the elven kingdom.", "Spellbreaker": "Elven soldiers trained to turn an enemy's magic back on him.",
    "Blood Knight": "Elven knights who took the Light by force and learned to live with what that cost.", "Magister": "The ruling mages of the elven kingdom.",
    "Phoenix": "A bird of living flame that rises again from its own ashes.", "Dragonhawk Rider": "Riders of the red-gold serpents of the northern woods.",
    "Mountaineer": "Dwarven hill troops who know every pass and carry a gun through all of them.", "Mortar Team": "Two dwarves, one tube and a long argument about the range.",
    "Gryphon Rider": "Hill dwarves who ride gryphons and throw storm hammers.", "Thane's Guard": "The household warriors of a dwarven lord.",
    "Steam Armor": "A dwarf inside a walking boiler.", "Dark Iron Golem": "Iron given a furnace for a heart.", "Fireguard": "Dark Iron soldiers who fight wreathed in flame.",
    "Mechanostrider Rider": "A gnome on a clockwork bird, which is faster than it looks.", "Spider Tank": "A walking gun platform; gnomes consider legs more reliable than wheels.",
    "Flying Machine": "A one-seat rotor craft, first into every fight and often first out.", "Vindicator": "Draenei champions of the Light who make every soldier beside them braver.",
    "Anchorite": "Draenei priests who have kept their people's faith across many worlds.", "Elekk Rider": "Riders of the great tusked beasts the Draenei brought from their old home.",
    "Lightforged Warframe": "A suit of consecrated armour the size of a house.", "Rangari": "Draenei scouts who have learned to live unseen.",
    "Worgen Stalker": "A Gilnean who has learned to use the curse and not be used by it.", "Harvest Witch": "Keepers of the old ways of the Gilnean countryside.",
    "Kul Tiran Marine": "Shipboard infantry who are first onto an enemy deck.", "Tidesage": "Sea priests who bless every hull and call the tide.",
    "Kul Tiran Man-o'-War": "The pride of the Admiralty: three decks of guns under a cloud of sail.",
    "Deathguard": "The Forsaken's rank and file, who cannot be killed twice the same way.", "Deathstalker": "Forsaken assassins and spies.",
    "Dark Ranger": "Fallen elven rangers who serve the Banshee Queen.", "Abomination": "Many corpses stitched into one, with a cleaver and a hook.",
    "Meat Wagon": "A catapult that throws what it collects from the field.", "Apothecary": "The Forsaken's alchemists, who heal with one hand and brew plague with the other.",
    "Banshee": "The screaming dead, who can take a living body for their own.",
    "Ghoul": "The first and commonest of the risen dead, always hungry.", "Crypt Fiend": "Spider-lords of the fallen northern kingdom, raised to serve.",
    "Necromancer": "Mortal wizards who bought power by raising the dead.", "Death Knight": "Fallen champions on skeletal chargers, each one worth a company.",
    "Frost Wyrm": "The bones of a dragon, raised and filled with killing cold.", "Gargoyle": "Stone-skinned fliers that roost in the citadels of the dead.",
    "Lich": "A sorcerer who has put death behind him and winter in front of him.", "Obsidian Statue": "A carved idol that mends the dead who stand near it.",
    "Goblin Sapper": "Two goblins, one barrel of powder, and a firm belief that the fuse is long enough.", "Iron Lumberjack": "A walking saw mill that does not care what it cuts.",
    "Goblin Zeppelin": "Slow, leaky and for hire.", "Trike Rider": "Three wheels, one engine, no brakes.",
    "Brewmaster": "Wandering Pandaren who fight as they drink: cheerfully and well.", "Shado-Pan Monk": "The masked order that guards the great wall of the hidden land.",
    "Mistweaver": "Healers who work with mist, tea and patience.", "Cloud Serpent Rider": "Riders who raise their serpents from the egg.",
    "Myrmidon": "The warrior caste of the Naga, all coil and trident.", "Sea Witch": "Naga sorceresses who command storm and tide.",
    "Siren": "Naga whose song has drowned whole crews.", "Dragon Turtle": "A sea beast with a shell like a fortress wall.",
    "Spellblade": "Nightborne duellists who fight with sword and spell together.", "Chronomancer": "Nightborne mages who have learned to bend time itself.",
    "Ogre Brute": "Ogres will fight for the Horde as long as there is something to hit.", "Ogre Mauler": "A two-headed ogre has twice the appetite and half the patience.",
    "Demolisher": "The Horde's stone-thrower, built heavy enough to drive through a wall it has not yet knocked down.", "Wind Rider": "Horde scouts mounted on wyverns of the high crags.",
    "Juggernaught": "The Horde's largest warship: slow, armoured and bristling with guns.", "Steam Tank": "An Alliance invention: armour, a boiler and one very large gun.",
    "Gyrocopter": "A light Alliance rotor craft used to scout and to hunt other fliers.", "Gunship": "An Alliance airship that carries a broadside into the sky.",
    "Zeppelin": "The Horde's airship: a gas bag, a gondola and a great many bombs.", "Battleship": "The Alliance's ship of the line.",
}


def describe(name, b, t, users, units):
    lines = RD.BUCKETS
    if len(users) == 1:
        who = "the " + users[0] if users[0] not in ("Kul Tirans",) else users[0]
        owner = users[0]
    elif set(users) <= set(RD.SIDE["A"]):
        who, owner = "the Alliance (%s)" % ", ".join(users), None
    elif set(users) <= set(RD.SIDE["H"]):
        who, owner = "the Horde (%s)" % ", ".join(users), None
    else:
        who, owner = " and ".join(users), None
    noun, play = ROLE[b]
    out = []
    if name in LORE:
        out.append(LORE[name])
    out.append("%s %s, fielded by %s. %s" % (noun[0].upper() + noun[1:], STAGE[t], who, play))
    if owner and owner in TRAIT:
        out.append(TRAIT[owner])
    prev = sorted({RD.line(n, b)[t - 1] for n in users if t > 0 and RD.line(n, b)[t - 1]})
    nxt = sorted({RD.line(n, b)[t + 1] for n in users if t < 2 and RD.line(n, b)[t + 1]})
    path = []
    if prev:
        path.append("Upgrades from %s." % " or ".join(prev))
    if nxt:
        path.append("Upgrades to %s." % " or ".join(nxt))
    if path:
        out.append(" ".join(path))
    return [{"text": s} for s in out]


def apply(units):
    import re
    import wc_roster
    slots = RD.slots()
    names = {u["name"] for u in units}
    gone = [g for g in wc_roster.OLD if g not in names] + ["Grand Champion", "Great Scientist"]
    n = m = 0
    for u in units:
        s = slots.get(u["name"])
        if not s:
            continue
        txt = u.get("civilopediaText") or []
        placeholder = len(txt) == 1 and ", tier " in txt[0].get("text", "") and "Fielded by" in txt[0].get("text", "")
        generated = bool(txt) and any("fielded by" in x.get("text", "") for x in txt)
        if placeholder or generated or not txt or (len(s[2]) > 1 and not any(x.get("text", "").startswith("Spell:") for x in txt)):
            u["civilopediaText"] = describe(u["name"], s[0], s[1], s[2], units)
            n += 1
        elif not any(x.get("text", "").startswith("Upgrades ") or "Upgrades to" in x.get("text", "") for x in txt):
            # an older hand-written entry: drop comparisons with units that no longer exist, then add the new line's place
            keep = [x for x in txt if not any(re.search(r"\b%s\b" % re.escape(g), x.get("text", "")) for g in gone)]
            tail = [x for x in describe(u["name"], s[0], s[1], s[2], units) if x["text"].startswith("Upgrades ")]
            u["civilopediaText"] = (keep or describe(u["name"], s[0], s[1], s[2], units)[:1]) + tail
            m += 1
    print("unit descriptions written: %d new, %d older entries updated" % (n, m))
