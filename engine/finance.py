"""Financial system dynamics — Minsky credit cycles, contagion, carry trade flows.

phi = liquidity / credit flow / capital in circulation
C   = counterparty risk / debt burden / regulatory friction
psi > 1.2 = credit expansion; psi < 0.8 = credit crunch; > 2.0 = bubble
"""
import numpy as np
from engine.physics import laplacian


def _credit_cycles(state, dt):
    # Minsky instability: expansion breeds hidden risk
    expanding = state.psi > 1.0
    if np.any(expanding):
        state.phi[expanding] += dt * 0.1 * state.phi[expanding] * state.psi[expanding]
        state.C[expanding] += dt * 0.05 * state.phi[expanding]
    # Contraction: credit destruction is fast and asymmetric
    contracting = state.C > state.phi * 1.1
    if np.any(contracting):
        state.phi[contracting] *= max(0.0, 1.0 - dt * 0.6)
        state.C[contracting] *= 1.0 + dt * 0.3
    state.phi = np.maximum(state.phi, 0.001)
    state.C = np.maximum(state.C, 0.05)


def _contagion(state, dt):
    crisis = state.psi < 0.4
    if not np.any(crisis):
        return
    crisis_phi = np.where(crisis, state.phi, 0.0)
    mean_crisis = float(np.mean(crisis_phi))
    # Flight to safety: phi drains from neighbors toward crisis cells
    drain = laplacian(crisis_phi) * 0.1
    state.phi -= dt * drain
    # Risk repricing spreads outward
    risk_spread = laplacian(np.where(crisis, state.C, 0.0)) * 0.05
    state.C += dt * np.maximum(risk_spread, 0.0)
    state.phi = np.maximum(state.phi, 0.001)


def _carry_trade_flows(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # High-yield destinations: high phi, low C
    high_yield = (state.phi > mean_phi * 1.3) & (state.C < mean_C * 0.8)
    # Safe haven: low phi, low C (low yield)
    safe_haven = (state.phi < mean_phi * 0.8) & (state.C < mean_C * 0.8)
    if np.any(high_yield) and np.any(safe_haven):
        # Capital flows toward high yield
        carry_flux = laplacian(np.where(high_yield, state.phi, 0.0)) * 0.03
        state.phi += dt * carry_flux
    # Carry unwind: when high-yield destination overloads
    unwind = high_yield & (state.psi > 1.5)
    if np.any(unwind):
        state.phi[unwind] -= dt * 0.4 * state.phi[unwind]
        state.C[unwind] += dt * 0.5
    state.phi = np.maximum(state.phi, 0.001)


def apply_finance(state, dt=0.01):
    try:
        _credit_cycles(state, dt)
        _contagion(state, dt)
        _carry_trade_flows(state, dt)
    except Exception:
        raise
