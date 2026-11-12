"""Semantic code audit: estimand -> assumption -> code -> output -> manuscript, with independent recomputation.

Writes docs/revision/SEMANTIC_CODE_AUDIT.md. Every check recomputes a reported quantity by a different code path or
by hand and compares it with the canonical output; failures are listed, not hidden."""
import glob, json, re, itertools, pathlib, math
import numpy as np, pandas as pd, docx
from scipy import stats

R = pathlib.Path("results"); rows = []
def chk(area, claim, how, ok, detail): rows.append((area, claim, how, "PASS" if ok else "FAIL", detail))
NOW = ["CONTROL", "CTLPERT_1", "CTLPERT_2", "CTLPERT_3"]
cases = sorted(p.split("/")[2] for p in glob.glob("results/wrf/*/country_signal_noise.csv"))

# 1. prediction-interval constant by hand
k = 3.182446305284263 * np.sqrt(1.25)
chk("PI", "half-width = t(0.975,n-1)·s·√(1+1/n), n = 4", "hand value t(0.975,3) = 3.182446 (table), ×√1.25",
    abs(stats.t.ppf(0.975, 3) * np.sqrt(1.25) - k) < 1e-9, f"factor {k:.4f}")
# 2. PI recomputed from raw member totals (country_precip.csv) vs w10 output
tot = bad = 0
for c in cases:
    cp = pd.read_csv(f"results/wrf/{c}/country_precip.csv"); sn = pd.read_csv(f"results/wrf/{c}/country_signal_noise.csv", index_col=0)
    P = {e: g.set_index("country").P_control_kg + g.set_index("country").dP_kg for e, g in cp.groupby("exp")}
    P["CONTROL"] = cp[cp.exp == "WIND"].set_index("country").P_control_kg
    E = np.array([P[m].loc[sn.index].values for m in NOW]); w = P["WIND"].loc[sn.index].values
    hw = k * E.std(0, ddof=1); f = np.abs(w - E.mean(0)) > hw
    tot += len(f); bad += int((f != sn.outside_internal_variability.values).sum())
    assert np.allclose(hw, sn.pi_halfwidth_kg.values, rtol=1e-9)
chk("PI", "country flags (w10) reproduce from member totals", "numpy recomputation from country_precip.csv", bad == 0, f"{tot} country-events, {bad} mismatches")
# 3. CONTROL identical across experiment rows
same = all(pd.read_csv(f"results/wrf/{c}/country_precip.csv").groupby("country").P_control_kg.nunique().max() == 1 for c in cases)
chk("PI", "one CONTROL baseline per event", "P_control_kg unique per country across exp rows", same, "")
# 4. 7/100 and binomial reference
WS = json.load(open(R / "wrf/programme_summary.json"))["pooled"]
K = sum(int(pd.read_csv(f"results/wrf/{c}/country_signal_noise.csv").outside_internal_variability.sum()) for c in cases)
N = sum(len(pd.read_csv(f"results/wrf/{c}/country_signal_noise.csv")) for c in cases)
pb = 1 - sum(math.comb(N, i) * .05 ** i * .95 ** (N - i) for i in range(K))
chk("PI", f"{WS['n_outside']}/{WS['n_tests']} flags; P(X≥K) for Bin(N,0.05)", "re-sum of flags; binomial by explicit sum",
    K == WS["n_outside"] and N == WS["n_tests"] and abs(pb - WS["p_binom_ge"]) < 1e-9, f"{K}/{N}, p = {pb:.4f} (descriptive: tests dependent)")
# 5. independent path: hourly country accumulation (w18, wrfsfc) vs window totals (w5, maps)
d = []
for c in cases:
    p = f"results/wrf/{c}/country_precip_time.csv"
    if not pathlib.Path(p).exists(): continue
    t = pd.read_csv(p); t = t[t.time == t.time.max()].set_index(["country", "exp"]).P_acc_kg
    cp = pd.read_csv(f"results/wrf/{c}/country_precip.csv")
    for _, r in cp.iterrows():
        d.append(abs(t[(r.country, r.exp)] - (r.P_control_kg + r.dP_kg)) / (r.P_control_kg + r.dP_kg))
    for _, r in cp[cp.exp == "WIND"].iterrows(): d.append(abs(t[(r.country, "CONTROL")] - r.P_control_kg) / r.P_control_kg)
chk("WRF", "country precipitation totals: hourly wrfsfc path (w18) = window path (w5)", "archived raw output re-read",
    len(d) > 0 and max(d) < 1e-3, f"{len(d)} values, max rel. diff {max(d) if d else float('nan'):.2e}")
SG = json.load(open(R / "wrf/spread_growth_summary.json"))
chk("WRF", "end-of-window flags from hourly path = w10 flags", "w20 recomputation", all(v["flags_end_recomputed"] == v["flags_w10"] for v in SG.values()),
    ", ".join(f"{c} {v['flags_end_recomputed']}/{v['flags_w10']}" for c, v in SG.items()))
# 6. field ratio definition vs wording
src = open("scripts/wrf/w10_signal_noise.py").read()
chk("WRF", "Fig. 9 denominator = mean over CTLPERT_k of RMS(CTLPERT_k − CONTROL)", "code inspection of w10 field loop",
    'mp[f"{f}_{k}"].values - mp[f"{f}_CONTROL"].values' in src, "caption and Section 4.6 now state this; earlier text said 'RMS spread'")
