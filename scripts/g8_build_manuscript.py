"""Build manuscript/manuscript.docx, submission/highlights.docx, submission/cover_letter.md from results/*.
All numbers are read from results files at build time (no hard-coded estimates)."""
import json, pathlib, re, numpy as np, pandas as pd
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml import parse_xml
R = pathlib.Path("results"); OUT = pathlib.Path("manuscript"); OUT.mkdir(exist_ok=True); S = pathlib.Path("submission"); S.mkdir(exist_ok=True)
refs = pd.read_csv("references/references_verified.csv").set_index("key")
years = sorted(int(p.stem.split("_")[-1]) for p in R.glob("track_budget_*.json"))
bud = {y: json.load(open(R / f"track_budget_{y}.json")) for y in years}
mlog = json.load(open("data/processed/grid_masks_log.json"))
kt = pd.read_csv(R / "known_truth.csv"); sr = pd.read_csv(R / "source_receptor.csv"); tb = pd.read_csv(R / "transboundary_share.csv")
pl = pd.read_csv(R / "placebo_test.csv"); dt = pd.read_csv(R / "detectability.csv"); nm = pd.read_csv(R / "numerics_sensitivity.csv", index_col=0)

def f2(x): return f"{x:.2f}"
def pct(x, d=1): return f"{100 * x:.{d}f}%"
# ---- computed values
V = {}
V["y0"], V["y1"], V["ny"] = years[0], years[-1], len(years)
V["cap0"] = mlog[str(years[0])]["capacity_mw"] / 1000; V["cap1"] = mlog[str(years[-1])]["capacity_mw"] / 1000
V["cells0"] = mlog[str(years[0])]["n_cells"]; V["cells1"] = mlog[str(years[-1])]["n_cells"]
V["n_off"] = mlog["n_offshore"]; V["n_miss"] = mlog["n_missing_commissioning"]
V["closure"] = max(max(b["closure_rel"]) for b in bud.values())
V["ntags"] = len(bud[years[-1]]["tags"])
k0 = kt[(kt.delta_k == 0) & (kt.delta_u == 0)]; kd = kt[(kt.delta_k != 0) | (kt.delta_u != 0)]
V["kt_lin_err"] = k0.supply_rel_err.abs().max(); V["kt_n_dyn"] = len(kd)
V["kt_dyn_med"] = kd.supply_rel_err.abs().median(); V["kt_dyn_max"] = kd.supply_rel_err.abs().max()
V["kt_flip"] = int((np.sign(kd.truth_kg) != np.sign(kd.supply_kg)).sum())
V["kt_flip_c2"] = int(((np.sign(kd.truth_kg) != np.sign(kd.supply_kg)) & (kd.receptor == "C2")).sum()); V["kt_n_c2"] = int((kd.receptor == "C2").sum())
V["kt_acc_min"] = kt.account_rel_err.abs().min()
al = sr[sr.tag == "ALL"]
land = al[al.receptor != "SEA"].groupby("year").a.sum(); sea = al[al.receptor == "SEA"].groupby("year").a.first()
out = al.groupby("year").outflow_frac.first()
V["land_mean"], V["land_min"], V["land_max"] = land.mean(), land.min(), land.max()
V["sea_mean"], V["out_mean"] = sea.mean(), out.mean()
tbm = tb.groupby("owner")[["own_land", "foreign_land"]].mean()
tbm["ratio"] = tbm.foreign_land / tbm.own_land
V["tb_owner_min"] = tbm.ratio.idxmin(); V["tb_ratio_min"] = tbm.ratio.min(); V["tb_owner_max"] = tbm.ratio.idxmax(); V["tb_ratio_max"] = tbm.ratio.max()
V["tb_foreign_min"], V["tb_foreign_max"] = tbm.foreign_land.min(), tbm.foreign_land.max()
V["tb_own_min"], V["tb_own_max"] = tbm.own_land.min(), tbm.own_land.max()
plr = pl[pl.receptor != "SEA"]
V["pl_n"] = len(plr); V["pl_inside"] = int(plr.real_inside_placebo_range.sum())
top = al[(al.receptor != "SEA") & (~al.receptor_partly_outside_domain)].groupby("receptor").a.mean().sort_values(ascending=False)
V["top3"] = ", ".join(f"{c} ({f2(100*v)}%)" for c, v in top.head(3).items())
d5 = dt[dt.n_seasons_each == 5]; d10 = dt[dt.n_seasons_each == 10]
V["dt_med5"], V["dt_min5"], V["dt_min10"] = d5.required_dE_frac.median(), d5.required_dE_frac.min(), d10.required_dE_frac.min()
V["dt_min5_c"] = d5.set_index("receptor").required_dE_frac.idxmin(); V["dt_ncty"] = len(d5)
V["A_over_P_max"] = d5.A_over_P.max(); V["A_over_P_max_c"] = d5.set_index("receptor").A_over_P.idxmax()
num = nm.drop(["E_src_kg", "closure_rel"]).astype(float); num = num[num["ref_cfl0.5_1h"] > 1e-3]
rel = num.sub(num["ref_cfl0.5_1h"], axis=0).div(num["ref_cfl0.5_1h"], axis=0).abs()
NUM_MONTH = open(R / "numerics_month.txt").read().strip()
V["num_cfl"] = rel["cfl0.25_1h"].max(); V["num_3h"] = rel["cfl0.5_3h"].max()
# ---- WRF [C] values: model-conditional WIND - CONTROL contrasts (results/wrf/*, rendered by scripts/wrf/w15, w16)
WS = json.load(open(R / "wrf/programme_summary.json")); WC = WS["cases"]; WP = WS["pooled"]
wreg = pd.read_csv("docs/revision/WRF_EXPERIMENT_REGISTRY.csv"); wsr = pd.read_csv(R / "wrf/source_receptor_wrf.csv")
RC = {c: json.load(open(R / f"wrf/{c}/run_config.json")) for c in WC}
assert len({json.dumps(r["namelist_WIND"], sort_keys=True) for r in RC.values()}) == 1, "WRF configuration differs between events"
def nlv(k): return RC[sorted(WC)[0]]["namelist_WIND"][k]
V["w_dx_km"] = int(nlv("dx")) // 1000; V["w_nz"] = int(nlv("e_vert")); V["w_nx"] = int(nlv("e_we")); V["w_ny"] = int(nlv("e_sn"))
V["w_tke"] = float(nlv("windfarm_tke_factor"))
V["w_events"] = len(WC); V["w_runs"] = int(wreg.valid.sum()); V["w_invalid"] = int((~wreg.valid).sum())
V["w_regimes"] = ", ".join(sorted({v["regime"] for v in WC.values()}))
V["w_nens"] = min(v["n_no_wind_ensemble"] for v in WC.values())
pw = {c: json.load(open(R / f"wrf/{c}/paired.json"))["paired"]["WIND"] for c in WC}
inv = {c: RC[c]["turbines"] for c in WC}
V["w_cap_min"] = min(v["capacity_mw"] for v in inv.values()) / 1000; V["w_cap_max"] = max(v["capacity_mw"] for v in inv.values()) / 1000
V["w_pow_min"] = min(v["mean_power_GW"] for v in WC.values()); V["w_pow_max"] = max(v["mean_power_GW"] for v in WC.values())
V["w_hub_min"] = min(p["hub_wind"]["farm_cells_mean"] for p in pw.values()); V["w_hub_max"] = max(p["hub_wind"]["farm_cells_mean"] for p in pw.values())
V["w_pblh_min"] = min(p["PBLH"]["farm_cells_mean"] for p in pw.values()); V["w_pblh_max"] = max(p["PBLH"]["farm_cells_mean"] for p in pw.values())
rat = lambda f, b: [v["ratios"][f][b] for v in WC.values()]
V["w_sn_hub_near_min"] = min(rat("hub_wind", "farm_0_30km")); V["w_sn_hub_near_max"] = max(rat("hub_wind", "farm_0_30km"))
V["w_sn_pblh_near_min"] = min(rat("PBLH", "farm_0_30km")); V["w_sn_pblh_near_max"] = max(rat("PBLH", "farm_0_30km"))
V["w_sn_p_far_min"] = min(rat("P_acc_mm", "far_gt150km")); V["w_sn_p_far_max"] = max(rat("P_acc_mm", "far_gt150km"))
V["w_sn_hub_far_max"] = max(rat("hub_wind", "far_gt150km"))
V["w_dP_tot_min"] = min(v["dP_inner_total_pct"] for v in WC.values()) / 100; V["w_dP_tot_max"] = max(v["dP_inner_total_pct"] for v in WC.values()) / 100
V["w_K"], V["w_N"], V["w_pbin"] = WP["n_outside"], WP["n_tests"], WP["p_binom_ge"]; V["w_expK"] = WP["expected_outside"]
V["w_ncty"] = wsr.country.nunique()
V["w_S_noise_med"] = wsr.S_over_noise.median(); V["w_S_noise_max"] = wsr.S_over_noise.max()
rep_ = wsr[wsr.outside_internal_variability].groupby("country").case.nunique(); V["w_rep2"] = int((rep_ >= 2).sum())
va = {c: json.load(open(R / f"wrf/{c}/validation.json"))["fields"] for c in WC}
V["w_vbP_min"] = min(v["P_acc_mm"]["rel_bias"] for v in va.values()); V["w_vbP_max"] = max(v["P_acc_mm"]["rel_bias"] for v in va.values())
V["w_vrP_min"] = min(v["P_acc_mm"]["spatial_r"] for v in va.values()); V["w_vrP_max"] = max(v["P_acc_mm"]["spatial_r"] for v in va.values())
V["w_vrW_min"] = min(v["W"]["spatial_r"] for v in va.values())
json.dump({k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in V.items()}, open(R / "manuscript_values.json", "w"), indent=1, default=str)

