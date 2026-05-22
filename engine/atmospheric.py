"""Atmospheric dynamics — circulation patterns, jet streams, pressure systems.

phi = atmospheric mass flux / wind velocity
C   = pressure gradient resistance / inversion layer / blocking high
psi > 1.3 = jet stream / zonal flow; psi ~ 1.0 = balanced; psi < 0.5 = stagnation
"""
import numpy as np
from engine.physics import laplacian


def _baroclinic_forcing(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    # Temperature gradients drive atmospheric flow
    forcing = 0.005 * np.maximum(1.0 - psi, 0.0)
    # Atmospheric friction (boundary layer drag)
    friction = 0.004 * state.phi
    state.phi += dt * (forcing - friction)
    state.phi = np.maximum(state.phi, 0.001)


def _blocking_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    mean_C = float(np.mean(state.C))
    # Rossby wave breaking causes blocking (raises constraint)
    blocking = 0.003 * np.exp(-np.clip(psi, 0, 5))
    # Radiative relaxation dissipates blocking patterns
    relaxation = 0.002 * state.C
    # Lateral diffusion of pressure anomalies
    diffusion = 0.004 * laplacian(state.C)
    state.C += dt * (blocking - relaxation + diffusion)
    state.C = np.maximum(state.C, 0.01)


def _advection(state, dt):
    # Momentum advection: smooth spatial gradients in phi
    spread = 0.003 * laplacian(state.phi)
    state.phi += dt * spread


def apply_atmospheric(state, dt=0.1):
    _baroclinic_forcing(state, dt)
    _blocking_dynamics(state, dt)
    _advection(state, dt)
