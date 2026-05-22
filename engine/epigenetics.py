"""Epigenetics — heritable gene expression changes without sequence alteration.

phi = gene expression flux / transcriptional activity
C   = methylation/histone constraint / chromatin compaction
psi > 1.2 = hypomethylated / active; psi < 0.5 = silenced / heterochromatin
"""
import numpy as np
from engine.physics import laplacian


def _methylation_dynamics(state, dt):
    safe_phi = np.where(state.phi > 1e-9, state.phi, 1e-9)
    # Environmental stress (low phi) increases methylation
    stress_methylation = 0.003 * (1.0 / safe_phi) * state.C
    # Active transcription partially demethylates
    demethylation = 0.004 * state.phi * (1.0 - state.C)
    # Transgenerational inheritance drift
    drift = 0.001 * laplacian(state.C)
    state.C += dt * (stress_methylation - demethylation + drift)
    state.C = np.clip(state.C, 0.01, 2.0)


def _chromatin_remodeling(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Chromatin remodeling restores basal expression toward mean
    remodeling = 0.002 * (mean_phi - state.phi)
    state.phi += dt * remodeling
    state.phi = np.maximum(state.phi, 0.001)


def _gene_silencing(state, dt):
    # Silenced regions: high C blocks expression
    silenced = state.C > 1.5
    if np.any(silenced):
        state.phi[silenced] -= dt * 0.05 * state.phi[silenced]
        state.phi[silenced] = np.maximum(state.phi[silenced], 0.001)


def apply_epigenetics(state, dt=0.1):
    _methylation_dynamics(state, dt)
    _chromatin_remodeling(state, dt)
    _gene_silencing(state, dt)
