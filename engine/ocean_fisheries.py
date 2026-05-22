"""Ocean fisheries dynamics — maximum sustainable yield, stock collapse, aquaculture.

phi = fish biomass flux / spawning stock productivity
C   = fishing mortality / habitat degradation / recruitment failure
psi ~ 1.0 = MSY; > 1.2 = overfishing; < 0.5 = stock collapse
"""
import numpy as np
from engine.physics import laplacian


def _stock_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    max_phi = float(np.max(state.phi)) + 1e-9
    # Beverton-Holt recruitment: logistic growth bounded by C
    growth = state.phi * (1.0 - state.phi / max_phi) / safe_C
    state.phi += dt * 0.05 * growth
    # Fish migrate toward productive zones
    state.phi += dt * 0.01 * laplacian(state.phi)
    state.phi = np.maximum(state.phi, 0.001)


def _overfishing_and_collapse(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Overfishing: extraction rate exceeds regeneration
    overfished = state.psi > 1.2
    if np.any(overfished):
        state.phi[overfished] -= dt * 0.1 * state.phi[overfished]
        state.phi[overfished] = np.maximum(state.phi[overfished], 0.001)
        state.C[overfished] += dt * 0.03  # habitat degradation from trawling
    # Collapse below critical spawning stock biomass
    critical = state.phi < mean_phi * 0.1
    if np.any(critical):
        state.phi[critical] -= dt * 0.05 * state.phi[critical]
        state.phi[critical] = np.maximum(state.phi[critical], 0.0001)


def _recovery_and_marine_reserves(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Marine protected areas: high C zones (no-take) rebuild phi
    protected = state.C > mean_C * 1.5
    if np.any(protected):
        state.phi[protected] += dt * 0.04 * state.phi[protected]
        # Spillover: phi diffuses from protected to adjacent zones
        spillover = laplacian(np.where(protected, state.phi, 0.0)) * 0.02
        state.phi += dt * np.maximum(spillover, 0.0)
    state.phi = np.maximum(state.phi, 0.001)


def apply_ocean_fisheries(state, dt=0.01):
    try:
        _stock_dynamics(state, dt)
        _overfishing_and_collapse(state, dt)
        _recovery_and_marine_reserves(state, dt)
    except Exception:
        raise
