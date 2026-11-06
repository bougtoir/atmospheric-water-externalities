import numpy as np
from tawe.tracking import Tracker, cfl_substeps

LAT = np.arange(56.0, 54.0 - 1e-9, -0.25)
LON = np.arange(0.0, 10.0 + 1e-9, 0.25)
SH = (LAT.size, LON.size)


def run(W, Fu, Fv, E, P, src, hours=48, dt_h=3600.0, init=None):
    tr = Tracker(LAT, LON, src)
    if init is not None:
        tr.Ws = init.copy()
    n = cfl_substeps(W, Fu, Fv, LAT, LON, dt_h)
    for _ in range(hours):
        for _ in range(n):
            tr.step(W, Fu, Fv, E, P, dt_h / n)
    return tr


def test_closure_uniform_flow_with_rain():
    W = np.full(SH, 25.0); Fu = np.full(SH, 250.0); Fv = np.full(SH, 30.0)
    E = np.full(SH, 1e-4); P = np.full(SH, 5e-5)
    src = np.zeros(SH, bool); src[3:6, 2:5] = True
    tr = run(W, Fu, Fv, E, P, src)
    rel = abs(tr.closure_residual()) / tr.budget["E_src"]
    assert rel < 1e-10
    assert tr.budget["P_tag"] > 0 and tr.budget["outflow"] > 0


def test_tag_never_exceeds_column():
    W = np.full(SH, 5.0); Fu = np.full(SH, 50.0); Fv = np.zeros(SH)
    E = np.full(SH, 5e-3); P = np.zeros(SH)
    src = np.ones(SH, bool)
    tr = run(W, Fu, Fv, E, P, src, hours=24)
    assert (tr.Ws <= W + 1e-9).all()
    assert abs(tr.closure_residual()) / tr.budget["E_src"] < 1e-10


def test_known_truth_exponential_rainout():
    """Steady eastward flow, rain rate P = k W: tagged column decays as exp(-k x / u)."""
    W = np.full(SH, 20.0); u = 10.0; Fu = np.full(SH, u * 20.0); Fv = np.zeros(SH)
    k = 1.0 / (6 * 3600.0); P = k * W; E = np.zeros(SH); E[:, 0] = 2e-4
    src = np.zeros(SH, bool); src[:, 0] = True
    tr = run(W, Fu, Fv, E, P, src, hours=96)
    row = tr.Ws[4]
    from tawe.tracking import grid_geometry
    _, _, dxn = grid_geometry(LAT, LON)
    dx = dxn[4]
    x = np.arange(LON.size) * dx
    sl = slice(2, 20)
    slope = np.polyfit(x[sl], np.log(row[sl]), 1)[0]
    assert abs(slope / (-k / u) - 1) < 0.15  # donor-cell numerical diffusion tolerance


def test_zero_source_zero_tag():
    W = np.full(SH, 25.0); Fu = np.full(SH, 250.0); Fv = np.full(SH, -40.0)
    E = np.full(SH, 1e-4); P = np.full(SH, 5e-5)
    tr = run(W, Fu, Fv, E, P, np.zeros(SH, bool), hours=12)
    assert tr.budget["E_src"] == 0 and tr.storage() == 0


def test_multi_tag_equals_single_tags():
    W = np.full(SH, 25.0); Fu = np.full(SH, 250.0); Fv = np.full(SH, 30.0)
    E = np.full(SH, 1e-4); P = np.full(SH, 5e-5)
    a = np.zeros(SH, bool); a[3:6, 2:5] = True
    b = np.zeros(SH, bool); b[1:3, 10:20] = True
    multi = run(W, Fu, Fv, E, P, np.stack([a, b]), hours=24)
    sa = run(W, Fu, Fv, E, P, a, hours=24); sb = run(W, Fu, Fv, E, P, b, hours=24)
    assert np.allclose(multi.P_tag_acc[0], sa.P_tag_acc) and np.allclose(multi.P_tag_acc[1], sb.P_tag_acc)
    assert np.all(np.abs(multi.closure_residual()) / multi.budget["E_src"] < 1e-10)
