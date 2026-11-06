# WRF experiment plan (Gate 2)

Estimand class **[C]**: a model-conditional intervention contrast \(\Delta X = X(\text{WIND}) - X(\text{CONTROL})\)
inside one fixed WRF configuration driven by ERA5. It is not an observed real-world causal effect, and
the WRF output is not a ground truth.

## Model
- WRF-ARW v4.6.1 with WPS v4.6.0, built from source on this VM (gfortran 11, MPICH, NetCDF; dmpar; LTO
  disabled because of link-time memory). Build logs are in the private archive.
- Single domain. Lambert projection with ref 54°N 8°E and true latitudes 50°/58°N. dx = 15 km, 141 × 111
  cells (about 46–61°N, 11°W–27°E). 45 hybrid levels (`hybrid_opt=2`), p_top = 50 hPa, dt = 60 s.
- Physics: Thompson microphysics (`mp=8`), RRTMG LW/SW (`radt=15`), MYNN 2.5 PBL with MYNN surface layer
  (`bl=5`, `sfclay=5`; the Fitch scheme requires MYNN), Noah LSM, Kain–Fritsch cumulus (`cu=1`, needed at
  15 km), gravity-wave drag on, 6th-order diffusion, Rayleigh damping above 5 km below the top
  (`damp_opt=3`).
- Forcing: ERA5 at 0.25° every 3 h on 37 pressure levels plus surface and 4 soil layers, read from ARCO
  ERA5 (`scripts/wrf/w1_fetch_forcing.py`). The data go through a direct NetCDF→WPS-intermediate writer
  (`w3_era5_to_intermediate.py`) because ungrib needs GRIB. LANDSEA is made binary at 0.5, SST over land
  is filled from skin temperature, and RH is diagnosed from q and T. `metgrid` acceptance and the
  `wrfinput` range checks are recorded in `WRF_PILOT_NUMERIC_QC.md`.
- Lateral boundaries: specified, 5-cell relaxation zone, updated every 3 h. No nudging.
- Spin-up: the first 24 h of every run are excluded from all diagnostics.

## Experiments (identical except for the intervention)
| name | intervention |
|---|---|
| CONTROL | `windfarm_opt=0` |
| WIND | `windfarm_opt=1`, Fitch (2012) momentum sink + TKE source (`windfarm_tke_factor=0.25`) for all offshore `eww` turbines commissioned before the run start (2020 pilot: 4,825 turbines, 21.3 GW) |
| WIND_<ISO> | as WIND but only the turbines of one country, so the intervention is isolated (attribution by isolated intervention, not by apportioning) |
| CTLPERT_k | CONTROL with a seeded 0.01 K i.i.d. perturbation of T in the lowest 10 levels of `wrfinput` (`w4b_perturb_ic.py`). Gives the chaotic-noise reference against which WIND−CONTROL is judged |

The turbine inventory and the idealised power/thrust curves are documented in
`TURBINE_INVENTORY_AUDIT.md` and `scripts/wrf/w2_turbines.py`. Fixing the inventory double-counting
before the first WIND run changed the fleet from 30.7 GW to 21.3 GW.

## Event selection (fixed before any WRF run; no treatment information used)
`scripts/wrf/w0_select_events.py` writes `results/wrf_event_selection.json`. The script ranks
non-overlapping 5-day JJA 2016–2021 windows by mean eastward integrated vapour flux across the North Sea
gate (3–8°E, 52–57°N). A window must also have central-European precipitation above the JJA median. The
selection takes the top westerly windows plus the best windows with positive and negative mean northward
flux. Each run covers the window plus one spin-up day before it and one day after it (7 days → 144 h of
integration including spin-up).

## Order and stopping rules
1. Pilot (2020-07-01..05, westerly): CONTROL and WIND. Numeric QC must pass before anything else runs.
2. Noise reference: CTLPERT_1 for the pilot. A WIND−CONTROL field is called distinguishable from
   noise only where it exceeds the CTLPERT−CONTROL spread. With one member this is a screening statement,
   not a significance test.
3. The remaining 4 events: CONTROL and WIND.
4. Country-isolated runs (largest fleets: GB, DE) for the pilot event, only if step 2 shows that
   WIND−CONTROL precipitation over land exceeds the noise level.
5. Sensitivity (if compute allows): `windfarm_tke_factor` 0.25 → 1.0, and cu off.
