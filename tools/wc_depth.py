"""The depth pass (Oct 2026): systems borrowed from the big Unciv mods, in Warcraft terms.

  1. Raids: eight world bosses (Onyxia ... N'Zoth) rise near a civilization through era-gated
     events, drop a Raid Trophy when slain, and a Raid victory goes to whoever collects enough.
     Plus a Religious victory (Unciv's built-in "world religion" milestone).
  2. Stealth and detection, battlefield auras, flanking, adjacency yields and raising the dead.
  3. Fateful choices: era events that adopt a permanent path (the fel, the Sunwell, the
     Shadowlands covenants) from a hidden policy branch.
  4. Hero classes (Champion / Arcane / Marksman) with class promotions, and a national
     wonder for every faction plus a Trophy Hall.
  5. In-game guide pages (Tutorials.json), an opening event for every faction and an event
     for every new age.
build.py calls apply(files, majors) after the v0.12 systems and before writing the jsons.
Everything here is original text; Warcraft names come from the setting.
"""
import copy

# ====================================================================== shared text helpers
def lore(*lines):
    return [{"text": t} for t in lines]


ERAS = ["Age of Tribes", "Age of Arathor", "Age of the Dark Portal", "Age of the Third War", "Age of the Lich King",
        "Age of the Cataclysm", "Age of the Legion", "Age of Azerite", "Age of the Void"]

FACTIONS = ["Humans", "Orcs", "Night Elves", "Dwarves", "Gnomes", "Tauren", "Trolls", "Blood Elves", "High Elves",
            "Pandaren", "Forsaken", "Draenei", "Goblins", "Worgen", "Scourge", "Dark Iron Dwarves", "Kul Tirans",
            "Zandalari Trolls"]


def need(amount, stat):
    return "Only available <when above [%d] [%s]>" % (amount - 1, stat)


def ai(weight):
    return "[%+d]%% weight to this choice for AI decisions" % weight


# ====================================================================== 1. raids
TROPHY = "Raid Trophy"
BOSS_TAG = "Raid Boss"
RAID_TARGET = 12                     # trophies needed for a Raid victory

BOSS_TYPE = {"name": BOSS_TAG, "movementType": "Land"}
BOSS_COMMON = [BOSS_TAG, "Unbuildable", "Cannot be purchased", "Never appears as a Barbarian unit",
               "Can only attack [{Land} {Military}] units", "[+25] HP when healing", "Can see invisible [Land] units"]

# name, strength, movement, (first era, era it fades), extra uniques, ranged (strength, range) or None, lore
BOSSES = [
    ("Onyxia", 45, 3, ("Age of the Dark Portal", "Age of the Lich King"), ["[+25]% Strength <when attacking>"], None,
     "Brood Mother of the black dragonflight and daughter of Deathwing, who once ruled Stormwind's court disguised as Lady "
     "Katrana Prestor. Her lair lies in the swamps of Dustwallow Marsh."),
    ("Hakkar the Soulflayer", 50, 2, ("Age of the Dark Portal", "Age of the Lich King"), ["Heals [25] damage if it kills a unit"], None,
     "The Blood God of the Gurubashi trolls, summoned into Azeroth by his Atal'ai priests and fed on the blood of the "
     "living in the jungles of Zul'Gurub."),
    ("Ragnaros the Firelord", 65, 2, ("Age of the Third War", "Age of the Cataclysm"), ["[-15]% Strength for enemy [Military] units in adjacent [All] tiles"], None,
     "Lord of the fire elementals, torn into the world by the Dark Iron dwarves and enthroned in the Molten Core beneath "
     "Blackrock Mountain. The ground burns wherever he stands."),
    ("C'Thun", 80, 1, ("Age of the Third War", "Age of the Cataclysm"), ["Cannot move"], (70, 2),
     "An Old God imprisoned by the Titans beneath Ahn'Qiraj, served by the silithid and the qiraji. It does not move; "
     "it does not need to. Its gaze reaches all who come near."),
    ("Sapphiron", 90, 3, ("Age of the Lich King", "Age of the Legion"), ["[-15]% Strength for enemy [Military] units in adjacent [All] tiles", "Heals [25] damage if it kills a unit"], None,
     "Once a blue dragon guarding the Lich King's frozen throne, slain and raised by Kel'Thuzad as the greatest frost "
     "wyrm of Naxxramas. Its wings bring a killing cold."),
    ("Deathwing the Destroyer", 120, 3, ("Age of the Cataclysm", "Age of Azerite"), ["[+25]% Strength <when attacking>", "Destroys tile improvements when attacking"], None,
     "The Aspect of Earth turned Aspect of Death, bound in molten elementium. His return from Deepholm shattered Azeroth "
     "in the Cataclysm."),
    ("Kil'jaeden the Deceiver", 145, 2, ("Age of the Legion", "Age of the Void"), ["[-15]% Strength for enemy [Military] units in adjacent [All] tiles"], None,
     "Eredar lord of the Burning Legion, who corrupted the orcs and sought the draenei across the stars for thousands of "
     "years. His lies weaken the hearts of all who stand near him."),
    ("N'Zoth the Corruptor", 175, 2, ("Age of Azerite", None), ["[-20]% Strength for enemy [Military] units in adjacent [All] tiles",
                                                               "Heals [25] damage if it kills a unit"], None,
     "The last free Old God, who whispered madness into Deathwing and dreamed for ages beneath Ny'alotha. When he wakes, "
     "the sky itself turns to tendrils."),
]


def boss_units():
    out = []
    for name, strength, move, eras, extra, ranged, text in BOSSES:
        u = {"name": name, "unitType": BOSS_TAG, "movement": move, "strength": strength, "cost": 999,
             "uniques": BOSS_COMMON + extra,
             "civilopediaText": lore(text, "A raid boss. Raid bosses appear only through raid events, cannot attack "
                                     "cities and heal quickly. Whoever slays one earns a Raid Trophy; collecting %d "
                                     "wins a Raid victory." % RAID_TARGET)}
        if ranged:
            u["rangedStrength"], u["range"] = ranged
        out.append(u)
    return out


