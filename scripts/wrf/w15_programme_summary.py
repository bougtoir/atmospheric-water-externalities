"""Programme-level WRF registry and summary (Gate 4) rendered from canonical per-case outputs — no hand-typed values.

Reads wrf_runs/CASE/logs/{status,timing}.txt, results/wrf/CASE/{qc,validation,signal_noise,paired}.json,
results/wrf/CASE/country_signal_noise.csv and the private-archive manifest copy docs/revision/DATA_ARCHIVE_MANIFEST.csv.
Writes docs/revision/WRF_EXPERIMENT_REGISTRY.csv, results/wrf/programme_summary.json,
results/wrf/programme_country.csv, docs/revision/WRF_MAIN_EXPERIMENT_REPORT.md, docs/revision/WRF_VALIDATION_REPORT.md.
All contrasts are model-conditional WIND - CONTROL differences in one WRF configuration (evidence class [C]).
"""
import csv, glob, json, os
import pandas as pd
from scipy.stats import binom

EV = json.load(open("results/wrf_event_selection.json"))["events"]
CASES = sorted(d.split("/")[-1] for d in glob.glob("wrf_runs/*") if os.path.exists(f"{d}/logs/status.txt"))
_AM = os.path.expanduser("~/archive/tawe-private-research-data/DATA_ARCHIVE_MANIFEST.csv")
MAN = list(csv.DictReader(open(_AM if os.path.exists(_AM) else "docs/revision/DATA_ARCHIVE_MANIFEST.csv")))
PI_LEVEL = 0.95


def event_of(case):
    import re, datetime as dt
    nl = glob.glob(f"wrf_runs/{case}/*/namelist.input")
    if not nl:
        return {}
    m = re.search(r"start_year\s*=\s*(\d+),\s*start_month\s*=\s*(\d+),\s*start_day\s*=\s*(\d+)", open(nl[0]).read())
    start = (dt.date(*map(int, m.groups())) + dt.timedelta(days=1)).isoformat()  # forcing starts 1 day early
    return next((e for e in EV if e["start"] == start), {})


def qc_pass(q):
    return bool(q["success"] and q["history_frames"] == q["history_frames_expected"] and q["nonfinite_qvapor"] == 0
                and q["negative_qvapor"] == 0 and q["precip_monotone"] and q["cfl_messages"] == 0)


reg = []
for c in CASES:
    status = {}
    for line in open(f"wrf_runs/{c}/logs/status.txt"):
        p = line.split(maxsplit=1)
        if len(p) == 2:
            x = p[0]
            if "INVALID" in p[1]:
                x = next((os.path.basename(d) for d in glob.glob(f"wrf_runs/{c}/{x}_INVALID*")), x + "_INVALID")
            status[x] = p[1].strip()
    wall = {}
    if os.path.exists(f"wrf_runs/{c}/logs/timing.txt"):
        for line in open(f"wrf_runs/{c}/logs/timing.txt"):
            p = line.split()
            if len(p) == 3 and p[1] == "wallclock_s":
                wall[p[0]] = int(p[2])
    qc = json.load(open(f"results/wrf/{c}/qc.json")) if os.path.exists(f"results/wrf/{c}/qc.json") else {}
    ev = event_of(c)
    for x, st in status.items():
        rb = [r for r in MAN if r["dataset_id"] == f"wrf_{c}_{x}"]
        reg.append(dict(case=c, experiment=x, regime=ev.get("regime", ""), event_start=ev.get("start", ""),
                        event_end=ev.get("end", ""), windfarm_opt=1 if x == "WIND" else 0,
                        ic_perturbed=x.startswith("CTLPERT"), status=st, valid="INVALID" not in st,
                        wallclock_s=wall.get(x, ""), qc_pass=qc_pass(qc[x]) if x in qc else "",
                        archive_objects=len(rb),
                        archive_readback_verified=bool(rb) and all("read-back verified" in r["archive_status"] for r in rb)))
pd.DataFrame(reg).to_csv("docs/revision/WRF_EXPERIMENT_REGISTRY.csv", index=False)

