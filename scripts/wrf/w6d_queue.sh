#!/usr/bin/env bash
# Noise-ensemble queue (3 initial-condition perturbation members per event, author-approved): waits for a running
# case (PID arg), then runs CTLPERT members for already-paired events and full CONTROL/WIND/CTLPERT_1-3 for the
# remaining events. Before each case it waits until >= MIN_FREE_GB is free (local copies are only removed after
# verified private-archive read-back).
set -uo pipefail
cd "$(dirname "$0")/../.."
[ -n "${1:-}" ] && while kill -0 "$1" 2>/dev/null; do sleep 60; done
F=data/raw/era5_wrf; MIN_FREE_GB=${MIN_FREE_GB:-14}
guard() { while [ $(df --output=avail -BG / | tail -1 | tr -dc 0-9) -lt $MIN_FREE_GB ]; do echo "$(date -u +%FT%TZ) waiting for disk ($1)" >> logs/w6d_queue.log; sleep 300; done; }
run() {  # CASE START END EXPS
  guard $1; echo "$(date -u +%FT%TZ) start $1 [$4]" >> logs/w6d_queue.log
  EXPS="$4" scripts/wrf/w4_run_case.sh $1 $2 $3 $PWD/$F/era5_wrf_${2}_${3}.nc
  nice -n 19 .venv/bin/python scripts/wrf/w8_compress_run.py wrf_runs/$1/wps >> logs/w8_queue.log 2>&1
  echo "$(date -u +%FT%TZ) done $1 [$4]" >> logs/w6d_queue.log
}
run pilot_2020w1 2020-06-30T00 2020-07-06T00 "CTLPERT_3"
run e2016sw 2016-08-03T00 2016-08-09T00 "CONTROL WIND CTLPERT_1 CTLPERT_2 CTLPERT_3"
run e2021nw 2021-08-13T00 2021-08-19T00 "CONTROL WIND CTLPERT_1 CTLPERT_2 CTLPERT_3"
echo QUEUE_DONE >> logs/w6d_queue.log
