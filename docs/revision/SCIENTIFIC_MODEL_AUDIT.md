# Scientific model audit (Gate 1)

## Estimands
- [A] provenance accounting A(S→c) = ∫∫_c P·W_S/W dA dt (ERA5 tagging; no causal content).
- [S] fixed-dynamics supply scenario ΔP^S_c = ΔE_S · a(S→c) (requires transport and rain efficiency unchanged).
- [C] WRF model-conditional intervention effect ΔP_c = P_c(WIND) − P_c(CONTROL) (paired simulations, identical
  configuration and forcing except the Fitch wind-farm parameterisation). [C] is model-conditional, not an observed effect.

## Moisture budget
∂W/∂t = E − P − ∇·Q, W [kg m⁻²], Q [kg m⁻¹ s⁻¹], E, P [kg m⁻² s⁻¹]. Tracker integrates over
JJA (2208 h), domain 20°W–35°E, 35–72°N, open lateral boundaries (outflow term), storage at season end retained
as a separate term. ERA5 accumulations converted with E = −1000·e/3600, P = 1000·tp/3600 (m h⁻¹ → kg m⁻² s⁻¹).
Closure residual ≤ 4.5e-14 of source evaporation in all seasons. Units verified in `tests/test_tracking.py`.

## Findings
1. Accounting shares omitted the end-of-season storage term → `WATER_BUDGET_RECONCILIATION.md` (fixed).
2. Sign-reversal fractions 10/14 and 10/28 use different denominators → `SIGN_REVERSAL_RECONCILIATION.md` (fixed).
3. Decomposition: for a WRF pair, ΔP_c = ΔP_supply + ΔP_dyn + interaction is not unique without a convention.
   Convention adopted: supply term = (E_S^WIND − E_S^CTRL)·a^CTRL(S→c) (tagging on CONTROL); residual
   ΔP_c − supply term is reported as "dynamic + interaction" (not split further). Stated in the manuscript.
4. ERA5 tagging and WRF contrasts are different models; ERA5 [A] coefficients are not used as WRF truth.

Gate 1 status: PASS (no unresolved mathematical/physical inconsistency; two reporting defects fixed).
