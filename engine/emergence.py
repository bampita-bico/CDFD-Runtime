"""Level 13 — Emergence Classifier.

Reads the Ψ field and detects structural patterns:
  fronts, clusters, voids, gradients, spirals, fragmentation.

The system sees its own shapes. No AI — pure field analysis.
"""
import numpy as np


def classify_field(state):
    """Top-level: return a list of detected emergent structures."""
    psi = state.psi
    structures = []

    if _has_front(psi):
        structures.append("front")
    if _has_cluster(psi):
        structures.append("cluster")
    if _has_void(psi):
        structures.append("void")
    if _has_gradient(psi):
        structures.append("gradient")
    if _is_fragmented(psi):
        structures.append("fragmentation")
    if _is_uniform(psi):
        structures.append("uniform")

    return structures if structures else ["unclassified"]


def _has_front(psi, threshold=0.3):
    grad_x = np.abs(np.roll(psi, -1, axis=1) - np.roll(psi, 1, axis=1)) / 2.0
    grad_y = np.abs(np.roll(psi, -1, axis=0) - np.roll(psi, 1, axis=0)) / 2.0
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    return float(grad_mag.max()) > threshold


def _has_cluster(psi, high_threshold=1.2, min_fraction=0.1):
    high_region = psi > high_threshold
    return float(high_region.mean()) >= min_fraction


def _has_void(psi, low_threshold=0.3, min_fraction=0.1):
    low_region = psi < low_threshold
    return float(low_region.mean()) >= min_fraction


def _has_gradient(psi, min_range=0.5):
    return float(psi.max() - psi.min()) > min_range


def _is_fragmented(psi, threshold=0.6):
    binary = (psi > threshold).astype(int)
    components = _count_components(binary)
    return components >= 3


def _is_uniform(psi, max_std=0.05):
    return float(psi.std()) < max_std


def _count_components(binary):
    visited = np.zeros_like(binary, dtype=bool)
    count = 0
    nx, ny = binary.shape

    def flood(i, j):
        stack = [(i, j)]
        while stack:
            ci, cj = stack.pop()
            if ci < 0 or ci >= nx or cj < 0 or cj >= ny:
                continue
            if visited[ci, cj] or binary[ci, cj] == 0:
                continue
            visited[ci, cj] = True
            stack.extend([(ci+1,cj),(ci-1,cj),(ci,cj+1),(ci,cj-1)])

    for i in range(nx):
        for j in range(ny):
            if binary[i, j] and not visited[i, j]:
                flood(i, j)
                count += 1
    return count


def field_entropy(state):
    psi = state.psi.flatten()
    psi_pos = np.clip(psi, 1e-9, None)
    psi_norm = psi_pos / psi_pos.sum()
    return float(-np.sum(psi_norm * np.log(psi_norm)))


def spatial_autocorrelation(state):
    """Moran's I approximation — measures how clustered the Ψ field is."""
    psi = state.psi
    mean = psi.mean()
    deviations = psi - mean
    shifted_x = np.roll(psi, 1, axis=1) - mean
    shifted_y = np.roll(psi, 1, axis=0) - mean
    spatial_cov = float((deviations * (shifted_x + shifted_y)).mean())
    variance = float((deviations ** 2).mean())
    if variance < 1e-12:
        return 0.0
    return spatial_cov / variance


def emergence_report(state):
    return {
        "structures": classify_field(state),
        "entropy": round(field_entropy(state), 4),
        "autocorrelation": round(spatial_autocorrelation(state), 4),
        "psi_range": round(float(state.psi.max() - state.psi.min()), 4),
        "regime": state.regime(),
    }
