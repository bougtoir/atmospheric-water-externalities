"""Temporal evolution of the no-wind ensemble spread and of member-to-member distances for one WRF case.

Usage: python scripts/wrf/w18_spread_growth.py CASE [RUNS_DIR=wrf_runs] [SPINUP_H=24]
Reads RUNS_DIR/CASE/<EXP>/wrfout_d01_* (3-hourly: hub-height wind, column vapour W, IVT magnitude) and
wrfsfc_d01_* (hourly: RAINC+RAINNC) for CONTROL, CTLPERT_1..3 and WIND; uses the inner-domain, farm and country
masks of results/wrf/CASE/maps.nc. Writes results/wrf/CASE/spread_growth.csv (field x band x time) and
results/wrf/CASE/country_precip_time.csv (accumulated precipitation since the end of spin-up, kg, per member, country, hour).
Spread = sqrt(band mean of the across-member variance, ddof=1) of the 4 no-wind members. Distances = band RMS of
member differences. Reference sigma_time = sqrt(band mean of the CONTROL temporal variance over the analysis window):
the spread two independent draws from the event's own variability would have (a non-stationary, approximate ceiling).
"""
import glob, sys, itertools
import numpy as np, pandas as pd, xarray as xr
from scipy.spatial import cKDTree

sys.argv += [None] * 3
case = sys.argv[1]; RD = sys.argv[2] or "wrf_runs"; spin = int(sys.argv[3] or 24)
OUT = f"results/wrf/{case}"; G = 9.80665
NOW = ["CONTROL", "CTLPERT_1", "CTLPERT_2", "CTLPERT_3"]; EXPS = NOW + ["WIND"]
mp = xr.open_dataset(f"{OUT}/maps.nc")
inner, farm, ctry = mp.inner.values.astype(bool), mp.farm.values.astype(bool), mp.country.values.astype(str)
d, _ = cKDTree(np.argwhere(farm)).query(np.argwhere(np.ones_like(farm))); dist = (d * 15.0).reshape(farm.shape)
BANDS = {"inner": inner, "farm_0_30km": inner & (dist <= 30), "near_30_150km": inner & (dist > 30) & (dist <= 150),
         "far_gt150km": inner & (dist > 150)}


def tt(ds):
    return pd.to_datetime([x.decode() if isinstance(x, bytes) else b"".join(x).decode() for x in ds.Times.values],
                          format="%Y-%m-%d_%H:%M:%S")


def hist(e):
    T, H, W, V, mf = [], [], [], [], None
    for f in sorted(glob.glob(f"{RD}/{case}/{e}/wrfout_d01_????-??-??_??:??:??")):
        x = xr.open_dataset(f, decode_times=False)
        h = x[["Times", "U", "V", "PH", "PHB", "HGT", "MU", "MUB", "C1H", "C2H", "DNW", "QVAPOR", "MAPFAC_M"]].load(); x.close()
        mf = h.MAPFAC_M.values[0]
        mut = (h.MU + h.MUB).values[:, None]
        dpd = -(h.C1H.values[:, :, None, None] * mut + h.C2H.values[:, :, None, None]) * h.DNW.values[:, :, None, None] / G
        u = 0.5 * (h.U.values[..., 1:] + h.U.values[..., :-1]); v = 0.5 * (h.V.values[..., 1:, :] + h.V.values[..., :-1, :])
        q = h.QVAPOR.values
        W.append((q * dpd).sum(1)); V.append(np.hypot((q * u * dpd).sum(1), (q * v * dpd).sum(1)))
        z = ((h.PH + h.PHB) / G).values; z = 0.5 * (z[:, 1:] + z[:, :-1]) - h.HGT.values[:, None]
        s = np.hypot(u, v); k = np.argmax(z > 100.0, axis=1); k0 = np.clip(k - 1, 0, None)
        take = lambda a, kk: np.take_along_axis(a, kk[:, None], 1)[:, 0]
        z0, z1 = take(z, k0), take(z, k); fr = np.clip((100.0 - z0) / np.maximum(z1 - z0, 1e-6), 0, 1)
        H.append(take(s, k0) * (1 - fr) + take(s, k) * fr); T += list(tt(h))
    return pd.DatetimeIndex(T), dict(hub_wind=np.concatenate(H), W=np.concatenate(W), IVT=np.concatenate(V)), mf


def sfc(e):
    T, P = [], []
    for f in sorted(glob.glob(f"{RD}/{case}/{e}/wrfsfc_d01_????-??-??_??:??:??")):
        x = xr.open_dataset(f, decode_times=False); h = x[["Times", "RAINC", "RAINNC"]].load(); x.close()
        P.append((h.RAINC + h.RAINNC).values); T += list(tt(h))
    return pd.DatetimeIndex(T), np.concatenate(P)


F, Ps = {}, {}
for e in EXPS:
    th, F[e], mf = hist(e); ts, Ps[e] = sfc(e)
area = (15000.0 / mf) ** 2
tspin = ts[0] + pd.Timedelta(hours=spin); i0 = ts.get_loc(tspin)
for e in EXPS:  # 3-hourly precipitation amount (mm) on the history times, and accumulation since spin-up end
    idx = [ts.get_loc(t) for t in th]
    F[e]["P_3h"] = np.stack([Ps[e][i] - Ps[e][max(i - 3, 0)] for i in idx])
    F[e]["P_acc"] = np.stack([Ps[e][i] - Ps[e][i0] if i >= i0 else np.zeros_like(Ps[e][i]) for i in idx])
win = np.asarray(th >= tspin)
rms = lambda a, m: float(np.sqrt(np.mean(a[m] ** 2)))
rows = []
for f in F["CONTROL"]:
    X = {e: F[e][f] for e in EXPS}
    sd_time = np.var(X["CONTROL"][win], axis=0, ddof=1)
    for it, t in enumerate(th):
        var = np.var(np.stack([X[e][it] for e in NOW]), axis=0, ddof=1)
        for b, m in BANDS.items():
            rows.append(dict(case=case, field=f, band=b, time=t, lead_h=(t - ts[0]) / pd.Timedelta(hours=1), in_window=bool(win[it]),
                             spread=float(np.sqrt(var[m].mean())), sigma_time=float(np.sqrt(sd_time[m].mean())),
                             d_ctl_pert=float(np.mean([rms(X[k][it] - X["CONTROL"][it], m) for k in NOW[1:]])),
                             d_pert_pert=float(np.mean([rms(X[a][it] - X[c][it], m) for a, c in itertools.combinations(NOW[1:], 2)])),
                             d_wind_ctl=rms(X["WIND"][it] - X["CONTROL"][it], m),
                             d_wind_pert=float(np.mean([rms(X["WIND"][it] - X[k][it], m) for k in NOW[1:]]))))
pd.DataFrame(rows).to_csv(f"{OUT}/spread_growth.csv", index=False)
cr = []
for iso in sorted(set(ctry[inner]) - {""}):
    m = inner & (ctry == iso)
    for e in EXPS:
        acc = ((Ps[e][i0:] - Ps[e][i0]) * area)[:, m].sum(1)
        cr += [dict(case=case, country=iso, exp=e, time=t, P_acc_kg=float(v)) for t, v in zip(ts[i0:], acc)]
pd.DataFrame(cr).to_csv(f"{OUT}/country_precip_time.csv", index=False)
print(case, "frames", len(th), "sfc", len(ts), "window from", tspin)
