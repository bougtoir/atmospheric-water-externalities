# Gate 1 — Physical definitions and conservation

Units: W column water vapour [kg m⁻²]; F=(F_u,F_v) vertically integrated vapour flux [kg m⁻¹ s⁻¹];
E evaporation, P precipitation [kg m⁻² s⁻¹]; ERA5 `evaporation` is negative upward and accumulated over the
previous hour [m w.e.] → E = −1000·evaporation/3600.

1. **Column budget** ∂W/∂t + ∇·F = E − P + ε, ε the analysis residual (diagnosed, reported, not forced to zero).
2. **Tagged moisture** from source mask S: ∂W_S/∂t + ∇·(F W_S/W) = E·1_S − P·W_S/W, with 0 ≤ W_S ≤ W.
   Discrete closure (exact, tested): Σ E_S = Σ P_S + outflow_S + ΔStorage_S + clip_S.
3. **Source–receptor accounting** A_{S→c} = ∫_season ∫_c P W_S/W dA dt ; normalised a_{S→c} = A_{S→c} / ∫E_S.
   This is *accounting of existing moisture*; it has no causal content.
4. **Transboundary atmospheric water externality (TAWE)** of an intervention I located in jurisdiction j:
   TAWE_{j→c} = P_c(I) − P_c(no I) for receptor c ≠ j (season-integrated, kg or mm). Defined only through a
   counterfactual pair; not observable in reanalysis.
5. **Channel decomposition** TAWE_{j→c} = Δ_supply + Δ_dynamic, where Δ_supply = Σ_S ΔE_S · a_{S→c}
   (perturbed source evaporation routed with *unchanged* winds/precipitation efficiency, first-order) and
   Δ_dynamic is everything else (circulation, convergence, BL/cloud microphysics changes). Δ_supply is computable
   offline from tracking; Δ_dynamic requires a coupled counterfactual model (e.g. WRF with a wind-farm scheme).
6. **Jurisdiction**: a source cell's owner is the country with the largest installed offshore capacity in it
   (turbine register); receptors are Natural Earth 1:50m country polygons (cell-centre rasterisation); sea cells
   are "sea".
7. **Conservation tests** (tests/test_tracking.py): exact tagged-mass closure; W_S ≤ W; zero-source → zero tag;
   analytic exponential rain-out e^{−kx/u}; multi-tag linearity.
