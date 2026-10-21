#!/bin/bash
# Full pipeline: build the ruleset, build the maps and scenarios, validate with Unciv, ship packed atlases.
# usage: make_mod.sh <unciv_jar_extract_dir> <out_dir>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
python3 $HERE/build.py "$1" "$2"
$HERE/build_map.sh "$2" | grep -E "MAP OK|RESOURCES|Exception|bad start"
$HERE/build_scenarios.sh "$2"
$HERE/validate.sh "$2" | grep -E "Error|Warning|exit="
V=${WORK:-/tmp/uncivwarcraft}/validate
cp $V/Atlases.json $V/*.atlas $V/*.png "$2"/
