"""Monetary policy dynamics — interest rates, QE, inflation, currency debasement.

phi = money supply / liquidity / purchasing power flux
C   = interest rate burden / inflation constraint / credit tightness
psi > 1.2 = inflationary / loose money; psi < 0.7 = deflationary / tight; psi ~ 1.0 = price stability
"""
import numpy as np
from engine.physics import laplacian


def _interest_rate_mechanism(state, dt):
    mean_psi = float(np.mean(state.psi))
    # Central bank reaction: tighten C when psi > 1.2 (inflation), loosen when psi < 0.8
    if mean_psi > 1.2:
        state.C += dt * 0.03 * (mean_psi - 1.0)  # rate hike
        state.phi -= dt * 0.01 * state.phi  # demand destruction
    elif mean_psi < 0.8:
        state.C -= dt * 0.02 * (1.0 - mean_psi)  # rate cut
        state.C = np.maximum(state.C, 0.01)
        state.phi += dt * 0.01 * state.phi  # stimulus
    state.phi = np.maximum(state.phi, 0.001)


def _quantitative_easing(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # QE: when C is very high and phi very low (deflationary spiral), inject phi
    deflationary_spiral = (state.C > mean_C * 1.8) & (state.phi < mean_phi * 0.5)
    if np.any(deflationary_spiral):
        state.phi[deflationary_spiral] += dt * 0.1 * mean_phi
        # Asset price inflation: QE raises phi in financial assets (low-C zones)
        financial = state.C < mean_C * 0.6
        state.phi[financial] += dt * 0.05 * state.phi[financial]


def _inflation_and_debasement(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Inflation: phi grows faster than C (real value erodes)
    inflationary = state.phi > mean_phi * 1.5
    if np.any(inflationary):
        # Real purchasing power erodes: C rises (cost of goods)
        state.C[inflationary] += dt * 0.04 * (state.phi[inflationary] / (mean_phi + 1e-9))
    # Hyperinflation threshold: phi >> C causes C to spike exponentially
    hyper = state.psi > 3.0
    if np.any(hyper):
        state.C[hyper] *= 1.0 + dt * 0.5
        state.phi[hyper] *= 1.0 + dt * 0.3  # nominal values spiral


def apply_monetary_policy(state, dt=0.01):
    try:
        _interest_rate_mechanism(state, dt)
        _quantitative_easing(state, dt)
        _inflation_and_debasement(state, dt)
    except Exception:
        raise
