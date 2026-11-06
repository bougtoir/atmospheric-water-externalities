"""Seeded initial-condition perturbation for noise-reference runs (CTLPERT*): adds i.i.d. N(0, SIGMA) K
to the perturbation potential temperature T of wrfinput_d01 in the lowest NLEV levels. With use_theta_m=1
(WRF v4 default) the prognostic variable is the moist potential temperature THM, so the same perturbation is
applied to THM scaled by (1 + Rv/Rd qv); perturbing T alone leaves the integration bit-identical to CONTROL.
The seed is the first 8 bytes of SHA-256 of the experiment name, so reruns are bit-reproducible.

Usage: python scripts/wrf/w4b_perturb_ic.py RUN_DIR EXP_NAME [SIGMA=0.01] [NLEV=10]
"""
import hashlib, json, os, sys
import numpy as np
from netCDF4 import Dataset

RV_RD = 461.6 / 287.0
run, name = sys.argv[1], sys.argv[2]
sigma = float(sys.argv[3]) if len(sys.argv) > 3 else 0.01
nlev = int(sys.argv[4]) if len(sys.argv) > 4 else 10
seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")
rng = np.random.default_rng(seed)
with Dataset(os.path.join(run, "wrfinput_d01"), "r+") as d:
    t = d["T"][:]
    dt = rng.normal(0.0, sigma, t[:, :nlev].shape).astype(t.dtype)
    t[:, :nlev] += dt
    d["T"][:] = t
    vars_ = ["T"]
    if "THM" in d.variables:
        thm, qv = d["THM"][:], d["QVAPOR"][:]
        thm[:, :nlev] += (dt * (1.0 + RV_RD * qv[:, :nlev])).astype(thm.dtype)
        d["THM"][:] = thm
        vars_.append("THM")
with Dataset(os.path.join(run, "wrfinput_d01")) as d:
    max_abs = {v: float(np.abs(d[v][:, :nlev]).max()) for v in vars_}
assert np.abs(dt).max() > 0
json.dump(dict(exp=name, seed=seed, sigma_K=sigma, levels=nlev, variables=vars_, max_abs_dT=float(np.abs(dt).max())),
          open(os.path.join(run, "ic_perturbation.json"), "w"), indent=1)
print("perturbed", name, seed, vars_)
