"""Figures (separate files, results-driven). Outputs figures/Figure_<n>.png (600 dpi) and .pdf."""
import json, pathlib, sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tawe.tracking import grid_geometry
F = pathlib.Path("figures"); F.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans"})
M = np.load("data/processed/grid_masks.npz"); lat, lon, country = M["lat"], M["lon"], M["country"]
area, _, _ = grid_geometry(lat, lon); land = country != ""
years = sorted(int(p.stem.split("_")[1]) for p in pathlib.Path("data/processed").glob("track_*.npz"))
ext = [lon[0] - .125, lon[-1] + .125, lat[-1] - .125, lat[0] + .125]

def save(fig, n):
    fig.savefig(F / f"Figure_{n}.png", dpi=600, bbox_inches="tight"); fig.savefig(F / f"Figure_{n}.pdf", bbox_inches="tight"); plt.close(fig)

# Figure 1: framework schematic (accounting vs supply scenario vs dynamic counterfactual)
fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax.axis("off")
boxes = [(0.02, "ERA5 column budget\nW, F, E, P (hourly)"), (0.27, "Forward tagging\nfrom farm cells S\n[A] accounting a(S→c)"),
         (0.52, "Supply channel\nΔE_S · a(S→c)\n[S] scenario"), (0.77, "Dynamic channel\ncoupled counterfactual\n(WRF wind-farm scheme)\nNOT RUN")]
for x, t in boxes:
    ax.add_patch(plt.Rectangle((x, 0.3), 0.21, 0.45, fill=False, lw=1)); ax.text(x + 0.105, 0.525, t, ha="center", va="center")
for x in (0.23, 0.48, 0.73):
    ax.annotate("", (x + 0.04, 0.525), (x, 0.525), arrowprops=dict(arrowstyle="->"))
ax.text(0.5, 0.12, "TAWE(j→c) = Δ_supply + Δ_dynamic ;  validation: closure, analytic rain-out, placebo sources, known-truth worlds",
        ha="center"); save(fig, 1)

# Figure 2: domain, farm cells (latest year) by owner, placebo cells
yr = years[-1]; owner = M[f"owner_{yr}"]
fig, ax = plt.subplots(figsize=(6, 4.2))
ax.imshow(np.where(land, 0.85, 1.0), extent=ext, cmap="gray", vmin=0, vmax=1, aspect="auto")
for k, pm in enumerate(M[f"placebo_{yr}"]):
    ii, jj = np.nonzero(pm); ax.scatter(lon[jj], lat[ii], s=1.5, c="0.55", marker="s", label="placebo cells (5 sets)" if k == 0 else None)
pal = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:olive", "tab:cyan"]
for o, col in zip(sorted(set(owner[owner != ""])), pal):
    ii, jj = np.nonzero(owner == o); ax.scatter(lon[jj], lat[ii], s=5, c=col, marker="s", label=f"farm cells {o}")
ax.set_xlim(-8, 25); ax.set_ylim(48, 62); ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.legend(fontsize=6, ncol=2, loc="upper right"); ax.set_title(f"Offshore wind-farm source cells, {yr} (0.25°)"); save(fig, 2)

# Figure 3: known-truth experiments
kt = pd.read_csv("results/known_truth.csv")
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
for ax, c in zip(axs, ("C1", "C2")):
    s = kt[(kt.receptor == c) & (kt.dE_frac == kt.dE_frac.max())]
    lab = [f"δk={a:+.2f}\nδu={b:+.1f}" for a, b in zip(s.delta_k, s.delta_u)]
    x = np.arange(len(s)); ax.bar(x - 0.2, s.truth_kg / 1e9, 0.4, label="truth P(I)−P(no I)"); ax.bar(x + 0.2, s.supply_kg / 1e9, 0.4, label="supply estimator")
    ax.axhline(0, c="k", lw=0.5); ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=5); ax.set_title(f"Receptor {c} ({'near' if c=='C1' else 'far'})")
axs[0].set_ylabel("Δ precipitation (10⁹ kg)"); axs[0].legend(fontsize=6); save(fig, 3)

# Figure 4: mean tagged precipitation map (ALL tag), mm per season
P = np.mean([np.load(f"data/processed/track_{y}.npz")["P_tag"][list(np.load(f"data/processed/track_{y}.npz")["names"]).index("ALL")] for y in years], axis=0)
fig, ax = plt.subplots(figsize=(6, 4.2))
im = ax.imshow(np.log10(np.maximum(P, 1e-6)), extent=ext, cmap="viridis", vmin=-3, vmax=1, aspect="auto")
ax.contour(lon, lat, land.astype(float), [0.5], colors="w", linewidths=0.4)
plt.colorbar(im, ax=ax, label="log10 tagged precipitation (mm per JJA)"); ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.set_title(f"Precipitation of farm-cell evaporation origin, JJA mean {years[0]}–{years[-1]}"); save(fig, 4)

# Figure 5: real vs placebo transfer coefficients
pl = pd.read_csv("results/placebo_test.csv"); pl = pl[pl.receptor != "SEA"].sort_values("a_real_mean", ascending=False).head(15)
fig, ax = plt.subplots(figsize=(7.2, 2.8)); x = np.arange(len(pl))
ax.vlines(x, pl.a_placebo_min, pl.a_placebo_max, color="tab:gray", lw=4, label="placebo range (5 sets × seasons)")
ax.scatter(x, pl.a_real_mean, c="tab:red", zorder=3, s=12, label="farm cells (mean)")
ax.errorbar(x, pl.a_real_mean, yerr=[pl.a_real_mean - pl.a_real_min, pl.a_real_max - pl.a_real_mean], fmt="none", ecolor="tab:red", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(pl.receptor); ax.set_ylabel("a(S→c)"); ax.legend(fontsize=6); save(fig, 5)

# Figure 6: detectability
dt = pd.read_csv("results/detectability.csv"); pv = dt.pivot(index="receptor", columns="n_seasons_each", values="required_dE_frac").sort_values(5)
fig, ax = plt.subplots(figsize=(7.2, 2.8)); x = np.arange(len(pv))
for n in pv.columns: ax.scatter(x, pv[n], s=10, label=f"{n} seasons before/after")
ax.set_yscale("log"); ax.axhline(1, c="k", lw=0.5, ls="--"); ax.set_xticks(x); ax.set_xticklabels(pv.index, fontsize=6)
ax.set_ylabel("required ΔE_S / E_S for detection"); ax.legend(fontsize=6); save(fig, 6)
print("figures", sorted(p.name for p in F.glob("*.png")))