def boss_events():
    events, triggers = [], []
    for name, strength, move, (first, last), extra, ranged, text in BOSSES:
        short = name.split(" the ")[0]
        ev = {"name": "Raid: %s" % short,
              "text": "%s %s" % (RAID_HOOKS[short], "Our champions are eager to raid. Do we sound the call?"),
              "presentation": "Alert",
              "choices": [
                  {"text": "Sound the call to raid! (%s rises near our lands; slay it for a Raid Trophy)" % short,
                   "uniques": ["A [%s] rebels" % name, "Gain [40] [Culture]", ai(60)]},
                  {"text": "Pay mercenaries to lure it elsewhere (-%d Gold)" % (60 + strength * 2),
                   "uniques": ["Gain [-%d] [Gold]" % (60 + strength * 2), need(60 + strength * 2, "Gold"), ai(-80)]},
              ]}
        events.append(ev)
        cond = "<upon turn start> <every [4] turns> <with [4]%% chance> <starting from the [%s]>" % first
        if last:
            cond += " <before the [%s]>" % last
        triggers.append("Triggers a [%s] event %s" % (ev["name"], cond))
    return events, triggers


RAID_HOOKS = {
    "Onyxia": "Black dragons have been seen circling our borders. The Brood Mother is hunting.",
    "Hakkar": "Gurubashi priests are spilling blood on jungle altars. The Soulflayer answers.",
    "Ragnaros": "The mountains near our lands split open and spill fire. The Firelord has broken through.",
    "C'Thun": "A great eye has opened beneath the sands near our borders. Its whispers keep our people awake.",
    "Sapphiron": "A killing frost descends from a cloudless sky. A frost wyrm of Naxxramas is on the wing.",
    "Deathwing": "The earth shakes and the sky burns orange. Deathwing has come out of Deepholm.",
    "Kil'jaeden": "Fel fire rains on the hills near our cities. Kil'jaeden the Deceiver walks Azeroth.",
    "N'Zoth": "The sea boils and black tendrils rise from the ground. The Corruptor has awakened.",
}

TROPHY_RESOURCE = {"name": TROPHY, "resourceType": "Strategic",
                   "uniques": ["Stockpiled", "Cannot be traded"],
                   "civilopediaText": lore("Proof of a raid boss slain: Onyxia's head, Ragnaros's hammer, a scale of "
                                           "Deathwing. Earned by the civilization whose unit lands the killing blow. "
                                           "Collect %d to win a Raid victory." % RAID_TARGET)}

# unit-trigger rewards go on every military unit (Unciv ignores unit triggers in GlobalUniques)
KILL_REWARDS = [
    "Instantly gain [1] [%s] <upon defeating a [%s] unit> <hidden from users>" % (TROPHY, BOSS_TAG),
    "Gain [150] [Gold] <upon defeating a [%s] unit> <hidden from users>" % BOSS_TAG,
    "[This Unit] gains the [Raid Veteran] promotion <upon defeating a [%s] unit> <hidden from users>" % BOSS_TAG,
]

RAID_VETERAN = {"name": "Raid Veteran", "unitTypes": [],
                "uniques": ["[+15]% Strength", "[+10] HP when healing"],
                "civilopediaText": lore("This unit struck down a raid boss. Its name is sung in every tavern.")}

VICTORIES = [
    {"name": "Raid", "victoryScreenHeader": "Slay raid bosses and collect %d Raid Trophies to win!" % RAID_TARGET,
     "milestones": ["Have at least [%d] [%s]" % (RAID_TARGET, TROPHY)],
     "victoryString": "Onyxia's head hangs over your gates, Ragnaros's hammer rests in your hall and the Old Gods dream "
                      "no more. No people of Azeroth has faced the great terrors as yours has. Your raiders are legends, "
                      "and the world bows to the slayers of gods.",
     "defeatString": "Another people has claimed the trophies of the great raids, and the bards sing their names, not "
                     "yours. Your warriors were brave, but bravery is not victory. There will be other raids."},
    {"name": "Religious", "victoryScreenHeader": "Make your faith the majority religion of the world to win!",
     "milestones": ["Become the world religion"],
     "victoryString": "From the cathedrals of Stormwind to the totems of Mulgore, the people of Azeroth now kneel to your "
                      "faith. Your priests, druids and shamans have won what no army could: the hearts of the world.",
     "defeatString": "Another faith now holds the hearts of Azeroth. Your temples empty and your priests fall silent. "
                     "But faith that endures in secret can still return."},
]

TROPHY_HALL = {"name": "Trophy Hall", "isNationalWonder": True, "cost": 260, "requiredTech": "Archaeology",
               "culture": 2,
               "uniques": ["[+2 Culture] [in capital] <for every [%s]>" % TROPHY,
                           "[+15]%% Strength <vs [%s] units> <for [Military] units>" % BOSS_TAG],
               "civilopediaText": lore("A hall of heads, hammers and dragon scales, where the deeds of your raiders are "
                                       "remembered. +2 Culture in the capital for every Raid Trophy, and your soldiers "
                                       "fight harder against raid bosses.")}


# ====================================================================== 2. stealth, auras, raising the dead
SHADOWMELD = {"name": "Shadowmeld", "unitTypes": [],
              "uniques": ["Invisible to non-adjacent units <in [Forest] tiles>"],
              "civilopediaText": lore("Night elves can melt into the shadows of the forest. While in a forest this unit "
                                      "can only be seen by adjacent units (or units that see the invisible).")}
KEEN_EYES = {"name": "Keen Eyes", "unitTypes": ["Scout", "Archery"], "prerequisites": [], "column": 41, "row": 0,
             "uniques": ["Can see invisible [Land] units", "[+1] Sight"],
             "civilopediaText": lore("Trackers trained to spot a rogue in the shadows or a night elf in the trees. "
                                     "This unit sees invisible units nearby.")}

