"""Water infrastructure dynamics — distribution networks, pipe decay, drought rationing, floods.

phi = potable water delivery flux / treatment capacity
C   = pipe deterioration / contamination risk / scarcity burden
psi > 1.2 = overflow / flooding system; psi ~ 1.0 = adequate supply; psi < 0.6 = shortage
"""
import numpy as np
from engine.physics import laplacian


def _distribution_network(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Water flows from treatment (high phi) to demand (low phi) through pipes (C)
    state.phi += dt * 0.04 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.0)
    # High-demand zones develop higher C (pressure loss, aging pipes)
    mean_phi = float(np.mean(state.phi))
    high_demand = state.phi < mean_phi * 0.8
    state.C[high_demand] += dt * 0.01


def _pipe_decay_and_leakage(state, dt):
    # Aging: C rises uniformly (corrosion, scale)
    state.C += dt * 0.002
    state.C = np.maximum(state.C, 0.05)
    mean_C = float(np.mean(state.C))
    # Leakage: high-C pipes lose phi (non-revenue water)
    leaking = state.C > mean_C * 1.4
    if np.any(leaking):
        loss = dt * 0.03 * (state.C[leaking] / (mean_C + 1e-9))
        state.phi[leaking] -= loss * state.phi[leaking]
        state.phi[leaking] = np.maximum(state.phi[leaking], 0.001)


def _drought_rationing(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Drought: phi supply drops, C (scarcity) spikes
    drought = state.phi < mean_phi * 0.5
    if np.any(drought):
        state.C[drought] += dt * 0.1
        # Rationing: phi redistributed from surplus to deficit zones
        surplus = state.phi > mean_phi * 1.3
        if np.any(surplus):
            transfer = dt * 0.05 * float(np.mean(state.phi[surplus]))
            state.phi[surplus] -= transfer
            state.phi[drought] += transfer * 0.6  # delivery loss
    state.phi = np.maximum(state.phi, 0.001)


def apply_water_infrastructure(state, dt=0.01):
    try:
        _distribution_network(state, dt)
        _pipe_decay_and_leakage(state, dt)
        _drought_rationing(state, dt)
    except Exception:
        raise
