"""Gate 3: forward-tag JJA evaporation from offshore wind-farm cells (by owner), all farms, and 5 placebos.

Usage: python scripts/g3_track.py 2019 [2016 ...]. Outputs data/processed/track_<yr>.npz and results/track_budget_<yr>.json
"""
import sys, json, time, pathlib, numpy as np, xarray as xr
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tawe.tracking import Tracker, cfl_substeps
M = np.load("data/processed/grid_masks.npz"); lat, lon = M["lat"], M["lon"]
OWNERS_MIN_CELLS = 2
pathlib.Path("results").mkdir(exist_ok=True)
for yr in map(int, sys.argv[1:]):
    owner = M[f"owner_{yr}"]; allm = owner != ""
    tags, names = [], []
    for o in sorted(set(owner[allm])):
        if (owner == o).sum() >= OWNERS_MIN_CELLS:
            tags.append(owner == o); names.append(f"owner_{o}")
    tags.append(allm); names.append("ALL")
    for k, pm in enumerate(M[f"placebo_{yr}"]):
        tags.append(pm.astype(bool)); names.append(f"placebo_{k}")
    src = np.stack(tags)
    ds = xr.concat([xr.open_dataset(f"data/raw/era5/era5_colbudget_{yr}-{m:02d}.nc").load() for m in (6, 7, 8)], "time")
    Wv = ds.total_column_water_vapour.values; Fu = ds.vertical_integral_of_eastward_water_vapour_flux.values
    Fv = ds.vertical_integral_of_northward_water_vapour_flux.values
    E = np.maximum(-1000.0 * ds.evaporation.values / 3600.0, 0.0); P = np.maximum(1000.0 * ds.total_precipitation.values / 3600.0, 0.0)
    tr = Tracker(lat, lon, src); t0 = time.time(); nsub_tot = 0; Ptot = np.zeros(lat.size * lon.size).reshape(lat.size, lon.size)
    Etot_src = 0.0
    for i in range(1, Wv.shape[0]):
        W = 0.5 * (Wv[i - 1] + Wv[i]); fu = 0.5 * (Fu[i - 1] + Fu[i]); fv = 0.5 * (Fv[i - 1] + Fv[i])
        n = cfl_substeps(W, fu, fv, lat, lon, 3600.0); nsub_tot += n
        for _ in range(n):
            tr.step(W, fu, fv, E[i], P[i], 3600.0 / n)
        Ptot += P[i] * 3600.0
    b = {k: (v.tolist() if hasattr(v, "tolist") else v) for k, v in tr.budget.items()}
    res = tr.closure_residual()
    out = dict(year=yr, tags=names, n_hours=int(Wv.shape[0] - 1), n_substeps=int(nsub_tot), runtime_s=round(time.time() - t0, 1),
               budget_kg=b, storage_end_kg=tr.storage().tolist(), closure_residual_kg=res.tolist(),
               closure_rel=(np.abs(res) / np.asarray(tr.budget["E_src"])).tolist(),
               time_start=str(ds.time.values[1]), time_end=str(ds.time.values[-1]))
    np.savez_compressed(f"data/processed/track_{yr}.npz", P_tag=tr.P_tag_acc.astype("float32"), P_total=Ptot.astype("float32"),
                        names=np.array(names), src=src)
    pathlib.Path(f"results/track_budget_{yr}.json").write_text(json.dumps(out, indent=1))
    print(yr, out["runtime_s"], "s; substeps", nsub_tot, "; max closure_rel", max(out["closure_rel"]), flush=True)
