#!/usr/bin/env bash
# Register one finished WRF case in the private archive: WPS intermediates/met_em (INTERMEDIATE), every regular
# (non-symlink) file of each experiment directory (SIMULATION), and results/wrf/<case> (ANALYSIS).
# Run only after compression (w8) has finished for the case.
set -euo pipefail
cd "$(dirname "$0")/../.."
CASE=$1; R=wrf_runs/$CASE; PY=.venv/bin/python
M="source=WRF v4.6.1 ARW (this project) license=project-generated related_scripts=scripts/wrf"
find $R/wps -maxdepth 1 -type f ! -name 'namelist.wps.*' -print0 | xargs -0 $PY archive/archive_to_private.py INTERMEDIATE wrf_$CASE --meta $M processing_status=wps_output
for X in $(ls -d $R/*/ | xargs -n1 basename | grep -v '^wps$'); do
  find $R/$X -maxdepth 1 -type f -print0 | xargs -0 $PY archive/archive_to_private.py SIMULATION wrf_${CASE}_$X --meta $M processing_status=wrf_run
done
find $R/logs $R/domain_bounds.json -type f -print0 | xargs -0 $PY archive/archive_to_private.py SIMULATION wrf_${CASE}_logs --meta $M processing_status=logs
find results/wrf/$CASE -type f -print0 | xargs -0 $PY archive/archive_to_private.py ANALYSIS wrf_${CASE}_analysis --meta $M processing_status=analysis
