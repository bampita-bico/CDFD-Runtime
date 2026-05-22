"""Geopolitical diplomacy dynamics — alliance networks, deterrence, hegemonic order, détente.

phi = diplomatic influence / soft power / alliance cohesion flux
C   = geopolitical friction / rivalry barrier / deterrence cost
psi > 1.1 = hegemonic stability; psi ~ 1.0 = multipolar balance; psi < 0.6 = failed order
"""
import numpy as np
from engine.physics import laplacian


def _alliance_formation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Allies: high-phi zones with similar phi values attract each other
    influential = state.phi > mean_phi
    # Alliance cohesion: phi diffuses between like-phi regions (balancing)
    alliance_flux = laplacian(np.where(influential, state.phi, 0.0)) / safe_C
    state.phi += dt * 0.02 * np.where(influential, alliance_flux, 0.0)
    # Alliance lowers C between members
    aligned = influential & (alliance_flux > 0)
    state.C[aligned] = np.maximum(state.C[aligned] - dt * 0.01, 0.05)
    state.phi = np.maximum(state.phi, 0.001)


def _deterrence_and_rivalry(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Rivals: high-phi zones separated by high-C barriers build deterrence
    great_powers = state.phi > mean_phi * 2.0
    if np.any(great_powers):
        # Arms/deterrence: C rises between rival cores
        neighbor_power = (
            np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
            np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
        ) / 4.0
        rival_zone = great_powers & (neighbor_power > mean_phi * 1.5)
        state.C[rival_zone] += dt * 0.04
        # Security dilemma: each power's phi grows in response
        state.phi[great_powers] += dt * 0.01 * state.phi[great_powers]


def _detente_and_normalization(state, dt):
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # Détente: when both sides have high phi and high C (mutually costly), C slowly drops
    detente = (state.phi > mean_phi * 1.5) & (state.C > mean_C * 1.5)
    if np.any(detente):
        state.C[detente] -= dt * 0.02 * (state.C[detente] - mean_C)
        state.C[detente] = np.maximum(state.C[detente], 0.1)


def apply_geopolitical_diplomacy(state, dt=0.01):
    try:
        _alliance_formation(state, dt)
        _deterrence_and_rivalry(state, dt)
        _detente_and_normalization(state, dt)
    except Exception:
        raise
