"""
Medical Systems and Clinical Diagnostics (AFL Biology & Medicine)
Implements:
1. AFL Renal Protocol (Anaemia & CKD-MBD)
2. Autoimmune Parasitic-Drain Boundary Logic
"""
import numpy as np

def apply_medicine(state, dt=0.01):
    """
    Applies clinical medicine models natively to the state.
    """
    _afl_renal_protocol(state, dt)
    _autoimmune_drain_logic(state, dt)
    state.S = np.maximum(state.S, 0.05)
    state.Ms = np.maximum(state.Ms, 1.0)
    state.update_psi()

def _afl_renal_protocol(state, dt):
    """
    Paper 06: Renal AFL CKD, Erythropoiesis, and Anaemia.
    Models the danger of flooding a rigid renal constraint (C) with Phi-driving hormones (EPO/Calcium).
    """
    # Assuming the center of the grid represents the renal nexus for this model
    renal_mask = np.zeros_like(state.C, dtype=bool)
    cx, cy = state.nx // 2, state.ny // 2
    renal_mask[cx-2:cx+2, cy-2:cy+2] = True
    
    # If renal constraint is extremely high (CKD state)
    high_c_mask = (state.C > 2.0) & renal_mask
    
    if np.any(high_c_mask):
        # The AFL Renal Protocol warns:
        # If Phi is artificially driven high here (e.g., EPO administration)
        # It causes vascular calcification (Ms locking)
        epo_driven_mask = high_c_mask & (state.phi > 1.2)
        if np.any(epo_driven_mask):
            state.Ms[epo_driven_mask] += 0.05 * dt # Vascular calcification penalty
            state.meta["renal_warning"] = "AFL Violation: EPO driven against high C. Calcification triggered."

def _autoimmune_drain_logic(state, dt):
    """
    Paper 08: Immunology and Autoimmune Boundary Logic.
    Models autoimmune disease as the immune system mistakenly applying 
    massive constraints (C) to healthy tissue flux, acting like it's a parasitic drain.
    """
    # Healthy flux normally does not trigger constraint
    healthy_flux_mask = (state.phi > 0.8) & (state.phi < 1.2)
    
    # Autoimmune trigger: Random topological error where healthy flux triggers C
    # We simulate an autoimmune state via a boolean flag in meta
    if state.meta.get("autoimmune_state_active", False):
        if np.any(healthy_flux_mask):
            # Immune system attacks healthy flux
            state.C[healthy_flux_mask] += 0.2 * dt
            
            # Classical treatment (global immunosuppression) crashes S everywhere
            if state.meta.get("treatment_type") == "global_immunosuppression":
                state.S -= 0.1 * dt
                state.S = np.maximum(state.S, 0.1)
                
            # AFL Protocol (targeted memory clearance)
            elif state.meta.get("treatment_type") == "afl_targeted_clearance":
                state.Ms[healthy_flux_mask] -= 0.2 * dt
                state.Ms = np.maximum(state.Ms, 1.0)
