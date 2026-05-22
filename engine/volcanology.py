"""Volcanology — magma chamber dynamics, eruption thresholds, lava flow.

phi = magma flux / heat flow from mantle
C   = lithostatic pressure / crustal resistance / conduit blockage
psi > 1.5 = eruption; psi ~ 1.0 = quiescent degassing; psi < 0.3 = deep intrusion
"""
import numpy as np
from engine.physics import laplacian


def _magma_recharge(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Mantle convection recharges magma chamber
    recharge = 0.003 * (mean_phi - state.phi)
    # Volatile buildup increases pressure (adds constraint)
    volatile_buildup = 0.004 * state.phi
    state.phi += dt * recharge
    state.C += dt * volatile_buildup
    state.phi = np.maximum(state.phi, 0.001)
    state.C = np.maximum(state.C, 0.01)


def _eruption_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    # Eruption when pressure exceeds crustal strength
    erupting = psi > 1.5
    if np.any(erupting):
        excess = psi[erupting] - 1.5
        release = 0.08 * excess * state.C[erupting]
        state.C[erupting] -= dt * release
        state.phi[erupting] -= dt * 0.05 * state.phi[erupting]
        state.C[erupting] = np.maximum(state.C[erupting], 0.01)
        state.phi[erupting] = np.maximum(state.phi[erupting], 0.001)


def _lava_flow(state, dt):
    # Lava diffuses from eruption zones
    diffusion = 0.003 * laplacian(state.phi)
    state.phi += dt * diffusion
    # Conduit sealing between eruptions
    mean_phi = float(np.mean(state.phi))
    sealing = 0.001 * (mean_phi - state.phi) * (1.0 - state.C)
    state.C += dt * sealing


def apply_volcanology(state, dt=0.1):
    _magma_recharge(state, dt)
    _eruption_dynamics(state, dt)
    _lava_flow(state, dt)
