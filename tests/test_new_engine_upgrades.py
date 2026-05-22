import numpy as np

from engine.state import State
from engine.pharmacology import apply_pharmacology
from engine.medicine import apply_medicine

def test_disease_horizon():
    print("--- Testing Disease Horizon ---")
    s = State(4,4)
    # Simulate rising Psi_s
    s.psi_s = np.full((4,4), 1.2)
    s.history.append({"time": 0.0, "psi_s": np.full((4,4), 1.1)})
    s.t = 0.01
    
    t_col = s.calculate_disease_horizon(threshold=1.5)
    print(f"Horizon calculated. t_collapse_min: {s.meta['t_collapse_min']:.3f}")
    assert s.meta['t_collapse_min'] > 0

def test_pharmacology_synergy():
    print("\n--- Testing Pharmacological Synergy ---")
    s = State(4,4)
    # Orthogonal synergy: Lower Phi, Raise Beta
    drugs = [
        {"target": "phi", "effect": -0.1},
        {"target": "beta", "effect": 0.05}
    ]
    apply_pharmacology(s, drugs, dt=0.01)
    print(f"Synergy Status: {s.meta['synergy_status']}")
    assert "ORTHOGONAL" in s.meta['synergy_status']

def test_clinical_protocols():
    print("\n--- Testing AFL Medicine Protocols ---")
    s = State(4,4)
    s.C = np.full((4,4), 2.5) # High CKD constraint
    s.phi = np.full((4,4), 1.5) # High EPO drive
    apply_medicine(s, dt=0.01)
    if "renal_warning" in s.meta:
        print(f"Renal Protocol Warning: {s.meta['renal_warning']}")
    assert "renal_warning" in s.meta

if __name__ == "__main__":
    test_disease_horizon()
    test_pharmacology_synergy()
    test_clinical_protocols()
    print("\nAll native engine upgrades successfully integrated and tested!")
