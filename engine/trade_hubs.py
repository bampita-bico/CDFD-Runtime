"""Trade hub dynamics — Silk Road competition, entrepôt formation, hegemonic cycles.

phi = traded goods / merchant capital in motion
C   = route friction (distance, tolls, blockades, rival interference)
psi > 1.0 = flourishing entrepôt; < 0.8 = bypassed hub; > 1.4 = monopoly peak
"""
import numpy as np


def _silk_road_competition(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_x = grad_phi_x / safe_C
    flux_y = grad_phi_y / safe_C
    flux_mag = np.sqrt(flux_x**2 + flux_y**2)
    mean_flux = float(np.mean(flux_mag))
    mean_C = float(np.mean(state.C))
    hub_mask = (flux_mag > mean_flux * 1.5) & (state.C < mean_C)
    if np.any(hub_mask):
        state.phi[hub_mask] += dt * 0.06 * flux_mag[hub_mask]
        state.C[hub_mask] = np.maximum(
            state.C[hub_mask] - dt * 0.025 * flux_mag[hub_mask], 0.05
        )
    mean_phi = float(np.mean(state.phi))
    bypassed = (state.phi > mean_phi) & (flux_mag < mean_flux * 0.5)
    if np.any(bypassed):
        state.phi[bypassed] -= dt * 0.04 * state.phi[bypassed]
        state.C[bypassed] += dt * 0.03


def _entrepot_dynamics(state, dt):
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    mean_gx = float(np.mean(np.abs(grad_phi_x)))
    mean_gy = float(np.mean(np.abs(grad_phi_y)))
    crossflow = (np.abs(grad_phi_x) > mean_gx * 1.3) & (np.abs(grad_phi_y) > mean_gy * 1.3)
    if np.any(crossflow):
        flux_boost = np.sqrt(grad_phi_x[crossflow]**2 + grad_phi_y[crossflow]**2)
        state.phi[crossflow] += dt * 0.07 * flux_boost
        state.C[crossflow] = np.maximum(state.C[crossflow] - dt * 0.015, 0.05)
    if not hasattr(state, 'prev_entrepot_phi'):
        state.prev_entrepot_phi = state.phi.copy()
    phi_loss = state.prev_entrepot_phi - state.phi
    mean_loss = float(np.mean(np.abs(phi_loss)))
    sudden_loss = crossflow & (phi_loss > mean_loss * 2.0)
    if np.any(sudden_loss):
        state.phi[sudden_loss] *= max(0.0, 1.0 - dt * 0.4)
        state.C[sudden_loss] += dt * 1.0
    state.prev_entrepot_phi = state.phi.copy()


def _hegemonic_cycles(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    hegemonic_mask = (state.phi > mean_phi * 3.0) & (state.C < mean_C * 0.5)
    if np.any(hegemonic_mask):
        periphery = state.phi < mean_phi * 0.7
        if np.any(periphery):
            extraction = dt * 0.02 * float(np.mean(state.phi[periphery]))
            state.phi[periphery] = np.maximum(state.phi[periphery] - extraction * 0.5, 0.01)
            state.phi[hegemonic_mask] += extraction
        state.C[hegemonic_mask] += dt * 0.06 * state.phi[hegemonic_mask]
    overextended = hegemonic_mask & (state.C > state.phi * 1.3)
    if np.any(overextended):
        state.phi[overextended] *= max(0.0, 1.0 - dt * 0.3)
        challenger = ~hegemonic_mask & (state.phi > mean_phi * 1.5)
        if np.any(challenger):
            state.phi[challenger] += dt * 0.05 * state.phi[challenger]
            state.C[challenger] = np.maximum(state.C[challenger] - dt * 0.02, 0.1)


def apply_trade_hubs(state, dt=0.01):
    try:
        _silk_road_competition(state, dt)
        _entrepot_dynamics(state, dt)
        _hegemonic_cycles(state, dt)
    except Exception:
        raise
