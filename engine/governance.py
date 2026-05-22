"""Governance and state dynamics — state building, corruption, legitimacy crises.

phi = state capacity / administrative throughput / public service delivery
C   = bureaucratic friction / corruption / institutional inertia
psi ~ 1.0 = functional state; < 0.8 = failed state; > 1.2 = authoritarian overreach
"""
import numpy as np
from engine.physics import laplacian


def _state_building(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    cores = (state.psi > 1.0) & (state.phi > mean_phi)
    if not np.any(cores):
        return
    core_phi = np.where(cores, state.phi, 0.0)
    expansion = laplacian(core_phi) * 0.02 / safe_C
    state.phi += dt * np.maximum(expansion, 0.0)
    # Standardization reduces friction in newly reached periphery
    reached = expansion > float(np.mean(np.abs(expansion)))
    state.C[reached] = np.maximum(state.C[reached] - dt * 0.01, 0.05)


def _corruption_dynamics(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Rent-seeking accumulates C proportional to phi^2
    state.C += dt * 0.01 * (state.phi**2) / (mean_phi + 1e-9)
    # Revenue collapse: when C far exceeds phi, tax base evaporates
    corrupt_collapse = state.C > state.phi * 2.0
    if np.any(corrupt_collapse):
        state.phi[corrupt_collapse] -= dt * 0.15 * state.phi[corrupt_collapse]
        state.phi[corrupt_collapse] = np.maximum(state.phi[corrupt_collapse], 0.01)


def _legitimacy_crisis(state, dt):
    if not hasattr(state, 'gov_stress'):
        state.gov_stress = np.zeros_like(state.phi)
    if not hasattr(state, 'gov_recovery'):
        state.gov_recovery = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    # Accumulate stress when psi is very low
    failing = state.psi < 0.6
    state.gov_stress[failing] += dt
    state.gov_stress[~failing] = np.maximum(state.gov_stress[~failing] - dt * 0.3, 0.0)
    # Dissolution when stress sustained
    dissolving = state.gov_stress > 4.0
    if np.any(dissolving):
        state.phi[dissolving] *= max(0.0, 1.0 - dt * 0.3)
        state.C[dissolving] += dt * 1.0
    # Recovery tracking
    stabilizing = state.phi > mean_phi * 0.3
    state.gov_recovery[stabilizing] += dt
    state.gov_recovery[~stabilizing] = 0.0
    rebuilding = state.gov_recovery > 3.0
    if np.any(rebuilding):
        rebuild_diff = laplacian(state.C)
        state.C[rebuilding] -= dt * 0.05 * np.abs(rebuild_diff[rebuilding])
        state.C[rebuilding] = np.maximum(state.C[rebuilding], 0.05)


def apply_governance(state, dt=0.01):
    try:
        _state_building(state, dt)
        _corruption_dynamics(state, dt)
        _legitimacy_crisis(state, dt)
    except Exception:
        raise
