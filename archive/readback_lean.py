"""Remote read-back with bounded disk: fresh pointer-only clone of the private archive, then for each dataset
'git lfs fetch' only its objects (no working-tree checkout), verify every object's SHA-256 against the manifest,
and delete the fetched objects before the next dataset. Usage: readback_lean.py WORKDIR DATASET [DATASET ...]
Exit 1 if any object is missing or mismatched. Requires TAWE_ARCHIVE_TOKEN."""
import csv, hashlib, os, shutil, subprocess, sys
REMOTE = "github.com/bougtoir/tawe-private-research-data.git"
wd, ids = sys.argv[1], sys.argv[2:]
env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
shutil.rmtree(wd, ignore_errors=True)
subprocess.run(["git", "clone", "-q", f"https://x-access-token:{os.environ['TAWE_ARCHIVE_TOKEN']}@{REMOTE}", wd], env=env, check=True)
rows = list(csv.DictReader(open(os.path.join(wd, "DATA_ARCHIVE_MANIFEST.csv"))))
bad = 0
for i in ids:
    rs = [r for r in rows if r["dataset_id"] == i]
    if not rs: print("NO ROWS", i); bad += 1; continue
    subprocess.run(["git", "lfs", "fetch", "origin", "--include", ",".join(r["archive_path"] for r in rs)], cwd=wd, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    ok = 0
    for r in rs:
        o = os.path.join(wd, ".git", "lfs", "objects", r["sha256"][:2], r["sha256"][2:4], r["sha256"])
        p = os.path.join(wd, r["archive_path"])
        if os.path.exists(o): f = o
        elif os.path.isfile(p) and os.path.getsize(p) > 1024: f = p  # file stored in git (not LFS)
        elif os.path.isfile(p): f = p
        else: print("MISSING", r["object_id"]); continue
        h = hashlib.sha256()
        with open(f, "rb") as g:
            for b in iter(lambda: g.read(1 << 20), b""): h.update(b)
        if h.hexdigest() == r["sha256"]: ok += 1
        else: print("BAD", r["object_id"])
    print(f"{i} {ok}/{len(rs)} objects verified", flush=True)
    bad += len(rs) - ok
    shutil.rmtree(os.path.join(wd, ".git", "lfs", "objects"), ignore_errors=True)
shutil.rmtree(wd, ignore_errors=True)
sys.exit(1 if bad else 0)
