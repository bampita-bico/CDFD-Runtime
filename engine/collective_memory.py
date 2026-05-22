"""Collective memory dynamics — trauma encoding, commemorative phi, historical amnesia.

phi = cultural memory intensity / commemorative energy / historical narrative flux
C   = trauma barrier / taboo / suppression of memory
psi > 1.2 = active memory / reckoning; psi < 0.6 = amnesia / suppressed history
"""
import numpy as np
from engine.physics import laplacian


def _trauma_encoding(state, dt):
    if not hasattr(state, 'trauma_layer'):
        state.trauma_layer = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    # Traumatic events: sudden phi drops encode as high C (psychic scar)
    trauma_event = state.phi < mean_phi * 0.3
    state.trauma_layer[trauma_event] += dt * 0.1
    # Trauma raises C long-term (barrier to future phi flows)
    state.C += dt * 0.02 * state.trauma_layer
    state.trauma_layer = np.maximum(state.trauma_layer - dt * 0.005, 0.0)  # slow decay


def _commemorative_phi(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Active commemoration: high phi zones reinforce memory (monuments, rituals)
    commemorating = (state.phi > mean_phi) & (state.psi > 1.0)
    if np.any(commemorating):
        # Memory phi diffuses culturally
        state.phi += dt * 0.01 * laplacian(np.where(commemorating, state.phi, 0.0))
    state.phi = np.maximum(state.phi, 0.001)


def _historical_amnesia(state, dt):
    mean_C = float(np.mean(state.C))
    # Amnesia: C decays over time (generational forgetting)
    state.C -= dt * 0.002
    state.C = np.maximum(state.C, 0.05)
    # Suppression: state power actively raises C on certain memory phi (censorship)
    mean_phi = float(np.mean(state.phi))
    suppressed = (state.phi < mean_phi * 0.5) & (state.C > mean_C * 1.5)
    if np.any(suppressed):
        state.phi[suppressed] -= dt * 0.01 * state.phi[suppressed]
        state.phi[suppressed] = np.maximum(state.phi[suppressed], 0.001)


def apply_collective_memory(state, dt=0.01):
    try:
        _trauma_encoding(state, dt)
        _commemorative_phi(state, dt)
        _historical_amnesia(state, dt)
    except Exception:
        raise
