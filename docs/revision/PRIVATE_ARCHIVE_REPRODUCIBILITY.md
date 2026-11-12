# Private archive reproducibility (Gate 10)

Archive: private GitHub repository `bougtoir/tawe-private-research-data` (Git LFS), manifest `DATA_ARCHIVE_MANIFEST.csv` (one row per object: source URL, licence, access time, project path, bytes, SHA-256, archive path, status, restore command). Archive head at the end of the programme: commit `9288e34`.

## Contents
| Category | Objects |
|---|---|
| SIMULATION (wrfout, wrfsfc, wrfrst, wrfinput, wrfbdy, namelists, rsl logs) | 1123 |
| INTERMEDIATE (WPS geogrid/met_em, ERA5 intermediate files) | 517 |
| RAW (ERA5 column budget JJA 2016–2021, ERA5 WRF forcing, WPS static geography, boundaries, turbine register, literature) | 81 |
| ANALYSIS (per-event analysis results, versioned snapshots) | 74 |
| DOCUMENTATION | 2 |
| **Total** | **1797 objects, 84.2 GB** |

All 1797 rows carry `ARCHIVED (remote read-back verified <date>)`: every object was pushed, then fetched from GitHub into an empty clone and its SHA-256 compared with the manifest before the row was marked. Local WRF output files (`wrfout`, `wrfsfc`, `wrfrst`) were deleted only after this check (`archive/PURGE_LEDGER.csv`); inputs needed to rerun WRF (forcing, `wrfinput`, `wrfbdy`, namelists, turbine tables) were kept locally as well as archived.

## Three levels of reproducibility
| Level | What it needs | Status |
|---|---|---|
| Configuration-only | public repo: `wrf_config/*.tmpl`, `scripts/wrf/w4_run_case.sh`, `results/wrf/<case>/run_config.json`, turbine tables | verified: namelists rendered from the public template are byte-identical to the archived CONTROL, WIND and CTLPERT_1 namelists of e2021nw (FRESH_VM_RESTORATION_AUDIT.md) |
| Archived-output postprocessing | public repo + archived wrfout/wrfsfc/rsl of one event | verified for e2021nw: all analysis outputs reproduced exactly (FRESH_VM_RESTORATION_AUDIT.md) |
| Full model rerun | WRF v4.6.1 / WPS v4.6.0 build, archived forcing/WPS inputs, about 3–10 h per run on 2 vCPU | not repeated (25 runs ≈ 90–250 CPU-hours); bitwise identity across machines is not expected for WRF, so a rerun would be judged statistically against the no-wind ensemble |

Restoration uses `archive/restore_project_data.py` (token in `TAWE_ARCHIVE_TOKEN`, never committed). No source dataset is re-downloaded from ECMWF/CDS, Natural Earth or the turbine-register provider.
