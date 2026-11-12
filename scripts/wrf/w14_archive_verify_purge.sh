#!/usr/bin/env bash
# Usage: w14_archive_verify_purge.sh CASE "EXP ..."
# After all EXPs of a case have succeeded, compression (w8) and postprocessing (w13) have finished: register the case
# in the private archive (w11), push, verify by lean fresh-clone read-back (archive/readback_lean.py, SHA-256 per
# object, bounded disk), mark read-back verified, purge ONLY local model output (wrfout/wrfsfc/wrfrst) and replace
# redundant archive-clone copies by LFS pointers (archive/dedupe_archive_tree.py). Rerun inputs stay local.
set -euo pipefail
cd "$(dirname "$0")/../.."
CASE=$1; EXPS=$2; PY=.venv/bin/python; A=~/archive/tawe-private-research-data; L=logs/w14_$CASE.log
for x in $EXPS; do until grep -qx "$x SUCCESS" wrf_runs/$CASE/logs/status.txt 2>/dev/null; do sleep 120; done; done
for x in $EXPS; do d=wrf_runs/$CASE/$x
  until [ -f $d/COMPRESSION_LEDGER.csv ] && ! ls $d/*.z.tmp >/dev/null 2>&1 && ! pgrep -f "w8_compress_run.py $d" >/dev/null \
        && [ "$(ls $d | grep -c '^wrf\(out\|sfc\)_d01_')" -le "$(($(wc -l < $d/COMPRESSION_LEDGER.csv) - 1))" ]; do sleep 120; done
done
until grep -q POSTPROCESS_EXIT logs/w13_$CASE.log 2>/dev/null; do sleep 120; done
echo "$(date -u +%FT%TZ) archive $CASE" >> $L
scripts/wrf/w11_archive_case.sh $CASE >> $L 2>&1
IDS=$(python3 -c "import csv;print(' '.join(sorted({r['dataset_id'] for r in csv.DictReader(open('$A/DATA_ARCHIVE_MANIFEST.csv')) if r['dataset_id'].startswith('wrf_${CASE}') and 'read-back verified' not in r['archive_status']})))")
(cd $A && git add -A && git commit -qm "WRF $CASE: runs, WPS, logs, analysis (compressed, bit-verified)" && git push -q origin HEAD) >> $L 2>&1
TAWE_ARCHIVE_TOKEN=$(gh auth token) nice $PY archive/readback_lean.py ~/readback_$CASE $IDS >> $L 2>&1
$PY archive/mark_readback_verified.py $(date -u +%F) $IDS >> $L 2>&1
(cd $A && git add DATA_ARCHIVE_MANIFEST.csv && git commit -qm "Mark $CASE read-back verified" && git push -q origin HEAD) >> $L 2>&1
RUNS=$(for x in $EXPS; do echo wrf_${CASE}_$x; done)
PURGE_ONLY='^wrf(out|sfc|rst)_d01_' $PY archive/purge_local_verified.py $RUNS >> $L 2>&1
nice $PY archive/dedupe_archive_tree.py >> $L 2>&1
echo "$(date -u +%FT%TZ) W14_DONE $CASE" >> $L
