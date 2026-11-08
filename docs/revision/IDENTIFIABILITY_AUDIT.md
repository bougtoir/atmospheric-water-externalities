# Identifiability audit (Gate 6)

Rendered by `scripts/g6c_identification_report.py` from `results/known_truth.csv` and `results/wrf/*/`.

## Observable information

ERA5 provides the realised state (W, Q, E, P) under the realised fleet. Tagged tracking of that state yields
[A] provenance accounting and, with an assumed evaporation increment and fixed dynamics, the [S] supply term.
The counterfactual state without the fleet is not observed. The receptor effect decomposes as
ΔP_j = S_j + D_j + I_j (supply, dynamic, interaction). Only S_j is a functional of the observed state plus
an assumed ΔE; D_j and I_j depend on unobserved changes in winds, stability and precipitation efficiency.

## Admissible counterexamples (known-truth model)

Known-truth rows: 32; dynamic configurations (δk≠0 or δu≠0): 28 receptor-cases.
Each configuration is mass-conserving and reproduces the same observed baseline, yet gives a different ΔP_j.

| receptor | dynamic cases | sign reversals (truth/supply<0) | min truth/supply | max truth/supply |
|---|---|---|---|---|
| C1 | 14 | 0 | 0.611 | 1.35 |
| C2 | 14 | 10 | -12.9 | 3.25 |

Hence ΔP_j is not point-identified from the observables used by [A]/[S]: observationally equivalent
structures give opposite signs at the far receptor. The supply term is recovered exactly only when the
dynamic perturbation is zero (see `KNOWN_TRUTH_VALIDATION.md`).

## Relevance check with completed WRF cases

WRF [C] contrasts are model-conditional (fixed WRF v4.6.1 configuration, generic turbine curves) and are
used only to judge whether the dynamic term is plausibly negligible, not as ground truth.

- `e2016w`: 19 countries; median |S/C| = 0.00248, max |S/C| = 0.0802; same sign 8/19; |C| exceeds single-member noise in 0/19
- `e2017w`: 19 countries; median |S/C| = 9.12e-05, max |S/C| = 0.00151; same sign 9/19; |C| exceeds single-member noise in 3/19
- `pilot_2020w1`: 19 countries; median |S/C| = 0.00352, max |S/C| = 0.0177; same sign 7/19; |C| exceeds single-member noise in 2/19
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
- `pilot_2020w1` RMS(WIND−CONTROL)/mean RMS(member−CONTROL), members ['CTLPERT_1', 'CTLPERT_2', 'CTLPERT_3'] by distance band:
  - P_acc_mm: farm_0_30km 1.14, near_30_150km 1, far_gt150km 1.04
  - E_acc_mm: farm_0_30km 1.28, near_30_150km 0.992, far_gt150km 0.999
  - hub_wind: farm_0_30km 6.74, near_30_150km 1.37, far_gt150km 1.03
  - IVTx: farm_0_30km 1.95, near_30_150km 1.42, far_gt150km 1.05
  - PBLH: farm_0_30km 1.96, near_30_150km 1.11, far_gt150km 0.988

Interpretation: in the completed WRF cases the [S] term is small relative to the WRF country-level
contrasts, and far-field contrasts are of the same order as a single initial-condition perturbation. The
dynamic/internal-variability component therefore cannot be assumed negligible; [S] is not a TAWE estimate.
