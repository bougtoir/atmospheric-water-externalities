# Partial identification report (Gate 6)

Rendered by `scripts/g6c_identification_report.py`.

## Decomposition and identified set

ΔP_j = S_j + R_j, with R_j = D_j + I_j. If |R_j| ≤ B_j is assumed, the identified set is [S_j − B_j, S_j + B_j],
and it is sharp for that assumption: every point is attained by some R_j with |R_j| ≤ B_j. The sign of ΔP_j is
identified only if |S_j| > B_j. The interval is exactly as credible as the assumption on B_j.

Four different quantities are kept apart:

| quantity | what it is | used here as |
|---|---|---|
| mathematically imposed bound | an assumption \|R_j\| ≤ B_j stated a priori | the premise of the interval formula |
| finite-grid maximum | max \|truth − supply\| over the prespecified synthetic grid | an illustrative B_j, conditional on the grid |
| statistically estimated interval | e.g. the WRF no-wind 95% prediction interval | a statement about internal variability, not a deterministic bound |
| physically justified bound | a bound on the dynamic response derived from physics or validated models | not available in this study |

## Illustration: B_j = finite-grid maximum (synthetic world only)

B_j is max |truth − supply| over the dynamic configurations of the prespecified grid in `results/known_truth.csv`.
It is not a physical bound: dynamic perturbations outside the grid can exceed it.

| dE_frac | receptor | S_j (kg) | grid max B_j (kg) | grid-conditional set (kg) | sign identified under this B_j |
|---|---|---|---|---|---|
| 0.05 | C1 | 1.78e+10 | 6.92e+09 | [1.09e+10, 2.47e+10] | yes |
| 0.05 | C2 | 9.42e+09 | 1.31e+11 | [-1.22e+11, 1.41e+11] | no |
| 0.2 | C1 | 7.11e+10 | 7.35e+09 | [6.38e+10, 7.85e+10] | yes |
| 0.2 | C2 | 3.77e+10 | 1.35e+11 | [-9.72e+10, 1.73e+11] | no |

Under the grid maximum the sign is identified for receptor(s) ['C1'] of the synthetic world only;
this conclusion holds only if the true dynamic response lies inside the grid.

## WRF: why no bound is derived

|C_j − S_j| from one WRF WIND − CONTROL pair mixes the model-conditional dynamic response with internal
variability of a single realisation. It is not a validated upper bound on R_j and is not used as one. The no-wind
95% prediction interval describes internal variability under assumptions audited in
WRF_PREDICTION_INTERVAL_AUDIT.md; turning its width into a deterministic B_j would require an additional assumption
(e.g. that the expected dynamic response is smaller than internal variability), which is not justified here.
Descriptively, |S_j| is smaller than |C_j − S_j| in every WRF country-case:
- `e2016sw`: countries with |S_j| > |C_j − S_j|: 0/19
- `e2016w`: countries with |S_j| > |C_j − S_j|: 0/19
- `e2017w`: countries with |S_j| > |C_j − S_j|: 0/19
- `e2021nw`: countries with |S_j| > |C_j − S_j|: 0/19
- `pilot_2020w1`: countries with |S_j| > |C_j − S_j|: 0/19

Consequence: no real-world country-specific TAWE interval is reported. A defensible B_j would require
isolated-intervention ensembles large enough to estimate the expected dynamic response and its uncertainty.