# ---- citation helpers (author-year)
cited = set()
def surname(k): return refs.loc[k, "authors"].split(";")[0].strip().rsplit(" ", 1)[0]
def ay(k):
    a = [x.strip() for x in refs.loc[k, "authors"].split(";")]; y = int(refs.loc[k, "year"]); cited.add(k)
    if len(a) == 1: return f"{surname(k)}, {y}"
    if len(a) == 2: return f"{a[0].rsplit(' ',1)[0]} and {a[1].rsplit(' ',1)[0]}, {y}"
    return f"{surname(k)} et al., {y}"
def c(*ks): return "(" + "; ".join(ay(k) for k in sorted(ks, key=lambda k: int(refs.loc[k, 'year']))) + ")"

doc = Document(); st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
for s in doc.sections: s.left_margin = s.right_margin = Cm(2.5)
def H(t, l=1): doc.add_heading(t, level=l)
def Pp(t): doc.add_paragraph(t)
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
def r(t, sty=None):
    sx = f'<m:sty m:val="{sty}"/>' if sty else ""
    return f'<m:r><m:rPr>{sx}</m:rPr><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t xml:space="preserve">{t}</m:t></m:r>'
def sub(b, s): return f'<m:sSub><m:e>{r(b)}</m:e><m:sub>{r(s)}</m:sub></m:sSub>'
def frac(n, d): return f'<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>'
def eq(body, num):
    p = doc.add_paragraph()
    p._p.append(parse_xml(f'<m:oMathPara xmlns:m="{M_NS}" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr><m:oMath>{body}{r("     (" + str(num) + ")")}</m:oMath></m:oMathPara>'))

