"""Symbiosis dynamics — mutualism, parasitism, commensalism, coevolution.

phi = biological interaction flux / resource exchange rate
C   = species barrier / immune exclusion / competitive interference
psi ~ 1.0 = balanced interaction; > 1.2 = mutualist boom; < 0.6 = parasitic drain
"""
import numpy as np
from engine.physics import laplacian


def _mutualism(state, dt):
    # Mutualist pairs: both phi rises, C between them drops
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    mutualist = (state.psi > 1.0) & (state.C < mean_C)
    if np.any(mutualist):
        state.phi[mutualist] += dt * 0.04 * state.phi[mutualist]
        state.C[mutualist] = np.maximum(state.C[mutualist] - dt * 0.01, 0.05)


def _parasitism(state, dt):
    # Parasite: high-phi cells drain phi from neighbors, raising their C
    mean_phi = float(np.mean(state.phi))
    parasite = state.phi > mean_phi * 1.8
    if np.any(parasite):
        drain = laplacian(np.where(parasite, state.phi, 0.0)) * 0.05
        state.phi -= dt * np.where(~parasite, np.maximum(-drain, 0.0), 0.0)
        state.C += dt * 0.02 * np.where(~parasite, np.maximum(-drain, 0.0), 0.0)
        # Parasite also gains
        state.phi[parasite] += dt * 0.03 * state.phi[parasite]
    state.phi = np.maximum(state.phi, 0.001)


def _coevolution(state, dt):
    # Arms race between host C and parasite phi
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # High-phi parasites drive host C up (immune evolution)
    exposed_host = (~(state.phi > mean_phi * 1.8)) & (state.C < mean_C)
    state.C[exposed_host] += dt * 0.015
    # High-C hosts drive parasite phi to evolve higher
    resistant_host = state.C > mean_C * 1.5
    parasite_evolution = resistant_host & (state.phi > mean_phi)
    if np.any(parasite_evolution):
        state.phi[parasite_evolution] += dt * 0.02 * state.phi[parasite_evolution]


def apply_symbiosis(state, dt=0.01):
    try:
        _mutualism(state, dt)
        _parasitism(state, dt)
        _coevolution(state, dt)
    except Exception:
        raise
