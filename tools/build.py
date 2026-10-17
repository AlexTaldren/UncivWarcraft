"""Build the UncivWarcraft base ruleset from Unciv's Gods & Kings ruleset.

usage: python3 build.py <unciv_jar_extract_dir> <output_mod_dir>
"""
import copy, json, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
import ljson
from atlas import Atlas
import wc_renames as R
import wc_factions as F
import wc_names as NG
import wc_terrain as WT
import wc_lore as LORE
import icons, race_sprites, human_sprites, tiles_art, citycenters, late_units
import race_units as RU, wc_events as WE, wc_text as TX, wc_lore_more as LM, wc_race_names as RN, legion

SRC, OUT = sys.argv[1], sys.argv[2]
GK = os.path.join(SRC, "jsons", "Civ V - Gods & Kings")
J = os.path.join(OUT, "jsons")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(J)

files = {f[:-5]: ljson.load(os.path.join(GK, f)) for f in os.listdir(GK) if f.endswith(".json")}
files.pop("Events", None)  # base-game tutorial tasks; not needed

# ------------------------------------------------------------ 1. drop real-world civ content
files["Nations"] = [n for n in files["Nations"] if n["name"] in ("Barbarians", "Spectator")]
files["Units"] = [u for u in files["Units"] if not u.get("uniqueTo")]
files["Buildings"] = [b for b in files["Buildings"] if not b.get("uniqueTo")]
files["TileImprovements"] = [i for i in files["TileImprovements"] if not i.get("uniqueTo")]
files["UnitNameGroups"] = [g for g in files["UnitNameGroups"] if g["name"] != "Khan"]
files["Personalities"] = []
# promotions that only existed for the removed real-world unique units
DEAD_PROMOS = {"Great Generals I", "Great Generals II", "Quick Study", "Haka War Dance",
               "Slinger Withdraw", "Pictish Courage", "Home Sweet Home"}
files["UnitPromotions"] = [p for p in files["UnitPromotions"]
                           if p["name"] not in DEAD_PROMOS and not (p["name"].endswith("] ability")
                               and p["name"][1:-9] not in {u["name"] for u in files["Units"]})]
files["Religions"] = list(F.RELIGIONS)

# wonder/tech quotes are real-world quotations; drop them on everything we rename
for key in ("Techs",):
    for col in files[key]:
        for t in col["techs"]:
            t.pop("quote", None)
for b in files["Buildings"]:
    if b["name"] in R.ALL:
        b.pop("quote", None)
for t in files["Terrains"]:
    if t["name"] in R.ALL:
        t.pop("civilopediaText", None)

# ------------------------------------------------------------ 2. renames
BR = re.compile(r"\[([^\[\]]+)\]")
TYPE_KEYS = {"unitType", "unitTypes"}

def bracket(m):
    """[X] inside a unique: unit-type names win (in the base rules every such
    bracket is a unit filter), then any other renamed entity."""
    x = m.group(1)
    if x in R.UNIT_TYPES:
        return "[" + R.UNIT_TYPES[x] + "]"
    if x in R.ALL:
        return "[" + R.ALL[x] + "]"
    return m.group(0)

def rn(o, key=None, file=None):
    if isinstance(o, dict):
        return {(R.ALL.get(k, k) if isinstance(k, str) else k): rn(v, k, file) for k, v in o.items()}
    if isinstance(o, list):
        return [rn(v, key, file) for v in o]
    if isinstance(o, str):
        if key in TYPE_KEYS or (file == "UnitTypes" and key == "name"):
            return R.UNIT_TYPES.get(o, o)
        if o in R.ALL:
            return R.ALL[o]
        return BR.sub(bracket, o)
    return o

for name in list(files):
    files[name] = rn(files[name], file=name)

# ------------------------------------------------------------ 2a. engine-required names
# Unciv's nuke code adds a terrain literally named "Fallout" (Nuke.kt). Keep one, with the
# same rules as our Blighted Land, so Mana Bombs work; workers clear it with "Remove Fallout".
_bl = next(t for t in files["Terrains"] if t["name"] == "Blighted Land")
_fo = copy.deepcopy(_bl); _fo["name"] = "Fallout"
_fo["civilopediaText"] = [{"text": "Ground scorched by arcane bombardment. Workers can clear it."}]
files["Terrains"].append(_fo)
_rb = next(i for i in files["TileImprovements"] if i["name"] == "Remove Blighted Land")
_rf = copy.deepcopy(_rb); _rf["name"] = "Remove Fallout"
files["TileImprovements"].append(_rf)

