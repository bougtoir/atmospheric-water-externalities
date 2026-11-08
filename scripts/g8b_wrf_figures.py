"""WRF figures (separate files, regenerated from results/wrf/*/ and run configuration files; no hand-typed values).

Outputs figures/wrf/Figure_W<n>.{png,pdf}. Contrasts are model-conditional WRF v4.6.1 WIND-CONTROL differences."""
import glob, json, os, pathlib, re
import numpy as np, pandas as pd, xarray as xr, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

F = pathlib.Path("figures/wrf"); F.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 8, "font.family": "DejaVu Sans"})
cases = sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob("results/wrf/*/maps.nc"))
def save(fig, n):
    fig.savefig(F / f"Figure_W{n}.png", dpi=600, bbox_inches="tight"); fig.savefig(F / f"Figure_W{n}.pdf", bbox_inches="tight"); plt.close(fig)
mp = {c: xr.open_dataset(f"results/wrf/{c}/maps.nc") for c in cases}
members = {c: sorted({m.group(1) for v in mp[c].data_vars if (m := re.match(r"P_acc_mm_(CTLPERT_\d+)$", v))}) for c in cases}

# W1: domain, inner analysis region and turbine locations per case
m0 = mp[cases[0]]; lat, lon = m0.lat.values, m0.lon.values
fig, ax = plt.subplots(figsize=(6, 4.6))
ax.contourf(lon, lat, (m0.country.values != "").astype(float) if m0.country.dtype.kind in "OUS" else (m0.country.values > 0).astype(float),
            levels=[-.5, .5, 1.5], colors=["#dfefff", "#e8e8e8"])
ax.contour(lon, lat, m0.inner.values.astype(float), levels=[.5], colors="k", linewidths=.8, linestyles="--")
ax.plot(np.r_[lon[0], lon[:, -1], lon[-1, ::-1], lon[::-1, 0]], np.r_[lat[0], lat[:, -1], lat[-1, ::-1], lat[::-1, 0]], "k-", lw=1)
tl = {c: np.loadtxt(f"wrf_runs/{c}/WIND/windturbines.txt") for c in cases if os.path.exists(f"wrf_runs/{c}/WIND/windturbines.txt")}
col = dict(zip(cases, plt.cm.tab10.colors))
for c in sorted(tl, key=lambda c: -len(tl[c])):  # largest fleet first so smaller fleets stay visible
    ax.scatter(tl[c][:, 1], tl[c][:, 0], s=.6, color=col[c], label=f"{c}: {len(tl[c])} turbines")
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)"); ax.legend(markerscale=12, fontsize=6, loc="upper left")
ax.set_title("WRF domain (15 km), inner analysis region (dashed) and Fitch turbines"); save(fig, 1)

# W2: precipitation contrast maps, WIND-CONTROL and first noise member minus CONTROL
nc = len(cases); fig, axs = plt.subplots(2, nc, figsize=(2.6 * nc, 4.6), squeeze=False)
for k, c in enumerate(cases):
    m = mp[c]; ref = m.P_acc_mm_CONTROL.values
    rows = [("WIND", m.P_acc_mm_WIND.values - ref)]
    rows.append((members[c][0], m[f"P_acc_mm_{members[c][0]}"].values - ref) if members[c] else ("no noise member", np.full_like(ref, np.nan)))
    for r, (nm, d) in enumerate(rows):
        a = axs[r, k]; im = a.pcolormesh(lon, lat, d, cmap="BrBG", vmin=-10, vmax=10, shading="auto")
        a.contour(lon, lat, m.farm.values.astype(float), levels=[.5], colors="m", linewidths=.5)
        a.set_title(f"{c}\n{nm} − CONTROL", fontsize=7); a.set_xticks([]); a.set_yticks([])
fig.colorbar(im, ax=axs, shrink=.7, label="Δ accumulated precipitation (mm, post-spin-up)"); save(fig, 2)

