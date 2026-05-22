"""Language spread and endangerment dynamics.

phi = linguistic vitality / speaker density / textual production
C   = linguistic barrier (script difference, grammar distance, prestige gap)
psi < 0.8 = endangered language; psi > 1.2 = expansionist lingua franca
"""
import numpy as np
from engine.physics import laplacian


def _lingua_franca_expansion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    prestige_boost = np.where(state.psi > 1.0, 1.5, 1.0)
    expansion_rate = prestige_boost * 0.03 / safe_C
    high_phi = state.phi > mean_phi
    diffusion = expansion_rate * laplacian(state.phi)
    state.phi += dt * np.where(high_phi, diffusion, 0.0)


def _language_death(state, dt):
    if not hasattr(state, 'language_stress'):
        state.language_stress = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    endangered = (state.phi < mean_phi * 0.3) & (state.C > mean_C)
    state.language_stress[endangered] += dt
    state.language_stress[~endangered] = np.maximum(
        state.language_stress[~endangered] - dt * 0.5, 0.0
    )
    collapsing = state.language_stress > 5.0
    if np.any(collapsing):
        state.phi[collapsing] *= max(0.0, 1.0 - dt * 0.3)
        state.phi[collapsing] = np.maximum(state.phi[collapsing], 0.001)


def _diglossia(state, dt):
    grad_y, grad_x = np.gradient(state.phi)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    mean_grad = float(np.mean(grad_mag))
    boundary = grad_mag > mean_grad * 2.0
    interior = grad_mag < mean_grad * 0.5
    state.C[boundary] += dt * 0.03 * grad_mag[boundary]
    state.C[interior] = np.maximum(state.C[interior] - dt * 0.005, 0.05)


def apply_language_spread(state, dt=0.01):
    try:
        _lingua_franca_expansion(state, dt)
        _language_death(state, dt)
        _diglossia(state, dt)
    except Exception:
        raise
