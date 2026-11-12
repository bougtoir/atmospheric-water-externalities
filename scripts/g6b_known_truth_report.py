"""Render docs/revision/KNOWN_TRUTH_VALIDATION.md from results/known_truth.csv (no hard-coded values)."""
import pandas as pd

k = pd.read_csv("results/known_truth.csv")
k["dynamic"] = (k.delta_k != 0) | (k.delta_u != 0)
k["sign_reversal"] = k.truth_kg * k.supply_kg < 0
g = k.groupby(["dynamic", "receptor"]).agg(
    n=("sign_reversal", "size"), sign_reversals=("sign_reversal", "sum"),
    median_abs_supply_rel_err=("supply_rel_err", lambda x: x.abs().median()),
    max_abs_supply_rel_err=("supply_rel_err", lambda x: x.abs().max()),
    min_accounting_over_truth=("account_rel_err", lambda x: (x + 1).min())).reset_index()
nd = k[k.dynamic]; rev = int(nd.sign_reversal.sum())
L = ["# Known-truth validation (Gate 6)", "",
     "Source: `results/known_truth.csv` from `scripts/g5_known_truth.py` (idealised linear single-layer world solved with",
     "the project tracker). Truth = P(intervention) − P(no intervention) per receptor; supply estimator = ΔE_S × a_{S→c};",
     "accounting = A_{S→c}. Rendered by `scripts/g6b_known_truth_report.py`.", "",
     f"Configurations: {len(k)} rows = {k.dE_frac.nunique()} source perturbations × "
     f"{k.groupby(['delta_k','delta_u']).ngroups} (δk, δu) settings × {k.receptor.nunique()} receptors.", "",
     "| dynamic channel | receptor | n | sign reversals | median abs rel. error (supply) | max abs rel. error (supply) | min accounting/truth |",
     "|---|---|---|---|---|---|---|"]
for r in g.itertuples():
    L.append(f"| {r.dynamic} | {r.receptor} | {r.n} | {r.sign_reversals} | {r.median_abs_supply_rel_err:.3g} | "
             f"{r.max_abs_supply_rel_err:.3g} | {r.min_accounting_over_truth:.3g} |")
L += ["", f"Sign reversals: {rev}/{len(nd)} of all dynamic cases; "
      f"{int(nd[nd.receptor=='C2'].sign_reversal.sum())}/{int((nd.receptor=='C2').sum())} at the far receptor C2 "
      "(denominators reconciled in SIGN_REVERSAL_RECONCILIATION.md).", "",
      "Conclusions: (1) the supply estimator reproduces the truth to round-off when transport and rain efficiency are",
      "unchanged; (2) with a dynamic perturbation it is biased and can take the wrong sign, mainly at the far receptor;",
      "(3) accounting is never an externality estimate. The known-truth world tests estimator logic only; it is not",
      "an atmospheric model. Relevance to the atmosphere is assessed against the WRF contrasts in IDENTIFIABILITY_AUDIT.md."]
open("docs/revision/KNOWN_TRUTH_VALIDATION.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