# new promotions on existing unit types (name, types, prerequisites, uniques, lore)
EXTRA_PROMOTIONS = [
    ("Ambush", ["Scout", "Archery"], ["Keen Eyes"], ["[+20]% Strength <when attacking> <when fighting in [Forest] tiles>"],
     "Strikes from cover before the enemy knows it is there."),
    ("Flanker", ["Mounted"], [], ["[+50]% to Flank Attack bonuses"],
     "Rides around the enemy line to hit it where it is weakest."),
    ("Hold the Line", ["Sword", "Firearm"], [], ["[+15]% Strength <when defending> <when adjacent to a [Military] unit>"],
     "Shoulder to shoulder, the line does not break."),
]

UNIT_UNIQUES = {
    # stealth
    "Deathstalker": ["Invisible to non-adjacent units"],
    "Gilnean Hunter": ["Invisible to non-adjacent units <in [Forest] tiles>"],
    "Headhunter": ["Invisible to non-adjacent units <in [Jungle] tiles>"],
    "Goblin Sapper": ["Invisible to non-adjacent units <in [Forest] tiles>"],
    # detection
    "Scout": ["Can see invisible [Land] units"],
    "Farstrider": ["Can see invisible [Land] units"],
    "Ranger-Lord": ["Can see invisible [Land] units"],
    "Spellbreaker": ["Can see invisible [Land] units"],
    # auras and battle traits
    "Death Knight": ["[-10]% Strength for enemy [Military] units in adjacent [All] tiles"],
    "Abomination": ["[-10]% Strength for enemy [Military] units in adjacent [All] tiles",
                    "[1] free [Ghoul] units appear <upon being defeated>"],
    "Paladin": ["All adjacent units heal [10] HP when healing"],
    "Grunt": ["No damage penalty for wounded units"],
    "Troll Berserker": ["No damage penalty for wounded units"],
    "Tauren Warrior": ["[+15]% Strength <when attacking>"],
    "Vindicator": ["All adjacent units heal [5] HP when healing"],
    "Worgen Stalker": ["[+50]% to Flank Attack bonuses"],
    "Worgen Ravager": ["[+50]% to Flank Attack bonuses"],
}

NATION_UNIQUES = {
    "Night Elves": ["All newly-trained [Archery] units [in all cities] receive the [Shadowmeld] promotion",
                    "All newly-trained [Scout] units [in all cities] receive the [Shadowmeld] promotion",
                    "All newly-trained [Huntress] units [in all cities] receive the [Shadowmeld] promotion"],
    "Worgen": ["[+25]% to Flank Attack bonuses"],
    "Scourge": ["[1] free [Ghoul] units appear <upon conquering a city>",
                "When defeating a [{Land} {Melee} {non-[Hero]} {non-[Raid Boss]}] unit, earn [5] Gold and recruit it"],
}

IMPROVEMENT_UNIQUES = {
    "Deep Mine": ["[+1 Production] for each adjacent [Mountain]"],
}


# ====================================================================== 3. fateful choices
CHOICE_BRANCH = "Fateful Choices"

# policy name -> (uniques, lore)
CHOICE_POLICIES = {
    "Embraced the Fel": (["[+15]% Strength <for [Military] units>", "[-15]% growth [in all cities]"],
                         "We drank the power the Legion offered. Our armies burn with fel strength; our lands wither a little."),
    "Rejected the Fel": (["[+15]% [Faith] [in all cities]", "[+20]% Strength <vs [Barbarian] units> <for [Military] units>"],
                         "We refused the demons' bargain. Our faith is stronger for it, and we stand fast against the Legion's raiders."),
    "Sunwell Restored by the Light": (["[+15]% [Faith] [in all cities]", "[+2 Culture] [in capital]"],
                                      "The naaru M'uru's light rekindled the Sunwell, holy and arcane at once."),
    "Sunwell Rekindled by Arcane": (["[+10]% [Science] [in all cities]", "[+2 Science] [in capital]"],
                                    "Our magisters rebuilt the Sunwell as it was: a font of pure arcane power."),
    "Kyrian Covenant": (["[+2 Faith] [in all cities]", "[+5] HP when healing <for [Military] units>"],
                        "We swore to the Kyrian of Bastion, who ferry the worthy dead and guard them with radiant wings."),
    "Venthyr Covenant": (["[+15]% [Gold] [in all cities]", "[+10]% Strength <when attacking> <for [Military] units>"],
                         "We bargained with the Venthyr of Revendreth, who refine sinful souls in gothic halls."),
    "Night Fae Covenant": (["[+10]% [Food] [in all cities]", "[+10]% Strength <when fighting in [Forest] tiles> <for [Military] units>"],
                           "We joined the Night Fae of Ardenweald, who tend the souls of nature through cycles of rebirth."),
    "Necrolord Covenant": (["[+10]% [Production] [in all cities]", "[+10]% Strength <when defending> <for [Military] units>"],
                           "We marched with the Necrolords of Maldraxxus, the armies that defend the Shadowlands."),
}


def choice_branch():
    pols = []
    for k, (name, (uq, text)) in enumerate(CHOICE_POLICIES.items()):
        pols.append({"name": name, "uniques": list(uq), "row": 1 + k // 4, "column": 1 + k % 4,
                     "civilopediaText": lore(text, "A fateful choice: adopted only through an event, never bought.")})
    pols.append({"name": CHOICE_BRANCH + " Complete", "uniques": []})
    return {"name": CHOICE_BRANCH, "era": ERAS[0], "priorities": {},
            "uniques": ["Unavailable"],
            "civilopediaText": lore("Paths chosen at turning points of history: the fel offer of the Third War, the "
                                    "rebirth of the Sunwell, the covenants of the Shadowlands. They are adopted through "
                                    "events, cost no Culture and can never be undone."),
            "policies": pols}


