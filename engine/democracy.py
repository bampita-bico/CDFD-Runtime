"""Democratic dynamics — legitimacy cycles, electoral thresholds, backsliding, polarization.

phi = civic participation flux / political voice / institutional trust
C   = authoritarian capture / veto power / electoral manipulation burden
psi > 1.1 = democratic deepening; psi ~ 1.0 = stable democracy; psi < 0.6 = autocratic capture
"""
import numpy as np
from engine.physics import laplacian


def _legitimacy_and_participation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # High-phi, low-C: civic trust grows, participation rises
    thriving = (state.psi > 1.0) & (state.phi > mean_phi)
    state.phi[thriving] += dt * 0.02 * state.phi[thriving]
    state.C[thriving] = np.maximum(state.C[thriving] - dt * 0.01, 0.05)
    # Civic spread: democratic norms diffuse spatially
    state.phi += dt * 0.01 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _democratic_backsliding(state, dt):
    if not hasattr(state, 'backslide_stress'):
        state.backslide_stress = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    # Backsliding: elites capture institutions when phi drops
    at_risk = state.phi < mean_phi * 0.6
    state.backslide_stress[at_risk] += dt
    state.backslide_stress[~at_risk] = np.maximum(state.backslide_stress[~at_risk] - dt * 0.3, 0.0)
    captured = state.backslide_stress > 3.0
    if np.any(captured):
        state.C[captured] += dt * 0.2  # institutional capture
        state.phi[captured] -= dt * 0.05 * state.phi[captured]
        state.phi[captured] = np.maximum(state.phi[captured], 0.01)


def _polarization(state, dt):
    # Polarization: steep phi gradients harden C (partisan barriers)
    grad_y, grad_x = np.gradient(state.phi)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    mean_grad = float(np.mean(grad_mag))
    polarized = grad_mag > mean_grad * 2.0
    state.C[polarized] += dt * 0.03 * grad_mag[polarized]
    # Depolarization: moderate zones slowly reduce C
    moderate = (state.psi > 0.8) & (state.psi < 1.2) & (grad_mag < mean_grad * 0.5)
    state.C[moderate] = np.maximum(state.C[moderate] - dt * 0.005, 0.05)


def apply_democracy(state, dt=0.01):
    try:
        _legitimacy_and_participation(state, dt)
        _democratic_backsliding(state, dt)
        _polarization(state, dt)
    except Exception:
        raise
