"""Single-layer Eulerian forward moisture tagging on a regular lat-lon grid.

Column budget:    dW/dt + div(F) = E - P (+ residual)
Tagged moisture:  dWs/dt + div(F * Ws/W) = E * src - P * Ws/W
Face fluxes are the mean of the two adjacent cell-centre fluxes; the tagged
fraction is taken from the upwind cell (donor-cell scheme). The domain edge is
open: tagged outflow leaves and is recorded, inflow carries zero tag.
All mass terms are tracked so that the tagged budget closes exactly:
  sum(E*src) = sum(P_tagged) + outflow + storage change + clip losses.
"""
import numpy as np

R_EARTH = 6.371e6


def grid_geometry(lat, lon):
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    dlat = np.deg2rad(abs(lat[1] - lat[0])); dlon = np.deg2rad(abs(lon[1] - lon[0]))
    phi = np.deg2rad(lat)
    area = (R_EARTH ** 2 * dlat * dlon * np.cos(phi))[:, None] * np.ones((1, lon.size))
    dy = R_EARTH * dlat
    phi_face = np.deg2rad(0.5 * (lat[1:] + lat[:-1]))
    dx_face_ns = R_EARTH * dlon * np.cos(phi_face)  # length of N-S faces (between rows)
    return area, dy, dx_face_ns


class Tracker:
    """lat must be ordered north->south or south->north consistently with the fields."""

    def __init__(self, lat, lon, source_mask):
        self.area, self.dy, self.dx_ns = grid_geometry(lat, lon)
        self.north_first = lat[0] > lat[-1]
        self.src = source_mask.astype(float)
        self.Ws = np.zeros(self.src.shape)
        self.budget = dict(E_src=0.0, P_tag=0.0, outflow=0.0, clip=0.0)
        self.P_tag_acc = np.zeros(self.src.shape)

    def face_transport(self, Fu, Fv):
        """Mass transport (kg s-1) across interior faces. East faces: (ny, nx-1); N-S faces: (ny-1, nx)."""
        Tu = 0.5 * (Fu[:, 1:] + Fu[:, :-1]) * self.dy
        Fv_n = 0.5 * (Fv[1:, :] + Fv[:-1, :])
        # positive northward flux moves mass from row i+1 to row i when rows run north->south
        Tv = (Fv_n if self.north_first else -Fv_n) * self.dx_ns[:, None]
        return Tu, Tv  # Tv > 0 : transport from row i+1 into row i

    def step(self, W, Fu, Fv, E, P, dt):
        """Advance by dt seconds. W kg m-2, F kg m-1 s-1, E,P kg m-2 s-1 (E>0 upward).

        Tagged arrays may carry leading tag dimensions (k, ny, nx); fields are (ny, nx).
        """
        A = self.area
        q = np.clip(np.where(W > 1e-6, self.Ws / np.maximum(W, 1e-6), 0.0), 0.0, 1.0)
        Tu, Tv = self.face_transport(Fu, Fv)
        fu = np.where(Tu > 0, Tu * q[..., :, :-1], Tu * q[..., :, 1:])
        fv = np.where(Tv > 0, Tv * q[..., 1:, :], Tv * q[..., :-1, :])
        div = np.zeros(q.shape)
        div[..., :, :-1] += fu; div[..., :, 1:] -= fu
        div[..., 1:, :] += fv; div[..., :-1, :] -= fv
        out = np.zeros(q.shape)
        out[..., :, 0] += np.maximum(-Fu[:, 0], 0) * self.dy * q[..., :, 0]
        out[..., :, -1] += np.maximum(Fu[:, -1], 0) * self.dy * q[..., :, -1]
        top = np.maximum(Fv[0] if self.north_first else -Fv[0], 0) * self.dx_ns[0]
        bot = np.maximum(-Fv[-1] if self.north_first else Fv[-1], 0) * self.dx_ns[-1]
        out[..., 0, :] += top * q[..., 0, :]
        out[..., -1, :] += bot * q[..., -1, :]
        Esrc = np.maximum(E, 0.0) * self.src * A
        Ptag = np.maximum(P, 0.0) * q * A
        M = self.Ws * A + (Esrc - Ptag - div - out) * dt
        added = -np.minimum(M, 0.0)
        M = np.maximum(M, 0.0)
        over = np.maximum(M - np.maximum(W, 0.0) * A, 0.0)
        M = M - over
        self.Ws = M / A
        ax = (-2, -1); b = self.budget
        b["E_src"] = b["E_src"] + Esrc.sum(ax) * dt
        b["P_tag"] = b["P_tag"] + Ptag.sum(ax) * dt
        b["outflow"] = b["outflow"] + out.sum(ax) * dt
        b["clip"] = b["clip"] + (over - added).sum(ax)
        self.P_tag_acc = self.P_tag_acc + Ptag * dt
        return Ptag * dt

    def storage(self):
        return (self.Ws * self.area).sum((-2, -1))

    def closure_residual(self):
        b = self.budget
        return b["E_src"] - b["P_tag"] - b["outflow"] - self.storage() - b["clip"]


def cfl_substeps(W, Fu, Fv, lat, lon, dt_total, cfl=0.5):
    area, dy, dxn = grid_geometry(lat, lon)
    dx_min = float(dxn.min()) if dxn.size else dy
    u = np.abs(Fu) / np.maximum(W, 1.0); v = np.abs(Fv) / np.maximum(W, 1.0)
    c = max(float(u.max()) / dx_min, float(v.max()) / dy)
    return max(1, int(np.ceil(c * dt_total / cfl)))