def adopt(policy, ai_weight=0):
    out = ["Adopt [%s]" % policy]
    if ai_weight:
        out.append(ai(ai_weight))
    return out


CHOICE_EVENTS = [
    ("The Fel Offer", None, "Age of the Third War",
     "A cloaked warlock comes before our council with a chalice of green fire. 'Drink,' he says, 'and no army on Azeroth "
     "will stand against you.' The blood of demons glows in the cup.",
     [("Drink from the chalice (+15% Strength for military units, -15% growth)", adopt("Embraced the Fel", -20)),
      ("Cast it down (+15% Faith, +20% Strength against raiders and demons)", adopt("Rejected the Fel", 20))]),
    ("The Sunwell Reborn", ["High Elves", "Blood Elves"], "Age of the Legion",
     "The Sunwell can burn again. The priests say it must be reborn in the Light of the naaru; the magisters say it must "
     "be rebuilt as it was, pure arcane fire.",
     [("Rekindle it with the Light (+15% Faith, +2 Culture in the capital)", adopt("Sunwell Restored by the Light")),
      ("Rebuild the arcane font (+10% Science, +2 Science in the capital)", adopt("Sunwell Rekindled by Arcane"))]),
    ("The Covenants Call", None, "Age of the Void",
     "The veil to the Shadowlands has torn. Envoys of four great covenants stand before us, each asking for our "
     "allegiance in the war for the realm of death.",
     [("Bastion's Kyrian (+2 Faith in every city, faster healing)", adopt("Kyrian Covenant")),
      ("Revendreth's Venthyr (+15% Gold, +10% attack)", adopt("Venthyr Covenant")),
      ("Ardenweald's Night Fae (+10% Food, +10% Strength in forests)", adopt("Night Fae Covenant")),
      ("Maldraxxus's Necrolords (+10% Production, +10% defence)", adopt("Necrolord Covenant"))]),
]


# ====================================================================== 4. hero classes and national wonders
HERO_CLASSES = {
    "Champion Hero": ["Uther the Lightbringer", "Grom Hellscream", "Muradin Bronzebeard", "Baine Bloodhoof", "Maraad",
                      "Gazlowe", "Darius Crowley", "Dagran Thaurissan", "Daelin Proudmoore", "Chen Stormstout",
                      "Kelsey Steelspark"],
    "Arcane Hero": ["Kael'thas Sunstrider", "Kel'Thuzad", "Rastakhan", "Malfurion Stormrage"],
    "Marksman Hero": ["Alleria Windrunner", "Nathanos Blightcaller", "Rokhan"],
}
CLASS_PROMOTIONS = [
    ("Champion Hero", "Shield Wall", [], ["[+25]% Strength <when defending>"], "Plants their feet and holds the line for the army behind them."),
    ("Champion Hero", "Cleave", ["Shield Wall"], ["[+20]% Strength <when attacking>"], "Sweeping blows that strike several foes at once."),
    ("Champion Hero", "Last Stand", ["Cleave"], ["No damage penalty for wounded units", "[+10] HP when healing"], "Fights hardest when the end is near."),
    ("Arcane Hero", "Arcane Intellect", [], ["[+1] Sight", "Can see invisible [Land] units"], "Sharpened senses that see through illusion and shadow."),
    ("Arcane Hero", "Spell Ward", ["Arcane Intellect"], ["[+25]% Strength <vs [Ranged] units>"], "A shimmering ward that turns arrows and bolts."),
    ("Arcane Hero", "Blink", ["Spell Ward"], ["[+1] Movement", "Ignores Zone of Control"], "Steps through space to wherever the battle needs them."),
    ("Marksman Hero", "Eagle Eye", [], ["[+1] Sight", "Can see invisible [Land] units"], "Nothing moves on the battlefield without a marksman seeing it."),
    ("Marksman Hero", "Volley Fire", ["Eagle Eye"], ["[+20]% Strength <when attacking>"], "Arrows fall like rain."),
    ("Marksman Hero", "Camouflage", ["Volley Fire"], ["Invisible to non-adjacent units <in [Forest] tiles>"], "Vanishes among the trees between shots."),
]

