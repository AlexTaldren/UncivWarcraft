"""The systems pass (Oct 2026): engine features the mod wasn't using yet, in Warcraft terms.

  1. Spells: heroes and spellcasters get action buttons that cost Mana and then recharge.
     Each spell is a timed status; casting it starts a "<spell> Cooldown" status, and the
     button only shows on units without that cooldown. AI players can't press buttons, so
     their units cast the same spells automatically (in combat, or when badly hurt).
  3. Landmarks: the first civilization to find each natural wonder gets a reward, and
     discovering ten of them starts a lore event (several tie into the raid bosses).
  4. Alliance and Horde politics: events when you attack your own side, when the other side
     attacks you, and when your own side betrays you.
  5. Themed barbarians: barbarian-only units (Kobolds, Gnolls, Murlocs ... the Faceless) that
     replace the generic units the barbarians used to field, age by age.
  7. Spies: faction spy names, faction spy strengths and the Ravenholdt wonder.
  8. Other ways to pay: holy units for Faith, Orc melee for Culture, Zandalari mounts and Kul
     Tiran ships for Faith, Goblins buy out allied city-states.
  9. Head starts: when a game starts in a later age, each faction founds its first city with
     lore-appropriate extra units, Mana and Gold.
build.py calls apply(files, majors) after wc_depth.apply. (Maps and scenarios are built by
azeroth.py / build_map.sh and sim/BuildScenario.java.)
Unciv can't fire anything on a peace treaty (tested: the trigger never runs), so the politics
hang on war declarations only.
"""
import copy

from wc_depth import lore, need, ai, ERAS, FACTIONS, HERO_CLASSES

MANA = "Mana"
ALLIANCE = ["Humans", "Night Elves", "Dwarves", "Gnomes", "High Elves", "Draenei", "Worgen", "Dark Iron Dwarves", "Kul Tirans"]
HORDE = ["Orcs", "Tauren", "Trolls", "Blood Elves", "Forsaken", "Goblins", "Zandalari Trolls"]
ADJ = "[%d]%% Strength for enemy [Military] units in adjacent [All] tiles"


