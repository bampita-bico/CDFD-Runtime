"""Ocean dynamics — thermohaline circulation, upwelling, acidification, sea level.

phi = ocean current flux / heat transport / nutrient upwelling
C   = thermal stratification / salinity barrier / acidification level
psi > 1.2 = vigorous circulation; psi < 0.6 = circulation collapse (AMOC shutdown)
"""
import numpy as np
from engine.physics import laplacian


def _thermohaline_circulation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Deep water formation: high-C (dense/cold/salty) sinks, driving circulation
    dense = state.C > float(np.mean(state.C)) * 1.2
    state.phi[dense] += dt * 0.03 * state.C[dense]
    # Warm surface currents flow toward dense zones
    current = laplacian(state.phi) / safe_C
    state.phi += dt * 0.02 * current
    state.phi = np.maximum(state.phi, 0.0)


def _upwelling_productivity(state, dt):
    # Upwelling zones: where phi gradient diverges upward, nutrients surface
    grad_y, grad_x = np.gradient(state.phi)
    div = np.gradient(grad_x, axis=1)[1] if grad_x.ndim > 1 else np.zeros_like(grad_x)
    upwelling = (grad_y < -float(np.mean(np.abs(grad_y))) * 1.5)
    if np.any(upwelling):
        # Productivity boost: nutrient phi rises, C (stratification) lowers
        state.phi[upwelling] += dt * 0.05 * np.abs(grad_y[upwelling])
        state.C[upwelling] = np.maximum(state.C[upwelling] - dt * 0.02, 0.05)


def _ocean_acidification(state, dt):
    # CO2 absorption raises C (acidity = higher constraint on marine life phi)
    mean_phi = float(np.mean(state.phi))
    # High-phi (warm/active) zones absorb more CO2 initially
    state.C += dt * 0.003 * (state.phi / (mean_phi + 1e-9))
    # Acidification collapses carbonate phi (coral/shellfish)
    acid_collapse = state.C > float(np.mean(state.C)) * 1.8
    if np.any(acid_collapse):
        state.phi[acid_collapse] -= dt * 0.04 * state.phi[acid_collapse]
        state.phi[acid_collapse] = np.maximum(state.phi[acid_collapse], 0.001)


def apply_oceanography(state, dt=0.01):
    try:
        _thermohaline_circulation(state, dt)
        _upwelling_productivity(state, dt)
        _ocean_acidification(state, dt)
    except Exception:
        raise
