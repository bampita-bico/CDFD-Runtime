"""Ecological Systems — Trophic cascades and ecosystem stability."""
import numpy as np


def apply_ecology(state, dt=0.01):
    try:
        _trophic_cascade(state, dt)
    except Exception:
        raise


def _trophic_cascade(state, dt):
    """
    Paper 13: Ecological Systems as Flux-Constrained Networks.
    Ecosystems balance biomass flux (Phi) against carrying capacity constraints (C).
    """
    # Ecosystems are characterized by distinct flux regimes (trophic levels)
    mean_flux = float(np.mean(state.phi))

    # Identify high flux regions (e.g., Primary Producers)
    producers = state.phi > mean_flux * 1.5

    # Identify low constraint regions (e.g., Top Predators controlling the system)
    # Predators act as a top-down constraint on herbivore flux
    predators = (state.C < float(np.mean(state.C)) * 0.8) & (state.phi > mean_flux)

    if np.any(producers):
        # Primary production bounded by carrying capacity
        safe_C = np.where(state.C[producers] > 1e-9, state.C[producers], 1e-9)
        # Logistic-style growth bounded by AFL constraint
        growth = 0.1 * state.phi[producers] * (1.0 - (state.phi[producers] / (10.0 / safe_C)))
        state.phi[producers] = np.maximum(state.phi[producers] + dt * growth, 0.0)

    if np.any(predators):
        # Predators impose constraint on neighboring producers/herbivores (top-down control)
        # Simulating predation by bleeding flux from neighbors
        grad_y, grad_x = np.gradient(state.phi)
        # Flux flows toward predators (consumption)
        state.phi[predators] += dt * 0.05 * np.sqrt(grad_x[predators]**2 + grad_y[predators]**2)

        # AFL: The presence of predators reinforces the ecosystem constraint barrier
        state.C[predators] += dt * 0.01
