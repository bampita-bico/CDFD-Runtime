"""Coral reef dynamics — bleaching, recovery, crown-of-thorns outbreaks, reef building.

phi = coral productivity / calcification rate / symbiotic algae flux
C   = thermal stress / acidification burden / predation pressure
psi > 1.2 = bleaching stress; psi ~ 1.0 = healthy reef; psi < 0.6 = dead reef
"""
import numpy as np
from engine.physics import laplacian


def _reef_growth(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Healthy corals grow and recruit larvae (laplacian spread)
    healthy = (state.psi > 0.7) & (state.psi < 1.1)
    state.phi[healthy] += dt * 0.03 * state.phi[healthy]
    state.phi += dt * 0.005 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _bleaching_cascade(state, dt):
    if not hasattr(state, 'bleach_stress'):
        state.bleach_stress = np.zeros_like(state.phi)
    # Thermal stress: C rising causes symbiont expulsion (bleaching)
    thermal = state.C > float(np.mean(state.C)) * 1.4
    state.bleach_stress[thermal] += dt
    state.bleach_stress[~thermal] = np.maximum(state.bleach_stress[~thermal] - dt * 0.2, 0.0)
    bleaching = state.bleach_stress > 2.0
    if np.any(bleaching):
        state.phi[bleaching] -= dt * 0.2 * state.phi[bleaching]
        state.phi[bleaching] = np.maximum(state.phi[bleaching], 0.001)
    # Death: prolonged bleaching leads to algae overgrowth (C spikes)
    dead = state.bleach_stress > 6.0
    if np.any(dead):
        state.C[dead] += dt * 0.1
        state.phi[dead] *= max(0.0, 1.0 - dt * 0.1)


def _crown_of_thorns_outbreak(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # COTS outbreak: predator bloom on weakened reef (low phi, nutrient runoff = low C barrier)
    vulnerable = (state.phi < mean_phi * 0.6) & (state.C < mean_C * 0.7)
    if np.any(vulnerable):
        state.phi[vulnerable] -= dt * 0.08 * state.phi[vulnerable]
        state.phi[vulnerable] = np.maximum(state.phi[vulnerable], 0.001)
        state.C[vulnerable] += dt * 0.03  # predation pressure


def apply_coral_reef(state, dt=0.01):
    try:
        _reef_growth(state, dt)
        _bleaching_cascade(state, dt)
        _crown_of_thorns_outbreak(state, dt)
    except Exception:
        raise
