"""Audit of the country-level prediction-interval (PI) comparison used in w10_signal_noise.py.

Writes results/wrf/pi_audit.json. All inputs are canonical result files (country_precip.csv per case); no WRF rerun.
1. Monte Carlo coverage of the n-member Student-t PI when the members are (a) i.i.d., (b) equicorrelated
   (exchangeable), (c) "centred": CONTROL is the unperturbed trajectory and every other member (CTLPERT_k and, under no
   effect, WIND) diverges from it: x_C = z0, x_k = kappa*z0 + sqrt(1-kappa^2)*z_k. kappa = 0 is exchangeable;
   kappa -> 1 means unsaturated spread. Pairwise-distance ratio r = d(P,P)/d(C,P) = sqrt(1+kappa).
2. Empirical r for each event from the WRF country totals (identifies where the design sits between (b) and (c)).
3. Leave-one-out placebo: each no-wind member in turn treated as 'WIND' against the other three (n = 3 PI);
   the flag rate estimates the actual false-flag rate of the procedure on this design.
4. WIND distances d(W,C) and d(W,P) against d(C,P), d(P,P) (pairing check).
"""
import glob, json, os, itertools
import numpy as np, pandas as pd
from scipy import stats

rng = np.random.default_rng(20261110)
NOW = ["CONTROL", "CTLPERT_1", "CTLPERT_2", "CTLPERT_3"]


def flag(x_new, ens):
    n = len(ens); s = np.std(ens, ddof=1, axis=0)
    return np.abs(x_new - ens.mean(0)) > stats.t.ppf(0.975, n - 1) * s * np.sqrt(1 + 1 / n)


def mc(kind, par, n=4, N=200000):
    z = rng.standard_normal((n + 1, N))
    if kind == "iid": x = z
    elif kind == "equicorr": x = np.sqrt(par) * rng.standard_normal(N) + np.sqrt(1 - par) * z
    else:  # centred: row 0 = CONTROL, rows 1..n-1 = CTLPERT, row n = WIND (no effect)
        x = np.vstack([z[:1], par * z[:1] + np.sqrt(1 - par ** 2) * z[1:]])
    return float(1 - flag(x[n], x[:n]).mean())


cov = dict(iid=mc("iid", 0), equicorr={str(r): mc("equicorr", r) for r in (0.3, 0.6, 0.9)},
           centred={str(k): mc("centred", k) for k in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0)})
# heavy tails: t3 members
zt = stats.t.rvs(3, size=(5, 200000), random_state=1); cov["iid_t3"] = float(1 - flag(zt[4], zt[:4]).mean())
kap = np.linspace(0, 1, 41); cov_curve = [mc("centred", k, N=60000) for k in kap]

ev = {}
for f in sorted(glob.glob("results/wrf/*/country_precip.csv")):
    case = f.split("/")[2]; cp = pd.read_csv(f)
    ctl = cp[cp.exp == "WIND"].set_index("country").P_control_kg
    P = pd.DataFrame({"CONTROL": ctl, **{e: g.set_index("country").P_control_kg + g.set_index("country").dP_kg
                                          for e, g in cp.groupby("exp")}})
    if not set(NOW) <= set(P): continue
    d2 = lambda a, b: float(((P[a] - P[b]) ** 2).sum())
    dcp = np.mean([d2("CONTROL", k) for k in NOW[1:]]); dpp = np.mean([d2(a, b) for a, b in itertools.combinations(NOW[1:], 2)])
    dwc = d2("WIND", "CONTROL"); dwp = np.mean([d2("WIND", k) for k in NOW[1:]])
    r = np.sqrt(dpp / dcp); k_hat = float(np.clip(r ** 2 - 1, 0, 1))
    loo = [bool(x) for j in NOW for x in flag(P[j].values, P[[m for m in NOW if m != j]].values.T)]
    # per-country ratio
    rc = np.sqrt(np.mean([(P[a] - P[b]) ** 2 for a, b in itertools.combinations(NOW[1:], 2)], 0) /
                 np.mean([(P["CONTROL"] - P[k]) ** 2 for k in NOW[1:]], 0))
    ev[case] = dict(n_countries=len(P), r_pp_over_cp=float(r), kappa_hat=k_hat,
                    coverage_at_kappa_hat=float(np.interp(k_hat, kap, cov_curve)),
                    r_country_median=float(np.median(rc)), r_country_iqr=[float(np.percentile(rc, 25)), float(np.percentile(rc, 75))],
                    d_wind_ctl_over_d_ctl_pert=float(np.sqrt(dwc / dcp)), d_wind_pert_over_d_pert_pert=float(np.sqrt(dwp / dpp)),
                    loo_flags=int(sum(loo)), loo_tests=len(loo))
L = sum(v["loo_flags"] for v in ev.values()); M = sum(v["loo_tests"] for v in ev.values())
rp = float(np.sqrt(np.mean([v["r_pp_over_cp"] ** 2 for v in ev.values()])))
out = dict(seed=20261110, n_members=4, coverage_mc=cov, kappa_grid=kap.tolist(), coverage_curve_centred=cov_curve,
           events=ev, pooled=dict(r_pp_over_cp_rms=rp, kappa_hat=float(np.clip(rp ** 2 - 1, 0, 1)),
                                  coverage_at_kappa_hat=float(np.interp(np.clip(rp ** 2 - 1, 0, 1), kap, cov_curve)),
                                  loo_flags=L, loo_tests=M, loo_rate=L / M,
                                  loo_binom_ci=[float(x) for x in stats.binomtest(L, M).proportion_ci(0.95)]))
json.dump(out, open("results/wrf/pi_audit.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("coverage_mc", "pooled")}, indent=1)); print(pd.DataFrame(ev).T.round(3).to_string())
