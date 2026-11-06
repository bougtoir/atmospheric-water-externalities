"""Seeded initial-condition perturbation for noise-reference runs (CTLPERT*): adds i.i.d. N(0, SIGMA) K
to the perturbation potential temperature T of wrfinput_d01 in the lowest NLEV levels. The seed is the
first 8 bytes of SHA-256 of the experiment name, so reruns are bit-reproducible.

Usage: python scripts/wrf/w4b_perturb_ic.py RUN_DIR EXP_NAME [SIGMA=0.01] [NLEV=10]
"""
import hashlib, json, os, sys
import numpy as np
from netCDF4 import Dataset

run, name = sys.argv[1], sys.argv[2]
sigma = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01
nlev = int(sys.argv[4]) if len(sys.argv) > 4 else 10
seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")
rng = np.random.default_rng(seed)
with Dataset(os.path.join(run, "wrfinput_d01"), "r+") as d:
    t = d["T"][:]
    t[:, :nlev] += rng.normal(0.0, sigma, t[:, :nlev].shape).astype(t.dtype)
    d["T"][:] = t
json.dump(dict(exp=name, seed=seed, sigma_K=sigma, levels=nlev, variable="T"),
          open(os.path.join(run, "ic_perturbation.json"), "w"), indent=1)
print("perturbed", name, seed)
