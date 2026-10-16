# UncivWarcraft build tools

The mod is generated from Unciv's own Gods & Kings ruleset, so it stays compatible with new Unciv versions: re-run the build against a newer Unciv.jar.

## Files
- `wc_renames.py` — every Warcraft rename (eras, techs, units, buildings, wonders, resources, natural wonders).
- `race_units.py` — the unique units and buildings of the 13 non-Human races, their sprites (race sprite + props) and icons.
- `wc_factions.py` — the races, leaders, abilities, city lists, city-states, religions, and the Human unique units/building.
- `wc_names.py` — generic Great Person names (city-states); `wc_race_names.py` — each race's own Great Person names.
- `wc_events.py` — the Warcraft random events and their triggers; `legion.py` — the Burning Legion's Felguard and Infernal (units and sprites).
- `wc_text.py` — ruins rewards, city-state quests, city-state type and specialist names; `wc_lore_more.py` — civilopedia lore for buildings, resources, improvements, beliefs, policies and promotions.
- `icons.py`, `sprites.py` — the original icons and map sprites.
- `wc_terrain.py`, `tiles_art.py` — the Warcraft terrain features and landmarks, and their tile art (HexaRealm and FantasyHex).
- `late_units.py` — Warcraft replacements for the modern-era unit sprites.
- `icon_set.py` — the Warcraft icon set (glyph library + per-item recipes).
- `wc_lore.py` — civilopedia lore for wonders, techs and units.
- `race_sprites.py` also draws the barbarians (murlocs, gnolls, Defias) and `tiles_art.py` their camp.
- `citycenters.py` — per-race city-center tiles in three growth stages.
- `map_tiles_preview.py` — renders part of the Azeroth map with the real tile art.
- `human_sprites.py` — the Humans' unique-unit sprites and blue-and-gold variants.
- `race_sprites.py`, `mounts.py` — race versions of every person unit, and each race's mounts (wolves, rams, mechanostriders, nightsabers, kodos, raptors, hawkstriders, elekks, dragon turtles, trikes, skeletal and Gilnean horses, white steeds).
- `build.py` — assembles everything into the mod folder.
- `azeroth.py` — the Azeroth map: coastlines, zones and their terrain, mountain ranges, lakes, natural wonders, capitals and city-states. `map_preview.py` renders it.
- `sim/BuildAzerothMap.java` + `build_map.sh` — turns that layout into a real Unciv map file using Unciv's own classes (coasts, rivers, resources, ruins).
- `validate.sh` — runs Unciv's built-in mod checker (`java -jar Unciv.jar mod-ci`).
- `sim/WarcraftSim.java` + `sim.sh` — plays a full all-AI game with the mod to catch runtime crashes.

- `README.md` — source of the repository/mod README (copied in by `build.py`).
- `preview_image.py` — renders `preview.jpg`, the picture shown in Unciv's mod browser.
- `publish.py` — copies a fresh build into the repository root, keeping `.git`, `tools/` and `LICENSE`.

## Usage
```
export UNCIV_JAR=/path/to/Unciv.jar WORK=/tmp/uncivwarcraft
mkdir -p $WORK/jar && cd $WORK/jar && unzip -q $UNCIV_JAR 'jsons/*' '*.atlas' '*.png'
./make_mod.sh $WORK/jar ./out/UncivWarcraft
javac -cp $UNCIV_JAR sim/WarcraftSim.java
javac -cp $UNCIV_JAR sim/BuildAzerothMap.java   # before make_mod.sh
./sim.sh ./out/UncivWarcraft 300 "Humans,Orcs,Night Elves,Dwarves" 1 Azeroth
```
Requires Python 3 with Pillow and numpy, and a JDK.

To update the repository after changes:
```
./make_mod.sh $WORK/jar ./out/UncivWarcraft
python3 publish.py ./out/UncivWarcraft <path to repo clone>
```
