"""Lore-first combat values for the roster (Nov 2026): what makes a Tauren Brave different from a Troll
Jungle Fighter or a Human Footman. Applied after wc_roster has placed the units.

Each faction has a profile: strength factors per bucket, a cost factor, and abilities for some buckets.
Stronger bodies cost more; swarms are cheap. Only a faction's own units change; shared Alliance and
Horde units keep the plain values. A second, balance pass can adjust these numbers.
"""
import roster_data as RD

MELEE = ("aggressive", "defensive")
LAND = ("aggressive", "defensive", "scout", "ranged", "magic", "mounted", "heavy")
ALL = tuple(RD.BUCKETS)

# faction -> {"str": {bucket: factor}, "cost": factor, "add": [(buckets, unique)], "move": {bucket: movement}}
P = {
    "Humans": {},                                                           # the yardstick
    "Orcs": {"str": {"aggressive": 1.12, "defensive": 1.08, "mounted": 1.08}, "cost": 1.05,
             "add": [(("aggressive",), "[+10]% Strength <when attacking>")]},
    "Tauren": {"str": {"aggressive": 1.2, "defensive": 1.2, "heavy": 1.2, "mounted": 1.25}, "cost": 1.2, "move": {"mounted": 3},
               "add": [(MELEE + ("heavy",), "[+10] HP when healing"), (LAND, "[+15]% Strength <when fighting in [Plains] tiles>")]},
    "Highmountain Tauren": {"str": {"aggressive": 1.2, "defensive": 1.2, "heavy": 1.2, "mounted": 1.25}, "cost": 1.2, "move": {"mounted": 3},
                            "add": [(MELEE + ("heavy",), "[+10] HP when healing"), (LAND, "[+20]% Strength <when fighting in [Hill] tiles>")]},
    "Trolls": {"str": {"aggressive": 0.95, "defensive": 0.95, "ranged": 1.1}, "cost": 0.95,
               "add": [(LAND, "[+10] HP when healing"), (LAND, "Double movement in [Jungle]")]},
    "Zandalari Trolls": {"str": {"aggressive": 1.08, "defensive": 1.08, "ranged": 1.08, "heavy": 1.15}, "cost": 1.12,
                         "add": [(LAND, "[+10] HP when healing"), (LAND, "Double movement in [Jungle]")]},
    "Night Elves": {"str": {"aggressive": 0.95, "ranged": 1.12, "mounted": 1.05}, "cost": 1.05,
                    "add": [(LAND, "Double movement in [Forest]"), (LAND, "[+15]% Strength <when fighting in [Forest] tiles>")]},
    "High Elves": {"str": {"aggressive": 0.9, "defensive": 0.92, "ranged": 1.15, "magic": 1.1}, "cost": 1.05,
                   "add": [(("ranged",), "[+1] Sight")]},
    "Blood Elves": {"str": {"aggressive": 0.95, "defensive": 0.95, "magic": 1.15, "ranged": 1.05}, "cost": 1.05},
    "Nightborne": {"str": {"aggressive": 0.9, "defensive": 0.92, "magic": 1.2}, "cost": 1.05},
    "Dwarves": {"str": {"defensive": 1.1, "ranged": 1.08}, "cost": 1.05,
                "add": [(MELEE, "[+15]% Strength <when defending>"), (LAND, "[+20]% Strength <when fighting in [Hill] tiles>")]},
    "Dark Iron Dwarves": {"str": {"defensive": 1.1, "siege": 1.15, "magic": 1.1}, "cost": 1.05,
                          "add": [(MELEE, "[+15]% Strength <when defending>"), (LAND, "[+20]% Strength <when fighting in [Hill] tiles>")]},
    "Gnomes": {"str": {"aggressive": 0.85, "defensive": 0.88, "siege": 1.15, "heavy": 1.15, "aerial": 1.15, "ranged": 1.05}, "cost": 0.92},
    "Goblins": {"str": {"aggressive": 0.85, "defensive": 0.88, "siege": 1.2, "heavy": 1.1}, "cost": 0.85},
    "Draenei": {"str": {"defensive": 1.1, "heavy": 1.1}, "cost": 1.06},
    "Worgen": {"str": {"aggressive": 1.15, "defensive": 0.95}, "cost": 1.1, "move": {"aggressive": 3},
               "add": [(("aggressive", "scout"), "[+10]% Strength <when attacking>")]},
    "Kul Tirans": {"str": {"naval": 1.2, "aggressive": 1.05, "ranged": 1.05}, "cost": 1.04},
    "Forsaken": {"str": {"aggressive": 0.95, "ranged": 1.05, "magic": 1.05, "heavy": 1.15}, "cost": 0.92},
    "Scourge": {"str": {"aggressive": 0.9, "defensive": 0.92, "heavy": 1.2, "mounted": 1.15}, "cost": 0.78},
    "Pandaren": {"str": {"defensive": 1.15, "aggressive": 1.05}, "cost": 1.06,
                 "add": [(MELEE, "[+10] HP when healing")]},
    "Naga": {"str": {b: 1.05 for b in LAND}, "cost": 1.06,
             "add": [(LAND, "[+20]% Strength <when fighting in [Coast] tiles>")]},
}
FAMILY = [{"Tauren", "Highmountain Tauren"}, {"Trolls", "Zandalari Trolls"}, {"High Elves", "Blood Elves"}, {"Dwarves", "Dark Iron Dwarves"},
          {"Forsaken", "Scourge"}]
