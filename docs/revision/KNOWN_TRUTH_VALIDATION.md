# Known-truth validation (Gate 6)

Source: `results/known_truth.csv` from `scripts/g5_known_truth.py` (idealised linear single-layer world solved with
the project tracker). Truth = P(intervention) − P(no intervention) per receptor; supply estimator = ΔE_S × a_{S→c};
accounting = A_{S→c}. Rendered by `scripts/g6b_known_truth_report.py`.

Configurations: 32 rows = 2 source perturbations × 8 (δk, δu) settings × 2 receptors.

| dynamic channel | receptor | n | sign reversals | median abs rel. error (supply) | max abs rel. error (supply) | min accounting/truth |
|---|---|---|---|---|---|---|
| False | C1 | 2 | 0 | 8.24e-14 | 1.2e-13 | 5 |
| False | C2 | 2 | 0 | 4.15e-13 | 7.18e-13 | 5 |
| True | C1 | 14 | 0 | 0.103 | 0.637 | 4.64 |
| True | C2 | 14 | 10 | 1.35 | 4.95 | 3.17 |

Sign reversals: 10/28 of all dynamic cases; 10/14 at the far receptor C2 (denominators reconciled in SIGN_REVERSAL_RECONCILIATION.md).

Conclusions: (1) the supply estimator reproduces the truth to round-off when transport and rain efficiency are
unchanged; (2) with a dynamic perturbation it is biased and can take the wrong sign, mainly at the far receptor;
(3) accounting is never an externality estimate. The known-truth world tests estimator logic only; it is not
an atmospheric model. Relevance to the atmosphere is assessed against the WRF contrasts in IDENTIFIABILITY_AUDIT.md.
