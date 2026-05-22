"""Level 16 — Information Flow.

Measures where information concentrates, how Φ and C fields are coupled,
and which direction causality runs — all from field values alone.

  - Entropy gradient: spatial map of where Ψ is most uncertain/active
  - Mutual information: how much Φ and C share structure
  - Transfer entropy: does Φ drive C, or C drive Φ?

No AI. Pure information theory on the fields.
"""
import numpy as np


def _discretize(values, n_bins=10):
    mn, mx = float(values.min()), float(values.max())
    if mx - mn < 1e-12:
        return np.zeros(len(values), dtype=int)
    bins = np.linspace(mn, mx, n_bins + 1)
    return np.digitize(values.flatten(), bins[:-1]) - 1


def _entropy_1d(indices, n_bins=10):
    counts = np.bincount(indices, minlength=n_bins).astype(float)
    probs = counts / max(counts.sum(), 1e-12)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs + 1e-12)))


def entropy_gradient(state, n_bins=10):
    """
    Spatial entropy map: each cell's local entropy computed from a 3x3 neighborhood.
    High values = high local variability = information-rich regions.
    """
    psi = state.psi
    nx, ny = psi.shape
    result = np.zeros((nx, ny))

    for i in range(nx):
        for j in range(ny):
            neighborhood = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni_, nj_ = (i + di) % nx, (j + dj) % ny
                    neighborhood.append(psi[ni_, nj_])
            arr = np.array(neighborhood)
            mn, mx = arr.min(), arr.max()
            if mx - mn < 1e-12:
                result[i, j] = 0.0
            else:
                normed = ((arr - mn) / (mx - mn) * (n_bins - 1)).astype(int)
                result[i, j] = _entropy_1d(normed, n_bins)

    return result


def field_entropy(field, n_bins=20):
    """Shannon entropy of an entire 2D field."""
    indices = _discretize(field, n_bins)
    return _entropy_1d(indices, n_bins)


def mutual_information(state, n_bins=10):
    """
    Mutual information between Φ and C fields.
    High MI → fields are strongly coupled (constraint tracks flow).
    Low MI → fields evolving independently.
    """
    phi_idx = _discretize(state.phi, n_bins)
    c_idx = _discretize(state.C, n_bins)

    joint = np.zeros((n_bins, n_bins))
    for p, c in zip(phi_idx, c_idx):
        joint[p, c] += 1
    joint /= max(joint.sum(), 1e-12)

    p_phi = joint.sum(axis=1)
    p_c = joint.sum(axis=0)

    mi = 0.0
    for i in range(n_bins):
        for j in range(n_bins):
            if joint[i, j] > 1e-12 and p_phi[i] > 1e-12 and p_c[j] > 1e-12:
                mi += joint[i, j] * np.log(joint[i, j] / (p_phi[i] * p_c[j]))

    return float(mi)


def transfer_entropy(source, target, lag=1, n_bins=8):
    """
    Transfer entropy from source → target time series.
    TE(source→target) > TE(target→source) means source drives target.

    Returns: (te_forward, te_backward, direction)
    """
    def _te(x, y, lag, n_bins):
        if len(x) <= lag + 1:
            return 0.0
        y_future = _discretize(np.array(y[lag:]), n_bins)
        y_past = _discretize(np.array(y[:-lag]), n_bins)
        x_past = _discretize(np.array(x[:-lag]), n_bins)

        n = len(y_future)
        joint3 = np.zeros((n_bins, n_bins, n_bins))
        joint2_yx = np.zeros((n_bins, n_bins))

        for t in range(n):
            yf, yp, xp = y_future[t], y_past[t], x_past[t]
            joint3[yf, yp, xp] += 1
            joint2_yx[yf, yp] += 1

        joint3 /= max(joint3.sum(), 1e-12)
        joint2_yx /= max(joint2_yx.sum(), 1e-12)
        joint2_yp_xp = joint3.sum(axis=0)
        p_yp = joint2_yp_xp.sum(axis=1)

        te = 0.0
        for yf in range(n_bins):
            for yp in range(n_bins):
                for xp in range(n_bins):
                    p3 = joint3[yf, yp, xp]
                    p2 = joint2_yx[yf, yp]
                    p2b = joint2_yp_xp[yp, xp]
                    pyp = p_yp[yp]
                    if p3 > 1e-12 and p2 > 1e-12 and p2b > 1e-12 and pyp > 1e-12:
                        te += p3 * np.log(p3 * pyp / (p2 * p2b))
        return float(te)

    te_fwd = _te(source, target, lag, n_bins)
    te_bwd = _te(target, source, lag, n_bins)
    direction = "source→target" if te_fwd > te_bwd else "target→source"
    if abs(te_fwd - te_bwd) < 0.01:
        direction = "bidirectional"

    return {"te_forward": round(te_fwd, 6),
            "te_backward": round(te_bwd, 6),
            "direction": direction}


def information_report(state, phi_history=None, c_history=None):
    eg = entropy_gradient(state)
    report = {
        "phi_entropy": round(field_entropy(state.phi), 4),
        "C_entropy": round(field_entropy(state.C), 4),
        "psi_entropy": round(field_entropy(state.psi), 4),
        "mutual_information_phi_C": round(mutual_information(state), 4),
        "entropy_gradient_mean": round(float(eg.mean()), 4),
        "entropy_gradient_max": round(float(eg.max()), 4),
        "high_info_fraction": round(float((eg > eg.mean()).mean()), 4),
    }
    if phi_history and c_history and len(phi_history) > 4:
        te = transfer_entropy(phi_history, c_history)
        report["transfer_entropy"] = te
    return report
