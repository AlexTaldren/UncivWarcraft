#!/bin/bash
# usage: sim.sh <mod_dir> <turns> <comma-separated nations> [seed] [map name inside mod's maps/]
HERE=$(cd "$(dirname "$0")" && pwd)
S=${WORK:-/tmp/uncivwarcraft}
W=$S/simrun; rm -rf $W; mkdir -p $W/mods
cp -r $S/jar/jsons $W/jsons
cp -r "$1" $W/mods/UncivWarcraft
MAP=""; [ -n "$5" ] && MAP="$W/mods/UncivWarcraft/maps/$5"
cd $W && timeout ${SIM_TIMEOUT:-3000} java -Xmx3g -cp ${UNCIV_JAR:-Unciv.jar}:$HERE/sim WarcraftSim "$2" "$3" "${4:-1}" ${MAP:+"$MAP"} 2>&1 | grep -v -e JAVA_TOOL -e "^\s*at kotlin" -e MapPathing
