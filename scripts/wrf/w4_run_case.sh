#!/usr/bin/env bash
# Run one paired WRF case: WPS (geogrid, ERA5->intermediate, metgrid), real.exe, then CONTROL and WIND wrf.exe.
# Usage: scripts/wrf/w4_run_case.sh CASE START END ERA5_NC [COUNTRIES=ALL] [DX=15000] [NX=141] [NY=111] [CU=1] [EXPS="CONTROL WIND"]
set -euo pipefail
CASE=$1; START=$2; END=$3; ERA5=$4; CTY=${5:-ALL}; DX=${6:-15000}; NX=${7:-141}; NY=${8:-111}; CU=${9:-1}
EXPS=${EXPS:-"CONTROL WIND"}; NP=${NP:-2}
ROOT=$(pwd); WRF=${WRF_DIR:-$HOME/wrf/WRFV4.6.1}; WPS=${WPS_DIR:-$HOME/wrf/WPS-4.6.0}
GEOG=$ROOT/data/raw/wps_geog/WPS_GEOG_LOW_RES; PY=$ROOT/.venv/bin/python
R=$ROOT/wrf_runs/$CASE; mkdir -p $R/wps $R/logs
DT=$(( DX / 250 ))
s=${START/T/_}:00:00; e=${END/T/_}:00:00
fill() { sed -e "s|{start}|$s|; s|{end}|$e|; s|{e_we}|$NX|; s|{e_sn}|$NY|; s|{dx}|$DX|g; s|{geog}|$GEOG|" "$1"; }
cd $R/wps
if [ ! -f geo_em.d01.nc ]; then
  fill $ROOT/wrf_config/namelist.wps.tmpl > namelist.wps
  ln -sf $WPS/geogrid/GEOGRID.TBL.ARW GEOGRID.TBL; mkdir -p geogrid; ln -sf $WPS/geogrid/GEOGRID.TBL.ARW geogrid/GEOGRID.TBL
  $WPS/geogrid.exe > $R/logs/geogrid.log 2>&1
fi
$PY - <<PYE
import json, xarray as xr
g = xr.open_dataset("geo_em.d01.nc"); la, lo = g.XLAT_M.values[0], g.XLONG_M.values[0]
json.dump(dict(lat_min=float(la.min()), lat_max=float(la.max()), lon_min=float(lo.min()), lon_max=float(lo.max())),
          open("$R/domain_bounds.json", "w"))
PYE
if ! ls met_em.d01.* >/dev/null 2>&1; then
  [ -f "ERA5:${START/T/_}" ] || $PY $ROOT/scripts/wrf/w3_era5_to_intermediate.py $ERA5 . > $R/logs/intermediate.log
  mkdir -p metgrid; ln -sf $WPS/metgrid/METGRID.TBL.ARW metgrid/METGRID.TBL
  $WPS/metgrid.exe > $R/logs/metgrid.log 2>&1
fi
read sy sm sd sh <<<$(echo $START | sed 's/[-T]/ /g'); read ey em ed eh <<<$(echo $END | sed 's/[-T]/ /g')
RH=$(( ( $(date -ud "${END/T/ }:00" +%s) - $(date -ud "${START/T/ }:00" +%s) ) / 3600 ))
for X in $EXPS; do
  D=$R/$X; mkdir -p $D; cd $D
  for f in $WRF/run/*; do [ -e "$(basename $f)" ] || ln -s $f .; done
  rm -f namelist.input; ln -sf $R/wps/met_em.d01.* .
  cp $ROOT/wrf_config/tawe_iofields.txt .
  WF=0; [ "$X" != "CONTROL" ] && [ "${X#CTLPERT}" == "$X" ] && WF=1
  fill $ROOT/wrf_config/namelist.input.tmpl | sed -e "s|{run_hours}|$RH|; s|{sy}|$sy|; s|{sm}|$sm|; s|{sd}|$sd|; s|{sh}|$sh|; s|{ey}|$ey|; s|{em}|$em|; s|{ed}|$ed|; s|{eh}|$eh|; s|{dt}|$DT|; s|{cu}|$CU|; s|{windfarm_opt}|$WF|" > namelist.input
  if [ $WF = 1 ]; then
    C=$CTY; [ "$X" != "WIND" ] && C=${X#WIND_}
    cp $R/domain_bounds.json $D/; (cd $ROOT && $PY scripts/wrf/w2_turbines.py $D ${START%T*} $C) > $R/logs/turbines_$X.log
  fi
  if [ ! -f wrfinput_d01 ]; then mpirun -np $NP ./real.exe > $R/logs/real_$X.log 2>&1; cp rsl.error.0000 $R/logs/real_$X.rsl; fi
  if ! grep -q "SUCCESS COMPLETE WRF" rsl.error.0000 2>/dev/null || [ ! -f wrfout_d01_* ]; then
    t0=$(date +%s); mpirun -np $NP ./wrf.exe > $R/logs/wrf_$X.log 2>&1; t1=$(date +%s)
    cp rsl.error.0000 $R/logs/wrf_$X.rsl; echo "$X wallclock_s $((t1-t0))" >> $R/logs/timing.txt
  fi
  grep -q "SUCCESS COMPLETE WRF" rsl.error.0000 && echo "$X SUCCESS" >> $R/logs/status.txt || echo "$X FAIL" >> $R/logs/status.txt
done
