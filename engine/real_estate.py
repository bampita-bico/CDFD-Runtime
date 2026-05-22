"""Real estate dynamics — land rent, gentrification, housing bubbles, zoning barriers.

phi = housing / land use flux / real property value flow
C   = zoning restriction / affordability stress / speculation barrier
psi > 1.2 = bubble / rent extraction; psi ~ 1.0 = functional market; psi < 0.7 = blight
"""
import numpy as np
from engine.physics import laplacian


def _land_rent_accumulation(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Georgist rent: central/accessible cells (low C, high phi) capture location value
    premium = (state.phi > mean_phi) & (state.C < mean_C)
    if np.any(premium):
        state.phi[premium] += dt * 0.04 * state.phi[premium]
        state.C[premium] += dt * 0.02  # rising rents increase access barrier


def _gentrification(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Gentrification: high-phi frontier advances into low-phi, previously low-C zones
    frontier = (state.phi > mean_phi * 1.5) & (state.C < mean_C)
    if np.any(frontier):
        # Phi spreads into adjacent low-phi areas
        gentrify_spread = laplacian(np.where(frontier, state.phi, 0.0)) * 0.03
        state.phi += dt * np.maximum(gentrify_spread, 0.0)
        # C rises in gentrifying zones (displacement)
        state.C += dt * 0.02 * np.where(gentrify_spread > 0, 1.0, 0.0)
    state.phi = np.maximum(state.phi, 0.001)


def _housing_bubble(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Speculative bubble: phi grows far above mean, C (debt service) accumulates
    bubble = state.phi > mean_phi * 2.5
    if np.any(bubble):
        state.phi[bubble] += dt * 0.06 * state.phi[bubble]
        state.C[bubble] += dt * 0.04 * state.phi[bubble] / (mean_phi + 1e-9)
    # Bust: when C exceeds phi (mortgage default threshold)
    bust = state.C > state.phi * 1.4
    if np.any(bust):
        state.phi[bust] -= dt * 0.3 * state.phi[bust]
        state.phi[bust] = np.maximum(state.phi[bust], 0.01)
        state.C[bust] += dt * 0.2  # foreclosure / vacancy raises friction


def apply_real_estate(state, dt=0.01):
    try:
        _land_rent_accumulation(state, dt)
        _gentrification(state, dt)
        _housing_bubble(state, dt)
    except Exception:
        raise
