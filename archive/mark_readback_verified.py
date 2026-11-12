"""Set archive_status to 'ARCHIVED (remote read-back verified DATE)' for datasets whose fresh-clone read-back
(archive/restore_project_data.py --check-only) succeeded. Usage: mark_readback_verified.py DATE DATASET [DATASET ...]"""
import csv, os, sys
A = os.path.expanduser(os.environ.get("TAWE_ARCHIVE_LOCAL", "~/archive/tawe-private-research-data"))
date, ids = sys.argv[1], set(sys.argv[2:])
p = os.path.join(A, "DATA_ARCHIVE_MANIFEST.csv")
rows = list(csv.DictReader(open(p))); fn = list(rows[0].keys()); n = 0
for r in rows:
    if r["dataset_id"] in ids:
        r["archive_status"] = f"ARCHIVED (remote read-back verified {date})"; n += 1
w = csv.DictWriter(open(p, "w", newline=""), fieldnames=fn); w.writeheader(); w.writerows(rows)
print(n, "objects marked")
