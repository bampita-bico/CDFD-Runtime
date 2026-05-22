import sys
import numpy as np
import json
import os

sys.path.append('/home/bampita/Projects/CDFD/cdfd_runtime')
from engine.state import State
from engine.biology import apply_biology

def run_synergy_test():
    print("Executing AFL Drug Synergy Prediction Engine...")
    dt = 0.01
    steps = 400
    
    # 1. Disease Control: High drive, impaired relaxation
    s_control = State(4,4)
    s_control.beta = np.full((4,4), 0.005)
    
    # 2. Redundant (Two Phi-lowering drugs)
    s_red = State(4,4)
    s_red.beta = np.full((4,4), 0.005)
    
    # 3. Orthogonal Synergy (One Phi-lowering, one Beta-enhancing)
    s_syn = State(4,4)
    s_syn.beta = np.full((4,4), 0.005)
    
    results = {
        "time": [],
        "control_psi": [],
        "redundant_psi": [],
        "redundant_phi": [],
        "synergy_psi": [],
        "synergy_C": []
    }
    
    for step in range(steps):
        t = step * dt
        
        # Apply disease stress (Phi drive)
        if t < 1.0:
            s_control.phi += 0.2 * dt
            s_red.phi += 0.2 * dt
            s_syn.phi += 0.2 * dt
            
        # Apply treatments starting at t = 1.0
        if t >= 1.0:
            # Redundant: aggressively lower Phi (e.g. insulin + sulfonylurea)
            s_red.phi -= 0.15 * dt
            
            # Synergy: gently lower Phi (e.g. SGLT2i) AND increase relaxation Beta (e.g. GLP1)
            s_syn.phi -= 0.05 * dt
            s_syn.beta = np.full((4,4), 0.05) # Drug restores elasticity
            
        # Prevent physical impossibilities
        for s in [s_control, s_red, s_syn]:
            s.phi = np.maximum(s.phi, 0.1)
            apply_biology(s, dt)
            s.psi_s = (s.phi / s.C) * s.S * s.Ms
            
        if step % 10 == 0:
            results["time"].append(t)
            results["control_psi"].append(float(s_control.psi_s.mean()))
            results["redundant_psi"].append(float(s_red.psi_s.mean()))
            results["redundant_phi"].append(float(s_red.phi.mean()))
            results["synergy_psi"].append(float(s_syn.psi_s.mean()))
            results["synergy_C"].append(float(s_syn.C.mean()))
            
    return results

if __name__ == "__main__":
    os.makedirs("/home/bampita/Projects/CDFD/experiments/outputs", exist_ok=True)
    res = run_synergy_test()
    
    out_file = "/home/bampita/Projects/CDFD/experiments/outputs/drug_synergy_predictions.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Synergy predictions saved to {out_file}")