# W3: RMS(WIND-CONTROL)/RMS(noise-CONTROL) by distance band
sn = {c: json.load(open(f"results/wrf/{c}/signal_noise.json")) for c in cases if os.path.exists(f"results/wrf/{c}/signal_noise.json")}
fl = ["hub_wind", "PBLH", "IVTx", "E_acc_mm", "P_acc_mm"]; bands = ["farm_0_30km", "near_30_150km", "far_gt150km"]
fig, axs = plt.subplots(1, len(fl), figsize=(8.0, 2.6), sharey=True)
for a, f in zip(axs, fl):
    for c, col in zip(cases, plt.cm.tab10.colors):
        if c in sn and f in sn[c]["fields"]:
            a.plot(range(3), [sn[c]["fields"][f][b]["ratio"] for b in bands], "o-", color=col, label=c, ms=3)
    a.axhline(1, color="k", lw=.6, ls=":"); a.set_xticks(range(3)); a.set_xticklabels(["0–30", "30–150", ">150"], fontsize=6, rotation=30)
    a.set_title(f, fontsize=7); a.set_yscale("log"); a.set_xlabel("km from farm")
axs[0].set_ylabel("RMS signal / RMS noise"); axs[-1].legend(fontsize=5); save(fig, 3)

# W4: country precipitation contrast vs no-wind ensemble prediction interval
fig, axs = plt.subplots(len(cases), 1, figsize=(7.2, 1.8 * len(cases)), squeeze=False)
for a, c in zip(axs[:, 0], cases):
    p = f"results/wrf/{c}/country_signal_noise.csv"
    if not os.path.exists(p) or "pi_halfwidth_kg" not in open(p).readline(): a.set_title(f"{c}: no-wind ensemble not yet available", fontsize=7); a.axis("off"); continue
    d = pd.read_csv(p).sort_values("country"); x = np.arange(len(d))
    a.errorbar(x, d.ens_mean_minus_control_kg / 1e9, yerr=d.pi_halfwidth_kg / 1e9, fmt="none", ecolor="0.6", capsize=1.5,
               label="no-wind ensemble 95% prediction interval")
    a.scatter(x, d.dP_wind_kg / 1e9, s=8, c=np.where(d.outside_internal_variability, "r", "k"), zorder=3, label="WIND − CONTROL")
    a.axhline(0, color="k", lw=.5); a.set_xticks(x); a.set_xticklabels(d.country, fontsize=6); a.set_ylabel("ΔP (Mt)")
    a.set_title(f"{c} (n = {json.load(open(f'results/wrf/{c}/signal_noise.json'))['n_no_wind_ensemble']} no-wind runs)", fontsize=7)
axs[0, 0].legend(fontsize=6); save(fig, 4)

# W5: CONTROL vs ERA5 (driving reanalysis) relative bias and spatial correlation
va = {c: json.load(open(f"results/wrf/{c}/validation.json")) for c in cases if os.path.exists(f"results/wrf/{c}/validation.json")}
vf = sorted({f for v in va.values() for f in v["fields"]})
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.6))
for i, c in enumerate(va):
    w = .8 / len(va)
    axs[0].bar(np.arange(len(vf)) + i * w, [va[c]["fields"].get(f, {}).get("rel_bias", np.nan) for f in vf], w, label=c)
    axs[1].bar(np.arange(len(vf)) + i * w, [va[c]["fields"].get(f, {}).get("spatial_r", np.nan) for f in vf], w)
for a, t in zip(axs, ["relative bias vs ERA5", "spatial correlation vs ERA5"]):
    a.set_xticks(np.arange(len(vf)) + .4 - .4 / len(va)); a.set_xticklabels(vf, rotation=45, fontsize=6); a.set_title(t, fontsize=7); a.axhline(0, color="k", lw=.5)
axs[0].legend(fontsize=5); save(fig, 5)
import shutil
for w, n in {1: 7, 5: 8, 3: 9, 2: 10, 4: 11}.items():  # manuscript numbering = order of first citation
    for ext in ("png", "pdf"):
        shutil.copyfile(F / f"Figure_W{w}.{ext}", pathlib.Path("figures") / f"Figure_{n}.{ext}")
print("wrote", sorted(p.name for p in F.glob("*.png")), cases)
