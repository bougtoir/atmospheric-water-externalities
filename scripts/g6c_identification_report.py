"""Render IDENTIFIABILITY_AUDIT.md and PARTIAL_IDENTIFICATION_REPORT.md from canonical result files.

Inputs: results/known_truth.csv, results/wrf/*/supply_vs_wrf.csv, results/wrf/*/signal_noise.json.
No scientific value is typed into this script; all numbers are read from the inputs.
"""
import glob, json, os
import numpy as np, pandas as pd

D = "docs/revision"
kt = pd.read_csv("results/known_truth.csv")
kt["ratio"] = kt.truth_kg / kt.supply_kg
dyn = kt[(kt.delta_k != 0) | (kt.delta_u != 0)]

cases = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob("results/wrf/*/supply_vs_wrf.csv"))
sv = {c: pd.read_csv(f"results/wrf/{c}/supply_vs_wrf.csv", index_col=0) for c in cases}
sn = {c: json.load(open(f"results/wrf/{c}/signal_noise.json")) for c in cases
      if os.path.exists(f"results/wrf/{c}/signal_noise.json")}

def g(x): return f"{x:.3g}"

n_c2 = len(dyn[dyn.receptor == "C2"]); r_c2 = int((dyn[dyn.receptor == "C2"].ratio < 0).sum())
r_all = int((dyn.ratio < 0).sum())
A = ["# Identifiability audit (Gate 6)", "",
     "Rendered by `scripts/g6c_identification_report.py` from `results/known_truth.csv` and `results/wrf/*/`.", "",
     "Three distinct findings are reported separately: (A) structural non-identifiability, (B) numerical sign reversals",
     "inside a prespecified synthetic grid, and (C) empirical uncertainty of the WRF intervention contrasts.", "",
     "## Observable information and estimand", "",
     "Observables: the realised atmospheric state (W, Q, E, P from ERA5) and an assumed evaporation increment ΔE_S.",
     "Model class: mass-conserving column-moisture transport, dW/dt + ∇·Q = E − P. Estimand: the receptor effect",
     "ΔP_j = P_j(fleet) − P_j(no fleet) = S_j + D_j + I_j (supply, dynamic, interaction). S_j is a functional of",
     "the observed state and ΔE_S. D_j and I_j depend on intervention-induced changes in winds, stability and",
     "precipitation efficiency, which appear only in the unobserved counterfactual state.", "",
     "## (A) Structural non-identifiability", "",
     "Within this model class, any intervention-dependent change in transport or precipitation efficiency that is not",
     "constrained by the observables leaves the observed state unchanged while changing ΔP_j. ΔP_j is therefore not",
     "point-identified from the stated observables unless D_j + I_j is restricted by an additional assumption",
     "(e.g. fixed dynamics, which makes ΔP_j = S_j). This follows from the construction of the problem; the",
     "known-truth experiment illustrates it but does not prove it. The statement is limited to the stated",
     "observables and model class; it does not exclude identification with additional information (e.g. validated",
     "coupled models, natural experiments or isolated interventions).", "",
     "## (B) Numerical sign reversals in the prespecified synthetic grid", "",
     f"Known-truth rows: {len(kt)}; dynamic receptor-cases (δk≠0 or δu≠0): {len(dyn)}. Grid: δk ∈ {sorted(kt.delta_k.unique().tolist())},",
     f"δu ∈ {sorted(kt.delta_u.unique().tolist())}, ΔE_S/E ∈ {sorted(kt.dE_frac.unique().tolist())}, chosen before the runs, not derived from physics.", "",
     "| receptor | dynamic cases | sign reversals (truth/supply<0) | min truth/supply | max truth/supply |",
     "|---|---|---|---|---|"]
for r, x in dyn.groupby("receptor"):
    A.append(f"| {r} | {len(x)} | {(x.ratio < 0).sum()} | {g(x.ratio.min())} | {g(x.ratio.max())} |")
A += ["", f"The {r_c2}/{n_c2} far-receptor reversals ({r_all}/{len(dyn)} over both receptors) are counts within this grid.",
      "They show that sign reversal is possible for modest dynamic perturbations. They are not a physical probability of",
      "sign reversal: a different grid would give a different count. With δ = 0 the supply estimator reproduces the",
      "truth to round-off (KNOWN_TRUTH_VALIDATION.md).", "",
      "### Direction of the observed baseline", "",
      "In the known-truth experiment the observed state is the no-intervention world, and the supply estimator uses its",
      "tagging. In the real setting the observed state (ERA5) already contains the existing wind farms, and the no-fleet",
      "state is the counterfactual. The identification argument is symmetric: in both directions one state is observed,",
      "the other is not, and the unconstrained dynamic response separates them. Formal non-identifiability (A) is",
      "therefore unaffected. The numerical values in (B) are affected: in the real direction S_j would be computed from",
      "the with-fleet state with the sign of ΔE reversed, and second-order differences (S evaluated on the wrong",
      "state) are not quantified by this experiment.", "",
      "## (C) Empirical uncertainty of the WRF contrasts", "",
      "WRF [C] contrasts are model-conditional (fixed WRF v4.6.1 configuration, generic turbine curves). They are",
      "compared with the 95% prediction interval derived from the four-member no-wind ensemble; the calibration of",
      "that interval is audited in WRF_PREDICTION_INTERVAL_AUDIT.md and WRF_ENSEMBLE_SPREAD_GROWTH.md.", ""]
