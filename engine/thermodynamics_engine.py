"""Thermodynamic dynamics — entropy production, heat death, Maxwell demon, dissipative structures.

phi = free energy flux / negentropy / ordered structure
C   = entropy burden / thermal equilibration / disorder accumulation
psi > 1.0 = free energy available; psi < 0.4 = approaching heat death / maximum entropy
"""
import numpy as np
from engine.physics import laplacian


def _entropy_production(state, dt):
    # Second law: C (entropy) always increases; phi (free energy) degrades
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Entropy diffuses universally
    state.C += dt * 0.01 * laplacian(state.C)
    state.C = np.maximum(state.C, 0.05)
    # Free energy dissipates proportional to use
    state.phi -= dt * 0.005 * state.C * state.phi / safe_C
    state.phi = np.maximum(state.phi, 0.0)


def _dissipative_structures(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Far-from-equilibrium zones spontaneously organize (Prigogine)
    # High phi-gradient regions self-organize: local C drops (order forms)
    grad_y, grad_x = np.gradient(state.phi)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    organizing = grad_mag > float(np.mean(grad_mag)) * 2.0
    if np.any(organizing):
        state.C[organizing] -= dt * 0.02 * grad_mag[organizing] / (float(np.max(grad_mag)) + 1e-9)
        state.C[organizing] = np.maximum(state.C[organizing], 0.05)
        state.phi[organizing] += dt * 0.01 * grad_mag[organizing]


def _maxwell_demon(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Demon effect: intelligence/life locally reduces entropy (C) at cost of global entropy increase
    demon_zones = (state.phi > mean_phi * 1.5) & (state.C < mean_C)
    if np.any(demon_zones):
        # Local entropy reduction
        state.C[demon_zones] -= dt * 0.01 * state.phi[demon_zones] / (mean_phi + 1e-9)
        state.C[demon_zones] = np.maximum(state.C[demon_zones], 0.01)
        # Global entropy compensates (Landauer's principle)
        state.C += dt * 0.001 * float(np.sum(demon_zones)) / state.phi.size


def apply_thermodynamics_engine(state, dt=0.01):
    try:
        _entropy_production(state, dt)
        _dissipative_structures(state, dt)
        _maxwell_demon(state, dt)
    except Exception:
        raise
