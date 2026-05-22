"""Consciousness and integrated information dynamics — phi integration, binding, global workspace.

phi = integrated information flux / conscious broadcast strength (IIT-inspired)
C   = neural integration barrier / modularity / unconscious binding cost
psi > 1.2 = high consciousness / global broadcast; psi < 0.5 = unconscious/anesthetic
"""
import numpy as np
from engine.physics import laplacian


def _phi_integration(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Tononi's phi: information integration across the whole system
    # High-connectivity (low-C) zones integrate phi across regions
    integration = laplacian(state.phi) / safe_C
    state.phi += dt * 0.04 * integration
    state.phi = np.maximum(state.phi, 0.0)
    # Binding: coherent regions lower C (unified experience)
    mean_phi = float(np.mean(state.phi))
    coherent = state.phi > mean_phi
    state.C[coherent] = np.maximum(state.C[coherent] - dt * 0.01, 0.05)


def _global_workspace_broadcast(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # GWT: a dominant region (high phi, low C) broadcasts to entire system
    workspace = (state.phi > mean_phi * 1.8) & (state.C < mean_C)
    if np.any(workspace):
        broadcast = laplacian(np.where(workspace, state.phi, 0.0)) * 0.05
        state.phi += dt * np.maximum(broadcast, 0.0)
    state.phi = np.maximum(state.phi, 0.0)


def _unconscious_and_anesthesia(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Anesthesia: C spikes globally, phi drops below broadcast threshold
    anesthetized = state.C > mean_C * 2.5
    if np.any(anesthetized):
        state.phi[anesthetized] -= dt * 0.1 * state.phi[anesthetized]
        state.phi[anesthetized] = np.maximum(state.phi[anesthetized], 0.001)
    # Recovery: C dissipates, phi re-integrates
    recovering = (state.C > mean_C * 1.5) & (state.phi > mean_phi * 0.5)
    state.C[recovering] -= dt * 0.05
    state.C = np.maximum(state.C, 0.05)


def apply_consciousness(state, dt=0.01):
    try:
        _phi_integration(state, dt)
        _global_workspace_broadcast(state, dt)
        _unconscious_and_anesthesia(state, dt)
    except Exception:
        raise
