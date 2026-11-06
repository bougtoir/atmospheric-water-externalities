"""Restore archived TAWE data from the private LFS archive into this checkout, verifying SHA-256.

Auth: set TAWE_ARCHIVE_TOKEN (GitHub token with read access to the private archive); never commit it.
Usage: python archive/restore_project_data.py --all | --dataset ID [--dataset ID ...] [--archive-dir DIR] [--check-only]
No source dataset is downloaded from its original provider; everything comes from the archive.
"""
import argparse, csv, hashlib, os, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTE = "github.com/bougtoir/tawe-private-research-data.git"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def run(cmd, cwd=None, env=None):
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dataset", action="append", default=[])
    ap.add_argument("--archive-dir", default=os.path.join(REPO, ".archive"))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    tok = os.environ.get("TAWE_ARCHIVE_TOKEN")
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    if not os.path.isdir(os.path.join(a.archive_dir, ".git")):
        if not tok:
            sys.exit("set TAWE_ARCHIVE_TOKEN")
        run(["git", "clone", "-q", f"https://x-access-token:{tok}@{REMOTE}", a.archive_dir], env=env)
    with open(os.path.join(a.archive_dir, "DATA_ARCHIVE_MANIFEST.csv")) as f:
        rows = [r for r in csv.DictReader(f) if a.all or r["dataset_id"] in a.dataset]
    if not rows:
        sys.exit("no matching manifest rows")
    inc = ",".join(r["archive_path"] for r in rows)
    run(["git", "lfs", "pull", "--include", inc], cwd=a.archive_dir)
    bad = 0
    for r in rows:
        src = os.path.join(a.archive_dir, r["archive_path"])
        ok = os.path.exists(src) and sha256(src) == r["sha256"]
        dst = os.path.join(REPO, r["project_path"])
        if ok and not a.check_only:
            if os.path.exists(dst) and sha256(dst) != r["sha256"]:
                print("SKIP existing file differs (not overwritten):", dst); bad += 1; continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
        print("OK " if ok else "BAD", r["object_id"])
        bad += not ok
    print(f"{len(rows) - bad}/{len(rows)} objects verified")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
