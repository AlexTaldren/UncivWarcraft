"""Unit upgrade lines (Oct 2026, user request): every line keeps its theme from start to finish.

  Melee (no guns):  Militia > Swordsman > Vanguard > Man-at-Arms > Royal Guard > Gladiator
                    > Vanquisher > Mechagnome Trooper
  Ranged:           Archer > Hunter > either
                      the Ranger line (bows: forest movement and bonuses, sight)
                        Ranger > Ranger Captain > Ranger-General
                      or the Rifleman line (guns: harder hitting, strong against cavalry)
                        Rifleman > Mountaineer > Grenadier > Azerite Sharpshooter
  Magic:            every faction has one school, chosen from the World of Warcraft classes its
                    race can take (see SCHOOLS): Arcane mages, Fel warlocks, Nature druids,
                    Elemental shamans, Holy priests, Scourge necromancers, troll Voodoo.
  Gnomes:           the Mechagnome Trooper is theirs alone (it replaces the Warbringer).

The stock-derived names used to put guns on melee units (Musketeer, Rifleman, Fusilier, Shock
Trooper) and a crossbowman in the bow line. Here those units are renamed everywhere, the gun
units become ranged, race unique units move to the slot that matches what they carry, and
three new lines get new units. Branching uses Unciv's "Can upgrade to [unit]".
build.py calls apply(files) after the race units and sounds, before wc_depth; rename_art()
before the pixel-art steps; write_icons() with the other icons.
"""
import json
import os
import re
import shutil

from wc_depth import lore

# old name -> new name (the old Rifleman becomes the Royal Guard; a new, ranged Rifleman is added)
RENAME = [("Musketeer", "Man-at-Arms"), ("Rifleman", "Royal Guard"), ("Fusilier", "Gladiator"),
          ("Shock Trooper", "Vanquisher"), ("Ranger", "Hunter"), ("Crossbowman", "Ranger")]
PROTECT = ["Ranger-Lord", "Ironforge Rifleman", "Gilnean Rifleman"]

RANGER_UNIQUES = ["[+1] Sight", "Double movement in [Forest]", "[+20]% Strength <when fighting in [Forest] tiles>"]
RIFLE_UNIQUES = ["[+33]% Strength <vs [Mounted] units>"]
MAGIC_UNIQUES = ["Ranged attacks may be performed over obstacles"]
MELEE_SOUND, BOW_SOUND, GUN_SOUND, ARCANE_SOUND = "metalhit", "arrow", "wc_rifle", "wc_arcane_blast"

