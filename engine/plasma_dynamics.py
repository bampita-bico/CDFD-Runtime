"""Plasma dynamics — magnetic confinement, instabilities, reconnection, fusion threshold.

phi = plasma energy flux / particle current density
C   = magnetic field constraint / MHD instability burden / resistivity
psi > 1.3 = runaway instability; psi ~ 1.0 = confined equilibrium; psi < 0.5 = quench
"""
import numpy as np
from engine.physics import laplacian


def _magnetic_confinement(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Magnetic field (C) confines plasma (phi); phi diffuses against C
    state.phi += dt * 0.03 * laplacian(state.phi) / (safe_C ** 2)
    state.phi = np.maximum(state.phi, 0.0)
    # Field strengthening: high phi pressures C upward (diamagnetic effect)
    mean_phi = float(np.mean(state.phi))
    high_pressure = state.phi > mean_phi * 1.5
    state.C[high_pressure] += dt * 0.02 * state.phi[high_pressure] / (mean_phi + 1e-9)


def _mhd_instability(state, dt):
    if not hasattr(state, 'plasma_refractory'):
        state.plasma_refractory = np.zeros_like(state.phi)
    state.plasma_refractory = np.maximum(state.plasma_refractory - dt, 0.0)
    # Kink/tearing instability: when psi > 1.3
    unstable = (state.psi > 1.3) & (state.plasma_refractory < 0.01)
    if np.any(unstable):
        state.phi += dt * 0.2 * laplacian(np.where(unstable, state.phi, 0.0))
        state.C[unstable] += dt * 0.5
        state.plasma_refractory[unstable] = 1.0
    state.phi = np.maximum(state.phi, 0.0)


def _magnetic_reconnection(state, dt):
    # Reconnection: where C gradient is very steep, field lines snap and phi releases
    grad_C_y, grad_C_x = np.gradient(state.C)
    reconnection_zone = np.sqrt(grad_C_x**2 + grad_C_y**2) > float(np.mean(np.sqrt(grad_C_x**2 + grad_C_y**2))) * 2.5
    if np.any(reconnection_zone):
        state.phi[reconnection_zone] += dt * 0.3 * state.C[reconnection_zone]
        state.C[reconnection_zone] -= dt * 0.4 * state.C[reconnection_zone]
        state.C[reconnection_zone] = np.maximum(state.C[reconnection_zone], 0.05)


def apply_plasma_dynamics(state, dt=0.01):
    try:
        _magnetic_confinement(state, dt)
        _mhd_instability(state, dt)
        _magnetic_reconnection(state, dt)
    except Exception:
        raise
