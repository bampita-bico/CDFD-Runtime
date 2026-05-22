"""Resource depletion dynamics — fisheries collapse, deforestation, peak extraction, no-recovery.

phi = extractable resource flux / harvest rate
C   = depletion burden / regeneration deficit / ecological debt
psi > 1.0 = unsustainable extraction; psi < 0.8 = managed; psi near 0 = collapse / extinction
"""
import numpy as np
from engine.physics import laplacian


def _extraction_and_regeneration(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Regeneration: resources recover at rate bounded by C
    recovering = state.phi < mean_phi
    state.phi[recovering] += dt * 0.03 * state.phi[recovering] * (1.0 - state.phi[recovering] / (mean_phi * 2.0 + 1e-9))
    # Extraction: C accumulates with each unit extracted
    extracted = state.phi > mean_phi
    state.C[extracted] += dt * 0.02 * state.phi[extracted] / (mean_phi + 1e-9)
    state.phi = np.maximum(state.phi, 0.001)


def _fisheries_collapse(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Overfishing: beyond MSY, population enters collapse spiral
    overfished = (state.psi > 1.3) & (state.phi > mean_phi * 0.5)
    if np.any(overfished):
        state.phi[overfished] -= dt * 0.1 * state.phi[overfished]
        state.phi[overfished] = np.maximum(state.phi[overfished], 0.001)
    # Collapse: below critical threshold, recovery impossible without phi injection
    collapsed = state.phi < mean_phi * 0.1
    if np.any(collapsed):
        state.phi[collapsed] -= dt * 0.05 * state.phi[collapsed]
        state.phi[collapsed] = np.maximum(state.phi[collapsed], 0.0001)
        state.C[collapsed] += dt * 0.1  # trophic cascade raises constraint


def _peak_and_no_recovery(state, dt):
    if not hasattr(state, 'depletion_accumulator'):
        state.depletion_accumulator = np.zeros_like(state.phi)
    mean_C = float(np.mean(state.C))
    # Track cumulative extraction burden
    state.depletion_accumulator += dt * state.C
    # Permanent depletion: once C integral exceeds threshold, phi cannot recover
    permanently_depleted = state.depletion_accumulator > 15.0
    if np.any(permanently_depleted):
        recovery_block = laplacian(state.phi) * 0.01
        state.phi[permanently_depleted] -= dt * np.abs(recovery_block[permanently_depleted]) * 0.5
        state.phi[permanently_depleted] = np.maximum(state.phi[permanently_depleted], 0.0001)


def apply_resource_depletion(state, dt=0.01):
    try:
        _extraction_and_regeneration(state, dt)
        _fisheries_collapse(state, dt)
        _peak_and_no_recovery(state, dt)
    except Exception:
        raise
