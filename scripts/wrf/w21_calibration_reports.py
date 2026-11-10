"""Render docs/revision/WRF_PREDICTION_INTERVAL_AUDIT.md and WRF_ENSEMBLE_SPREAD_GROWTH.md from
results/wrf/pi_audit.json and results/wrf/spread_growth_summary.json (no hand-typed values)."""
import json, pathlib
import pandas as pd
PA = json.load(open("results/wrf/pi_audit.json")); SG = json.load(open("results/wrf/spread_growth_summary.json"))
WS = json.load(open("results/wrf/programme_summary.json"))["pooled"]; D = pathlib.Path("docs/revision")
g = lambda x, n=3: f"{x:.{n}f}"; INST = ["hub_wind", "W", "IVT", "P_3h"]
cm = PA["coverage_mc"]; po = PA["pooled"]
A = ["# WRF prediction-interval audit", "",
     "Rendered by `scripts/wrf/w21_calibration_reports.py` from `results/wrf/pi_audit.json` (`scripts/wrf/w19_pi_audit.py`)",
     "and `results/wrf/spread_growth_summary.json` (`scripts/wrf/w18_spread_growth.py`, `w20_spread_summary.py`). No WRF rerun.", "",
     "## Procedure audited (`scripts/wrf/w10_signal_noise.py`)", "",
     "Per event and country: no-wind ensemble {CONTROL, CTLPERT_1–3} (n = 4) of post-spin-up precipitation totals; mean m and",
     "sample SD s (ddof = 1); one WIND run per event. Flag if |WIND − m| > t(0.975, 3)·s·√(1 + 1/4) = 3.558·s. This is the",
     "95% prediction interval for one new draw from the no-wind distribution. Code, numbers and hand recomputation agree",
     "(SEMANTIC_CODE_AUDIT.md).", "",
     "## Assumptions and checks", "",
     "| assumption | why it matters | check | result |", "|---|---|---|---|",
     f"| exchangeability of WIND (under no effect) and the four no-wind members | t-interval coverage | Monte Carlo, i.i.d. normal | coverage {g(cm['iid'])} |",
     f"| independence not required if exchangeable | members share synoptic forcing | equicorrelated members ρ = 0.3/0.6/0.9 | {', '.join(g(v) for v in cm['equicorr'].values())} |",
     f"| CONTROL is the unperturbed member; others diverge from it | non-exchangeable if spread unsaturated | 'CONTROL-centred' model x_k = κ z_0 + √(1−κ²) z_k, κ = {', '.join(cm['centred'])} | {', '.join(g(v) for v in cm['centred'].values())} (κ = 1: zero spread, degenerate) |",
     f"| where the design sits | κ from d(pert,pert)/d(CONTROL,pert) = √(1+κ) | pooled over 5 events × 20 countries | ratio {g(po['r_pp_over_cp_rms'])}, κ̂ = {g(po['kappa_hat'],2)}, implied coverage {g(po['coverage_at_kappa_hat'])} |",
     f"| approximate normality | small n, heavy tails | i.i.d. t₃ members | coverage {g(cm['iid_t3'])} |",
     f"| actual false-flag rate on this design | combines all of the above | leave-one-out placebo: each no-wind member vs the other three (n = 3 interval) | {po['loo_flags']}/{po['loo_tests']} = {g(po['loo_rate'])} (95% CI {g(po['loo_binom_ci'][0])}–{g(po['loo_binom_ci'][1])}) |",
     "| WIND–CONTROL pairing | WIND starts from CONTROL's initial state | d(WIND,CONTROL)/d(CONTROL,pert), d(WIND,pert)/d(pert,pert) per event | table below |",
     "| country dependence | 20 neighbouring countries share weather | not modelled | binomial reference descriptive only |",
     "| temporal spread evolution | interval reflects spread at one lead time | WRF_ENSEMBLE_SPREAD_GROWTH.md | spread not saturated |", "",
     "| event | r = d(P,P)/d(C,P) | κ̂ | implied coverage | per-country r median [IQR] | d(W,C)/d(C,P) | d(W,P)/d(P,P) | LOO flags |",
     "|---|---|---|---|---|---|---|---|"]
for c, v in PA["events"].items():
    A.append(f"| {c} | {g(v['r_pp_over_cp'])} | {g(v['kappa_hat'],2)} | {g(v['coverage_at_kappa_hat'])} | {g(v['r_country_median'],2)} [{g(v['r_country_iqr'][0],2)}, {g(v['r_country_iqr'][1],2)}] | "
             f"{g(v['d_wind_ctl_over_d_ctl_pert'])} | {g(v['d_wind_pert_over_d_pert_pert'])} | {v['loo_flags']}/{v['loo_tests']} |")