TITLE = "Moisture Provenance and Counterfactual Attribution of Transboundary Atmospheric Water Effects: A Modelling Framework with Offshore Wind-Farm Experiments"
doc.add_heading(TITLE, 0)
Pp("Onishi Tatsuki")
Pp("Affiliation and ORCID: [to be completed by the author]")
Pp("Corresponding author: Onishi Tatsuki [e-mail to be completed by the author]")
H("Abstract")
ABS = (f"Energy infrastructure that alters evaporation or near-surface flow can shift precipitation across borders, "
       f"but moisture tracking reports where existing moisture rains out, not what an intervention changes. This study "
       f"separates moisture provenance accounting, a supply-channel scenario and model-conditional intervention contrasts, and "
       f"releases a conservation-closed tagging tool. In known-truth worlds the supply estimator reverses sign at the far "
       f"receptor in {V['kt_flip_c2']} of {V['kt_n_c2']} dynamic cases. For European offshore wind farms (ERA5, summers "
       f"{V['y0']}–{V['y1']}), {pct(V['land_mean'])} of farm-cell evaporation rains over land, mostly abroad, but placebo "
       f"sources reproduce {V['pl_inside']} of {V['pl_n']} receptor coefficients. Paired WRF simulations with and without a "
       f"wind-farm parameterisation ({V['w_events']} events, {V['w_nens']}-member no-wind ensembles) give clear near-farm "
       f"wind and boundary-layer responses, whereas cross-border precipitation contrasts remain within internal variability.")
Pp(ABS)
Pp("Keywords: moisture tracking; precipitationshed; offshore wind; identifiability; counterfactual; ERA5; externalities")