# race -> (name, tech, cost, uniques, lore)
NATIONAL_WONDERS = {
    "Humans": ("Stormwind Throne Room", "War Doctrine", 300, ["[+15]% Production when constructing [Military] units [in all cities]", "[+2 Happiness] [in capital]"],
               "Where the kings of Stormwind hold court beneath the banners of the Alliance."),
    "Orcs": ("Ring of Valor", "War Doctrine", 300, ["[+10]% Strength <for [Military] units>", "[+2 Culture] [in capital]"],
             "An arena where orcs prove their strength before the Warchief and the Horde."),
    "Night Elves": ("Temple of the Moon", "Astronomy", 280, ["[+1 Faith] [in all cities]", "[+15]% Strength <when fighting in [Forest] tiles> <for [Military] units>"],
                    "The moonlit temple of the Sisters of Elune, where Tyrande's priestesses keep vigil."),
    "Dwarves": ("High Seat of Ironforge", "Steamworks", 300, ["[+10]% [Production] [in all cities]"],
                "The throne room of Ironforge, hewn from the heart of Khaz Modan beside the Great Forge."),
    "Gnomes": ("Tinkertown Workshops", "Steamworks", 280, ["[+10]% [Science] [in all cities]"],
               "Workshops crammed with half-finished inventions, where every gnome has a better idea."),
    "Tauren": ("Spirit Rise", "Archaeology", 280, ["[+1 Food, +1 Faith] [in all cities]"],
               "The quiet mesa of Thunder Bluff where the elders speak with the spirits of the ancestors."),
    "Trolls": ("Darkspear Voodoo Hall", "Alchemy", 260, ["[+10] HP when healing <for [Military] units>", "[+2 Faith] [in capital]"],
               "Where the witch doctors of the Echo Isles brew the hexes and healing draughts of the Darkspear."),
    "Blood Elves": ("Court of the Sun", "Arcane Science", 300, ["[+15]% [Gold] [in all cities]", "Provides [2] [Mana]"],
                    "The gilded court of Silvermoon, where magisters and nobles vie for the Regent Lord's favour."),
    "High Elves": ("Sunstrider Spire", "Arcane Science", 300, ["[+15]% [Culture] [in all cities]"],
                   "The soaring palace of the Sunstrider dynasty, older than any human kingdom."),
    "Pandaren": ("Temple of the Jade Serpent", "Natural Lore", 280, ["[+15]% Great Person generation [in all cities]"],
                 "The temple of Yu'lon, the Jade Serpent, where scholars seek wisdom in the waters of the Jade Forest."),
    "Forsaken": ("Royal Apothecary Society", "Alchemy", 280, ["[+10]% [Science] [in all cities]", "[+2 Gold] [in capital]"],
                 "The vats beneath the Undercity, where the apothecaries brew remedies and worse."),
    "Draenei": ("Vault of Lights", "Choral Hymns", 280, ["[+1 Faith, +1 Science] [in all cities]"],
                "The sanctum of the Exodar, where the naaru's light is kept and the anchorites pray."),
    "Goblins": ("Steamwheedle Exchange", "Auctioneering", 280, ["[+20]% [Gold] [in all cities]"],
                "The trading floor of the Steamwheedle Cartel. Everything has a price; most things are on sale."),
    "Worgen": ("Greymane Court", "Long Rifles", 280, ["[+20]% Strength <when fighting in [Forest] tiles> <for [Military] units>", "[+2 Culture] [in capital]"],
               "The court of King Genn Greymane, where Gilneas plans its vengeance."),
    "Scourge": ("Throne of the Damned", "Frost Enchantment", 320, ["[+15]% Strength <for [Military] units>", "[+2 Faith] [in capital]"],
                "A throne of ice and bone from which the Lich King's will reaches every ghoul and wyrm."),
    "Dark Iron Dwarves": ("Black Anvil", "Steamworks", 300, ["[+15]% Production when constructing [Siege] units [in all cities]", "[+10]% [Production] [in all cities]"],
                          "The great anvil of Shadowforge City, struck by the Dark Iron forgemasters in the glow of molten fire."),
    "Kul Tirans": ("Proudmoore Admiralty", "Navigation", 280, ["[+20]% Production when constructing [Water] units [in all cities]", "[+2 Gold] [in capital]"],
                   "The halls of the Lord Admiral in Boralus, from which the greatest fleet on Azeroth is commanded."),
    "Zandalari Trolls": ("Great Seal of Dazar'alor", "Auctioneering", 300, ["[+15]% [Culture] [in all cities]", "[+2 Gold] [in capital]"],
                         "The golden seat of the Zandalari Empire atop the great pyramid of Dazar'alor."),
}


def national_wonders():
    out = []
    for race, (name, tech, cost, uq, text) in NATIONAL_WONDERS.items():
        out.append({"name": name, "isNationalWonder": True, "uniqueTo": race, "cost": cost, "requiredTech": tech,
                    "culture": 1, "uniques": list(uq) + ["Never destroyed when the city is captured"],
                    "civilopediaText": lore(text, "A national wonder of the %s." % race)})
    out.append(copy.deepcopy(TROPHY_HALL))
    return out