# ====================================================================== 1. spells
# (spell, units, turns, status uniques, one-off effects, mana, cooldown, movement, glyphs, lore)
CLASS_SPELLS = {
    "Champion Hero": ("Rallying Cry", 2, ["All adjacent units heal [15] HP when healing", "[+15]% Strength"], [], 10, 5, 0,
                      ("banner", "heart"), "The hero's war cry steadies the line: +15% Strength, and adjacent units heal 15 HP more, for 2 turns."),
    "Arcane Hero": ("Mana Shield", 2, ["[+40]% Strength <when defending>"], [], 10, 5, 0,
                    ("orb", "shield"), "A shell of pure mana: +40% Strength when defending for 2 turns."),
    "Marksman Hero": ("Hunter's Mark", 2, ["[+25]% Strength <when attacking>", "[+1] Sight"], [], 10, 5, 0,
                      ("target", "eye"), "Marks the prey: +25% Strength when attacking and +1 Sight for 2 turns."),
}
SPELLS = [
    # ---- hero signatures
    ("Divine Shield", ["Uther the Lightbringer"], 1, ["[+100]% Strength <when defending>"], [], 20, 8, 0, ("hand_light", "shield"),
     "An unbreakable bubble of holy light: +100% Strength when defending for 1 turn."),
    ("Hellscream's Fury", ["Grom Hellscream"], 2, ["[+30]% Strength <when attacking>", "[+1] Movement"], [], 20, 7, 0, ("axe", "flame"),
     "Shamanic fury: +30% Strength when attacking and +1 Movement for 2 turns."),
    ("Thunder Clap", ["Muradin Bronzebeard"], 2, [ADJ % -20], [], 20, 7, 0, ("hammer", "bolt"),
     "The ground shakes: adjacent enemies fight at -20% Strength for 2 turns."),
    ("Overclock", ["Kelsey Steelspark"], 1, ["[+2] Movement", "[+20]% Strength <when attacking>"], [], 15, 6, 0, ("gears", "bolt"),
     "Every gear at full spin: +2 Movement and +20% Strength when attacking for 1 turn."),
    ("War Stomp", ["Baine Bloodhoof"], 1, [ADJ % -30], [], 15, 6, 0, ("feet", "bolt"),
     "A tauren stomp that knocks foes off their feet: adjacent enemies fight at -30% Strength for 1 turn."),
    ("Holy Light", ["Maraad"], 1, [], ["[This Unit] heals [50] HP"], 15, 5, 1, ("hand_light", "heart"),
     "Heals the hero for 50 HP."),
    ("Call the Sappers", ["Gazlowe"], 1, [], ["[2] free [Goblin Sapper] units appear"], 30, 10, 1, ("bomb", "coins"),
     "Two Goblin Sappers answer the call, for a fee."),
    ("Pounce", ["Darius Crowley"], 1, ["[+2] Movement", "[+15]% Strength <when attacking>"], [], 10, 5, 0, ("wolf", "boot"),
     "A worgen's leap: +2 Movement and +15% Strength when attacking for 1 turn."),
    ("Call the Fireguard", ["Dagran Thaurissan"], 1, [], ["[1] free [Fireguard] units appear"], 25, 10, 1, ("flame", "helm"),
     "A Fireguard of the Shadowforge marches to the emperor's side."),
    ("Rally the Admiralty", ["Daelin Proudmoore"], 2, ["All adjacent units heal [20] HP when healing"], ["[This Unit] heals [30] HP"],
     20, 7, 1, ("anchor", "heart"), "Heals the admiral for 30 HP; adjacent units heal 20 HP more for 2 turns."),
    ("Storm, Earth and Fire", ["Chen Stormstout"], 1, [], ["[2] free [Brewmaster] units appear"], 35, 12, 1, ("ghost", "flame"),
     "Chen splits into elemental spirits: two Brewmasters join him."),
    ("Phoenix Fire", ["Kael'thas Sunstrider"], 2, [ADJ % -25, "[+20]% Strength <when attacking>"], [], 25, 8, 0, ("flame", "wing"),
     "A phoenix wreathes the prince in fire: adjacent enemies -25% Strength, +20% when attacking, for 2 turns."),
    ("Raise Dead", ["Kel'Thuzad"], 1, [], ["[2] free [Ghoul] units appear"], 20, 8, 1, ("skull", "coffin"),
     "The lich calls two Ghouls from the grave."),
    ("Pact of Bwonsamdi", ["Rastakhan"], 2, ["No damage penalty for wounded units"], ["[This Unit] heals [60] HP"], 20, 8, 1,
     ("mask", "skull"), "The loa of death lends the king his strength: heals 60 HP, no wound penalty for 2 turns."),
    ("Tranquility", ["Malfurion Stormrage"], 2, ["All adjacent units heal [25] HP when healing"], [], 25, 8, 0, ("leaf", "moon"),
     "A rain of nature's magic: adjacent units heal 25 HP more for 2 turns."),
    ("Windrunner Volley", ["Alleria Windrunner"], 1, ["[+40]% Strength <when attacking>"], [], 15, 6, 0, ("bow", "arrows_up"),
     "Arrow after arrow: +40% Strength when attacking for 1 turn."),
    ("Black Arrow", ["Nathanos Blightcaller"], 2, ["[+25]% Strength <when attacking>", ADJ % -10], [], 20, 7, 0, ("bow", "skull"),
     "Blighted arrows: +25% Strength when attacking, adjacent enemies -10%, for 2 turns."),
    ("Voodoo Hex", ["Rokhan"], 2, [ADJ % -20], [], 15, 6, 0, ("mask", "flask"),
     "Hexed foes stumble: adjacent enemies fight at -20% Strength for 2 turns."),
    # ---- spellcasters and other gifted units
    ("Frost Armor", ["Mage"], 2, ["[+30]% Strength <when defending>"], [], 8, 5, 0, ("crystal", "shield"),
     "A coat of ice: +30% Strength when defending for 2 turns."),
    ("Death Coil", ["Death Knight"], 1, [], ["[This Unit] heals [30] HP"], 8, 5, 1, ("skull", "heart"),
     "Unholy energy mends the death knight: heals 30 HP."),
    ("Spell Steal", ["Spellbreaker"], 1, [], ["Instantly gain [8] [Mana]"], 0, 6, 1, ("orb", "hand_light"),
     "Siphons magic from the air: +8 Mana for your empire."),
    ("Drunken Haze", ["Brewmaster"], 2, [ADJ % -15], [], 8, 5, 0, ("flask", "star"),
     "A cloud of strong brew: adjacent enemies fight at -15% Strength for 2 turns."),
    ("Lay on Hands", ["Vindicator", "Paladin"], 1, [], ["[This Unit] heals [40] HP"], 10, 6, 1, ("hand_light", "heart"),
     "Heals the unit for 40 HP."),
    ("Berserk", ["Headhunter", "Troll Berserker"], 1, ["[+30]% Strength <when attacking>"], [], 6, 5, 0, ("axe", "heart"),
     "Troll fury: +30% Strength when attacking for 1 turn."),
    ("Arcane Torrent", ["Blood Knight"], 1, [ADJ % -15], [], 8, 5, 0, ("orb", "bolt"),
     "A burst of stolen arcane power: adjacent enemies fight at -15% Strength for 1 turn."),
    ("Web", ["Crypt Fiend"], 1, [ADJ % -20], [], 8, 5, 0, ("net", "skull"),
     "Sticky webs: adjacent enemies fight at -20% Strength for 1 turn."),
    ("Chi Wave", ["Shado-Pan Monk"], 1, [], ["[This Unit] heals [25] HP"], 6, 5, 1, ("wave", "heart"),
     "Heals the monk for 25 HP."),
    ("Cannibalize", ["Abomination", "Ghoul"], 1, [], ["[This Unit] heals [30] HP"], 0, 5, 1, ("skull", "heart"),
     "Feeds on the fallen: heals 30 HP."),
    ("Aimed Shot", ["Farstrider", "Ranger-Lord"], 1, ["[+25]% Strength <when attacking>"], [], 6, 5, 0, ("bow", "target"),
     "A careful shot: +25% Strength when attacking for 1 turn."),
    ("Sentinel Owl", ["Huntress"], 2, ["[+2] Sight", "Can see invisible [Land] units"], [], 5, 4, 0, ("eye", "moon"),
     "An owl scouts ahead: +2 Sight and sees stealthed units for 2 turns."),
    ("Feral Leap", ["Worgen Stalker", "Worgen Ravager"], 1, ["[+2] Movement"], [], 5, 4, 0, ("wolf", "boot"),
     "+2 Movement for 1 turn."),
]


