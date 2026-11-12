"""Gate 6: compare the [S] supply-channel estimate with the WRF [C] contrast for one case.

[S]_c = dE_farm (WRF WIND-CONTROL evaporation change over farm cells, kg) x a_{ALL->c} (ERA5 tracking, JJA of the
case year). [C]_c = WRF WIND-CONTROL precipitation change over country c. Internal variability: no-wind ensemble prediction interval from w10 (country_signal_noise.csv) when
available, else the single CTLPERT-CONTROL change.
a is a seasonal coefficient applied to a 5-day event, so [S] is an order-of-magnitude reference, not a forecast.
Usage: python scripts/wrf/w12_supply_vs_wrf.py CASE YEAR [NOISE=CTLPERT_1]
"""
import json, sys
import pandas as pd

case, year = sys.argv[1], int(sys.argv[2]); noise = sys.argv[3] if len(sys.argv) > 3 else "CTLPERT_1"
OUT = f"results/wrf/{case}"
pj = json.load(open(f"{OUT}/paired.json"))["paired"]["WIND"]
dE = pj["E_farm_total_kg"]["diff"]
sr = pd.read_csv("results/source_receptor.csv")
a = sr[(sr.year == year) & (sr.tag == "ALL")].set_index("receptor").a
cp = pd.read_csv(f"{OUT}/country_precip.csv")
w = cp[cp.exp == "WIND"].set_index("country")
df = pd.DataFrame(dict(C_dP_kg=w.dP_kg))
df["S_dP_kg"] = dE * a.reindex(df.index)
import os
csn = f"{OUT}/country_signal_noise.csv"
if os.path.exists(csn) and "outside_internal_variability" in open(csn).readline():
    e = pd.read_csv(csn, index_col=0)
    df["pi_halfwidth_kg"] = e.pi_halfwidth_kg
    df["C_exceeds_noise"] = e.outside_internal_variability
    noise = "no-wind ensemble n=%d (95%% prediction interval)" % json.load(open(f"{OUT}/signal_noise.json"))["n_no_wind_ensemble"]
    df["noise_dP_kg"] = e.pi_halfwidth_kg
elif noise in set(cp.exp):
    df["noise_dP_kg"] = cp[cp.exp == noise].set_index("country").dP_kg
    df["C_exceeds_noise"] = df.C_dP_kg.abs() > df.noise_dP_kg.abs()
df["S_over_C"] = df.S_dP_kg / df.C_dP_kg
df["same_sign"] = (df.S_dP_kg * df.C_dP_kg) > 0
df.to_csv(f"{OUT}/supply_vs_wrf.csv")
summ = dict(case=case, year=year, dE_farm_kg=dE, n_countries=int(df.S_dP_kg.notna().sum()),
            sum_abs_S_kg=float(df.S_dP_kg.abs().sum()), sum_abs_C_kg=float(df.C_dP_kg.abs().sum()),
            n_same_sign=int(df.same_sign.sum()),
            n_C_exceeds_noise=int(df.C_exceeds_noise.sum()) if "C_exceeds_noise" in df else None,
            noise_reference=noise if "noise_dP_kg" in df else None)
json.dump(summ, open(f"{OUT}/supply_vs_wrf.json", "w"), indent=1)
print(json.dumps(summ, indent=1)); print(df.round(4).to_string())