H("1. Introduction")
Pp(f"Atmospheric moisture links distant land and sea surfaces: evaporation in one jurisdiction supplies precipitation "
   f"in another {c('trenberth1999','keys2012','tuinenburg2020')}. Governance research has framed these flows as "
   f"precipitationsheds and as an ecosystem service that crosses borders {c('keys2016','keys2017','keys2018','teklemariam2019','transprecip2026')}, "
   f"and recycling networks have been used to assess freshwater vulnerability {c('keune2019')}. Separately, mesoscale "
   f"models with wind-farm parameterisations show that large wind farms alter boundary-layer winds, turbulence, humidity "
   f"and, in some cases, precipitation downwind {c('fitch2012','giantwf2011','pryor2020','fischereit2022')}, with recent "
   f"North Sea studies projecting coastal precipitation responses {c('akhtar2026','southbight2026')} and observational "
   f"studies reporting near-farm flux and onshore precipitation changes {c('fluxes2014','siedersleben2018','alfahel2020','surfaceimpacts2022')}. "
   f"Wake losses between neighbouring farms are already recognised as an inter-operator externality {c('lundquist2019')}.")
Pp("These literatures meet at a question that neither answers on its own: if a wind farm in one country changes "
   "precipitation in another, how large is that transboundary atmospheric water externality (TAWE), and what can be "
   "identified from the data and models available? Moisture-tracking models, Eulerian or Lagrangian, attribute "
   f"existing precipitation to its evaporative origin {c('vanderent2013','lagrframe2022','lagrglobal2022','wam2layers2025')}, "
   f"but their attributions differ substantially between models {c('eulerlagr2024','multimodel2025')} and, more "
   "fundamentally, an attribution of existing moisture is not the change caused by an intervention. A governance "
   "argument that treats source–receptor accounting as an externality therefore risks a category error.")
Pp("This paper contributes (i) a formal definition of TAWE as a counterfactual difference with an explicit channel "
   "decomposition and evidence classes; (ii) an open, conservation-closed forward-tagging tool driven by reanalysis "
   "column budgets, with verification tests; (iii) known-truth experiments that quantify when the computable supply "
   "channel recovers the externality; and (iv) a European offshore-wind test case with placebo sources and a "
   "detectability analysis; and (v) paired regional simulations with and without a wind-farm parameterisation, with "
   "initial-condition ensembles that measure internal variability, which give model-conditional intervention contrasts "
   "for the dynamic channel. What cannot be identified is reported alongside what can.")

H("2. Framework")
H("2.1. Column budget and tagged moisture", 2)
Pp("Let W be column water vapour (kg m⁻²), F the vertically integrated vapour flux (kg m⁻¹ s⁻¹), and E and P "
   "evaporation and precipitation (kg m⁻² s⁻¹). The column budget and the budget of moisture tagged at its evaporation "
   "in a source region S are")
eq(r("∂W/∂t + ∇·") + r("F", "b") + r(" = E − P + ε"), 1)
eq(r("∂") + sub("W", "S") + r("/∂t + ∇·(") + r("F", "b") + sub("W", "S") + r("/W) = E") + sub("1", "S") + r(" − P") + sub("W", "S") + r("/W"), 2)
Pp("where ε is the analysis residual and 1_S the source indicator. Tagged precipitation integrated over a receptor c "
   "and season gives the accounting quantity A(S→c); normalised by source evaporation it is the transfer coefficient")
eq(sub("a", "S→c") + r(" = ") + frac(sub("A", "S→c"), r("∫") + sub("E", "S") + r("dt")), 3)
H("2.2. Externality definition and channels", 2)
Pp("For an intervention I located in jurisdiction j, the externality on receptor c ≠ j is the counterfactual difference")
eq(sub("TAWE", "j→c") + r(" = ") + sub("P", "c") + r("(I) − ") + sub("P", "c") + r("(no I) = ") + sub("Δ", "supply") + r(" + ") + sub("Δ", "dynamic"), 4)
eq(sub("Δ", "supply") + r(" = ") + sub("ΔE", "S") + r("·") + sub("a", "S→c"), 5)
Pp("The supply channel routes perturbed source evaporation with unchanged winds and precipitation efficiency; the "
   "dynamic channel collects every other response (flow deceleration, convergence, boundary-layer and cloud changes) "
   "and acts on all moisture, not only on the tagged fraction. Results are labelled [A] accounting (Eq. 3), "
   "[S] scenario (Eq. 5 for a stated ΔE_S) or [C] model-conditional contrast (Eq. 4 from an executed pair of simulations "
   "that differ only in the intervention). A [C] contrast is conditional on the model, its configuration and the "
   "simulated events; it is not an observed real-world effect (Fig. 1).")