for c, x in sv.items():
    m = x.S_dP_kg.notna() & x.C_dP_kg.notna() & (x.C_dP_kg != 0)
    q = (x.S_dP_kg[m] / x.C_dP_kg[m]).abs()
    A.append(f"- `{c}`: {m.sum()} countries; median |S/C| = {g(q.median())}, max |S/C| = {g(q.max())}; "
             f"same sign {int(x.same_sign[m].sum())}/{m.sum()}"
             + (f"; C outside the 95% prediction interval derived from the four-member no-wind ensemble in {int(x.C_exceeds_noise[m].sum())}/{m.sum()}"
                if "C_exceeds_noise" in x and x.C_exceeds_noise.notna().any() else "; no noise reference"))
for c, s in sn.items():
    A.append(f"- `{c}` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members {s.get('noise_members', [s.get('noise_reference')])} by distance band:")
    for f in ("P_acc_mm", "E_acc_mm", "hub_wind", "IVTx", "PBLH"):
        if f in s["fields"]:
            A.append("  - " + f + ": " + ", ".join(f"{b} {g(v['ratio'] if isinstance(v, dict) else v)}"
                                                   for b, v in s["fields"][f].items()))
A += ["", "Interpretation: [S] is small relative to the WRF country-level contrasts, and the far-field contrasts are of",
      "the same order as the no-wind ensemble spread. A WRF contrast that is not distinguishable from internal variability",
      "is not evidence of zero effect; it bounds nothing deterministically. [S] is not a TAWE estimate."]
open(f"{D}/IDENTIFIABILITY_AUDIT.md", "w").write("\n".join(A) + "\n")

P = ["# Partial identification report (Gate 6)", "",
     "Rendered by `scripts/g6c_identification_report.py`.", "",
     "## Decomposition and identified set", "",
     "ΔP_j = S_j + R_j, with R_j = D_j + I_j. If |R_j| ≤ B_j is assumed, the identified set is [S_j − B_j, S_j + B_j],",
     "and it is sharp for that assumption: every point is attained by some R_j with |R_j| ≤ B_j. The sign of ΔP_j is",
     "identified only if |S_j| > B_j. The interval is exactly as credible as the assumption on B_j.", "",
     "Four different quantities are kept apart:", "",
     "| quantity | what it is | used here as |",
     "|---|---|---|",
     "| mathematically imposed bound | an assumption \\|R_j\\| ≤ B_j stated a priori | the premise of the interval formula |",
     "| finite-grid maximum | max \\|truth − supply\\| over the prespecified synthetic grid | an illustrative B_j, conditional on the grid |",
     "| statistically estimated interval | e.g. the WRF no-wind 95% prediction interval | a statement about internal variability, not a deterministic bound |",
     "| physically justified bound | a bound on the dynamic response derived from physics or validated models | not available in this study |", "",
     "## Illustration: B_j = finite-grid maximum (synthetic world only)", "",
     "B_j is max |truth − supply| over the dynamic configurations of the prespecified grid in `results/known_truth.csv`.",
     "It is not a physical bound: dynamic perturbations outside the grid can exceed it.", "",
     "| dE_frac | receptor | S_j (kg) | grid max B_j (kg) | grid-conditional set (kg) | sign identified under this B_j |", "|---|---|---|---|---|---|"]
for (e, r), x in dyn.groupby(["dE_frac", "receptor"]):
    S = kt[(kt.dE_frac == e) & (kt.receptor == r) & (kt.delta_k == 0) & (kt.delta_u == 0)].supply_kg.iloc[0]
    B = (x.truth_kg - x.supply_kg).abs().max()
    P.append(f"| {e} | {r} | {g(S)} | {g(B)} | [{g(S - B)}, {g(S + B)}] | {'yes' if abs(S) > B else 'no'} |")
kt_id = [r for (e, r), x in dyn.groupby(["dE_frac", "receptor"])
         if abs(kt[(kt.dE_frac == e) & (kt.receptor == r) & (kt.delta_k == 0) & (kt.delta_u == 0)].supply_kg.iloc[0])
         > (x.truth_kg - x.supply_kg).abs().max()]
P += ["", f"Under the grid maximum the sign is identified for receptor(s) {sorted(set(kt_id)) or 'none'} of the synthetic world only;",
      "this conclusion holds only if the true dynamic response lies inside the grid.", "",
      "## WRF: why no bound is derived", "",
      "|C_j − S_j| from one WRF WIND − CONTROL pair mixes the model-conditional dynamic response with internal",
      "variability of a single realisation. It is not a validated upper bound on R_j and is not used as one. The no-wind",
      "95% prediction interval describes internal variability under assumptions audited in",
      "WRF_PREDICTION_INTERVAL_AUDIT.md; turning its width into a deterministic B_j would require an additional assumption",
      "(e.g. that the expected dynamic response is smaller than internal variability), which is not justified here.",
      "Descriptively, |S_j| is smaller than |C_j − S_j| in every WRF country-case:"]
for c, x in sv.items():
    m = x.S_dP_kg.notna() & x.C_dP_kg.notna()
    R = (x.C_dP_kg[m] - x.S_dP_kg[m]).abs()
    P.append(f"- `{c}`: countries with |S_j| > |C_j − S_j|: {int((x.S_dP_kg[m].abs() > R).sum())}/{m.sum()}")
P += ["", "Consequence: no real-world country-specific TAWE interval is reported. A defensible B_j would require",
      "isolated-intervention ensembles large enough to estimate the expected dynamic response and its uncertainty."]
open(f"{D}/PARTIAL_IDENTIFICATION_REPORT.md", "w").write("\n".join(P) + "\n")
print("wrote", f"{D}/IDENTIFIABILITY_AUDIT.md", f"{D}/PARTIAL_IDENTIFICATION_REPORT.md", cases)
