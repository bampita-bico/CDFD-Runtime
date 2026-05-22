"""Climate-civilization coupling — drought migration, flood collapse, little ice age effects.

Cross-domain module: climate psi feeds into population phi and infrastructure C,
modeling Bronze Age Collapse, Maya drought, Little Ice Age famines, etc.
"""
import numpy as np
from engine.physics import laplacian


def _drought_migration(state, dt):
    # When climate psi is low (drought), populations are pushed out
    drought_zones = state.psi < 0.6
    if not np.any(drought_zones):
        return
    # Advect population away from drought stress
    grad_psi_y, grad_psi_x = np.gradient(state.psi)
    migratory_flow_x = np.where(drought_zones, -grad_psi_x * state.phi, 0.0)
    migratory_flow_y = np.where(drought_zones, -grad_psi_y * state.phi, 0.0)
    div_y, _ = np.gradient(migratory_flow_y, axis=0)
    _, div_x = np.gradient(migratory_flow_x, axis=1)
    state.phi += dt * 0.15 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.001)
    # Receiving areas face resource pressure
    receiving = (~drought_zones) & ((div_x + div_y) > 0)
    if np.any(receiving):
        state.C[receiving] += dt * 0.05


def _flood_collapse(state, dt):
    flood_zones = state.psi > 1.6
    if not np.any(flood_zones):
        return
    flood_intensity = state.psi[flood_zones] - 1.6
    state.phi[flood_zones] -= dt * 0.2 * flood_intensity * state.phi[flood_zones]
    state.phi[flood_zones] = np.maximum(state.phi[flood_zones], 0.001)
    state.C[flood_zones] += dt * 0.3 * flood_intensity
    # Trade route disruption near floods
    near_flood = laplacian(np.where(flood_zones, 1.0, 0.0).astype(float)) > 0
    if np.any(near_flood & ~flood_zones):
        state.C[near_flood & ~flood_zones] += dt * 0.05


def _little_ice_age(state, dt):
    if not hasattr(state, 'climate_cold_duration'):
        state.climate_cold_duration = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    cold = state.phi < mean_phi * 0.4
    state.climate_cold_duration[cold] += dt
    state.climate_cold_duration[~cold] = np.maximum(
        state.climate_cold_duration[~cold] - dt * 0.2, 0.0
    )
    # Sustained cold (> 5 time units) triggers cascade: famine → unrest → governance collapse
    crisis_region = state.climate_cold_duration > 5.0
    if np.any(crisis_region):
        state.C[crisis_region] += dt * 0.1
        state.phi[crisis_region] -= dt * 0.05 * state.phi[crisis_region]
        state.phi[crisis_region] = np.maximum(state.phi[crisis_region], 0.001)


def apply_climate_civilization(state, dt=0.01):
    try:
        _drought_migration(state, dt)
        _flood_collapse(state, dt)
        _little_ice_age(state, dt)
    except Exception:
        raise