def all_spells():
    out = []
    for cls, (name, turns, status, effects, mana, cd, mv, glyphs, text) in CLASS_SPELLS.items():
        out.append((name, HERO_CLASSES[cls], turns, status, effects, mana, cd, mv, glyphs, text))
    return out + SPELLS


def spell_uniques(name, turns, status, effects, mana, cd, mv):
    cool = name + " Cooldown"
    cost = " <costs [%d] [%s]>" % (mana, MANA) if mana else ""
    act = "[This Unit] gains the [%s] status for [%d] turn(s) <for units without [%s]> <for [%d] movement>%s" % (name, turns, cool, mv, cost)
    hidden = " <hidden from users>"
    out = [act, "[This Unit] gains the [%s] status for [%d] turn(s) <upon gaining the [%s] status>%s" % (cool, cd, name, hidden)]
    out += ["%s <upon gaining the [%s] status>%s" % (e, name, hidden) for e in effects]
    if mana:   # the AI's automatic cast pays its Mana here (a player pays through the button's cost)
        out.append("Instantly consumes [%d] [%s] <upon gaining the [%s] status> <for [AI player] Civilizations>%s" % (mana, MANA, name, hidden))
    # AI players can't press action buttons: cast automatically (buffs and curses in combat,
    # heals when badly hurt, summons and Mana at the start of a turn at war)
    when = ("<upon turn start> <when below [50] HP>" if any("heals" in e for e in effects) and not status
            else "<upon turn start> <when at war>" if effects and not status
            else "<upon entering combat>")
    gate = " <when above [%d] [%s]>" % (max(mana - 1, 0), MANA) if mana else ""
    out.append("[This Unit] gains the [%s] status for [%d] turn(s) %s <for units without [%s]> <for [AI player] Civilizations>%s%s"
               % (name, turns, when, cool, gate, hidden))
    return out


# ====================================================================== 3. landmarks
FIRST_FINDER = {
    "Kelp'thar Forest": "+100 Gold", "Lakkari Tar Pits": "+80 Science", "Lake Elune'ara": "+100 Faith",
    "Thousand Needles": "+80 Culture", "Mount Hyjal": "+150 Faith", "The Maelstrom": "+100 Faith",
    "Cape of Stranglethorn": "+150 Gold", "Blackrock Mountain": "+100 Science", "Un'Goro Crater": "+120 Science",
    "Moonglade": "+100 Faith", "Stonetalon Peak": "+80 Culture", "Teldrassil": "+100 Culture", "Red Rocks of Mulgore": "+100 Faith",
    "The Dark Portal": "+100 Culture", "The Nexus": "+150 Science", "Galakrond's Rest": "+100 Science", "Sunken Temple": "+100 Faith",
    "Maraudon": "+100 Gold", "The Lifeblood Pillar": "+100 Science",
    # Lost City of the Tol'vir already grants 500 Gold
}


def boss(name, era, culture):
    # every faction that finds the landmark gets the event, so computer players rarely take the
    # challenge (a test game with +20% weight had twice the raid bosses and an early Raid victory)
    return ["A [%s] rebels" % name, "Gain [%d] [Culture]" % culture, "Only available <starting from the [%s]>" % era, ai(-60)]