A += ["", "## Interpretation", "",
      "- Inclusion of CONTROL does not by itself invalidate the interval. If the members are exchangeable, coverage is nominal even",
      "  when they are correlated. If CONTROL is the centre from which unsaturated members diverge, coverage drops only to about",
      f"  {g(cm['centred']['0.9'])} (κ = 0.9). The observed distance ratios lie between the two cases, with large event-to-event scatter",
      f"  (single-event r from 4 members is itself very noisy). Implied coverage {g(po['coverage_at_kappa_hat'])}; leave-one-out flag rate {g(po['loo_rate'])}.",
      "- Interval width is estimated from three degrees of freedom; the t-factor accounts for that on average, but individual",
      "  half-widths are uncertain by roughly a factor of two.",
      f"- {WS['n_outside']}/{WS['n_tests']} flags against {WS['expected_outside']:.0f} expected. Bin({WS['n_tests']}, 0.05) gives P(X ≥ {WS['n_outside']}) = {WS['p_binom_ge']:.3f}; this is a",
      "  calibration aid only, because country tests are spatially dependent and share one WIND run per event.",
      "- The interval describes internal variability at the end of the analysis window under the present (unsaturated)",
      "  spread. It is not a deterministic bound on the dynamic response and is not used as one.",
      "- No relabelling of the interval was required; the manuscript states its assumptions (Sections 3.5, 4.8)."]
(D / "WRF_PREDICTION_INTERVAL_AUDIT.md").write_text("\n".join(A) + "\n")
B = ["# WRF ensemble spread growth", "",
     "Rendered by `scripts/wrf/w21_calibration_reports.py` from `results/wrf/*/spread_growth.csv` and",
     "`results/wrf/spread_growth_summary.json`. Source: archived `wrfout_d01_*` (3-hourly) and `wrfsfc_d01_*` (hourly) of all",
     "five members per event, restored from the private archive with SHA-256 verification; no new WRF simulation.", "",
     "Fields: hub-height (100 m) wind speed; column water vapour W; |IVT| (vertically integrated vapour transport magnitude);",
     "3-h precipitation and post-spin-up accumulated precipitation. Spread = √(band mean of across-member variance, ddof = 1) of",
     "the four no-wind members. Reference σ_time = √(band mean of CONTROL temporal variance over the analysis window); this is",
     "an approximate, non-stationary saturation scale, not a climatological variance. Figure 12 / Figure_W6.", "",
     "Metrics (band > 150 km from farms): sat_end = spread / σ_time over the final 24 h; growth = spread(final 24 h) / spread(preceding 24 h);",
     "r_pp = d(pert,pert)/d(CONTROL,pert) (1 exchangeable, √2 CONTROL-centred).", "",
     "| event | field | sat_end | growth | r_pp | d(W,C)/d(C,P) |", "|---|---|---|---|---|---|"]
for c, v in SG.items():
    for f in INST + ["P_acc"]:
        x = v["fields"][f]["far_gt150km"]
        B.append(f"| {c} | {f} | {'' if x['sat_end'] is None else g(x['sat_end'])} | {g(x['growth_24'],2)} | {g(x['r_pp_cp'],2)} | {g(x['r_wc_cp'],2)} |")
B += ["", "## Country flags over time", "", "| event | flags at 00 UTC each day | end | min after 24 h | max any hour |", "|---|---|---|---|---|"]
for c, v in SG.items():
    fd = {k: n for k, n in v["country_flags_by_day"].items() if k != "end"}
    B.append(f"| {c} | {', '.join(f'{k[5:10]}: {n}' for k, n in fd.items())} | {v['flags_end_recomputed']} | {v['flags_min_after_24h']} | {v['flags_max_any_hour']} |")
sat = max(v["fields"][f]["far_gt150km"]["sat_end"] for v in SG.values() for f in INST)
grow = [c for c, v in SG.items() if pd.Series([v["fields"][f]["far_gt150km"]["growth_24"] for f in INST]).median() > 1]
B += ["", "## Findings", "",
      f"- Spread starts from zero and, over the final 24 h, reaches at most {sat:.0%} of σ_time for the instantaneous fields.",
      f"- Median growth over the final 24 h exceeds 1 in {len(grow)}/{len(SG)} events ({', '.join(grow) or 'none'}); in the others the spread",
      "  fluctuates with the synoptic evolution rather than levelling off at a ceiling.",
      "- Saturation is therefore not established. Spread is far below σ_time, which itself is only an approximate ceiling.",
      "- Consequence: the four-member prediction interval describes internal variability at the present lead time and may",
      "  underestimate the variability of a saturated ensemble (and, for accumulated precipitation, its continued growth).",
      "  Intervals that are too narrow would flag too often; intervals estimated from too few members are also noisy.",
      "- The number of flagged countries varies over the window (table above), so end-of-window counts are one realisation.",
      "- A contrast not distinguishable from this spread is not evidence of zero effect."]
(D / "WRF_ENSEMBLE_SPREAD_GROWTH.md").write_text("\n".join(B) + "\n")
print("wrote", D / "WRF_PREDICTION_INTERVAL_AUDIT.md", D / "WRF_ENSEMBLE_SPREAD_GROWTH.md", list(SG))