# public copy of the run configuration needed downstream (wrf_runs/ is not in the public repository)
import re as _re
for c in CASES:
    tl, nl = f"wrf_runs/{c}/logs/turbines_WIND.log", glob.glob(f"wrf_runs/{c}/WIND/namelist.input")
    if os.path.exists(tl) and nl and os.path.isdir(f"results/wrf/{c}"):
        txt = open(tl).read()  # w4 keeps the first 600 characters of the generator log; header fields are complete
        inv = {k: json.loads(_re.search(rf'"{k}": ([^,]+),', txt).group(1)) for k in ("date", "countries", "n_turbines", "capacity_mw")}
        n = open(nl[0]).read()
        keys = ["dx", "e_we", "e_sn", "e_vert", "time_step", "p_top_requested", "mp_physics", "ra_lw_physics", "ra_sw_physics",
                "sf_sfclay_physics", "sf_surface_physics", "bl_pbl_physics", "cu_physics", "windfarm_opt", "windfarm_tke_factor"]
        cfg = {k: float(_re.search(rf"\b{k}\s*=\s*([\d.]+)", n).group(1)) for k in keys}
        json.dump(dict(case=c, namelist_WIND=cfg, turbines=inv), open(f"results/wrf/{c}/run_config.json", "w"), indent=1)

BANDS = ["farm_0_30km", "near_30_150km", "far_gt150km"]
FIELDS = ["hub_wind", "PBLH", "E_acc_mm", "P_acc_mm", "IVTx", "W", "T2"]
cases, ctry = {}, []
for c in CASES:
    f = f"results/wrf/{c}/signal_noise.json"
    if not os.path.exists(f):
        continue
    sn = json.load(open(f))
    if sn["n_no_wind_ensemble"] < 4:
        continue
    k, n = sn["n_outside_internal_variability"], sn["n_countries"]
    pr = json.load(open(f"results/wrf/{c}/paired.json"))["paired"]["WIND"]
    cases[c] = dict(regime=event_of(c).get("regime", ""), n_no_wind_ensemble=sn["n_no_wind_ensemble"], n_countries=n,
                    n_outside=k, expected_outside=n * (1 - PI_LEVEL), p_binom_ge=float(binom.sf(k - 1, n, 1 - PI_LEVEL)),
                    ratios={fl: {b: sn["fields"][fl][b]["ratio"] for b in BANDS} for fl in FIELDS if fl in sn["fields"]},
                    dP_inner_total_pct=100 * pr["P_inner_total_kg"]["diff"] / pr["P_inner_total_kg"]["control"],
                    mean_power_GW=pr.get("mean_power_GW"))
    d = pd.read_csv(f"results/wrf/{c}/country_signal_noise.csv"); d["case"] = c; ctry.append(d)

K = sum(v["n_outside"] for v in cases.values()); N = sum(v["n_countries"] for v in cases.values())
pool = dict(n_cases=len(cases), n_tests=N, n_outside=K, expected_outside=N * (1 - PI_LEVEL),
            p_binom_ge=float(binom.sf(K - 1, N, 1 - PI_LEVEL)) if N else None, pi_level=PI_LEVEL,
            note="Tests are not independent (countries share weather); the binomial reference is a calibration aid only.")
cs = pd.DataFrame()
if ctry:
    a = pd.concat(ctry)
    cs = a.groupby("country").agg(n_cases=("case", "nunique"), n_outside=("outside_internal_variability", "sum"),
                                  n_positive=("dP_wind_kg", lambda s: int((s > 0).sum())),
                                  mean_z=("z", "mean"), max_abs_z=("z", lambda s: float(s.abs().max()))).reset_index()
    cs["sign_consistent"] = (cs.n_positive == 0) | (cs.n_positive == cs.n_cases)
    cs.to_csv("results/wrf/programme_country.csv", index=False)
json.dump(dict(cases=cases, pooled=pool), open("results/wrf/programme_summary.json", "w"), indent=1)