# changes to existing (already renamed) units
CHANGES = {
    # melee line
    "Vanguard": dict(obsoleteTech="Mithril Forged Swords"),
    "Man-at-Arms": dict(requiredTech="Mithril Forged Swords", obsoleteTech="Storm Hammers", attackSound=MELEE_SOUND,
                        text="Veteran foot soldiers in mail and plate, the core of every kingdom's army after the Second War."),
    "Royal Guard": dict(requiredTech="Storm Hammers", attackSound=MELEE_SOUND,
                        text="The elite guard of the capital, in polished plate with sword and tower shield."),
    "Gladiator": dict(attackSound=MELEE_SOUND,
                      text="Arena-hardened warriors of every race, masters of axe and shield, champions of the Ring of Valor and the Gurubashi Arena."),
    # ranged line
    "Hunter": dict(add_uniques=["Can upgrade to [Rifleman]"], obsoleteTech="Scholarship",
                   text="Woodsmen and trackers with longbows. A Hunter can train as a Ranger (bows) or a Rifleman (guns)."),
    "Ranger": dict(requiredTech="Scholarship", obsoleteTech="Natural Lore", upgradesTo="Ranger Captain", strength=12,
                   rangedStrength=17, attackSound=BOW_SOUND, add_uniques=RANGER_UNIQUES,
                   text="Rangers of the wilds, who move through forests twice as fast, see farther and fight better among the trees."),
    "Mountaineer": dict(requiredTech="Long Rifles", add_uniques=RIFLE_UNIQUES),
    "Grenadier": dict(upgradesTo="Azerite Sharpshooter", add_uniques=RIFLE_UNIQUES),
    # Humans' magic line
    "Vanquisher": dict(attackSound=MELEE_SOUND, upgradesTo="Warbringer",
                       text="Champions of the last wars, in arcanite plate, who break the enemy line wherever it stands."),
    "Mechagnome Trooper": dict(uniqueTo="Gnomes", replaces="Warbringer", strength=95,
                               text="Mechagnomes of Mechagon, more machine than gnome, who fight in place of the Warbringer.",
                               text2="Stronger than a Warbringer."),
    # race unique units moved to the slot that matches their weapons
    "Headhunter": dict(add_uniques=["Can upgrade to [Rifleman]"]),
    "Farstrider": dict(add_uniques=["Can upgrade to [Rifleman]"]),
    "Ironforge Rifleman": dict(unitType="Ranged Firearm", range=2, strength=18, rangedStrength=26, replaces="Rifleman",
                               upgradesTo="Mountaineer", add_uniques=RIFLE_UNIQUES,
                               text2="Stronger than a Rifleman, with +25% Strength in hills."),
    "Admiralty Gunner": dict(unitType="Ranged Firearm", range=2, strength=17, rangedStrength=25, replaces="Rifleman",
                             upgradesTo="Mountaineer", add_uniques=RIFLE_UNIQUES,
                             text2="Stronger than a Rifleman, attacks from ships without penalty and sees farther."),
    "Troll Berserker": dict(requiredTech="Mithril Forged Swords", obsoleteTech="Storm Hammers", upgradesTo="Royal Guard",
                            text2="Stronger than a Man-at-Arms, +15% Strength when attacking, and heals 10 HP whenever it kills a unit."),
    "Gilnean Rifleman": dict(unitType="Ranged Firearm", range=2, strength=32, rangedStrength=34, replaces="Mountaineer",
                             requiredTech="Long Rifles", upgradesTo="Grenadier", obsoleteTech="Fragmentation Shards",
                             add_uniques=RIFLE_UNIQUES, text2="Stronger than a Mountaineer."),
    "Deathstalker": dict(unitType="Archery", strength=26, rangedStrength=30, replaces="Ranger Captain", requiredTech="Natural Lore",
                         obsoleteTech="Nature's Blessing", upgradesTo="Ranger-General", attackSound="crossbow",
                         text2="Stronger than a Ranger Captain, sees farther, ignores zones of control and is invisible to "
                               "units that aren't adjacent."),
    "Ranger-Lord": dict(unitType="Archery", strength=27, rangedStrength=32, replaces="Ranger Captain", requiredTech="Natural Lore",
                        obsoleteTech="Nature's Blessing", upgradesTo="Ranger-General", attackSound=BOW_SOUND, drop=["range"],
                        add_uniques=["Double movement in [Forest]"],
                        text2="Stronger than a Ranger Captain, sees farther and gains +25% Strength in forests."),
    "Crypt Fiend": dict(requiredTech="Long Rifles"),
    # content pass: the Nightborne archer sits in the Ranger slot (bows)
    "Duskwatch Sentinel": dict(requiredTech="Scholarship", obsoleteTech="Natural Lore", upgradesTo="Ranger Captain",
                               attackSound=BOW_SOUND, add_uniques=RANGER_UNIQUES[1:]),
    # Oct 24 2026 endgame pass (user request): riders stay riders, pikes stay on foot, the Paladin is endgame.
    # Mounted: Knight > Cavalry > War Rider > Grand Champion. War machines are their own line from War Golem.
    "Cavalry": dict(upgradesTo="War Rider"),
    # balance round 2: Humans rarely hold Horses, so the order's knights (and the Paladins after them) ride without
    "Knight of the Silver Hand": dict(upgradesTo="War Rider", drop=["requiredResource"]),
    "Raider": dict(upgradesTo="War Rider"),
    "Lancer": dict(upgradesTo="Cavalry"),
    # Anti-cavalry, on foot: Spearman > Pikeman > Halberdier > Siegebreaker > Phalanx
    "Pikeman": dict(upgradesTo="Halberdier"),
    "Shado-Pan Monk": dict(upgradesTo="Halberdier"),
    "Fireguard": dict(upgradesTo="Halberdier"),
    "Siegebreaker": dict(upgradesTo="Phalanx", add_uniques=["[+50]% Strength <vs [Mounted] units>"],
                         text="Heavy infantry with rocket mortars and tower shields, who break charging riders and war machines alike."),
    # the Humans' Paladin is their endgame rider (as in Warcraft II, where Knights become Paladins)
    "Paladin": dict(replaces="Grand Champion", requiredTech="Titan Logic", strength=105, cost=450, drop=["obsoleteTech", "upgradesTo", "requiredResource"],
                    text="Holy warriors of the Order of the Silver Hand, clad in blessed plate on barded chargers, who heal their comrades and "
                         "turn the tide wherever they ride. Humans field ordinary Knights early on; their riders become Paladins at the end of the age.",
                    text2="Stronger than a Grand Champion, inspires and heals nearby units, and can Lay on Hands."),
}

