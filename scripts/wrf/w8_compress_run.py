"""Lossless in-place compression of a finished WRF experiment directory (netCDF deflate level 4 + shuffle).

Usage: python scripts/wrf/w8_compress_run.py RUN_DIR
For every wrfout*/wrfsfc*/wrfrst*/wrfinput*/wrfbdy*/met_em* file: nccopy -d4 -s to a temporary file, verify
that every variable is bit-identical (NaN-aware) and every attribute is equal, then replace the original.
Original and compressed SHA-256 are appended to RUN_DIR/COMPRESSION_LEDGER.csv.
"""
import csv, glob, hashlib, os, subprocess, sys
import numpy as np, xarray as xr


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


run = sys.argv[1]; led = os.path.join(run, "COMPRESSION_LEDGER.csv")
done = set()
if os.path.exists(led):
    done = {r["file"] for r in csv.DictReader(open(led))}
files = sorted(f for p in ("wrfout*", "wrfsfc*", "wrfrst*", "wrfinput*", "wrfbdy*", "met_em*")
               for f in glob.glob(os.path.join(run, p)) if not os.path.islink(f))
new = not os.path.exists(led)
with open(led, "a", newline="") as fh:
    w = csv.writer(fh)
    if new: w.writerow(["file", "orig_bytes", "orig_sha256", "comp_bytes", "comp_sha256", "verified"])
    for f in files:
        b = os.path.basename(f)
        if b in done: continue
        o_sha, o_b = sha(f), os.path.getsize(f); tmp = f + ".z.tmp"
        subprocess.run(["nccopy", "-k", "nc4", "-d", "4", "-s", f, tmp], check=True)
        a, c = xr.open_dataset(f, decode_times=False, mask_and_scale=False), xr.open_dataset(tmp, decode_times=False, mask_and_scale=False)
        ok = all(np.array_equal(np.asarray(a.attrs[k]), np.asarray(c.attrs.get(k))) for k in a.attrs) and set(a.attrs) == set(c.attrs) and set(a.variables) == set(c.variables) and all(
            np.array_equal(a[v].values, c[v].values, equal_nan=a[v].dtype.kind == "f") for v in a.variables)
        a.close(); c.close()
        if not ok:
            os.remove(tmp); print("VERIFY FAIL", f); sys.exit(1)
        os.replace(tmp, f); w.writerow([b, o_b, o_sha, os.path.getsize(f), sha(f), True]); fh.flush()
        print(b, o_b, "->", os.path.getsize(f), flush=True)
