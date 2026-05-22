"""Adaptive change — replication, error dynamics, variation, selection (Darwinian Evolution)."""
import numpy as np


def apply_evolution(state, dt=0.01):
    try:
        _template_replication(state, dt)
        _error_dynamics(state, dt)
        _darwinian_selection(state, dt)
    except Exception:
        raise


def _template_replication(state, dt):
    """
    Paper 8: Flux-Constrained Replication.
    Replication (copying of Constraint patterns) is driven by local energy flux.
    If the flux provides enough energy to overcome degradation, the pattern spreads.
    """
    # Calculate local energy flux magnitude (J)
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    flux_mag = np.sqrt((grad_phi_x / safe_C)**2 + (grad_phi_y / safe_C)**2)

    # Replication threshold: Gamma_rep > 1
    degradation_rate = 0.01 / safe_C
    replication_rate = 0.05 * flux_mag

    growth_mask = replication_rate > degradation_rate

    # Replicating constraints (information) spreads to neighboring regions
    # Simulating spatial replication fronts using a simple convolution-like spread
    C_spread = (np.roll(state.C, 1, axis=0) + np.roll(state.C, -1, axis=0) +
                np.roll(state.C, 1, axis=1) + np.roll(state.C, -1, axis=1)) / 4.0

    state.C[growth_mask] = state.C[growth_mask] * (1 - dt) + C_spread[growth_mask] * dt


def _error_dynamics(state, dt):
    """
    Paper 8: Error Threshold and Variation.
    Fidelity depends on energy flux. Low flux leads to high mutation (noise),
    while high flux allows high-fidelity replication.
    """
    # Flux drives fidelity:
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_mag = np.sqrt(grad_phi_x**2 + grad_phi_y**2)

    mean_flux = float(np.mean(flux_mag)) + 1e-9
    normalized_flux = flux_mag / mean_flux

    # Error rate is inversely proportional to normalized flux
    # Base error noise scale is 0.005
    error_rate = 0.005 / (1.0 + normalized_flux)

    # Apply mutation (noise) to the constraints
    mutations = np.random.normal(0, error_rate, state.C.shape)
    state.C += dt * mutations * state.C  # Multiplicative noise


def _darwinian_selection(state, dt):
    """
    Paper 8: Emergence of Evolution and Fitness Landscapes.
    Systems that maintain Equilibrium (Psi ~ 1.0) survive.
    Those that fall out of equilibrium (Overload or Collapse) are selected against.
    """
    # Fitness is highest near the balanced Psi regime.
    fitness = 1.0 / (1.0 + np.abs(state.psi - 1.0))

    # High fitness regions draw resources (Phi) from low fitness regions
    mean_fitness = float(np.mean(fitness))

    strong_mask = fitness > mean_fitness * 1.2
    weak_mask = fitness < mean_fitness * 0.8

    # Transfer flow from weak to strong (Competition)
    transfer = dt * 0.01 * state.phi[weak_mask]
    state.phi[weak_mask] -= transfer

    # Distribute the transferred resources to the strong replicators
    if np.any(strong_mask) and np.any(weak_mask):
        bonus_per_cell = np.sum(transfer) / np.sum(strong_mask)
        state.phi[strong_mask] += bonus_per_cell
