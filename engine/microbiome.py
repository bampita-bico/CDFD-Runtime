"""Microbiome dynamics — microbial community regulation, dysbiosis, horizontal gene transfer.

phi = microbial metabolic flux / community diversity
C   = pathogen exclusion / competitive resistance / colonization resistance
psi ~ 1.0 = healthy eubiosis; < 0.6 = dysbiosis; > 1.5 = bloom/overgrowth
"""
import numpy as np
from engine.physics import laplacian


def _community_regulation(state, dt):
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    mean_phi = float(np.mean(state.phi))
    # Stable microbiome: diverse communities maintain phi, build C resistance
    stable = (state.psi > 0.8) & (state.psi < 1.2)
    state.phi[stable] += dt * 0.01 * state.phi[stable]
    state.C[stable] += dt * 0.005
    # Diversity diffuses spatially
    state.phi += dt * 0.005 * laplacian(state.phi) / safe_C
    state.phi = np.maximum(state.phi, 0.001)


def _dysbiosis(state, dt):
    mean_C = float(np.mean(state.C))
    # Dysbiosis: low C (disrupted barrier) allows pathogen bloom
    disrupted = state.C < mean_C * 0.4
    if np.any(disrupted):
        state.phi[disrupted] += dt * 0.1 * state.phi[disrupted]  # pathogen bloom
        state.C[disrupted] = np.maximum(state.C[disrupted] - dt * 0.02, 0.01)
    # Recovery: phi diffuses in from healthy neighbors
    recovery_flux = laplacian(np.where(~disrupted, state.phi, 0.0)) * 0.01
    state.phi[disrupted] += dt * np.maximum(recovery_flux[disrupted], 0.0)


def _horizontal_gene_transfer(state, dt):
    # HGT: high-phi microbes transfer genetic information (phi) across C barriers
    mean_phi = float(np.mean(state.phi))
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    hgt_donors = state.phi > mean_phi * 1.5
    if np.any(hgt_donors):
        transfer = laplacian(np.where(hgt_donors, state.phi, 0.0)) * 0.02 / safe_C
        state.phi += dt * np.maximum(transfer, 0.0)
        # Antibiotic resistance: C rises in recipient communities (gene transfer = new resistance)
        recipients = (transfer > 0) & (~hgt_donors)
        state.C[recipients] += dt * 0.01
    state.phi = np.maximum(state.phi, 0.001)


def apply_microbiome(state, dt=0.01):
    try:
        _community_regulation(state, dt)
        _dysbiosis(state, dt)
        _horizontal_gene_transfer(state, dt)
    except Exception:
        raise
