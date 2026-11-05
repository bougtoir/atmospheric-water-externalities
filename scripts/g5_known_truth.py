"""Gate 5: known-truth experiments for the TAWE estimators (idealised linear moisture world).

Truth model: dW/dt + div(u W) = E - k(x) W on a 0.25 deg channel (54-58N, 0-20E), solved with the same
donor-cell tracker (constant capacity trick). Jurisdictions: source strip S (owner J) at sea, receptor
countries C1 (near), C2 (far) downwind. The intervention raises E in S by dE and, optionally, (a) changes rain
efficiency k by delta_k in a downstream box (precipitation/cloud channel), (b) reduces transport speed by
delta_u in a wake box (dynamic channel). Truth TAWE = P(I) - P(no I) per receptor. Estimators:
  supply   : dE_S * a_{S->c} from baseline tagging (Gate 1 channel Delta_supply)
  account  : A_{S->c} (baseline tagged precipitation, i.e. mistaking accounting for an externality)
Outputs results/known_truth.csv.
"""
import sys, pathlib, itertools, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tawe.tracking import Tracker, cfl_substeps
LAT = np.arange(58.0, 54.0 - 1e-9, -0.25); LON = np.arange(0.0, 20.0 + 1e-9, 0.25); SH = (LAT.size, LON.size)
C = 1e4; U = 8.0; K0 = 1 / (18 * 3600.0); E0 = 3.0 / 86400; HOURS = 24 * 20
S = np.zeros(SH, bool); S[6:11, 8:16] = True             # source (sea, jurisdiction J)
C1 = np.zeros(SH, bool); C1[:, 24:48] = True             # near receptor 6-12E
C2 = np.zeros(SH, bool); C2[:, 48:76] = True             # far receptor 12-19E
BOX = np.zeros(SH, bool); BOX[4:13, 16:30] = True        # perturbed box just downwind of S


def run(E, k, u, src):
    Fu = u * C; Fv = np.zeros(SH); W = np.full(SH, C)
    tr = Tracker(LAT, LON, src)
    n = cfl_substeps(W, Fu, Fv, LAT, LON, 3600.0)
    for _ in range(HOURS * n):
        tr.step(W, Fu, Fv, E, k * C, 3600.0 / n)
    return tr


def recv(P):
    return {"C1": float((P * C1).sum()), "C2": float((P * C2).sum())}


rows = []
base_tr = run(np.full(SH, E0), np.full(SH, K0), np.full(SH, U), np.stack([np.ones(SH, bool), S]))
P_base = recv(base_tr.P_tag_acc[0]); A_S = recv(base_tr.P_tag_acc[1]); Es = float(base_tr.budget["E_src"][1])
for dE_frac, dk, du in itertools.product([0.05, 0.2], [0.0, 0.05, -0.05, 0.2], [0.0, -0.1]):
    E = np.full(SH, E0) + dE_frac * E0 * S; k = np.full(SH, K0) * np.where(BOX, 1 + dk, 1.0)
    u = np.full(SH, U) * np.where(BOX, 1 + du, 1.0)
    tr = run(E, k, u, np.ones(SH, bool)[None])
    P_I = recv(tr.P_tag_acc[0]); dE_tot = dE_frac * Es
    for c in ("C1", "C2"):
        truth = P_I[c] - P_base[c]; sup = dE_tot * A_S[c] / Es
        rows.append(dict(dE_frac=dE_frac, delta_k=dk, delta_u=du, receptor=c, truth_kg=truth, supply_kg=sup,
                         account_kg=A_S[c], supply_rel_err=(sup - truth) / abs(truth) if truth else np.nan,
                         account_rel_err=(A_S[c] - truth) / abs(truth) if truth else np.nan,
                         truth_frac_of_baseline=truth / P_base[c]))
df = pd.DataFrame(rows); pathlib.Path("results").mkdir(exist_ok=True); df.to_csv("results/known_truth.csv", index=False)
pd.set_option("display.width", 200); print(df.round(4).to_string())
