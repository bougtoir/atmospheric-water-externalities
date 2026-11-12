# Hostile review (Gate 10)

Performed on the rebuilt five-event package before final mechanical QC. Each perspective lists the strongest objection a reviewer in that role would raise, the evidence checked, and the disposition: **fixed** (manuscript or code changed), **disclosed** (limitation stated in the manuscript) or **open** (not resolvable in this revision). Numbers are quoted from the generated reports; none are typed into the manuscript.

## 1. EMS editor
- *Is this a modelling-software contribution, or a climate-impact paper?* The contributions are a definition with evidence classes, an open conservation-closed tool with verification tests, known-truth identifiability experiments and a worked application. **Disclosed/fit**: framed as software + evaluation; Software and data availability section complete.
- *Stale content.* Figure 1 still said "NOT RUN" and the graphical abstract showed four-event values. **Fixed** (FIGURE_REPAIR_AUDIT.md); `make all` now rebuilds the graphical abstract and ZIPs.
- *Contribution list grammar ("and (iv) … and (v)").* **Fixed.**
- *Affiliation, e-mail, GenAI declaration and acknowledgements are placeholders.* **Open — author action** (technical, not scientific).

## 2. WRF specialist
- *Single configuration (15 km, 45 levels, MYNN, Fitch TKE factor 0.25), no nesting, Kain–Fritsch at 15 km.* No resolution, PBL, TKE-factor, microphysics or domain sensitivity was run. **Disclosed** in Discussion and WRF_SENSITIVITY_REPORT.md (sampled vs unsampled dimensions).
- *Is the farm-cell response physically plausible?* Hub-wind deficit negative in every event and PBLH increase near farms; sign and order consistent with Fitch et al. (2012) and Siedersleben et al. (2018). Fleet power 7.3–15.1 GW for 11.2–24.2 GW installed. **Checked.**
- *Power-table units / turbine double counting.* MW→kW and EWW-only inventory fixes recorded in TURBINE_INVENTORY_AUDIT.md. **Fixed earlier**; turbine tables now public in `results/wrf/<case>/`.
- *Invalid IC perturbation (T without THM).* Detected (bit-identical output), retained as `CTLPERT_1_INVALID_unperturbed_THM`, rerun. **Fixed and disclosed.**
- *Lateral-boundary dominance in a small domain could suppress far-field signals.* **Disclosed** as domain-extent limitation; far-field ratios ~1 are conditional on this domain.

## 3. Atmospheric scientist
- *Five events, all with strong onshore transport; no convective or blocked regimes.* **Disclosed** (season sample limitation; events prespecified from ERA5 alone, before any treatment output was inspected).
- *CONTROL precipitation bias vs ERA5 (+15% to +38%).* Reported with spatial correlation; northward-IVT relative bias removed from Fig. 8 because it is undefined for a near-zero mean. **Fixed/disclosed.**
- *σ = 0.01 K perturbations may under-sample spread in the first days.* Analysed in the final calibration gate from archived 3-hourly output of all five events (WRF_ENSEMBLE_SPREAD_GROWTH.md, Fig. 12): spread is far below the temporal SD and saturation is not established. Prediction-interval assumptions audited by Monte Carlo coverage and a leave-one-out placebo (WRF_PREDICTION_INTERVAL_AUDIT.md). **Disclosed** in Sections 3.5 and 4.8: the interval may underestimate internal variability; non-detection is not evidence of zero effect.

## 4. Hydrologist
- *Precipitation is not freshwater availability.* Simulations last five days; soil moisture, groundwater and runoff responses are not represented. **Disclosed** in Discussion; WRF_SOURCE_RECEPTOR_REPORT.md separates ΔP from these quantities.
- *Accounting closure: 20.1% land + 11.1% sea + 63.7% outflow.* Residual is end-of-season storage plus clipping; reconciled in WATER_BUDGET_RECONCILIATION.md. **Checked.**

