"""Permafrost and carbon feedback dynamics — thaw, methane release, thermokarst, tipping point.

phi = frozen carbon store / permafrost integrity flux
C   = thermal burden / microbial decomposition rate / methane constraint
psi < 0.7 = active thaw; psi ~ 1.0 = stable frozen; psi > 1.3 = accumulating frozen carbon
"""
import numpy as np
from engine.physics import laplacian


def _thaw_dynamics(state, dt):
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # Warming: C (thermal burden) rises in warm regions, phi (frozen carbon) decreases
    warming = state.C > mean_C * 1.1
    if np.any(warming):
        state.phi[warming] -= dt * 0.03 * (state.C[warming] - mean_C)
        state.phi[warming] = np.maximum(state.phi[warming], 0.001)
    # Thermal diffusion: warmth spreads
    state.C += dt * 0.005 * laplacian(state.C)
    state.C = np.maximum(state.C, 0.05)


def _methane_release(state, dt):
    if not hasattr(state, 'methane_accumulator'):
        state.methane_accumulator = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    # Thawed zones release methane: high C, low phi = active decomposition
    thawed = (state.phi < mean_phi * 0.5) & (state.C > float(np.mean(state.C)) * 1.2)
    if np.any(thawed):
        released = dt * 0.05 * (mean_phi - state.phi[thawed])
        state.methane_accumulator[thawed] += released
        # Methane is a GHG: further raises C globally
        state.C += dt * 0.001 * float(np.mean(state.methane_accumulator))


def _thermokarst_formation(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Thermokarst: ground collapses where phi crashes (subsidence lakes)
    collapse = state.phi < mean_phi * 0.2
    if np.any(collapse):
        state.C[collapse] += dt * 0.1
        # Positive feedback: water in thermokarst absorbs more heat
        state.C += dt * 0.005 * laplacian(np.where(collapse, state.C, 0.0))


def apply_permafrost(state, dt=0.01):
    try:
        _thaw_dynamics(state, dt)
        _methane_release(state, dt)
        _thermokarst_formation(state, dt)
    except Exception:
        raise
