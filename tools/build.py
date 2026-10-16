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
import icons, race_sprites, human_sprites

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
    p = {"name": n["leaderName"], **copy.deepcopy(F.PERSONALITIES[n["name"]])}
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
    minors.append({
        "name": name, "adjective": [name], "cityStateType": cstype,
        "declaringWar": "You leave us no choice. To arms!",
        "attacked": "This insult will not be forgotten.",
        "defeated": "Our walls have fallen...",
        "outerColor": outer, "innerColor": inner, "cities": [name]})

barb = [n for n in files["Nations"] if n["name"] == "Barbarians"]
spec = [n for n in files["Nations"] if n["name"] == "Spectator"]
files["Nations"] = spec + majors + minors + barb

files["ModOptions"] = {"isBaseRuleset": True, "uniques": ["Mod preselects map [Azeroth Large]"]}

for name, data in files.items():
    ljson.dump(data, os.path.join(J, name + ".json"))

# ------------------------------------------------------------ 6. tileset layering rules for renamed things
TS = os.path.join(SRC, "jsons", "TileSets")
os.makedirs(os.path.join(J, "TileSets"), exist_ok=True)
for f in os.listdir(TS):
    cfg = ljson.load(os.path.join(TS, f))
    extra = {}
    for key, layers in cfg.get("ruleVariants", {}).items():
        toks = key.split("+")
        if any(t in R.ALL for t in toks):
            extra["+".join(R.ALL.get(t, t) for t in toks)] = layers
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
        newleaf = leaf
        for old, new in R.ALL.items():
            if leaf == old or leaf.startswith(old + "-"):
                newleaf = new + leaf[len(old):]
                break
        for old, new in R.ERAS.items():   # era-specific variants, e.g. "Great Artist-Industrial era"
            newleaf = newleaf.replace("-" + old, "-" + new)
        if newleaf != leaf:
            path = os.path.join(IMG, folder, newleaf + ".png")
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                a.crop(region).save(path)
                count += 1
print("re-keyed images:", count)

# ------------------------------------------------------------ 8. original Warcraft art
icons.write_all(IMG)

# Map art (unit sprites, tiles) goes in its own texture pack so nothing spills into a 2nd page.
shutil.move(os.path.join(IMG, "TileSets"), os.path.join(OUT, "Images.WarcraftMap", "TileSets"))
# Race-specific versions of every person unit ("Swordsman-Orcs" ...), in their own texture pack
n = race_sprites.write_all(Atlas(os.path.join(SRC, "AbsoluteUnits.atlas")),
                           os.path.join(OUT, "Images.RaceUnits"), R.ALL, R.ERAS)
print("race sprites:", n)
n = human_sprites.write_all(os.path.join(SRC, "AbsoluteUnits.atlas"), os.path.join(OUT, "Images.WarcraftMap"),
                            os.path.join(OUT, "Images.RaceUnits"), R.ALL, R.ERAS)
print("human sprites:", n)
with open(os.path.join(OUT, "Images.RaceUnits", "TexturePacker.settings"), "w") as f:
    # thin padding: these are ~2,000 small pixel-art frames, so the default 8px wastes pages
    f.write(json.dumps({"fast": True, "combineSubdirectories": True, "maxWidth": 2048,
                        "maxHeight": 2048, "paddingX": 2, "paddingY": 2, "duplicatePadding": True,
                        "filterMin": "MipMapLinearLinear", "filterMag": "MipMapLinearLinear"}, indent=1))
shutil.copy(os.path.join(os.path.dirname(__file__), "README.md"), OUT)
print("nations:", len(majors), "city-states:", len(minors), "units:", len(files["Units"]),
      "buildings:", len(files["Buildings"]))
