"""Military conflict dynamics — force projection, arms races, guerrilla asymmetry.

phi = military force projection / mobilized violence
C   = defensive fortification / terrain friction / distance attenuation
psi > 1.2 = offensive dominance; psi ~ 1.0 = stalemate; psi < 0.8 = defensive hold
"""
import numpy as np
from engine.physics import laplacian


def _force_projection(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    attackers = state.phi > mean_phi * 2.0
    if not np.any(attackers):
        return
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_x = grad_phi_x / safe_C
    flux_y = grad_phi_y / safe_C
    flux_mag = np.sqrt(flux_x**2 + flux_y**2)
    # Targets: cells receiving inbound flux from attacker neighbors
    target_flux = np.where(attackers, flux_mag, 0.0)
    incoming = laplacian(target_flux)
    receiving = (incoming > 0) & (~attackers)
    if np.any(receiving):
        # Occupation: phi accumulates, infrastructure destroyed
        state.phi[receiving] += dt * 0.05 * incoming[receiving]
        state.C[receiving] -= dt * 0.1 * incoming[receiving]
        state.C[receiving] = np.maximum(state.C[receiving], 0.05)


def _arms_race(state, dt):
    mean_phi = float(np.mean(state.phi))
    high_mil = state.phi > mean_phi * 1.5
    # Detect adjacency: a high-phi cell with high-phi neighbors
    neighbor_phi = (
        np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
        np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
    ) / 4.0
    escalating = high_mil & (neighbor_phi > mean_phi * 1.5)
    if np.any(escalating):
        state.phi[escalating] += dt * 0.05 * state.phi[escalating]
        state.C[escalating] += dt * 0.03  # fortification buildup


def _guerrilla_asymmetry(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Weak cells surrounded by strong attackers
    neighbor_phi = (
        np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
        np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
    ) / 4.0
    insurgent = (state.psi < 0.5) & (state.phi < mean_phi * 0.3) & (neighbor_phi > mean_phi * 1.5)
    if np.any(insurgent):
        safe_phi = np.where(state.phi[insurgent] > 1e-9, state.phi[insurgent], 1e-9)
        state.C[insurgent] += dt * 0.2 * (mean_phi / safe_phi)
        # Slow phi recovery from untouched surroundings
        recovery = laplacian(state.phi) * 0.01
        state.phi[insurgent] += dt * np.abs(recovery[insurgent])


def apply_conflict(state, dt=0.01):
    try:
        _force_projection(state, dt)
        _arms_race(state, dt)
        _guerrilla_asymmetry(state, dt)
    except Exception:
        raise
