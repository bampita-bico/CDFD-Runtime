"""Stellar evolution dynamics — main sequence, red giant, supernova, neutron star/black hole.

phi = nuclear fusion flux / stellar energy output
C   = gravitational pressure / opacity / degeneracy pressure
psi > 1.2 = expanding giant; psi ~ 1.0 = main sequence equilibrium; psi < 0.3 = collapse
"""
import numpy as np
from engine.physics import laplacian


def _main_sequence_burning(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Fusion: phi generated proportional to C (gravitational pressure drives fusion)
    burning = (state.psi > 0.6) & (state.psi < 1.3)
    state.phi[burning] += dt * 0.02 * state.C[burning]
    # Radiation pressure: phi pushes back against C
    state.C[burning] -= dt * 0.01 * state.phi[burning] / (mean_phi + 1e-9)
    state.C = np.maximum(state.C, 0.05)
    # Fuel depletion: burning slowly reduces available fuel (phi decays at core)
    core = state.phi > mean_phi * 1.5
    state.phi[core] -= dt * 0.005 * state.phi[core]
    state.phi = np.maximum(state.phi, 0.001)


def _red_giant_expansion(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Core contraction (C rises) forces envelope expansion (phi redistributes outward)
    contracting_core = state.C > float(np.mean(state.C)) * 1.8
    if np.any(contracting_core):
        # Envelope expands: phi pushed to periphery
        expansion = laplacian(np.where(contracting_core, -state.phi, 0.0))
        state.phi += dt * 0.05 * expansion
        state.phi = np.maximum(state.phi, 0.001)


def _supernova_and_remnant(state, dt):
    if not hasattr(state, 'stellar_refractory'):
        state.stellar_refractory = np.zeros_like(state.phi)
    state.stellar_refractory = np.maximum(state.stellar_refractory - dt, 0.0)
    # Supernova: core C >> phi (degeneracy pressure fails)
    collapse = (state.C > state.phi * 3.0) & (state.stellar_refractory < 0.01)
    if np.any(collapse):
        # Massive energy release
        released = state.phi[collapse] * 0.8
        state.phi[collapse] -= released
        state.phi += dt * 0.5 * laplacian(np.where(collapse, released, 0.0))
        # Remnant: neutron star (very high C, very low phi) or black hole (C → ∞)
        state.C[collapse] += dt * 5.0
        state.phi[collapse] = np.maximum(state.phi[collapse], 0.0001)
        state.stellar_refractory[collapse] = 10.0
    state.phi = np.maximum(state.phi, 0.0)


def apply_stellar_evolution(state, dt=0.01):
    try:
        _main_sequence_burning(state, dt)
        _red_giant_expansion(state, dt)
        _supernova_and_remnant(state, dt)
    except Exception:
        raise
