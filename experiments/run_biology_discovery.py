import sys
import numpy as np
import json
import os

sys.path.append('/home/bampita/Projects/CDFD/cdfd_runtime')
from engine.state import State
from engine.biology import apply_biology
from engine.kernel import Kernel

def run_metabolic_saturation():
    print("Running Metabolic Saturation (Mujjabi Capacity Law)...")
    s = State(16, 16)
    dt = 0.01
    results = {"time": [], "phi": [], "C": [], "psi_s": []}
    
    for step in range(500):
        t = step * dt
        # Add external nutrient load
        s.phi += 0.05 * dt
        apply_biology(s, dt)
        s.psi_s = (s.phi / s.C) * s.S * s.Ms
        
        if step % 10 == 0:
            results["time"].append(t)
            results["phi"].append(float(s.phi.mean()))
            results["C"].append(float(s.C.mean()))
            results["psi_s"].append(float(s.psi_s.mean()))
            
    return results

def run_chronic_drift():
    print("Running Chronic Disease Drift (Mujjabi Vacuum Memory Law)...")
    s = State(16, 16)
    dt = 0.01
    # Impair relaxation
    s.beta = np.full((16, 16), 0.001) 
    results = {"time": [], "phi": [], "C": [], "psi_s": []}
    
    for step in range(500):
        t = step * dt
        # Transient stress load
        if t < 2.0:
            s.phi += 0.1 * dt
        else:
            s.phi -= 0.02 * dt # Stress removed, returning to baseline
            s.phi = np.maximum(s.phi, 1.0)
            
        apply_biology(s, dt)
        s.psi_s = (s.phi / s.C) * s.S * s.Ms
        
        if step % 10 == 0:
            results["time"].append(t)
            results["phi"].append(float(s.phi.mean()))
            results["C"].append(float(s.C.mean()))
            results["psi_s"].append(float(s.psi_s.mean()))
            
    return results

def run_tri_regime():
    print("Running Tri-Regime Bioenergetics (Lambda Transition)...")
    s = State(16, 16)
    dt = 0.01
    results = {"time": [], "life_number": [], "throughput": []}
    
    for step in range(500):
        t = step * dt
        s.phi += 0.01 * dt
        apply_biology(s, dt)
        
        if step % 10 == 0:
            results["time"].append(t)
            results["life_number"].append(float(s.meta.get("life_number", 0.0)))
            results["throughput"].append(float(s.meta.get("throughput_J", 0.0)))
            
    return results

if __name__ == "__main__":
    os.makedirs("/home/bampita/Projects/CDFD/experiments/outputs", exist_ok=True)
    res1 = run_metabolic_saturation()
    res2 = run_chronic_drift()
    res3 = run_tri_regime()
    
    out_file = "/home/bampita/Projects/CDFD/experiments/outputs/biology_discoveries.json"
    with open(out_file, "w") as f:
        json.dump({"metabolic_saturation": res1, "chronic_drift": res2, "tri_regime": res3}, f, indent=2)
    print(f"Discoveries saved to {out_file}")
