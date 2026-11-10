# EMS submission decision (Gate 11, updated after the final scientific calibration gate)

**Decision: CONDITIONAL GO.** The calibration gate found no implementation error and no change to canonical results; it found interpretation and wording defects, all fixed through the generation sources. Submission waits only on author metadata.

## Calibration-gate findings (all resolved)
1. Stale one-member noise-reference wording → "95% prediction interval derived from the four-member no-wind ensemble" (pilot report section marked superseded; manuscript, captions, cover letter, highlights, audits checked; FINAL_DELTA_QC.md).
2. Non-identifiability: structural result (stated observables, stated model class) separated from the 10/14 grid-conditional sign reversals and from WRF empirical uncertainty; the count is not a physical probability; synthetic baseline orientation (no-intervention observed) vs real world (fleet observed) stated (IDENTIFIABILITY_AUDIT.md; manuscript 2.2, 3.4, 4.2).
3. Partial identification: imposed bound, finite-grid maximum, statistical interval and physical bound distinguished; the grid maximum is not a physical bound and |C − S| is not a validated upper bound; Eq. (6) added (PARTIAL_IDENTIFICATION_REPORT.md).
4. Prediction interval: implementation verified by independent recomputation. CONTROL inclusion does not by itself invalidate it: Monte Carlo coverage under the estimated dependence 0.944; leave-one-out placebo 26/400 = 0.065 (95% CI 0.043–0.094). 7/100 binomial reference kept as descriptive only (WRF_PREDICTION_INTERVAL_AUDIT.md).
5. Spread growth (archived 3-hourly output, all 5 events, no new WRF runs): spread far below the temporal SD (≤ 30%), still rising in 2/5 events; saturation not established. The interval may underestimate internal variability; manuscript Section 4.8 and Fig. 12 state this, and non-detection is explicitly not evidence of zero effect (WRF_ENSEMBLE_SPREAD_GROWTH.md).
6. Semantic audit: Fig. 9 denominator was described as "ensemble spread"; it is the mean RMS(CTLPERT_k − CONTROL). Wording fixed; numbers unchanged (SEMANTIC_CODE_AUDIT.md, 21/21).

## Why not NO-GO
The headline WRF statement is a non-detection. An interval that is too narrow would over-flag, so unsaturated spread weakens no reported detection; the manuscript no longer implies that the contrasts are zero or bounded. A NO-GO would apply only if the paper had to report an observed real-world causal TAWE magnitude, which it does not.

## Disclosed scientific limitations (do not block submission)
- One WRF configuration; five summer onshore-flow events; four-member no-wind ensembles with unsaturated spread.
- Whole-fleet intervention only; no country-specific attribution.
- Five-day runs describe precipitation, not freshwater availability.
- Identification statements are limited to the stated observables and model class.

## Routine technical blockers (author action)
1. Affiliation, ORCID and e-mail. 2. Generative-AI declaration. 3. Acknowledgements. 4. Author read of cover letter and highlights.

## Evidence
g9_qc ALL PASS; g9b ALL PASS; g10 semantic audit ALL PASS; FINAL_DELTA_QC.md ALL PASS; pytest pass. New outputs archived with read-back verification (FINAL_HANDOFF.md). PRs #1, #2 (TAWE) and #8 (ECM) remain unmerged.
