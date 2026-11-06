# Repository inventory

Public (code, tests, docs, small results): `bougtoir/atmospheric-water-externalities`.
Private (all raw/intermediate/simulation/analysis objects, Git LFS): `bougtoir/tawe-private-research-data`
(visibility verified PRIVATE via GitHub API before first upload).
Scientific reference (read-only, unchanged): `bougtoir/ecm-wind-heatwave`.

Canonical pipeline (v1): `scripts/g2_fetch_era5.py` → `g2_masks.py` → `g3_track.py` → `g5_known_truth.py`,
`g5_numerics.py` → `g6_case_study.py` → `g7_gate_report.py` → `g8_figures.py` → `g8_build_manuscript.py` →
`g8_package.py` → `g9_qc.py` (`Makefile`). WRF programme: `scripts/wrf/` (this revision).
Archive tooling: `archive/archive_to_private.py` (register/copy, refuses overwrite), `archive/restore_project_data.py`
(restore + SHA-256 verify; token from `TAWE_ARCHIVE_TOKEN`).
