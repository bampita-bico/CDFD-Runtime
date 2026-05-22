"""Colonialism and decolonization dynamics — extraction, institutional destruction, independence.

phi = productive output / local economic activity
C   = colonial extraction burden / imposed institutional friction / dependency constraint
psi > 1.0 = colonial extraction profitable; psi < 0.5 = extractive collapse / independence
"""
import numpy as np
from engine.physics import laplacian


def _extraction_and_dependency(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Colonial core: low C (for colonizer), extracts phi from periphery
    core = (state.phi > mean_phi * 1.5) & (state.C < mean_C * 0.5)
    periphery = (state.phi < mean_phi) & (state.C > mean_C * 1.3)
    if np.any(core) and np.any(periphery):
        # Extraction: phi flows from periphery to core
        extraction_rate = dt * 0.05 * float(np.mean(state.phi[periphery]))
        state.phi[periphery] = np.maximum(state.phi[periphery] - extraction_rate, 0.001)
        state.phi[core] += extraction_rate * 0.7  # leakage in transit
    # Dependency trap: periphery C rises (destroyed local institutions)
    if np.any(periphery):
        state.C[periphery] += dt * 0.03


def _institutional_destruction(state, dt):
    mean_C = float(np.mean(state.C))
    # Colonized zones: pre-existing low-C structures replaced by high-C extraction apparatus
    colonized = state.C > mean_C * 1.5
    if np.any(colonized):
        # Local phi (human capital, enterprise) drained
        state.phi[colonized] -= dt * 0.02 * state.phi[colonized]
        state.phi[colonized] = np.maximum(state.phi[colonized], 0.001)
    # Settler colonies: some zones get C lowered selectively (infrastructure for extraction)
    settler = (state.phi > float(np.mean(state.phi)) * 0.8) & (state.C > mean_C * 1.2)
    state.C[settler] -= dt * 0.01  # road/port infrastructure serves extraction


def _independence_and_decolonization(state, dt):
    if not hasattr(state, 'decolonize_momentum'):
        state.decolonize_momentum = np.zeros_like(state.phi)
    mean_C = float(np.mean(state.C))
    # Resistance builds: high C, falling phi
    resistance = (state.C > mean_C * 1.5) & (state.phi < float(np.mean(state.phi)) * 0.7)
    self.decolonize_momentum = getattr(state, 'decolonize_momentum')
    state.decolonize_momentum[resistance] += dt
    state.decolonize_momentum[~resistance] = np.maximum(
        state.decolonize_momentum[~resistance] - dt * 0.2, 0.0
    )
    # Independence: when momentum > threshold, C collapses (external constraint removed)
    independent = state.decolonize_momentum > 5.0
    if np.any(independent):
        state.C[independent] -= dt * 0.3 * state.C[independent]
        state.C[independent] = np.maximum(state.C[independent], 0.1)
        state.phi[independent] += dt * 0.04 * state.phi[independent]
        state.decolonize_momentum[independent] = 0.0


def apply_colonialism(state, dt=0.01):
    try:
        _extraction_and_dependency(state, dt)
        _institutional_destruction(state, dt)
        # independence check
        if not hasattr(state, 'decolonize_momentum'):
            state.decolonize_momentum = np.zeros_like(state.phi)
        mean_C = float(np.mean(state.C))
        resistance = (state.C > mean_C * 1.5) & (state.phi < float(np.mean(state.phi)) * 0.7)
        state.decolonize_momentum[resistance] += dt
        state.decolonize_momentum[~resistance] = np.maximum(
            state.decolonize_momentum[~resistance] - dt * 0.2, 0.0
        )
        independent = state.decolonize_momentum > 5.0
        if np.any(independent):
            state.C[independent] -= dt * 0.3 * state.C[independent]
            state.C[independent] = np.maximum(state.C[independent], 0.1)
            state.phi[independent] += dt * 0.04 * state.phi[independent]
            state.decolonize_momentum[independent] = 0.0
    except Exception:
        raise
