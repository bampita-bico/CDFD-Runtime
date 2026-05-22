"""Science and knowledge dynamics — paradigm accumulation, Kuhnian revolution, peer review.

phi = knowledge production flux / research output / citation flow
C   = paradigm rigidity / peer review barrier / funding gatekeeping
psi > 1.2 = paradigm shift imminent; psi ~ 1.0 = normal science; psi < 0.7 = stagnation
"""
import numpy as np
from engine.physics import laplacian


def _normal_science(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Knowledge accumulates: phi diffuses and grows within established paradigm
    state.phi += dt * 0.02 * laplacian(state.phi) / safe_C
    state.phi += dt * 0.01 * state.phi  # incremental progress
    state.phi = np.maximum(state.phi, 0.001)
    # Paradigm calcification: C rises as consensus hardens
    mean_phi = float(np.mean(state.phi))
    established = state.phi > mean_phi * 1.2
    state.C[established] += dt * 0.005


def _anomaly_accumulation(state, dt):
    if not hasattr(state, 'anomaly_count'):
        state.anomaly_count = np.zeros_like(state.phi)
    mean_C = float(np.mean(state.C))
    # Anomalies build where phi is blocked by C (results that don't fit paradigm)
    blocked = (state.psi < 0.8) & (state.C > mean_C)
    state.anomaly_count[blocked] += dt
    state.anomaly_count[~blocked] = np.maximum(state.anomaly_count[~blocked] - dt * 0.1, 0.0)


def _paradigm_revolution(state, dt):
    if not hasattr(state, 'anomaly_count'):
        state.anomaly_count = np.zeros_like(state.phi)
    # Revolution: when anomaly count exceeds threshold, C collapses (paradigm shift)
    revolutionary = state.anomaly_count > 5.0
    if np.any(revolutionary):
        state.C[revolutionary] *= max(0.0, 1.0 - dt * 0.5)
        state.C[revolutionary] = np.maximum(state.C[revolutionary], 0.05)
        state.phi[revolutionary] += dt * 0.2 * state.phi[revolutionary]
        state.anomaly_count[revolutionary] = 0.0
        # New paradigm diffuses outward
        state.phi += dt * 0.05 * laplacian(np.where(revolutionary, state.phi, 0.0))
    state.phi = np.maximum(state.phi, 0.001)


def apply_science_paradigms(state, dt=0.01):
    try:
        _normal_science(state, dt)
        _anomaly_accumulation(state, dt)
        _paradigm_revolution(state, dt)
    except Exception:
        raise
