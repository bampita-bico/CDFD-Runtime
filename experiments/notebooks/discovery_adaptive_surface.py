import sys
import os
import numpy as np
import h5py

# Ensure the cdfd_runtime module can be imported from the current repo layout.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'cdfd_runtime'))
OUTPUT_DIR = os.path.join(ROOT, 'experiments', 'outputs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

from engine.state import State
from engine.physics import step

def run_surface_discovery():
    print("--- Discovery Target F: Adaptive Surface Homeostasis ---")
    
    nx, ny = 32, 32 # Smaller grid for faster/stable sweep
    state = State(nx=nx, ny=ny)
    
    # Moderate overload to avoid overflow
    state.phi[:] = 5.0
    state.C[:] = 1.0
    state.update_psi()
    
    initial_psi = state.mean_psi()
    print(f"   Initial System State (Psi_s): {initial_psi:.4f} (Overload)")
    
    steps = 500
    dt = 0.05
    history = []
    
    print(f"Monitoring Adaptive Surface Evolution (S) for {steps} steps...")
    
    for i in range(steps):
        step(state, dt=dt)
        # Manually clip S to prevent runaway growth in this edge-case sweep
        state.S = np.clip(state.S, 0.01, 10.0)
        
        m_psi = state.mean_psi()
        if np.isnan(m_psi): break
            
        history.append({
            "t": state.t,
            "mean_psi": m_psi,
            "mean_s": np.mean(state.S),
            "mean_c": np.mean(state.C)
        })
        
    if not history:
        print("   [ERROR] Simulation diverged.")
        return

    final_psi = history[-1]["mean_psi"]
    print(f"   Final System State (Psi_s): {final_psi:.4f}")
    
    if abs(final_psi - 1.0) < abs(initial_psi - 1.0):
        print(f"   [CANDIDATE] Adaptive surface homeostasis observed; S(t) moved the system toward Psi_s ~ 1.0.")
    
    output_file = os.path.join(OUTPUT_DIR, "discovery_surface_evolution.h5")
    with h5py.File(output_file, 'w') as f:
        for key in history[0].keys():
            f.create_dataset(key, data=[h[key] for h in history])
    print(f"   Done. Results in {output_file}")

if __name__ == "__main__":
    run_surface_discovery()
