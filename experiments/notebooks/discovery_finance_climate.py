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

from engine.kernel import Kernel
from engine.state import State
from discovery.causal_discovery import CausalDiscoveryEngine

def run_coupled_discovery():
    print("--- Discovery Target B: Finance-Climate Coupling ---")
    
    steps = 400
    dt = 0.1
    
    # We will simulate two systems in a single grid for simplicity, 
    # but with a coupling tensor.
    # Region 1 (Left): Financial Market (Flow = Capital, C = Friction)
    # Region 2 (Right): Climate (Flow = Heat, C = CO2 forcing)
    
    nx, ny = 64, 64
    state = State(nx=nx, ny=ny)
    
    # Financial parameters
    state.alpha[:nx//2, :] = 0.2
    state.beta[:nx//2, :] = 0.05
    
    # Climate parameters
    state.alpha[nx//2:, :] = 0.1
    state.beta[nx//2:, :] = 0.02
    
    history = []
    
    print(f"Running coupled simulation for {steps} steps...")
    
    for i in range(steps):
        # 1. Standard Step
        # Manual coupling: If financial Psi is too high, increase climate constraint C
        fin_psi = np.mean(state.psi_s[:nx//2, :])
        if fin_psi > 1.3:
            # "Carbon-intensive market overload"
            state.C[nx//2:, :] *= 1.01 
            
        # Physics step
        from engine.physics import step as apply_physics
        apply_physics(state, dt=dt)
        
        # Record history of means
        history.append({
            "step": i,
            "fin_phi": np.mean(state.phi[:nx//2, :]),
            "fin_C": np.mean(state.C[:nx//2, :]),
            "fin_psi": np.mean(state.psi_s[:nx//2, :]),
            "cli_phi": np.mean(state.phi[nx//2:, :]),
            "cli_C": np.mean(state.C[nx//2:, :]),
            "cli_psi": np.mean(state.psi_s[nx//2:, :])
        })
        
        # Trigger an economic shock halfway through
        if i == steps // 2:
            print("   [SHOCK] Injecting massive capital flux into Financial sector...")
            state.phi[:nx//2, :] += 50.0

    # Save to HDF5
    output_file = os.path.join(OUTPUT_DIR, "discovery_finance_climate_results.h5")
    with h5py.File(output_file, 'w') as f:
        for key in history[0].keys():
            f.create_dataset(key, data=[h[key] for h in history])
            
    print(f"   [DONE] Results saved to {output_file}")
    
    # Run Causal Discovery on the results
    print("\n[Analysis] Extracting Causal Drivers from history...")
    time_series = {
        "Fin_Psi": np.array([h["fin_psi"] for h in history]),
        "Cli_C": np.array([h["cli_C"] for h in history]),
        "Fin_Phi": np.array([h["fin_phi"] for h in history])
    }
    
    discovery = CausalDiscoveryEngine(significance_level=0.05)
    cpdag, nodes = discovery.pc_algorithm(time_series)
    
    print(f"   Nodes: {nodes}")
    print("   Causal Adjacency Matrix:")
    print(cpdag)
    
    # Find index of Fin_Psi and Cli_C
    idx_fin = nodes.index("Fin_Psi")
    idx_cli = nodes.index("Cli_C")
    
    if cpdag[idx_fin, idx_cli] == 1:
        print("\n   [CANDIDATE] Detected model-side causal link: financial volatility -> climate constraint.")
    else:
        print("\n   [Result] No direct causal link detected at current significance.")

if __name__ == "__main__":
    run_coupled_discovery()
