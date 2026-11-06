# WRF execution log

Chronological record of WRF runs, failures and corrections. Run status and wall-clock times are taken from
`wrf_runs/<case>/logs/status.txt` and `timing.txt`; QC values are in `results/wrf/<case>/qc.json`.

## pilot_2020w1 (2020-06-30T00 – 2020-07-06T00, 24 h spin-up)

| run | status | note |
|---|---|---|
| CONTROL | SUCCESS COMPLETE WRF | `windfarm_opt=0` |
| WIND | SUCCESS COMPLETE WRF | `windfarm_opt=1`, EWW offshore fleet (see TURBINE_INVENTORY_AUDIT.md) |
| CTLPERT_1 (first attempt) | completed, **INVALID** | see defect D1; directory retained as `CTLPERT_1_INVALID_unperturbed_THM` for audit |
| CTLPERT_1 (rerun) | queued (`scripts/wrf/w6b_queue.sh`) | THM perturbed consistently with T |

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
| CONTROL | running |
| WIND | queued |
