# Partial identification report (Gate 6)

Rendered by `scripts/g6c_identification_report.py`.

With ΔP_j = S_j + R_j and only a bound |R_j| ≤ B_j available, the identified set is
[S_j − B_j, S_j + B_j]. The sign of ΔP_j is identified only if |S_j| > B_j.

## Bounds implied by the known-truth admissible family

B_j is taken as max |truth − supply| over the dynamic configurations in `results/known_truth.csv`.

| dE_frac | receptor | S_j (kg) | B_j (kg) | identified set (kg) | sign identified |
|---|---|---|---|---|---|
| 0.05 | C1 | 1.78e+10 | 6.92e+09 | [1.09e+10, 2.47e+10] | yes |
| 0.05 | C2 | 9.42e+09 | 1.31e+11 | [-1.22e+11, 1.41e+11] | no |
| 0.2 | C1 | 7.11e+10 | 7.35e+09 | [6.38e+10, 7.85e+10] | yes |
| 0.2 | C2 | 3.77e+10 | 1.35e+11 | [-9.72e+10, 1.73e+11] | no |

## WRF-informed scale of the residual

Using the WRF [C] contrast as a model-conditional scale for R_j = C_j − S_j:

- `e2016w`: countries with |S_j| > |C_j − S_j|: 0/19
- `e2017w`: countries with |S_j| > |C_j − S_j|: 0/19
- `pilot_2020w1`: countries with |S_j| > |C_j − S_j|: 0/19

Under the known-truth bound the sign is identified for receptor(s) ['C1'] only.
Under the WRF-informed scale, the sign is identified from [S] in 0 country-case(s).
Country-specific TAWE claims would require isolated-intervention ensembles large enough to bound
internal variability.
