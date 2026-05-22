"""Religious and belief system dynamics — diffusion, schism, institutional calcification.

phi = belief system intensity / devotional energy / ritual practice
C   = doctrinal rigidity / institutional authority / sectarian boundary
psi < 0.8 = secularization/apostasy; psi > 1.2 = fundamentalist overload / persecution
"""
import numpy as np
from engine.physics import laplacian


def _belief_diffusion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    stable = (state.psi > 0.8) & (state.psi < 1.2)
    spread = np.where(stable, 0.03 / safe_C, 0.0) * laplacian(state.phi)
    state.phi += dt * spread
    state.phi = np.maximum(state.phi, 0.0)


def _schism_dynamics(state, dt):
    grad_y, grad_x = np.gradient(state.phi)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    mean_grad = float(np.mean(grad_mag))
    tension_zone = grad_mag > mean_grad * 2.0
    if np.any(tension_zone):
        state.C[tension_zone] += dt * 0.15 * grad_mag[tension_zone]


def _institutional_calcification(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    established = (state.C > mean_C) & (state.phi > mean_phi)
    if np.any(established):
        state.C[established] += dt * 0.03 * state.phi[established]


def apply_religion(state, dt=0.01):
    try:
        _belief_diffusion(state, dt)
        _schism_dynamics(state, dt)
        _institutional_calcification(state, dt)
    except Exception:
        raise
