"""Media and information dynamics — narrative diffusion, filter bubbles, information cascades.

phi = narrative intensity / information signal strength
C   = epistemic friction / media plurality / critical thinking barrier
psi > 1.2 = information cascade / viral spread; psi < 0.8 = information desert / censorship
"""
import numpy as np
from engine.physics import laplacian


def _narrative_diffusion(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    spread = laplacian(state.phi) / safe_C
    state.phi += dt * 0.04 * spread
    # Dominant narratives suppress competing signals (Overton narrowing)
    dominant = state.phi > mean_phi * 1.5
    if np.any(dominant):
        state.C[dominant] += dt * 0.04 * state.phi[dominant] / (mean_phi + 1e-9)
    state.phi = np.maximum(state.phi, 0.0)


def _filter_bubbles(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    bubble = (state.C > mean_C) & (state.phi > mean_phi)
    if np.any(bubble):
        # Echo chamber: C deepens, phi grows locally
        state.C[bubble] += dt * 0.03 * state.phi[bubble] * (state.C[bubble] / (mean_C + 1e-9))
        state.phi[bubble] += dt * 0.02 * state.phi[bubble]


def _information_cascade(state, dt):
    if not hasattr(state, 'media_cascade_front'):
        state.media_cascade_front = np.zeros_like(state.phi)
    trigger = state.psi > 1.5
    state.media_cascade_front[trigger] = 1.0
    # Cascade spreads: neighbors with psi > 1.2 adopt
    cascade_spread = laplacian(state.media_cascade_front)
    receptive = (state.psi > 1.2) & (cascade_spread > 0)
    if np.any(receptive):
        # Phi jumps toward sender level
        neighbor_phi = (
            np.roll(state.phi, 1, axis=0) + np.roll(state.phi, -1, axis=0) +
            np.roll(state.phi, 1, axis=1) + np.roll(state.phi, -1, axis=1)
        ) / 4.0
        state.phi[receptive] = np.maximum(
            state.phi[receptive],
            neighbor_phi[receptive] * 0.8
        )
        state.media_cascade_front[receptive] = 1.0
    # Cascade decays at high-C barriers and low-phi sinks
    state.media_cascade_front *= np.where(state.C > float(np.mean(state.C)) * 2.0, 0.0, 1.0)
    state.media_cascade_front *= np.where(state.phi < float(np.mean(state.phi)) * 0.3, 0.0, 1.0)


def apply_media(state, dt=0.01):
    try:
        _narrative_diffusion(state, dt)
        _filter_bubbles(state, dt)
        _information_cascade(state, dt)
    except Exception:
        raise
