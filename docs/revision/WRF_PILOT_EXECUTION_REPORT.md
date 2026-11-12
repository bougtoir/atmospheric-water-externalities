# WRF execution and paired contrasts — case `pilot_2020w1`

Analysis window (after 24 h spin-up): 2020-07-01T00:00:00.000000000 to 2020-07-06T00:00:00.000000000.
Farm cells (grid cells containing ≥1 turbine): 141; inner analysis region: 10800 cells (10-cell boundary margin removed).

Wall-clock: CONTROL wallclock_s 11891; WIND wallclock_s 11133; CTLPERT_1_INVALID wallclock_s 10736; CTLPERT_1 wallclock_s 11829

All contrasts are model-conditional differences within this WRF configuration (evidence class [C]).

## CTLPERT_1 − CONTROL

| field | inner-domain mean Δ | farm-cell mean Δ | inner max |Δ| |
|---|---|---|---|
| P_acc_mm | -0.01596 | -0.1196 | 21.06 |
| E_acc_mm | 0.008519 | 0.004964 | 1.777 |
| W | -3.568e-05 | -0.006231 | 0.3478 |
| COND | -0.000356 | -0.0009911 | 0.1152 |
| IVTx | 0.04222 | 0.007242 | 3.568 |
| IVTy | 0.0004625 | 0.03363 | 3.162 |
| hub_wind | 0.002381 | 0.008101 | 0.3397 |
| U10 | 0.001774 | 0.005965 | 0.2753 |
| T2 | 0.002735 | -0.001625 | 0.1924 |
| Q2 | 1.236e-06 | 3.977e-07 | 8.583e-05 |
| LH | 0.03801 | 0.02123 | 11.2 |
| HFX | 0.008853 | -0.01435 | 10.17 |
| PBLH | 0.005637 | -0.4032 | 46.09 |

P_inner_total_kg: CONTROL 5.465e+13 kg; Δ -3.88e+10 kg (-0.071 %)

E_inner_total_kg: CONTROL 4.245e+13 kg; Δ 2.065e+10 kg (0.0486 %)

E_farm_total_kg: CONTROL 4.116e+11 kg; Δ 1.591e+08 kg (0.0387 %)

| country | cells | P CONTROL (kg) | ΔP (kg) | ΔP (mm) | ΔE (kg) |
|---|---|---|---|---|---|
| AT | 149 | 1.586e+12 | -2.975e+10 | -0.892 | -2.18e+09 |
| NO | 258 | 3.214e+12 | -2.089e+10 | -0.361 | -1.746e+09 |
| LV | 63 | 5.571e+11 | -1.164e+10 | -0.82 | -8.048e+08 |
| FR | 824 | 2.095e+12 | -8.649e+09 | -0.0467 | -1.247e+09 |
| LT | 52 | 3.844e+11 | -5.57e+09 | -0.474 | -2.723e+08 |
| CZ | 345 | 1.513e+12 | -3.824e+09 | -0.0492 | -8.692e+08 |
| RU | 46 | 2.543e+11 | -3.797e+08 | -0.0365 | -1.225e+09 |
| BE | 135 | 6.221e+11 | -3.781e+08 | -0.0126 | 1.583e+08 |
| IM | 4 | 1.109e+10 | -2.577e+08 | -0.285 | 1.49e+07 |
| GG | 1 | 6.139e+08 | -2.964e+06 | -0.0132 | 1.16e+06 |
| LU | 11 | 1.692e+10 | 3.449e+08 | 0.139 | -6.517e+07 |
| EE | 21 | 2.611e+11 | 1.539e+09 | 0.326 | 4.79e+08 |
| NL | 165 | 7.109e+11 | 2.032e+09 | 0.0545 | 1.764e+07 |
| GB | 989 | 5.46e+12 | 2.233e+09 | 0.00989 | 5.394e+09 |
| SK | 154 | 1.671e+12 | 2.372e+09 | 0.0684 | 9.455e+09 |
| DK | 183 | 1.147e+12 | 3.335e+09 | 0.0805 | 9.55e+08 |
| HU | 66 | 8.365e+11 | 5.669e+09 | 0.383 | 3.228e+09 |
| SE | 609 | 4.738e+12 | 1.28e+10 | 0.0941 | 3.757e+09 |
| PL | 985 | 4.734e+12 | 1.833e+10 | 0.0831 | 4.1e+09 |
| DE | 1520 | 7.343e+12 | 1.949e+10 | 0.0571 | 2.933e+09 |

