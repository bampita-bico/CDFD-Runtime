"""Galaxy dynamics — spiral arm flows, dark matter halo, galactic center accretion, mergers.

phi = stellar/gas mass flux / star formation rate
C   = dark matter potential / galactic friction / tidal disruption
psi > 1.2 = starburst; psi ~ 1.0 = stable spiral; psi < 0.5 = quiescent / quenched
"""
import numpy as np
from engine.physics import laplacian


def _spiral_arm_dynamics(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Density waves: phi flows into spiral arms (density wave compression)
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    arm_flux = np.sqrt(grad_phi_x**2 + grad_phi_y**2) / safe_C
    arm_region = arm_flux > float(np.mean(arm_flux)) * 1.5
    if np.any(arm_region):
        state.phi[arm_region] += dt * 0.02 * arm_flux[arm_region]
        state.C[arm_region] -= dt * 0.005  # compression triggers star formation
    state.C = np.maximum(state.C, 0.05)
    state.phi = np.maximum(state.phi, 0.001)


def _dark_matter_halo(state, dt):
    # Dark matter: background C field that provides gravitational scaffolding
    # Modeled as slow C diffusion keeping phi from dispersing
    mean_C = float(np.mean(state.C))
    mean_phi = float(np.mean(state.phi))
    # DM halo maintains C floor: prevents phi from fully escaping
    state.C += dt * 0.002 * laplacian(state.C)
    # Galaxy-scale phi retained by DM gravity
    escaping = state.phi < mean_phi * 0.3
    state.phi[escaping] += dt * 0.01 * mean_phi * (state.C[escaping] / (mean_C + 1e-9))


def _galactic_center_accretion(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Central black hole: highest phi zone accretes material from surroundings
    center = state.phi > mean_phi * 2.5
    if np.any(center):
        # Accretion disk: phi drains from neighbors into center
        drain = laplacian(np.where(center, -1.0, 0.0).astype(float)) * 0.01
        state.phi += dt * np.where(~center, drain * state.phi, 0.0)
        state.phi[center] += dt * 0.03 * state.phi[center]
        # AGN feedback: central energy jets raise C in surroundings
        state.C += dt * 0.005 * np.where(center, state.phi / (mean_phi + 1e-9), 0.0)
    state.phi = np.maximum(state.phi, 0.001)


def apply_galaxy_dynamics(state, dt=0.01):
    try:
        _spiral_arm_dynamics(state, dt)
        _dark_matter_halo(state, dt)
        _galactic_center_accretion(state, dt)
    except Exception:
        raise
