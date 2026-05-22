"""Power grid dynamics — load balancing, cascade blackouts, renewable integration, resilience.

phi = electrical power flux / load flow
C   = transmission resistance / congestion / frequency deviation
psi > 1.2 = overloaded line (trip risk); psi ~ 1.0 = nominal; psi < 0.7 = undervoltage
"""
import numpy as np
from engine.physics import laplacian


def _load_flow(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Power flows from generation nodes (high phi) to load nodes (low phi) via low-C lines
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flow_x = grad_phi_x / safe_C
    flow_y = grad_phi_y / safe_C
    _, div_x = np.gradient(flow_x)
    div_y, _ = np.gradient(flow_y)
    state.phi += dt * 0.05 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.0)
    # Transmission losses: C accumulates slightly (Joule heating)
    flow_mag = np.sqrt(flow_x**2 + flow_y**2)
    state.C += dt * 0.001 * flow_mag


def _cascade_blackout(state, dt):
    if not hasattr(state, 'grid_refractory'):
        state.grid_refractory = np.zeros_like(state.phi)
    state.grid_refractory = np.maximum(state.grid_refractory - dt, 0.0)
    # Line trip: overloaded cells disconnect (psi > 1.3), shedding load to neighbors
    tripped = (state.psi > 1.3) & (state.grid_refractory < 0.01)
    if np.any(tripped):
        shed = laplacian(np.where(tripped, state.phi, 0.0))
        state.phi += dt * 0.3 * shed
        state.C[tripped] += dt * 2.0  # tripped line = high resistance
        state.phi[tripped] *= max(0.0, 1.0 - dt * 0.5)
        state.grid_refractory[tripped] = 2.0
    state.phi = np.maximum(state.phi, 0.0)


def _renewable_intermittency(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Renewables: low-C generation (low marginal cost) but stochastic phi
    renewable = state.C < mean_C * 0.5
    if np.any(renewable):
        # Intermittency: random phi perturbation
        noise = np.random.normal(0, 0.05, state.phi[renewable].shape)
        state.phi[renewable] *= (1.0 + noise)
        state.phi[renewable] = np.maximum(state.phi[renewable], 0.0)
    # Storage response: smooth out spikes
    spike = state.phi > mean_phi * 2.0
    state.phi[spike] -= dt * 0.1 * (state.phi[spike] - mean_phi * 2.0)


def apply_power_grid(state, dt=0.01):
    try:
        _load_flow(state, dt)
        _cascade_blackout(state, dt)
        _renewable_intermittency(state, dt)
    except Exception:
        raise
