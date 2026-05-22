"""Climate and environmental dynamics — hydrological cycle, albedo feedback, extreme events.

phi = precipitation / solar energy flux / atmospheric moisture
C   = atmospheric resistance / albedo / thermal inertia
psi ~ 1.0 = temperate equilibrium; < 0.8 = drought/cold; > 1.2 = flood/heat overload
"""
import numpy as np
from engine.physics import laplacian


def _hydrological_cycle(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    moisture_flux = laplacian(state.phi) / safe_C
    state.phi += dt * 0.04 * moisture_flux
    state.phi = np.maximum(state.phi, 0.0)


def _albedo_feedback(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Cold/dry zones: high C reflects energy, phi drops further
    cold = state.phi < mean_phi
    state.C[cold] += dt * 0.05 * (1.0 - state.phi[cold] / (mean_phi + 1e-9))
    # Warm/wet zones: low C absorbs energy, phi rises
    warm = state.phi > mean_phi
    state.phi[warm] += dt * 0.03 * (mean_C / safe_C[warm])


def _extreme_events(state, dt):
    # Floods
    flood = state.psi > 1.5
    if np.any(flood):
        # Export phi to neighbors (runoff)
        exported = laplacian(np.where(flood, state.phi, 0.0))
        state.phi += dt * 0.2 * exported
        # Infrastructure damage in flooded cells
        state.C[flood] += dt * 0.5
        state.phi[flood] = np.maximum(state.phi[flood] - dt * 0.1 * state.phi[flood], 0.0)
    # Droughts
    drought = state.psi < 0.4
    if np.any(drought):
        state.phi[drought] -= dt * 0.08 * state.phi[drought]
        state.phi[drought] = np.maximum(state.phi[drought], 0.001)
        state.C[drought] += dt * 0.1  # soil degradation


def apply_climate(state, dt=0.01):
    try:
        _hydrological_cycle(state, dt)
        _albedo_feedback(state, dt)
        _extreme_events(state, dt)
    except Exception:
        raise
