# Figure repair audit (Gate 7)

All figures are regenerated from canonical result files by `scripts/g8_figures.py` (Figures 1–6), `scripts/g8b_wrf_figures.py` (WRF Figures W1–W5, submitted as Figures 7–11) and `scripts/g8_package.py` (graphical abstract). No figure was edited by hand. Each figure exists as vector PDF and 600-dpi PNG in `figures/`; the editable source is the generating script plus the canonical inputs listed below. `make figures wrf_figures package` rebuilds all of them.

| Figure | Defect found | Repair | Canonical inputs |
|---|---|---|---|
| 1 (framework) | Dynamic-channel box still read "NOT RUN" after the WRF programme was executed; box text overflowed the frames. | Box now reads "WRF WIND − CONTROL + no-wind ensemble, [C] model-conditional"; font reduced so text fits. | none (schematic) |
| 2 (source cells) | none | — | `data/processed/grid_masks.npz` |
| 3 (known truth) | none on re-inspection (bars, zero line, receptor labels, δk/δu ticks legible). | — | `results/known_truth.csv` |
| 4 (tagged precipitation map) | Tagged precipitation was plotted in kg per grid cell while labelled mm, so every cell exceeded the colour-scale maximum and the map was uniformly saturated. | Divide by cell area (kg m⁻² = mm); colour range set from the data maximum over four decades. | `data/processed/track_*.npz` |
| 5 (placebo) | none | — | `results/placebo_test.csv`, `results/source_receptor.csv` |
| 6 (detectability) | none | — | `results/detectability.csv` |
| 7 (WRF domain, turbines) | Turbine coordinates were read from ignored `wrf_runs/`, so a public clone could not rebuild the figure; e2016w and e2016sw (identical inventories) were drawn on top of each other with two legend entries, hiding one. | Turbine tables copied to `results/wrf/<case>/windturbines.txt` and `wind-turbine-*.tbl`; identical inventories merged into one legend entry ("e2016sw = e2016w"). | `results/wrf/*/windturbines.txt`, `wrf_config/` |
| 8 (CONTROL vs ERA5) | Relative bias of northward IVT (domain mean near zero, sign-changing) reached ~3 and dominated the panel; raw variable names on the axis. | Relative bias shown only for fields with a well-defined positive mean; panel title states it is undefined for northward IVT; readable field names. | `results/wrf/*/validation.json` |
| 9 (signal/noise by distance) | raw variable names in panel titles | readable names | `results/wrf/*/signal_noise.json` |
| 10 (precipitation maps) | none | — | `results/wrf/*/maps.nc` |
| 11 (country contrasts) | panel titles overlapped tick labels; no legend distinguishing contrasts outside the interval | larger vertical spacing; inside/outside legend | `results/wrf/*/country_signal_noise.csv` |
| Graphical abstract | Values were stale (4 events, "5/60") because `g8_package.py` was not in the rebuild chain; text overflowed the last box. | Added `package` and `wrf_figures` targets to `make all`; text wrapped. | `results/manuscript_values.json` |