# 7. known truth
kt = pd.read_csv(R / "known_truth.csv"); dyn = kt[(kt.delta_k != 0) | (kt.delta_u != 0)]
st = kt[(kt.delta_k == 0) & (kt.delta_u == 0)]
chk("KT", "δ = 0 ⇒ truth = supply (linearity)", "max |rel err| over static rows", st.supply_rel_err.abs().max() < 1e-10, f"{st.supply_rel_err.abs().max():.1e}")
c2 = dyn[dyn.receptor == "C2"]; rev = int((np.sign(c2.truth_kg) != np.sign(c2.supply_kg)).sum())
chk("KT", "10/14 far-receptor sign reversals", "sign comparison of truth_kg vs supply_kg", (rev, len(c2)) == (10, 14), f"{rev}/{len(c2)} (grid-conditional count)")
chk("KT", "grid size 2×4×2 = 16 configs × 2 receptors = 32 rows", "row count", len(kt) == 32 and len(dyn) == 28, f"{len(kt)} rows, {len(dyn)} dynamic")
# supply formula: S = dE_tot·A_S/E_s is linear in dE_frac: S(0.2)/S(0.05) = 4
r4 = st.groupby("receptor")[["dE_frac", "supply_kg"]].apply(lambda x: x[x.dE_frac == .2].supply_kg.iloc[0] / x[x.dE_frac == .05].supply_kg.iloc[0])
chk("KT", "Eq. (5) linear in ΔE_S", "S(0.20)/S(0.05) = 4", np.allclose(r4, 4), r4.round(6).to_dict())
# accounting ≠ externality: account/truth = 1/dE_frac exactly in static case
chk("KT", "accounting A(S→c) is not the externality", "account_rel_err = 1/ΔE − 1 in static rows",
    np.allclose(st.account_rel_err, 1 / st.dE_frac - 1, rtol=1e-6), "e.g. 19 for ΔE = 5%")
# 8. partial identification: set recomputed and sharp
pi = []
for (e, rc), x in dyn.groupby(["dE_frac", "receptor"]):
    S = st[(st.dE_frac == e) & (st.receptor == rc)].supply_kg.iloc[0]; B = (x.truth_kg - x.supply_kg).abs().max()
    inside = ((x.truth_kg >= S - B - 1) & (x.truth_kg <= S + B + 1)).all(); attained = np.isclose((x.truth_kg - S).abs().max(), B)
    pi.append(inside and attained)
chk("PI-set", "every grid truth lies in [S−B, S+B] and an endpoint is attained", "recomputation per (ΔE, receptor)", all(pi), f"{len(pi)} sets")
rep = open("docs/revision/PARTIAL_IDENTIFICATION_REPORT.md").read()
chk("PI-set", "B labelled finite-grid, not physical; |C−S| not called a bound", "text check of report",
    "not a physical bound" in rep and "not a validated upper bound" in rep, "")
# 9. manuscript semantic text checks
doc = docx.Document("manuscript/manuscript.docx"); T = "\n".join(p.text for p in doc.paragraphs)
chk("MS", "no 'single-member noise'", "grep manuscript", "single-member" not in T, "")
chk("MS", "four-member PI wording in Fig. 11 caption", "grep", "95% prediction interval derived from the four-member no-wind ensemble" in T, "")
chk("MS", "10/14 described as grid-conditional", "grep", "prespecified synthetic grid" in T and "not how probable" in T, "")
chk("MS", "non-detection ≠ zero effect", "grep", "not evidence of zero effect" in T, "")
chk("MS", "identified set Eq. (6) present as OMML", "count m:oMath", len(doc.element.body.xpath(".//m:oMath")) == 6, f"{len(doc.element.body.xpath('.//m:oMath'))} equations")
chk("MS", "no 'within internal variability' as a positive claim", "grep", "remain within internal variability" not in T, "")
chk("MS", "spread saturation not asserted", "grep", not re.search(r"spread (had )?saturated|saturated before", T), "")
L = ["# Semantic code audit", "", "Rendered by `scripts/g10_semantic_audit.py`. Each row compares a stated estimand or claim with the code and",
     "its output by an independent recomputation (different code path, hand value or text check). Unit tests are not counted.", "",
     "| area | claim | independent check | status | detail |", "|---|---|---|---|---|"]
L += [f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows]
L += ["", "## Estimand–assumption map", "",
      "| quantity | estimand | key assumption | code | manuscript |", "|---|---|---|---|---|",
      "| a(S→c) [A] | share of tagged source evaporation precipitating in c | well-mixed column tagging | g3_track.py | Eq. 3 |",
      "| Δ_supply [S] | ΔE_S·a(S→c) | fixed dynamics, assumed ΔE_S | g5_known_truth.py, w12_supply_vs_wrf.py | Eq. 5 |",
      "| TAWE [C] | P_c(WIND) − P_c(CONTROL) in WRF | model-conditional; one realisation | w5_analyse_case.py | Eq. 4 |",
      "| identified set | [S − B, S + B] | assumed |Δ_dynamic| ≤ B | g6c_identification_report.py | Eq. 6 |",
      "| PI flag | |WIND − mean| > t·s·√(1+1/n) | exchangeability, normality | w10_signal_noise.py | Sec. 3.5, 4.8 |", "",
      f"Overall: {'ALL PASS' if all(r[3] == 'PASS' for r in rows) else 'FAILURES PRESENT'} ({sum(r[3] == 'PASS' for r in rows)}/{len(rows)})."]
pathlib.Path("docs/revision/SEMANTIC_CODE_AUDIT.md").write_text("\n".join(L) + "\n")
print(L[-1]); [print(r) for r in rows if r[3] != "PASS"]
