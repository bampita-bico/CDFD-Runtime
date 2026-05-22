"""Geological dynamics — tectonic stress, earthquakes, volcanism, mountain building.

phi = tectonic energy flux / mantle convection
C   = crustal rigidity / fault lock strength
psi > 1.4 = imminent rupture; psi ~ 1.0 = slow creep; psi < 0.6 = locked fault
"""
import numpy as np
from engine.physics import laplacian


def _tectonic_stress_accumulation(state, dt):
    # Stress builds where phi is high and C is high (locked faults)
    mean_phi = float(np.mean(state.phi))
    locked = state.C > float(np.mean(state.C)) * 1.3
    state.phi[locked] += dt * 0.02 * state.phi[locked]
    # Slow creep in low-C zones dissipates stress
    creep = state.C < float(np.mean(state.C)) * 0.7
    state.phi[creep] -= dt * 0.01 * state.phi[creep]
    state.phi = np.maximum(state.phi, 0.0)


def _earthquake_rupture(state, dt):
    if not hasattr(state, 'seismic_refractory'):
        state.seismic_refractory = np.zeros_like(state.phi)
    state.seismic_refractory = np.maximum(state.seismic_refractory - dt, 0.0)
    rupture = (state.psi > 1.4) & (state.seismic_refractory < 0.01)
    if np.any(rupture):
        released = state.phi[rupture] * 0.6
        state.phi[rupture] -= released
        # Energy radiates outward
        state.phi += dt * 0.3 * laplacian(np.where(rupture, released, 0.0))
        state.C[rupture] = np.maximum(state.C[rupture] - dt * 2.0, 0.1)
        state.seismic_refractory[rupture] = 3.0
    state.phi = np.maximum(state.phi, 0.0)


def _mountain_building(state, dt):
    mean_C = float(np.mean(state.C))
    # Convergent zones: high phi gradient builds mountains (C increases permanently)
    grad_y, grad_x = np.gradient(state.phi)
    compression = np.sqrt(grad_x**2 + grad_y**2)
    mean_comp = float(np.mean(compression))
    convergent = compression > mean_comp * 2.0
    if np.any(convergent):
        state.C[convergent] += dt * 0.005 * compression[convergent]
    # Erosion: high-C ridges slowly lose phi (weathering)
    ridge = state.C > mean_C * 1.5
    state.phi[ridge] -= dt * 0.002 * state.C[ridge]
    state.phi = np.maximum(state.phi, 0.0)


def apply_geology(state, dt=0.01):
    try:
        _tectonic_stress_accumulation(state, dt)
        _earthquake_rupture(state, dt)
        _mountain_building(state, dt)
    except Exception:
        raise
