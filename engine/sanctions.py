"""Economic sanctions dynamics — targeted C spikes, black-market rerouting, sanction fatigue.

phi = economic activity / trade volume
C   = sanction burden / international isolation / compliance cost
psi < 0.6 = sanctions biting; psi ~ 1.0 = sanctions evaded; psi > 1.2 = sanctions strengthening target
"""
import numpy as np
from engine.physics import laplacian


def _sanction_imposition(state, dt):
    if not hasattr(state, 'sanction_target'):
        state.sanction_target = np.zeros_like(state.phi, dtype=bool)
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # Sanctioned zones: C spikes, phi drops (trade cut off)
    sanctioned = state.sanction_target
    if np.any(sanctioned):
        state.C[sanctioned] += dt * 0.15
        state.phi[sanctioned] -= dt * 0.06 * state.phi[sanctioned]
        state.phi[sanctioned] = np.maximum(state.phi[sanctioned], 0.01)


def _black_market_rerouting(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_C = float(np.mean(state.C))
    sanctioned = getattr(state, 'sanction_target', np.zeros_like(state.phi, dtype=bool))
    if not np.any(sanctioned):
        return
    # Black market: high-C sanctioned zones reroute phi through third-party low-C neighbors
    neighbor_C = (
        np.roll(state.C, 1, axis=0) + np.roll(state.C, -1, axis=0) +
        np.roll(state.C, 1, axis=1) + np.roll(state.C, -1, axis=1)
    ) / 4.0
    third_party = (~sanctioned) & (neighbor_C > mean_C * 0.8) & (state.C < mean_C)
    if np.any(third_party):
        # Third parties gain phi (sanctions-busting trade profits)
        state.phi[third_party] += dt * 0.03 * float(np.mean(state.phi[sanctioned]))
        # Sanctioned zone partially recovers phi through illicit channel
        state.phi[sanctioned] += dt * 0.02 * float(np.mean(state.phi[third_party]))


def _sanction_fatigue(state, dt):
    if not hasattr(state, 'sanction_duration'):
        state.sanction_duration = np.zeros_like(state.phi)
    sanctioned = getattr(state, 'sanction_target', np.zeros_like(state.phi, dtype=bool))
    state.sanction_duration[sanctioned] += dt
    # Sanction fatigue: C imposed by sanctions gradually erodes (enforcement slips)
    fatigued = state.sanction_duration > 10.0
    if np.any(fatigued & sanctioned):
        state.C[fatigued & sanctioned] -= dt * 0.02
        state.C[fatigued & sanctioned] = np.maximum(state.C[fatigued & sanctioned], 0.1)


def apply_sanctions(state, dt=0.01):
    try:
        if not hasattr(state, 'sanction_target'):
            state.sanction_target = np.zeros_like(state.phi, dtype=bool)
        _sanction_imposition(state, dt)
        _black_market_rerouting(state, dt)
        _sanction_fatigue(state, dt)
    except Exception:
        raise
