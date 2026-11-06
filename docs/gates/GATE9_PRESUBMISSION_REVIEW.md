# Gate 9 — Hostile pre-submission review (reviewer view) and QC

## Highest priority (resolve or disclose before submission)
1. **Single-layer tagging (model structure).** Reviewers will ask for a two-layer/Lagrangian comparison
   (WAM2layers v3, UTrack). Disclosed in Discussion; not executed. Fix: run WAM2layers on the same domain/seasons
   (needs pressure/model-level ERA5, ~10× data) or compare against the published UTrack atlas footprints.
2. **No causal estimate.** The paper's value rests on the framework and the identifiability result. Framing is
   consistently [A]/[S]; TAWE declared not identified; WRF suite declared NOT RUN.
3. **Manuscript length** (`results/manuscript_wordcount.json`) is short for an EMS research article; EMS has no
   hard limit, but reviewers may ask for more method detail (algorithm listing, software architecture, test suite).

## High priority
4. Domain truncation: ~64% of tagged moisture leaves the domain; receptor coefficients are in-domain lower bounds;
   countries extending beyond the domain are excluded (list in `data/processed/grid_masks_log.json`).
5. Detectability uses interannual SD from 6 seasons only (uncertain SD); conclusion (factor ≫ 1) is robust to this.
6. Placebo design: translations ≤3° keep cluster shape; alternative placebo designs (latitude-matched, coast-distance
   matched) would strengthen the test.

## Medium / optional
7. Known-truth world is idealised (linear, 2-D). 8. ERA5 precipitation/evaporation biases are not propagated.
9. Owner assignment by largest capacity per 0.25° cell; single-cell owners (IE, NO) appear only in the ALL tag.

## Mechanical QC (`scripts/g9_qc.py` → `results/qc_report.json`)
Abstract ≤150 words, 1–7 keywords, 3–5 highlights ≤85 characters, software/data availability, CRediT, competing
interests, GenAI declaration placeholder, acknowledgements before references, figures as separate files and cited
in order 1–6, Table 1 cited, author–date references alphabetical with Crossref-verified DOIs, no priority words,
no repository paths in prose, numeric provenance (every body number traced to results files or design constants),
ZIP integrity with relative arcnames. Fabrication audit: no synthetic result is presented as an atmospheric
simulation; the known-truth world is labelled idealised. Hard-code audit: manuscript numbers are read from
`results/manuscript_values.json`, which is computed from results CSV/JSON at build time.
