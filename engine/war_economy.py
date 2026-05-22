"""War-economy coupling — wartime production, blockade effects, reconstruction boom.

Cross-domain module: conflict phi feeds back into economics and infrastructure C/phi.
"""
import numpy as np
from engine.physics import laplacian


def _wartime_production(state, dt):
    mean_phi = float(np.mean(state.phi))
    # High-conflict zones redirect economic output to military
    conflict_zone = state.phi > mean_phi * 1.8
    if not np.any(conflict_zone):
        return
    # Guns vs butter: economic phi diverted, military phi gains
    economic_drain = dt * 0.08 * state.phi[conflict_zone] * (state.phi[conflict_zone] / (mean_phi + 1e-9))
    state.phi[conflict_zone] -= economic_drain
    state.phi[conflict_zone] = np.maximum(state.phi[conflict_zone], 0.01)
    # Military production raises C in surrounding economy (resource diversion)
    state.C += dt * 0.01 * np.where(conflict_zone, state.phi, 0.0) / (mean_phi + 1e-9)


def _blockade_effects(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Blockaded cells: surrounded by high-phi (conflict) neighbors, they lose phi
    neighbor_phi = (
        np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
        np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
    ) / 4.0
    blockaded = (neighbor_phi > mean_phi * 2.0) & (state.phi < mean_phi * 0.8)
    if np.any(blockaded):
        state.phi[blockaded] -= dt * 0.06 * state.phi[blockaded]
        state.phi[blockaded] = np.maximum(state.phi[blockaded], 0.001)
        state.C[blockaded] += dt * 0.15  # supply shortage friction


def _war_reconstruction(state, dt):
    if not hasattr(state, 'conflict_resolved'):
        state.conflict_resolved = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Detect recently resolved conflict: C was high from warfare, phi now recovering
    recently_resolved = (state.C > mean_C * 1.3) & (state.phi > mean_phi * 0.5) & (state.psi > 0.7)
    state.conflict_resolved[recently_resolved] += dt
    state.conflict_resolved[~recently_resolved] = np.maximum(
        state.conflict_resolved[~recently_resolved] - dt * 0.5, 0.0
    )
    rebuilding = state.conflict_resolved > 1.0
    if np.any(rebuilding):
        # Marshall Plan effect: rapid C reduction, double phi growth
        state.C[rebuilding] -= dt * 0.15 * (state.C[rebuilding] - mean_C)
        state.C[rebuilding] = np.maximum(state.C[rebuilding], 0.05)
        state.phi[rebuilding] += dt * 0.06 * state.phi[rebuilding]


def apply_war_economy(state, dt=0.01):
    try:
        _wartime_production(state, dt)
        _blockade_effects(state, dt)
        _war_reconstruction(state, dt)
    except Exception:
        raise