# single units: what sets the holy warriors (and a few signatures) apart
UNIT = {
    "Paladin": {"promotions": ["Medic"], "add": ["[+25]% Strength <vs [Undead] units>", "[+10] HP when healing"]},
    "Blood Knight": {"add": ["Heals [15] damage if it kills a unit"]},
    "Vindicator": {"add": ["[+10]% Strength bonus for [Military] units within [1] tiles"]},
    "Death Knight": {"add": ["Heals [15] damage if it kills a unit"]},
    "Sunwalker": {"cost": 0.8, "add": ["[+15]% Strength bonus for [Military] units within [1] tiles"]},
    "Prelate": {"cost": 0.8, "add": ["[+15]% Strength bonus for [Military] units within [1] tiles"]},
    "Mountain Giant": {"str": 1.15, "add": ["[+25]% Strength <vs cities> <when attacking>"]},
    "Blademaster": {"add": ["[+25]% Strength <when attacking>"]},
}
HEAL = {0: 5, 1: 10, 2: 15}                                                 # healer bucket: adjacent units heal faster


def apply(units):
    slots = RD.slots()
    by = {u["name"]: u for u in units}
    n = 0
    for name, (b, t, users) in slots.items():
        u = by.get(name)
        if u is None or u.get("_valued"):
            continue
        prof = None
        if len(users) == 1:
            prof = P.get(users[0])
        elif any(set(users) <= fam for fam in FAMILY):
            prof = {k: v for k, v in P.get(users[0], {}).items() if k != "add"}     # kin share the body, not the homeland
        if prof:
            f = prof.get("str", {}).get(b, 1)
            for k in ("strength", "rangedStrength"):
                if u.get(k):
                    u[k] = max(1, int(round(u[k] * f)))
            if u.get("cost"):
                u["cost"] = int(round(u["cost"] * prof.get("cost", 1) / 5.0)) * 5
            if b in prof.get("move", {}) and t > 0 and u.get("movement"):
                u["movement"] = prof["move"][b]
            for buckets, q in prof.get("add", []):
                if b in buckets and q not in u["uniques"]:
                    u["uniques"].append(q)
            n += 1
        if b == "healer":
            u["uniques"].append("All adjacent units heal [+%d] HP when healing" % HEAL[t])
        x = UNIT.get(name)
        if x:
            for k in ("strength", "rangedStrength"):
                if u.get(k) and x.get("str"):
                    u[k] = int(round(u[k] * x["str"]))
            if x.get("cost") and u.get("cost"):
                u["cost"] = int(round(u["cost"] * x["cost"] / 5.0)) * 5
            u["uniques"] += [q for q in x.get("add", []) if q not in u["uniques"]]
            if x.get("promotions"):
                u["promotions"] = sorted(set(u.get("promotions", [])) | set(x["promotions"]))
    print("lore values: %d faction units tuned" % n)
