# Gate 5 — Known-truth validation and identifiability limits

Scripts: `scripts/g5_known_truth.py` (idealised linear world, 32 configurations) → `results/known_truth.csv`;
`scripts/g5_numerics.py` (CFL 0.25 vs 0.5, 3-hourly vs hourly forcing; July 2019) → `results/numerics_sensitivity.csv`;
unit tests `tests/test_tracking.py` (closure, capacity bound, zero source, analytic rain-out, multi-tag linearity).
Summary numbers are rendered from these files into `docs/gates/GATE3_7_RESULTS.md` and the manuscript.

Identifiability limits established:
1. Supply estimator is exact (to round-off) only if the intervention leaves transport and rain efficiency unchanged.
2. With a downwind dynamic perturbation the supply estimator is biased and can have the wrong sign, mostly at far
   receptors, because the dynamic channel acts on background (untagged) moisture.
3. Accounting A(S→c) is never an externality estimate (it is larger than the truth by a factor ≥ 3 in all cases).
4. Observational detection of the supply channel in national JJA precipitation requires implausibly large
   evaporation changes (`results/detectability.csv`).
Limitation: the known-truth world is linear, 2-D and single-layer; it tests estimator logic, not atmospheric realism.
