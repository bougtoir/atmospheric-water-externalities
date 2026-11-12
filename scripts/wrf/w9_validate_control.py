"""Validate a WRF CONTROL run against ERA5 (the driving reanalysis; not an independent observation) over the
post-spin-up analysis window on the inner region.

Usage: python scripts/wrf/w9_validate_control.py CASE
Writes results/wrf/CASE/validation.json. ERA5 fields are taken from the archived hourly column-budget files.
"""
import glob, json, sys
import numpy as np, pandas as pd, xarray as xr
from scipy.spatial import cKDTree

case = sys.argv[1]; D = f"results/wrf/{case}"
pj = json.load(open(f"{D}/paired.json")); m = xr.open_dataset(f"{D}/maps.nc")
t0, t1 = pd.Timestamp(pj["window"][0]), pd.Timestamp(pj["window"][1])
months = sorted({f"{t:%Y-%m}" for t in pd.date_range(t0, t1, freq="h")})
e5 = xr.concat([xr.open_dataset(f"data/raw/era5/era5_colbudget_{mo}.nc") for mo in months], "time")
e5 = e5.sel(time=slice(t0 + pd.Timedelta(hours=1), t1))
inner = m.inner.values.astype(bool)
lat, lon = m.lat.values, m.lon.values
LA, LO = np.meshgrid(e5.latitude.values, e5.longitude.values, indexing="ij")
_, ii = cKDTree(np.c_[LA.ravel(), LO.ravel()]).query(np.c_[lat[inner], lon[inner]])
pick = lambda a: np.asarray(a).ravel()[ii]
era = dict(P_acc_mm=pick(1000 * e5.total_precipitation.sum("time")),
           E_acc_mm=pick(-1000 * e5.evaporation.sum("time")),
           W=pick(e5.total_column_water_vapour.mean("time")),
           IVTx=pick(e5.vertical_integral_of_eastward_water_vapour_flux.mean("time")),
           IVTy=pick(e5.vertical_integral_of_northward_water_vapour_flux.mean("time")))
out = dict(case=case, window=pj["window"], reference="ERA5 (driving reanalysis)", n_cells=int(inner.sum()), fields={})
for k, ev in era.items():
    wv = m[f"{k}_CONTROL"].values[inner]
    out["fields"][k] = dict(wrf_mean=float(wv.mean()), era5_mean=float(ev.mean()), bias=float((wv - ev).mean()),
                            rel_bias=float((wv - ev).mean() / ev.mean()), rmse=float(np.sqrt(((wv - ev) ** 2).mean())),
                            spatial_r=float(np.corrcoef(wv, ev)[0, 1]))
json.dump(out, open(f"{D}/validation.json", "w"), indent=1)
print(json.dumps(out, indent=1))
