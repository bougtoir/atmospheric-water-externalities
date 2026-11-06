# WRF execution log

Chronological record of WRF runs, failures and corrections. Run status and wall-clock times are taken from
`wrf_runs/<case>/logs/status.txt` and `timing.txt`; QC values are in `results/wrf/<case>/qc.json`.

## pilot_2020w1 (2020-06-30T00 – 2020-07-06T00, 24 h spin-up)

| run | status | note |
|---|---|---|
| CONTROL | SUCCESS COMPLETE WRF | `windfarm_opt=0` |
| WIND | SUCCESS COMPLETE WRF | `windfarm_opt=1`, EWW offshore fleet (see TURBINE_INVENTORY_AUDIT.md) |
| CTLPERT_1 (first attempt) | completed, **INVALID** | see defect D1; directory retained as `CTLPERT_1_INVALID_unperturbed_THM` for audit |
| CTLPERT_1 (rerun) | running | THM perturbed consistently with T; divergence from CONTROL confirmed in output frames 1–2 (max |ΔT| 0.78–0.98 K, max |ΔU| 3.2–3.6 m/s) |

### Defect D1 — noise reference not perturbed

`scripts/wrf/w4b_perturb_ic.py` originally perturbed only `T` in `wrfinput_d01`. WRF v4 runs with
`use_theta_m=1`, for which the prognostic thermodynamic variable is the moist potential temperature `THM`;
`T` is diagnosed from it. The perturbation was therefore present in the first output frame (`T` max |Δ| 0.044 K)
but absent from the integration: all later CTLPERT_1 frames were bit-identical to CONTROL (max |Δ| of `T`,
`QVAPOR`, `RAINNC` = 0). Detected by `scripts/wrf/w10_signal_noise.py`, which returned zero noise in every
country. Correction: `T` and `THM` are perturbed by the same seeded draw (THM scaled by 1 + (Rv/Rd) qv);
the script now records the perturbed variables. A test on a copy of the CONTROL input gave max |Δ| T 0.045 K,
THM 0.045 K, QVAPOR 0. No WIND − CONTROL contrast is interpreted as a signal until the valid noise reference
has completed.

## e2017w (2017-06-21T00 – 2017-06-27T00)

| run | status |
|---|---|
| CONTROL | SUCCESS COMPLETE WRF |
| WIND | SUCCESS COMPLETE WRF |

QC and paired contrasts: `results/wrf/e2017w/`, rendered in `docs/revision/wrf_cases/e2017w_*.md`.

### Defect D2 — analysis globbed compression temporaries

`w5_analyse_case.py` globbed `wrfout_d01_*`, which also matched `*.z.tmp` files being written by the compression
watcher, and failed with an HDF error. File patterns now require the exact WRF timestamp form.
