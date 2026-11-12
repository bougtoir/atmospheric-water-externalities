# WRF ensemble spread growth

Rendered by `scripts/wrf/w21_calibration_reports.py` from `results/wrf/*/spread_growth.csv` and
`results/wrf/spread_growth_summary.json`. Source: archived `wrfout_d01_*` (3-hourly) and `wrfsfc_d01_*` (hourly) of all
five members per event, restored from the private archive with SHA-256 verification; no new WRF simulation.

Fields: hub-height (100 m) wind speed; column water vapour W; |IVT| (vertically integrated vapour transport magnitude);
3-h precipitation and post-spin-up accumulated precipitation. Spread = √(band mean of across-member variance, ddof = 1) of
the four no-wind members. Reference σ_time = √(band mean of CONTROL temporal variance over the analysis window); this is
an approximate, non-stationary saturation scale, not a climatological variance. Figure 12 / Figure_W6.

Metrics (band > 150 km from farms): sat_end = spread / σ_time over the final 24 h; growth = spread(final 24 h) / spread(preceding 24 h);
r_pp = d(pert,pert)/d(CONTROL,pert) (1 exchangeable, √2 CONTROL-centred).

| event | field | sat_end | growth | r_pp | d(W,C)/d(C,P) |
|---|---|---|---|---|---|
| e2016sw | hub_wind | 0.031 | 0.99 | 1.01 | 0.97 |
| e2016sw | W | 0.021 | 0.90 | 1.00 | 0.95 |
| e2016sw | IVT | 0.017 | 1.20 | 1.06 | 0.99 |
| e2016sw | P_3h | 0.062 | 1.55 | 0.93 | 0.99 |
| e2016sw | P_acc |  | 1.01 | 0.86 | 0.97 |
| e2016w | hub_wind | 0.090 | 1.27 | 1.03 | 1.03 |
| e2016w | W | 0.031 | 1.28 | 1.02 | 0.99 |
| e2016w | IVT | 0.039 | 1.49 | 1.04 | 0.96 |
| e2016w | P_3h | 0.301 | 1.09 | 1.00 | 1.02 |
| e2016w | P_acc |  | 1.63 | 0.97 | 0.98 |
| e2017w | hub_wind | 0.051 | 0.93 | 0.94 | 1.07 |
| e2017w | W | 0.020 | 0.63 | 0.94 | 1.05 |
| e2017w | IVT | 0.020 | 0.64 | 0.88 | 1.05 |
| e2017w | P_3h | 0.129 | 0.67 | 0.97 | 1.00 |
| e2017w | P_acc |  | 1.05 | 1.00 | 1.07 |
| e2021nw | hub_wind | 0.063 | 0.70 | 1.10 | 0.99 |
| e2021nw | W | 0.035 | 0.71 | 1.11 | 0.99 |
| e2021nw | IVT | 0.044 | 0.68 | 1.17 | 0.99 |
| e2021nw | P_3h | 0.125 | 0.64 | 1.10 | 1.00 |
| e2021nw | P_acc |  | 1.07 | 1.09 | 0.96 |
| pilot_2020w1 | hub_wind | 0.037 | 0.92 | 1.00 | 0.99 |
| pilot_2020w1 | W | 0.013 | 0.66 | 1.02 | 1.08 |
| pilot_2020w1 | IVT | 0.013 | 1.14 | 1.04 | 1.04 |
| pilot_2020w1 | P_3h | 0.058 | 0.98 | 1.03 | 1.01 |
| pilot_2020w1 | P_acc |  | 1.01 | 1.03 | 1.04 |

## Country flags over time

| event | flags at 00 UTC each day | end | min after 24 h | max any hour |
|---|---|---|---|---|
| e2016sw | 08-05: 0, 08-06: 2, 08-07: 2, 08-08: 1, 08-09: 1 | 1 | 0 | 4 |
| e2016w | 07-09: 1, 07-10: 3, 07-11: 1, 07-12: 0, 07-13: 0 | 0 | 0 | 3 |
| e2017w | 06-23: 0, 06-24: 1, 06-25: 1, 06-26: 3, 06-27: 3 | 3 | 0 | 3 |
| e2021nw | 08-15: 1, 08-16: 2, 08-17: 1, 08-18: 3, 08-19: 1 | 1 | 0 | 4 |
| pilot_2020w1 | 07-02: 0, 07-03: 4, 07-04: 3, 07-05: 3, 07-06: 2 | 2 | 0 | 5 |

## Findings

- Spread starts from zero and, over the final 24 h, reaches at most 30% of σ_time for the instantaneous fields.
- Median growth over the final 24 h exceeds 1 in 2/5 events (e2016sw, e2016w); in the others the spread
  fluctuates with the synoptic evolution rather than levelling off at a ceiling.
- Saturation is therefore not established. Spread is far below σ_time, which itself is only an approximate ceiling.
- Consequence: the four-member prediction interval describes internal variability at the present lead time and may
  underestimate the variability of a saturated ensemble (and, for accumulated precipitation, its continued growth).
  Intervals that are too narrow would flag too often; intervals estimated from too few members are also noisy.
- The number of flagged countries varies over the window (table above), so end-of-window counts are one realisation.
- A contrast not distinguishable from this spread is not evidence of zero effect.
