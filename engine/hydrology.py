"""Hydrological dynamics — river flows, groundwater, watersheds, flood plains.

phi = freshwater flux / river discharge / groundwater pressure
C   = soil permeability / aquifer resistance / channel friction
psi > 1.2 = flood / aquifer overpressure; psi < 0.6 = drought / aquifer depletion
"""
import numpy as np
from engine.physics import laplacian


def _river_flow(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Water flows downhill (toward low phi via gravity analog)
    grad_y, grad_x = np.gradient(state.phi)
    flow_x = -grad_x / safe_C
    flow_y = -grad_y / safe_C
    _, div_x = np.gradient(flow_x)
    div_y, _ = np.gradient(flow_y)
    state.phi += dt * 0.05 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.0)
    # Channel formation: high-flow corridors lower C (erosion)
    flow_mag = np.sqrt(flow_x**2 + flow_y**2)
    channel = flow_mag > float(np.mean(flow_mag)) * 2.0
    if np.any(channel):
        state.C[channel] = np.maximum(state.C[channel] - dt * 0.01 * flow_mag[channel], 0.05)


def _groundwater_dynamics(state, dt):
    # Recharge: high-phi surface areas push phi into aquifer (C-mediated)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    recharge = state.phi > float(np.mean(state.phi))
    if np.any(recharge):
        state.phi[recharge] -= dt * 0.01 * state.phi[recharge] / safe_C[recharge]
    # Depletion: over-extraction raises C (aquifer compaction)
    depleted = state.psi < 0.5
    if np.any(depleted):
        state.C[depleted] += dt * 0.05


def _flood_plain_dynamics(state, dt):
    # Flood plains: when psi > 1.3, phi spills laterally
    flood = state.psi > 1.3
    if np.any(flood):
        spillover = laplacian(np.where(flood, state.phi, 0.0))
        state.phi += dt * 0.1 * np.where(~flood, np.maximum(spillover, 0.0), 0.0)
        state.phi[flood] -= dt * 0.05 * state.phi[flood]
        state.phi = np.maximum(state.phi, 0.0)
        # Sediment deposition: C rises in flooded areas (alluvial soil fertility)
        state.C[flood] -= dt * 0.01  # fertile deposition lowers constraint


def apply_hydrology(state, dt=0.01):
    try:
        _river_flow(state, dt)
        _groundwater_dynamics(state, dt)
        _flood_plain_dynamics(state, dt)
    except Exception:
        raise