# ------------------------------------------------------------ 2c. Warcraft terrain and landmarks
files["Terrains"] += copy.deepcopy(WT.FEATURES) + copy.deepcopy(WT.WONDERS)
for t in files["Terrains"]:
    if t["name"] in WT.WONDER_TEXT:
        t["civilopediaText"] = [{"text": WT.WONDER_TEXT[t["name"]]}]
for feat, (tech, turns) in WT.CLEANSE.items():
    imp = copy.deepcopy(_rb)
    imp.update({"name": "Remove " + feat, "techRequired": tech, "turnsToBuild": turns})
    files["TileImprovements"].append(imp)

# ------------------------------------------------------------ 2b. text clean-up
# Drop Unciv's legacy unit types that no unit uses (AtomicBomber, WaterSubmarine, ...)
used_types = {u["unitType"] for u in files["Units"]}
files["UnitTypes"] = [t for t in files["UnitTypes"] if t["name"] in used_types]
for p in files["UnitPromotions"]:
    if "unitTypes" in p:
        p["unitTypes"] = [t for t in p["unitTypes"] if t in used_types]

VICTORY_TEXT = {
    "Scientific": ("Build the Titan Ascension Project and assemble the Titan vessel to win!",
                   "You have achieved victory through mastery of the arcane and the mechanical! You have "
                   "unlocked the secrets of the Titans and led your people beyond the skies of Azeroth. "
                   "Your triumph will be remembered as long as the stars burn in the night sky!"),
    "Cultural": ("Complete 5 policy branches and restore the Well of Eternity to win!", None),
    "Diplomatic": ("Build the Grand Council of Azeroth and be voted its leader to win!", None),
}
for v in files["VictoryTypes"]:
    if v["name"] in VICTORY_TEXT:
        header, text = VICTORY_TEXT[v["name"]]
        v["victoryScreenHeader"] = header
        if text:
            v["victoryString"] = text

