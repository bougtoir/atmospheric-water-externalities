# WRF execution log

Chronological record of WRF runs, failures and corrections. Run status and wall-clock times are taken from
`wrf_runs/<case>/logs/status.txt` and `timing.txt`; QC values are in `results/wrf/<case>/qc.json`.

## pilot_2020w1 (2020-06-30T00 – 2020-07-06T00, 24 h spin-up)

| run | status | note |
|---|---|---|
| CONTROL | SUCCESS COMPLETE WRF | `windfarm_opt=0` |
| WIND | SUCCESS COMPLETE WRF | `windfarm_opt=1`, EWW offshore fleet (see TURBINE_INVENTORY_AUDIT.md) |
| CTLPERT_1 (first attempt) | completed, **INVALID** | see defect D1; directory retained as `CTLPERT_1_INVALID_unperturbed_THM` for audit |
| CTLPERT_1 (rerun) | SUCCESS COMPLETE WRF | THM perturbed consistently with T; divergence from CONTROL confirmed in output frames 1–2 (max |ΔT| 0.78–0.98 K, max |ΔU| 3.2–3.6 m/s) |

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

## e2016w

CONTROL and WIND completed (SUCCESS COMPLETE WRF); QC in `docs/revision/wrf_cases/e2016w_NUMERIC_QC.md`. Noise members CTLPERT_1-3 queued via `scripts/wrf/w6c_queue.sh` (author-approved 3-member ensemble per event).

## Defect D3 — hard-linked archive staging of rewritable files (found and fixed 2026-11-07)

`archive/archive_to_private.py` hard-linked every staged file into the private-archive working tree. Two small
analysis files (`results/wrf/pilot_2020w1/signal_noise.json`, `country_signal_noise.csv`) were later rewritten in
place, which also altered the archive working-tree copies. The committed and pushed archive versions were not
affected (read-back 50/50 had already verified them); the working tree was restored with `git checkout` and its
SHA-256 matched the manifest. Fix: only large model files (>= 50 MiB, outside `results/`) are hard-linked; all
374 existing small hard links were broken into independent copies. Local purges of read-back-verified datasets
are now done only by `archive/purge_local_verified.py`, which re-hashes before deletion and logs to
`archive/PURGE_LEDGER.csv` (first use: invalid pilot CTLPERT_1, 34 objects).

### D4 — Disk exhaustion during the e2016w archive read-back (2026-11-07)

`git add` in the private-archive clone stores a separate copy of every LFS object in `.git/lfs/objects`; with the
archive working tree and the project tree this was a third local copy (≈15 GB for e2016w), and the full-checkout
read-back (`restore_project_data.py --check-only`) needs a fourth. Free disk fell to 0 B while e2017w CTLPERT_1 was
running. The WRF processes had been suspended (SIGSTOP) at 4.7 GB free and were resumed (SIGCONT) only after space
was recovered, so no output was written while the disk was full; the run continued from the same model state.
No project data was lost: the interrupted read-back clone was deleted, and only redundant copies were removed by
`archive/dedupe_archive_tree.py` (pushed LFS cache copies, and archive working-tree copies of read-back-verified
objects replaced by LFS pointers; every removal is in `archive/PURGE_LEDGER.csv`; project copies were re-hashed first).
Read-back now uses `archive/readback_lean.py` (pointer-only fresh clone, per-dataset `git lfs fetch`, SHA-256 per
object, fetched objects deleted before the next dataset). Logs and analysis files rewritten when a case gains members
are archived as new versioned datasets (`ARCHIVE_VERSIONED`), so archived objects are never overwritten.
`scripts/wrf/w14_archive_verify_purge.sh` chains archive → push → read-back → mark → output-only purge per case.