NEW_UNITS = [
    {"name": "Ranger Captain", "unitType": "Archery", "movement": 2, "strength": 24, "rangedStrength": 28, "cost": 200,
     "requiredTech": "Natural Lore", "obsoleteTech": "Nature's Blessing", "upgradesTo": "Ranger-General", "attackSound": BOW_SOUND,
     "uniques": RANGER_UNIQUES + ["Can see invisible [Land] units"],
     "text": "Veteran rangers who lead the scouts of the realm. They see stealthed units nearby."},
    {"name": "Ranger-General", "unitType": "Archery", "movement": 3, "strength": 50, "rangedStrength": 58, "cost": 320,
     "requiredTech": "Nature's Blessing", "attackSound": BOW_SOUND,
     "uniques": RANGER_UNIQUES + ["Can see invisible [Land] units"],
     "text": "The greatest archers of the age, in the tradition of Sylvanas and Alleria Windrunner."},
    {"name": "Rifleman", "unitType": "Ranged Firearm", "range": 2, "movement": 2, "strength": 16, "rangedStrength": 24, "cost": 150,
     "requiredTech": "Blackpowder", "obsoleteTech": "Long Rifles", "upgradesTo": "Mountaineer", "attackSound": GUN_SOUND,
     "uniques": RIFLE_UNIQUES,
     "text": "Riflemen with long guns in the style of Ironforge, deadly against charging cavalry."},
    {"name": "Azerite Sharpshooter", "unitType": "Ranged Firearm", "range": 2, "movement": 2, "strength": 75, "rangedStrength": 85,
     "cost": 450, "requiredTech": "Azerite Refinement", "requiredResource": "Azerite", "attackSound": GUN_SOUND,
     "uniques": RIFLE_UNIQUES,
     "text": "Marksmen whose rifles fire Azerite-charged rounds, the deadliest guns ever made on Azeroth."},
    {"name": "Warbringer", "unitType": "Heavy Infantry", "movement": 2, "strength": 90, "cost": 450, "requiredTech": "War Drums",
     "attackSound": MELEE_SOUND, "uniques": [],
     "text": "The greatest warriors of the Azerite age, who carry the war banner at the head of every charge."},
    # Oct 24 2026 endgame pass
    {"name": "Halberdier", "unitType": "Sword", "movement": 2, "strength": 25, "cost": 150, "requiredTech": "Mithril Forged Swords",
     "obsoleteTech": "Battle Formations", "upgradesTo": "Siegebreaker", "attackSound": MELEE_SOUND,
     "uniques": ["[+50]% Strength <vs [Mounted] units>"],
     "text": "Foot soldiers with long halberds, the wall that cavalry breaks upon."},
    {"name": "Phalanx", "unitType": "Heavy Infantry", "movement": 2, "strength": 85, "cost": 425, "requiredTech": "Titan Logic",
     "attackSound": MELEE_SOUND,
     "uniques": ["[+50]% Strength <vs [Mounted] units>", "[+50]% Strength <vs [War Machine] units>"],
     "text": "A locked wall of tower shields and runed pikes, raised to stop the charges of the last wars, beast and machine alike."},
    {"name": "War Rider", "unitType": "Mounted", "movement": 4, "strength": 60, "cost": 350, "requiredTech": "Liquid Fire",
     "obsoleteTech": "Titan Logic", "upgradesTo": "Grand Champion", "requiredResource": "Horses", "attackSound": "cavalry",
     "uniques": ["Can move after attacking", "No defensive terrain bonus", "[-33]% Strength <vs cities> <when attacking>", "Never appears as a Barbarian unit"],
     "text": "Heavy riders on armoured mounts, with lance, banner and shield: the shock troops of the great wars."},
    {"name": "Grand Champion", "unitType": "Mounted", "movement": 4, "strength": 95, "cost": 400, "requiredTech": "Titan Logic",
     "requiredResource": "Horses", "attackSound": "cavalry",
     "uniques": ["Can move after attacking", "No defensive terrain bonus", "[-33]% Strength <vs cities> <when attacking>", "Never appears as a Barbarian unit"],
     "text": "Champions of the Argent Tournament and their like from every race, the finest riders Azeroth has ever known."},
]


