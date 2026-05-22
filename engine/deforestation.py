"""Deforestation dynamics — clearing fronts, fragmentation, carbon release, reforestation.

phi = forest cover flux / tree biomass / canopy connectivity
C   = clearing pressure / road access / economic incentive to deforest
psi < 0.6 = rapid clearing; psi ~ 1.0 = stable frontier; > 1.2 = reforestation pressure
"""
import numpy as np
from engine.physics import laplacian


def _deforestation_front(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Clearing front: high C (road access, demand) advances into high-phi forest
    frontier = (state.C > mean_C) & (state.phi > mean_phi * 0.8)
    if np.any(frontier):
        cleared = dt * 0.08 * state.C[frontier] / (float(np.max(state.C)) + 1e-9)
        state.phi[frontier] -= cleared * state.phi[frontier]
        state.phi[frontier] = np.maximum(state.phi[frontier], 0.001)
    # Frontier advances: C diffuses along cleared edge
    state.C += dt * 0.01 * laplacian(np.where(frontier, state.C, 0.0))


def _fragmentation(state, dt):
    # Forest fragments: isolated low-phi patches surrounded by cleared land are more vulnerable
    neighbor_phi = (
        np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
        np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
    ) / 4.0
    mean_phi = float(np.mean(state.phi))
    isolated = (state.phi > mean_phi * 0.5) & (neighbor_phi < mean_phi * 0.4)
    if np.any(isolated):
        state.phi[isolated] -= dt * 0.04 * state.phi[isolated]
        state.phi[isolated] = np.maximum(state.phi[isolated], 0.001)
        state.C[isolated] += dt * 0.02  # edge effects raise clearing pressure


def _reforestation(state, dt):
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # Reforestation: where C drops (policy change, land abandonment), forest recovers
    recovering = (state.C < mean_C * 0.5) & (state.phi < mean_phi * 0.6)
    if np.any(recovering):
        state.phi[recovering] += dt * 0.05 * (mean_phi - state.phi[recovering])
        # Neighbor seed source helps
        seed_source = laplacian(np.where(state.phi > mean_phi, state.phi, 0.0)) * 0.01
        state.phi[recovering] += dt * np.maximum(seed_source[recovering], 0.0)
    state.phi = np.maximum(state.phi, 0.001)


def apply_deforestation(state, dt=0.01):
    try:
        _deforestation_front(state, dt)
        _fragmentation(state, dt)
        _reforestation(state, dt)
    except Exception:
        raise
