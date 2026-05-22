"""
Pharmacological Synergy and Constraint Prediction Engine
Implements the AFL Synergy Theorem directly into the native runtime.
"""
import numpy as np

def apply_pharmacology(state, drugs, dt=0.01):
    """
    drugs is a list of dicts. Example:
    [
        {"target": "phi", "effect": -0.1},    # e.g., Insulin (lowering glucose flux directly)
        {"target": "beta", "effect": +0.05}   # e.g., GLP-1 RA (improving relaxation/elasticity)
    ]
    """
    phi_change = 0.0
    beta_change = 0.0
    c_change = 0.0
    
    # Aggregate effects
    for drug in drugs:
        target = drug.get("target")
        effect = float(drug.get("effect", 0.0))
        if target == "phi":
            phi_change += effect
        elif target == "beta":
            beta_change += effect
        elif target == "C":
            c_change += effect
            
    # Apply to state
    state.phi += phi_change * dt
    state.beta += beta_change * dt
    state.C += c_change * dt
    
    # Redundancy and Clashing Diagnostics
    phi_targeting_count = sum(1 for d in drugs if d.get("target") == "phi" and float(d.get("effect", 0.0)) < 0)
    beta_targeting_count = sum(1 for d in drugs if d.get("target") == "beta" and float(d.get("effect", 0.0)) > 0)
    
    if phi_targeting_count >= 2 and beta_targeting_count == 0:
        state.meta["ischemia_warning"] = True
        state.meta["synergy_status"] = "REDUNDANT: Dangerous Phi collapse risk."
        
    elif phi_targeting_count >= 1 and beta_targeting_count >= 1:
        state.meta["ischemia_warning"] = False
        state.meta["synergy_status"] = "ORTHOGONAL SYNERGY: Optimal Psi_s recovery."
        
    else:
        state.meta["synergy_status"] = "STANDARD"

    # Enforce physical boundaries
    state.phi = np.maximum(state.phi, 0.01)
    state.beta = np.maximum(state.beta, 0.0001)
    state.C = np.maximum(state.C, 0.01)
    state.update_psi()
