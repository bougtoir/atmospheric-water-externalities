# WRF prediction-interval audit

Rendered by `scripts/wrf/w21_calibration_reports.py` from `results/wrf/pi_audit.json` (`scripts/wrf/w19_pi_audit.py`)
and `results/wrf/spread_growth_summary.json` (`scripts/wrf/w18_spread_growth.py`, `w20_spread_summary.py`). No WRF rerun.

## Procedure audited (`scripts/wrf/w10_signal_noise.py`)

Per event and country: no-wind ensemble {CONTROL, CTLPERT_1–3} (n = 4) of post-spin-up precipitation totals; mean m and
sample SD s (ddof = 1); one WIND run per event. Flag if |WIND − m| > t(0.975, 3)·s·√(1 + 1/4) = 3.558·s. This is the
95% prediction interval for one new draw from the no-wind distribution. Code, numbers and hand recomputation agree
(SEMANTIC_CODE_AUDIT.md).

## Assumptions and checks

| assumption | why it matters | check | result |
|---|---|---|---|
| exchangeability of WIND (under no effect) and the four no-wind members | t-interval coverage | Monte Carlo, i.i.d. normal | coverage 0.950 |
| independence not required if exchangeable | members share synoptic forcing | equicorrelated members ρ = 0.3/0.6/0.9 | 0.950, 0.951, 0.949 |
| CONTROL is the unperturbed member; others diverge from it | non-exchangeable if spread unsaturated | 'CONTROL-centred' model x_k = κ z_0 + √(1−κ²) z_k, κ = 0.0, 0.25, 0.5, 0.75, 0.9, 1.0 | 0.950, 0.945, 0.938, 0.934, 0.931, 1.000 (κ = 1: zero spread, degenerate) |
| where the design sits | κ from d(pert,pert)/d(CONTROL,pert) = √(1+κ) | pooled over 5 events × 20 countries | ratio 1.127, κ̂ = 0.27, implied coverage 0.944 |
| approximate normality | small n, heavy tails | i.i.d. t₃ members | coverage 0.930 |
| actual false-flag rate on this design | combines all of the above | leave-one-out placebo: each no-wind member vs the other three (n = 3 interval) | 26/400 = 0.065 (95% CI 0.043–0.094) |
| WIND–CONTROL pairing | WIND starts from CONTROL's initial state | d(WIND,CONTROL)/d(CONTROL,pert), d(WIND,pert)/d(pert,pert) per event | table below |
| country dependence | 20 neighbouring countries share weather | not modelled | binomial reference descriptive only |
| temporal spread evolution | interval reflects spread at one lead time | WRF_ENSEMBLE_SPREAD_GROWTH.md | spread not saturated |

| event | r = d(P,P)/d(C,P) | κ̂ | implied coverage | per-country r median [IQR] | d(W,C)/d(C,P) | d(W,P)/d(P,P) | LOO flags |
|---|---|---|---|---|---|---|---|
| e2016sw | 0.547 | 0.00 | 0.949 | 0.95 [0.67, 1.30] | 0.791 | 1.133 | 4/80 |
| e2016w | 1.285 | 0.65 | 0.934 | 1.31 [0.52, 1.41] | 0.411 | 0.812 | 7/80 |
| e2017w | 1.290 | 0.66 | 0.935 | 1.01 [0.77, 1.53] | 1.248 | 0.818 | 4/80 |
| e2021nw | 1.219 | 0.49 | 0.938 | 0.80 [0.57, 1.14] | 0.894 | 0.873 | 3/80 |
| pilot_2020w1 | 1.117 | 0.25 | 0.944 | 1.19 [0.78, 1.45] | 1.150 | 1.066 | 8/80 |

## Interpretation

- Inclusion of CONTROL does not by itself invalidate the interval. If the members are exchangeable, coverage is nominal even
  when they are correlated. If CONTROL is the centre from which unsaturated members diverge, coverage drops only to about
  0.931 (κ = 0.9). The observed distance ratios lie between the two cases, with large event-to-event scatter
  (single-event r from 4 members is itself very noisy). Implied coverage 0.944; leave-one-out flag rate 0.065.
- Interval width is estimated from three degrees of freedom; the t-factor accounts for that on average, but individual
  half-widths are uncertain by roughly a factor of two.
- 7/100 flags against 5 expected. Bin(100, 0.05) gives P(X ≥ 7) = 0.234; this is a
  calibration aid only, because country tests are spatially dependent and share one WIND run per event.
- The interval describes internal variability at the end of the analysis window under the present (unsaturated)
  spread. It is not a deterministic bound on the dynamic response and is not used as one.
- No relabelling of the interval was required; the manuscript states its assumptions (Sections 3.5, 4.8).
