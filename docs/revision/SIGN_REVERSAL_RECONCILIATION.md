# Sign-reversal reconciliation (known-truth experiment)

`results/known_truth.csv` has 32 rows = 2 source perturbations (dE_frac 0.05, 0.20) × 8 (δk, δu) settings
(δk ∈ {−0.05, 0, 0.05, 0.20} × δu ∈ {0, −0.1}) × 2 receptors (C1 near, C2 far).
Rows with δk = δu = 0 (4 rows) are the supply-only control; the remaining **28 rows** contain a dynamic change.
A sign reversal is defined as sign(truth_kg) ≠ sign(supply_kg). Count: **10 of 28** dynamic cases overall;
all 10 occur at the far receptor, which has **14** dynamic cases → **10 of 14** at C2, 0 of 14 at C1.
The two fractions are both correct with different denominators; the revised manuscript states both denominators
explicitly. The values are recomputed by `scripts/g8_build_manuscript.py` from the CSV (keys `kt_flip`,
`kt_n_dyn`, `kt_n_c2`).
