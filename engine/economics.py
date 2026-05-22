"""
Economics and Markets — Trade Networks, Capital Flow, and Market Cycles.
Applying the CDFT framework to macroeconomics.
"""
import numpy as np


def apply_economics(state, dt=0.01):
    try:
        _trade_networks(state, dt)
        _market_cycles(state, dt)
        _inequality_trap(state, dt)
        _comparative_advantage(state, dt)
        _rent_seeking(state, dt)
        _kondratieff_waves(state, dt)
    except Exception:
        raise


def _trade_networks(state, dt):
    """
    Models global trade routes and capital flow.
    Phi (J) = Capital / Goods Flux.
    Lambda (C) = Market friction (tariffs, transport costs, borders).
    """
    # Capital flows along paths of least resistance (low C)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)

    # Calculate capital flux gradient
    grad_phi_y, grad_phi_x = np.gradient(state.phi)

    # Trade flux is driven by wealth gradients but bottlenecked by friction
    trade_flux_x = grad_phi_x / safe_C
    trade_flux_y = grad_phi_y / safe_C

    trade_mag = np.sqrt(trade_flux_x**2 + trade_flux_y**2)

    # Trade hubs emerge where flux crosses intersecting low-friction regions
    hubs = trade_mag > float(np.mean(trade_mag)) * 1.5

    if np.any(hubs):
        # Wealth accumulation at hubs
        state.phi[hubs] += dt * 0.05 * trade_mag[hubs]
        # Trade actively erodes market friction (e.g., trade agreements, better ports)
        state.C[hubs] = np.maximum(state.C[hubs] - dt * 0.02 * trade_mag[hubs], 0.1)


def _market_cycles(state, dt):
    """
    Models economic booms, speculative bubbles, and market crashes.
    Psi = Market efficiency / Speculative Leverage.
    """
    # Speculative Boom: Phi (perceived value/capital) grows faster than actual economic capacity (C)
    boom_mask = (state.psi > 1.2) & (state.phi > float(np.mean(state.phi)))

    if np.any(boom_mask):
        # Irrational exuberance: capital attracts more capital
        state.phi[boom_mask] += dt * 0.15 * state.phi[boom_mask]

        # Systemic risk (C) accumulates invisibly in the background (debt, illiquidity)
        # This is the AFL alpha term in macroeconomics
        state.C[boom_mask] += dt * 0.08 * state.phi[boom_mask]

    # Market Crash (Minsky Moment):
    # When systemic risk (C) catches up and eclipses the inflated capital (Phi),
    # Psi collapses rapidly (liquidity crisis)
    crash_mask = (state.C > state.phi * 1.2) & (state.phi > 1.0)

    if np.any(crash_mask):
        # Massive wealth destruction (deleveraging)
        state.phi[crash_mask] *= (1.0 - dt * 0.8)
        # Market friction spikes (credit freeze, loss of trust)
        state.C[crash_mask] *= (1.0 + dt * 0.5)


def _inequality_trap(state, dt):
    """Piketty r > g: returns on capital exceed labor income growth, widening the gap."""
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Capital: high phi, low C — earns at rate r
    capital = (state.phi > mean_phi * 2.0) & (state.C < mean_C * 0.5)
    if np.any(capital):
        state.phi[capital] += dt * 0.08 * state.psi[capital] * state.phi[capital]
    # Labor: high C, low-to-mid phi — earns at rate g < r
    labor = state.C > mean_C
    if np.any(labor):
        state.phi[labor] += dt * 0.03 * state.phi[labor]
    # When inequality (std/mean) exceeds threshold, political friction rises
    gini_proxy = float(np.std(state.phi)) / (float(np.mean(state.phi)) + 1e-9)
    if gini_proxy > 2.0:
        state.C += dt * 0.02  # systemic political friction


def _comparative_advantage(state, dt):
    """Ricardo specialization: efficient producers attract phi, others specialize in imports."""
    mean_C = float(np.mean(state.C))
    specialist = state.C < mean_C * 0.6
    if not np.any(specialist):
        return
    from engine.physics import laplacian
    # Specialists attract phi from neighbors via gradient
    specialist_flux = laplacian(np.where(specialist, state.phi, 0.0)) * 0.03
    state.phi += dt * specialist_flux
    # Non-specialists lose some phi but gain efficiency (C reduction from trade)
    generalist = ~specialist
    state.phi[generalist] -= dt * 0.01 * state.phi[generalist]
    state.phi[generalist] = np.maximum(state.phi[generalist], 0.01)
    state.C[generalist] -= dt * 0.005  # efficiency gain from trade specialization
    state.C[generalist] = np.maximum(state.C[generalist], 0.05)


def _rent_seeking(state, dt):
    """Landlords, monopolists, toll collectors: stable high-psi cells extract rent."""
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    rent_seeker = (state.psi > 1.0) & (state.psi < 1.2) & (state.phi > mean_phi)
    if np.any(rent_seeker):
        state.C[rent_seeker] += dt * 0.02 * (state.phi[rent_seeker]**1.5) / (mean_phi + 1e-9)
    # Deadweight loss: high-C cells drain productive phi
    high_friction = state.C > mean_C
    if np.any(high_friction):
        state.phi[high_friction] -= dt * 0.01 * (state.C[high_friction] - mean_C)
        state.phi[high_friction] = np.maximum(state.phi[high_friction], 0.01)


def _kondratieff_waves(state, dt):
    """40-60 year economic supercycles: expansion, peak, contraction, trough."""
    if not hasattr(state, 'kondratieff_phase'):
        state.kondratieff_phase = 0.0
    state.kondratieff_phase += dt
    cycle_length = 50.0
    phase = (state.kondratieff_phase % cycle_length) / cycle_length
    if phase < 0.3:
        # Expansion: falling friction, rising output
        state.C *= (1.0 - dt * 0.002)
        state.phi += dt * 0.001 * state.phi
    elif phase < 0.5:
        # Peak: risk accumulates
        state.C += dt * 0.003 * state.phi / (float(np.mean(state.phi)) + 1e-9)
    elif phase < 0.75:
        # Contraction
        state.phi -= dt * 0.003 * state.phi
        state.phi = np.maximum(state.phi, 0.01)
    else:
        # Trough: C resets toward mean, innovation boost
        mean_C = float(np.mean(state.C))
        state.C -= dt * 0.002 * (state.C - mean_C)
        # Innovation seeds: low-C cells get a phi boost
        innovative = state.C < float(np.percentile(state.C, 25))
        if np.any(innovative):
            state.phi[innovative] += dt * 0.01 * state.phi[innovative]
