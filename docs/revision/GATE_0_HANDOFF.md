# Gate 0 handoff
Status: PASS. Baseline hashes in `BASELINE_LOCK.md`; revision branch created; private archive
`bougtoir/tawe-private-research-data` created (visibility PRIVATE verified), initial commit with 99 objects
(5.3 GB, Git LFS) pushed (push exit 0). Remote read-back: isolated clone + `restore_project_data.py --all`
(see `DATA_RESTORATION_TEST.md`).

Later archive batches are not covered by the 99/99 read-back above:
- `8a71fa6`: WPS geography (LFS).
- `d0dc95b`: pilot WRF forcing.

These batches are push-verified only (exit 0). Read-back for them, and for all WRF outputs, is recorded
separately in `PRIVATE_ARCHIVE_REPRODUCIBILITY.md` (Gate 10).
