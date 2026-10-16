#!/bin/bash
# Generate the Azeroth map into <mod_dir>/maps/Azeroth.  usage: build_map.sh <mod_dir>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
S=${WORK:-/tmp/uncivwarcraft}
W=$S/maprun; rm -rf $W; mkdir -p $W/mods
cp -r $S/jar/jsons $W/jsons
cp -r "$1" $W/mods/UncivWarcraft
python3 $HERE/azeroth.py $W/azeroth.json $W/tiles.txt
python3 $HERE/map_preview.py $W/azeroth.json $S/azeroth_preview.png
mkdir -p "$1/maps"
cd $W && java -Xmx2g -cp ${UNCIV_JAR:-Unciv.jar}:$HERE/sim BuildAzerothMap tiles.txt "$1/maps/Azeroth" 104 64 2>&1 \
  | grep -v -e JAVA_TOOL -e "\[RulesetCache\]" -e "Loaded .* rulesets"
