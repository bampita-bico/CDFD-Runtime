"""Biodiversity dynamics — species richness, extinction cascades, keystone species, rewilding.

phi = species richness / ecological interaction flux / biodiversity index
C   = extinction pressure / habitat fragmentation / invasive species burden
psi > 1.0 = diversifying; psi ~ 1.0 = stable; psi < 0.5 = mass extinction cascade
"""
import numpy as np
from engine.physics import laplacian


def _species_richness_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Speciation: phi grows in stable, connected habitat (low C, high phi)
    diversifying = (state.psi > 0.9) & (state.phi > mean_phi * 0.5)
    state.phi[diversifying] += dt * 0.02 * state.phi[diversifying]
    # Dispersal: species colonize adjacent habitats
    state.phi += dt * 0.01 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _extinction_cascade(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Extinction: below viability threshold with high C, phi enters cascade
    at_risk = (state.phi < mean_phi * 0.3) & (state.C > mean_C * 1.3)
    if np.any(at_risk):
        state.phi[at_risk] -= dt * 0.06 * state.phi[at_risk]
        state.phi[at_risk] = np.maximum(state.phi[at_risk], 0.0001)
    # Cascade: extinction in one cell raises C in neighbors (trophic disruption)
    collapsed = state.phi < mean_phi * 0.05
    if np.any(collapsed):
        cascade = laplacian(np.where(collapsed, 1.0, 0.0).astype(float))
        state.C += dt * 0.05 * np.maximum(cascade, 0.0)


def _keystone_species(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Keystone: cells with both high phi and below-mean C anchor surrounding diversity
    keystone = (state.phi > mean_phi * 1.5) & (state.C < mean_C * 0.7)
    if np.any(keystone):
        # Keystone presence lowers C in neighborhood (ecosystem engineering)
        keystone_effect = laplacian(np.where(keystone, 1.0, 0.0).astype(float))
        state.C -= dt * 0.02 * np.maximum(keystone_effect, 0.0)
        state.C = np.maximum(state.C, 0.05)
        # Also supports neighbor phi
        state.phi += dt * 0.01 * np.maximum(keystone_effect, 0.0) * mean_phi


def apply_biodiversity(state, dt=0.01):
    try:
        _species_richness_dynamics(state, dt)
        _extinction_cascade(state, dt)
        _keystone_species(state, dt)
    except Exception:
        raise
