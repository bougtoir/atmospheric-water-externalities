# Turbine inventory audit (revision, Gate 2)

**Defect found.** `data/raw/turbines_from_ecm_wind_heatwave.csv` (SHA-256 `6b67b848…7948`) stacks two
national registries on top of the European Wind Watch (`eww`) layer for the same offshore turbines:

| country | source | offshore MW commissioned before 2020-06-30 | n |
|---|---|---|---|
| DE | eww | 7389.8 | 1467 |
| DE | mastr | 7867.7 | 1498 |
| DK | eww | 1673.7 | 554 |
| DK | dk_stamdata | 1459.6 | 499 |

Nearest-neighbour distance from each `mastr` / `dk_stamdata` offshore turbine to the closest `eww` turbine
has median 12 m / 4 m; 86 % / 98 % lie within 0.5 km. The rows are therefore duplicates of the same
physical turbines, and a naive sum gives 15.3 GW for DE in mid-2020 instead of roughly 7.5 GW.

**Effect on WRF.** The first draft of `scripts/wrf/w2_turbines.py` would have placed each DE/DK turbine
twice in the Fitch input (30.7 GW instead of 21.3 GW). The defect was found before any WIND run.
The fix keeps a single source (`SOURCE = "eww"`) for every country. The resulting fleet for 2020-06-30
inside the WRF domain is 4,825 turbines and 21.3 GW (`windfarm_summary.json` in each WIND run).

**Effect on v1 ERA5 tagging ([A]/[S]).** The v1 source masks are presence masks at 0.25°, so
duplicates do not change mask values. The national registries add 4–5 cells per year (out of 77–108)
that have no `eww` turbine. They are kept in v1 and are disclosed as a mask-definition sensitivity.
Capacity sums are used only to assign a cell's owning country, and both sources agree on the
country, so the v1 country labels are unchanged.

**Remaining inventory limits.** 89 `eww` offshore turbines have no commissioning date and are
excluded. Hub height and rotor diameter are filled with the median of their rated-power class.
Power and thrust curves are idealised and generic (see `w2_turbines.py`), not manufacturer curves.
