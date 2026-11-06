# WRF resource benchmark (Gate 2, measured on this VM)

Machine: Ubuntu, 2 vCPU, 7.7 GB RAM, 124 GB disk (41 GB free when the pilot started). WRF 4.6.1 dmpar,
`mpirun -np 2`, `HWLOC_COMPONENTS=-x86`.

| item | measured |
|---|---|
| geogrid (141×111, 15 km, lowres) | < 1 min |
| ERA5→intermediate + metgrid, 49 times | ≈ 3 min; met_em 2.1 GB |
| real.exe | ≈ 1 min; wrfinput 74 MB, wrfbdy 597 MB |
| wrf.exe step time (dt = 60 s), CONTROL | 0.71–0.78 s per non-radiation step; ≈ 90 s wall per simulated hour including radiation and output |
| wrf.exe RAM | ≈ 0.9 GB per rank (1.8 GB total) |
| history output (3-hourly, full) | 150 MB per 8 frames uncompressed; 44 MB after `nccopy -d 4 -s` (×3.4) |
| hourly surface stream | ≈ 4.7 MB per 8 frames |

Derived (144-h run): ≈ 3.6 h wall and ≈ 7.2 core-h per run. The paired CONTROL + WIND case takes
≈ 7.2 h wall and ≈ 14.4 core-h. Final wall times from `wrf_runs/<case>/logs/timing.txt` replace these
estimates in `WRF_PILOT_EXECUTION_REPORT.md`.
