"""Gate 5: numerical sensitivity of the accounting coefficients (ALL tag, July 2019 by default).

Variants: CFL 0.5 (reference), CFL 0.25 (time step halved), 3-hourly forcing (every 3rd hour, fluxes held,
accumulations summed). Output results/numerics_sensitivity.csv.
"""
import sys, json, pathlib, numpy as np, pandas as pd, xarray as xr
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tawe.tracking import Tracker, cfl_substeps
month = sys.argv[1] if len(sys.argv) > 1 else "2019-07"; yr = int(month[:4])
M = np.load("data/processed/grid_masks.npz"); lat, lon, country = M["lat"], M["lon"], M["country"]
src = (M[f"owner_{yr}"] != "")
ds = xr.open_dataset(f"data/raw/era5/era5_colbudget_{month}.nc").load()
Wv = ds.total_column_water_vapour.values; Fu = ds.vertical_integral_of_eastward_water_vapour_flux.values
Fv = ds.vertical_integral_of_northward_water_vapour_flux.values
E = np.maximum(-1000.0 * ds.evaporation.values / 3600.0, 0); P = np.maximum(1000.0 * ds.total_precipitation.values / 3600.0, 0)
PARTIAL = set(json.load(open("data/processed/grid_masks_log.json"))["receptors_partly_outside_domain"])

def run(cfl, stride):
    tr = Tracker(lat, lon, src)
    for i in range(stride, Wv.shape[0], stride):
        W = 0.5 * (Wv[i - stride] + Wv[i]); fu = 0.5 * (Fu[i - stride] + Fu[i]); fv = 0.5 * (Fv[i - stride] + Fv[i])
        e = E[i - stride + 1:i + 1].mean(0); p = P[i - stride + 1:i + 1].mean(0)
        n = cfl_substeps(W, fu, fv, lat, lon, 3600.0 * stride, cfl)
        for _ in range(n): tr.step(W, fu, fv, e, p, 3600.0 * stride / n)
    Es = float(tr.budget["E_src"]); out = {"E_src_kg": Es, "closure_rel": abs(float(tr.closure_residual())) / Es}
    for c in sorted(set(country.ravel()) - {""} - PARTIAL):
        out[c] = float(tr.P_tag_acc[country == c].sum()) / Es
    out["SEA"] = float(tr.P_tag_acc[country == ""].sum()) / Es
    return out

rows = []
for name, cfl, stride in [("ref_cfl0.5_1h", 0.5, 1), ("cfl0.25_1h", 0.25, 1), ("cfl0.5_3h", 0.5, 3)]:
    r = run(cfl, stride); r["variant"] = name; rows.append(r); print(name, r["closure_rel"], flush=True)
df = pd.DataFrame(rows).set_index("variant").T
df.to_csv("results/numerics_sensitivity.csv"); pathlib.Path("results/numerics_month.txt").write_text(month)
num = df.drop(["E_src_kg", "closure_rel"])
num = num[num["ref_cfl0.5_1h"] > 1e-3]
print((num.sub(num["ref_cfl0.5_1h"], axis=0).div(num["ref_cfl0.5_1h"], axis=0)).abs().max())
