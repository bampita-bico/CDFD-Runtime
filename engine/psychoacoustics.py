"""Psychoacoustics — auditory perception, masking, and cognitive load.

phi = acoustic energy flux / auditory neural firing rate
C   = masking threshold / cognitive load / auditory fatigue
psi > 1.4 = hyperacusis / overload; psi ~ 1.0 = normal hearing; psi < 0.4 = masked signal
"""
import numpy as np
from engine.physics import laplacian


def _auditory_adaptation(state, dt):
    # Prolonged stimulation reduces neural gain (adaptation)
    adaptation = 0.005 * state.phi
    # Cognitive fatigue accumulates from sustained attention
    fatigue = 0.003 * state.phi * state.C
    state.C += dt * fatigue
    state.phi -= dt * adaptation
    state.phi = np.maximum(state.phi, 0.001)


def _threshold_recovery(state, dt):
    mean_C = float(np.mean(state.C))
    # Silence restores hearing threshold (release from masking)
    recovery = 0.004 * (mean_C - state.C)
    state.C += dt * recovery
    state.C = np.maximum(state.C, 0.01)


def _attention_modulation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    psi = state.phi / safe_C
    # Top-down attention boosts signal in masked regions
    masked = psi < 0.5
    if np.any(masked):
        attention_gain = 0.003 * (0.5 - psi[masked])
        state.phi[masked] += dt * attention_gain * state.phi[masked]
    # Spatial spread of auditory processing (tonotopic map)
    spread = 0.001 * laplacian(state.phi)
    state.phi += dt * spread


def apply_psychoacoustics(state, dt=0.1):
    _auditory_adaptation(state, dt)
    _threshold_recovery(state, dt)
    _attention_modulation(state, dt)
