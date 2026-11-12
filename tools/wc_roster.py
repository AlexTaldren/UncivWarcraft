"""Applies the unit roster (roster_data.py) to the rules: twelve buckets, three tiers, one line per faction.

Names and placement only: every unit takes the combat values of the unit that used to fill its slot
(the template below), and a faction unit that already existed keeps its own strength edge and special
abilities on top. Values are tuned in a later pass.

How availability works in Unciv terms:
  * the Humans' line is the generic line (city-states and barbarians use it);
  * a unit only one faction fields is `uniqueTo` it and `replaces` the generic unit of its slot;
  * a unit several factions share is a plain unit made "Unavailable" to everyone else.
All new unit types unlock in tech columns 0-9 (tier I 0-3, tier II 4-6, tier III 7-9).
"""
import copy
import re

import roster_data as RD

# slot -> (template unit, required tech, value overrides)
T = {
    ("aggressive", 0): ("Militia", "Farming", {}), ("aggressive", 1): ("Swordsman", "Iron Forged Swords", {}),
    ("aggressive", 2): ("Halberdier", "Mithril Forged Swords", {}),
    ("defensive", 0): ("Spearman", "Bronze Working", {}), ("defensive", 1): ("Pikeman", "Arathi Law", {}),
    ("defensive", 2): ("Man-at-Arms", "Mithril Forged Swords", {}),
    ("scout", 0): ("Scout", "Farming", {}), ("scout", 1): ("Scout", "Bardic Lore", {"strength": 12, "cost": 75}),
    ("scout", 2): ("Scout", "Inscription", {"strength": 22, "cost": 150}),
    ("ranged", 0): ("Archer", "Archery", {}), ("ranged", 1): ("Ranger", "Scholarship", {}), ("ranged", 2): ("Rifleman", "Blackpowder", {}),
    ("magic", 0): ("Apprentice", "Runic Script", {}), ("magic", 1): ("Mage", "Philosophy", {}), ("magic", 2): ("Sorcerer", "Arcane Science", {}),
    ("mounted", 0): ("Outrider", "Riding", {}), ("mounted", 1): ("Knight", "Animal War Training", {}), ("mounted", 2): ("Cavalry", "War Doctrine", {}),
    ("heavy", 0): ("Spearman", "The Wheel", {"strength": 15, "cost": 85, "unitType": "Heavy Infantry"}),
    ("heavy", 1): ("Vanguard", "Steel Forged Swords", {"strength": 27, "cost": 190, "unitType": "Heavy Infantry", "requiredResource": None}),
    ("heavy", 2): ("Man-at-Arms", "Steamworks", {"strength": 36, "cost": 260}),
    ("siege", 0): ("Catapult", "Mathematics", {}), ("siege", 1): ("Ballista", "Siege Engineering", {}), ("siege", 2): ("Cannon", "Alchemy", {}),
    ("naval", 0): ("Longboat", "Sailing", {}), ("naval", 1): ("War Galley", "Seafaring", {}), ("naval", 2): ("Frigate", "Navigation", {}),
    ("aerial", 1): ("Gyrocopter", "Clockwork", {"strength": 18, "rangedStrength": 18, "cost": 160, "requiredResource": None}),
    ("aerial", 2): ("Gyrocopter", "Steamworks", {"strength": 30, "rangedStrength": 30, "cost": 260, "requiredResource": None}),
    ("healer", 0): ("Cleric", "Herbalism", {"cost": 50}), ("healer", 1): ("Cleric", "Priesthood", {}), ("healer", 2): ("Cleric", "Choral Hymns", {"cost": 120}),
}
# where the old units sat, so references to them (free units, events) can be pointed at the new unit of that slot
OLD = {"Militia": ("aggressive", 0), "Swordsman": ("aggressive", 1), "Vanguard": ("aggressive", 1), "Halberdier": ("aggressive", 2),
       "Gladiator": ("aggressive", 2), "Vanquisher": ("aggressive", 2), "Kul Tiran Marine": ("aggressive", 2), "Warbringer": ("aggressive", 2),
       "Spearman": ("defensive", 0), "Pikeman": ("defensive", 1), "Man-at-Arms": ("defensive", 2), "Royal Guard": ("defensive", 2),
       "Scout": ("scout", 0), "Archer": ("ranged", 0), "Hunter": ("ranged", 0), "Ranger": ("ranged", 1), "Ranger Captain": ("ranged", 2),
       "Rifleman": ("ranged", 2), "Mountaineer": ("ranged", 2), "Mounted Archer": ("mounted", 0), "Outrider": ("mounted", 0),
       "Knight": ("mounted", 1), "Lancer": ("mounted", 1), "Cavalry": ("mounted", 2), "Grand Champion": ("mounted", 2),
       "Catapult": ("siege", 0), "Ballista": ("siege", 1), "Cannon": ("siege", 2), "Mortar Team": ("siege", 2),
       "War Golem": ("heavy", 2), "Siege Engine": ("heavy", 2), "Longboat": ("naval", 0), "War Galley": ("naval", 1), "Brigantine": ("naval", 1),
       "Frigate": ("naval", 2), "Gyrocopter": ("aerial", 1), "Gryphon Rider": ("aerial", 2), "Cleric": ("healer", 1)}
