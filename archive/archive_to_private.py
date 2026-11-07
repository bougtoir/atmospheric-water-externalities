"""Register project data in the private LFS archive (bougtoir/tawe-private-research-data).

Usage: python archive/archive_to_private.py CATEGORY DATASET_ID SRC_PATH [SRC_PATH ...] --meta key=value ...
Copies each file into <archive>/objects/<CATEGORY>/<relative path>, records it in
DATA_ARCHIVE_MANIFEST.csv and never overwrites an archived object with different content.
"""
import argparse, csv, hashlib, os, shutil, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.environ.get("TAWE_ARCHIVE_DIR", os.path.expanduser("~/archive/tawe-private-research-data"))
FIELDS = ["object_id", "dataset_id", "dataset_name", "category", "source", "source_url", "access_date_utc", "license",
          "original_filename", "project_path", "bytes", "sha256", "spatial_coverage", "temporal_coverage", "variables",
          "format", "processing_status", "archive_path", "remote_object_id", "archive_status", "restore_command",
          "related_scripts"]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load(man):
    if not os.path.exists(man):
        return {}
    with open(man) as f:
        return {r["object_id"]: r for r in csv.DictReader(f)}


def save(man, rows):
    with open(man, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for k in sorted(rows):
            w.writerow(rows[k])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("category", choices=["RAW", "INTERMEDIATE", "SIMULATION", "ANALYSIS", "DOCUMENTATION"])
    ap.add_argument("dataset_id")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--meta", nargs="*", default=[])
    a = ap.parse_args()
    meta = dict(m.split("=", 1) for m in a.meta)
    man = os.path.join(ARCH, "DATA_ARCHIVE_MANIFEST.csv")
    rows = load(man)
    for p in a.paths:
        p = os.path.abspath(p)
        rel = os.path.relpath(p, REPO) if p.startswith(REPO) else os.path.relpath(p, os.path.expanduser("~"))
        dst_rel = os.path.join("objects", a.category, rel)
        if os.environ.get("ARCHIVE_VERSIONED"):  # re-archived, rewritable outputs (logs, analysis): new dataset version
            dst_rel = os.path.join("objects", a.category, "versions", a.dataset_id, rel)
        dst = os.path.join(ARCH, dst_rel)
        h = sha256(p)
        oid = f"{a.dataset_id}:{rel}"
        if oid in rows and rows[oid]["sha256"] == h and rows[oid]["archive_path"] == dst_rel:
            pass  # already registered with identical content (archive copy may be an LFS pointer after purge)
        elif os.path.exists(dst):
            if sha256(dst) != h:
                sys.exit(f"REFUSE overwrite with different content: {dst}")
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # Hard-link only large model files (replaced atomically, never rewritten in place); copy small files,
            # which analysis scripts may rewrite in place and would otherwise alter the archived copy.
            try:
                if os.path.getsize(p) < 50 * 2**20 or p.startswith("results"):
                    raise OSError
                os.link(p, dst)
            except OSError:
                shutil.copy2(p, dst)
            if sha256(dst) != h:
                sys.exit(f"copy checksum mismatch: {dst}")
        r = rows.get(oid, {k: "" for k in FIELDS})
        r.update({k: v for k, v in meta.items() if k in FIELDS})
        r.update(object_id=oid, dataset_id=a.dataset_id, category=a.category, original_filename=os.path.basename(p),
                 project_path=rel, bytes=str(os.path.getsize(p)), sha256=h, archive_path=dst_rel,
                 remote_object_id=f"lfs-sha256:{h}" if os.path.getsize(p) > 0 else "git-blob",
                 archive_status=r.get("archive_status") or "STAGED",
                 restore_command=f"python archive/restore_project_data.py --dataset {a.dataset_id}")
        r.setdefault("access_date_utc", "")
        if not r["access_date_utc"]:
            r["access_date_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows[oid] = r
    save(man, rows)
    print(len(a.paths), "objects registered;", len(rows), "in manifest")


if __name__ == "__main__":
    main()
