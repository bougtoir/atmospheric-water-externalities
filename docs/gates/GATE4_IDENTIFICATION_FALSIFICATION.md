# Gate 4 — Causal identification and falsification

Evidence classes used throughout: **[A] accounting** (conservation-closed tagging of existing moisture, no causal
content); **[S] scenario** (offline first-order supply channel under a stated ΔE; conditional on assumptions);
**[C] causal estimate** (requires an executed counterfactual model pair or a valid observational design).
No [C] result is produced in this project.

| Target | Data/design | Identified? | Why |
|---|---|---|---|
| A_{S→c} (where farm-cell evaporation rains out) | ERA5 + tracker | Yes, as [A] | Mass-closed accounting; model-structural uncertainty (single layer, donor cell) remains |
| Δ_supply_{S→c} for given ΔE_S | ERA5 + tracker × ΔE | Conditional [S] | Linear in ΔE; assumes winds, W and P/W unchanged; ΔE_S itself is not estimated here |
| Δ_dynamic | WRF with wind-farm scheme (Fitch-type) | **Not identified: NOT RUN** | Compute budget (one 2-core VM); not substitutable by tracking |
| TAWE_{j→c} | counterfactual pair | **Not identified** | Requires Δ_dynamic; Gate 5 shows Δ_dynamic can flip the sign at far receptors |
| TAWE from ERA5 before/after build-out | DiD on reanalysis | **Invalid** | ERA5/IFS has no wind-farm parameterisation; any ERA5 trend is not caused by the farms in the model |
| TAWE from station/radar data | DiD around commissioning | Not attempted | Detection power check in Gate 6 (minimum detectable effect vs interannual SD) |

Falsification tests (implemented, results in Gate 6):
1. **Placebo sources**: 5 sets of farm clusters translated independently to nearby sea cells (≤3°, off farms).
   If a_{S→c} for real farms lies inside the placebo range, the transfer coefficient reflects geography and
   meteorology, not anything specific to the infrastructure → it must not be presented as a farm effect.
2. **Conservation**: tagged-mass closure per tag and season must be ≲1e-9 relative.
3. **Linearity**: owner tags must sum to the ALL tag (minus single-cell owners), confirming additivity of [A].
4. **Interannual stability**: a_{S→c} across 6 JJA seasons; a quantity that varies more between years than
   between real and placebo sources cannot be attributed to the source location.
