"""Free disk held by redundant local copies inside the private-archive clone, never touching project files.
(1) For every manifest object whose remote commit is pushed (local HEAD == origin HEAD) and whose project copy has the
manifest SHA-256: delete the .git/lfs/objects cache copy if it is a separate inode from the project file.
(2) For read-back-verified objects whose archive working-tree file is a separate copy (not a hard link of the project
file): replace it with its LFS pointer. Remote + project copies remain. Logged to archive/PURGE_LEDGER.csv."""
import csv, datetime, hashlib, os, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.expanduser("~/archive/tawe-private-research-data")
g = lambda *c: subprocess.run(["git", *c], cwd=A, capture_output=True, text=True, check=True).stdout.split()[0]
assert g("rev-parse", "HEAD") == g("ls-remote", "origin", "HEAD"), "archive HEAD not pushed"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1"); freed = 0
with open(os.path.join(REPO, "archive", "PURGE_LEDGER.csv"), "a", newline="") as f:
    w = csv.writer(f)
    for r in csv.DictReader(open(os.path.join(A, "DATA_ARCHIVE_MANIFEST.csv"))):
        lp, ap = os.path.join(REPO, r["project_path"]), os.path.join(A, r["archive_path"])
        o = os.path.join(A, ".git", "lfs", "objects", r["sha256"][:2], r["sha256"][2:4], r["sha256"])
        if not os.path.isfile(lp) or os.path.getsize(lp) != int(r["bytes"]) or int(r["bytes"]) < 2**20: continue
        st = os.stat(lp)
        cand_o = os.path.exists(o) and os.stat(o).st_ino != st.st_ino
        cand_a = ("read-back verified" in r["archive_status"] and os.path.isfile(ap) and os.path.getsize(ap) > 1024
                  and os.stat(ap).st_ino != st.st_ino)
        if not (cand_o or cand_a) or sha(lp) != r["sha256"]: continue
        if cand_o:
            freed += os.path.getsize(o); os.remove(o)
            w.writerow([now, r["object_id"], ".git/lfs cache", r["bytes"], r["sha256"], "LFS cache copy dropped (pushed; project copy kept)"])
        if cand_a:
            freed += os.path.getsize(ap); os.remove(ap)
            subprocess.run(["git", "checkout", "--", r["archive_path"]], cwd=A, env=env, check=True)
            w.writerow([now, r["object_id"], r["archive_path"], r["bytes"], r["sha256"], "archive working copy -> LFS pointer (read-back verified; project copy kept)"])
print(f"freed {freed / 1e9:.2f} GB")
