"""Compare WIND-CONTROL contrasts with the internal variability of the unperturbed-fleet ensemble for one case.

The no-wind ensemble is {CONTROL, CTLPERT_1..N} (identical except for initial-condition perturbations of 0.01 K).
Field level: RMS(WIND-CONTROL) / mean over members of RMS(CTLPERT_k-CONTROL), by distance from the nearest farm.
Country level: WIND precipitation is compared with the no-wind ensemble mean and SD; a contrast is flagged as
outside internal variability when |WIND - mean| > t(0.975, n-1) * SD * sqrt(1 + 1/n) (prediction interval).
With n <= 4 the test has low power; flags are descriptive and model-conditional."""
import json, re, sys
import numpy as np, pandas as pd, xarray as xr
from scipy import stats

case = sys.argv[1]
OUT = f"results/wrf/{case}"
mp = xr.open_dataset(f"{OUT}/maps.nc")
members = sorted({m.group(1) for v in mp.data_vars if (m := re.match(r".*_(CTLPERT_\d+)$", v))})
if not members: sys.exit(f"{case}: no CTLPERT members in maps.nc")
inner, farm = mp.inner.values.astype(bool), mp.farm.values.astype(bool)
dist = np.full(inner.shape, np.inf)
if farm.any():
    from scipy.spatial import cKDTree
    d, _ = cKDTree(np.argwhere(farm)).query(np.argwhere(np.ones_like(farm)))
    dist = (d * 15.0).reshape(farm.shape)
fields = [v[: -len("_CONTROL")] for v in mp.data_vars if v.endswith("_CONTROL")]
bands = {"farm_0_30km": dist <= 30, "near_30_150km": (dist > 30) & (dist <= 150), "far_gt150km": dist > 150}
rms = lambda a, m: float(np.sqrt(np.mean(a[m] ** 2)))
out = {}
for f in fields:
    if f"{f}_WIND" not in mp: continue
    s = mp[f"{f}_WIND"].values - mp[f"{f}_CONTROL"].values
    ns = [mp[f"{f}_{k}"].values - mp[f"{f}_CONTROL"].values for k in members if f"{f}_{k}" in mp]
    r = {}
    for b, m in bands.items():
        m = m & inner
        rs, rn = rms(s, m), float(np.mean([rms(n, m) for n in ns]))
        r[b] = dict(n_cells=int(m.sum()), rms_signal=rs, rms_noise=rn, ratio=rs / rn if rn > 0 else None,
                    mean_signal=float(s[m].mean()), mean_noise=float(np.mean([n[m].mean() for n in ns])))
    out[f] = r
cp = pd.read_csv(f"{OUT}/country_precip.csv")
P = {e: (g.set_index("country").P_control_kg + g.set_index("country").dP_kg) for e, g in cp.groupby("exp")}
ctl = cp[cp.exp == cp.exp.iloc[0]].set_index("country").P_control_kg
ens = pd.DataFrame({"CONTROL": ctl, **{k: P[k] for k in members if k in P}})
n = ens.shape[1]
c = pd.DataFrame(dict(n_cells=cp[cp.exp == "WIND"].set_index("country").n_cells,
                      dP_wind_kg=P["WIND"] - ctl, ens_mean_minus_control_kg=ens.mean(axis=1) - ctl,
                      ens_sd_kg=ens.std(axis=1, ddof=1)))
c["wind_minus_ens_mean_kg"] = P["WIND"] - ens.mean(axis=1)
c["pi_halfwidth_kg"] = stats.t.ppf(0.975, n - 1) * c.ens_sd_kg * np.sqrt(1 + 1 / n)
c["outside_internal_variability"] = c.wind_minus_ens_mean_kg.abs() > c.pi_halfwidth_kg
c["z"] = c.wind_minus_ens_mean_kg / c.ens_sd_kg
c.to_csv(f"{OUT}/country_signal_noise.csv")
json.dump(dict(case=case, noise_members=members, n_no_wind_ensemble=n,
               note="no-wind ensemble = CONTROL + CTLPERT members; descriptive, model-conditional",
               n_countries=int(len(c)), n_outside_internal_variability=int(c.outside_internal_variability.sum()),
               bands_km=[0, 30, 150], fields=out), open(f"{OUT}/signal_noise.json", "w"), indent=1)
print(json.dumps({f: {b: round(v["ratio"], 2) if v["ratio"] else None for b, v in r.items()} for f, r in out.items()}))
print(c.round(3).to_string())
