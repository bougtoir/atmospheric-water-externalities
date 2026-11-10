"""Summarise spread_growth.csv / country_precip_time.csv of all cases into results/wrf/spread_growth_summary.json.

Per case, field (instantaneous: hub_wind, W, IVT, P_3h) and band:
  sat_end   = no-wind spread averaged over the final 24 h / sigma_time (CONTROL temporal SD over the window, an
              approximate saturation level; non-stationary, so only indicative)
  growth_24 = spread averaged over the final 24 h / spread averaged over the preceding 24 h (>1: still growing)
  r_pp_cp   = window-mean d(pert,pert)/d(control,pert): 1 if members are exchangeable, sqrt(2) if each CTLPERT is an
              independent small departure from CONTROL (unsaturated, CONTROL-centred ensemble)
  r_wc_cp   = window-mean d(WIND,CONTROL)/d(control,pert); r_wp_pp = d(WIND,pert)/d(pert,pert)
Country accumulated precipitation: the PI half-width and flags recomputed at every hour from country_precip_time.csv
(independent code path from w10) and the final-hour flags compared with signal_noise.json.
"""
import glob, json
import numpy as np, pandas as pd
from scipy import stats

NOW = ["CONTROL", "CTLPERT_1", "CTLPERT_2", "CTLPERT_3"]; INST = ["hub_wind", "W", "IVT", "P_3h"]
out = {}
for f in sorted(glob.glob("results/wrf/*/spread_growth.csv")):
    case = f.split("/")[2]; d = pd.read_csv(f, parse_dates=["time"]); d = d[d.in_window]
    t1 = d.time.max(); last = d.time > t1 - pd.Timedelta(hours=24); prev = (d.time <= t1 - pd.Timedelta(hours=24)) & (d.time > t1 - pd.Timedelta(hours=48))
    R = {}
    for (fld, b), x in d.groupby(["field", "band"]):
        if fld not in INST + ["P_acc"]: continue
        L, Pv = x[last.loc[x.index]], x[prev.loc[x.index]]
        R.setdefault(fld, {})[b] = dict(
            sat_end=float(L.spread.mean() / L.sigma_time.mean()) if fld in INST else None,
            growth_24=float(L.spread.mean() / Pv.spread.mean()),
            r_pp_cp=float(x.d_pert_pert.mean() / x.d_ctl_pert.mean()),
            r_wc_cp=float(x.d_wind_ctl.mean() / x.d_ctl_pert.mean()),
            r_wp_pp=float(x.d_wind_pert.mean() / x.d_pert_pert.mean()))
    c = pd.read_csv(f"results/wrf/{case}/country_precip_time.csv", parse_dates=["time"])
    pv = c.pivot_table(index=["time", "country"], columns="exp", values="P_acc_kg")
    m, s = pv[NOW].mean(1), pv[NOW].std(1, ddof=1); hw = stats.t.ppf(0.975, 3) * s * np.sqrt(1 + 1 / 4)
    fl = ((pv.WIND - m).abs() > hw).groupby(level=0).sum()
    sd = s.groupby(level=0).median(); tt = sd.index
    fin = pv.loc[tt[-1]]; w10 = pd.read_csv(f"results/wrf/{case}/country_signal_noise.csv", index_col=0) if glob.glob(f"results/wrf/{case}/country_signal_noise.csv") else None
    sn = json.load(open(f"results/wrf/{case}/signal_noise.json"))
    out[case] = dict(fields=R, t_window_end=str(t1),
                     country_flags_by_day={str(t.date()) + "T" + str(t.time())[:5]: int(fl[t]) for t in tt if t.hour == 0 and t != tt[0]} | {"end": int(fl.iloc[-1])},
                     country_median_sd_kg_by_day={str(t)[:16]: float(sd[t]) for t in tt if t.hour == 0 and t != tt[0]} | {"end": float(sd.iloc[-1])},
                     flags_end_recomputed=int(fl.iloc[-1]), flags_max_any_hour=int(fl.max()), flags_min_after_24h=int(fl[fl.index >= tt[0] + pd.Timedelta(hours=24)].min()), flags_w10=int(sn["n_outside_internal_variability"]))
json.dump(out, open("results/wrf/spread_growth_summary.json", "w"), indent=1)
for k, v in out.items():
    print(k, "flags end", v["flags_end_recomputed"], "w10", v["flags_w10"], "by day", v["country_flags_by_day"])
    print(pd.DataFrame({f"{fl}/{b}": r for fl, bb in v["fields"].items() for b, r in bb.items() if b in ("inner", "far_gt150km")}).T.round(3).to_string())