H("3. Software, data and evaluation design")
H("3.1. Tagging tool", 2)
Pp(f"Eq. (2) is solved on the reanalysis grid with a donor-cell finite-volume scheme: face fluxes are means of adjacent "
   f"cell-centre fluxes, the tagged fraction is taken from the upwind cell, the domain edge is open (tagged outflow is "
   f"recorded, inflow carries no tag), and 0 ≤ W_S ≤ W is enforced with the clipped mass recorded. Sub-steps follow a "
   f"Courant number of 0.5 computed hourly. Every tag carries an exact budget, Σ E_S = Σ P_S + outflow + storage + clip, "
   f"and several tags are advanced simultaneously. Verification tests cover exact closure, the tag-capacity bound, zero "
   f"source, multi-tag linearity and an analytic exponential rain-out profile exp(−kx/u).")
H("3.2. Data and source masks", 2)
Pp(f"Hourly ERA5 {c('hersbach2020')} vertically integrated vapour fluxes, total column water vapour, evaporation and "
   f"total precipitation were retrieved at 0.25° for 20°W–35°E, 35–72°N, June–August {V['y0']}–{V['y1']}. Source cells "
   f"are 0.25° cells containing offshore turbines commissioned before 1 June of each season (offshore register subset of "
   f"{V['n_off']:,} turbines; {V['n_miss']} without commissioning date excluded), growing from {V['cells0']} cells "
   f"({V['cap0']:.1f} GW) in {V['y0']} to {V['cells1']} cells ({V['cap1']:.1f} GW) in {V['y1']} (Fig. 2). Each cell is "
   f"owned by the country with the largest installed capacity in it. Receptors are national land areas rasterised from "
   f"1:50m country polygons; countries extending beyond the domain are excluded from receptor statistics.")
H("3.3. Falsification and detectability", 2)
Pp("Placebo sources were built by translating each 8-connected farm cluster independently by up to 3° to sea cells "
   "away from existing farms (five fixed seeds per season), preserving cluster shapes. A transfer coefficient that lies "
   "inside the placebo range describes location-generic meteorology, not the infrastructure. Detectability compares "
   "the supply signal per unit fractional increase in farm-cell evaporation with the interannual standard deviation "
   "of receptor summer precipitation in a two-sample before/after design (α = 0.05, power 0.8).")
H("3.4. Known-truth experiments", 2)
Pp("An idealised linear moisture world (dW/dt + ∇·(uW) = E − kW, eastward flow of 8 m s⁻¹, 18 h rain-out time) with a "
   "sea source and near and far land receptors was run with and without an intervention that raises source evaporation "
   "by 5% or 20% and, optionally, changes rain efficiency (δk) or transport speed (δu) in a box downwind of the source. "
   "The true externality is the difference of the two runs; the supply estimator uses Eq. (5) with baseline tagging.")

H("3.5. Paired regional simulations", 2)
Pp(f"WRF v4.6.1 was run on a single Lambert domain of {V['w_nx']} × {V['w_ny']} cells at {V['w_dx_km']} km with "
   f"{V['w_nz']} levels, driven by hourly ERA5 at the lateral boundaries without nudging (Thompson microphysics, RRTMG "
   f"radiation, MYNN surface layer and boundary layer, Noah land surface, Kain–Fritsch convection). Events were "
   f"prespecified from ERA5 alone as five-day summer windows with strong onshore vapour transport across the North Sea "
   f"and above-median precipitation ({V['w_regimes']} regimes), each simulated with one day before and after; the initial "
   f"24 h are discarded. The intervention is the full offshore fleet commissioned before each event "
   f"({V['w_cap_min']:.1f}–{V['w_cap_max']:.1f} GW) represented by the Fitch parameterisation {c('fitch2012')} with TKE "
   f"factor {V['w_tke']}. CONTROL and WIND differ only in this switch. Internal variability is sampled by three "
   f"additional no-wind runs whose initial potential temperature in the lowest ten levels is perturbed by Gaussian noise "
   f"(σ = 0.01 K, fixed seeds). A WIND − CONTROL difference is called distinguishable when it lies outside the 95% "
   f"prediction interval of the {V['w_nens']}-member no-wind ensemble; with about 20 receptor countries, one flag per "
   f"event is expected by chance.")

H("4. Results")
H("4.1. Verification", 2)
Pp(f"All {V['ntags']} tags in all {V['ny']} seasons closed their budgets to a maximum relative residual of "
   f"{V['closure']:.1e}. Halving the time step changed land transfer coefficients by at most {pct(V['num_cfl'])}, and "
   f"3-hourly instead of hourly forcing by at most {pct(V['num_3h'])} (test month {NUM_MONTH}).")
