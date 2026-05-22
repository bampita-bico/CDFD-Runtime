import sys
import numpy as np
import json
import os

sys.path.append('/home/bampita/Projects/CDFD/cdfd_runtime')
from engine.state import State
from engine.biology import apply_biology

def run_parasitic_drain():
    print("Running Mujjabi Parasitic-Drain Law...")
    s = State(16, 16)
    dt = 0.01
    results = {"time": [], "phi_sys": [], "phi_tumor": [], "C_sys": [], "psi_sys": []}
    
    # Create tumor node (high Phi, 0 surface responsiveness S)
    tumor_idx = (8, 8)
    s.S[tumor_idx] = 0.0
    
    for step in range(500):
        t = step * dt
        
        # Tumor aggressively consumes Phi
        s.phi[tumor_idx] += 0.5 * dt
        
        apply_biology(s, dt)
        s.psi_s = (s.phi / s.C) * s.S * s.Ms
        
        if step % 10 == 0:
            sys_mask = np.ones((16,16), dtype=bool)
            sys_mask[tumor_idx] = False
            
            results["time"].append(t)
            results["phi_sys"].append(float(s.phi[sys_mask].mean()))
            results["phi_tumor"].append(float(s.phi[tumor_idx]))
            results["C_sys"].append(float(s.C[sys_mask].mean()))
            results["psi_sys"].append(float(s.psi_s[sys_mask].mean()))
            
    return results

def run_cycling_retention():
    print("Running Mujjabi Cycling-Retention Test...")
    s = State(16, 16)
    dt = 0.01
    results = {"time": [], "phi": [], "C": [], "Ms": [], "psi_s": []}
    
    for step in range(500):
        t = step * dt
        
        # Oscillating stress (Fasting / Feeding cycle)
        if (step // 50) % 2 == 0:
            s.phi += 0.2 * dt # Feeding/Stress
        else:
            s.phi -= 0.1 * dt # Fasting/Recovery
            s.phi = np.maximum(s.phi, 1.0)
            
        # Recovery phase improves structural memory (Ms reduces towards optimal 1.0)
        if s.phi.mean() < 1.2:
            s.Ms -= 0.01 * dt
            s.Ms = np.maximum(s.Ms, 1.0)
            
        apply_biology(s, dt)
        s.psi_s = (s.phi / s.C) * s.S * s.Ms
        
        if step % 10 == 0:
            results["time"].append(t)
            results["phi"].append(float(s.phi.mean()))
            results["C"].append(float(s.C.mean()))
            results["Ms"].append(float(s.Ms.mean()))
            results["psi_s"].append(float(s.psi_s.mean()))
            
    return results

if __name__ == "__main__":
    os.makedirs("/home/bampita/Projects/CDFD/experiments/outputs", exist_ok=True)
    res1 = run_parasitic_drain()
    res2 = run_cycling_retention()
    
    out_file = "/home/bampita/Projects/CDFD/experiments/outputs/biology_mujjabi_discoveries.json"
    with open(out_file, "w") as f:
        json.dump({"parasitic_drain": res1, "cycling_retention": res2}, f, indent=2)
    print(f"Biological Mujjabi Discoveries saved to {out_file}")