# wonder -> (event name, text, [(choice, uniques)])
DISCOVERIES = {
    "Blackrock Mountain": ("The Molten Depths",
        "Our scouts stand before Blackrock Mountain. Far below, the Firelord's servants stoke the fires of the Molten Core, "
        "and the Thorium Brotherhood trades at the mountain's foot.",
        [("Challenge the Firelord in his lair.", boss("Ragnaros the Firelord", "Age of the Third War", 60)),
         ("Trade with the Thorium Brotherhood.", ["Gain [120] [Gold]"]),
         ("Study the living stone of the Searing Gorge.", ["Gain [80] [Science]"])]),
    "Sunken Temple": ("The Temple of Atal'Hakkar",
        "In the Swamp of Sorrows, the drowned temple of the Atal'ai still echoes with chanting. They are calling their blood god back.",
        [("Break the ritual and face what answers.", boss("Hakkar the Soulflayer", "Age of the Dark Portal", 50)),
         ("Loot the flooded outer shrines.", ["Gain [100] [Gold]"]),
         ("Leave the swamp to its gods.", ["Gain [40] [Faith]"])]),
    "The Dark Portal": ("The Dark Portal",
        "A gate of carved stone towers over the Blasted Lands. Fel light flickers between its pillars, and something on the far side is watching.",
        [("Seal the gate with wards.", ["Gain [80] [Faith]"]),
         ("Study the fel magic that powers it.", ["Gain [100] [Science]", "Instantly gain [15] [Mana]"]),
         ("Stand against the Deceiver himself.", boss("Kil'jaeden the Deceiver", "Age of the Legion", 100))]),
    "Galakrond's Rest": ("The Bones of Galakrond",
        "The bones of Galakrond, the first and greatest proto-dragon, lie across the Dragonblight. The Scourge would give much to raise them.",
        [("Study the first of dragons.", ["Gain [100] [Science]"]),
         ("Burn the bones before the Scourge can use them.", ["Gain [80] [Faith]"]),
         ("Hunt the frost wyrm that guards them.", boss("Sapphiron", "Age of the Lich King", 80))]),
    "Mount Hyjal": ("Nordrassil",
        "The World Tree crowns the summit of Mount Hyjal, its roots bound to the Well of Eternity below.",
        [("Pray beneath its boughs.", ["Gain [100] [Faith]"]),
         ("Learn from its keepers.", ["Gain [60] [Culture]", "Gain [40] [Science]"]),
         ("Renew the night elves' oath to the tree.", ["Gain [150] [Faith]", "[2] free [Wisp] units appear",
                                                       "Only available <for [Night Elves] Civilizations>", ai(40)])]),
    "Un'Goro Crater": ("The Crater's Secrets",
        "Un'Goro is a lost world of giant plants and devilsaurs. Among the ferns stand crystal pylons left by the titans.",
        [("Decipher the titan pylons.", ["Gain [120] [Science]"]),
         ("Harvest power crystals.", ["Gain [80] [Gold]", "Instantly gain [10] [Mana]"])]),
    "The Nexus": ("The Nexus",
        "Malygos's citadel of the Blue Dragonflight floats over Coldarra, humming with gathered magic.",
        [("Draw on the ley lines.", ["Instantly gain [30] [Mana]"]),
         ("Copy the dragonflight's tomes.", ["Gain [100] [Science]"])]),
    "The Lifeblood Pillar": ("The Lifeblood Pillar",
        "A titan pillar in the Sholazar Basin pours life into the jungle around it.",
        [("Tend the pillar's gardens.", ["Gain [80] [Faith]"]),
         ("Study the titan machine.", ["Gain [80] [Science]"])]),
    "Lost City of the Tol'vir": ("Whispers Beneath the Sands",
        "The Tol'vir guard their lost city in Uldum. Far beneath the desert, an old god dreams in the dark of Ahn'Qiraj.",
        [("March into the depths of Ahn'Qiraj.", boss("C'Thun", "Age of the Third War", 80)),
         ("Trade with the Tol'vir.", ["Gain [100] [Gold]"]),
         ("Record the city's titan carvings.", ["Gain [60] [Science]"])]),
    "The Maelstrom": ("The Maelstrom",
        "Where the Well of Eternity imploded, the sea turns forever around a whirlpool of churning magic. Deep below lies Deepholm.",
        [("Offer prayers to calm the waters.", ["Gain [60] [Faith]"]),
         ("Gather magic from the spray.", ["Instantly gain [20] [Mana]"]),
         ("Face the Destroyer as he breaks free.", boss("Deathwing the Destroyer", "Age of the Cataclysm", 120))]),
}


def discovery_events():
    events, uniques = [], []
    for wonder, (name, text, choices) in DISCOVERIES.items():
        events.append({"name": name, "text": text, "presentation": "Alert",
                       "choices": [{"text": t, "uniques": u} for t, u in choices]})
        uniques.append("Triggers a [%s] event <upon discovering a [%s] tile> <hidden from users>" % (name, wonder))
    return events, uniques


LANDMARK_NATIONS = {
    "Dwarves": ["[+50 Science, +50 Culture] for discovering a Natural Wonder (bonus enhanced to [+100 Science, +100 Culture] "
                "if first to discover it)"],
    "Night Elves": ["[+1 Faith, +1 Culture] for every known Natural Wonder"],
}


# ====================================================================== 4. Alliance and Horde politics
def rebels(unit_by_era):
    out = []
    for k, (first, unit) in enumerate(unit_by_era):
        cond = "<starting from the [%s]>" % first
        if k + 1 < len(unit_by_era):
            cond += " <before the [%s]>" % unit_by_era[k + 1][0]
        out.append(("Let the dissenters take up arms.", ["A [%s] rebels" % unit, "Only available %s" % cond, ai(-30)]))
    return out


REBELS = rebels([("Age of Tribes", "Spearman"), ("Age of the Third War", "Musketeer"), ("Age of the Cataclysm", "Rifleman"),
                 ("Age of Azerite", "Shock Trooper")])


def politics_events():
    ev = []
    for side, other, banner in (("Alliance", "Horde", "the Alliance"), ("Horde", "Alliance", "the Horde")):
        kin = "Brother Against Brother" if side == "Alliance" else "Blood Against Blood"
        ev.append({"name": kin, "presentation": "Alert",
                   "text": "We have declared war on fellow members of %s. Our people and our allies are outraged." % banner,
                   "choices": [{"text": "Pay reparations to quiet the dissenters.", "uniques": ["Gain [-150] [Gold]", need(150, "Gold"), ai(20)]},
                               {"text": "Justify the war in every square and temple.", "uniques": ["Gain [-100] [Culture]", need(100, "Culture"), ai(10)]}]
                              + [{"text": t, "uniques": u} for t, u in REBELS]})
        ev.append({"name": "%s Attacks!" % ("The Horde" if side == "Alliance" else "The Alliance"), "presentation": "Alert",
                   "text": ("The Horde has declared war on us. The people rally to the banners of the Alliance!" if side == "Alliance"
                            else "The Alliance has declared war on us. Lok'tar! The Horde stands as one!"),
                   "choices": [{"text": "Rally the people.", "uniques": ["Empire enters a [2]-turn Golden Age"]},
                               {"text": "Fill the war chest.", "uniques": ["Gain [150] [Gold]"]}]})
        ev.append({"name": "Betrayed by Kin" if side == "Alliance" else "Betrayed by the Horde", "presentation": "Alert",
                   "text": "A fellow member of %s has turned on us. Our people are shocked, and the world's sympathy is with us." % banner,
                   "choices": [{"text": "Mourn the broken oath.", "uniques": ["Gain [80] [Faith]"]},
                               {"text": "Turn grief into resolve.", "uniques": ["Gain [100] [Culture]"]}]})
    return ev


