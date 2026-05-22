"""Ideological dynamics — worldview competition, radicalization, hegemony, collapse.

phi = ideological conviction flux / mobilizing belief intensity
C   = cognitive dissonance barrier / outgroup hostility / counter-narrative friction
psi > 1.3 = ideological hegemony / radicalization; psi ~ 1.0 = pluralism; psi < 0.6 = belief vacuum
"""
import numpy as np
from engine.physics import laplacian


def _ideological_competition(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Dominant ideology spreads through low-C zones
    dominant = state.phi > mean_phi * 1.5
    spread = laplacian(np.where(dominant, state.phi, 0.0)) / safe_C
    state.phi += dt * 0.03 * np.where(dominant, spread, 0.0)
    # Counter-ideologies: where phi gradients are steep, C rises (ideological boundary)
    grad_y, grad_x = np.gradient(state.phi)
    boundary = np.sqrt(grad_x**2 + grad_y**2) > float(np.mean(np.sqrt(grad_x**2 + grad_y**2))) * 2.0
    state.C[boundary] += dt * 0.03
    state.phi = np.maximum(state.phi, 0.001)


def _radicalization(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Radicalization: isolated high-C, high-phi cells self-reinforce
    radical = (state.phi > mean_phi * 1.8) & (state.C > mean_C * 1.3)
    if np.any(radical):
        state.phi[radical] += dt * 0.06 * state.phi[radical]
        state.C[radical] += dt * 0.04  # epistemic closure deepens


def _ideological_collapse(state, dt):
    if not hasattr(state, 'ideological_stress'):
        state.ideological_stress = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    # Collapse: ideology fails to deliver (psi < 0.5 = belief vacuum)
    failing = state.psi < 0.5
    state.ideological_stress[failing] += dt
    state.ideological_stress[~failing] = np.maximum(state.ideological_stress[~failing] - dt * 0.3, 0.0)
    collapsing = state.ideological_stress > 4.0
    if np.any(collapsing):
        state.phi[collapsing] *= max(0.0, 1.0 - dt * 0.2)
        state.C[collapsing] -= dt * 0.1  # barriers dissolve with ideology
        state.C[collapsing] = np.maximum(state.C[collapsing], 0.05)
        state.ideological_stress[collapsing] = 0.0


def apply_ideology(state, dt=0.01):
    try:
        _ideological_competition(state, dt)
        _radicalization(state, dt)
        _ideological_collapse(state, dt)
    except Exception:
        raise
