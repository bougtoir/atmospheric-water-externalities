# WRF compute budget (Gate 2)

Based on `WRF_RESOURCE_BENCHMARK.md` (≈ 7.2 core-h per 144-h run on 2 vCPU, ≈ 3.6 h wall).

| block | runs | wall (h) | core-h |
|---|---|---|---|
| pilot CONTROL + WIND | 2 | 7.2 | 14.4 |
| pilot noise reference CTLPERT_1 | 1 | 3.6 | 7.2 |
| 4 further events × (CONTROL + WIND) | 8 | 28.8 | 57.6 |
| country-isolated pilot runs (GB, DE) | 2 | 7.2 | 14.4 |
| sensitivity (tke factor 1.0; cu off) for pilot | 2–4 | 7–14 | 14–29 |
| **total** | 15–17 | ≈ 54–61 | ≈ 108–123 |

The programme fits on this VM without paid compute, run sequentially over about 2.5 days of wall
time. A higher resolution (5 km nest) or a multi-member ensemble per event would need about 25–30×
more compute and is out of scope. The limit is disclosed in the manuscript.

Storage: about 1.5–2 GB compressed per event in the private archive. The total of about 18–20 GB
exceeds the GitHub LFS free quota, so this is a decision for the author (see the session log).
Locally, raw (uncompressed) run directories are compressed and pruned only after the remote read-back
is verified.
