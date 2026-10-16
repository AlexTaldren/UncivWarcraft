#!/bin/bash
# Run Unciv's mod validator on a copy of the mod (it writes packed atlases into the folder).
set -e
S=${WORK:-/tmp/uncivwarcraft}/validate
rm -rf $S && mkdir -p $S && cp -r "$1"/. $S/
cd $S && timeout 600 java -jar ${UNCIV_JAR:-Unciv.jar} mod-ci 2>&1 | grep -v -e JAVA_TOOL -e "used by several ruleset entries" > report.txt; echo "exit=${PIPESTATUS[0]}" >> report.txt
cat report.txt