# ====================================================================== magic schools
# (school, tag on the nation, races, flavour uniques, [(unit, recipe colours/props)] x 4 tiers)
TIERS = [  # (tech, obsolete tech, strength, ranged strength, cost, Mana)
    ("Philosophy", "Scholarship", 7, 11, 75, 4),
    ("Scholarship", "Arcane Science", 12, 20, 120, 10),
    ("Arcane Science", "Mana Theory", 24, 32, 200, 12),
    ("Mana Theory", None, 50, 64, 320, 20),
]
# recipe: (robe colour, human hat, hood, prop, glow, orc hat)
SCHOOLS = {
    "Arcane": dict(tag="Arcane Magic", races=["Humans", "Gnomes", "High Elves", "Blood Elves", "Naga", "Nightborne"],
                   uniques=[], top=["[+1] Range"],
                   units=[("Apprentice", ((70, 90, 170), "hair", False, "book", (150, 180, 255), None),
                           "Students of the arcane, fresh from the academies of Dalaran and Silvermoon."),
                          ("Mage", ((60, 70, 160), "hair", False, "light", (140, 170, 255), None),
                           "Mages who hurl fire and frost from afar."),
                          ("Sorcerer", ((72, 52, 118), "hair", True, "staff", (190, 140, 255), "hood"),
                           "Masters of the arcane whose spells can level a battlefield."),
                          ("Magus", ((110, 60, 165), "hair", False, "staff", (200, 160, 255), None),
                           "The greatest wizards of the age, who strike from farther away than any other mage.")]),
    "Fel": dict(tag="Fel Magic", races=["Orcs", "Forsaken", "Goblins"],
                uniques=["[+20]% Strength <when attacking>", "[-10]% Strength <when defending>"], top=[],
                units=[("Fel Initiate", ((80, 40, 40), "hair", True, "book", (120, 255, 90), "hood"),
                        "Students of forbidden magic, drawn to the power of the Burning Legion."),
                       ("Warlock", ((60, 30, 40), "hair", True, "staff", (110, 255, 80), "hood"),
                        "Warlocks who burn their foes with fel fire and shadow, heedless of the cost."),
                       ("Demonologist", ((40, 40, 50), "hair", False, "light", (90, 240, 70), "skullcap"),
                        "Warlocks who bind demons to their will."),
                       ("Grand Warlock", ((90, 20, 30), "crown", False, "staff", (130, 255, 80), "warhelm"),
                        "Masters of the fel, in the tradition of Gul'dan and the Shadow Council.")]),
    "Nature": dict(tag="Nature Magic", races=["Night Elves", "Tauren", "Worgen"],
                   uniques=["All adjacent units heal [5] HP when healing", "Double movement in [Forest]"], top=[],
                   units=[("Druid Initiate", ((80, 110, 60), "hair", False, "staff", (150, 255, 150), None),
                           "Young druids learning the ways of the wild from the Cenarion Circle."),
                          ("Druid of the Talon", ((60, 80, 110), "feather_cap", False, "light", (170, 220, 255), "feathers"),
                           "Druids of the storm and sky, who call down lightning and moonfire."),
                          ("Keeper of the Grove", ((70, 100, 50), "hair", False, "staff", (180, 255, 140), None),
                           "Ancient guardians of the forest who command roots, thorns and storms."),
                          ("Archdruid", ((110, 90, 50), "crown", False, "staff", (220, 255, 160), "feathers"),
                           "The greatest of druids, heirs to Malfurion and Hamuul Runetotem.")]),
    "Elemental": dict(tag="Elemental Magic", races=["Dwarves", "Dark Iron Dwarves", "Kul Tirans", "Pandaren", "Highmountain Tauren"],
                      uniques=["[+25]% Strength <when defending>"], top=[],
                      units=[("Seer", ((110, 80, 50), "hair", False, "censer", (255, 200, 120), None),
                              "Seers who listen to the spirits of earth, fire, water and air."),
                             ("Shaman", ((70, 90, 120), "hair", False, "staff", (140, 200, 255), "feathers"),
                              "Shamans who call lightning, fire and stone to the battle."),
                             ("Far Seer", ((90, 70, 110), "feather_cap", False, "light", (160, 210, 255), "feathers"),
                              "Shamans who see beyond the horizon and command the storm."),
                             ("Stormlord", ((50, 70, 140), "crown", False, "light", (160, 210, 255), "warhelm"),
                              "Masters of the elemental lords, whose word is thunder.")]),
    "Holy": dict(tag="Holy Magic", races=["Draenei"],
                 uniques=["All adjacent units heal [10] HP when healing"], top=[],
                 units=[("Disciple", ((230, 225, 210), "hair", False, "book", (255, 230, 150), None),
                         "Disciples of the Light, taught by the naaru."),
                        ("Oracle", ((215, 215, 235), "hair", True, "light", (255, 240, 180), "hood"),
                         "Oracles who smite the enemy with holy fire and shield their allies."),
                        ("Exarch", ((200, 190, 230), "mitre", False, "staff", (255, 240, 180), None),
                         "High priests of the Light, whose prayers heal whole armies."),
                        ("Hierarch", ((240, 230, 200), "crown", False, "light", (255, 250, 200), None),
                         "The holiest of the Light's servants, in the footsteps of the Prophet Velen.")]),
    "Necromancy": dict(tag="Necromancy", races=["Scourge"],
                       uniques=["[This Unit] heals [10] HP <upon defeating a [Military] unit>"], top=[],
                       units=[("Cult Initiate", ((50, 45, 60), "hair", True, "book", (130, 220, 255), "hood"),
                               "Recruits of the Cult of the Damned, who trade their lives for the Lich King's promise."),
                              ("Necromancer", ((40, 35, 50), "hair", True, "staff", (140, 230, 255), "hood"),
                               "Necromancers who raise the fallen and wither the living."),
                              ("Lich", ((50, 70, 110), "crown", False, "staff", (120, 210, 255), "skullcap"),
                               "Undying sorcerers of ice and death."),
                              ("Archlich", ((30, 40, 80), "crown", False, "light", (150, 230, 255), "warhelm"),
                               "The mightiest liches, peers of Kel'Thuzad.")]),
    "Voodoo": dict(tag="Voodoo", races=["Trolls", "Zandalari Trolls"],
                   uniques=["[-10]% Strength for enemy [Military] units in adjacent [All] tiles"], top=[],
                   units=[("Hexer", ((110, 60, 40), "hair", False, "censer", (180, 255, 120), "feathers"),
                           "Troll hexers who curse their enemies with voodoo."),
                          ("Shadow Hunter", ((60, 40, 70), "feather_cap", False, "staff", (170, 255, 110), "feathers"),
                           "Masters of hexes and healing waves, chosen of the loa."),
                          ("Hexlord", ((90, 50, 80), "crown", False, "light", (200, 255, 120), "skullcap"),
                           "Hexlords who bargain with the loa for dark power."),
                          ("Loa Herald", ((170, 130, 50), "crown", False, "staff", (255, 220, 100), "warhelm"),
                           "Living vessels of the loa, speaking with the voice of the gods.")]),
}
HUMAN_TOP = ("Kirin Tor Magus", "Magus",
             "The magi of the Kirin Tor, the ruling council of Dalaran, who can strike from farther away than any other mage.")
