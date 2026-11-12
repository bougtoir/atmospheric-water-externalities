# Water-budget reconciliation (v1 accounting shares)

Issue: v1 manuscript reported land 20.1 %, sea 11.1 %, outflow 63.7 % of tagged source evaporation (sum 94.9 %).

Canonical check (`results/track_budget_YYYY.json`, `results/transboundary_share.csv`): for every tag and season

  E_src = P_tag(land) + P_tag(sea) + outflow + storage_end + closure_residual,

with closure_residual/E_src ≤ 4.5e-14 and clip = 0. The missing 5.1 points are **tagged vapour still in the
atmospheric column at the end of the season (storage_end)**; per-season ALL-tag storage/E_src = 0.042 (2016),
0.035 (2017), 0.062 (2018), 0.040 (2019), 0.066 (2020), 0.056 (2021). The storage column was already present in
`transboundary_share.csv` but omitted from the manuscript sentence. No residual category is invented; the shares
close to 1 to round-off. Fix: manuscript now reports all four terms (land, sea, outflow, end-of-season storage).
