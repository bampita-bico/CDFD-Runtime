"""Molecular flow interactions — aromatic stability, catalysis, and distributed transport fields."""
import numpy as np

def apply_chemistry(state, dt=0.01):
    try:
        _mineral_catalysis(state, dt)
        _distributed_transport(state, dt)
        _molecular_exchange(state, dt)
        _aromatic_stability_and_encoding(state, dt)
        _melanin_buffering(state, dt)
        _phosphate_activation(state, dt)
        _chirality_symmetry_breaking(state, dt)
    except Exception:
        raise

def _mineral_catalysis(state, dt):
    """
    Paper 1 & 5: Fe-S and Mineral-Organic Catalysis.
    Mineral surfaces (high gradient in Constraint C) lower activation energy,
    increasing local flow (Phi) and driving specific reactions.
    """
    grad_y, grad_x = np.gradient(state.C)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)

    # Mineral interfaces are where the constraint gradient is high
    mean_grad = float(np.mean(grad_mag))
    if mean_grad > 0:
        interface_mask = grad_mag > mean_grad * 1.5
        # Catalytic boost: Flow increases rapidly at the boundary
        state.phi[interface_mask] += dt * 0.05 * state.phi[interface_mask]

def _distributed_transport(state, dt):
    """
    Paper 2 & 3: Magnetite (electron transport) and Structured Water (proton conduction).
    Networked transport connects spatially separated reactions by forming
    low-constraint corridors (Lambda reduction) where flux is high.
    """
    # Calculate Flux: J = - (1/C) * grad(Phi)
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    flux_mag = np.sqrt((grad_phi_x / safe_C)**2 + (grad_phi_y / safe_C)**2)

    mean_flux = float(np.mean(flux_mag))
    if mean_flux > 0:
        high_flux_mask = flux_mag > mean_flux * 2.0
        # The transport network adapts: high flux reduces constraints (creates channels)
        state.C[high_flux_mask] = np.maximum(state.C[high_flux_mask] * (1.0 - 0.01 * dt), 1e-9)

def _molecular_exchange(state, dt):
    """Basic background chemical equilibrium."""
    state.phi += dt * 0.001 * (state.C - state.phi)

def _aromatic_stability_and_encoding(state, dt):
    """
    Paper 7: Aromatic Chemical Systems bridging Energy to Information.
    Aromatics (Quinones, Nucleobases) stabilize regions of high energy flux,
    creating persistent patterns (Information) that resist degradation.
    """
    mean_phi = float(state.phi.mean())
    mask = state.phi > mean_phi * 1.5

    # Aromatic stabilization: constraints adapt toward the energetic flow,
    # creating a persistent pattern where Psi approaches the balanced regime.
    state.C[mask] = state.C[mask] * 0.9 + state.phi[mask] * 0.1

def _melanin_buffering(state, dt):
    """
    Paper 11 guardrail: eumelanin is a mature endpoint exemplar of surplus
    stabilization, not an origin requirement. The runtime term stands for a
    broad redox/radical-buffering function that prebiotic analogues may satisfy
    with different chemistry.
    """
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    # Melanin provides an effective constraint barrier against overload
    lambda_melanin = 0.5 * safe_C
    lambda_eff = safe_C + lambda_melanin

    # Calculate effective buffered flux
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    J_eff_mag = np.sqrt((grad_phi_x / lambda_eff)**2 + (grad_phi_y / lambda_eff)**2)

    # Shift systems away from chaotic overload (Psi > 1.2) using buffered flux
    overload_mask = state.psi > 1.2
    if np.any(overload_mask):
        state.phi[overload_mask] -= dt * 0.1 * J_eff_mag[overload_mask]

def _phosphate_activation(state, dt):
    """
    Paper 10 Upgrade: Phosphate Chemistry as Energy Storage.
    High continuous flux environments catalyze the formation of discrete
    energy packets (E_p). Quantizes energy for later structural use.
    """
    grad_phi_y, grad_phi_x = np.gradient(state.phi)
    safe_C = np.where(state.C > 1e-9, state.C, 1e-9)
    flux_mag = np.sqrt((grad_phi_x / safe_C)**2 + (grad_phi_y / safe_C)**2)

    # Phosphate activation occurs in high flux / moderate constraint regions
    activation_threshold = float(np.mean(flux_mag)) * 1.5
    active_mask = flux_mag > activation_threshold

    # Convert continuous flux into stored discrete energy packets
    # E_p (Delta E_P) unit is arbitrated as 0.1
    if np.any(active_mask):
        energy_transfer = dt * 0.05 * flux_mag[active_mask]
        state.stored_energy[active_mask] += energy_transfer
        # Conserve energy by reducing continuous flow
        state.phi[active_mask] -= energy_transfer

def _chirality_symmetry_breaking(state, dt):
    """
    Paper 7/10 Upgrade: Chirality and Symmetry Breaking.
    Stochastic imbalances in C_L vs C_D are amplified by flux-constraint feedback.
    The dominant chirality reduces its own constraints via AFL, leading to homochirality.
    """
    safe_C_L = np.where(state.C_L > 1e-9, state.C_L, 1e-9)
    safe_C_D = np.where(state.C_D > 1e-9, state.C_D, 1e-9)

    grad_CL_y, grad_CL_x = np.gradient(state.C_L)
    grad_CD_y, grad_CD_x = np.gradient(state.C_D)

    J_L = np.sqrt((grad_CL_x / safe_C_L)**2 + (grad_CL_y / safe_C_L)**2)
    J_D = np.sqrt((grad_CD_x / safe_C_D)**2 + (grad_CD_y / safe_C_D)**2)

    # Positive feedback loop: higher flux reduces Lambda, which further increases L or D
    diff = J_L - J_D

    # Where J_L > J_D, C_L grows and C_D is suppressed (and vice versa)
    l_dominant = diff > 0
    d_dominant = diff < 0

    state.C_L[l_dominant] += dt * 0.1 * diff[l_dominant]
    state.C_D[l_dominant] = np.maximum(state.C_D[l_dominant] - dt * 0.1 * diff[l_dominant], 1e-9)

    state.C_D[d_dominant] += dt * 0.1 * np.abs(diff[d_dominant])
    state.C_L[d_dominant] = np.maximum(state.C_L[d_dominant] - dt * 0.1 * np.abs(diff[d_dominant]), 1e-9)