## WIND − CONTROL

| field | inner-domain mean Δ | farm-cell mean Δ | inner max |Δ| |
|---|---|---|---|
| P_acc_mm | -0.02224 | 0.4351 | 26.39 |
| E_acc_mm | 0.006732 | 0.07988 | 1.988 |
| W | -0.001728 | -0.002944 | 0.2246 |
| COND | -0.0001207 | 0.001828 | 0.1122 |
| IVTx | -0.03648 | -0.7674 | 3.672 |
| IVTy | -0.005831 | -0.07143 | 2.572 |
| hub_wind | -0.01117 | -0.3464 | 1.091 |
| U10 | -0.001271 | -0.04959 | 0.4366 |
| T2 | 0.001105 | 0.01074 | 0.1314 |
| Q2 | -1.021e-06 | -2.386e-05 | 0.0001049 |
| LH | 0.04125 | 0.4743 | 11.27 |
| HFX | -0.00991 | -0.2852 | 9.623 |
| PBLH | 0.3989 | 9.166 | 46.95 |

P_inner_total_kg: CONTROL 5.465e+13 kg; Δ -5.398e+10 kg (-0.0988 %)

E_inner_total_kg: CONTROL 4.245e+13 kg; Δ 1.637e+10 kg (0.0386 %)

E_farm_total_kg: CONTROL 4.116e+11 kg; Δ 2.545e+09 kg (0.618 %)

Mean simulated fleet power: 13.78 GW

| country | cells | P CONTROL (kg) | ΔP (kg) | ΔP (mm) | ΔE (kg) |
|---|---|---|---|---|---|
| AT | 149 | 1.586e+12 | -6.821e+10 | -2.04 | -9.414e+07 |
| GB | 989 | 5.46e+12 | -1.909e+10 | -0.0854 | -1.318e+09 |
| CZ | 345 | 1.513e+12 | -1.631e+10 | -0.212 | -5.884e+08 |
| LV | 63 | 5.571e+11 | -1.432e+10 | -1.01 | 5.096e+07 |
| DE | 1520 | 7.343e+12 | -1.012e+10 | -0.0291 | -2.329e+09 |
| SE | 609 | 4.738e+12 | -7.047e+09 | -0.0512 | -7.793e+08 |
| EE | 21 | 2.611e+11 | -6.577e+09 | -1.39 | -4.26e+08 |
| DK | 183 | 1.147e+12 | -1.94e+09 | -0.0469 | -1.989e+09 |
| PL | 985 | 4.734e+12 | -1.542e+09 | -0.00684 | 9.765e+09 |
| BE | 135 | 6.221e+11 | -1.161e+09 | -0.0382 | -1.423e+07 |
| LT | 52 | 3.844e+11 | -4.877e+08 | -0.0416 | -9.498e+08 |
| IM | 4 | 1.109e+10 | -3.477e+07 | -0.0384 | 9e+07 |
| GG | 1 | 6.139e+08 | -2.81e+07 | -0.125 | -2.825e+06 |
| LU | 11 | 1.692e+10 | 3.829e+08 | 0.155 | 1.391e+07 |
| NL | 165 | 7.109e+11 | 2.353e+09 | 0.0629 | 2.429e+08 |
| FR | 824 | 2.095e+12 | 3.374e+09 | 0.0184 | 1.826e+09 |
| NO | 258 | 3.214e+12 | 5.351e+09 | 0.092 | -2.41e+09 |
| RU | 46 | 2.543e+11 | 8.567e+09 | 0.824 | 1.561e+09 |
| SK | 154 | 1.671e+12 | 1.246e+10 | 0.361 | 5.302e+09 |
| HU | 66 | 8.365e+11 | 2.733e+10 | 1.85 | 2.407e+09 |


## Pilot-stage signal versus one perturbed member (WIND−CONTROL vs CTLPERT_1−CONTROL)

> Superseded. This section records the pilot stage, when only CTLPERT_1 existed. The final analysis compares WIND with the
> 95% prediction interval derived from the four-member no-wind ensemble (CONTROL, CTLPERT_1–3); see
> WRF_MAIN_EXPERIMENT_REPORT.md and WRF_PREDICTION_INTERVAL_AUDIT.md. The values below are pilot-stage values.

