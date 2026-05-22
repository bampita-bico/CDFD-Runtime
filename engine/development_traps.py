"""Development trap dynamics — poverty traps, middle-income trap, resource curse, Dutch disease.

phi = productive economic output / human capital accumulation
C   = structural barriers / institutional weakness / commodity dependency
psi > 1.0 = development momentum; psi < 0.6 = trap condition
"""
import numpy as np
from engine.physics import laplacian


def _poverty_trap(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Poverty trap: low phi cannot fund the investment needed to raise phi
    trapped = (state.phi < mean_phi * 0.4) & (state.C > mean_C)
    if np.any(trapped):
        # Self-reinforcing decline
        state.phi[trapped] -= dt * 0.03 * state.phi[trapped]
        state.phi[trapped] = np.maximum(state.phi[trapped], 0.001)
        state.C[trapped] += dt * 0.02
    # Escape velocity: external phi injection (aid / FDI threshold)
    escape = trapped & (state.phi > mean_phi * 0.35)
    if np.any(escape):
        boost = laplacian(state.phi) * 0.02
        state.phi[escape] += dt * np.abs(boost[escape])


def _middle_income_trap(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Middle-income: can't compete on low wages (cost risen) or high-tech (skill gap = high C)
    mid = (state.phi > mean_phi * 0.7) & (state.phi < mean_phi * 1.3) & (state.C > mean_C)
    if np.any(mid):
        # Stagnation: phi growth slows
        state.phi[mid] += dt * 0.005 * state.phi[mid]  # slower than normal
        state.C[mid] += dt * 0.01  # structural C doesn't drop


def _resource_curse(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Resource windfall: sudden phi injection in low-C resource zones
    resource_boom = (state.phi > mean_phi * 2.0) & (state.C < mean_C * 0.6)
    if np.any(resource_boom):
        # Dutch disease: manufacturing phi collapses in non-resource sectors
        non_resource = ~resource_boom & (state.phi > mean_phi * 0.8)
        if np.any(non_resource):
            state.phi[non_resource] -= dt * 0.04 * state.phi[non_resource]
            state.phi[non_resource] = np.maximum(state.phi[non_resource], 0.01)
        # Institutional deterioration: C rises (corruption, patronage)
        state.C[resource_boom] += dt * 0.03


def apply_development_traps(state, dt=0.01):
    try:
        _poverty_trap(state, dt)
        _middle_income_trap(state, dt)
        _resource_curse(state, dt)
    except Exception:
        raise
