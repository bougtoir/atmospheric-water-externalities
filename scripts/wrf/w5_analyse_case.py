"""Numeric QC and paired WIND-CONTROL diagnostics for one WRF case.

Usage: python scripts/wrf/w5_analyse_case.py CASE [SPINUP_H=24]
Reads wrf_runs/CASE/<EXP>/wrfout_d01_* (3-hourly) and wrfsfc_d01_* (hourly). Writes
results/wrf/CASE/{qc.json, paired.json, country_precip.csv, maps.nc}. All numbers come from the files.
Diagnostics are model-conditional contrasts within this WRF configuration, not observed effects.
"""
import glob, io, json, os, re, sys, zipfile
import numpy as np, pandas as pd, xarray as xr, shapefile, shapely
from shapely.geometry import shape

G = 9.80665
case = sys.argv[1]; spin = int(sys.argv[2]) if len(sys.argv) > 2 else 24
R = f"wrf_runs/{case}"; OUT = f"results/wrf/{case}"; os.makedirs(OUT, exist_ok=True)
exps = sorted(d for d in os.listdir(R) if os.path.isdir(f"{R}/{d}") and glob.glob(f"{R}/{d}/wrfout_d01_*"))


def open_set(e, pat):
    fs = sorted(glob.glob(f"{R}/{e}/{pat}"))
    ds = xr.concat([xr.open_dataset(f, decode_times=False) for f in fs], "Time", data_vars="minimal", coords="minimal", compat="override")
    t = pd.to_datetime([x.decode() if isinstance(x, bytes) else b"".join(x).decode() for x in ds.Times.values], format="%Y-%m-%d_%H:%M:%S")
    return ds.assign_coords(Time=t)


def column(ds):
    """Dry-air layer mass (kg m-2), vapour/condensate columns, vertically integrated vapour flux."""
    mut = ds.MU + ds.MUB
    dpd = -(ds.C1H * mut + ds.C2H) * ds.DNW / G            # kg m-2 per layer, positive
    q = ds.QVAPOR
    cond = sum(ds[v] for v in ("QCLOUD", "QRAIN", "QICE", "QSNOW", "QGRAUP") if v in ds)
    u = 0.5 * (ds.U.values[..., 1:] + ds.U.values[..., :-1])
    v = 0.5 * (ds.V.values[..., 1:, :] + ds.V.values[..., :-1, :])
    w = (q * dpd).sum("bottom_top").values
    c = (cond * dpd).sum("bottom_top").values
    qx = (q.values * u * dpd.values).sum(1); qy = (q.values * v * dpd.values).sum(1)
    return w, c, qx, qy


def hub_wind(ds, z_hub=100.0):
    z = ((ds.PH + ds.PHB) / G).values; z = 0.5 * (z[:, 1:] + z[:, :-1]) - ds.HGT.values[:, None]
    u = 0.5 * (ds.U.values[..., 1:] + ds.U.values[..., :-1]); v = 0.5 * (ds.V.values[..., 1:, :] + ds.V.values[..., :-1, :])
    s = np.hypot(u, v); k = np.argmax(z > z_hub, axis=1)
    k0 = np.clip(k - 1, 0, None)
    take = lambda a, kk: np.take_along_axis(a, kk[:, None], 1)[:, 0]
    z0, z1 = take(z, k0), take(z, k); f = np.clip((z_hub - z0) / np.maximum(z1 - z0, 1e-6), 0, 1)
    return take(s, k0) * (1 - f) + take(s, k) * f


