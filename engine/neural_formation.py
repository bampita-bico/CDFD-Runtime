"""Neural network formation dynamics — synaptogenesis, pruning, plasticity, criticality.

phi = neural activity flux / synaptic signal strength
C   = synaptic resistance / inhibitory tone / metabolic constraint
psi ~ 1.0 = critical state (edge of chaos); < 0.6 = hypoactive; > 1.5 = seizure/epilepsy
"""
import numpy as np
from engine.physics import laplacian


def _synaptogenesis(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Active regions grow new synapses: phi spreads, C drops (Hebbian learning)
    active = (state.phi > mean_phi) & (state.psi > 0.8) & (state.psi < 1.3)
    state.phi += dt * 0.03 * laplacian(state.phi) / safe_C
    if np.any(active):
        state.C[active] = np.maximum(state.C[active] - dt * 0.01 * state.phi[active] / (mean_phi + 1e-9), 0.05)
    state.phi = np.maximum(state.phi, 0.0)


def _synaptic_pruning(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Weak synapses pruned: low activity, high C removed
    weak = (state.phi < mean_phi * 0.3) & (state.C > float(np.mean(state.C)))
    if np.any(weak):
        state.phi[weak] -= dt * 0.05 * state.phi[weak]
        state.phi[weak] = np.maximum(state.phi[weak], 0.001)
        state.C[weak] += dt * 0.03  # pruning raises local resistance


def _criticality_and_seizure(state, dt):
    # Criticality: engine naturally operates near psi = 1 (edge of chaos)
    # Seizure: when phi cascades uncontrolled (psi > 1.6)
    if not hasattr(state, 'neural_refractory'):
        state.neural_refractory = np.zeros_like(state.phi)
    state.neural_refractory = np.maximum(state.neural_refractory - dt, 0.0)
    seizure = (state.psi > 1.6) & (state.neural_refractory < 0.01)
    if np.any(seizure):
        # Spreading depolarization
        state.phi += dt * 0.2 * laplacian(np.where(seizure, state.phi, 0.0))
        state.phi[seizure] -= dt * 0.4 * state.phi[seizure]
        state.C[seizure] += dt * 0.5  # postictal inhibition
        state.neural_refractory[seizure] = 2.0
    state.phi = np.maximum(state.phi, 0.0)


def apply_neural_formation(state, dt=0.01):
    try:
        _synaptogenesis(state, dt)
        _synaptic_pruning(state, dt)
        _criticality_and_seizure(state, dt)
    except Exception:
        raise