SCHOOL_OF = {u: name for name, sc in SCHOOLS.items() for u, _, _ in sc["units"]}
SCHOOL_RACES = {u: SCHOOLS[sc]["races"] for u, sc in SCHOOL_OF.items()}


def magic_units():
    out = []
    for name, sc in SCHOOLS.items():
        units = sc["units"]
        for k, (unit, _, text) in enumerate(units):
            tech, obs, st, rs, cost, mana = TIERS[k]
            u = {"name": unit, "unitType": "Archery", "movement": 2, "strength": st, "rangedStrength": rs, "cost": cost,
                 "requiredTech": tech, "attackSound": ARCANE_SOUND, "uniqueTo": sc["tag"],
                 "uniques": MAGIC_UNIQUES + sc["uniques"] + ["Costs [%d] [Mana]" % mana] + (sc["top"] if k == 3 else []),
                 "civilopediaText": lore(text, "%s school (%s)." % (name, ", ".join(sc["races"])))}
            if obs:
                u["obsoleteTech"] = obs
            if k < 3:
                u["upgradesTo"] = units[k + 1][0]
            out.append(u)
    top = dict(next(u for u in out if u["name"] == HUMAN_TOP[1]))
    top.update(name=HUMAN_TOP[0], uniqueTo="Humans", replaces=HUMAN_TOP[1], strength=54, rangedStrength=68,
               civilopediaText=lore(HUMAN_TOP[2], "Stronger than a Magus."))
    out.append(top)
    return out


