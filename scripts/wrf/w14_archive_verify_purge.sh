#!/usr/bin/env bash
# After a case is complete and compressed: register it in the private archive (w11), push, read back from a fresh
# clone (SHA-256 per object), mark read-back verified, then purge ONLY local model-output files (wrfout/wrfsfc/wrfrst)
# of the read-back-verified datasets. Rerun inputs (wrfinput, wrfbdy, met_em, namelists, tables) stay local.
set -euo pipefail
cd "$(dirname "$0")/../.."
CASE=$1; PY=.venv/bin/python; A=~/archive/tawe-private-research-data; L=logs/w14_$CASE.log
for d in wrf_runs/$CASE/*/; do
  b=$(basename $d); [ "$b" = wps ] || [ "$b" = logs ] && continue
  until [ -f $d/COMPRESSION_LEDGER.csv ]; do sleep 120; done
done
until grep -q POSTPROCESS_EXIT logs/w13_$CASE.log 2>/dev/null; do sleep 120; done
echo "$(date -u +%FT%TZ) archive $CASE" >> $L
scripts/wrf/w11_archive_case.sh $CASE >> $L 2>&1
IDS=$(python3 -c "import csv;print(' '.join(sorted({r['dataset_id'] for r in csv.DictReader(open('$A/DATA_ARCHIVE_MANIFEST.csv')) if r['dataset_id'].startswith('wrf_${CASE}') and 'read-back verified' not in r['archive_status']})))")
(cd $A && git add -A && git commit -qm "WRF $CASE: runs, WPS, logs, analysis (compressed, bit-verified)" && git push -q origin HEAD) >> $L 2>&1
RB=~/readback_$CASE; : > logs/w14_${CASE}_readback.log
for i in $IDS; do  # one dataset at a time to bound the disk footprint of the read-back copy
  rm -rf $RB
  TAWE_ARCHIVE_TOKEN=$(gh auth token) $PY archive/restore_project_data.py --check-only --archive-dir $RB --dataset $i >> logs/w14_${CASE}_readback.log 2>&1
  echo "$i $(tail -1 logs/w14_${CASE}_readback.log)" >> $L
done
rm -rf $RB
$PY archive/mark_readback_verified.py $(date -u +%F) $IDS >> $L 2>&1
(cd $A && git add -A && git commit -qm "Mark $CASE read-back verified" && git push -q origin HEAD) >> $L 2>&1
PURGE_ONLY='^wrf(out|sfc|rst)_d01_' $PY archive/purge_local_verified.py $(echo $IDS | tr ' ' '\n' | grep -v -e _analysis -e _logs -e "^wrf_${CASE}$") >> $L 2>&1
echo "$(date -u +%FT%TZ) W14_DONE $CASE" >> $L