R = pd.DataFrame(reg)
L = ["# WRF main experiment report (Gate 4)", "",
     "Generated by `scripts/wrf/w15_programme_summary.py` from canonical per-case outputs in `results/wrf/`.",
     "Every number is a model-conditional WIND − CONTROL contrast in one WRF v4.6.1 configuration (Fitch wind-farm",
     "parameterisation, 15 km, ERA5 boundaries; evidence class [C]). It is not an observed real-world causal effect,",
     "and WRF output is not treated as ground truth.", "",
     f"Experiments registered: {len(R)} ({int(R.valid.sum())} valid, {int((~R.valid).sum())} invalid and retained for audit);"
     f" events with a complete no-wind ensemble (CONTROL + CTLPERT_1..3): {len(cases)}.", "",
     "## Internal-variability test per event", "",
     f"A country is flagged when WIND − CONTROL precipitation lies outside the {int(PI_LEVEL*100)} % prediction interval",
     "of the no-wind ensemble (n = 4). Under no effect about 5 % of countries are expected outside by chance.", "",
     "| case | regime | countries | outside | expected | P(X ≥ outside) | ΔP inner total (%) | mean power (GW) |",
     "|---|---|---|---|---|---|---|---|"]
for c, v in cases.items():
    L.append(f"| {c} | {v['regime']} | {v['n_countries']} | {v['n_outside']} | {v['expected_outside']:.2g} | "
             f"{v['p_binom_ge']:.3g} | {v['dP_inner_total_pct']:.3g} | {v['mean_power_GW']:.4g} |")
if N:
    L += ["", f"Pooled: {K}/{N} country-event tests outside (expected {pool['expected_outside']:.3g}; binomial "
          f"P(X ≥ {K}) = {pool['p_binom_ge']:.3g}). {pool['note']}"]
L += ["", "## Signal-to-noise ratio by distance from the nearest farm cell", "",
      "RMS(WIND − CONTROL) / RMS(CTLPERT − CONTROL) over cells in each band; ≈1 means indistinguishable from internal variability.", "",
      "| case | field | 0–30 km | 30–150 km | >150 km |", "|---|---|---|---|---|"]
for c, v in cases.items():
    for fl, r in v["ratios"].items():
        L.append(f"| {c} | {fl} | " + " | ".join(f"{r[b]:.3g}" for b in BANDS) + " |")
if len(cs):
    L += ["", "## Country consistency across events", "",
          f"Countries flagged in more than one event: {int((cs.n_outside > 1).sum())}; countries with the same sign of ΔP in "
          f"every event: {int(cs.sign_consistent.sum())}/{len(cs)}. Full table: `results/wrf/programme_country.csv`.", "",
          "| country | events | flagged | ΔP>0 events | mean z | max |z| |", "|---|---|---|---|---|---|"]
    L += [f"| {r.country} | {r.n_cases} | {int(r.n_outside)} | {r.n_positive} | {r.mean_z:.2g} | {r.max_abs_z:.2g} |"
          for r in cs.sort_values("max_abs_z", ascending=False).itertuples()]
open("docs/revision/WRF_MAIN_EXPERIMENT_REPORT.md", "w").write("\n".join(L) + "\n")

V = ["# WRF validation report (Gate 4)", "", "Generated by `scripts/wrf/w15_programme_summary.py`.", "",
     "## Numerical QC (all experiments)", "",
     "Pass rule: SUCCESS COMPLETE WRF, all history frames, no non-finite/negative QVAPOR, monotone accumulated",
     "precipitation, no CFL messages. Per-case detail: `docs/revision/wrf_cases/*_NUMERIC_QC.md`.", "",
     "| case | experiment | status | QC | wall-clock (s) | archive objects | read-back verified |", "|---|---|---|---|---|---|---|"]
V += [f"| {r.case} | {r.experiment} | {r.status} | {r.qc_pass} | {r.wallclock_s} | {r.archive_objects} | {r.archive_readback_verified} |"
      for r in R.itertuples()]
V += ["", "## CONTROL against the driving reanalysis (ERA5), analysis window, inner domain", "",
      "ERA5 is itself a model product; agreement is a plausibility check, not validation against truth.", "",
      "| case | field | WRF mean | ERA5 mean | relative bias | RMSE | spatial r |", "|---|---|---|---|---|---|---|"]
for c in CASES:
    f = f"results/wrf/{c}/validation.json"
    if os.path.exists(f):
        for fl, s in json.load(open(f))["fields"].items():
            V.append(f"| {c} | {fl} | {s['wrf_mean']:.4g} | {s['era5_mean']:.4g} | {s['rel_bias']:.3g} | {s['rmse']:.4g} | {s['spatial_r']:.3g} |")
open("docs/revision/WRF_VALIDATION_REPORT.md", "w").write("\n".join(V) + "\n")
print("cases", list(cases), "pooled", K, N)