def magic_recipes(hr, or_):
    """{"<unit>-Humans": recipe, "<unit>-Orcs": recipe} for every school unit (other races adapt these)."""
    out = {}
    for name, sc in SCHOOLS.items():
        for unit, (robe, hat, hood, prop, glow, ohat), _ in sc["units"]:
            out[unit + "-Humans"] = (hr(robe_col=robe, robe_layer="base", hat=hat, hood=hood, prop=prop, glow=glow), "foot")
            out[unit + "-Orcs"] = (or_(robe_col=robe, robe_layer="base", hat=ohat, prop=prop, glow=glow), "foot")
    out["Kirin Tor Magus"] = (hr(robe_col=(118, 62, 168), robe_layer="base", hat="hair", hair=(205, 205, 212), beard=(232, 232, 238),
                                 prop="light", glow=(215, 170, 255)), "foot")
    return out


def _rename_text(text):
    holders = {}
    for i, p in enumerate(PROTECT):
        holders["\x00P%d\x00" % i] = p
        text = text.replace(p, "\x00P%d\x00" % i)
    for i, (old, new) in enumerate(RENAME):
        text = re.sub(r"(?<![\w'-])%s(?![\w-])" % re.escape(old), "\x00N%d\x00" % i, text)
    for i, (old, new) in enumerate(RENAME):
        text = text.replace("\x00N%d\x00" % i, new)
    for k, v in holders.items():
        text = text.replace(k, v)
    return text


def apply(files):
    # nothing else may be named like a unit we rename
    olds = {o for o, n in RENAME}
    for key, data in files.items():
        if key == "Units" or not isinstance(data, list):
            continue
        clash = [x.get("name") for x in data if isinstance(x, dict) and x.get("name") in olds]
        assert not clash, (key, clash)
    for key in list(files):
        text = _rename_text(json.dumps(files[key], ensure_ascii=False))
        # the melee "Firearm" unit type no longer carries guns: call it what it is
        text = re.sub(r"(?<!Ranged )\bFirearm\b", "Heavy Infantry", text)
        new = json.loads(text)
        old = files[key]
        # update the objects in place: build.py keeps references to them (e.g. its list of major nations)
        if isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
            for o, n in zip(old, new):
                if isinstance(o, dict):
                    o.clear()
                    o.update(n)
            if not all(isinstance(o, dict) for o in old):
                old[:] = new
        elif isinstance(old, dict):
            old.clear()
            old.update(new)
        else:
            files[key] = new
    units = {u["name"]: u for u in files["Units"]}
    for name, ch in CHANGES.items():
        u = units[name]
        ch = dict(ch)
        for k in ch.pop("drop", []):
            u.pop(k, None)
        u["uniques"] = u.get("uniques", []) + [q for q in ch.pop("add_uniques", []) if q not in u.get("uniques", [])]
        text, text2 = ch.pop("text", None), ch.pop("text2", None)
        u.update(ch)
        if text:
            u["civilopediaText"] = lore(text)
        if text2:   # the second line of a unique unit's entry compares it with the unit it replaces
            first = (u.get("civilopediaText") or [{"text": ""}])[0]
            u["civilopediaText"] = [first] + lore(text2)
    # the Humans' old Mage becomes the Arcane school's Mage (same painted art); Sorcerer etc. are new
    files["Units"] = [u for u in files["Units"] if u["name"] != "Mage"]
    units.pop("Mage")
    for u in magic_units():
        assert u["name"] not in units, u["name"]
        files["Units"].append(u)
        units[u["name"]] = u
    for n in files["Nations"]:
        for name, sc in SCHOOLS.items():
            if n["name"] in sc["races"]:
                n["uniques"] = n.get("uniques", []) + [sc["tag"]]
    for spec in NEW_UNITS:
        spec = dict(spec)
        text = spec.pop("text")
        assert spec["name"] not in units, spec["name"]
        spec["civilopediaText"] = lore(text)
        files["Units"].append(spec)
        units[spec["name"]] = spec
    # a unit goes obsolete when its upgrade arrives; one that can train into two lines never does
    for u in files["Units"]:
        if any(q.startswith("Can upgrade to") for q in u.get("uniques", [])):
            u.pop("obsoleteTech", None)
        elif u.get("upgradesTo") in units and units[u["upgradesTo"]].get("requiredTech") and u.get("obsoleteTech"):
            u["obsoleteTech"] = units[u["upgradesTo"]]["requiredTech"]
    # every upgrade target and replaced unit must exist
    for u in files["Units"]:
        for k in ("upgradesTo", "replaces"):
            assert u.get(k) is None or u[k] in units, (u["name"], k, u.get(k))
    return files


