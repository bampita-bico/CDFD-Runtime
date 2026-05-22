"""Technology diffusion dynamics — S-curve adoption, creative destruction, path dependency.

phi = knowledge flow / innovation rate / technology diffusion
C   = adoption barrier / incumbency resistance / cognitive load
psi > 1.0 = frontier expanding; psi < 0.8 = stagnation / lock-in
"""
import numpy as np
from engine.physics import laplacian


def _innovation_diffusion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    max_phi = float(np.max(state.phi)) + 1e-9
    # Logistic adoption rate: peaks at intermediate phi (early majority)
    normalized = state.phi / max_phi
    logistic_rate = 4.0 * normalized * (1.0 - normalized)  # peaks at 0.5
    spread = logistic_rate * laplacian(state.phi) / safe_C
    state.phi += dt * 0.03 * spread
    state.phi = np.maximum(state.phi, 0.0)


def _creative_destruction(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Dominant technologies erode incumbent barriers
    dominant = state.phi > mean_phi * 2.0
    if np.any(dominant):
        state.C[dominant] -= dt * 0.04 * (state.phi[dominant] - mean_phi)
        state.C[dominant] = np.maximum(state.C[dominant], 0.05)
    # Previously dominant cells now mid-range: obsolescence
    obsolete = (state.phi > mean_phi * 1.5) & (~dominant)
    if np.any(obsolete):
        state.phi[obsolete] -= dt * 0.1 * (state.phi[obsolete] - mean_phi * 1.5)
        state.phi[obsolete] = np.maximum(state.phi[obsolete], 0.01)


def _path_dependency(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    locked = (state.C > mean_C * 1.5) & (state.phi > mean_phi * 0.3) & (state.phi < mean_phi)
    if np.any(locked):
        # Standards and network effects deepen lock-in
        state.C[locked] += dt * 0.02
    # Coordination shock: neighbor with phi > 3*mean breaks lock-in
    max_neighbor_phi = (
        np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
        np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
    ) / 4.0
    shock = locked & (max_neighbor_phi > mean_phi * 3.0)
    if np.any(shock):
        state.C[shock] *= 0.5


def apply_technology(state, dt=0.01):
    try:
        _innovation_diffusion(state, dt)
        _creative_destruction(state, dt)
        _path_dependency(state, dt)
    except Exception:
        raise
