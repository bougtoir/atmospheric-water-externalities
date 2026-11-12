#!/usr/bin/env bash
# Every 10 min, losslessly compress (w8_compress_run.py, bit-identity verified) any finished WRF experiment directory.
cd "$(dirname "$0")/../.."
while true; do
  for rs in wrf_runs/*/*/rsl.error.0000; do
    d=$(dirname "$rs")
    grep -q "SUCCESS COMPLETE WRF" "$rs" || continue
    pgrep -f "wrf.exe" >/dev/null && [ "$(readlink -f /proc/$(pgrep -f -n wrf.exe)/cwd)" = "$(readlink -f $d)" ] && continue
    nice -n 19 .venv/bin/python scripts/wrf/w8_compress_run.py "$d" >> logs/w8_watch.log 2>&1
  done
  sleep 600
done
