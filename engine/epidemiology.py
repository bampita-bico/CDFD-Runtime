"""Epidemiological dynamics — spatial disease spread, immunity buildup, epidemic waves.

phi = pathogen load / infection prevalence
C   = host immunity / public health infrastructure / herd immunity threshold
psi > 1.0 = epidemic spreading; psi < 0.8 = controlled; > 2.0 = runaway pandemic

Distinct from medicine.py (clinical treatment); this models population-level spatial spread.
"""
import numpy as np
from engine.physics import laplacian


def _spatial_spread(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # General diffusion through immune barrier
    spread = laplacian(state.phi) / safe_C
    state.phi += dt * 0.03 * spread
    # Superspreader cells shed extra load to neighbors
    superspreader = (state.phi > mean_phi * 2.0) & (state.C < mean_C)
    if np.any(superspreader):
        extra = laplacian(np.where(superspreader, state.phi, 0.0))
        state.phi += dt * 0.12 * extra / safe_C
    state.phi = np.maximum(state.phi, 0.0)


def _immunity_buildup(state, dt):
    # Natural immunity: high exposure builds C
    state.C += dt * 0.05 * state.phi
    # Waning immunity: C slowly decays
    state.C -= dt * 0.005
    state.C = np.maximum(state.C, 0.05)


def _epidemic_waves(state, dt):
    if not hasattr(state, 'epi_wave_counter'):
        state.epi_wave_counter = 0.0
    if not hasattr(state, 'epi_peak_phi'):
        state.epi_peak_phi = float(np.max(state.phi))
    current_max = float(np.max(state.phi))
    state.epi_peak_phi = max(state.epi_peak_phi, current_max)
    mean_psi = float(np.mean(state.psi))
    # Herd immunity threshold: wave collapses
    if mean_psi < 0.5 and state.epi_peak_phi > 0.1:
        state.phi *= max(0.0, 1.0 - dt * 0.4)
        state.epi_wave_counter += dt
    # After wave ends, reset peak and begin waning immunity for next wave
    if current_max < state.epi_peak_phi * 0.1 and state.epi_wave_counter > 0.5:
        state.epi_peak_phi = 0.0
        state.epi_wave_counter = 0.0
        # Waning: accelerate C decay to set up susceptible population
        state.C -= dt * 0.05
        state.C = np.maximum(state.C, 0.05)


def apply_epidemiology(state, dt=0.01):
    try:
        _spatial_spread(state, dt)
        _immunity_buildup(state, dt)
        _epidemic_waves(state, dt)
    except Exception:
        raise
