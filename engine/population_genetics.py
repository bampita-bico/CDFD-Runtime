"""Population genetics dynamics — gene flow, natural selection, genetic drift and bottlenecks.

phi = allele frequency / genetic diversity flow
C   = reproductive barrier / selection pressure / genetic drift strength
psi ~ 1.0 = neutral drift; > 1.2 = positive selection sweep; < 0.8 = purifying selection
"""
import numpy as np
from engine.physics import laplacian


def _gene_flow(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Allele frequencies diffuse across population boundaries
    state.phi += dt * 0.03 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.0)


def _natural_selection(state, dt):
    # Positive selection: beneficial allele spreads when psi > 1.1
    positive = state.psi > 1.1
    if np.any(positive):
        state.phi[positive] += dt * 0.06 * (state.psi[positive] - 1.0) * state.phi[positive]
    # Purifying selection: deleterious alleles reduced when psi < 0.9
    purifying = state.psi < 0.9
    if np.any(purifying):
        state.phi[purifying] -= dt * 0.04 * (1.0 - state.psi[purifying]) * state.phi[purifying]
        state.phi[purifying] = np.maximum(state.phi[purifying], 0.001)


def _genetic_drift_and_bottleneck(state, dt):
    mean_phi = float(np.mean(state.phi))
    mean_C = float(np.mean(state.C))
    # Small populations: stochastic drift scales with inverse population size
    small_pop = state.phi < mean_phi * 0.2
    if np.any(small_pop):
        noise_scale = 0.05 * (mean_phi / (state.phi[small_pop] + 1e-9))
        noise = np.random.normal(0.0, 1.0, state.phi[small_pop].shape)
        state.phi[small_pop] *= np.clip(1.0 + noise * noise_scale, 0.01, 5.0)
    # Bottleneck: sudden C spike > 3*mean collapses phi (founder effect)
    bottleneck = state.C > mean_C * 3.0
    if np.any(bottleneck):
        state.phi[bottleneck] *= max(0.0, 1.0 - dt * 0.5)
        state.phi[bottleneck] = np.maximum(state.phi[bottleneck], 0.001)
        # Slow recovery from neighboring populations
        recovery = laplacian(state.phi) * 0.005
        state.phi[bottleneck] += dt * np.abs(recovery[bottleneck])


def apply_population_genetics(state, dt=0.01):
    try:
        _gene_flow(state, dt)
        _natural_selection(state, dt)
        _genetic_drift_and_bottleneck(state, dt)
    except Exception:
        raise
