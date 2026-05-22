"""Crystallography — nucleation, crystal growth, and defect propagation.

phi = atomic flux / diffusion rate / supersaturation
C   = lattice strain / dislocation density / grain boundary resistance
psi > 1.5 = rapid crystallization; psi ~ 1.0 = equilibrium growth; psi < 0.3 = dissolution
"""
import numpy as np
from engine.physics import laplacian


def _crystal_growth(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    # Supersaturation drives nucleation and crystal growth
    growing = psi > 1.0
    growth_rate = np.where(growing, 0.006 * (psi - 1.0), 0.0)
    state.phi -= dt * growth_rate * state.phi
    state.phi = np.maximum(state.phi, 0.001)


def _dislocation_dynamics(state, dt):
    # Dislocations multiply under strain (stress × existing density)
    dislocation_growth = 0.004 * state.phi * state.C
    # Annealing removes defects (thermal treatment)
    annealing = 0.003 * state.C
    # Defects diffuse via climb and glide
    diffusion = 0.002 * laplacian(state.C)
    state.C += dt * (dislocation_growth - annealing + diffusion)
    state.C = np.maximum(state.C, 0.01)


def _ostwald_ripening(state, dt):
    # Large crystals grow; small ones dissolve (mean-field exchange)
    mean_phi = float(np.mean(state.phi))
    ripening = 0.002 * (mean_phi - state.phi)
    state.phi += dt * ripening


def apply_crystallography(state, dt=0.1):
    _crystal_growth(state, dt)
    _dislocation_dynamics(state, dt)
    _ostwald_ripening(state, dt)
