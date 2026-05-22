import sys
import numpy as np
import json
import os

sys.path.append('/home/bampita/Projects/CDFD/cdfd_runtime')
from engine.state import State
from engine.kernel import Kernel

def run_universal_collapse():
    print("Executing Universal Network Collapse Engine...")
    dt = 0.01
    steps = 500
    
    # Simulate a network (e.g. power grid or financial market)
    s = State(16,16)
    s.beta = np.full((16,16), 0.01) # Rigid constraint relaxation (slow recovery)
    
    # Core hub node taking massive flux
    hub_idx = (8,8)
    
    results = {
        "time": [],
        "phi_hub": [],
        "C_hub": [],
        "psi_hub": [],
        "psi_system_mean": [],
        "collapsed_nodes": []
    }
    
    for step in range(steps):
        t = step * dt
        
        # Exponential growth of drive (e.g. market bubble, climate heat flux)
        s.phi[hub_idx] += 1.5 * dt * (1 + 0.1 * t)
        
        # Standard CDFD constraint closure: dC/dt = alpha*Phi - beta*C
        s.C += dt * (0.1 * s.phi - s.beta * s.C)
        
        # Calculate Operating Ratio Psi_s
        s.psi_s = (s.phi / s.C) * s.S * s.Ms
        
        # Cascade Logic: If a node collapses (Psi > 1.5), it sheds Phi to neighbors
        collapsed = s.psi_s > 1.5
        num_collapsed = np.sum(collapsed)
        
        if np.any(collapsed):
            # Rapid constraint hardening (M_s locks) on collapsed nodes
            s.Ms[collapsed] += 0.5 * dt
            
            # Simple diffusion of Phi to simulate topological shunting
            grad_y, grad_x = np.gradient(s.phi)
            s.phi += dt * 0.5 * (grad_x**2 + grad_y**2)
            
        if step % 10 == 0:
            results["time"].append(t)
            results["phi_hub"].append(float(s.phi[hub_idx]))
            results["C_hub"].append(float(s.C[hub_idx]))
            results["psi_hub"].append(float(s.psi_s[hub_idx]))
            results["psi_system_mean"].append(float(s.psi_s.mean()))
            results["collapsed_nodes"].append(int(num_collapsed))
            
    return results

if __name__ == "__main__":
    os.makedirs("/home/bampita/Projects/CDFD/experiments/outputs", exist_ok=True)
    res = run_universal_collapse()
    
    out_file = "/home/bampita/Projects/CDFD/experiments/outputs/universal_collapse.json"
    with open(out_file, "w") as f:
        json.dump(res, f, indent=2)
    print(f"Universal collapse discovery saved to {out_file}")
