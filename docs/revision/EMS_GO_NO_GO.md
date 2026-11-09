# EMS submission decision (Gate 11)

**Decision: CONDITIONAL GO.** The science is ready to submit. Submission waits only on author metadata, which is not a scientific issue.

## Scientific defects (would block submission)
None outstanding. Defects found during the revision were fixed and re-verified: Figure 4 unit error, stale "NOT RUN" text in Figure 1 and the graphical abstract, the invalid pilot perturbation (rerun; the invalid run is retained for audit), turbine double counting and power-table units, the sign-reversal denominator wording, and an overclaim about ensemble-spread saturation in the review draft (FIGURE_REPAIR_AUDIT.md, HOSTILE_REVIEW.md, FINAL_SCIENTIFIC_QC.md).

## Disclosed scientific limitations (do not block submission)
- One WRF configuration (resolution, PBL scheme, TKE factor, microphysics and domain extent were not varied); WRF_SENSITIVITY_REPORT.md.
- Five summer onshore-flow events, each with a 4-member no-wind ensemble; ensemble spread growth not analysed.
- Only the whole wind fleet was switched on or off, so no country-specific source attribution is claimed.
- Five-day runs describe precipitation, not freshwater availability.

## Routine technical blockers (author action before upload)
1. Affiliation, ORCID and e-mail on the title page.
2. Generative-AI declaration text.
3. Acknowledgements (funding/none).
4. Final read of the cover letter and highlights by the author.

## Evidence that the package is ready
- WRF: 25 valid runs (5 events × CONTROL, WIND, 3 CTLPERT), all passing numerical QC, archived and read back with SHA-256 checks (PRIVATE_ARCHIVE_REPRODUCIBILITY.md).
- Gate 9: g9_qc ALL PASS; g9b audits (numeric, hard-code mutation, references, figures/tables, OMML, document integrity) ALL PASS.
- Gate 10: hostile review from nine perspectives; fresh-clone restoration (FRESH_VM_RESTORATION_AUDIT.md).
- Status of the existing PRs: TAWE PR #1 and ECM PR #8 are open and not merged; merging needs the author's explicit approval.