def countries(lat, lon):
    z = zipfile.ZipFile("data/raw/boundaries/ne_50m_admin_0_countries.zip")
    nm = lambda e: next(n for n in z.namelist() if n.endswith(e))
    r = shapefile.Reader(shp=io.BytesIO(z.read(nm(".shp"))), dbf=io.BytesIO(z.read(nm(".dbf"))), shx=io.BytesIO(z.read(nm(".shx"))))
    fields = [f[0] for f in r.fields[1:]]; lab = np.full(lat.shape, "", dtype=object)
    for sr in r.iterShapeRecords():
        a = dict(zip(fields, sr.record)); iso = a["ISO_A2_EH"] if a.get("ISO_A2_EH", "-99") not in ("-99", "") else a["ADM0_A3"]
        geom = shape(sr.shape.__geo_interface__); x0, y0, x1, y1 = geom.bounds
        if x1 < lon.min() or x0 > lon.max() or y1 < lat.min() or y0 > lat.max(): continue
        m = shapely.contains_xy(geom, lon, lat); lab[m & (lab == "")] = iso
    return lab


qc, data = {}, {}
for e in exps:
    rsl = open(f"{R}/{e}/rsl.error.0000", errors="ignore").read()
    h, s = open_set(e, "wrfout_d01_*"), open_set(e, "wrfsfc_d01_*")
    w, c, qx, qy = column(h)
    exp_frames = int((h.Time.values[-1] - h.Time.values[0]) / np.timedelta64(3, "h")) + 1
    dt3 = np.diff(h.Time.values) / np.timedelta64(1, "h")
    pr = (s.RAINC + s.RAINNC).values
    num = dict(success="SUCCESS COMPLETE WRF" in rsl, cfl_messages=len(re.findall(r"cfl", rsl, re.I)),
               history_frames=int(h.sizes["Time"]), history_frames_expected=exp_frames,
               history_interval_h_unique=sorted(set(dt3.round(3).tolist())), sfc_frames=int(s.sizes["Time"]),
               nonfinite_qvapor=int((~np.isfinite(h.QVAPOR.values)).sum()), negative_qvapor=int((h.QVAPOR.values < 0).sum()),
               min_qvapor=float(h.QVAPOR.min()), max_abs_w_ms=float(abs(h.W).max()) if "W" in h else None,
               precip_monotone=bool((np.diff(pr, axis=0) >= -1e-3).all()), max_precip_mm=float(pr[-1].max()),
               max_u_ms=float(abs(h.U).max()), t2_range_K=[float(s.T2.min()), float(s.T2.max())])
    # boundary discontinuity: accumulated precip in the 5-cell relaxation zone vs. the next 5 cells inward
    p = pr[-1] - pr[np.searchsorted(s.Time.values, s.Time.values[0] + np.timedelta64(spin, "h"))]
    ring = lambda a, b: np.r_[p[a:b, :].ravel(), p[-b:p.shape[0] - a or None, :].ravel(), p[:, a:b].ravel(), p[:, -b:p.shape[1] - a or None].ravel()]
    num["bdy_zone_mean_precip_mm"] = float(ring(0, 5).mean()); num["inner_ring_mean_precip_mm"] = float(ring(5, 10).mean())
    qc[e] = num
    data[e] = dict(h=h, s=s, w=w, c=c, qx=qx, qy=qy)
json.dump(qc, open(f"{OUT}/qc.json", "w"), indent=1, default=str)

ref = data["CONTROL"]; s0 = ref["s"]; h0 = ref["h"]
lat, lon = h0.XLAT.values[0], h0.XLONG.values[0]
lab = countries(lat, lon)
mf = h0.MAPFAC_M.values[0]; area = (15000.0 / mf) ** 2
it_s = np.searchsorted(s0.Time.values, s0.Time.values[0] + np.timedelta64(spin, "h"))
it_h = np.searchsorted(h0.Time.values, h0.Time.values[0] + np.timedelta64(spin, "h"))
inner = np.zeros(lat.shape, bool); inner[10:-10, 10:-10] = True
farm = np.zeros(lat.shape, bool)
if os.path.exists(f"{R}/WIND/windturbines.txt"):
    tb = pd.read_csv(f"{R}/WIND/windturbines.txt", sep=r"\s+", header=None, names=["lat", "lon", "k"])
    from scipy.spatial import cKDTree
    _, ii = cKDTree(np.c_[lat.ravel(), lon.ravel() * np.cos(np.radians(54))]).query(np.c_[tb.lat, tb.lon * np.cos(np.radians(54))])
    farm.ravel()[np.unique(ii)] = True


