"""Wetland dynamics — water retention, nutrient cycling, carbon sequestration, drainage.

phi = hydrological flux / nutrient processing rate / peat accumulation
C   = drainage burden / eutrophication / subsidence pressure
psi ~ 1.0 = healthy wetland; < 0.6 = drained/degraded; > 1.3 = flooded/waterlogged
"""
import numpy as np
from engine.physics import laplacian


def _water_retention(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Wetlands retain water: phi accumulates in low-C zones (natural sponges)
    retaining = state.C < float(np.mean(state.C)) * 0.7
    state.phi[retaining] += dt * 0.03 * state.phi[retaining]
    # Water flows into wetlands from adjacent high-phi zones
    state.phi += dt * 0.02 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _nutrient_cycling(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Nutrient uptake: wetlands remove C from water column (denitrification)
    productive = (state.psi > 0.8) & (state.psi < 1.3)
    state.C[productive] -= dt * 0.02
    state.C = np.maximum(state.C, 0.05)
    # Eutrophication: excess phi (nutrient loading) raises C (algal blooms, hypoxia)
    eutrophic = state.phi > mean_phi * 1.8
    if np.any(eutrophic):
        state.C[eutrophic] += dt * 0.04 * state.phi[eutrophic] / (mean_phi + 1e-9)


def _drainage_and_peat_loss(state, dt):
    mean_C = float(np.mean(state.C))
    # Drainage: external C pressure (agriculture, development) lowers phi
    drained = state.C > mean_C * 1.5
    if np.any(drained):
        state.phi[drained] -= dt * 0.06 * state.phi[drained]
        state.phi[drained] = np.maximum(state.phi[drained], 0.001)
        # Peat oxidation releases carbon: C (atmospheric) rises further
        state.C[drained] += dt * 0.03
    # Rewetting: intentional C reduction restores phi
    rewetted = (state.C < mean_C * 0.5) & (state.phi < float(np.mean(state.phi)) * 0.6)
    if np.any(rewetted):
        state.phi[rewetted] += dt * 0.04 * float(np.mean(state.phi))


def apply_wetlands(state, dt=0.01):
    try:
        _water_retention(state, dt)
        _nutrient_cycling(state, dt)
        _drainage_and_peat_loss(state, dt)
    except Exception:
        raise