## 5. Numerical modeller
- *Closure and convergence of the tagging tool.* Max relative residual 4.5e-14; time-step halving ≤0.4%; 3-hourly forcing ≤4.8%. **Checked.**
- *Compression of WRF output could alter values.* Lossless deflate, variable-by-variable equality checked before replacement (COMPRESSION_LEDGER.csv). **Checked.**
- *Figure 4 colour scale.* Saturated because of a unit error (kg per cell vs mm). **Fixed.**

## 6. Causal-inference statistician
- *Multiple testing across 100 dependent country–event tests.* 7 flags vs 5 expected; binomial P(X≥7) is labelled a calibration aid only, not a test. **Fixed wording** (now "binomial probability of at least 7 flags"); dependence disclosed.
- *Prediction interval with n = 4.* Formula now stated in Methods (mean ± t₀.₉₇₅,₃ · s · √(1+1/n)). **Fixed.**
- *Denominator of sign reversals (10/28 vs 10/14).* Results now state "10 of 28 cases (10 of 14 at the far receptor)"; Abstract uses the far-receptor denominator explicitly. **Fixed**; SIGN_REVERSAL_RECONCILIATION.md.
- *Is WIND − CONTROL a causal effect?* Labelled [C] model-conditional throughout; QC enforces the label and bans causal claim words. **Checked.**
- *Country attribution.* Only all-fleet interventions were simulated; no country-specific source attribution is made. **Disclosed.**

## 7. Moisture-tracking specialist
- *Single-layer Eulerian tagging ignores shear.* **Disclosed**; comparison across trackers recommended before policy use.
- *Placebo result (24/24) undermines specificity of accounting.* Stated as a central result: coefficients describe source-area meteorology. **Disclosed.**
- *Known-truth world is linear and idealised.* **Disclosed** as a lower bound on failure modes, not a calibration.

## 8. Policy researcher
- *Risk that [A] coefficients are cited as damages.* Abstract, Discussion and Conclusions state accounting is not an externality estimate; governance use requires [A]/[S]/[C] labels. **Checked.**
- *Absence of detected far-field effect is not evidence of absence.* Wording is "not distinguishable from internal variability for the simulated events", conditional on configuration and ensemble size. **Checked.**

## 9. Reproducibility engineer
- *Figure 7 required ignored runtime files.* **Fixed** (public turbine tables).
- *Hard-coded numbers.* Mutation tests across abstract, results, conclusions, table, highlights and cover letter pass (HARDCODE_AUDIT.md); 0 unmatched numeric tokens.
- *Restoration without re-downloading sources.* See FRESH_VM_RESTORATION_AUDIT.md and PRIVATE_ARCHIVE_REPRODUCIBILITY.md.
- *WRF outputs are private.* Stated in the availability section; configuration (namelists, turbine tables, run_config.json) and per-event analysis results are public. **Disclosed.**

## Final calibration gate addendum
- *Structural vs numerical non-identifiability conflated; 10/14 read as a probability.* **Fixed**: IDENTIFIABILITY_AUDIT.md separates (A) structural, (B) grid-conditional, (C) WRF empirical uncertainty; manuscript Sections 2.2, 3.4, 4.2.
- *Finite-grid maximum used as if a physical bound; |C − S| read as a bound.* **Fixed**: PARTIAL_IDENTIFICATION_REPORT.md and Eq. (6) distinguish imposed, finite-grid, statistical and physical bounds.
- *Fig. 9 denominator described as 'ensemble spread'.* **Fixed**: it is the mean RMS(CTLPERT_k − CONTROL) (SEMANTIC_CODE_AUDIT.md).

## Residual open items
1. Author placeholders (affiliation, ORCID, e-mail, GenAI declaration, acknowledgements) — author action.
2. Unsampled WRF sensitivity dimensions (resolution, PBL scheme, TKE factor, microphysics, domain, country-isolated interventions) — scientific limitation, disclosed; not a defect of the reported contrasts.
