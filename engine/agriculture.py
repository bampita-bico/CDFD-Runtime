"""Agricultural dynamics — crop yields, famine thresholds, Green Revolution, monoculture risk.

phi = agricultural output flux / caloric production
C   = pest/disease pressure / water/soil deficit / market access friction
psi > 1.1 = surplus / export; psi ~ 1.0 = food secure; psi < 0.6 = famine threshold
"""
import numpy as np
from engine.physics import laplacian


def _crop_yield_cycles(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Productive land grows output (logistic bounded by C)
    growing = state.psi > 0.7
    cap = 3.0 / safe_C
    growth_rate = np.where(growing, 0.03 * (1.0 - state.phi / cap), 0.0)
    state.phi += dt * growth_rate * state.phi
    # Post-harvest: phi drops seasonally
    state.phi -= dt * 0.005 * state.phi
    state.phi = np.maximum(state.phi, 0.001)


def _famine_and_surplus(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Famine: phi < threshold, phi spirals down (seed corn eaten)
    famine = state.psi < 0.5
    if np.any(famine):
        state.phi[famine] -= dt * 0.1 * state.phi[famine]
        state.phi[famine] = np.maximum(state.phi[famine], 0.001)
        state.C[famine] += dt * 0.05  # social breakdown
    # Surplus: phi exported to low-phi regions (trade / food aid)
    surplus = state.psi > 1.3
    if np.any(surplus) and np.any(famine):
        export = laplacian(np.where(surplus, state.phi, 0.0)) * 0.03
        state.phi += dt * np.where(famine, np.maximum(export, 0.0), 0.0)


def _green_revolution_and_monoculture(state, dt):
    mean_C = float(np.mean(state.C))
    # Green Revolution: sudden C drop (new seed varieties, irrigation)
    # Modeled as persistent low-C cells with high phi producing instability
    monoculture = (state.phi > float(np.mean(state.phi)) * 1.5) & (state.C < mean_C * 0.5)
    if np.any(monoculture):
        # Vulnerability: one blight can collapse monoculture
        # C slowly creeps up (pest resistance builds)
        state.C[monoculture] += dt * 0.02
    # Blight event: if C spikes suddenly in monoculture zone
    blight = monoculture & (state.C > mean_C * 1.2)
    if np.any(blight):
        state.phi[blight] -= dt * 0.4 * state.phi[blight]
        state.phi[blight] = np.maximum(state.phi[blight], 0.001)


def apply_agriculture(state, dt=0.01):
    try:
        _crop_yield_cycles(state, dt)
        _famine_and_surplus(state, dt)
        _green_revolution_and_monoculture(state, dt)
    except Exception:
        raise
