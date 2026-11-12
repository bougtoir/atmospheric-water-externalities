"""Build Fitch wind-farm inputs (windturbines.txt + wind-turbine-N.tbl) for a WRF case.

Usage: python scripts/wrf/w2_turbines.py RUN_DIR DATE [COUNTRIES]  e.g. wrf_runs/pilot 2020-06-30 ALL|NL,DK
Intervention = offshore turbines in the register commissioned before DATE inside the WRF domain (optionally
restricted to listed countries). Missing hub height / rotor diameter are filled from the median of
offshore turbines with the same rated power class; turbines with missing commissioning date are excluded
(as in the ERA5 source masks). Power/thrust curves are idealised generic curves per class (no
manufacturer curves are available in the register): P(U)=min(C_P2 * 0.5 rho A U^3, P_r) for cut-in 3.5 m/s
to cut-out 25 m/s with C_P2=0.45; C_T=0.80 below rated and C_T=0.80*C_P/C_P2 above rated. Table power is
written in kW and nominal power in MW, as read by WRF module_wind_fitch.
"""
import json, os, sys
import numpy as np, pandas as pd

run, date = sys.argv[1], sys.argv[2]
cty = None if len(sys.argv) < 4 or sys.argv[3] == "ALL" else sys.argv[3].split(",")
dom = json.load(open(os.path.join(run, "domain_bounds.json")))
# The register stacks national registries (DE MaStR, DK Stamdata) on top of EWW for the same offshore
# turbines (median nearest-neighbour distance 4–12 m); a single source avoids double-counting.
SOURCE = "eww"
t = pd.read_csv("data/raw/turbines_from_ecm_wind_heatwave.csv", parse_dates=["commissioning"])
o = t[(t.offshore == True) & (t.source == SOURCE) & t.commissioning.notna() & (t.commissioning < date) & t.capacity_mw.notna()].copy()
o = o[(o.lat > dom["lat_min"]) & (o.lat < dom["lat_max"]) & (o.lon > dom["lon_min"]) & (o.lon < dom["lon_max"])]
if cty:
    o = o[o.country.isin(cty)]
o["cls"] = np.clip(np.round(o.capacity_mw), 2, 12).astype(int)
for c in ("hub_height_m", "rotor_diameter_m"):
    med = o.groupby("cls")[c].transform("median")
    o[c] = o[c].fillna(med).fillna(o[c].median())
classes = sorted(o.cls.unique())
# Idealised generic curve (no manufacturer data in the register): constant Cp = CP2 below rated power,
# constant Ct = CT2 below rated; above rated, Ct scales with the power-limited Cp (Ct = CT2*Cp/CP2),
# which is continuous at rated and close to NREL 5-MW reference thrust values. WRF expects power in kW and nominal power in MW.
rho, uci, uco, CP2, CT2 = 1.225, 3.5, 25.0, 0.45, 0.80
meta = []
for k, c in enumerate(classes, start=1):
    s = o[o.cls == c]
    hh, d, pr = float(s.hub_height_m.median()), float(s.rotor_diameter_m.median()), float(c)
    A = np.pi * d * d / 4
    rows = []
    for u in np.arange(uci, uco + 0.01, 0.5):
        p = min(CP2 * 0.5 * rho * A * u ** 3, pr * 1e6)
        cp = p / (0.5 * rho * A * u ** 3)
        ct = CT2 * cp / CP2
        rows.append((u, ct, p / 1e3))
    with open(os.path.join(run, f"wind-turbine-{k}.tbl"), "w") as f:
        f.write(f"{len(rows)}\n{hh:.1f} {d:.1f} 0.130 {pr:.2f}\n")
        for u, ct, p in rows:
            f.write(f"{u:.1f} {ct:.4f} {p:.1f}\n")
    meta.append(dict(type=k, rated_mw=pr, hub_m=hh, diameter_m=d, n=int(len(s))))
    o.loc[o.cls == c, "type"] = k
with open(os.path.join(run, "windturbines.txt"), "w") as f:
    for r in o.itertuples():
        f.write(f"{r.lat:.5f} {r.lon:.5f} {int(r.type)}\n")
summ = dict(date=date, countries=cty or "ALL", n_turbines=int(len(o)), capacity_mw=float(o.capacity_mw.sum()),
            by_country=o.groupby("country").capacity_mw.sum().round(1).to_dict(), types=meta)
json.dump(summ, open(os.path.join(run, "windfarm_summary.json"), "w"), indent=1)
print(json.dumps(summ)[:600])
