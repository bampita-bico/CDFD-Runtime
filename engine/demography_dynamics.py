"""Demographic dynamics — birth/death rates, age structure, demographic dividend, migration.

phi = population vitality flux / reproductive output
C   = mortality burden / dependency ratio / resource constraint per capita
psi > 1.1 = demographic boom; psi ~ 1.0 = replacement; psi < 0.7 = demographic collapse
"""
import numpy as np
from engine.physics import laplacian


def _birth_death_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # High-phi, low-C regions: demographic boom (high birth, low mortality)
    boom = (state.phi > mean_phi) & (state.C < float(np.mean(state.C)))
    state.phi[boom] += dt * 0.03 * state.phi[boom]
    # Low-phi, high-C: demographic decline (aging, emigration)
    decline = (state.phi < mean_phi * 0.7) & (state.C > float(np.mean(state.C)))
    state.phi[decline] -= dt * 0.02 * state.phi[decline]
    state.phi[decline] = np.maximum(state.phi[decline], 0.001)
    # Malthusian check: C rises when phi exceeds carrying capacity
    overpop = state.phi > safe_C * 2.0
    state.C[overpop] += dt * 0.04 * (state.phi[overpop] / (safe_C[overpop]))


def _demographic_dividend(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Dividend window: medium-phi, falling C (working-age bulge)
    dividend = (state.phi > mean_phi * 0.8) & (state.phi < mean_phi * 1.5) & (state.C < mean_C)
    if np.any(dividend):
        # Economic phi bonus from large working-age cohort
        state.phi[dividend] += dt * 0.02 * state.phi[dividend]
        state.C[dividend] = np.maximum(state.C[dividend] - dt * 0.01, 0.05)
    # Aging: after dividend, C rises (pension/healthcare burden)
    aging = (state.phi < mean_phi * 0.8) & (state.C < mean_C)
    state.C[aging] += dt * 0.015


def _migration_pressure(state, dt):
    # Population migrates from high-C to low-C regions
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    grad_C_y, grad_C_x = np.gradient(state.C)
    # Migration flux away from high C
    mig_x = -grad_C_x * state.phi / safe_C
    mig_y = -grad_C_y * state.phi / safe_C
    _, div_x = np.gradient(mig_x)
    div_y, _ = np.gradient(mig_y)
    state.phi += dt * 0.05 * (div_x + div_y)
    state.phi = np.maximum(state.phi, 0.001)


def apply_demography_dynamics(state, dt=0.01):
    try:
        _birth_death_dynamics(state, dt)
        _demographic_dividend(state, dt)
        _migration_pressure(state, dt)
    except Exception:
        raise