From `results/wrf/pilot_2020w1/signal_noise.json` (`scripts/wrf/w10_signal_noise.py`). RMS over inner-domain cells by
distance from the nearest farm cell. One perturbed member is one draw of intrinsic variability; ratios are descriptive.

| field | band | cells | RMS signal | RMS noise | ratio |
|---|---|---|---|---|---|
| P_acc_mm | farm_0_30km | 792 | 1.174 | 0.8871 | 1.32 |
| P_acc_mm | near_30_150km | 3939 | 1.227 | 1.247 | 0.984 |
| P_acc_mm | far_gt150km | 6069 | 2.668 | 2.582 | 1.03 |
| E_acc_mm | farm_0_30km | 792 | 0.1332 | 0.09875 | 1.35 |
| E_acc_mm | near_30_150km | 3939 | 0.1421 | 0.1447 | 0.982 |
| E_acc_mm | far_gt150km | 6069 | 0.2201 | 0.2307 | 0.954 |
| W | farm_0_30km | 792 | 0.03103 | 0.02306 | 1.35 |
| W | near_30_150km | 3939 | 0.02807 | 0.02461 | 1.14 |
| W | far_gt150km | 6069 | 0.03905 | 0.04037 | 0.967 |
| COND | farm_0_30km | 792 | 0.006307 | 0.006435 | 0.98 |
| COND | near_30_150km | 3939 | 0.006789 | 0.006883 | 0.986 |
| COND | far_gt150km | 6069 | 0.009759 | 0.007752 | 1.26 |
| IVTx | farm_0_30km | 792 | 0.9353 | 0.4549 | 2.06 |
| IVTx | near_30_150km | 3939 | 0.6188 | 0.4679 | 1.32 |
| IVTx | far_gt150km | 6069 | 0.6939 | 0.6514 | 1.07 |
| IVTy | farm_0_30km | 792 | 0.4968 | 0.3066 | 1.62 |
| IVTy | near_30_150km | 3939 | 0.3898 | 0.3517 | 1.11 |
| IVTy | far_gt150km | 6069 | 0.5069 | 0.4832 | 1.05 |
| hub_wind | farm_0_30km | 792 | 0.247 | 0.0359 | 6.88 |
| hub_wind | near_30_150km | 3939 | 0.04915 | 0.03714 | 1.32 |
| hub_wind | far_gt150km | 6069 | 0.03929 | 0.04122 | 0.953 |
| U10 | farm_0_30km | 792 | 0.06554 | 0.02697 | 2.43 |
| U10 | near_30_150km | 3939 | 0.03169 | 0.02877 | 1.1 |
| U10 | far_gt150km | 6069 | 0.02318 | 0.02476 | 0.936 |
| T2 | farm_0_30km | 792 | 0.01502 | 0.01269 | 1.18 |
| T2 | near_30_150km | 3939 | 0.01874 | 0.01676 | 1.12 |
| T2 | far_gt150km | 6069 | 0.02638 | 0.02712 | 0.973 |
| Q2 | farm_0_30km | 792 | 1.665e-05 | 8.957e-06 | 1.86 |
| Q2 | near_30_150km | 3939 | 1.036e-05 | 9.06e-06 | 1.14 |
| Q2 | far_gt150km | 6069 | 1.815e-05 | 1.705e-05 | 1.06 |
| LH | farm_0_30km | 792 | 0.8529 | 0.6745 | 1.26 |
| LH | near_30_150km | 3939 | 1.097 | 1.094 | 1 |
| LH | far_gt150km | 6069 | 1.595 | 1.65 | 0.967 |
| HFX | farm_0_30km | 792 | 0.7411 | 0.6964 | 1.06 |
| HFX | near_30_150km | 3939 | 1.045 | 1.05 | 0.996 |
| HFX | far_gt150km | 6069 | 1.307 | 1.331 | 0.982 |
| PBLH | farm_0_30km | 792 | 6.444 | 2.848 | 2.26 |
| PBLH | near_30_150km | 3939 | 3.269 | 2.898 | 1.13 |
| PBLH | far_gt150km | 6069 | 5.107 | 5.361 | 0.953 |

Country totals with the noise reference: `results/wrf/pilot_2020w1/country_signal_noise.csv`;
supply-channel [S] versus WRF [C]: `results/wrf/pilot_2020w1/supply_vs_wrf.{csv,json}`.
