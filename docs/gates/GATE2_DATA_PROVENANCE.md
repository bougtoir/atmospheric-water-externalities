# Gate 2 — Data and provenance

| Data | Source / version | Local path | Ledger | Terms | Public repo? |
|---|---|---|---|---|---|
| ERA5 hourly column budget (W, F_u, F_v, E, P), 0.25°, 20°W–35°E, 35–72°N, JJA 2016–2021 | ARCO-ERA5 Zarr v3 `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3` (anonymous) | `data/raw/era5/era5_colbudget_YYYY-MM.nc` (~0.3 GB each, VM-persistent) | `data/raw/era5/LEDGER.csv` (URL, time range, UTC retrieval, bytes, SHA-256) | Copernicus licence | No (size); re-fetch with `scripts/g2_fetch_era5.py`, verify SHA-256 against ledger |
| Turbine register (140,010 turbines; offshore subset) | `bougtoir/ecm-wind-heatwave` main `03e3c19`, `data/processed/turbines.csv` (read-only reference) | `data/raw/turbines_from_ecm_wind_heatwave.csv` | SHA-256 in `data/raw/LEDGER.csv` | as documented in that repository | Yes (copy) |
| Country polygons | Natural Earth 1:50m admin-0 (public domain) | `data/raw/boundaries/ne_50m_admin_0_countries.zip` | `data/raw/boundaries/LEDGER.csv` | Public domain | Yes |
| Literature search | OpenAlex (first page per query, 25 records; not exhaustive) | `data/raw/literature/openalex/` | `LEDGER.csv` + `queries.txt` | CC0 | Yes |
| Reference metadata | Crossref REST API | `references/crossref_raw/` | `LEDGER.csv` | CC0 metadata | Yes |
| Journal guide | EMS Guide for Authors, Aims & Scope, OA page (rendered text via Chrome) | `docs/journal_guides/` | `LEDGER.csv` | Elsevier web pages (snapshot for compliance only) | Yes |

Derived (regenerable): `data/processed/grid_masks.npz` (country raster, owner masks per season, placebo masks),
`data/processed/track_YYYY.npz` (tagged precipitation fields; not in git), `results/*.csv|json`.

Conventions: ERA5 accumulations at hour t cover (t−1 h, t]; instantaneous fields averaged over t−1 and t.
Negative evaporation (dew/condensation) and negative precipitation round-off are set to zero for tagging.
Offshore turbines with missing commissioning date are excluded from source masks (count in
`data/processed/grid_masks_log.json`). Owner masks use turbines commissioned before 1 June of each season.