def summarise(e):
    d = data[e]; s, h = d["s"], d["h"]
    P = (s.RAINC + s.RAINNC).values; Pacc = P[-1] - P[it_s]
    E = s.SFCEVP.values; Eacc = E[-1] - E[it_s]
    hub = hub_wind(h)[it_h:].mean(0)
    out = dict(P_acc_mm=Pacc, E_acc_mm=Eacc, W=d["w"][it_h:].mean(0), IVTx=d["qx"][it_h:].mean(0), IVTy=d["qy"][it_h:].mean(0),
               hub_wind=hub, U10=np.hypot(s.U10, s.V10).values[it_s:].mean(0), T2=s.T2.values[it_s:].mean(0), Q2=s.Q2.values[it_s:].mean(0),
               LH=s.LH.values[it_s:].mean(0), HFX=s.HFX.values[it_s:].mean(0), PBLH=s.PBLH.values[it_s:].mean(0))
    if "POWER" in s: out["POWER"] = s.POWER.values[it_s:].mean(0)
    return out


summ = {e: summarise(e) for e in exps}
paired, rows = {}, []
for e in exps:
    if e == "CONTROL": continue
    dd = {k: summ[e][k] - summ["CONTROL"][k] for k in summ["CONTROL"]}
    stat = {}
    for k, v in dd.items():
        stat[k] = dict(domain_inner_mean=float(v[inner].mean()), farm_cells_mean=float(v[farm].mean()) if farm.any() else None,
                       inner_abs_max=float(abs(v[inner]).max()))
    kg = lambda a, m: float((a * area)[m].sum())   # mm == kg m-2
    stat["P_inner_total_kg"] = dict(control=kg(summ["CONTROL"]["P_acc_mm"], inner), diff=kg(dd["P_acc_mm"], inner))
    stat["E_inner_total_kg"] = dict(control=kg(summ["CONTROL"]["E_acc_mm"], inner), diff=kg(dd["E_acc_mm"], inner))
    stat["E_farm_total_kg"] = dict(control=kg(summ["CONTROL"]["E_acc_mm"], farm), diff=kg(dd["E_acc_mm"], farm)) if farm.any() else None
    if "POWER" in summ[e]: stat["mean_power_GW"] = float(summ[e]["POWER"].sum() / 1e9)
    paired[e] = stat
    for iso in sorted(set(lab[inner]) - {""}):
        m = inner & (lab == iso)
        rows.append(dict(exp=e, country=iso, n_cells=int(m.sum()), area_km2=float(area[m].sum() / 1e6),
                         P_control_kg=kg(summ["CONTROL"]["P_acc_mm"], m), dP_kg=kg(dd["P_acc_mm"], m),
                         dP_mm=float(dd["P_acc_mm"][m].mean()), dE_kg=kg(dd["E_acc_mm"], m)))
json.dump(dict(case=case, spinup_h=spin, window=[str(s0.Time.values[it_s]), str(s0.Time.values[-1])],
               n_farm_cells=int(farm.sum()), inner_cells=int(inner.sum()), paired=paired),
          open(f"{OUT}/paired.json", "w"), indent=1)
pd.DataFrame(rows).to_csv(f"{OUT}/country_precip.csv", index=False)
mp = xr.Dataset({f"{k}_{e}": (("y", "x"), np.asarray(v, "float32")) for e in exps for k, v in summ[e].items()},
                coords=dict(lat=(("y", "x"), lat), lon=(("y", "x"), lon)))
mp["farm"] = (("y", "x"), farm.astype("int8")); mp["inner"] = (("y", "x"), inner.astype("int8"))
mp["country"] = (("y", "x"), lab.astype(str))
mp.to_netcdf(f"{OUT}/maps.nc")
print(json.dumps(qc, indent=1, default=str)[:3000])
