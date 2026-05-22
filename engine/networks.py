"""Network topology dynamics — hub formation, cascade failures, small-world rewiring.

phi = information/traffic flux
C   = network friction (latency, congestion, broken links)
psi ~ 1.0 = efficient routing; > 1.2 = hub overload; < 0.8 = dead zone
"""
import numpy as np
from engine.physics import laplacian


def _hub_formation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_x = grad_phi_x / safe_C
    flux_y = grad_phi_y / safe_C
    _, div_x = np.gradient(flux_x)
    div_y, _ = np.gradient(flux_y)
    divergence = div_x + div_y
    threshold = float(np.mean(divergence)) - float(np.std(divergence))
    hub_mask = divergence < threshold
    if np.any(hub_mask):
        state.phi[hub_mask] += dt * 0.05 * np.abs(divergence[hub_mask])
        state.C[hub_mask] = np.maximum(state.C[hub_mask] - dt * 0.02, 0.05)


def _cascade_failure(state, dt):
    if not hasattr(state, 'network_refractory'):
        state.network_refractory = np.zeros_like(state.phi)
    state.network_refractory = np.maximum(state.network_refractory - dt, 0.0)
    overloaded = (state.psi > 1.4) & (state.network_refractory < 0.01)
    if np.any(overloaded):
        load_shed = laplacian(state.phi)
        state.phi[overloaded] -= dt * 0.3 * state.phi[overloaded]
        state.phi = np.maximum(state.phi + dt * 0.05 * np.where(overloaded, load_shed, 0.0), 0.0)
        state.C[overloaded] += dt * 1.5
        state.network_refractory[overloaded] = 1.0


def _small_world_rewiring(state, dt):
    mean_psi = float(np.mean(state.psi))
    underused = state.psi < mean_psi * 0.6
    if not np.any(underused):
        return
    high_phi_idx = np.unravel_index(int(np.argmax(state.phi)), state.phi.shape)
    candidates = np.argwhere(underused)
    if len(candidates) == 0:
        return
    pick = tuple(candidates[np.random.randint(len(candidates))])
    transfer = dt * 0.03 * float(state.phi[high_phi_idx])
    state.phi[pick] += transfer
    state.C[pick] = np.maximum(state.C[pick] - dt * 0.01, 0.05)


def apply_networks(state, dt=0.01):
    try:
        _hub_formation(state, dt)
        _cascade_failure(state, dt)
        _small_world_rewiring(state, dt)
    except Exception:
        raise
