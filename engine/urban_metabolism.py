"""Urban metabolism dynamics — city growth, Zipf's law emergence, congestion, heat islands.

phi = urban energy/material/population throughput
C   = congestion / infrastructure overhead / cost of living burden
psi > 1.2 = agglomeration boom; psi ~ 1.0 = sustainable city; psi < 0.7 = urban decay
"""
import numpy as np
from engine.physics import laplacian


def _agglomeration_and_zipf(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Agglomeration: cities attract phi superlinearly (scaling law)
    city = state.phi > mean_phi
    scale_factor = (state.phi[city] / (mean_phi + 1e-9)) ** 0.15
    state.phi[city] += dt * 0.05 * state.phi[city] * scale_factor
    # Smaller centers lose phi to larger (Zipf rank redistribution)
    small = state.phi < mean_phi * 0.7
    state.phi[small] -= dt * 0.01 * state.phi[small]
    state.phi[small] = np.maximum(state.phi[small], 0.001)
    # Diffusion of urban amenities
    state.phi += dt * 0.005 * laplacian(state.phi) / safe_C


def _congestion_and_sprawl(state, dt):
    mean_C = float(np.mean(state.C))
    # Congestion accumulates as C when phi grows too fast
    dense = state.psi > 1.3
    if np.any(dense):
        state.C[dense] += dt * 0.06 * state.phi[dense] / (float(np.mean(state.phi)) + 1e-9)
    # Sprawl: high-C cities push phi outward (suburbanization)
    sprawling = state.C > mean_C * 1.5
    if np.any(sprawling):
        outflow = laplacian(np.where(sprawling, state.phi, 0.0)) * 0.02
        state.phi += dt * np.where(~sprawling, np.maximum(outflow, 0.0), 0.0)
        state.phi[sprawling] -= dt * 0.02 * state.phi[sprawling]
    state.phi = np.maximum(state.phi, 0.001)


def _urban_heat_and_decay(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Heat island: high-phi dense cities raise local C (energy overhead)
    hot = state.phi > mean_phi * 1.8
    state.C[hot] += dt * 0.01
    # Urban decay: low-phi, high-C zones spiral downward
    decaying = (state.phi < mean_phi * 0.4) & (state.C > mean_C)
    if np.any(decaying):
        state.phi[decaying] -= dt * 0.03 * state.phi[decaying]
        state.phi[decaying] = np.maximum(state.phi[decaying], 0.001)
        state.C[decaying] += dt * 0.02


def apply_urban_metabolism(state, dt=0.01):
    try:
        _agglomeration_and_zipf(state, dt)
        _congestion_and_sprawl(state, dt)
        _urban_heat_and_decay(state, dt)
    except Exception:
        raise
