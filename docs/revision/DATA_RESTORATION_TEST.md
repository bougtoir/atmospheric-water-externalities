# Data restoration test (isolated clean workspace)

Procedure (2026-11-06): fresh clone of the public repository into `~/restore_test/pub` (no data present),
then `TAWE_ARCHIVE_TOKEN=<token> python restore_project_data.py --all`. The script cloned the private archive
with `GIT_LFS_SKIP_SMUDGE=1`, fetched all LFS objects from GitHub (`git lfs pull`), verified SHA-256 against
`DATA_ARCHIVE_MANIFEST.csv` and copied objects into the project paths.

Result: **99/99 objects verified** (ERA5 JJA 2016–2021 column fields, boundaries, turbine register, literature
snapshots, masks, tracking outputs, canonical v1 results, v1 submission ZIPs). No source dataset was downloaded
from ECMWF/Google/Natural Earth. Later batches (WRF forcing, WPS, WRF outputs) are re-tested in Gate 10.

## Read-back 2 — WRF forcing, WPS geography and pilot WRF case (2026-11-06)

Private archive commit `6dcc5c2` (push exit 0). Fresh clone of the private archive into an empty directory with
`GIT_LFS_SKIP_SMUDGE=1`, then `restore_project_data.py --check-only` for datasets `era5_wrf_forcing`,
`wps_geog_low_res`, `wrf_pilot_2020w1` (WPS intermediates and met_em), `wrf_pilot_2020w1_CONTROL`,
`wrf_pilot_2020w1_WIND`, `wrf_pilot_2020w1_CTLPERT_1_INVALID_unperturbed_THM` and `wrf_pilot_2020w1_logs`.
All LFS objects were downloaded from GitHub and checked against the manifest SHA-256.

Result: **240/240 objects verified**. The read-back directory was deleted afterwards (a verified copy).
WRF NetCDF files were archived after lossless deflate compression; each compressed file was checked
variable-by-variable against its original before replacement (`COMPRESSION_LEDGER.csv` in each run directory
records both SHA-256 values).

## Read-back 3 — WRF case e2017w (2026-11-06)

Private archive commit `9fea214` (push exit 0). Fresh clone into an empty directory and
`restore_project_data.py --check-only` for `wrf_e2017w`, `wrf_e2017w_CONTROL`, `wrf_e2017w_WIND`,
`wrf_e2017w_logs`: **193/193 objects verified**. Read-back directory deleted afterwards.
