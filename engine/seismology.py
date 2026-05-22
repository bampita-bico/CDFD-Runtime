"""Seismology — tectonic stress accumulation and seismic release.

phi = tectonic plate velocity / stress propagation flux
C   = fault lock strength / lithospheric rigidity
psi > 1.2 = aseismic creep; psi ~ 1.0 = locked fault; psi < 0.4 = rupture threshold
"""
import numpy as np
from engine.physics import laplacian


def _stress_accumulation(state, dt):
    # Tectonic loading increases constraint (stress buildup)
    loading = 0.002 * state.phi
    # Seismic waves propagate via diffusion
    diffusion = 0.005 * laplacian(state.C)
    state.C += dt * (loading + diffusion)
    state.C = np.maximum(state.C, 0.01)


def _seismic_release(state, dt):
    # Rupture when psi drops below threshold (over-constrained)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    rupture = psi < 0.4
    if np.any(rupture):
        release = 0.05 * (0.4 - psi[rupture]) * state.phi[rupture]
        state.phi[rupture] = np.maximum(state.phi[rupture] - dt * release, 0.001)
        # Constraint drops sharply at rupture (stress release)
        state.C[rupture] -= dt * 0.08 * state.C[rupture]
        state.C[rupture] = np.maximum(state.C[rupture], 0.01)


def _fault_healing(state, dt):
    # Locked faults slowly reheal (restrengthening)
    mean_C = float(np.mean(state.C))
    healing = 0.001 * (mean_C - state.C)
    state.C += dt * healing


def apply_seismology(state, dt=0.1):
    _stress_accumulation(state, dt)
    _seismic_release(state, dt)
    _fault_healing(state, dt)
