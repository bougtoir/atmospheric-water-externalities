"""Gate 2: rasterise receptor countries and build source / placebo masks on the ERA5 grid (0.25 deg)."""
import json, zipfile, io, pathlib, numpy as np, pandas as pd, xarray as xr, shapefile, shapely
from shapely.geometry import shape
OUT = pathlib.Path("data/processed"); OUT.mkdir(parents=True, exist_ok=True)
g = xr.open_dataset(sorted(pathlib.Path("data/raw/era5").glob("era5_colbudget_*.nc"))[0])
lat, lon = g.latitude.values, g.longitude.values
LON, LAT = np.meshgrid(lon, lat)
z = zipfile.ZipFile("data/raw/boundaries/ne_50m_admin_0_countries.zip")
nm = lambda e: next(n for n in z.namelist() if n.endswith(e))
r = shapefile.Reader(shp=io.BytesIO(z.read(nm(".shp"))), dbf=io.BytesIO(z.read(nm(".dbf"))), shx=io.BytesIO(z.read(nm(".shx"))))
fields = [f[0] for f in r.fields[1:]]
country = np.full(LAT.shape, "", dtype=object)
partial = set()
for sr in r.iterShapeRecords():
    a = dict(zip(fields, sr.record)); iso = a["ISO_A2_EH"] if a.get("ISO_A2_EH", "-99") not in ("-99", "") else a["ADM0_A3"]
    geom = shape(sr.shape.__geo_interface__)
    minx, miny, maxx, maxy = geom.bounds
    if maxx < lon.min() or minx > lon.max() or maxy < lat.min() or miny > lat.max():
        continue
    box = shapely.box(lon.min(), lat.min(), lon.max(), lat.max())
    parts = [g_ for g_ in getattr(geom, "geoms", [geom]) if g_.intersects(box)]
    if parts:
        whole = shapely.union_all(parts)
        if whole.intersection(box).area / whole.area < 0.99:
            partial.add(iso)
    inside = shapely.contains_xy(geom, LON, LAT)
    country[inside & (country == "")] = iso
land = country != ""
t = pd.read_csv("data/raw/turbines_from_ecm_wind_heatwave.csv", parse_dates=["commissioning"])
off = t[t.offshore == True].copy()
off["i"] = np.rint((lat[0] - off.lat) / 0.25).astype(int); off["j"] = np.rint((off.lon - lon[0]) / 0.25).astype(int)
masks = {}
log = {"n_offshore": int(len(off)), "n_missing_commissioning": int(off.commissioning.isna().sum())}
for yr in range(2016, 2022):
    o = off[off.commissioning < f"{yr}-06-01"]
    cap = o.groupby(["i", "j", "country"]).capacity_mw.sum().reset_index()
    own = cap.sort_values("capacity_mw").groupby(["i", "j"]).tail(1)
    owner = np.full(LAT.shape, "", dtype=object)
    owner[own.i.values, own.j.values] = own.country.values
    allm = owner != ""
    # placebo: each farm cluster (8-connected) is translated independently (|shift| <= 12 cells = 3 deg) to sea
    # cells off existing farms (+1 cell halo) and off other placebo clusters; 5 fixed seeds.
    from scipy import ndimage
    halo = ndimage.binary_dilation(allm, np.ones((3, 3), bool))
    lab, nlab = ndimage.label(allm, np.ones((3, 3), int))
    pl = []
    for seed in range(5):
        rng = np.random.default_rng(1000 * yr + seed); pm = np.zeros_like(allm); failed = 0
        for k in range(1, nlab + 1):
            ii, jj = np.nonzero(lab == k); ok = []
            for di in range(-12, 13):
                for dj in range(-12, 13):
                    if (di, dj) == (0, 0): continue
                    a_, b_ = ii + di, jj + dj
                    if a_.min() < 1 or b_.min() < 1 or a_.max() >= LAT.shape[0] - 1 or b_.max() >= LAT.shape[1] - 1: continue
                    if land[a_, b_].any() or halo[a_, b_].any() or pm[a_, b_].any(): continue
                    ok.append((di, dj))
            if not ok: failed += 1; continue
            di, dj = ok[rng.integers(len(ok))]; pm[ii + di, jj + dj] = True
        pl.append(pm)
    log_pl = [dict(n_cells=int(m.sum()), failed_clusters=0) for m in pl]
    masks[yr] = dict(owner=owner, all=allm, placebo=pl, cap=float(o.capacity_mw.sum()), n_cells=int(allm.sum()))
    log[str(yr)] = dict(capacity_mw=round(float(o.capacity_mw.sum()), 3), n_cells=int(allm.sum()),
                        owners={k: int((owner == k).sum()) for k in sorted(set(owner[allm]))}, n_clusters=int(nlab), placebo=[int(m.sum()) for m in pl])
np.savez_compressed(OUT / "grid_masks.npz", lat=lat, lon=lon, country=country.astype("U8"),
                    **{f"owner_{y}": m["owner"].astype("U4") for y, m in masks.items()},
                    **{f"placebo_{y}": np.array(m["placebo"]) for y, m in masks.items()}, land=land)
log["receptors_partly_outside_domain"] = sorted(partial)
(OUT / "grid_masks_log.json").write_text(json.dumps(log, indent=1))
print(json.dumps(log, indent=1)[:2500])
