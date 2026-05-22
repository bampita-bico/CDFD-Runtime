"""Labor market dynamics — wage dynamics, unemployment, strikes, automation displacement.

phi = labor productivity flux / employed worker output
C   = structural unemployment / wage rigidity / skill mismatch
psi > 1.1 = tight labor market (wages rising); psi < 0.7 = slack / mass unemployment
"""
import numpy as np
from engine.physics import laplacian


def _wage_dynamics(state, dt):
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Tight labor (psi > 1.1): wages bid up, phi grows, C drops (barriers fall)
    tight = state.psi > 1.1
    state.phi[tight] += dt * 0.04 * state.phi[tight]
    state.C[tight] = np.maximum(state.C[tight] - dt * 0.01, 0.05)
    # Slack labor (psi < 0.7): wages suppressed, phi drifts down
    slack = state.psi < 0.7
    state.phi[slack] -= dt * 0.02 * state.phi[slack]
    state.phi[slack] = np.maximum(state.phi[slack], 0.01)
    # Spatial labor mobility: phi diffuses from low-wage to high-wage regions
    state.phi += dt * 0.01 * laplacian(state.phi) / safe_C


def _strike_waves(state, dt):
    if not hasattr(state, 'labor_grievance'):
        state.labor_grievance = np.zeros_like(state.phi)
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Grievance builds when wages fall relative to productivity
    exploited = (state.phi < mean_phi) & (state.C > mean_C)
    state.labor_grievance[exploited] += dt
    state.labor_grievance[~exploited] = np.maximum(state.labor_grievance[~exploited] - dt * 0.3, 0.0)
    # Strike threshold: collective action raises C (friction for employer) and phi (wages won)
    striking = state.labor_grievance > 3.0
    if np.any(striking):
        state.C[striking] += dt * 0.3  # strike cost to production
        state.phi[striking] += dt * 0.05 * state.phi[striking]  # wage gains
        state.labor_grievance[striking] = 0.0


def _automation_displacement(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Automation frontier: low-C, high-phi regions displace routine labor
    automating = (state.C < mean_C * 0.5) & (state.phi > mean_phi * 1.5)
    if np.any(automating):
        # Routine labor phi drops (jobs disappear)
        state.phi[automating] -= dt * 0.06 * state.phi[automating]
        state.phi[automating] = np.maximum(state.phi[automating], 0.01)
        # C rises in displaced regions (structural unemployment)
        state.C[automating] += dt * 0.04


def apply_labor_markets(state, dt=0.01):
    try:
        _wage_dynamics(state, dt)
        _strike_waves(state, dt)
        _automation_displacement(state, dt)
    except Exception:
        raise
