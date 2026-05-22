"""
OOL tri-regime channels aligned with Origins_of_life_series.

Primary sketch: ``Origins_of_life_series/plants-we forgot.docx`` (chlorophyll-like energy
input, magnetite-like electron transport, structured-water proton coherence, melanin-like
stability buffer). Formal addendum: ``OOL_re-written_with_proofs/ool_11_tri_regime_addendum.tex``.
Runnable demo: ``supplementary_ool_11.py`` and ``cdfd --ool-paper 11``.

Maps prebiotic / biological roles to named scalars used by Λ and throughput J.
Notation bridge for Life Number components (C replaces legacy Lambda):

  chlorophyll-like  → C_input     (energy input proxy)
  magnetite-like    → σ_e         (electron transport; inverse effective constraint)
  water-like        → σ_p         (proton coherence / spatial coherence of Φ)
  melanin-like      → S_stability (dissipation + buffering; disorder + mean Λ proxy)

Unified throughput: J = |Φ| · (σ_e · σ_p) / S  (grid-level with coherent σ_p scaling).

Life number: Λ = (C_input · σ̄_e · σ̄_p · τ_relax) / (S̄ · E_maintenance)
"""

import numpy as np

TAU_RELAX = 1.0
E_MAINTENANCE = 1.0

# Stable keys on state.meta (also documented on State)
META_OOL_PREFIX = "ool_"


def update_tri_regime_channels(state) -> dict[str, float]:
    """
    Populate state.meta with scalar OOL channel summaries + grid-derived throughput.
    Safe to call every biology step.
    """
    phi = np.nan_to_num(state.phi, nan=0.0, posinf=25.0, neginf=0.0)
    lambda_field = np.nan_to_num(state.C, nan=1.0, posinf=25.0, neginf=1e-12)
    safe_lambda = np.maximum(np.abs(lambda_field), 1e-12)

    # --- Chlorophyll-like: energy input proxy (mean activity / absorption analogue)
    c_input = float(np.mean(np.abs(phi)))

    grad_y, grad_x = np.gradient(phi)
    flux_mag = np.sqrt(np.clip((grad_x / safe_lambda) ** 2 + (grad_y / safe_lambda) ** 2, 0.0, 1e12))

    # --- Magnetite-like: distributed electron transport — channels lower effective resistance
    sigma_e_arr = 1.0 / safe_lambda
    sigma_e_mean = float(np.mean(sigma_e_arr))
    # Couple high flux corridors (Paper 2–3) into transport effectiveness
    mean_fm = float(np.mean(flux_mag)) + 1e-12
    transport_factor = float(np.mean(flux_mag / (mean_fm + flux_mag * 0.1)))
    sigma_e_mean *= max(0.5, min(1.5, transport_factor))

    # --- Water-like: proton / coherence — high mean |phi| with low spatial variance → high σ_p
    std_phi = float(np.std(phi))
    sigma_p = float(np.mean(np.abs(phi))) / (std_phi + 1e-9)
    sigma_p = max(0.0, min(sigma_p, 1e6))

    # --- Melanin-like: stability / dissipation — disorder plus mean constraint (redox buffer analogue)
    melanin_buffer = 0.15 * float(np.mean(safe_lambda))
    S_stability = std_phi + 1e-9 + melanin_buffer

    m = state.meta
    # Map to weakest-link capacity notation (C_i)
    c_electron = sigma_e_mean
    c_proton = sigma_p
    c_stability = 1.0 / S_stability

    # Weakest-link throughput bound
    j_max = min(c_input, c_electron, c_proton, c_stability)

    m[META_OOL_PREFIX + "C_input"] = c_input
    m[META_OOL_PREFIX + "C_electron"] = c_electron
    m[META_OOL_PREFIX + "C_proton"] = c_proton
    m[META_OOL_PREFIX + "C_stability"] = c_stability
    m[META_OOL_PREFIX + "sigma_e"] = sigma_e_mean
    m[META_OOL_PREFIX + "sigma_p"] = sigma_p
    m[META_OOL_PREFIX + "S_stability"] = S_stability
    m[META_OOL_PREFIX + "transport_factor"] = transport_factor
    m[META_OOL_PREFIX + "J_max"] = j_max

    return {
        "C_input": c_input,
        "C_electron": c_electron,
        "C_proton": c_proton,
        "C_stability": c_stability,
        "J_max": j_max,
        "sigma_e": sigma_e_mean,
        "sigma_p": sigma_p,
        "S_stability": S_stability,
    }


def tri_regime_throughput_grid(state) -> np.ndarray:
    """J = |Φ| (σ_e · σ_p) / S on the grid (σ_p uses local coherence proxy)."""
    phi = np.nan_to_num(state.phi, nan=0.0, posinf=25.0, neginf=0.0)
    safe_lambda = np.maximum(np.abs(np.nan_to_num(state.C, nan=1.0, posinf=25.0, neginf=1e-12)), 1e-12)
    sigma_e_arr = 1.0 / safe_lambda
    grad_y, grad_x = np.gradient(phi)
    grad_mag = np.sqrt(np.clip(grad_x**2 + grad_y**2, 0.0, 1e12)) + 1e-9
    # Local coherence: strong relative to local gradient (Grotthuss / structured-water proxy)
    phi_abs = np.abs(phi)
    sigma_p_arr = phi_abs / (grad_mag + 0.05 * float(np.mean(phi_abs) + 1e-9))

    std_phi = float(np.std(phi))
    S_scalar = std_phi + 1e-9 + 0.15 * float(np.mean(safe_lambda))
    S_arr = np.full_like(phi, S_scalar, dtype=float)

    J = phi_abs * (sigma_e_arr * sigma_p_arr) / S_arr
    J = np.nan_to_num(J, nan=0.0, posinf=1e6, neginf=0.0)
    return J


def compute_life_number_from_cached_channels(state) -> float:
    """Λ from meta populated by update_tri_regime_channels (no recompute)."""
    m = state.meta
    pre = META_OOL_PREFIX
    ci = float(m.get(pre + "C_input", 1e-9))
    se = float(m.get(pre + "sigma_e", 1.0))
    sp = float(m.get(pre + "sigma_p", 1.0))
    S = float(m.get(pre + "S_stability", 1.0))
    # Equivalently: lam = (ci * c_electron * c_proton * TAU_RELAX) / (S * E_MAINTENANCE + 1e-15)
    lam = (ci * se * sp * TAU_RELAX) / (S * E_MAINTENANCE + 1e-15)
    lam = float(np.nan_to_num(lam, nan=0.0, posinf=1e6, neginf=0.0))
    state.meta["life_number"] = lam
    return float(lam)


def compute_life_number(state) -> float:
    """Refresh OOL channels then compute Λ."""
    update_tri_regime_channels(state)
    return compute_life_number_from_cached_channels(state)
