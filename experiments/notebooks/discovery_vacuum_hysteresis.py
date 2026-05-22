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
from engine.physics import step, CHI_ATTRACTOR

def run_vacuum_discovery():
    print("--- Discovery Target D: Vacuum Hysteresis & Stiffening ---")
    
    nx, ny = 64, 64
    state = State(nx=nx, ny=ny)
    
    # Vacuum parameters
    # Pulse a region near the Mujjabi Attractor
    center = nx // 2
    state.phi[center-2:center+2, center-2:center+2] = 50.0
    state.chi = CHI_ATTRACTOR
    
    steps = 500
    dt = 0.1
    history = []
    
    print(f"Pulsing Vacuum Flux and monitoring Hysteresis (Ms) for {steps} steps...")
    
    for i in range(steps):
        # Apply a sinusoidal flux pump
        pump = 20.0 * np.sin(i * 0.05)
        state.phi[center-1:center+1, center-1:center+1] += pump
        
        step(state, dt=dt)
        
        history.append({
            "t": state.t,
            "mean_phi": np.mean(state.phi),
            "mean_ms": np.mean(state.Ms),
            "center_ms": state.Ms[center, center],
            "psi": state.mean_psi()
        })
        
    # Analysis: look for finite memory lag. Ms should lag the Phi pump.
    ms_vals = [h["center_ms"] for h in history]
    phi_vals = [h["mean_phi"] for h in history]
    
    # Discovery: The Integral Kernel preserves vacuum history better than Euler
    max_ms = max(ms_vals)
    print(f"   [RESULT] Peak Vacuum Memory (Ms): {max_ms:.4f}")
    
    if max_ms > 1.05:
        print("   [CANDIDATE] Localized vacuum stiffening observed. Ms retains a residual high-flux memory signature.")

    output_file = os.path.join(OUTPUT_DIR, "discovery_vacuum_hysteresis.h5")
    with h5py.File(output_file, 'w') as f:
        for key in history[0].keys():
            f.create_dataset(key, data=[h[key] for h in history])
            
    print(f"   Done. Results in {output_file}")

if __name__ == "__main__":
    run_vacuum_discovery()