# ====================================================================== 5. opening and era events, guide pages
# race -> (text, [(choice text, uniques)])
OPENINGS = {
    "Humans": ("Our first city rises on the bones of Arathor, the old kingdom of men. The Light and the sword will guard it.",
               [("Raise a militia (a free Militia)", ["Free [Militia] appears"]), ("Build a chapel (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Orcs": ("The clans have come together under one banner. Our first stronghold is raised in a land as harsh as we are.",
             [("Sharpen the axes (a free Spearman)", ["Free [Spearman] appears"]), ("Beat the war drums (+30 Culture)", ["Gain [30] [Culture]"])]),
    "Night Elves": ("Beneath the boughs of the ancient forest, the Kaldorei found their first city in the light of Elune.",
                    [("Send the Sentinels into the woods (a free Scout)", ["Free [Scout] appears"]), ("Pray at the moonwell (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Dwarves": ("Deep in the mountains, the first halls of our kingdom are carved and the first forge is lit.",
                [("Open the first mine (+40 Production worth of Gold)", ["Gain [40] [Gold]"]), ("Toast the founding (+30 Culture)", ["Gain [30] [Culture]"])]),
    "Gnomes": ("Our first city is founded, and three gnomes have already proposed improvements to it.",
               [("Fund the inventors (+40 Science)", ["Gain [40] [Science]"]), ("Build a clockwork scout (a free Scout)", ["Free [Scout] appears"])]),
    "Tauren": ("The tribes gather on the plains and raise their first great tent. The Earth Mother watches over us.",
               [("Hunt the plainstriders (+1 population)", ["[1] population in a random city"]), ("Speak with the spirits (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Trolls": ("The Darkspear plant their totems on new ground. The loa have shown us the way.",
               [("Call the hunters (a free Scout)", ["Free [Scout] appears"]), ("Honor the loa (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Blood Elves": ("From the ashes of the old kingdom, the sin'dorei raise a new city of gold and crimson.",
                    [("Gather the magisters (+40 Science)", ["Gain [40] [Science]"]), ("Hold a grand reception (+30 Culture)", ["Gain [30] [Culture]"])]),
    "High Elves": ("The quel'dorei found their first city in the eternal spring of Eversong, guarded by runestones.",
                   [("Raise the runestones (+30 Culture)", ["Gain [30] [Culture]"]), ("Send out the Farstriders (a free Scout)", ["Free [Scout] appears"])]),
    "Pandaren": ("The pandaren raise their first village among misty peaks and terraced fields. The tea is warm.",
                 [("Brew a celebration (+30 Culture)", ["Gain [30] [Culture]"]), ("Tend the fields (+1 population)", ["[1] population in a random city"])]),
    "Forsaken": ("Free of the Lich King's will, the Forsaken claim their first city among the ruins of the living.",
                 [("Raise the walls (+40 Gold)", ["Gain [40] [Gold]"]), ("Put the apothecaries to work (+40 Science)", ["Gain [40] [Science]"])]),
    "Draenei": ("After ages of flight across the stars, the draenei set down and build their first city. The Light has led us here.",
                [("Pray in thanks (+30 Faith)", ["Gain [30] [Faith]"]), ("Salvage the crystals (+40 Science)", ["Gain [40] [Science]"])]),
    "Goblins": ("A new city, a new market! The first shop is already open and the prices are already high.",
                [("Open for business (+60 Gold)", ["Gain [60] [Gold]"]), ("Hire some muscle (a free Militia)", ["Free [Militia] appears"])]),
    "Worgen": ("Behind the Greymane Wall, Gilneas raises its first city. Whatever comes, we will face it together.",
               [("Muster the watch (a free Militia)", ["Free [Militia] appears"]), ("Build the harvest hall (+1 population)", ["[1] population in a random city"])]),
    "Scourge": ("The cold of Northrend gathers into a will. The first necropolis rises, and the dead begin to stir.",
                [("Raise the fallen (a free Ghoul)", ["Free [Ghoul] appears"]), ("Spread the plague (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Dark Iron Dwarves": ("In the shadow of the mountain, the Dark Irons light their forges. Fire is our birthright.",
                          [("Stoke the forges (+40 Gold)", ["Gain [40] [Gold]"]), ("Arm the guard (a free Spearman)", ["Free [Spearman] appears"])]),
    "Kul Tirans": ("The first city of Kul Tiras rises above a deep harbor. The sea will make us great.",
                   [("Build the docks (+40 Gold)", ["Gain [40] [Gold]"]), ("Bless the tides (+30 Faith)", ["Gain [30] [Faith]"])]),
    "Zandalari Trolls": ("The Zandalari raise a golden temple at the heart of their first city. An empire begins.",
                         [("Honor the loa of kings (+30 Faith)", ["Gain [30] [Faith]"]), ("Gather tribute (+40 Gold)", ["Gain [40] [Gold]"])]),
}

ERA_EVENTS = {
    "Age of Arathor": ("The Age of Arathor",
                       "Kingdoms rise where tribes once roamed. Thoradin's Arathor unites the humans, and the elves teach them magic.",
                       [("Build roads between our cities (+60 Gold)", ["Gain [60] [Gold]"]), ("Found a school of magic (+60 Science)", ["Gain [60] [Science]"])]),
    "Age of the Dark Portal": ("The Dark Portal Opens",
                               "A rift has opened in the Black Morass and the orcish Horde pours through. The age of war has begun.",
                               [("Raise our defences (a free Spearman)", ["Free [Spearman] appears"]), ("Gird our faith (+60 Faith)", ["Gain [60] [Faith]"])]),
    "Age of the Third War": ("The Third War",
                             "Plague in Lordaeron, demons in Ashenvale, a prince who took up a cursed blade. The world will not be the same.",
                             [("Prepare for the worst (+80 Gold)", ["Gain [80] [Gold]"]), ("Seek the prophet's counsel (+80 Culture)", ["Gain [80] [Culture]"])]),
    "Age of the Lich King": ("The Lich King Stirs",
                             "Atop the Frozen Throne, the Lich King gathers his armies. Every people of Azeroth looks north.",
                             [("Forge weapons against the dead (+100 Production worth of Gold)", ["Gain [100] [Gold]"]), ("Call the priests (+100 Faith)", ["Gain [100] [Faith]"])]),
    "Age of the Cataclysm": ("The Cataclysm",
                             "Deathwing has torn the world apart. Coastlines are drowned, mountains split and old roads gone.",
                             [("Rebuild our cities (+1 population)", ["[1] population in a random city"]), ("Study the elemental chaos (+120 Science)", ["Gain [120] [Science]"])]),
    "Age of the Legion": ("The Legion Returns",
                          "The Burning Legion has come again, in greater numbers than ever. Azeroth must stand together or burn.",
                          [("Rally every soldier (a 3-turn Golden Age)", ["Empire enters a [3]-turn Golden Age"]), ("Seek the Pillars of Creation (+150 Science)", ["Gain [150] [Science]"])]),
    "Age of Azerite": ("The Age of Azerite",
                       "The world-soul of Azeroth bleeds a golden ore of terrible power, and every nation wants it.",
                       [("Mine the azerite (+200 Gold)", ["Gain [200] [Gold]"]), ("Heal the world-soul (+200 Faith)", ["Gain [200] [Faith]"])]),
    "Age of the Void": ("The Void Beckons",
                        "Beyond the Shadowlands and the stars, the Void watches. The last age of Azeroth has begun.",
                        [("Hold to the Light (+250 Faith)", ["Gain [250] [Faith]"]), ("Study the darkness (+250 Science)", ["Gain [250] [Science]"])]),
}


def opening_and_era_events():
    events, per_race = [], {}
    for race, (text, choices) in OPENINGS.items():
        name = "A New Beginning: %s" % race
        events.append({"name": name, "text": text, "presentation": "Alert",
                       "choices": [{"text": t, "uniques": u} for t, u in choices]})
        per_race[race] = ["Triggers a [%s] event <upon founding a city> <when number of [Cities] is less than [2]>" % name]
    era_triggers = []
    for era, (name, text, choices) in ERA_EVENTS.items():
        events.append({"name": name, "text": text, "presentation": "Alert",
                       "choices": [{"text": t, "uniques": u} for t, u in choices]})
        era_triggers.append("Triggers a [%s] event <upon entering the [%s]>" % (name, era))
    return events, per_race, era_triggers


TUTORIALS = [
    ("Warcraft: Mana", ["Mana is the stockpiled arcane energy of your civilization. Every capital gathers a little each "
                        "turn, and each race has buildings that gather more (Moonwells, Voodoo Lounges, Arcane Sanctums...).",
                        "Spellcasters, heroes, magical buildings and wonders, Mage Tower portals and some event choices "
                        "spend Mana. Check your stockpile on the resource overview."]),
    ("Warcraft: Blight and Cleansing", ["The Scourge spread Plagued Land and demons leave Fel-Scorched Land, which ruin "
                                        "tile yields.", "Only Clerics (each race has its own) can remove them, with the "
                                        "Remove Plagued Land and Remove Fel-Scorched Land actions. Peasants cannot."]),
    ("Warcraft: Heroes", ["Every faction can field one hero at a time. Heroes inspire nearby units (+15% Strength), heal "
                          "when they kill and grow stronger in later ages.",
                          "Heroes come in three classes, each with its own promotions: Champions (front-line fighters), "
                          "Arcane heroes (casters who see through stealth) and Marksmen (ranged hunters who vanish in forests)."]),
    ("Warcraft: Portals", ["A Mage Tower lets newly trained military units open a portal: spend 10 Mana in a city to gain "
                           "Portal Attunement for one turn, then travel instantly to another of your cities up to 20 tiles away."]),
    ("Warcraft: Alliance, Horde and Undead", ["Factions belong to the Alliance, the Horde, the Undead or stand apart. These "
                                              "tags matter: some units and abilities fight harder against a rival faction."]),
    ("Warcraft: Raids", ["From the Age of the Dark Portal on, raid bosses (Onyxia, Ragnaros, C'Thun, Deathwing...) may stir "
                         "near your lands. You choose whether to sound the call to raid.",
                         "Raid bosses cannot attack cities but are deadly in the field. Whoever lands the killing blow "
                         "earns a Raid Trophy, 150 Gold and a Raid Veteran promotion. Collect %d trophies for a Raid "
                         "victory, and build a Trophy Hall to turn them into Culture." % RAID_TARGET]),
    ("Warcraft: Stealth and Auras", ["Some units are hard to see: Night Elf archers and scouts Shadowmeld in forests, "
                                     "Forsaken Deathstalkers are always hidden, Troll Headhunters vanish in jungles. Only "
                                     "adjacent units, Scouts, Farstriders, Spellbreakers, raid bosses and some heroes can "
                                     "see them.",
                                     "Auras affect neighbouring tiles: Death Knights and Abominations weaken adjacent enemies, "
                                     "Paladins and Vindicators heal allies. Orc Grunts and Troll Berserkers fight on unhurt "
                                     "when wounded, Worgen excel at flanking, and the Scourge raise the melee soldiers they defeat."]),
    ("Warcraft: Fateful Choices", ["At turning points of history your civilization must choose a path: the fel offer of "
                                   "the Third War, the rebirth of the Sunwell for the elves, and the covenants of the "
                                   "Shadowlands in the Age of the Void.",
                                   "These choices are permanent and appear in the policy screen under Fateful Choices. "
                                   "They cost no Culture."]),
    ("Warcraft: Victories", ["Besides the usual Scientific (the Titan vessel), Cultural (the Well of Eternity), Domination "
                             "and Diplomatic (the Grand Council of Azeroth) victories, UncivWarcraft adds a Raid victory "
                             "(collect %d Raid Trophies) and a Religious victory (make your faith the world's majority "
                             "religion)." % RAID_TARGET]),
    ("Warcraft: Events", ["Festivals, plagues, refugees, demon incursions, dragonflights, raids and the changing of the "
                          "ages all arrive as events with choices. Some choices cost Gold, Faith or Mana and are offered "
                          "only when you can pay."]),
]


def tutorials():
    return [{"name": n, "civilopediaText": lore(*lines)} for n, lines in TUTORIALS]


# ====================================================================== icons
ICONS = {
    "UnitIcons": {"Onyxia": ("dragon", "flame"), "Hakkar the Soulflayer": ("mask", "heart"),
                  "Ragnaros the Firelord": ("flame", "hammer"), "C'Thun": "tentacle_eye",
                  "Sapphiron": ("dragon", "skull"), "Deathwing the Destroyer": ("dragon", "mountain"),
                  "Kil'jaeden the Deceiver": ("skull", "flame"), "N'Zoth the Corruptor": ("tentacle_eye", "void")},
    "ResourceIcons": {TROPHY: ("skull", "star")},
    "UnitPromotionIcons": {"Raid Veteran": ("skull", "sword"), "Shadowmeld": ("moon", "tree"), "Keen Eyes": "eye",
                           "Ambush": ("bow", "tree"), "Flanker": ("horse", "arrows_up"), "Hold the Line": ("shield", "shield"),
                           "Shield Wall": "shield", "Cleave": "axe", "Last Stand": ("shield", "heart"),
                           "Arcane Intellect": ("eye", "sparkle"), "Spell Ward": ("orb", "shield"), "Blink": ("portal", "boot"),
                           "Eagle Eye": ("eye", "target"), "Volley Fire": ("bow", "star"), "Camouflage": ("tree", "eye")},
    "PolicyIcons": {"Embraced the Fel": ("flame", "skull"), "Rejected the Fel": ("hand_light", "shield"),
                    "Sunwell Restored by the Light": ("sun", "hand_light"), "Sunwell Rekindled by Arcane": ("sun", "orb"),
                    "Kyrian Covenant": ("wing", "hand_light"), "Venthyr Covenant": ("castle", "chalice"),
                    "Night Fae Covenant": ("tree", "moon"), "Necrolord Covenant": ("skull", "shield")},
    "PolicyBranchIcons": {CHOICE_BRANCH: ("scales", "star")},
    "VictoryTypeIcons": {"Raid": ("dragon", "sword"), "Religious": "temple"},
}
BUILDING_ICONS = {
    "Stormwind Throne Room": ("crown", "sword"), "Ring of Valor": ("swords", "axe"), "Temple of the Moon": ("moon", "temple"),
    "High Seat of Ironforge": ("crown", "anvil"), "Tinkertown Workshops": ("gears", "hammer"), "Spirit Rise": ("totem", "feather_plume"),
    "Darkspear Voodoo Hall": ("mask", "flask"), "Court of the Sun": ("sun", "coins"), "Sunstrider Spire": ("spire", "sun"),
    "Temple of the Jade Serpent": ("pagoda", "jade"), "Royal Apothecary Society": ("flask", "skull"),
    "Vault of Lights": ("naaru", "crystal"), "Steamwheedle Exchange": ("coins", "scales"), "Greymane Court": ("castle", "wolf"),
    "Throne of the Damned": ("crown", "skull"), "Black Anvil": ("anvil", "flame"), "Proudmoore Admiralty": ("anchor", "crown"),
    "Great Seal of Dazar'alor": ("ziggurat", "coins"), "Trophy Hall": ("skull", "star"),
}


def write_icons(images_dir):
    import os
    import icon_set as I
    n = 0
    for folder, table in ICONS.items():
        for name, recipe in table.items():
            main, badge = (recipe, None) if isinstance(recipe, str) else recipe
            I.save(I.compose(main, badge), os.path.join(images_dir, folder, name + ".png"), (255, 255, 255))
            n += 1
    for name, (main, badge) in BUILDING_ICONS.items():
        I.save(I.compose(main, badge), os.path.join(images_dir, "BuildingIcons", name + ".png"), (0, 0, 0))
        n += 1
    return n


# ====================================================================== apply
def apply(files, majors):
    by = lambda key: {x["name"]: x for x in files[key]}
    # 1. raids
    files["UnitTypes"].append(dict(BOSS_TYPE))
    files["Units"] += boss_units()
    files["TileResources"].append(dict(TROPHY_RESOURCE))
    files["UnitPromotions"].append(dict(RAID_VETERAN))
    for u in files["Units"]:
        if u.get("strength") and u.get("unitType") != BOSS_TAG:
            u["uniques"] = u.get("uniques", []) + KILL_REWARDS
    files["VictoryTypes"] += copy.deepcopy(VICTORIES)
    raid_events, raid_triggers = boss_events()
    files["Events"] += raid_events

    # 2. stealth, auras, raising the dead
    files["UnitPromotions"] += [dict(SHADOWMELD), dict(KEEN_EYES)]
    for k, (name, types, pre, uq, text) in enumerate(EXTRA_PROMOTIONS):
        files["UnitPromotions"].append({"name": name, "unitTypes": types, "prerequisites": pre, "uniques": uq,
                                        "column": 40, "row": k, "civilopediaText": lore(text)})
    units = by("Units")
    for name, uq in UNIT_UNIQUES.items():
        if uq:
            units[name]["uniques"] = units[name].get("uniques", []) + uq
    imps = by("TileImprovements")
    for name, uq in IMPROVEMENT_UNIQUES.items():
        imps[name]["uniques"] = imps[name].get("uniques", []) + uq

    # 4a. hero classes: three unit types, a "Hero" tag so [Hero] filters keep working
    for t in HERO_CLASSES:
        files["UnitTypes"].append({"name": t, "movementType": "Land"})
    hero_of = {h: t for t, hs in HERO_CLASSES.items() for h in hs}
    for u in files["Units"]:
        if u.get("unitType") == "Hero":
            u["unitType"] = hero_of[u["name"]]
            u["uniques"] = ["Hero"] + u.get("uniques", []) + ["Can see invisible [Land] units"]
            u["civilopediaText"] = u.get("civilopediaText", []) + lore("Hero class: %s." % hero_of[u["name"]].replace(" Hero", ""))
    for p in files["UnitPromotions"]:
        if "Hero" in p.get("unitTypes", []):
            p["unitTypes"] = [t for t in p["unitTypes"] if t != "Hero"] + list(HERO_CLASSES)
    for k, (cls, name, pre, uq, text) in enumerate(CLASS_PROMOTIONS):
        files["UnitPromotions"].append({"name": name, "unitTypes": [cls], "prerequisites": pre, "uniques": uq,
                                        "column": 34 + list(HERO_CLASSES).index(cls), "row": k % 3,
                                        "civilopediaText": lore(text)})
    # 4b. national wonders
    taken = {b["name"] for b in files["Buildings"]}
    new_b = national_wonders()
    clash = [b["name"] for b in new_b if b["name"] in taken]
    assert not clash, clash
    files["Buildings"] += new_b

    # 3. fateful choices
    files["Policies"].append(choice_branch())
    choice_events, choice_triggers = [], {}
    for name, only, era, text, choices in CHOICE_EVENTS:
        choice_events.append({"name": name, "text": text, "presentation": "Alert",
                              "choices": [{"text": t, "uniques": u} for t, u in choices]})
        for race in (only or FACTIONS):
            choice_triggers.setdefault(race, []).append("Triggers a [%s] event <upon entering the [%s]>" % (name, era))
    files["Events"] += choice_events

    # 5. openings, ages, guide pages
    oe_events, openings, era_triggers = opening_and_era_events()
    files["Events"] += oe_events
    files["Tutorials"] = tutorials()

    # nation triggers and abilities (major civs only; hidden from the civilopedia listing)
    for n in majors:
        race = n["name"]
        extra = raid_triggers + era_triggers + openings.get(race, []) + choice_triggers.get(race, [])
        n["uniques"] = n.get("uniques", []) + [t + " <hidden from users>" for t in extra] + NATION_UNIQUES.get(race, [])
    return files
