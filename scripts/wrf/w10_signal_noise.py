"""Compare WIND-CONTROL contrasts with a CTLPERT-CONTROL internal-variability reference for one case.

A single perturbed control is one draw of intrinsic variability, not an ensemble; ratios are descriptive only."""
import json, sys
import numpy as np, pandas as pd, xarray as xr

case = sys.argv[1]; noise = sys.argv[2] if len(sys.argv) > 2 else "CTLPERT_1"
OUT = f"results/wrf/{case}"
mp = xr.open_dataset(f"{OUT}/maps.nc")
inner, farm = mp.inner.values.astype(bool), mp.farm.values.astype(bool)
dist = np.full(inner.shape, np.inf)
if farm.any():
    from scipy.spatial import cKDTree
    yx = np.argwhere(farm); d, _ = cKDTree(yx).query(np.argwhere(np.ones_like(farm)))
    dist = (d * 15.0).reshape(farm.shape)
fields = [v[: -len("_CONTROL")] for v in mp.data_vars if v.endswith("_CONTROL")]
bands = {"farm_0_30km": dist <= 30, "near_30_150km": (dist > 30) & (dist <= 150), "far_gt150km": dist > 150}
out = {}
for f in fields:
    if f"{f}_WIND" not in mp or f"{f}_{noise}" not in mp: continue
    s = mp[f"{f}_WIND"].values - mp[f"{f}_CONTROL"].values
    n = mp[f"{f}_{noise}"].values - mp[f"{f}_CONTROL"].values
    r = {}
    for b, m in bands.items():
        m = m & inner
        rs, rn = float(np.sqrt(np.mean(s[m] ** 2))), float(np.sqrt(np.mean(n[m] ** 2)))
        r[b] = dict(n_cells=int(m.sum()), rms_signal=rs, rms_noise=rn, ratio=rs / rn if rn > 0 else None,
                    mean_signal=float(s[m].mean()), mean_noise=float(n[m].mean()))
    out[f] = r
cp = pd.read_csv(f"{OUT}/country_precip.csv")
w = cp[cp.exp == "WIND"].set_index("country"); z = cp[cp.exp == noise].set_index("country")
c = pd.DataFrame(dict(n_cells=w.n_cells, dP_wind_kg=w.dP_kg, dP_noise_kg=z.dP_kg, dP_wind_mm=w.dP_mm, dP_noise_mm=z.dP_mm))
c["abs_ratio"] = c.dP_wind_kg.abs() / c.dP_noise_kg.abs()
c.to_csv(f"{OUT}/country_signal_noise.csv")
json.dump(dict(case=case, noise_reference=noise, note="single-member reference; descriptive ratios only",
               bands_km=[0, 30, 150], fields=out), open(f"{OUT}/signal_noise.json", "w"), indent=1)
print(json.dumps({f: {b: round(v["ratio"], 2) if v["ratio"] else None for b, v in r.items()} for f, r in out.items()}, indent=0))
print(c.round(3).to_string())
