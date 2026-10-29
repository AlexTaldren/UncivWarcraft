#!/bin/bash
# Build the scenarios (saved games) into <mod_dir>/scenarios/. Needs the maps built first.
# usage: build_scenarios.sh <mod_dir>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
MOD=$(cd "$1" && pwd)
S=${WORK:-/tmp/uncivwarcraft}
W=$S/scenariorun; rm -rf $W; mkdir -p $W/mods
cp -r $S/jar/jsons $W/jsons
cp -r "$MOD" $W/mods/UncivWarcraft
rm -rf "$MOD/scenarios"
(cd $W && timeout 3000 java -Xmx3g -cp ${UNCIV_JAR:-Unciv.jar}:$HERE/sim BuildScenario "$MOD/scenarios" 2>&1 | grep -E "SCENARIO|Exception")
(cd $W && rm -rf mods/UncivWarcraft/scenarios && cp -r "$MOD/scenarios" mods/UncivWarcraft/ && timeout 5400 java -Xmx3g -cp ${UNCIV_JAR:-Unciv.jar}:$HERE/sim ScenarioCheck \
   "$MOD/scenarios/The Third War" "$MOD/scenarios/The Cataclysm" "$MOD/scenarios/Battle for Azeroth" \
   "$MOD/scenarios/Alliance versus Horde" "$MOD/scenarios/The Legion Invasion" "$MOD/scenarios/Mists of Pandaria" \
   "$MOD/scenarios/Wrath of the Lich King" 10 2>&1 | grep -E "PLAYED|Exception")