def politics_uniques(race):
    if race in ALLIANCE:
        side, other, attacked, betrayed, kin = "Alliance", "Horde", "The Horde Attacks!", "Betrayed by Kin", "Brother Against Brother"
    elif race in HORDE:
        side, other, attacked, betrayed, kin = "Horde", "Alliance", "The Alliance Attacks!", "Betrayed by the Horde", "Blood Against Blood"
    elif race == "Pandaren":
        return ["Gain [60] [Faith] <upon being declared war on by [Alliance] Civilizations>",
                "Gain [60] [Faith] <upon being declared war on by [Horde] Civilizations>"]
    else:
        return []
    return ["Triggers a [%s] event <upon declaring war on [%s] Civilizations> <hidden from users>" % (kin, side),
            "Triggers a [%s] event <upon being declared war on by [%s] Civilizations> <hidden from users>" % (attacked, other),
            "Triggers a [%s] event <upon being declared war on by [%s] Civilizations> <hidden from users>" % (betrayed, side),
            "Gain [30] [Culture] <upon declaring war on [%s] Civilizations>" % other]


# ====================================================================== 5. themed barbarians
# barbarian unit -> (generic unit it replaces, lore)
BARBARIANS = {
    "Kobold Tunneler": ("Militia", "Candle-headed kobolds from the mines. They will fight to the death over their wax."),
    "Gnoll Poacher": ("Archer", "Hyena-headed gnolls of the Riverpaw and Gnoll packs, quick with a crude bow."),
    "Murloc Tidehunter": ("Spearman", "Mrrgllgl! Coastal murlocs armed with spears and nets, who raid in screeching swarms."),
    "Centaur Outrunner": ("Outrider", "Raiders of the Desolace clans, the bastard children of Cenarius. Fast and merciless."),
    "Harpy Windwitch": ("Ranger", "Winged harpies who nest in cliffs and hurl curses and javelins at travellers."),
    "Quilboar Thornguard": ("Swordsman", "Boar-men of the Razorfen, armoured in briars and blessed by Agamaggan."),
    "Ogre Mauler": ("Pikeman", "Two-headed or one, an ogre is a hill of muscle with a club."),
    "Naga Siren": ("Crossbowman", "Serpentine servants of Queen Azshara, risen from the sea with bows and frost magic."),
    "Satyr Hellcaller": ("Vanguard", "Night elves twisted by the Legion into goat-legged demons, haunting the dark woods."),
    "Defias Pillager": ("Musketeer", "The red-masked Defias Brotherhood, stonemasons turned outlaws, armed with blackpowder."),
    "Bloodsail Sharpshooter": ("Mountaineer", "Marksmen of the Bloodsail Buccaneers, the terror of the South Seas."),
    "Venture Co. Enforcer": ("Rifleman", "Goblin muscle hired by the Venture Company to strip the land bare."),
    "Kvaldir Reaver": ("Fusilier", "Cursed sea-raiders of the Howling Fjord, hulking and pale with kelp in their beards."),
    "Twilight Doomcaller": ("Grenadier", "Cultists of the Twilight's Hammer, hurling shadow-fire for the end of the world."),
    "Faceless Destroyer": ("Shock Trooper", "Servants of the Old Gods with tentacles for faces, risen from the dark."),
    # at sea
    "Bloodsail Corsair": ("War Galley", "A Bloodsail raiding galley."),
    "Naga Myrmidon": ("Brigantine", "Naga warriors who strike ships from beneath the waves."),
    "Bloodsail Raider": ("Buccaneer", "A Bloodsail boarding ship."),
    "Bloodsail Man-o'-War": ("Frigate", "The pride of the Bloodsail fleet."),
    "Kvaldir Longship": ("Destroyer", "A Kvaldir longship crewed by the drowned."),
}
BARB_ICONS = {
    "Kobold Tunneler": ("pick", "lantern"), "Gnoll Poacher": ("bow", "paw"), "Murloc Tidehunter": ("fish", "spear"),
    "Centaur Outrunner": ("horse", "bow"), "Harpy Windwitch": ("wing", "spear"), "Quilboar Thornguard": ("tusk", "shield"),
    "Ogre Mauler": ("fist", "hammer"), "Naga Siren": ("wave", "bow"), "Satyr Hellcaller": ("ram_head", "flame"),
    "Defias Pillager": ("mask", "gun"), "Bloodsail Sharpshooter": ("anchor", "gun"), "Venture Co. Enforcer": ("coins", "gun"),
    "Kvaldir Reaver": ("axe", "wave"), "Twilight Doomcaller": ("void", "bomb"), "Faceless Destroyer": ("tentacle_eye", "fist"),
    "Bloodsail Corsair": ("ship", "skull"), "Naga Myrmidon": ("wave", "spear"), "Bloodsail Raider": ("ship", "swords"),
    "Bloodsail Man-o'-War": ("ship", "cannon"), "Kvaldir Longship": ("ship", "axe"),
}
DROP = {"upgradesTo", "obsoleteTech", "civilopediaText", "attackSound", "replacementTextForUniques"}


