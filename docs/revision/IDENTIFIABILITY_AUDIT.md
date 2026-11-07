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

- `pilot_2020w1`: 19 countries; median |S/C| = 0.00352, max |S/C| = 0.0177; same sign 7/19; |C| exceeds single-member noise in 11/19
- `pilot_2020w1` RMS(WIND−CONTROL)/RMS(CTLPERT_1−CONTROL) by distance band:
  - P_acc_mm: farm_0_30km 1.32, near_30_150km 0.984, far_gt150km 1.03
  - E_acc_mm: farm_0_30km 1.35, near_30_150km 0.982, far_gt150km 0.954
  - hub_wind: farm_0_30km 6.88, near_30_150km 1.32, far_gt150km 0.953
  - IVTx: farm_0_30km 2.06, near_30_150km 1.32, far_gt150km 1.07
  - PBLH: farm_0_30km 2.26, near_30_150km 1.13, far_gt150km 0.953

Interpretation: in the completed WRF cases the [S] term is small relative to the WRF country-level
contrasts, and far-field contrasts are of the same order as a single initial-condition perturbation. The
dynamic/internal-variability component therefore cannot be assumed negligible; [S] is not a TAWE estimate.
