# Semantic code audit

Rendered by `scripts/g10_semantic_audit.py`. Each row compares a stated estimand or claim with the code and
its output by an independent recomputation (different code path, hand value or text check). Unit tests are not counted.

| area | claim | independent check | status | detail |
|---|---|---|---|---|
| PI | half-width = t(0.975,n-1)·s·√(1+1/n), n = 4 | hand value t(0.975,3) = 3.182446 (table), ×√1.25 | PASS | factor 3.5581 |
| PI | country flags (w10) reproduce from member totals | numpy recomputation from country_precip.csv | PASS | 100 country-events, 0 mismatches |
| PI | one CONTROL baseline per event | P_control_kg unique per country across exp rows | PASS |  |
| PI | 7/100 flags; P(X≥K) for Bin(N,0.05) | re-sum of flags; binomial by explicit sum | PASS | 7/100, p = 0.2340 (descriptive: tests dependent) |
| WRF | country precipitation totals: hourly wrfsfc path (w18) = window path (w5) | archived raw output re-read | PASS | 500 values, max rel. diff 1.55e-06 |
| WRF | end-of-window flags from hourly path = w10 flags | w20 recomputation | PASS | e2016sw 1/1, e2016w 0/0, e2017w 3/3, e2021nw 1/1, pilot_2020w1 2/2 |
| WRF | Fig. 9 denominator = mean over CTLPERT_k of RMS(CTLPERT_k − CONTROL) | code inspection of w10 field loop | PASS | caption and Section 4.6 now state this; earlier text said 'RMS spread' |
| KT | δ = 0 ⇒ truth = supply (linearity) | max |rel err| over static rows | PASS | 7.2e-13 |
| KT | 10/14 far-receptor sign reversals | sign comparison of truth_kg vs supply_kg | PASS | 10/14 (grid-conditional count) |
| KT | grid size 2×4×2 = 16 configs × 2 receptors = 32 rows | row count | PASS | 32 rows, 28 dynamic |
| KT | Eq. (5) linear in ΔE_S | S(0.20)/S(0.05) = 4 | PASS | {'C1': 4.0, 'C2': 4.0} |
| KT | accounting A(S→c) is not the externality | account_rel_err = 1/ΔE − 1 in static rows | PASS | e.g. 19 for ΔE = 5% |
| PI-set | every grid truth lies in [S−B, S+B] and an endpoint is attained | recomputation per (ΔE, receptor) | PASS | 4 sets |
| PI-set | B labelled finite-grid, not physical; |C−S| not called a bound | text check of report | PASS |  |
| MS | no 'single-member noise' | grep manuscript | PASS |  |
| MS | four-member PI wording in Fig. 11 caption | grep | PASS |  |
| MS | 10/14 described as grid-conditional | grep | PASS |  |
| MS | non-detection ≠ zero effect | grep | PASS |  |
| MS | identified set Eq. (6) present as OMML | count m:oMath | PASS | 6 equations |
| MS | no 'within internal variability' as a positive claim | grep | PASS |  |
| MS | spread saturation not asserted | grep | PASS |  |

## Estimand–assumption map

| quantity | estimand | key assumption | code | manuscript |
|---|---|---|---|---|
| a(S→c) [A] | share of tagged source evaporation precipitating in c | well-mixed column tagging | g3_track.py | Eq. 3 |
| Δ_supply [S] | ΔE_S·a(S→c) | fixed dynamics, assumed ΔE_S | g5_known_truth.py, w12_supply_vs_wrf.py | Eq. 5 |
| TAWE [C] | P_c(WIND) − P_c(CONTROL) in WRF | model-conditional; one realisation | w5_analyse_case.py | Eq. 4 |
| identified set | [S − B, S + B] | assumed |Δ_dynamic| ≤ B | g6c_identification_report.py | Eq. 6 |
| PI flag | |WIND − mean| > t·s·√(1+1/n) | exchangeability, normality | w10_signal_noise.py | Sec. 3.5, 4.8 |

Overall: ALL PASS (21/21).
