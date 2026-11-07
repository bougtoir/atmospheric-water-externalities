"""Free local disk for datasets already pushed AND read back from the private archive.

For each object of the given datasets whose manifest status is 'ARCHIVED (remote read-back verified ...)':
re-hash the local project file against the manifest SHA-256, delete it, replace the archive working-tree copy
with its LFS pointer and drop the cached LFS object. Every purge is appended to archive/PURGE_LEDGER.csv.
Restore with: python archive/restore_project_data.py --dataset ID
Usage: purge_local_verified.py DATASET [DATASET ...]"""
import csv, datetime, hashlib, os, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.expanduser(os.environ.get("TAWE_ARCHIVE_LOCAL", "~/archive/tawe-private-research-data"))
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
ids = set(sys.argv[1:]); now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rows = [r for r in csv.DictReader(open(os.path.join(A, "DATA_ARCHIVE_MANIFEST.csv"))) if r["dataset_id"] in ids]
bad = [r["object_id"] for r in rows if "read-back verified" not in r["archive_status"]]
if bad: sys.exit(f"refusing: {len(bad)} objects not read-back verified, e.g. {bad[0]}")
led = os.path.join(REPO, "archive", "PURGE_LEDGER.csv"); new = not os.path.exists(led); freed = 0
with open(led, "a", newline="") as f:
    w = csv.writer(f)
    if new: w.writerow(["purged_utc", "object_id", "project_path", "bytes", "sha256", "archive_status"])
    for r in rows:
        lp, ap = os.path.join(REPO, r["project_path"]), os.path.join(A, r["archive_path"])
        if os.path.isfile(lp) and not os.path.islink(lp):
            if sha(lp) != r["sha256"]: sys.exit(f"local copy differs from archive: {lp}")
            os.remove(lp); freed += int(r["bytes"])
        o = os.path.join(A, ".git", "lfs", "objects", r["sha256"][:2], r["sha256"][2:4], r["sha256"])
        if os.path.exists(o): os.remove(o)
        if os.path.isfile(ap) and os.path.getsize(ap) > 1024:
            os.remove(ap)
            subprocess.run(["git", "checkout", "--", r["archive_path"]], cwd=A, check=True,
                           env=dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"))
        w.writerow([now, r["object_id"], r["project_path"], r["bytes"], r["sha256"], r["archive_status"]])
print(f"purged {len(rows)} objects, {freed / 1e9:.2f} GB local project data")
