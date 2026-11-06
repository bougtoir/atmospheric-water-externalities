#!/usr/bin/env bash
# Register one finished WRF case in the private archive: WPS intermediates/met_em (INTERMEDIATE), every regular
# (non-symlink) file of each experiment directory (SIMULATION), and results/wrf/<case> (ANALYSIS, unless
# SKIP_ANALYSIS is set). Run only after compression (w8) has finished for the case.
set -euo pipefail
cd "$(dirname "$0")/../.."
CASE=$1; R=wrf_runs/$CASE; PY=.venv/bin/python
M=("source=WRF v4.6.1 ARW (this project)" "license=project-generated" "related_scripts=scripts/wrf")
reg() {  # CATEGORY DATASET_ID STATUS < NUL-separated paths
  mapfile -d '' P; [ ${#P[@]} -gt 0 ] || return 0
  $PY archive/archive_to_private.py "$1" "$2" "${P[@]}" --meta "${M[@]}" "processing_status=$3"
}
find $R/wps -maxdepth 1 -type f -print0 | reg INTERMEDIATE wrf_$CASE wps_output
for X in $(ls -d $R/*/ | xargs -n1 basename | grep -v -e '^wps$' -e '^logs$'); do
  find $R/$X -maxdepth 1 -type f -print0 | reg SIMULATION wrf_${CASE}_$X wrf_run
done
find $R/logs $R/domain_bounds.json -type f -print0 | reg SIMULATION wrf_${CASE}_logs logs
[ -n "${SKIP_ANALYSIS:-}" ] || find results/wrf/$CASE -type f -print0 | reg ANALYSIS wrf_${CASE}_analysis analysis