def barbarian_units(units):
    by = {u["name"]: u for u in units}
    out = []
    for name, (base, text) in BARBARIANS.items():
        b = by[base]
        u = {k: copy.deepcopy(v) for k, v in b.items() if k not in DROP}
        u.update(name=name, uniqueTo="Barbarians", replaces=base,
                 uniques=[q for q in b.get("uniques", []) if "Raid" not in q and "upon discovering" not in q and "<for [AI player]" not in q],
                 civilopediaText=lore(text, "Fielded only by the barbarians, in place of the %s." % base))
        if b.get("obsoleteTech"):
            u["obsoleteTech"] = b["obsoleteTech"]
        if "attackSound" in b:
            u["attackSound"] = b["attackSound"]
        out.append(u)
    return out


# ====================================================================== 7. spies
SPY_NAMES = {
    "Humans": ["Mathias Shaw", "Renzik the Shiv", "Lady Elena Hartwell", "Corin Ashby", "Marla Fowler", "Tobias Greaves"],
    "Orcs": ["Garona's Shadow", "Zelga Grimtongue", "Grukk the Silent", "Ashka Nightfang", "Durgo Ironhide", "Mokra Blackhand"],
    "Night Elves": ["Shandris's Watcher", "Maiev's Eye", "Selenia Moonshadow", "Ilthara Duskwind", "Kaelis Silverleaf", "Nyara Starfall"],
    "Dwarves": ["Thargas Anvilmar", "Brenna Coalbeard", "Dunstan Stonehew", "Moira's Ear", "Gorran Ironfoot", "Hilda Blackvein"],
    "Gnomes": ["Fizzik Quickspanner", "Nixie Cogwhistle", "Bix Sprocketbang", "Tilly Gearsworth", "Mekki Fusefinger", "Pip Wobblebolt"],
    "Tauren": ["Kaya Swiftwind", "Hagan Mistmane", "Tahu Quietstep", "Nala Duskhorn", "Orun Grasswalker", "Mayla Softhoof"],
    "Trolls": ["Zen'tabra", "Vol'kar the Quiet", "Jinzil Shadowtusk", "Ra'jin", "Zalazane's Shade", "Kezzik"],
    "Blood Elves": ["Valeera's Kin", "Lyrana Sunshadow", "Kaelan Dawnwhisper", "Sarith Emberleaf", "Melandra Sunveil", "Taeloran"],
    "High Elves": ["Sylanna Windrunner", "Aelthar Swiftbow", "Lirien Dawnstrider", "Faelan Brightwood", "Ithanis Silvergale", "Vaeryn"],
    "Pandaren": ["Taran Zhu's Shadow", "Li Mistwalker", "Mei Quietpaw", "Fung Snowfur", "Ana Riverleaf", "Shu Darkbrew"],
    "Forsaken": ["Lilian's Echo", "Varimathras's Whisper", "Mordo Graveshade", "Belle Tombwright", "Silas Rotfinger", "Agatha Crowe"],
    "Draenei": ["Arzaal the Silent", "Noraani", "Kehran", "Ishaali", "Torveen", "Menaal"],
    "Goblins": ["Sassy Hardwrench", "Gizmo Fastfingers", "Noz Sharpwallet", "Kezzle Quickbribe", "Brix Tunnelrat", "Zazzo Slyhands"],
    "Worgen": ["Lorna's Shadow", "Ivar Blackfang", "Eliza Thornwood", "Gideon Hollow", "Marta Duskhowl", "Corwin Ashgrove"],
    "Scourge": ["Cult Whisperer", "Plague Herald", "Shadow of Naxxramas", "Silent Acolyte", "Grave Watcher", "Whisper of the Lich"],
    "Dark Iron Dwarves": ["Grimtotem's Bane", "Hurley Blackbreath", "Kharra Emberfist", "Dorn Smoldersmith", "Vesha Ashvein", "Gorm Cinderhand"],
    "Kul Tirans": ["Flynn's Contact", "Taelia's Runner", "Amelia Blackwater", "Edwin Saltmarsh", "Hesta Driftwood", "Corbin Galewind"],
    "Zandalari Trolls": ["Zul's Whisper", "Kiro the Unseen", "Ja'zinn", "Naz'kira", "Roh'tal", "Zan'jin"],
}
SPY_NATIONS = {
    "Humans": ["[+15]% spy effectiveness [in all cities]"],
    "Forsaken": ["[+20]% spy effectiveness [in all cities]"],
    "Goblins": ["[+15]% spy effectiveness [in all cities]"],
    "Blood Elves": ["New spies start with [1] level(s)"],
    "Night Elves": ["[-20]% enemy spy effectiveness [in all cities]"],
    "Worgen": ["[-20]% enemy spy effectiveness [in all cities]"],
    "Pandaren": ["[-25]% enemy spy effectiveness [in all cities]"],
}
RAVENHOLDT = {"name": "Ravenholdt", "isWonder": True, "culture": 1, "requiredTech": "Banking",
              "greatPersonPoints": {"Great Merchant": 1},
              "uniques": ["Only available <when espionage is enabled>", "Gain an extra spy", "New spies start with [1] level(s)",
                          "[+15]% spy effectiveness [in all cities]"],
              "civilopediaText": lore("The hidden manor of the Assassins' League in the Alterac foothills, where the "
                                      "finest rogues of Azeroth are trained. Gives a spy, makes new spies more experienced "
                                      "and all your spies more effective.")}