def fix_text(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "text" and isinstance(v, str):
                o[k] = (v.replace("Apollo Program", "Titan Ascension Project")
                         .replace("spaceship parts", "Titan vessel parts")
                         .replace("Who knows what the future holds?", "What secrets lie beyond the Void?"))
            else:
                fix_text(v)
    elif isinstance(o, list):
        for v in o:
            fix_text(v)
for name in files:
    fix_text(files[name])

# Eras: always start with the Peasant (not the fishing skiff) as worker
for e in files["Eras"]:
    e["startingWorkerUnit"] = "Peasant"

# ------------------------------------------------------------ 3. great people names
for g in files["UnitNameGroups"]:
    if g["name"] in NG.GREAT_PEOPLE:
        g["unitNames"] = NG.GREAT_PEOPLE[g["name"]]

# ------------------------------------------------------------ 4. Human unique content
def apply_overrides(obj, ov):
    ov = copy.deepcopy(ov)
    renames, drop, add = ov.pop("renameUniques", {}), ov.pop("dropUniques", []), ov.pop("addUniques", [])
    for stat, amt in ov.pop("addStats", {}).items():
        obj[stat] = obj.get(stat, 0) + amt
    for k, v in ov.items():
        if v is None: obj.pop(k, None)
        else: obj[k] = v
    uq = obj.get("uniques", [])
    for old, new in renames.items():
        assert old in uq, (obj["name"], old)
        uq = [new if u == old else u for u in uq]
    uq = [u for u in uq if u not in drop] + add
    if uq: obj["uniques"] = uq
    else: obj.pop("uniques", None)
    return obj

units = {u["name"]: u for u in files["Units"]}
for base, ov in F.HUMAN_UNITS:
    files["Units"].append(apply_overrides(copy.deepcopy(units[base]), ov))

bld = {b["name"]: b for b in files["Buildings"]}
for base, ov in F.HUMAN_BUILDINGS:
    files["Buildings"].append(apply_overrides(copy.deepcopy(bld[base]) if base else {}, ov))

# v0.11: two unique units and one unique building for each of the other 13 races
units = {u["name"]: u for u in files["Units"]}
for race, base, ov in RU.UNITS:
    ov = dict(ov, replaces=base, uniqueTo=race)
    files["Units"].append(apply_overrides(copy.deepcopy(units[base]), ov))
bld = {b["name"]: b for b in files["Buildings"]}
for race, base, ov in RU.BUILDINGS:
    ov = dict(ov, replaces=base, uniqueTo=race)
    b = apply_overrides(copy.deepcopy(bld[base]), ov)
    b.pop("quote", None)
    files["Buildings"].append(b)

# Human-only Great Person name lists
for group, names in NG.HUMAN_GROUPS.items():
    files["UnitNameGroups"].append({"name": group, "unitNames": names})

# "Call to Arms": 2 free infantry of the current era when war is declared on the Humans.
# Walk the basic-infantry upgrade line from Militia, using the Humans' own versions.
units = {u["name"]: u for u in files["Units"]}
human_eq = {u["replaces"]: u["name"] for u in files["Units"] if u.get("uniqueTo") == "Humans" and u.get("replaces")}
chain, u = [], "Militia"
while u:
    chain.append(human_eq.get(u, u))
    u = units[u].get("upgradesTo")
CALL_TO_ARMS = []
for i, name in enumerate(chain):
    cond = "<upon being declared war on by [All] Civilizations>"
    if i > 0: cond += " <after discovering [%s]>" % units[name]["requiredTech"]
    if i + 1 < len(chain): cond += " <before discovering [%s]>" % units[chain[i + 1]]["requiredTech"]
    CALL_TO_ARMS.append("[2] free [%s] units appear %s" % (name, cond))
print("call to arms:", chain)

# ------------------------------------------------------------ 5. nations, personalities, city-states
src_pers = {p["name"]: p for p in ljson.load(os.path.join(GK, "Personalities.json"))}
majors = []
for n in F.NATIONS:
    n = dict(n)
    n.pop("_basis")
    p = {"name": n["leaderName"], **rn(copy.deepcopy(F.PERSONALITIES[n["name"]]))}
    if n["name"] == "Humans":
        extra = []
        for x in F.HUMAN_ABILITY_EXTRA:
            extra += CALL_TO_ARMS if x == "{CALL_TO_ARMS}" else [x]
        n["uniques"] = n["uniques"] + extra
        n["uniqueText"] = F.HUMAN_ABILITY_TEXT
    files["Personalities"].append(p)
    majors.append(n)

minors = []
for name, cstype, outer, inner in F.CITY_STATES:
    war, attacked, defeated, intro = TX.CS_DIALOGUE[name]
    minors.append({
        "name": name, "adjective": [name], "cityStateType": cstype,
        "declaringWar": war, "attacked": attacked, "defeated": defeated, "introduction": intro,
        "outerColor": outer, "innerColor": inner, "cities": [name]})

barb = [n for n in files["Nations"] if n["name"] == "Barbarians"]
spec = [n for n in files["Nations"] if n["name"] == "Spectator"]
files["Nations"] = spec + majors + minors + barb

# ------------------------------------------------------------ 5b. Warcraft lore in the civilopedia
def add_lore(obj, text):
    if text and not obj.get("civilopediaText"):
        obj["civilopediaText"] = [{"text": text}]
for u in files["Units"]:
    add_lore(u, LORE.UNITS.get(u["name"]))
for b in files["Buildings"]:
    add_lore(b, LORE.WONDERS.get(b["name"]))
for col in files["Techs"]:
    for t in col["techs"]:
        add_lore(t, LORE.TECHS.get(t["name"]))
missing = [u["name"] for u in files["Units"] if not u.get("civilopediaText")] + \
          [t["name"] for c in files["Techs"] for t in c["techs"] if not t.get("civilopediaText")] + \
          [b["name"] for b in files["Buildings"] if (b.get("isWonder") or b.get("isNationalWonder")) and not b.get("civilopediaText")]
print("lore missing:", missing)

# ------------------------------------------------------------ 5c. v0.10: events, Legion, text, lore
# Burning Legion demons: unbuildable, only spawned by the Legion Incursion event
units = {u["name"]: u for u in files["Units"]}
for name, base, stats in legion.UNITS:
    u = copy.deepcopy(units[base])
    for k in ("upgradesTo", "obsoleteTech", "replaces", "uniqueTo", "promotions", "civilopediaText", "requiredResource"):
        u.pop(k, None)
    u.update(stats)
    u["name"] = name
    u["uniques"] = ["Unbuildable", "Cannot be purchased"]
    u["civilopediaText"] = [{"text": legion.LORE[name]}]
    files["Units"].append(u)

files["Events"] = WE.json_events()
# triggered for major civs only (city-states would otherwise roll events too), hidden in the civilopedia
for n in majors:
    n["uniques"] = n.get("uniques", []) + [t + " <hidden from users>" for t in WE.triggers(n["name"])]

# ------------------------------------------------------------ 5d. v0.12: play styles, heroes, travel, Mana
import wc_playstyles as PS
units = {u["name"]: u for u in files["Units"]}
for base, ov in PS.UNITS:
    u = apply_overrides(copy.deepcopy(units[base]), ov)
    for k in ("upgradesTo", "obsoleteTech", "replaces") if "replaces" not in ov else ():
        u.pop(k, None)
    files["Units"].append(u)
units = {u["name"]: u for u in files["Units"]}
for name, extra in PS.UNIT_EXTRA_UNIQUES.items():
    units[name]["uniques"] = units[name].get("uniques", []) + extra

# heroes: their own unit type and promotion line
files["UnitTypes"].append(dict(PS.HERO_TYPE))
for race, (hname, title, sig, lore) in PS.HEROES.items():
    h = copy.deepcopy(units[PS.HERO_BASE])
    for k in ("upgradesTo", "obsoleteTech", "replaces", "promotions", "civilopediaText"):
        h.pop(k, None)
    h.update({k: v for k, v in PS.HERO_STATS.items() if v is not None})
    h.pop("requiredResource", None)
    h.update(name=hname, unitType="Hero", uniqueTo=race,
             uniques=PS.HERO_COMMON + sig + PS.HERO_SCALING,
             civilopediaText=[{"text": "%s, %s. %s" % (hname, title, lore)},
                              {"text": "A hero of the %s: only one can serve at a time. Inspires nearby units (+15%%), heals on kills, gains strength in later ages and has its own line of hero promotions." % race}])
    files["Units"].append(h)
for i, p in enumerate(PS.HERO_PROMOTIONS):
    p = dict(p, unitTypes=["Hero"], column=30 + (i % 3), row=i // 3)
    base_name = re.sub(r" (I|II|III)$", "", p["name"])
    p["civilopediaText"] = [{"text": PS.HERO_PROMO_LORE[base_name]}]
    files["UnitPromotions"].append(p)
files["UnitPromotions"] += [dict(p) for p in PS.TRAVEL_PROMOTIONS]

# cleansing: only Clerics (and each race's own version) can remove plague and fel
files["Units"].append(copy.deepcopy(PS.CLERIC))
for race, (cname, clore) in PS.CLERICS.items():
    c = copy.deepcopy(PS.CLERIC)
    c.update(name=cname, replaces="Cleric", uniqueTo=race)
    c["uniques"] = [q for q in c["uniques"] if not q.startswith("Unavailable")]
    c["civilopediaText"] = [{"text": clore}, PS.CLERIC["civilopediaText"][1]]
    files["Units"].append(c)
WORKER_FILTER = "Can build [{Land} %s] improvements on tiles" % " ".join("{non-[%s]}" % t for t in PS.CORRUPT_TILES)
for u in files["Units"]:
    if "Can build [Land] improvements on tiles" in u.get("uniques", []):
        u["uniques"] = [WORKER_FILTER if q == "Can build [Land] improvements on tiles" else q for q in u["uniques"]]

# buildings: the Pandaren paths; portals in Mage Towers; Mana
files["Buildings"] += copy.deepcopy(PS.BUILDINGS)
files["TileResources"].append(dict(PS.MANA))
for b in files["Buildings"]:
    if b["name"] == "Mage Tower":
        b["uniques"] = b.get("uniques", []) + [PS.MAGE_TOWER_PORTALS]
    if b["name"] in PS.MANA_SOURCES:
        b["uniques"] = b.get("uniques", []) + ["Provides [%d] [Mana]" % PS.MANA_SOURCES[b["name"]]]
    if b["name"] in PS.MANA_WITH_CRYSTALS:
        b["uniques"] = b.get("uniques", []) + ["Provides [%d] [Mana] <with [Arcane Crystals]>" % PS.MANA_WITH_CRYSTALS[b["name"]]]
    if b["name"] in PS.BUILDING_MANA_COSTS:
        b["uniques"] = b.get("uniques", []) + ["Costs [%d] [Mana]" % PS.BUILDING_MANA_COSTS[b["name"]]]
hero_names = {h[0] for h in PS.HEROES.values()}
for u in files["Units"]:
    cost = PS.MANA_COSTS.get(u["name"]) or (PS.HERO_MANA if u["name"] in hero_names else None)
    if cost:
        u["uniques"] = u.get("uniques", []) + ["Costs [%d] [Mana]" % cost]

# improvements: blight, the Dwarves' Deep Mine, race restrictions
files["TileImprovements"] += copy.deepcopy(PS.IMPROVEMENTS)
imps = {i["name"]: i for i in files["TileImprovements"]}
files["TileImprovements"].append(apply_overrides(copy.deepcopy(imps["Mine"]), PS.DEEP_MINE))
for name, uq in PS.RESTRICT_IMPROVEMENTS:
    imps[name]["uniques"] = imps[name].get("uniques", []) + [uq]
files["Ruins"] += copy.deepcopy(PS.RUINS)

# nations: faction tags, rivalry and play styles
for n in majors:
    tags = PS.TAGS.get(n["name"], [])
    if tags:
        n["uniques"] = [q for q in n["uniques"] if not q.startswith("Comment [Faction:")]
    extra, text = PS.PLAYSTYLE.get(n["name"], ([], None))
    n["uniques"] = tags + [PS.RIVALRY[t] for t in tags if t in PS.RIVALRY] + n["uniques"] + extra
    if n["name"] == "Humans":
        n["uniqueText"] += " Alliance: +10% Strength against the Horde."

# per-race Great Person names: each race's GP takes names from its own list
GP_TAG = re.compile(r"^\[This Unit\] gets a name from the \[(\w+)\] group$")
for u in files["Units"]:
    out = []
    for q in u.get("uniques", []):
        m = GP_TAG.match(q)
        if not m or m.group(1) not in NG.GREAT_PEOPLE:
            out.append(q)
            continue
        kind = m.group(1)
        for race, kinds in RN.RACE_GP.items():
            if kind in kinds:
                out.append("[This Unit] gets a name from the [%s %s] group <for [%s] Civilizations> <hidden from users>" % (race, kind, race))
        out.append(q + " <for [City-States] Civilizations> <hidden from users>")
    if "uniques" in u:
        u["uniques"] = out
for race, kinds in RN.RACE_GP.items():
    for kind, names in kinds.items():
        files["UnitNameGroups"].append({"name": "%s %s" % (race, kind), "unitNames": names})

# ancient ruins and city-state quests in Warcraft terms
for r in files["Ruins"]:
    if r["name"] in TX.RUINS:
        r["notification"] = TX.RUINS[r["name"]]
for q in files["Quests"]:
    if q["name"] in TX.QUESTS:
        q["description"] = TX.QUESTS[q["name"]]

# city-state types (only where the engine doesn't name them) and specialists
def rekey(d, m):
    return {m.get(k, k): v for k, v in d.items()}
for t in files["CityStateTypes"]:
    t["name"] = TX.CS_TYPES.get(t["name"], t["name"])
for n in files["Nations"] + minors:
    if "cityStateType" in n:
        n["cityStateType"] = TX.CS_TYPES.get(n["cityStateType"], n["cityStateType"])
for q in files["Quests"]:
    if "weightForCityStateType" in q:
        q["weightForCityStateType"] = rekey(q["weightForCityStateType"], TX.CS_TYPES)
for sp in files["Specialists"]:
    sp["name"] = TX.SPECIALISTS.get(sp["name"], sp["name"])
SPEC_BR = re.compile(r"\[(%s)\]" % "|".join(TX.SPECIALISTS))
for b in files["Buildings"]:
    if "specialistSlots" in b:
        b["specialistSlots"] = rekey(b["specialistSlots"], TX.SPECIALISTS)
for name in ("Buildings", "Policies", "Beliefs", "Nations", "Techs"):
    def fix(o):
        if isinstance(o, dict):
            if "uniques" in o:
                o["uniques"] = [SPEC_BR.sub(lambda m: "[" + TX.SPECIALISTS[m.group(1)] + "]", q) for q in o["uniques"]]
            for v in o.values(): fix(v)
        elif isinstance(o, list):
            for v in o: fix(v)
    fix(files[name])

# civilopedia lore for everything else
for b in files["Buildings"]:
    add_lore(b, LM.BUILDINGS.get(b["name"]))
for r in files["TileResources"]:
    add_lore(r, LM.RESOURCES.get(r["name"]))
for i in files["TileImprovements"]:
    add_lore(i, LM.IMPROVEMENTS.get(i["name"]))
for b in files["Beliefs"]:
    add_lore(b, LM.BELIEFS.get(b["name"]))
for br in files["Policies"]:
    add_lore(br, LM.BRANCHES.get(br["name"]))
    for p in br["policies"]:
        add_lore(p, LM.POLICIES.get(p["name"]))
PROMO_LVL = re.compile(r" (I|II|III)$")
for p in files["UnitPromotions"]:
    add_lore(p, LM.PROMOTIONS.get(PROMO_LVL.sub("", p["name"])))
missing2 = [x["name"] for k in ("TileResources", "TileImprovements", "Beliefs") for x in files[k] if not x.get("civilopediaText")] + \
           [b["name"] for b in files["Buildings"] if not b.get("civilopediaText")] + \
           [p["name"] for br in files["Policies"] for p in br["policies"] if not p.get("civilopediaText") and not p["name"].endswith("Complete")] + \
           [p["name"] for p in files["UnitPromotions"] if not p.get("civilopediaText")]
print("lore missing (v0.10):", missing2)

files["ModOptions"] = {"isBaseRuleset": True, "uniques": ["Mod preselects map [Azeroth Large]"]}

for name, data in files.items():
    ljson.dump(data, os.path.join(J, name + ".json"))

# ------------------------------------------------------------ 6. tileset layering rules
MODERN_ERAS = ("Industrial era", "Modern era", "Atomic era", "Information era", "Future era")

def rename_leaf(leaf):
    """Rename an image name like "Truffles+Camp-Pillaged" token by token."""
    def one(tok):
        for old, new in R.ALL.items():
            if tok == old or tok.startswith(old + "-"):
                return new + tok[len(old):]
        return tok
    out = "+".join(one(t) for t in leaf.split("+"))
    for old, new in R.ERAS.items():   # era-specific variants, e.g. "Great Artist-Industrial era"
        out = out.replace("-" + old, "-" + new)
    return out

# tileset layering rules for renamed things
TS = os.path.join(SRC, "jsons", "TileSets")
os.makedirs(os.path.join(J, "TileSets"), exist_ok=True)
for f in os.listdir(TS):
    cfg = ljson.load(os.path.join(TS, f))
    extra = {}
    for key, layers in cfg.get("ruleVariants", {}).items():
        toks = key.split("+")
        if any(t in R.ALL for t in toks):
            # layer images are renamed token by token too, so our own art is used
            extra["+".join(R.ALL.get(t, t) for t in toks)] = [rename_leaf(l) for l in layers]
        if "Mine" in toks:      # the Dwarves' Deep Mine looks like a Mine
            extra["+".join("Deep Mine" if t == "Mine" else R.ALL.get(t, t) for t in toks)] = [rename_leaf(l) for l in layers]
    if extra:
        ljson.dump({"ruleVariants": extra}, os.path.join(J, "TileSets", f))

# ------------------------------------------------------------ 7. re-key Unciv's art under the new names
IMG = os.path.join(OUT, "Images")
atlases = [Atlas(os.path.join(SRC, f)) for f in os.listdir(SRC) if f.endswith(".atlas")]
count = 0
for a in atlases:
    for region in a.regions:
        folder, _, leaf = region.rpartition("/")
        if folder not in R.IMAGE_FOLDERS:
            continue
        # map tiles keep their pre-industrial look in every era (no bunkers or glass towers)
        if folder.endswith("/Tiles") and any(e in leaf for e in MODERN_ERAS):
            continue
        newleaf = rename_leaf(leaf)
        if folder.endswith("/Tiles") and (leaf == "Mine" or leaf.startswith("Mine-")):
            path = os.path.join(IMG, folder, "Deep " + leaf + ".png")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            a.crop(region).save(path)
        if newleaf != leaf:
            path = os.path.join(IMG, folder, newleaf + ".png")
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                a.crop(region).save(path)
                count += 1
print("re-keyed images:", count)

# ------------------------------------------------------------ 8. original Warcraft art
icons.write_all(IMG)
import icon_set
print("warcraft icons:", icon_set.write_all(IMG))

# Icons for techs, buildings and policies in their own pack so "game" stays one page.
for _f in ("TechIcons", "BuildingIcons", "PolicyIcons"):
    shutil.move(os.path.join(IMG, _f), os.path.join(OUT, "Images.WarcraftIcons", _f))
# Map art (unit sprites, tiles) goes in its own texture pack so nothing spills into a 2nd page.
shutil.move(os.path.join(IMG, "TileSets"), os.path.join(OUT, "Images.WarcraftMap", "TileSets"))
# Warcraft replacements for the modern-era unit sprites (every civ)
_lu = Atlas(os.path.join(SRC, "AbsoluteUnits.atlas"))
for src in late_units.SOURCES:
    for suf, im in zip(("", "-1", "-2"), late_units.source_layers(_lu, src)):
        path = os.path.join(OUT, "Images.WarcraftMap", late_units.P, R.ALL.get(src, src) + suf + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path)
print("late-era sprites:", len(late_units.SOURCES))
# Race-specific versions of every person unit ("Swordsman-Orcs" ...), in their own texture pack
n = race_sprites.write_all(Atlas(os.path.join(SRC, "AbsoluteUnits.atlas")),
                           os.path.join(OUT, "Images.RaceUnits"), R.ALL, R.ERAS)
print("race sprites:", n)
n = human_sprites.write_all(os.path.join(SRC, "AbsoluteUnits.atlas"), os.path.join(OUT, "Images.WarcraftMap"),
                            os.path.join(OUT, "Images.RaceUnits"), R.ALL, R.ERAS)
print("human sprites:", n)
# Barbarian raiders: murlocs, gnolls and the Defias Brotherhood ("<Unit>-Barbarians")
n = race_sprites.write_barbarians(_lu, os.path.join(OUT, "Images.WarcraftMap"), R.ALL)
print("barbarian sprites:", n)
n = RU.write_all(_lu, os.path.join(OUT, "Images.WarcraftMap"))
print("race unique-unit sprites:", n)
for name, fn in legion.SPRITES.items():
    for suf, im in zip(("", "-1", "-2"), fn()):
        path = os.path.join(OUT, "Images.WarcraftMap", late_units.P, name + suf + ".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path)
# Painted-style Human and Orc sprites (closer to the Warcraft look); drawn last so they win
import wc_style_units
n = wc_style_units.write_all([os.path.join(OUT, "Images.RaceUnits"), os.path.join(OUT, "Images.WarcraftMap")])
print("painted Human/Orc sprites:", n)
# Warcraft terrain features and landmarks (overrides re-keyed real-world wonder art)
n = tiles_art.write_all(Atlas(os.path.join(SRC, "Tilesets.atlas")), os.path.join(OUT, "Images.WarcraftMap"))
print("tile art:", n)
n = citycenters.write_all(os.path.join(OUT, "Images.WarcraftMap"), R.ERAS, [x["name"] for x in F.NATIONS],
                          [c[0] for c in F.CITY_STATES])
print("city centers:", n)
with open(os.path.join(OUT, "Images.RaceUnits", "TexturePacker.settings"), "w") as f:
    # thin padding: these are ~2,000 small pixel-art frames, so the default 8px wastes pages
    f.write(json.dumps({"fast": True, "combineSubdirectories": True, "maxWidth": 2048,
                        "maxHeight": 2048, "paddingX": 2, "paddingY": 2, "duplicatePadding": True,
                        "filterMin": "MipMapLinearLinear", "filterMag": "MipMapLinearLinear"}, indent=1))
shutil.copy(os.path.join(os.path.dirname(__file__), "README.md"), OUT)
# music: royalty-free fantasy tracks played for every faction (Ambient/Peace/Menu moods)
MUSIC = os.path.join(os.path.dirname(__file__), "music")
if not os.path.isdir(MUSIC):          # in the repo, the tracks live at the root, not in tools/
    MUSIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")
if os.path.isdir(MUSIC):
    shutil.copytree(MUSIC, os.path.join(OUT, "music"), dirs_exist_ok=True)
    print("music tracks:", len(os.listdir(MUSIC)))
print("nations:", len(majors), "city-states:", len(minors), "units:", len(files["Units"]),
      "buildings:", len(files["Buildings"]))
