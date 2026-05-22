"""Pollution dynamics — toxin diffusion, point sources, bioaccumulation, remediation.

phi = pollutant concentration flux / toxic load in circulation
C   = ecosystem resilience / detoxification capacity / regulatory enforcement
psi > 1.2 = toxic overload; psi ~ 1.0 = at threshold; psi < 0.6 = clean / remediated
"""
import numpy as np
from engine.physics import laplacian


def _toxin_diffusion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Pollutants spread via laplacian; C resists diffusion (soil/tissue binding)
    state.phi += dt * 0.04 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.0)
    # Natural degradation: phi decays slowly
    state.phi -= dt * 0.005 * state.phi
    state.phi = np.maximum(state.phi, 0.0)


def _bioaccumulation(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Top of food chain: phi accumulates beyond mean (biomagnification)
    apex = state.phi > mean_phi * 1.5
    if np.any(apex):
        state.phi[apex] += dt * 0.03 * state.phi[apex]
    # Ecosystem damage: high phi erodes C (kills organisms that maintain resilience)
    toxic = state.psi > 1.3
    if np.any(toxic):
        state.C[toxic] -= dt * 0.04 * (state.psi[toxic] - 1.0)
        state.C[toxic] = np.maximum(state.C[toxic], 0.01)


def _remediation(state, dt):
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # Active remediation: low-C zones with high phi get treated
    remediated = (state.phi > mean_phi * 1.3) & (state.C > mean_C * 1.5)
    if np.any(remediated):
        state.phi[remediated] -= dt * 0.1 * state.phi[remediated]
        state.phi[remediated] = np.maximum(state.phi[remediated], 0.0)
        state.C[remediated] += dt * 0.02  # remediation builds resilience capacity
    state.phi = np.maximum(state.phi, 0.0)


def apply_pollution(state, dt=0.01):
    try:
        _toxin_diffusion(state, dt)
        _bioaccumulation(state, dt)
        _remediation(state, dt)
    except Exception:
        raise