# ====================================================================== 8. other ways to pay
FAITH_UNITS = ["Paladin", "Knight of the Silver Hand", "Vindicator", "Blood Knight", "Shado-Pan Monk"]
PURCHASE_NATIONS = {
    "Orcs": ["May buy [Melee] units with [Culture] [in all cities]"],
    "Zandalari Trolls": ["May buy [Mounted] units with [Faith] [in all cities]"],
    "Kul Tirans": ["May buy [Water] units with [Faith] [in all cities]"],
    "Goblins": ["Can spend Gold to annex or puppet a City-State that has been your Ally for [15] turns"],
}


# ====================================================================== 9. head starts in later ages
HEAD_STARTS = {   # race: (Arathor/Dark Portal, Third War/Lich King, Cataclysm onwards)
    "Humans": (["Footman", "Footman"], ["Paladin", "Footman"], ["Knight of the Silver Hand", "Footman"]),
    "Orcs": (["Grunt", "Grunt"], ["Grunt", "Wolf Rider"], ["Raider", "Grunt"]),
    "Night Elves": (["Huntress", "Wisp"], ["Huntress", "Glaive Thrower"], ["Mountain Giant", "Huntress"]),
    "Dwarves": (["Ironforge Rifleman"], ["Ram Rider", "Ironforge Rifleman"], ["Steam Armor", "Ironforge Rifleman"]),
    "Gnomes": (["Mechanostrider Rider"], ["Gnomish Bombardier", "Mechanostrider Rider"], ["Spider Tank", "Gnomish Bombardier"]),
    "Tauren": (["Tauren Warrior"], ["Tauren Warrior", "Kodo Beast"], ["Tauren Warrior", "Tauren Warrior"]),
    "Trolls": (["Headhunter", "Headhunter"], ["Headhunter", "Troll Berserker"], ["Troll Berserker", "Troll Berserker"]),
    "Blood Elves": (["Spellbreaker"], ["Spellbreaker", "Blood Knight"], ["Blood Knight", "Blood Knight"]),
    "High Elves": (["Farstrider", "Farstrider"], ["Farstrider", "Farstrider"], ["Ranger-Lord", "Farstrider"]),
    "Pandaren": (["Shado-Pan Monk"], ["Brewmaster", "Shado-Pan Monk"], ["Brewmaster", "Brewmaster"]),
    "Forsaken": (["Abomination"], ["Abomination", "Meat Wagon"], ["Deathstalker", "Abomination"]),
    "Draenei": (["Vindicator"], ["Vindicator", "Elekk Rider"], ["Lightforged Warframe", "Vindicator"]),
    "Goblins": (["Goblin Sapper"], ["Goblin Sapper", "Goblin Shredder"], ["Goblin Sapper", "Goblin Sapper"]),
    "Worgen": (["Gilnean Hunter"], ["Worgen Stalker", "Gilnean Hunter"], ["Worgen Ravager", "Gilnean Rifleman"]),
    "Scourge": (["Ghoul", "Ghoul"], ["Ghoul", "Ghoul", "Crypt Fiend"], ["Death Knight", "Ghoul", "Ghoul"]),
    "Dark Iron Dwarves": (["Fireguard"], ["Fireguard", "Fireguard"], ["Dark Iron Golem", "Fireguard"]),
    "Kul Tirans": (["Admiralty Gunner"], ["Admiralty Gunner", "Admiralty Gunner"], ["Admiralty Gunner", "Kul Tiran Marine"]),
    "Zandalari Trolls": (["Raptor Rider"], ["Raptor Rider", "Direhorn Rider"], ["Direhorn Rider", "Direhorn Rider"]),
}
TIER_OF = {era: (0 if i <= 2 else 1 if i <= 4 else 2) for i, era in enumerate(ERAS) if i >= 1}


def head_start_uniques(race):
    out = []
    first = "<upon founding a city> <when number of [Cities] is less than [2]>"
    for era, tier in TIER_OF.items():
        cond = "%s <if starting in the [%s]> <hidden from users>" % (first, era)
        units = HEAD_STARTS[race][tier]
        for unit in sorted(set(units)):
            n = units.count(unit)
            out.append(("[%d] free [%s] units appear %s" % (n, unit, cond)) if n > 1 else "Free [%s] appears %s" % (unit, cond))
        out.append("Instantly gain [%d] [%s] %s" % (20 * (tier + 1), MANA, cond))
        out.append("Gain [%d] [Gold] %s" % (100 * (tier + 1), cond))
    return out