# ====================================================================== art
# sprite stems: old art -> new unit (what the figure carries decides where it goes)
ART_RENAME = [("Ranger", "Hunter"), ("Crossbowman", "Ranger"), ("Musketeer", "Rifleman"), ("Rifleman", "Azerite Sharpshooter"),
              ("Fusilier", "Gladiator"), ("Shock Trooper", "Vanquisher")]
# new units take a copy of an existing sprite as their canvas (the pixel-art steps then redraw it)
ART_COPY = [("Vanguard", "Man-at-Arms"), ("Vanguard", "Royal Guard"), ("Vanguard", "Warbringer"), ("Hunter", "Ranger Captain"),
            ("Hunter", "Ranger-General"), ("Mage", "Kirin Tor Magus"),
            ("Cavalry", "War Rider"), ("Cavalry", "Grand Champion"), ("Pikeman", "Halberdier"), ("Vanguard", "Phalanx")]
UNIT_DIR = "TileSets/AbsoluteUnits/Units/"


def _owned(stem, name):
    """Is this sprite stem one of `name`'s files (the unit itself, a race/era version or a layer)?"""
    base = stem[:-2] if stem.endswith(("-1", "-2")) else stem
    if base == name:
        return True
    if not base.startswith(name + "-"):
        return False
    rest = base[len(name) + 1:]
    return rest not in ("Lord", "General")       # Ranger-Lord and Ranger-General are units of their own


