"""Social and human science dynamics — inequality, cultural diffusion, collective action.

phi = social energy / wealth circulation / collective mobilization
C   = social friction / structural barriers / stratification rigidity
psi ~ 1.0 = functioning society; < 0.8 = suppressed; > 1.2 = revolutionary overload
"""
import numpy as np
from engine.physics import laplacian


def _inequality_dynamics(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    elite_mask = (state.phi > mean_phi * 2.0) & (state.C < mean_C)
    marginal_mask = state.phi < mean_phi * 0.5
    if np.any(elite_mask):
        state.phi[elite_mask] += dt * 0.08 * state.phi[elite_mask]
        state.C[elite_mask] = np.maximum(state.C[elite_mask] - dt * 0.03, 0.05)
    if np.any(marginal_mask):
        state.phi[marginal_mask] -= dt * 0.04 * state.phi[marginal_mask]
        state.phi[marginal_mask] = np.maximum(state.phi[marginal_mask], 0.01)
    redistribution = laplacian(state.phi) * 0.02
    state.phi += dt * redistribution * (mean_C / safe_C)


def _cultural_diffusion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    stable_mask = (state.psi > 0.8) & (state.psi < 1.2)
    diffusion_rate = np.where(stable_mask, 0.03 / safe_C, 0.0)
    cultural_spread = diffusion_rate * laplacian(state.phi)
    state.phi += dt * cultural_spread
    grad_y, grad_x = np.gradient(state.phi)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    mean_grad = float(np.mean(grad_mag))
    steep_boundary = grad_mag > mean_grad * 2.0
    state.C[steep_boundary] += dt * 0.02 * grad_mag[steep_boundary]


def _collective_action(state, dt):
    mobilized = state.psi > 1.2
    if not np.any(mobilized):
        return
    mobilization_field = np.where(mobilized, state.phi, 0.0)
    spread = laplacian(mobilization_field) * 0.05
    state.phi += dt * spread
    severe = mobilized & (state.psi > 1.5)
    if np.any(severe):
        state.C[severe] = np.maximum(
            state.C[severe] - dt * 0.1 * state.phi[severe], 0.05
        )
    borderline = mobilized & (state.psi < 1.4)
    state.C[borderline] += dt * 0.05


def apply_social(state, dt=0.01):
    try:
        _inequality_dynamics(state, dt)
        _cultural_diffusion(state, dt)
        _collective_action(state, dt)
    except Exception:
        raise