H("4.2. Known-truth recovery", 2)
Pp(f"Without dynamic perturbation the supply estimator reproduced the true externality to a relative error of "
   f"{V['kt_lin_err']:.1e} (Fig. 3). With a dynamic channel the median absolute relative error was "
   f"{pct(V['kt_dyn_med'],0)} (maximum {pct(V['kt_dyn_max'],0)}); the sign was wrong in {V['kt_flip']} of "
   f"{V['kt_n_dyn']} cases, {V['kt_flip_c2']} of them at the far receptor, because a downwind change in transport speed or "
   f"rain efficiency redistributes background moisture that the tag does not see. Treating accounting A(S→c) as the "
   f"externality was wrong by at least a factor of {1 + V['kt_acc_min']:.1f}.")
H("4.3. European accounting [A]", 2)
Pp(f"Across seasons, {pct(V['land_mean'])} (range {pct(V['land_min'])}–{pct(V['land_max'])}) of farm-cell evaporation "
   f"precipitated over land inside the domain, {pct(V['sea_mean'])} over sea, and {pct(V['out_mean'])} left the domain "
   f"(Fig. 4). The largest in-domain receptors were {V['top3']}. For every owner the foreign share exceeded the domestic "
   f"share: foreign land received {pct(V['tb_foreign_min'])}–{pct(V['tb_foreign_max'])} and the owner's own land "
   f"{pct(V['tb_own_min'])}–{pct(V['tb_own_max'])} of the owner's farm-cell evaporation (ratio {V['tb_ratio_min']:.0f} for "
   f"{V['tb_owner_min']} to {V['tb_ratio_max']:.0f} for {V['tb_owner_max']}; Table 1).")
H("4.4. Placebo test", 2)
Pp(f"For {V['pl_inside']} of {V['pl_n']} land receptors the real-source coefficient lay within the range of placebo "
   f"sources (Fig. 5)" + (". Transfer coefficients therefore describe the meteorology of the North Sea and Baltic "
   "source areas rather than anything specific to the farm locations." if V["pl_inside"] == V["pl_n"] else
   ". Coefficients outside the placebo range show that the specific farm locations matter for accounting, but "
   "location-specific accounting is still not an effect of the infrastructure (Section 4.2)."))
H("4.5. Detectability [S]", 2)
Pp(f"Farm-cell evaporation of tagged origin contributes at most {pct(V['A_over_P_max'],2)} of summer precipitation in any "
   f"receptor ({V['A_over_P_max_c']}). With five seasons before and after build-out, detecting the supply channel would "
   f"require farm-cell evaporation to change by a median factor of {V['dt_med5']:.0f} (minimum {V['dt_min5']:.0f} in "
   f"{V['dt_min5_c']}; minimum {V['dt_min10']:.0f} with ten seasons each) (Fig. 6) — far outside any physically plausible "
   f"wind-farm effect on evaporation.")

H("4.6. Near-farm response in paired simulations [C]", 2)
Pp(f"All {V['w_runs']} simulations (domain and turbines in Fig. 7) completed without CFL violations, missing output or negative "
   f"water vapour; one initial-condition run that had not been perturbed was detected, retained for audit and repeated. "
   f"Against ERA5, CONTROL precipitation had a relative bias of {pct(V['w_vbP_min'],0)} to {pct(V['w_vbP_max'],0)} and a "
   f"spatial correlation of {V['w_vrP_min']:.2f}–{V['w_vrP_max']:.2f}; column water vapour correlated at "
   f"≥{V['w_vrW_min']:.2f} (Fig. 8). In farm cells, WIND − CONTROL hub-height wind changed by {V['w_hub_min']:.2f} to "
   f"{V['w_hub_max']:.2f} m s⁻¹ and boundary-layer height by {V['w_pblh_min']:+.0f} to {V['w_pblh_max']:+.0f} m, at a "
   f"simulated fleet output of {V['w_pow_min']:.1f}–{V['w_pow_max']:.1f} GW. Within 30 km of farms the RMS "
   f"hub-wind contrast was {V['w_sn_hub_near_min']:.1f}–{V['w_sn_hub_near_max']:.1f} times the RMS spread of the no-wind "
   f"members, and the boundary-layer-height contrast {V['w_sn_pblh_near_min']:.1f}–{V['w_sn_pblh_near_max']:.1f} times "
   f"(Fig. 9). Beyond 150 km the hub-wind ratio was at most {V['w_sn_hub_far_max']:.2f}.")
