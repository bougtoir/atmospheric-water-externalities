# Data restoration test (isolated clean workspace)

Procedure (2026-11-06): fresh clone of the public repository into `~/restore_test/pub` (no data present),
then `TAWE_ARCHIVE_TOKEN=<token> python restore_project_data.py --all`. The script cloned the private archive
with `GIT_LFS_SKIP_SMUDGE=1`, fetched all LFS objects from GitHub (`git lfs pull`), verified SHA-256 against
`DATA_ARCHIVE_MANIFEST.csv` and copied objects into the project paths.

Result: **99/99 objects verified** (ERA5 JJA 2016–2021 column fields, boundaries, turbine register, literature
snapshots, masks, tracking outputs, canonical v1 results, v1 submission ZIPs). No source dataset was downloaded
from ECMWF/Google/Natural Earth. Later batches (WRF forcing, WPS, WRF outputs) are re-tested in Gate 10.
