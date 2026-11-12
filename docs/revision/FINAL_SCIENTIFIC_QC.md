# Final scientific QC (Gate 10)

Checks made on the rebuilt five-event package after the hostile review (HOSTILE_REVIEW.md). Every number comes from canonical result files; see NUMERIC_PROVENANCE.csv.

| # | Check | Evidence | Result |
|---|---|---|---|
| 1 | Water accounting closes | tagging max relative residual ~4e-14 per season (results/track_budget, fresh-VM rerun) | PASS |
| 2 | 20.1% land + 11.1% sea + 63.7% outflow reconciled with storage | WATER_BUDGET_RECONCILIATION.md | PASS |
| 3 | Sign-reversal denominator stated explicitly (10/28 all, 10/14 far receptor) | SIGN_REVERSAL_RECONCILIATION.md, manuscript Results/Abstract | PASS |
| 4 | Evidence classes [A]/[S]/[C] kept separate; supply, dynamic and interaction terms not mixed | IDENTIFIABILITY_AUDIT.md, PARTIAL_IDENTIFICATION_REPORT.md, g9_qc label check | PASS |
| 5 | All 25 valid WRF runs pass numerical QC (CFL, missing frames, NaN/negative moisture, monotone accumulations) | WRF_EXPERIMENT_REGISTRY.csv, wrf_cases/*_NUMERIC_QC.md | PASS |
| 6 | CONTROL and WIND differ only in `windfarm_opt`; CTLPERT differ only in seeded T/THM perturbation | run_config.json, namelist diff, ic_perturbation.json | PASS |
| 7 | Invalid pilot perturbation (T without THM) excluded from statistics but retained | registry row `CTLPERT_1_INVALID_unperturbed_THM` | PASS |
| 8 | No-wind prediction interval formula stated and implemented identically | w10_signal_noise.py, manuscript Methods | PASS |
| 9 | Pooled 7/100 flags vs 5 expected, binomial reference labelled a calibration aid, dependence disclosed | programme_summary.json, manuscript | PASS |
| 10 | WRF contrast described as model-conditional, not a real-world causal effect; WRF not called ground truth | g9_qc wording checks | PASS |
| 11 | No country-specific source attribution claimed (only all-fleet interventions) | WRF_SOURCE_RECEPTOR_REPORT.md, manuscript | PASS |
| 12 | Supply channel vs WRF contrast reported separately (max supply/noise ratio ≈ 0.022) | supply_vs_wrf.json per event | PASS |
| 13 | Figures regenerated from canonical outputs; Figure 4 unit fix; no stale "NOT RUN" | FIGURE_REPAIR_AUDIT.md, FIGURE_VISUAL_QC.md | PASS |
| 14 | Archive persistence verified before any purge | PRIVATE_ARCHIVE_REPRODUCIBILITY.md, PURGE_LEDGER.csv | PASS |
| 15 | Results reproduce from a fresh public clone (+ archive for WRF outputs) | FRESH_VM_RESTORATION_AUDIT.md | see that report |

## Limitations carried into the manuscript (not defects)
- One WRF configuration: resolution, PBL scheme, Fitch TKE factor, microphysics and domain extent not varied.
- Five summer events with onshore transport; 4-member no-wind ensembles; ensemble spread growth not analysed.
- All-fleet interventions only; country-isolated interventions not run.
- Five-day simulations: precipitation, not freshwater availability.
