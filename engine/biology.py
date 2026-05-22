"""Living systems as flow vortices — metabolism, bioelectrics, immunology, morphogenesis."""
import numpy as np

from engine.origins_of_life import (
    compute_life_number,
    compute_life_number_from_cached_channels,
    tri_regime_throughput_grid,
    update_tri_regime_channels,
)


def _stabilize_biology_fields(state):
    """Keep biological toy updates finite under stress-test parameter sweeps."""
    state.phi = np.nan_to_num(state.phi, nan=0.0, posinf=25.0, neginf=0.0)
    state.C = np.nan_to_num(state.C, nan=1.0, posinf=25.0, neginf=0.05)
    state.S = np.nan_to_num(state.S, nan=1.0, posinf=5.0, neginf=0.05)
    state.Ms = np.nan_to_num(state.Ms, nan=1.0, posinf=5.0, neginf=1.0)
    state.phi = np.clip(state.phi, 0.0, 25.0)
    state.C = np.clip(state.C, 0.05, 25.0)
    state.S = np.clip(state.S, 0.05, 5.0)
    state.Ms = np.clip(state.Ms, 1.0, 5.0)


def apply_biology(state, dt=0.01):
    try:
        _stabilize_biology_fields(state)
        _autocatalytic_closure(state, dt)
        _stabilize_biology_fields(state)
        _metabolic_regulation(state, dt)
        _stabilize_biology_fields(state)
        state.update_psi()
        _bioelectrics(state, dt)
        _stabilize_biology_fields(state)
        _immunology(state, dt)
        _stabilize_biology_fields(state)
        _morphogenesis(state, dt)
        _stabilize_biology_fields(state)
        _tri_regime_bioenergetics(state, dt)
        _stabilize_biology_fields(state)
        state.update_psi()
    except Exception:
        raise


def _autocatalytic_closure(state, dt):
    """
    Paper 6: Autocatalytic Networks and Metabolic Closure.
    Production is proportional to Phi^2, loss is proportional to 1/C.
    """
    production = 0.05 * (state.phi ** 2)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    diffusive_loss = 0.02 / safe_C

    closure_mask = production > diffusive_loss
    state.phi[closure_mask] += dt * (production[closure_mask] - diffusive_loss[closure_mask])
    state.C[closure_mask] += dt * 0.01 * state.C[closure_mask]


def _metabolic_regulation(state, dt):
    """
    Paper 1 & 4: AFL Metabolic Regulation (Insulin Resistance).
    High nutrient flux (Phi) causes mitochondrial constraint (C) to adapt upward.
    """
    # Simulate an external metabolic drive proportional to global Phi
    mean_flux = float(np.mean(state.phi))
    nutrient_load = np.where(state.phi > mean_flux * 1.5, state.phi, 0.0)

    # AFL constraint response to nutrient overload (preventing mitochondrial burnout)
    overload_mask = nutrient_load > 0
    if np.any(overload_mask):
        state.C[overload_mask] += dt * 0.07 * np.abs(nutrient_load[overload_mask])


def _bioelectrics(state, dt):
    """
    Paper 10: Bioelectric Regulation.
    Membrane potential acts as constraint. Action potentials are transient Psi spikes.
    """
    # Depolarization (Psi > 1.5) triggers an action potential (massive flux spike)
    ap_mask = state.psi_s > 1.5
    if np.any(ap_mask):
        # Spike flux
        state.phi[ap_mask] += dt * 5.0
        # Repolarization: K+ channels open, sharply increasing C to restore Psi
        state.C[ap_mask] += dt * 2.0


def _immunology(state, dt):
    """
    Paper 8: Immunology as System-Wide Constraint Amplification.
    Inflammation acts as a global regulator that alters flux capacity.
    """
    # Inflammation triggered by local constraint damage (C dropping too low in high flux)
    damage_mask = (state.C < 0.5) & (state.phi > 1.0)
    if np.any(damage_mask):
        # Immune response: radically increase local constraint (swelling/barrier)
        state.C[damage_mask] += dt * 0.5
        # Cytokine spread: diffuse the constraint increase to neighbors
        grad_y, grad_x = np.gradient(state.C)
        state.C += dt * 0.01 * (grad_x**2 + grad_y**2)


def _tri_regime_bioenergetics(state, dt):
    """
    Tri-Regime Model (OOL): chlorophyll-like C_input, magnetite σ_e, water σ_p, melanin S.
    Unified throughput J from engine.origins_of_life.tri_regime_throughput_grid.
    """
    update_tri_regime_channels(state)
    phi = state.phi
    C = state.C
    S_scalar = float(state.meta.get("ool_S_stability", float(np.std(phi)) + 1e-9 + 0.15 * float(np.mean(np.maximum(np.abs(C), 1e-12)))))

    J = tri_regime_throughput_grid(state)

    # Overload: energy input >> stability -> damp phi
    overload = np.abs(phi) > S_scalar * 5
    if np.any(overload):
        damp_amount = dt * 0.1 * (np.abs(phi[overload]) - S_scalar * 5)
        # Prevent artificial zero-crossing overshoot
        phi_sign = np.sign(phi[overload])
        state.phi[overload] = np.maximum(0, np.abs(phi[overload]) - damp_amount) * phi_sign

    # Transport bottleneck: very high C -> reduce phi
    bottleneck = C > 10.0
    state.phi[bottleneck] -= dt * 0.05 * phi[bottleneck]

    state.meta["throughput_J"] = float(np.mean(J))
    compute_life_number_from_cached_channels(state)


def _morphogenesis(state, dt):
    """
    Paper 11: Developmental Patterning via Morphogen Gradients.
    Turing-like pattern formation via AFL feedback.
    """
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    flux_grad_mag = np.sqrt(grad_phi_x**2 + grad_phi_y**2)

    # Morphogen flux structures the tissue boundaries
    pattern_mask = flux_grad_mag > float(np.mean(flux_grad_mag)) * 1.2
    if np.any(pattern_mask):
        # Tissue hardens (C increases) where morphogen flux gradient is steep
        state.C[pattern_mask] += dt * 0.05 * flux_grad_mag[pattern_mask]
