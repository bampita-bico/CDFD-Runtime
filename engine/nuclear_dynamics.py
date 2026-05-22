"""Nuclear dynamics — fission chain reactions, criticality, decay chains, proliferation.

phi = neutron flux / fission rate / radioactive decay energy
C   = neutron absorption / control rod / moderator resistance
psi > 1.0 = supercritical (chain reaction); psi = 1.0 = critical; psi < 1.0 = subcritical
"""
import numpy as np
from engine.physics import laplacian


def _criticality_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Neutron multiplication: phi grows supercritically when psi > 1
    supercritical = state.psi > 1.0
    if np.any(supercritical):
        k_eff = state.psi[supercritical] - 1.0
        state.phi[supercritical] += dt * 0.5 * k_eff * state.phi[supercritical]
    # Subcritical: phi decays (neutrons absorbed)
    subcritical = state.psi < 1.0
    state.phi[subcritical] -= dt * 0.1 * state.phi[subcritical]
    state.phi = np.maximum(state.phi, 0.0)
    # Neutron diffusion
    state.phi += dt * 0.02 * laplacian(state.phi) / safe_C


def _decay_and_transmutation(state, dt):
    # Radioactive decay: phi decreases, C shifts (daughter products)
    mean_phi = float(np.mean(state.phi))
    decaying = state.phi > mean_phi
    state.phi[decaying] -= dt * 0.01 * state.phi[decaying]
    # Decay heat: daughter products raise local C (activation products)
    state.C += dt * 0.002 * state.phi / (mean_phi + 1e-9)
    state.phi = np.maximum(state.phi, 0.0)


def _proliferation_dynamics(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Proliferation: high-phi, low-C zones attempt to build critical mass
    proliferating = (state.phi > mean_phi * 1.5) & (state.C < mean_C * 0.6)
    if np.any(proliferating):
        state.phi[proliferating] += dt * 0.03 * state.phi[proliferating]
        state.C[proliferating] = np.maximum(state.C[proliferating] - dt * 0.01, 0.01)
    # Nonproliferation: high C barriers prevent critical mass
    blocked = state.C > mean_C * 2.0
    state.phi[blocked] -= dt * 0.05 * state.phi[blocked]
    state.phi[blocked] = np.maximum(state.phi[blocked], 0.001)


def apply_nuclear_dynamics(state, dt=0.01):
    try:
        _criticality_dynamics(state, dt)
        _decay_and_transmutation(state, dt)
        _proliferation_dynamics(state, dt)
    except Exception:
        raise
