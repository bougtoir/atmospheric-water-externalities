#!/usr/bin/env bash
# Sequential WRF programme queue (Gate 3-4). Waits for a running case (PID arg) and then runs, in order:
# pilot noise reference, then CONTROL+WIND for the remaining prespecified events once their forcing exists.
set -uo pipefail
cd "$(dirname "$0")/../.."
[ -n "${1:-}" ] && while kill -0 "$1" 2>/dev/null; do sleep 60; done
F=data/raw/era5_wrf
EXPS="CTLPERT_1" scripts/wrf/w4_run_case.sh pilot_2020w1 2020-06-30T00 2020-07-06T00 $PWD/$F/era5_wrf_2020-06-30T00_2020-07-06T00.nc
for w in "e2017w 2017-06-21T00 2017-06-27T00" "e2016w 2016-07-07T00 2016-07-13T00" "e2016sw 2016-08-03T00 2016-08-09T00" "e2021nw 2021-08-13T00 2021-08-19T00"; do
  set -- $w; nc=$PWD/$F/era5_wrf_${2}_${3}.nc
  while ! grep -q "^era5_wrf_${2}_${3}.nc" $F/LEDGER.csv; do sleep 120; done
  scripts/wrf/w4_run_case.sh $1 $2 $3 $nc
done
echo QUEUE_DONE
