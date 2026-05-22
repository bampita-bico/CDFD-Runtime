"""Organizational dynamics — firm formation, growth, bureaucratic decay, creative destruction.

phi = organizational output flux / productive capacity / innovation throughput
C   = bureaucratic overhead / coordination cost / institutional inertia
psi > 1.1 = high-performance; psi ~ 1.0 = viable; psi < 0.6 = organizational failure
"""
import numpy as np
from engine.physics import laplacian


def _firm_formation_and_growth(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # New firms emerge in low-C, low-phi zones (market opportunity)
    opportunity = (state.phi < mean_phi * 0.6) & (state.C < float(np.mean(state.C)) * 0.8)
    if np.any(opportunity):
        state.phi[opportunity] += dt * 0.04 * mean_phi
    # Growing firms: phi scales, C rises slowly (Penrose growth constraint)
    growing = (state.phi > mean_phi) & (state.psi > 1.0)
    state.phi[growing] += dt * 0.03 * state.phi[growing]
    state.C[growing] += dt * 0.01 * state.phi[growing] / (mean_phi + 1e-9)
    # Spillovers: phi diffuses to adjacent zones (knowledge externalities)
    state.phi += dt * 0.005 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _bureaucratic_decay(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Large orgs: C rises with size (span of control, committee overhead)
    large = state.phi > mean_phi * 1.8
    if np.any(large):
        state.C[large] += dt * 0.02 * (state.phi[large] / (mean_phi + 1e-9))
    # Ossified: when C >> phi, org loses productivity (Weberian iron cage)
    ossified = state.C > state.phi * 2.0
    if np.any(ossified):
        state.phi[ossified] -= dt * 0.05 * state.phi[ossified]
        state.phi[ossified] = np.maximum(state.phi[ossified], 0.01)


def _organizational_death_and_rebirth(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Firm death: phi collapses, zone becomes opportunity for new entrants
    dying = (state.psi < 0.4) & (state.phi < mean_phi * 0.3)
    if np.any(dying):
        state.phi[dying] *= max(0.0, 1.0 - dt * 0.3)
        state.C[dying] -= dt * 0.1  # dismantling lowers C (releasing resources)
        state.C[dying] = np.maximum(state.C[dying], 0.05)
    # Spin-offs: high-phi, high-C orgs spawn new low-C ventures nearby
    spinning = (state.phi > mean_phi * 2.0) & (state.C > float(np.mean(state.C)) * 1.5)
    if np.any(spinning):
        spinoff_phi = laplacian(np.where(spinning, state.phi * 0.1, 0.0))
        state.phi += dt * np.maximum(spinoff_phi, 0.0)


def apply_organizational_dynamics(state, dt=0.01):
    try:
        _firm_formation_and_growth(state, dt)
        _bureaucratic_decay(state, dt)
        _organizational_death_and_rebirth(state, dt)
    except Exception:
        raise
