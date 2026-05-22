"""Supply chain dynamics — just-in-time logistics, single-point failure, reshoring.

phi = goods/component throughput flux
C   = logistics friction / inventory buffer / geopolitical barrier
psi ~ 1.0 = lean efficient flow; > 1.3 = backlog/bottleneck; < 0.6 = supply shock
"""
import numpy as np
from engine.physics import laplacian


def _just_in_time_flow(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # JIT: phi flows efficiently through low-C corridors
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_x = grad_phi_x / safe_C
    flux_y = grad_phi_y / safe_C
    _, div_x = np.gradient(flux_x)
    div_y, _ = np.gradient(flux_y)
    state.phi += dt * 0.04 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.0)
    # Efficiency: sustained flow erodes C (supplier relationship investment)
    efficient = (state.psi > 0.9) & (state.psi < 1.1)
    state.C[efficient] = np.maximum(state.C[efficient] - dt * 0.005, 0.05)


def _supply_shock_cascade(state, dt):
    if not hasattr(state, 'supply_refractory'):
        state.supply_refractory = np.zeros_like(state.phi)
    state.supply_refractory = np.maximum(state.supply_refractory - dt, 0.0)
    # Shock: single node failure (psi > 1.4) cascades upstream
    bottleneck = (state.psi > 1.4) & (state.supply_refractory < 0.01)
    if np.any(bottleneck):
        # Upstream phi backs up
        state.phi += dt * 0.2 * laplacian(np.where(bottleneck, state.phi, 0.0))
        state.C[bottleneck] += dt * 1.0  # port/factory shutdown
        state.supply_refractory[bottleneck] = 2.0
    state.phi = np.maximum(state.phi, 0.0)


def _reshoring_and_diversification(state, dt):
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # After sustained disruption (high C), firms reshore: C redistributed spatially
    disrupted = state.C > mean_C * 1.8
    if np.any(disrupted):
        # New suppliers emerge in previously idle cells (phi diffuses to alternatives)
        idle = (state.phi < mean_phi * 0.5) & (~disrupted)
        if np.any(idle):
            state.phi[idle] += dt * 0.03 * mean_phi
            state.C[idle] = np.maximum(state.C[idle] - dt * 0.02, 0.1)
        state.C[disrupted] -= dt * 0.05  # pressure to diversify reduces single-source C


def apply_supply_chains(state, dt=0.01):
    try:
        _just_in_time_flow(state, dt)
        _supply_shock_cascade(state, dt)
        _reshoring_and_diversification(state, dt)
    except Exception:
        raise