# ====================================================================== guide page
TUTORIAL = ("Warcraft: Spells, Landmarks and Politics", [
    "Heroes and many spellcasters have spells: action buttons in the unit panel that cost Mana. After a spell is cast it "
    "recharges for a few turns (the unit shows a Cooldown status) before the button comes back. Computer players' units "
    "cast their spells by themselves.",
    "The first civilization to find each landmark (natural wonder) gets a reward. Ten landmarks start a lore event when "
    "discovered, and some let you challenge a raid boss: Ragnaros under Blackrock Mountain, Hakkar in the Sunken Temple, "
    "C'Thun beneath the Lost City of the Tol'vir, Sapphiron at Galakrond's Rest, Deathwing at the Maelstrom and Kil'jaeden "
    "at the Dark Portal.",
    "Alliance and Horde: declaring war on your own side angers your people (pay, lose Culture, or face rebels). When the "
    "other side declares war on you, your people rally; when your own side betrays you, the world sympathises. Declaring "
    "war on the other side earns a little Culture. The Pandaren gain Faith when either side attacks them.",
    "Barbarians are now the wild peoples of Azeroth: Kobolds, Gnolls, Murlocs, Centaurs, Harpies, Quilboar, Ogres, Naga, "
    "Satyrs, the Defias, Bloodsail pirates, the Venture Company, Kvaldir, the Twilight's Hammer and the Faceless.",
    "Spies have faction names, some factions are better at espionage or at stopping it, and Ravenholdt trains the best rogues.",
    "Other ways to pay: holy units can be bought with Faith; Orcs buy melee units with Culture; Zandalari buy mounted units "
    "and Kul Tirans buy ships with Faith; Goblins can buy out a city-state that has been their ally for 15 turns.",
    "Starting in a later age gives every faction lore-appropriate extra units, Mana and Gold with its first city.",
    "Maps: besides Azeroth, you can play Kalimdor, the Eastern Kingdoms, Northrend or Pandaria. Scenarios (New Game, "
    "Scenario) start in a moment of history: the Third War, the Cataclysm or the Battle for Azeroth.",
])


# ====================================================================== icons
def write_icons(images_dir):
    import os
    import icon_set as I
    n = 0
    for name, units, turns, status, effects, mana, cd, mv, (g1, g2), text in all_spells():
        I.save(I.compose(g1, g2), os.path.join(images_dir, "UnitPromotionIcons", name + ".png"), (255, 255, 255))
        I.save(I.compose("hourglass", g1), os.path.join(images_dir, "UnitPromotionIcons", name + " Cooldown.png"), (255, 255, 255))
        n += 2
    for name, (g1, g2) in BARB_ICONS.items():
        I.save(I.compose(g1, g2), os.path.join(images_dir, "UnitIcons", name + ".png"), (255, 255, 255))
        n += 1
    I.save(I.compose("mask", "key"), os.path.join(images_dir, "BuildingIcons", "Ravenholdt.png"), (0, 0, 0))
    return n + 1


# ====================================================================== apply
def apply(files, majors):
    by = lambda key: {x["name"]: x for x in files[key]}
    promos = by("UnitPromotions")
    units = by("Units")

    # 1. spells
    for name, who, turns, status, effects, mana, cd, mv, glyphs, text in all_spells():
        assert name not in promos and name + " Cooldown" not in promos, name
        cost = " Costs %d Mana." % mana if mana else ""
        files["UnitPromotions"].append({"name": name, "unitTypes": [], "uniques": status,
                                        "civilopediaText": lore("Spell. " + text + cost, "Recharges for %d turns after casting." % cd)})
        files["UnitPromotions"].append({"name": name + " Cooldown", "unitTypes": [], "uniques": [],
                                        "civilopediaText": lore("%s is recharging." % name)})
        for u in who:
            units[u]["uniques"] = units[u].get("uniques", []) + spell_uniques(name, turns, status, effects, mana, cd, mv)
            units[u]["civilopediaText"] = units[u].get("civilopediaText", []) + lore("Spell: %s. %s%s" % (name, text, cost))

    # 3. landmarks
    for t in files["Terrains"]:
        if t["name"] in FIRST_FINDER:
            t["uniques"] = t.get("uniques", []) + ["Grants [%s] to the first civilization to discover it" % FIRST_FINDER[t["name"]]]
    d_events, d_uniques = discovery_events()
    files["Events"] += d_events
    for u in files["Units"]:
        if u.get("unitType") != "Raid Boss" and u.get("uniqueTo") != "Barbarians" and u["name"] not in ("Felguard", "Infernal"):
            u["uniques"] = u.get("uniques", []) + d_uniques

    # 4. politics
    files["Events"] += politics_events()

    # 5. barbarians (made after the discovery uniques so they don't carry them)
    new_units = barbarian_units(files["Units"])
    assert not {u["name"] for u in new_units} & set(units)
    files["Units"] += new_units

    # 7. spies
    files["Buildings"].append(dict(RAVENHOLDT))
    assert sum(1 for b in files["Buildings"] if b["name"] == "Ravenholdt") == 1

    # 8. purchasing
    for u in FAITH_UNITS:
        units[u]["uniques"] = units[u].get("uniques", []) + ["Can be purchased with [Faith] [in all cities]"]

    # tutorial
    files["Tutorials"].append({"name": TUTORIAL[0], "civilopediaText": lore(*TUTORIAL[1])})

    # nations
    for n in majors:
        race = n["name"]
        n["spyNames"] = SPY_NAMES[race]
        n["uniques"] = (n.get("uniques", []) + politics_uniques(race) + LANDMARK_NATIONS.get(race, []) + SPY_NATIONS.get(race, [])
                        + PURCHASE_NATIONS.get(race, []) + head_start_uniques(race))
    return files