KEEP_TYPES = ("Civilian", "Civilian Water", "Raid Boss")
KEEP_NAMES = ("Felguard", "Infernal")
HUMAN_ONLY_GENERIC = ("Paladin",)          # generic-line units that city-states and barbarians may not field
RUINS = re.compile(r"^May upgrade to \[.*\] through ruins-like effects$")


def _slot_of(old, name):
    seen = set()
    while name and name not in seen:
        if name in OLD:
            return OLD[name]
        seen.add(name)
        name = old.get(name, {}).get("replaces")
    return None


def apply(files):
    old = {u["name"]: u for u in files["Units"]}
    majors = list(RD.ROSTER)
    slots = RD.slots()
    base = {(b, t): RD.line("Humans", b)[t] for b in RD.BUCKETS for t in range(3)}
    tech_of = {k: v[1] for k, v in T.items()}
    new = {}
    for name, (b, t, users) in slots.items():
        tpl_name, tech, over = T[(b, t)]
        u = copy.deepcopy(old[tpl_name])
        for k in ("replaces", "uniqueTo", "upgradesTo", "obsoleteTech"):
            u.pop(k, None)
        u["name"], u["requiredTech"] = name, tech
        for k, v in over.items():
            if v is None:
                u.pop(k, None)
            else:
                u[k] = v
        u["uniques"] = [q for q in u.get("uniques", []) if not RUINS.match(q)]
        prev = old.get(name)
        if prev is not None and prev.get("replaces") in old and prev.get("uniqueTo") in users:
            ref = old[prev["replaces"]]                                    # keep the faction unit's own edge
            for k in ("strength", "rangedStrength"):
                if prev.get(k) and ref.get(k) and u.get(k):
                    u[k] = int(round(u[k] * prev[k] / ref[k]))
            u["uniques"] += [q for q in prev.get("uniques", []) if q not in ref.get("uniques", []) and q not in u["uniques"]]
            if prev.get("promotions"):
                u["promotions"] = sorted(set(u.get("promotions", [])) | set(prev["promotions"]))
        if prev is not None and prev.get("civilopediaText"):
            u["civilopediaText"] = prev["civilopediaText"]
        else:
            who = "the Alliance" if set(users) <= set(RD.SIDE["A"]) and len(users) > 1 else ("the Horde" if set(users) <= set(RD.SIDE["H"]) and len(users) > 1 else users[0])
            u["civilopediaText"] = [{"text": "%s, tier %s. Fielded by %s." % (RD.LABEL[b], "I" * (t + 1), who if len(users) == 1 or who.startswith("the ") else ", ".join(users))}]
        if prev is not None and prev.get("attackSound"):
            u["attackSound"] = prev["attackSound"]
        bname = base[(b, t)]
        if name == bname:
            blocked = []
            for n in majors:
                if n in users:
                    continue
                theirs = RD.line(n, b)[t]
                if theirs is None or len(slots[theirs][2]) > 1:            # nothing of their own replaces it
                    blocked.append(n)
            if name in HUMAN_ONLY_GENERIC:
                blocked += ["City-States", "Barbarians"]
        elif len(users) == 1:
            u["uniqueTo"] = users[0]
            if bname:
                u["replaces"] = bname
            blocked = []
        else:
            blocked = [n for n in majors if n not in users] + ["City-States", "Barbarians"]
        u["uniques"] += ["Unavailable <for [%s] Civilizations>" % n for n in blocked]
        nxt = {n: (RD.line(n, b)[t + 1] if t < 2 else None) for n in users}
        if t < 2:
            u["obsoleteTech"] = tech_of[(b, t + 1)]
            targets = set(nxt.values())
            if len(targets) == 1 and None not in targets:
                u["upgradesTo"] = targets.pop()
            else:
                if name == bname and nxt.get("Humans"):
                    u["upgradesTo"] = nxt["Humans"]
                u["uniques"] += ["Can upgrade to [%s] <for [%s] Civilizations>" % (y, n) for n, y in nxt.items()
                                 if y and y != u.get("upgradesTo")]
        new[name] = u

    kept = []
    for u in files["Units"]:
        n = u["name"]
        if n in new:
            continue
        hero = "Hero" in u.get("unitType", "") or "Hero" in u.get("uniques", [])
        ship_part = any("Spaceship part" in q for q in u.get("uniques", []))
        if not (u.get("unitType") in KEEP_TYPES or hero or ship_part or n in KEEP_NAMES):
            continue
        if u.get("uniqueTo") == "Barbarians" or (u.get("replaces") == "Cleric" and n not in new):
            continue
        kept.append(u)
    names = {u["name"] for u in kept} | set(new)
    for u in kept:
        for k in ("replaces", "upgradesTo"):
            if u.get(k) and u[k] not in names:
                u.pop(k)
        u["uniques"] = [q for q in u.get("uniques", []) if not (RUINS.match(q) and re.search(r"\[(.*?)\]", q).group(1) not in names)]
    files["Units"] = kept + list(new.values())

    # ---- point every reference to a removed or moved unit at the new unit of that slot
    def remap(text, nation):
        def sub(m):
            x = m.group(1)
            if x not in old or (x in names and (x not in slots or nation is None or nation in slots[x][2])):
                return m.group(0)
            s = _slot_of(old, x)
            if s is None:
                return "[\0]"
            for t in range(s[1], -1, -1):
                y = RD.line(nation or "Humans", s[0])[t]
                if y:
                    return "[%s]" % y
            return "[\0]"
        return re.sub(r"\[([^\[\]]+)\]", sub, text)

    def fix(obj, nation=None):
        if isinstance(obj, dict):
            return {k: fix(v, nation) for k, v in obj.items()}
        if isinstance(obj, list):
            out = [fix(v, nation) for v in obj]
            return [v for v in out if not (isinstance(v, str) and "\0" in v)]
        if isinstance(obj, str):
            return remap(obj, nation)
        return obj

    for n in files["Nations"]:
        if "uniques" in n:
            n["uniques"] = fix(n["uniques"], n["name"] if n["name"] in RD.ROSTER else None)
    for key in ("Events", "Buildings", "Policies", "Beliefs", "UnitPromotions", "Techs", "GlobalUniques", "Ruins", "Quests", "TileImprovements",
                "Personalities"):
        if key in files:
            files[key] = fix(files[key])
    for u in files["Units"]:
        u["uniques"] = fix(u.get("uniques", []))
    for era in files.get("Eras", []):                                      # era start units: the generic unit of the same slot
        x = era.get("startingMilitaryUnit")
        if x and x not in names:
            sl = _slot_of(old, x)
            era["startingMilitaryUnit"] = base[sl] if sl and base[sl] else "Militia"
    import wc_values                                                      # lore-first values on top of the slot templates
    wc_values.apply(files["Units"])
    print("roster: %d units in the rules (%d roster, %d kept)" % (len(files["Units"]), len(new), len(kept)))
