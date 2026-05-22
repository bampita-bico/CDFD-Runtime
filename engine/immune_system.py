"""Immune system spatial dynamics — innate response, adaptive immunity, autoimmunity.

phi = immune activation flux / effector cell density
C   = pathogen load / inflammatory burden / tissue damage
psi > 1.2 = active immune response; psi ~ 1.0 = surveillance; psi < 0.5 = immunodeficiency
"""
import numpy as np
from engine.physics import laplacian


def _innate_response(state, dt):
    # Innate: fast, nonspecific; phi surges where C (pathogen/damage) is high
    mean_C = float(np.mean(state.C))
    threatened = state.C > mean_C * 1.3
    if np.any(threatened):
        state.phi[threatened] += dt * 0.15 * state.C[threatened]
        # Inflammation: C rises further initially (cytokine storm risk)
        state.C[threatened] += dt * 0.05 * state.phi[threatened]
    # Resolution: where phi > C (cleared), C drops
    cleared = state.phi > state.C * 1.2
    state.C[cleared] -= dt * 0.1 * (state.phi[cleared] - state.C[cleared])
    state.C = np.maximum(state.C, 0.05)
    state.phi = np.maximum(state.phi, 0.001)


def _adaptive_immunity(state, dt):
    # Adaptive: slower but specific; memory cells (high-phi zones) rapidly clear future C
    mean_phi = float(np.mean(state.phi))
    memory = state.phi > mean_phi * 1.5
    if np.any(memory):
        # Rapid C clearance where memory exists
        state.C[memory] = np.maximum(state.C[memory] - dt * 0.2 * state.phi[memory], 0.05)
    # Spatial spread of immune signal (lymphatic flow)
    state.phi += dt * 0.02 * laplacian(state.phi)
    state.phi = np.maximum(state.phi, 0.001)


def _autoimmunity(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Autoimmune: phi attacks low-C self tissue
    autoimmune = (state.phi > mean_phi * 2.0) & (state.C < mean_C * 0.5)
    if np.any(autoimmune):
        # Self tissue phi drops (organ damage), C spikes (fibrosis)
        state.phi[autoimmune] -= dt * 0.08 * state.phi[autoimmune]
        state.phi[autoimmune] = np.maximum(state.phi[autoimmune], 0.01)
        state.C[autoimmune] += dt * 0.1


def apply_immune_system(state, dt=0.01):
    try:
        _innate_response(state, dt)
        _adaptive_immunity(state, dt)
        _autoimmunity(state, dt)
    except Exception:
        raise
