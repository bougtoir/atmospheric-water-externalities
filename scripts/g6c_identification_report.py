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

A = ["# Identifiability audit (Gate 6)", "",
     "Rendered by `scripts/g6c_identification_report.py` from `results/known_truth.csv` and `results/wrf/*/`.", "",
     "## Observable information", "",
     "ERA5 provides the realised state (W, Q, E, P) under the realised fleet. Tagged tracking of that state yields",
     "[A] provenance accounting and, with an assumed evaporation increment and fixed dynamics, the [S] supply term.",
     "The counterfactual state without the fleet is not observed. The receptor effect decomposes as",
     "ΔP_j = S_j + D_j + I_j (supply, dynamic, interaction). Only S_j is a functional of the observed state plus",
     "an assumed ΔE; D_j and I_j depend on unobserved changes in winds, stability and precipitation efficiency.", "",
     "## Admissible counterexamples (known-truth model)", "",
     f"Known-truth rows: {len(kt)}; dynamic configurations (δk≠0 or δu≠0): {len(dyn)} receptor-cases.",
     "Each configuration is mass-conserving and reproduces the same observed baseline, yet gives a different ΔP_j.", "",
     "| receptor | dynamic cases | sign reversals (truth/supply<0) | min truth/supply | max truth/supply |",
     "|---|---|---|---|---|"]
for r, x in dyn.groupby("receptor"):
    A.append(f"| {r} | {len(x)} | {(x.ratio < 0).sum()} | {g(x.ratio.min())} | {g(x.ratio.max())} |")
A += ["", "Hence ΔP_j is not point-identified from the observables used by [A]/[S]: observationally equivalent",
      "structures give opposite signs at the far receptor. The supply term is recovered exactly only when the",
      "dynamic perturbation is zero (see `KNOWN_TRUTH_VALIDATION.md`).", "",
      "## Relevance check with completed WRF cases", "",
      "WRF [C] contrasts are model-conditional (fixed WRF v4.6.1 configuration, generic turbine curves) and are",
      "used only to judge whether the dynamic term is plausibly negligible, not as ground truth.", ""]
for c, x in sv.items():
    m = x.S_dP_kg.notna() & x.C_dP_kg.notna() & (x.C_dP_kg != 0)
    q = (x.S_dP_kg[m] / x.C_dP_kg[m]).abs()
    A.append(f"- `{c}`: {m.sum()} countries; median |S/C| = {g(q.median())}, max |S/C| = {g(q.max())}; "
             f"same sign {int(x.same_sign[m].sum())}/{m.sum()}"
             + (f"; |C| exceeds single-member noise in {int(x.C_exceeds_noise[m].sum())}/{m.sum()}"
                if "C_exceeds_noise" in x and x.C_exceeds_noise.notna().any() else "; no noise reference"))
for c, s in sn.items():
    A.append(f"- `{c}` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members {s.get('noise_members', [s.get('noise_reference')])} by distance band:")
    for f in ("P_acc_mm", "E_acc_mm", "hub_wind", "IVTx", "PBLH"):
        if f in s["fields"]:
            A.append("  - " + f + ": " + ", ".join(f"{b} {g(v['ratio'] if isinstance(v, dict) else v)}"
                                                   for b, v in s["fields"][f].items()))
A += ["", "Interpretation: in the completed WRF cases the [S] term is small relative to the WRF country-level",
      "contrasts, and far-field contrasts are of the same order as a single initial-condition perturbation. The",
      "dynamic/internal-variability component therefore cannot be assumed negligible; [S] is not a TAWE estimate."]
open(f"{D}/IDENTIFIABILITY_AUDIT.md", "w").write("\n".join(A) + "\n")

P = ["# Partial identification report (Gate 6)", "",
     "Rendered by `scripts/g6c_identification_report.py`.", "",
     "With ΔP_j = S_j + R_j and only a bound |R_j| ≤ B_j available, the identified set is",
     "[S_j − B_j, S_j + B_j]. The sign of ΔP_j is identified only if |S_j| > B_j.", "",
     "## Bounds implied by the known-truth admissible family", "",
     "B_j is taken as max |truth − supply| over the dynamic configurations in `results/known_truth.csv`.", "",
     "| dE_frac | receptor | S_j (kg) | B_j (kg) | identified set (kg) | sign identified |", "|---|---|---|---|---|---|"]
for (e, r), x in dyn.groupby(["dE_frac", "receptor"]):
    S = kt[(kt.dE_frac == e) & (kt.receptor == r) & (kt.delta_k == 0) & (kt.delta_u == 0)].supply_kg.iloc[0]
    B = (x.truth_kg - x.supply_kg).abs().max()
    P.append(f"| {e} | {r} | {g(S)} | {g(B)} | [{g(S - B)}, {g(S + B)}] | {'yes' if abs(S) > B else 'no'} |")
P += ["", "## WRF-informed scale of the residual", "",
      "Using the WRF [C] contrast as a model-conditional scale for R_j = C_j − S_j:", ""]
for c, x in sv.items():
    m = x.S_dP_kg.notna() & x.C_dP_kg.notna()
    R = (x.C_dP_kg[m] - x.S_dP_kg[m]).abs()
    P.append(f"- `{c}`: countries with |S_j| > |C_j − S_j|: {int((x.S_dP_kg[m].abs() > R).sum())}/{m.sum()}")
kt_id = [r for (e, r), x in dyn.groupby(["dE_frac", "receptor"])
         if abs(kt[(kt.dE_frac == e) & (kt.receptor == r) & (kt.delta_k == 0) & (kt.delta_u == 0)].supply_kg.iloc[0])
         > (x.truth_kg - x.supply_kg).abs().max()]
wrf_id = sum(int((x.S_dP_kg.abs() > (x.C_dP_kg - x.S_dP_kg).abs()).sum()) for x in sv.values())
P += ["", f"Under the known-truth bound the sign is identified for receptor(s) {sorted(set(kt_id)) or 'none'} only.",
      f"Under the WRF-informed scale, the sign is identified from [S] in {wrf_id} country-case(s).",
      "Country-specific TAWE claims would require isolated-intervention ensembles large enough to bound",
      "internal variability."]
open(f"{D}/PARTIAL_IDENTIFICATION_REPORT.md", "w").write("\n".join(P) + "\n")
print("wrote", f"{D}/IDENTIFIABILITY_AUDIT.md", f"{D}/PARTIAL_IDENTIFICATION_REPORT.md", cases)
