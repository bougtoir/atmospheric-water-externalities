"""Gate 6: European JJA case study from tracking outputs (accounting [A], placebo falsification, detectability).

Reads data/processed/track_<yr>.npz, grid_masks.npz; writes results/source_receptor.csv, results/placebo_test.csv,
results/transboundary_share.csv, results/detectability.csv.
"""
import json, pathlib, numpy as np, pandas as pd
from scipy import stats
M = np.load("data/processed/grid_masks.npz"); country = M["country"]
import sys; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tawe.tracking import grid_geometry
area, _, _ = grid_geometry(M["lat"], M["lon"])
years = sorted(int(p.stem.split("_")[1]) for p in pathlib.Path("data/processed").glob("track_*.npz"))
PARTIAL = set(json.load(open("data/processed/grid_masks_log.json"))["receptors_partly_outside_domain"])
codes = sorted(set(country.ravel()) - {""})
rows, tot = [], []
for yr in years:
    d = np.load(f"data/processed/track_{yr}.npz"); b = json.load(open(f"results/track_budget_{yr}.json"))
    for k, name in enumerate(d["names"]):
        Pt = d["P_tag"][k]; Es = b["budget_kg"]["E_src"][k]
        rec = {c: float(Pt[country == c].sum()) for c in codes}
        rec["SEA"] = float(Pt[country == ""].sum())
        for c, v in rec.items():
            rows.append(dict(year=yr, tag=str(name), receptor=c, P_tag_kg=v, E_src_kg=Es, a=v / Es,
                             outflow_frac=b["budget_kg"]["outflow"][k] / Es, storage_frac=b["storage_end_kg"][k] / Es,
                             closure_rel=b["closure_rel"][k]))
    for c in codes:
        tot.append(dict(year=yr, receptor=c, P_total_kg=float((d["P_total"] * area)[country == c].sum())))
sr = pd.DataFrame(rows); sr.to_csv("results/source_receptor.csv", index=False)
pt = pd.DataFrame(tot)
# transboundary share: owner tags, fraction of source evaporation precipitating over land outside the owner
tb = []
for (yr, tag), g in sr[sr.tag.str.startswith("owner_")].groupby(["year", "tag"]):
    o = tag.split("_")[1]; land = g[g.receptor != "SEA"]
    tb.append(dict(year=yr, owner=o, own_land=land[land.receptor == o].a.sum(), foreign_land=land[land.receptor != o].a.sum(),
                   sea=g[g.receptor == "SEA"].a.sum(), outflow=g.outflow_frac.iloc[0], storage=g.storage_frac.iloc[0]))
tb = pd.DataFrame(tb); tb.to_csv("results/transboundary_share.csv", index=False)
# placebo test on ALL tag: per receptor, real a vs placebo distribution (pooled over years)
land_c = [c for c in codes if c not in PARTIAL and sr[(sr.tag == "ALL") & (sr.receptor == c)].a.mean() > 1e-3]
sr["receptor_partly_outside_domain"] = sr.receptor.isin(PARTIAL); sr.to_csv("results/source_receptor.csv", index=False)
pl = []
for c in land_c + ["SEA"]:
    s = sr[sr.receptor == c]
    real = s[s.tag == "ALL"].set_index("year").a
    plac = s[s.tag.str.startswith("placebo_")].pivot(index="year", columns="tag", values="a")
    diff = real.values[:, None] - plac.values
    rank = float((real.values[:, None] > plac.values).mean())
    pl.append(dict(receptor=c, a_real_mean=real.mean(), a_real_min=real.min(), a_real_max=real.max(),
                   a_placebo_mean=plac.values.mean(), a_placebo_min=plac.values.min(), a_placebo_max=plac.values.max(),
                   frac_placebo_below_real=rank, real_inside_placebo_range=bool(plac.values.min() <= real.mean() <= plac.values.max()),
                   interannual_sd_real=real.std(ddof=1) if len(real) > 1 else np.nan,
                   real_minus_placebo_sd=np.std(diff, ddof=1)))
pl = pd.DataFrame(pl); pl.to_csv("results/placebo_test.csv", index=False)
# detectability: supply-channel signal per unit fractional increase of farm-cell evaporation vs interannual SD of
# receptor JJA precipitation; two-sample before/after design with n seasons each, alpha=0.05 two-sided, power 0.8
z = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
dt = []
for c in land_c:
    sd = pt[pt.receptor == c].P_total_kg.std(ddof=1); mean = pt[pt.receptor == c].P_total_kg.mean()
    A = sr[(sr.tag == "ALL") & (sr.receptor == c)].P_tag_kg.mean()
    for n in (3, 5, 10):
        mde = z * sd * np.sqrt(2 / n)
        dt.append(dict(receptor=c, n_seasons_each=n, P_JJA_mean_kg=mean, P_JJA_sd_kg=sd, A_ALL_kg=A,
                       A_over_P=A / mean, mde_kg=mde, required_dE_frac=mde / A))
dt = pd.DataFrame(dt); dt.to_csv("results/detectability.csv", index=False)
pd.set_option("display.width", 220)
print(tb.groupby("owner")[["own_land", "foreign_land", "sea", "outflow"]].mean().round(4))
print(pl.round(4).to_string()); print(dt[dt.n_seasons_each == 5].round(4).to_string())
