"""Forest ecosystem dynamics — succession, canopy competition, fire regimes, carbon storage.

phi = biomass flux / photosynthetic productivity / carbon flow
C   = canopy closure / competition burden / fire fuel load
psi ~ 1.0 = climax forest; < 0.6 = pioneer/open; > 1.5 = fire-prone dense stand
"""
import numpy as np
from engine.physics import laplacian


def _succession(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Pioneer phase: low phi grows fast
    pioneer = state.phi < mean_phi * 0.5
    state.phi[pioneer] += dt * 0.08 * state.phi[pioneer]
    # Climax phase: high phi grows slow, builds canopy (C rises)
    climax = state.phi > mean_phi * 1.2
    state.phi[climax] += dt * 0.01 * state.phi[climax]
    state.C[climax] += dt * 0.02
    # Spatial seed dispersal
    state.phi += dt * 0.005 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _canopy_competition(state, dt):
    mean_C = float(np.mean(state.C))
    # Dense canopy suppresses understory phi
    dense = state.C > mean_C * 1.5
    if np.any(dense):
        state.phi[dense] -= dt * 0.02 * state.phi[dense]
        state.phi[dense] = np.maximum(state.phi[dense], 0.01)
    # Gap dynamics: when a canopy tree falls, phi in gap surges
    gap = (state.C > mean_C * 1.3) & (state.phi < float(np.mean(state.phi)) * 0.6)
    if np.any(gap):
        state.C[gap] = np.maximum(state.C[gap] - dt * 0.1, 0.05)
        state.phi[gap] += dt * 0.05 * state.phi[gap]


def _fire_regime(state, dt):
    # Fire: when fuel load (C) is very high and phi is stressed (psi > 1.4)
    fire = (state.C > float(np.mean(state.C)) * 2.0) & (state.psi > 1.4)
    if not np.any(fire):
        return
    # Fire burns phi and resets C (charcoal layer lowers C, nutrients released)
    state.phi[fire] *= max(0.0, 1.0 - dt * 1.0)
    state.C[fire] = np.maximum(state.C[fire] - dt * 1.5, 0.1)
    # Fire spreads to neighbors with high C
    fire_spread = laplacian(np.where(fire, 1.0, 0.0).astype(float))
    spread_zone = (fire_spread > 0.1) & (~fire) & (state.C > float(np.mean(state.C)) * 1.5)
    if np.any(spread_zone):
        state.phi[spread_zone] *= max(0.0, 1.0 - dt * 0.5)
        state.C[spread_zone] = np.maximum(state.C[spread_zone] - dt * 0.5, 0.1)
    state.phi = np.maximum(state.phi, 0.001)


def apply_forest_dynamics(state, dt=0.01):
    try:
        _succession(state, dt)
        _canopy_competition(state, dt)
        _fire_regime(state, dt)
    except Exception:
        raise
