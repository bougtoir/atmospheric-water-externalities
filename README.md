# atmospheric-water-externalities

Conservation-closed moisture tagging and identifiability framework for **transboundary atmospheric water
externalities (TAWE)** of energy infrastructure, with a European offshore-wind test case (ERA5, JJA 2016–2021).

Evidence classes: **[A]** accounting (tagging of existing moisture), **[S]** supply-channel scenario for a stated
ΔE, **[C]** causal estimate (needs an executed counterfactual pair). This repository produces [A] and [S] only.
The WRF wind-farm counterfactual suite was designed but **NOT RUN** (compute budget); TAWE is not identified.

## Layout
- `tawe/tracking.py` — donor-cell Eulerian forward tagging with exact per-tag mass budget
- `scripts/g2_*` data + masks, `g3_track.py` tracking, `g5_*` known-truth and numerics, `g6_case_study.py`,
  `g7_gate_report.py`, `g8_*` figures/manuscript/package, `g9_qc.py`
- `docs/gates/` Gate 0–9 records; `docs/journal_guides/` EMS guide snapshots (ledger + SHA-256)
- `data/raw/**/LEDGER.csv` provenance ledgers. ERA5 NetCDFs (~0.3 GB/month) are not in git: re-fetch with
  `make fetch` and verify SHA-256 against `data/raw/era5/LEDGER.csv`.

## Reproduce
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.lock.txt
make fetch   # ~5.5 GB, anonymous access to ARCO-ERA5
make all     # masks → track → known_truth → numerics → case → figures → report → manuscript → qc
make test
```
Runtime of the full tracking: ~7–10 min per season on 2 CPU cores, 8 GB RAM.

Source data: ERA5 (Copernicus licence), Natural Earth (public domain), offshore turbine register copied with checksum
from `bougtoir/ecm-wind-heatwave` (commit 03e3c19). Code: MIT licence.
