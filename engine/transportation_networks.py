"""Transportation network dynamics — congestion, route choice, modal shift, infrastructure decay.

phi = passenger/freight throughput flux
C   = congestion / travel time burden / infrastructure maintenance gap
psi > 1.2 = gridlock/saturation; psi ~ 1.0 = free flow; psi < 0.7 = underutilized
"""
import numpy as np
from engine.physics import laplacian


def _traffic_flow(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Traffic flows along least-resistance paths
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flow_x = grad_phi_x / safe_C
    flow_y = grad_phi_y / safe_C
    _, div_x = np.gradient(flow_x)
    div_y, _ = np.gradient(flow_y)
    state.phi += dt * 0.04 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.0)
    # Braess's paradox: adding low-C links can raise mean C (induced demand)
    mean_phi = float(np.mean(state.phi))
    induced = state.phi > mean_phi * 1.5
    state.C[induced] += dt * 0.02 * (state.phi[induced] / (mean_phi + 1e-9))


def _congestion_pricing(state, dt):
    mean_C = float(np.mean(state.C))
    # Dynamic pricing: congested zones raise C further (tolls), diverting flow
    congested = state.C > mean_C * 1.5
    if np.any(congested):
        state.C[congested] += dt * 0.05
        # Flow diverts to alternative routes (laplacian redistribution)
        divert = laplacian(np.where(congested, state.phi, 0.0)) * (-0.1)
        state.phi += dt * divert
    state.phi = np.maximum(state.phi, 0.0)


def _infrastructure_maintenance(state, dt):
    # Road degradation: C rises over time without maintenance
    state.C += dt * 0.003
    mean_phi = float(np.mean(state.phi))
    # High-traffic corridors self-maintain (investment follows traffic)
    high_traffic = state.phi > mean_phi * 1.5
    state.C[high_traffic] -= dt * 0.005
    state.C = np.maximum(state.C, 0.05)


def apply_transportation_networks(state, dt=0.01):
    try:
        _traffic_flow(state, dt)
        _congestion_pricing(state, dt)
        _infrastructure_maintenance(state, dt)
    except Exception:
        raise
