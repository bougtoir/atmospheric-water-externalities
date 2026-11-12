# Fresh-environment restoration audit (Gate 10)

Date: 2026-11-09 (UTC). Directory `~/fresh_vm`, separate from the working checkout; nothing was copied from the working tree.

## Procedure
1. `git clone` of the public repository `bougtoir/atmospheric-water-externalities`, branch `devin/1793925965-tawe-wrf-revision` (commit 6bb927b; the four non-e2021nw `maps.nc` files were then taken from daa22b4, which first published them).
2. New `.venv`, `pip install -r requirements.txt` → exit 0.
3. Separate clone of the private archive (`GIT_LFS_SKIP_SMUDGE=1`) and `archive/restore_project_data.py` for the inputs the public pipeline needs (ERA5 column budget JJA 2016–2021, boundaries, turbine register): **73/73 objects SHA-256 verified**. Nothing was downloaded again from ECMWF/CDS or other providers.
4. Full public pipeline: `make test masks track known_truth numerics case figures wrf_figures report manuscript package qc`.
5. WRF archived-output check: 84 objects for event e2021nw (wrfout/wrfsfc/namelists/rsl/turbine tables, 6.76 GB) fetched from LFS. All **84/84 objects matched SHA-256** and were placed in `wrf_runs/e2021nw/`. The committed e2021nw results were then deleted, and `w5_analyse_case.py`, `w9_validate_control.py` and `w10_signal_noise.py` were rerun.
6. Configuration check: the e2021nw CONTROL, WIND and CTLPERT_1 namelists were rendered from `wrf_config/namelist.input.tmpl` with the `w4_run_case.sh` substitutions and compared with the archived namelists.

## Results
| Target | Time | Outcome |
|---|---|---|
| test | 0.6 s | 5 passed |
| masks | 6.8 s | OK |
| track (6 JJA seasons) | 2493 s | max closure residual 2.9e-14 – 4.5e-14; all budgets identical to committed except `runtime_s` |
| known_truth, numerics, case | 49 s | OK; no tracked result changed |
| figures, wrf_figures | 18 s | all 11 PNG figures byte-identical; PDFs differ only in `/CreationDate` |
| report, manuscript, package | 1.8 s | manuscript, cover letter and highlights DOCX: every XML part identical; ZIP member lists identical |
| qc | 0.4 s | **ALL PASS** |

WRF archived-output postprocessing (e2021nw): `qc.json`, `paired.json`, `validation.json`, `signal_noise.json`, `country_precip.csv`, `country_signal_noise.csv` are **byte-identical** to the committed files. In `maps.nc`, all 66 floating-point fields have a maximum absolute difference of 0.0.

Configuration: rendered namelists are **byte-identical** to the archived CONTROL, WIND and CTLPERT_1 namelists. CONTROL and WIND differ only in `windfarm_opt`.

## Defect found and fixed
The per-event `results/wrf/<case>/maps.nc` files were git-ignored, so `make wrf_figures` (Figure 10) could not run from a public clone. They are now committed (~5 MB each; commit daa22b4).

## Not repeated
The WRF model integrations themselves (25 runs, about 3–10 h each on 2 vCPU). WRF is not expected to be bitwise reproducible across hardware or compilers. A rerun from the archived `wrfinput`/`wrfbdy` should therefore be compared statistically against the no-wind ensemble, not byte-for-byte.
