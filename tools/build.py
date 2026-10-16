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
import icons, sprites

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
SKIP_KEYS = {"unitType", "unitTypes"}

def rn(o, key=None, file=None):
    if isinstance(o, dict):
        return {(R.ALL.get(k, k) if isinstance(k, str) else k): rn(v, k, file) for k, v in o.items()}
    if isinstance(o, list):
        return [rn(v, key, file) for v in o]
    if isinstance(o, str):
        if key in SKIP_KEYS or file == "UnitTypes":
            return o
        if o in R.ALL:
            return R.ALL[o]
        return BR.sub(lambda m: "[" + R.ALL[m.group(1)] + "]"
                      if m.group(1) in R.ALL and m.group(1) not in R.TYPE_COLLISIONS
                      else m.group(0), o)
    return o

for name in list(files):
    files[name] = rn(files[name], file=name)

# Eras: always start with the Peasant (not the fishing skiff) as worker
for e in files["Eras"]:
    e["startingWorkerUnit"] = "Peasant"

# ------------------------------------------------------------ 3. great people names
for g in files["UnitNameGroups"]:
    if g["name"] in NG.GREAT_PEOPLE:
        g["unitNames"] = NG.GREAT_PEOPLE[g["name"]]

# ------------------------------------------------------------ 4. Human unique content
units = {u["name"]: u for u in files["Units"]}
for base, ov in F.HUMAN_UNITS:
    u = copy.deepcopy(units[base])
    ov = dict(ov)
    add = ov.pop("addUniques", [])
    for k, v in ov.items():
        if v is None: u.pop(k, None)
        else: u[k] = v
    if add: u["uniques"] = u.get("uniques", []) + add
    files["Units"].append(u)

bld = {b["name"]: b for b in files["Buildings"]}
for base, ov in F.HUMAN_BUILDINGS:
    b = copy.deepcopy(bld[base])
    ov = dict(ov)
    for stat, amt in ov.pop("addStats", {}).items():
        b[stat] = b.get(stat, 0) + amt
    b.update(ov)
    files["Buildings"].append(b)

# ------------------------------------------------------------ 5. nations, personalities, city-states
src_pers = {p["name"]: p for p in ljson.load(os.path.join(GK, "Personalities.json"))}
majors = []
for n in F.NATIONS:
    n = dict(n)
    basis = n.pop("_basis")
    p = copy.deepcopy(src_pers[basis]); p["name"] = n["leaderName"]; p.pop("civilopediaText", None)
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

files["ModOptions"] = {"isBaseRuleset": True, "uniques": ["Mod preselects map [Azeroth]"]}

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
sprites.write_all(os.path.join(SRC, "AbsoluteUnits.atlas"), IMG)

# Map art (unit sprites, tiles) goes in its own texture pack so nothing spills into a 2nd page.
shutil.move(os.path.join(IMG, "TileSets"), os.path.join(OUT, "Images.WarcraftMap", "TileSets"))
shutil.copy(os.path.join(os.path.dirname(__file__), "README.md"), OUT)
print("nations:", len(majors), "city-states:", len(minors), "units:", len(files["Units"]),
      "buildings:", len(files["Buildings"]))
