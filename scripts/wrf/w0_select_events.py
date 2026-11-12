"""Prespecified WRF event selection from archived ERA5 column fields (no treatment information used).

Criterion (fixed before any WRF run): non-overlapping 5-day JJA windows ranked by mean eastward vertically
integrated vapour flux across the North Sea gate 3-8E, 52-57N (onshore transport toward the continent),
requiring domain-mean precipitation over 5-20E, 47-56N above the JJA median. Regimes: top windows
(westerly), plus the highest-ranked window with mean northward flux >0 (southerly) and <0 (northerly).
"""
import glob, json
import numpy as np, xarray as xr

rows = []
for f in sorted(glob.glob("data/raw/era5/era5_colbudget_*.nc")):
    ds = xr.open_dataset(f)
    g = ds.sel(latitude=slice(57, 52), longitude=slice(3, 8))
    r = ds.sel(latitude=slice(56, 47), longitude=slice(5, 20))
    fe = g["vertical_integral_of_eastward_water_vapour_flux"].mean(("latitude", "longitude")).resample(time="1D").mean()
    fn = g["vertical_integral_of_northward_water_vapour_flux"].mean(("latitude", "longitude")).resample(time="1D").mean()
    pr = (1000 * r["total_precipitation"]).mean(("latitude", "longitude")).resample(time="1D").sum()
    for t, a, b, c in zip(fe.time.values, fe.values, fn.values, pr.values):
        rows.append((str(t)[:10], float(a), float(b), float(c)))
rows.sort()
d = np.array([r[0] for r in rows]); fe = np.array([r[1] for r in rows]); fn = np.array([r[2] for r in rows]); pr = np.array([r[3] for r in rows])
win = []
for i in range(len(d) - 4):
    if d[i][:4] != d[i + 4][:4]:
        continue
    win.append(dict(start=d[i], end=d[i + 4], fe=fe[i:i + 5].mean(), fn=fn[i:i + 5].mean(), pr=pr[i:i + 5].mean()))
med = np.median([w["pr"] for w in win])
cand = sorted([w for w in win if w["pr"] > med], key=lambda w: -w["fe"])
chosen = []
def free(w):
    return all(abs((np.datetime64(w["start"]) - np.datetime64(c["start"])).astype(int)) >= 10 for c in chosen)
for w in cand:
    if len([c for c in chosen if c["regime"] == "westerly"]) < 3 and free(w):
        chosen.append(dict(w, regime="westerly"))
for name, cond in (("southwesterly", lambda w: w["fn"] > 0), ("northwesterly", lambda w: w["fn"] < 0)):
    for w in cand:
        if cond(w) and free(w) and not any(c["regime"] == name for c in chosen):
            chosen.append(dict(w, regime=name)); break
out = dict(criterion=__doc__.strip(), precip_median_mm_day=med, n_windows=len(win),
           events=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in c.items()} for c in chosen])
json.dump(out, open("results/wrf_event_selection.json", "w"), indent=1)
print(json.dumps(out["events"], indent=1))
