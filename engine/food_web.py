"""Full food web dynamics — producers, herbivores, carnivores, decomposers.

phi = biomass energy flux through trophic levels
C   = predation pressure / competition / metabolic constraint
psi ~ 1.0 = balanced ecosystem; < 0.6 = trophic collapse; > 1.4 = population boom
"""
import numpy as np
from engine.physics import laplacian


def _producer_layer(state, dt):
    # Primary producers: photosynthesis grows phi, bounded by carrying capacity (C)
    mean_phi = float(np.mean(state.phi))
    producers = state.phi < mean_phi * 0.8
    if np.any(producers):
        growth = state.phi[producers] * (1.0 - state.phi[producers] / (float(np.max(state.phi)) + 1e-9))
        state.phi[producers] += dt * 0.06 * growth
    # Nutrient diffusion (spatial spread)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    state.phi += dt * 0.01 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.0)


def _herbivore_carnivore_cascade(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Herbivores: consume producers (high-phi, low-C zones)
    herbivore_zone = (state.phi > mean_phi) & (state.C < mean_C)
    if np.any(herbivore_zone):
        consumed = dt * 0.04 * state.phi[herbivore_zone]
        state.phi[herbivore_zone] -= consumed
        state.C[herbivore_zone] += dt * 0.02  # grazing pressure
    # Carnivores: exploit high-density herbivore zones
    carnivore_zone = (state.phi > mean_phi * 1.5) & (state.C > mean_C)
    if np.any(carnivore_zone):
        state.phi[carnivore_zone] -= dt * 0.06 * state.phi[carnivore_zone]
        state.C[carnivore_zone] = np.maximum(state.C[carnivore_zone] - dt * 0.03, 0.05)
    state.phi = np.maximum(state.phi, 0.001)


def _decomposer_recycling(state, dt):
    # Decomposers recycle dead biomass: low-phi cells recover nutrients
    mean_phi = float(np.mean(state.phi))
    dead = state.phi < mean_phi * 0.2
    if np.any(dead):
        recycled = laplacian(state.phi) * 0.02
        state.phi[dead] += dt * np.abs(recycled[dead])
        state.C[dead] = np.maximum(state.C[dead] - dt * 0.01, 0.05)
    state.phi = np.maximum(state.phi, 0.001)


def apply_food_web(state, dt=0.01):
    try:
        _producer_layer(state, dt)
        _herbivore_carnivore_cascade(state, dt)
        _decomposer_recycling(state, dt)
    except Exception:
        raise
