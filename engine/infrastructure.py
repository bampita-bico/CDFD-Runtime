"""Infrastructure buildup, decay, and expansion dynamics.

phi = throughput capacity (traffic, goods, people, data)
C   = maintenance burden / degradation / congestion
psi ~ 1.0 = maintained network; < 0.8 = crumbling; > 1.2 = overcapacity strain
"""
import numpy as np
from engine.physics import laplacian


def _road_network_buildup(state, dt):
    mean_phi = float(np.mean(state.phi))
    stable = (state.psi > 0.8) & (state.psi < 1.2) & (state.phi > mean_phi)
    if np.any(stable):
        surplus = state.phi[stable] - mean_phi
        state.C[stable] = np.maximum(state.C[stable] - dt * 0.025 * surplus, 0.05)


def _infrastructure_decay(state, dt):
    entropy = laplacian(state.C) * 0.01
    state.C += dt * entropy
    state.C = np.maximum(state.C, 0.05)
    deficit = state.phi < state.C * 0.7
    if np.any(deficit):
        state.C[deficit] += dt * 0.04 * (state.C[deficit] - state.phi[deficit])


def _network_expansion(state, dt):
    if not hasattr(state, 'infra_overload_counter'):
        state.infra_overload_counter = np.zeros_like(state.phi)
    overloaded = state.psi > 1.2
    state.infra_overload_counter[overloaded] += dt
    state.infra_overload_counter[~overloaded] = np.maximum(
        state.infra_overload_counter[~overloaded] - dt * 0.5, 0.0
    )
    expanding = state.infra_overload_counter > 2.0
    if not np.any(expanding):
        return
    low_phi_mask = state.phi < float(np.mean(state.phi)) * 0.5
    if not np.any(low_phi_mask):
        return
    candidates = np.argwhere(low_phi_mask)
    exp_cells = np.argwhere(expanding)
    # Transfer capacity from most-overloaded cell to nearest low-phi cell
    exp_idx = exp_cells[np.argmax(state.infra_overload_counter[expanding])]
    distances = np.sum((candidates - exp_idx)**2, axis=1)
    nearest = tuple(candidates[np.argmin(distances)])
    transfer = dt * 0.05 * float(state.phi[tuple(exp_idx)])
    state.phi[nearest] += transfer
    state.C[nearest] = np.maximum(state.C[nearest] - dt * 0.02, 0.05)
    state.infra_overload_counter[tuple(exp_idx)] = 0.0


def apply_infrastructure(state, dt=0.01):
    try:
        _road_network_buildup(state, dt)
        _infrastructure_decay(state, dt)
        _network_expansion(state, dt)
    except Exception:
        raise
