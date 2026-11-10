PY ?= .venv/bin/python
YEARS ?= 2016 2017 2018 2019 2020 2021
RUNS ?= wrf_runs
CASES ?= e2016sw e2016w e2017w e2021nw pilot_2020w1
MONTHS = $(foreach y,$(YEARS),$(y)-06 $(y)-07 $(y)-08)
.PHONY: all fetch masks track known_truth numerics case figures wrf_figures calibration report manuscript semantic package qc test spread_growth
all: masks track known_truth numerics case figures calibration wrf_figures report manuscript semantic package qc
fetch:       ; $(PY) scripts/g2_fetch_era5.py $(MONTHS)
masks:       ; $(PY) scripts/g2_masks.py
track:       ; $(PY) scripts/g3_track.py $(YEARS)
known_truth: ; $(PY) scripts/g5_known_truth.py
numerics:    ; $(PY) scripts/g5_numerics.py 2019-07
case:        ; $(PY) scripts/g6_case_study.py
figures:     ; $(PY) scripts/g8_figures.py
wrf_figures: ; $(PY) scripts/g8b_wrf_figures.py
package:     ; $(PY) scripts/g8_package.py
report:      ; $(PY) scripts/g7_gate_report.py
manuscript:  ; $(PY) scripts/g8_build_manuscript.py
# spread_growth needs archived wrfout/wrfsfc restored into RUNS (archive/restore); results/wrf/*/spread_growth.csv are published
spread_growth: ; for c in $(CASES); do $(PY) scripts/wrf/w18_spread_growth.py $$c $(RUNS); done
calibration: ; $(PY) scripts/wrf/w19_pi_audit.py && $(PY) scripts/wrf/w20_spread_summary.py && $(PY) scripts/wrf/w21_calibration_reports.py && $(PY) scripts/g6c_identification_report.py
semantic:    ; $(PY) scripts/g10_semantic_audit.py
qc:          ; $(PY) scripts/g9_qc.py
test:        ; $(PY) -m pytest tests -q
