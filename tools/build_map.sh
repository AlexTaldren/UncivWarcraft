#!/bin/bash
# Generate the Azeroth maps into <mod_dir>/maps/.  usage: build_map.sh <mod_dir>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
MOD=$(cd "$1" && pwd)
S=${WORK:-/tmp/uncivwarcraft}
W=$S/maprun; rm -rf $W; mkdir -p $W/mods
cp -r $S/jar/jsons $W/jsons
cp -r "$MOD" $W/mods/UncivWarcraft
mkdir -p "$MOD/maps"
build_one() {  # name width height [region]
  local tag=${1// /_}
  python3 $HERE/azeroth.py $W/$tag.json $W/$tag.txt $2 $3 ${4:+"$4"}
  (cd $W && java -Xmx3g -cp ${UNCIV_JAR:-Unciv.jar}:$HERE/sim BuildAzerothMap $tag.txt "$MOD/maps/$1" $2 $3 2>&1 \
     | grep -v -e JAVA_TOOL -e "\[RulesetCache\]" -e "Loaded .* rulesets" -e MapGenerationRandomness | sed "s/^/[$1] /")
}
build_one "Azeroth" 104 64
build_one "Azeroth Large" 144 88
# Oct 2026: regional maps (azeroth.REGIONS) and Pandaria (azeroth.PANDARIA)
build_one "Kalimdor" 81 91 "Kalimdor"
build_one "Eastern Kingdoms" 72 100 "Eastern Kingdoms"
build_one "Northrend" 81 52 "Northrend"
build_one "Pandaria" 78 57 "Pandaria"
