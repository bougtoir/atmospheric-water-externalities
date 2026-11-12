# Gate 0 — Literature, novelty and EMS scope audit

Access date: 2026-11-05/06 (UTC 2026-11-05). Evidence: `references/crossref_raw/*.json` (Crossref, 29 DOIs, ledger
`references/crossref_raw/LEDGER.csv`), `data/raw/literature/openalex/q01–q10.json` (OpenAlex first result page,
25 records per query; **not exhaustive**), live EMS guide snapshots in `docs/journal_guides/` (ledger with SHA-256).

## 1. Literature matrix (verified DOIs only; key = `references/references_verified.csv`)

| Strand | Keys | What they establish | What they do not do |
|---|---|---|---|
| Moisture-recycling governance / precipitationsheds | keys2012, keys2016, keys2017, keys2018, teklemariam2019, transprecip2026, keune2019 | Upwind evaporation sustains downwind precipitation across borders; governance framing; recycling networks | No energy-infrastructure intervention; source–receptor *accounting*, not counterfactual change |
| Moisture tracking models | vanderent2013, wam2layers2025, eulerlagr2024, multimodel2025, tuinenburg2020, lagrframe2022, lagrglobal2022, trenberth1999 | Eulerian/Lagrangian tagging of evaporation to precipitation; large inter-model spread | Tagging attributes *existing* moisture; it does not identify the effect of perturbing a source |
| Wind-farm atmospheric effects (models) | fitch2012, fischereit2022, pryor2020, giantwf2011, akhtar2026, southbight2026 | Wind-farm parameterisations alter BL winds, TKE, humidity, local precipitation; responses parameterisation-sensitive | No conservation-closed partition of the response across jurisdictions; no identifiability analysis |
| Wind-farm effects (observations) | alfahel2020, siedersleben2018, surfaceimpacts2022, fluxes2014 | Observed near-farm changes in fluxes/humidity; onshore precipitation change after installation | Single-site / before–after designs; confounded by weather variability |
| Wake externalities (economic) | lundquist2019 | Transboundary-type wake externalities between farms are real and costly | Concerns wind resource, not water |
| Reanalysis | hersbach2020 | ERA5 column budget fields | ERA5 contains **no wind-farm parameterisation**; it cannot carry the intervention |

## 2. Novelty audit (bounded)

Searched (OpenAlex, 10 queries, first page each; Crossref title checks) for work that defines a
conservation-closed, jurisdiction-resolved precipitation externality of energy infrastructure and evaluates its
identifiability. **Not found in the searched set.** Closest: (i) moisture-recycling governance (accounting of
existing flows, no intervention), (ii) WRF wind-farm precipitation studies (counterfactual change, but no
source–receptor partition or identifiability limits). This is a bounded statement, not a priority claim; the
manuscript must not use "first"/"novel".

## 3. EMS scope fit (live guide, `docs/journal_guides/EMS_*`)

- Scope lists "model development, model evaluation, process identification", "sensitivity and uncertainty
  assessment", "quality assurance and evaluation of models", and "global pollution and global climate change"
  applications → a conservation-checked tracking tool + identifiability/validation framework fits **research article**.
- EMS requires: abstract ≤150 words; 1–7 keywords; 3–5 highlights ≤85 characters (separate file, name contains
  "highlights"); graphical abstract **required**; figures as separate files; "Software and/or data availability"
  section; single-anonymised review; Elsevier author–date reference style (applied at proof); hybrid journal
  (subscription route no fee; OA APC USD 3570 per live OA page).
- Scope risk: EMS expects generalisable modelling insight and substantial testing/comparison with alternatives.
  A pure European case study without method evaluation would be out of scope.

## Gate 0 verdict: PASS (proceed), with the constraint that the contribution is a method + identifiability
framework, not a claimed causal estimate.
