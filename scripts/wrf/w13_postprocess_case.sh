#!/usr/bin/env bash
# Wait until every listed experiment of CASE has logged SUCCESS, then run the canonical analysis chain.
# Usage: scripts/wrf/w13_postprocess_case.sh CASE YEAR "EXP1 EXP2 ..."
set -uo pipefail
cd "$(dirname "$0")/../.."
CASE=$1; YEAR=$2; EXPS=$3; PY=.venv/bin/python; L=logs/w13_$CASE.log
for x in $EXPS; do until grep -qx "$x SUCCESS" wrf_runs/$CASE/logs/status.txt 2>/dev/null; do sleep 120; done; done
echo "$(date -u +%FT%TZ) all done: $EXPS" >> $L
nice -n 5 $PY scripts/wrf/w5_analyse_case.py $CASE 24 >> $L 2>&1 &&
[ -f results/wrf/$CASE/validation.json ] || nice -n 5 $PY scripts/wrf/w9_validate_control.py $CASE >> $L 2>&1
$PY scripts/wrf/w10_signal_noise.py $CASE >> $L 2>&1 && $PY scripts/wrf/w12_supply_vs_wrf.py $CASE $YEAR >> $L 2>&1 &&
$PY scripts/wrf/w7_case_report.py $CASE docs/revision/wrf_cases/${CASE}_NUMERIC_QC.md docs/revision/wrf_cases/${CASE}_EXECUTION_REPORT.md >> $L 2>&1 &&
$PY scripts/g6c_identification_report.py >> $L 2>&1
echo "$(date -u +%FT%TZ) POSTPROCESS_EXIT $?" >> $L
