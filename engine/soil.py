"""Soil dynamics — fertility cycles, erosion, salinization, dust bowl collapse.

phi = soil organic matter / nutrient flux / microbial activity
C   = erosion burden / compaction / salt/toxin accumulation
psi ~ 1.0 = productive soil; psi < 0.6 = degraded land; psi > 1.3 = over-fertile runoff
"""
import numpy as np
from engine.physics import laplacian


def _fertility_cycles(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Organic matter builds in vegetated, stable areas
    productive = (state.psi > 0.8) & (state.psi < 1.3)
    state.phi[productive] += dt * 0.02 * state.phi[productive]
    # Decomposition releases nutrients (laplacian diffusion of phi)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    state.phi += dt * 0.01 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.0)


def _erosion_and_degradation(state, dt):
    mean_phi = float(np.mean(state.phi))
    # Bare/depleted cells erode: phi loss, C rises (compaction, exposed subsoil)
    bare = state.phi < mean_phi * 0.4
    if np.any(bare):
        state.phi[bare] -= dt * 0.03 * state.phi[bare]
        state.phi[bare] = np.maximum(state.phi[bare], 0.001)
        state.C[bare] += dt * 0.04
    # Wind/water erosion propagates: high phi-gradient areas lose topsoil
    grad_y, grad_x = np.gradient(state.phi)
    erosion_front = np.sqrt(grad_x**2 + grad_y**2) > float(np.mean(np.sqrt(grad_x**2 + grad_y**2))) * 2.0
    state.C[erosion_front] += dt * 0.02


def _salinization(state, dt):
    # Irrigation without drainage: C accumulates as salt
    mean_phi = float(np.mean(state.phi))
    irrigated_overuse = (state.phi > mean_phi * 1.5) & (state.psi > 1.2)
    if np.any(irrigated_overuse):
        state.C[irrigated_overuse] += dt * 0.03 * state.phi[irrigated_overuse] / (mean_phi + 1e-9)
    # Saline threshold: land becomes unusable
    salt_dead = state.C > float(np.mean(state.C)) * 2.5
    if np.any(salt_dead):
        state.phi[salt_dead] *= max(0.0, 1.0 - dt * 0.1)
        state.phi[salt_dead] = np.maximum(state.phi[salt_dead], 0.001)


def apply_soil(state, dt=0.01):
    try:
        _fertility_cycles(state, dt)
        _erosion_and_degradation(state, dt)
        _salinization(state, dt)
    except Exception:
        raise