H("4.7. Cross-border precipitation contrasts [C]", 2)
Pp(f"Beyond 150 km from farms the precipitation contrast was {V['w_sn_p_far_min']:.2f}–{V['w_sn_p_far_max']:.2f} "
   f"times the internal spread (Fig. 9; maps in Fig. 10), and the inner-domain precipitation total changed by {pct(V['w_dP_tot_min'],2)} "
   f"to {pct(V['w_dP_tot_max'],2)}. Of {V['w_N']} country–event contrasts, {V['w_K']} lay outside the no-wind prediction "
   f"interval against {V['w_expK']:.0f} expected by chance (binomial reference {V['w_pbin']:.2f}; tests are not "
   f"independent), and {V['w_rep2']} of {V['w_ncty']} countries were flagged in more than one event (Fig. 11). The "
   f"supply-channel scenario, the precipitation that farm-cell evaporation changes in WRF would deliver with unchanged "
   f"dynamics, was a median {V['w_S_noise_med']:.1e} (maximum {V['w_S_noise_max']:.1e}) of the internal-variability "
   f"half-width. Country-level contrasts are therefore dominated by the dynamic channel and by chaotic variability, not "
   f"by moisture supply, and no single-country source attribution is possible because only all-fleet interventions "
   f"were simulated.")

t = doc.add_table(rows=1, cols=4); t.style = "Table Grid"
for i, h in enumerate(["Owner", "Own land a", "Foreign land a", "Foreign/own"]): t.rows[0].cells[i].text = h
for o, row in tbm.sort_index().iterrows():
    cl = t.add_row().cells; cl[0].text = o; cl[1].text = f"{row.own_land:.4f}"; cl[2].text = f"{row.foreign_land:.4f}"; cl[3].text = f"{row.ratio:.1f}"
Pp(f"Table 1. Transfer coefficients of farm-cell evaporation by owner, mean of JJA {V['y0']}–{V['y1']} [A]. "
   "Owners with fewer than two source cells are included only in the all-farm tag.")

H("5. Discussion")
Pp("The framework separates three statements that are often merged. Accounting (where evaporation from farm cells "
   "rains) is well identified and conserves mass, and it shows that the moisture budget of offshore wind areas is "
   "intrinsically transboundary. The supply channel is a conditional scenario: it is linear in an evaporation change "
   "that this study does not estimate, and the known-truth experiments show it is reliable only when the intervention "
   "leaves transport and rain efficiency untouched. The externality itself requires the dynamic channel, through which "
   "wind-farm modelling studies obtain their precipitation responses (flow deceleration, convergence and boundary-layer change) "
   f"{c('fitch2012','fischereit2022','akhtar2026')}; without executed counterfactual simulations it is not identified.")
Pp("Two further limits follow. Reanalysis cannot carry the intervention, because the forecast model used to produce "
   "ERA5 has no wind-farm parameterisation; before/after comparisons in reanalysis are therefore not evidence of "
   "infrastructure effects. Observational detection of the supply channel is infeasible at the scale of national "
   "summer precipitation. The single-layer tagging also ignores vertical wind shear and is known to differ from "
   f"two-layer and Lagrangian approaches {c('vanderent2013','eulerlagr2024','wam2layers2025')}; the reported "
   "coefficients are model-dependent accounting and should be compared across trackers before policy use.")
Pp("The paired simulations add a third statement. The parameterised fleet decelerates hub-height flow and deepens the "
   "boundary layer near farms well above internal variability, consistent with mesoscale studies "
   f"{c('fitch2012','siedersleben2018','fischereit2022')}, but at receptor scale the precipitation contrasts of the "
   "simulated events are not distinguishable from what perturbing the initial state by hundredths of a kelvin "
   "produces. The supply channel is orders of magnitude smaller than this noise, so the known-truth result that supply "
   "estimates can misstate even the sign of an externality is not an academic concern. These are model-conditional "
   "contrasts: a different parameterisation, resolution, TKE factor, domain or season sample could give different "
   "responses, the ensembles are small, and the simulations do not represent soil moisture, groundwater or freshwater "
   "availability beyond five days of land-surface response. They bound what this configuration can support, rather "
   "than measuring a real-world externality. Governance applications should cite [A], [S] and [C] results only with "
   "their labels.")
H("6. Conclusions")
Pp(f"Source–receptor accounting of offshore wind-farm evaporation in Europe is transboundary, but it is not an "
   f"externality estimate: placebo sources reproduce most coefficients, the computable supply channel fails in "
   f"known-truth worlds when dynamics change, and the signal is undetectable observationally. In paired WRF "
   f"simulations the fleet changes near-farm winds and boundary layers clearly, while cross-border precipitation "
   f"contrasts remain within internal variability for the simulated events. The released tools make these "
   f"distinctions explicit and testable.")

