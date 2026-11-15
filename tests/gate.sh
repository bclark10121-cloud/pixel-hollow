#!/bin/bash
# runs the release gate suites four at a time, then the heavy fuzz suite alone, one line per suite
cd /home/claude/test
SUITES="t7 t8 t9 t10 t11 t12 t13 t14 t16_iso t20_village t21_deep t22_fit t23_quiet t25_progress t27_reach t28_quickwins t29_icons t30_comfort t31_wildlife t32_xmas t33_third $EXTRA"
SOLO="t24_museum t26_fuzz"
run(){ r=$(timeout 600 python3 $1.py 2>&1 | grep -E "^errors|Traceback|AssertionError|Error" | head -2 | cut -c1-240); echo "$1: $r" > /tmp/gate_$1.txt; }
for t in $SUITES; do run $t & while [ $(jobs -r | wc -l) -ge 3 ]; do sleep 1; done; done; wait
for t in $SOLO; do run $t; done
FAIL=0; for t in $SUITES $SOLO; do cat /tmp/gate_$t.txt; grep -q ": errors \[\]$" /tmp/gate_$t.txt || FAIL=1; done
echo "FAIL=$FAIL"
