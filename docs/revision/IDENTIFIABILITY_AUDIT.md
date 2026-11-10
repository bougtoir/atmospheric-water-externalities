# Identifiability audit (Gate 6)

Rendered by `scripts/g6c_identification_report.py` from `results/known_truth.csv` and `results/wrf/*/`.

Three distinct findings are reported separately: (A) structural non-identifiability, (B) numerical sign reversals
inside a prespecified synthetic grid, and (C) empirical uncertainty of the WRF intervention contrasts.

## Observable information and estimand

Observables: the realised atmospheric state (W, Q, E, P from ERA5) and an assumed evaporation increment ΔE_S.
Model class: mass-conserving column-moisture transport, dW/dt + ∇·Q = E − P. Estimand: the receptor effect
ΔP_j = P_j(fleet) − P_j(no fleet) = S_j + D_j + I_j (supply, dynamic, interaction). S_j is a functional of
the observed state and ΔE_S. D_j and I_j depend on intervention-induced changes in winds, stability and
precipitation efficiency, which appear only in the unobserved counterfactual state.

## (A) Structural non-identifiability

Within this model class, any intervention-dependent change in transport or precipitation efficiency that is not
constrained by the observables leaves the observed state unchanged while changing ΔP_j. ΔP_j is therefore not
point-identified from the stated observables unless D_j + I_j is restricted by an additional assumption
(e.g. fixed dynamics, which makes ΔP_j = S_j). This follows from the construction of the problem; the
known-truth experiment illustrates it but does not prove it. The statement is limited to the stated
observables and model class; it does not exclude identification with additional information (e.g. validated
coupled models, natural experiments or isolated interventions).

## (B) Numerical sign reversals in the prespecified synthetic grid

Known-truth rows: 32; dynamic receptor-cases (δk≠0 or δu≠0): 28. Grid: δk ∈ [-0.05, 0.0, 0.05, 0.2],
δu ∈ [-0.1, 0.0], ΔE_S/E ∈ [0.05, 0.2], chosen before the runs, not derived from physics.

| receptor | dynamic cases | sign reversals (truth/supply<0) | min truth/supply | max truth/supply |
|---|---|---|---|---|
| C1 | 14 | 0 | 0.611 | 1.35 |
| C2 | 14 | 10 | -12.9 | 3.25 |

The 10/14 far-receptor reversals (10/28 over both receptors) are counts within this grid.
They show that sign reversal is possible for modest dynamic perturbations. They are not a physical probability of
sign reversal: a different grid would give a different count. With δ = 0 the supply estimator reproduces the
truth to round-off (KNOWN_TRUTH_VALIDATION.md).

### Direction of the observed baseline

In the known-truth experiment the observed state is the no-intervention world, and the supply estimator uses its
tagging. In the real setting the observed state (ERA5) already contains the existing wind farms, and the no-fleet
state is the counterfactual. The identification argument is symmetric: in both directions one state is observed,
the other is not, and the unconstrained dynamic response separates them. Formal non-identifiability (A) is
therefore unaffected. The numerical values in (B) are affected: in the real direction S_j would be computed from
the with-fleet state with the sign of ΔE reversed, and second-order differences (S evaluated on the wrong
state) are not quantified by this experiment.

## (C) Empirical uncertainty of the WRF contrasts

WRF [C] contrasts are model-conditional (fixed WRF v4.6.1 configuration, generic turbine curves). They are
compared with the 95% prediction interval derived from the four-member no-wind ensemble; the calibration of
that interval is audited in WRF_PREDICTION_INTERVAL_AUDIT.md and WRF_ENSEMBLE_SPREAD_GROWTH.md.

- `e2016sw`: 19 countries; median |S/C| = 0.000139, max |S/C| = 0.00173; same sign 11/19; C outside the 95% prediction interval derived from the four-member no-wind ensemble in 1/19
- `e2016w`: 19 countries; median |S/C| = 0.00248, max |S/C| = 0.0802; same sign 8/19; C outside the 95% prediction interval derived from the four-member no-wind ensemble in 0/19
- `e2017w`: 19 countries; median |S/C| = 9.12e-05, max |S/C| = 0.00151; same sign 9/19; C outside the 95% prediction interval derived from the four-member no-wind ensemble in 3/19
- `e2021nw`: 19 countries; median |S/C| = 0.00283, max |S/C| = 0.0548; same sign 9/19; C outside the 95% prediction interval derived from the four-member no-wind ensemble in 1/19
- `pilot_2020w1`: 19 countries; median |S/C| = 0.00352, max |S/C| = 0.0177; same sign 7/19; C outside the 95% prediction interval derived from the four-member no-wind ensemble in 2/19
- `e2016sw` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 1.08, near_30_150km 1, far_gt150km 0.961
  - E_acc_mm: farm_0_30km 1.28, near_30_150km 1.06, far_gt150km 1
  - hub_wind: farm_0_30km 5.59, near_30_150km 1.2, far_gt150km 0.991
  - IVTx: farm_0_30km 1.88, near_30_150km 1.05, far_gt150km 1
  - PBLH: farm_0_30km 1.43, near_30_150km 1.03, far_gt150km 0.98
- `e2016w` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 0.977, near_30_150km 1.03, far_gt150km 1.03
  - E_acc_mm: farm_0_30km 0.931, near_30_150km 1.12, far_gt150km 1.01
  - hub_wind: farm_0_30km 13.6, near_30_150km 1.97, far_gt150km 1.06
  - IVTx: farm_0_30km 2.37, near_30_150km 1.21, far_gt150km 0.866
  - PBLH: farm_0_30km 3.15, near_30_150km 1.25, far_gt150km 1.37
- `e2017w` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 1.08, near_30_150km 1.12, far_gt150km 1.05
  - E_acc_mm: farm_0_30km 1.31, near_30_150km 1.1, far_gt150km 1.07
  - hub_wind: farm_0_30km 6.62, near_30_150km 1.48, far_gt150km 1.07
  - IVTx: farm_0_30km 2.32, near_30_150km 1.35, far_gt150km 1.07
  - PBLH: farm_0_30km 3.36, near_30_150km 1.11, far_gt150km 1.05
- `e2021nw` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 1, near_30_150km 1.01, far_gt150km 0.964
  - E_acc_mm: farm_0_30km 2.46, near_30_150km 0.968, far_gt150km 0.993
  - hub_wind: farm_0_30km 6.56, near_30_150km 1.15, far_gt150km 0.923
  - IVTx: farm_0_30km 1.6, near_30_150km 1.09, far_gt150km 0.984
  - PBLH: farm_0_30km 2.41, near_30_150km 1.01, far_gt150km 0.98
- `pilot_2020w1` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 1.14, near_30_150km 1, far_gt150km 1.04
  - E_acc_mm: farm_0_30km 1.28, near_30_150km 0.992, far_gt150km 0.999
  - hub_wind: farm_0_30km 6.74, near_30_150km 1.37, far_gt150km 1.03
  - IVTx: farm_0_30km 1.95, near_30_150km 1.42, far_gt150km 1.05
  - PBLH: farm_0_30km 1.96, near_30_150km 1.11, far_gt150km 0.988

Interpretation: [S] is small relative to the WRF country-level contrasts, and the far-field contrasts are of
the same order as the no-wind ensemble spread. A WRF contrast that is not distinguishable from internal variability
is not evidence of zero effect; it bounds nothing deterministically. [S] is not a TAWE estimate.