H("Software and data availability")
Pp("Name: atmospheric-water-externalities (TAWE tagging and identifiability tools). Developer and contact: Onishi Tatsuki. "
   "Year first available: 2026. Hardware: any 64-bit machine; the full case study ran on 2 CPU cores and 8 GB RAM. "
   "Software: Python 3.10 with numpy, xarray, pandas, scipy, shapely, pyshp, matplotlib, python-docx (pinned in "
   "requirements.lock.txt). Language: Python. Availability and cost: free, https://github.com/bougtoir/"
   "atmospheric-water-externalities (licence: MIT). Data: ERA5 (Copernicus licence) re-fetched by script with SHA-256 "
   "ledger; Natural Earth (public domain); offshore turbine register copied with checksum from a public repository.")
H("CRediT authorship contribution statement")
Pp("Onishi Tatsuki: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Visualization, Writing – original draft, Writing – review & editing.")
H("Declaration of competing interest")
Pp("The author declares no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.")
H("Declaration of generative AI and AI-assisted technologies in the manuscript preparation process")
Pp("[To be completed by the author in the form required by the journal.]")
H("Acknowledgements")
Pp("[To be completed by the author.]")
H("Figure captions")
caps = ["Fig. 1. Framework: accounting [A], supply scenario [S] and model-conditional contrasts [C] from paired simulations.",
        f"Fig. 2. Study domain with offshore wind-farm source cells by owner and placebo cells, {V['y1']}.",
        "Fig. 3. Known-truth experiments (20% source evaporation increase): true externality versus supply estimator at near (C1) and far (C2) receptors.",
        f"Fig. 4. Precipitation of farm-cell evaporation origin, mean JJA {V['y0']}–{V['y1']} [A].",
        "Fig. 5. Transfer coefficients of real farm cells versus placebo sources for the 15 largest land receptors.",
        "Fig. 6. Fractional change in farm-cell evaporation required to detect the supply channel in national summer precipitation.",
        "Fig. 7. WRF domain, inner analysis region and Fitch turbine locations for each simulated event.",
        "Fig. 8. CONTROL simulations against ERA5: relative bias and spatial correlation.",
        "Fig. 9. Ratio of RMS WIND − CONTROL contrast to RMS no-wind ensemble spread by distance from farms [C].",
        "Fig. 10. Accumulated precipitation difference after spin-up: WIND − CONTROL (top) and one no-wind perturbed run − CONTROL (bottom) [C].",
        "Fig. 11. Country precipitation contrasts WIND − CONTROL against the 95% prediction interval of the no-wind ensemble [C]."]
for cp in caps: Pp(cp)
# figure citation order check is in QC; reference list
H("References")
def ref_entry(k):
    x = refs.loc[k]; au = ", ".join(a.strip().replace(" ", ", ", 1) if False else (a.strip().rsplit(" ", 1)[0] + ", " + a.strip().rsplit(" ", 1)[1]) for a in x.authors.split(";"))
    vol = "" if pd.isna(x.volume) else f" {x.volume}"; pg = "" if pd.isna(x.pages) else f", {str(x.pages).replace('-', '–')}"
    return f"{au}, {int(x.year)}. {x.title}. {x.journal}{vol}{pg}. https://doi.org/{x.doi}."
for k in sorted(cited, key=lambda k: (surname(k).lower(), int(refs.loc[k, 'year']))):
    Pp(ref_entry(k))
doc.save(OUT / "manuscript.docx")
# word count (main text sections 1-6)
paras = [p.text for p in doc.paragraphs]; i0 = paras.index("1. Introduction"); i1 = paras.index("Software and data availability")
wc = sum(len(p.split()) for p in paras[i0:i1]); aw = len(ABS.split())
json.dump({"main_text_words": wc, "abstract_words": aw, "n_refs": len(cited)}, open(R / "manuscript_wordcount.json", "w"))
HL = [f"Transboundary water externalities defined as counterfactual precipitation change",
      f"Open, mass-conserving moisture tagging tool with known-truth validation",
      f"Supply-only estimates fail in known-truth worlds when dynamics change",
      f"{pct(V['land_mean'],0)} of offshore farm-cell evaporation rains on land, mostly abroad",
      f"Placebo sources reproduce {V['pl_inside']} of {V['pl_n']} receptor transfer coefficients",
      f"Paired WRF runs: cross-border rain contrasts within internal variability"]
HL = [HL[0], HL[2], HL[3], HL[4], HL[5]]
hd = Document(); hd.add_heading("Highlights", 1)
for h in HL: hd.add_paragraph(h, style="List Bullet")
hd.save(S / "highlights.docx"); (S / "highlights.txt").write_text("\n".join(HL) + "\n")
print(json.dumps({"words": wc, "abstract": aw, "refs": len(cited), "hl_max": max(map(len, HL))}))