def rename_art(image_dirs, stock_atlas=None):
    n = 0
    folders = [os.path.join(d, UNIT_DIR) for d in image_dirs if os.path.isdir(os.path.join(d, UNIT_DIR))]
    for folder in folders:
        files = sorted(os.listdir(folder))
        moves = []
        for f in files:
            stem = f[:-4]
            for old, new in ART_RENAME:
                if _owned(stem, old):
                    moves.append((f, new + stem[len(old):] + ".png"))
                    break
        for f, dst in moves:                         # two steps, since Ranger -> Hunter and Crossbowman -> Ranger
            os.rename(os.path.join(folder, f), os.path.join(folder, "\x01" + dst))
        for f, dst in moves:
            os.rename(os.path.join(folder, "\x01" + dst), os.path.join(folder, dst))
            n += 1
    for folder in folders:
        files = sorted(os.listdir(folder))
        for src, new in ART_COPY:
            for f in files:
                stem = f[:-4]
                if _owned(stem, src):
                    shutil.copy(os.path.join(folder, f), os.path.join(folder, new + stem[len(src):] + ".png"))
                    n += 1
    # magic schools: a canvas for each school unit in each of its races (the Humans keep their painted Mage)
    for folder in folders:
        for unit, races in SCHOOL_RACES.items():
            for race in races:
                if (unit, race) == ("Mage", "Humans"):
                    continue
                for suf in ("", "-1", "-2"):
                    src = os.path.join(folder, "Hunter-%s%s.png" % (race, suf))
                    if os.path.exists(src):
                        shutil.copy(src, os.path.join(folder, "%s-%s%s.png" % (unit, race, suf)))
                        n += 1
        # the Mechagnome Trooper is the Gnomes' alone now: drop the other races' versions
        for f in os.listdir(folder):
            stem = f[:-4]
            if stem.startswith("Mechagnome Trooper-"):
                rest = stem[len("Mechagnome Trooper"):]
                if rest not in ("-1", "-2") and not rest.startswith(("-Gnomes", "-Age of")):
                    os.remove(os.path.join(folder, f))
    # units whose base sprite only existed in the stock atlas (old Crossbowman, old Rifleman)
    if stock_atlas is not None and folders:
        for old, new in ART_RENAME:
            have = any(os.path.exists(os.path.join(fd, new + ".png")) for fd in folders)
            region = "TileSets/AbsoluteUnits/Units/" + old
            if not have and region in stock_atlas.regions:
                for suf in ("", "-1", "-2"):
                    if region + suf in stock_atlas.regions:
                        stock_atlas.crop(region + suf).save(os.path.join(folders[-1], new + suf + ".png"))
                        n += 1
    return n


ICONS = {"Man-at-Arms": ("helm", "hammer"), "Royal Guard": ("crown", "shield"), "Gladiator": ("swords", "shield"),
         "Vanquisher": ("skull", "sword"), "Hunter": ("bow", "paw"), "Ranger": ("bow", "leaf"), "Ranger Captain": ("bow", "star"),
         "Ranger-General": ("bow", "crown"), "Rifleman": "gun", "Azerite Sharpshooter": ("gun", "crystal"),
         "Kirin Tor Magus": ("orb", "crown"), "Warbringer": ("banner", "axe"),
         "Apprentice": ("book", "sparkle"), "Mage": ("flame", "orb"), "Sorcerer": ("orb", "flame"), "Magus": ("orb", "star"),
         "Fel Initiate": ("flame", "book"), "Warlock": ("flame", "skull"), "Demonologist": ("skull", "chains"), "Grand Warlock": ("flame", "crown"),
         "Druid Initiate": ("leaf", "sparkle"), "Druid of the Talon": ("feather_plume", "bolt"), "Keeper of the Grove": ("tree", "leaf"),
         "Archdruid": ("tree", "crown"), "Seer": ("eye", "totem"), "Shaman": ("totem", "bolt"), "Far Seer": ("eye", "bolt"),
         "Stormlord": ("bolt", "crown"), "Disciple": ("book", "hand_light"), "Oracle": ("hand_light", "eye"), "Exarch": ("naaru", "hand_light"),
         "Hierarch": ("naaru", "crown"), "Cult Initiate": ("skull", "book"), "Necromancer": ("skull", "coffin"), "Lich": ("skull", "crystal"),
         "Archlich": ("skull", "crown"), "Hexer": ("mask", "flask"), "Shadow Hunter": ("mask", "bow"), "Hexlord": ("mask", "skull"),
         "Loa Herald": ("mask", "crown"), "Mountaineer": ("gun", "mountain"),
         "Cavalry": ("horse", "sword"), "War Rider": ("horse", "banner"), "Grand Champion": ("horse", "crown"),
         "Halberdier": ("spear", "helm"), "Phalanx": ("spear", "castle")}
OLD_ICONS = ["Musketeer", "Crossbowman", "Fusilier", "Shock Trooper"]


def write_icons(images_dir):
    import icon_set as I
    for name in OLD_ICONS:
        p = os.path.join(images_dir, "UnitIcons", name + ".png")
        if os.path.exists(p):
            os.remove(p)
    for name, recipe in ICONS.items():
        main, badge = (recipe, None) if isinstance(recipe, str) else recipe
        I.save(I.compose(main, badge), os.path.join(images_dir, "UnitIcons", name + ".png"), (255, 255, 255))
    return len(ICONS)
