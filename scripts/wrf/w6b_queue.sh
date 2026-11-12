#!/usr/bin/env bash
# Resumed WRF programme queue after the CTLPERT_1 THM fix: waits for a running case (PID arg), then
# compresses its WPS output, reruns the pilot noise reference, and runs the remaining prespecified events.
set -uo pipefail
cd "$(dirname "$0")/../.."
[ -n "${1:-}" ] && while kill -0 "$1" 2>/dev/null; do sleep 60; done
F=data/raw/era5_wrf
nice -n 19 .venv/bin/python scripts/wrf/w8_compress_run.py wrf_runs/e2017w/wps >> logs/w8_queue.log 2>&1
EXPS="CTLPERT_1" scripts/wrf/w4_run_case.sh pilot_2020w1 2020-06-30T00 2020-07-06T00 $PWD/$F/era5_wrf_2020-06-30T00_2020-07-06T00.nc
for w in "e2016w 2016-07-07T00 2016-07-13T00" "e2016sw 2016-08-03T00 2016-08-09T00" "e2021nw 2021-08-13T00 2021-08-19T00"; do
  set -- $w; nc=$PWD/$F/era5_wrf_${2}_${3}.nc
  scripts/wrf/w4_run_case.sh $1 $2 $3 $nc
  nice -n 19 .venv/bin/python scripts/wrf/w8_compress_run.py wrf_runs/$1/wps >> logs/w8_queue.log 2>&1
done
echo QUEUE_DONE
