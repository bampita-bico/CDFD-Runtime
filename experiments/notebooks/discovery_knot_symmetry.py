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
from engine.physics import step, VortexRingSolver, CHI_ATTRACTOR

def run_knot_discovery():
    print("--- Discovery Target E: Higher-Order Torus Knot Stability (n=7) ---")
    
    # We will simulate a T(2,7) knot by embedding 7 focal points of constraint
    nx, ny = 128, 128
    state = State(nx=nx, ny=ny)
    
    # Heptafoil (n=7)
    n = 7
    knot_data = {
        "n": n,
        "masses": [1.5, 1.6, 1.4, 1.7, 1.5, 1.6, 1.8] # Quasi-symmetric masses
    }
    
    print(f"Embedding T(2,{n}) knot structure into the vacuum constraint field...")
    state.embed_knot(knot_data)
    
    # Analyze initial stability index
    solver = VortexRingSolver()
    mean_phi_c = np.mean(state.phi / state.C)
    initial_stab = solver.stability_index(mean_phi_c)
    
    print(f"   Initial Stability Index (relative to Chi={CHI_ATTRACTOR}): {initial_stab:.6f}")
    
    # Evolve the knot
    steps = 200
    history = []
    
    for i in range(steps):
        step(state, dt=0.05)
        mean_phi_c = np.mean(state.phi / state.C)
        history.append(solver.stability_index(mean_phi_c))
        
    final_stab = history[-1]
    print(f"   Final Stability Index after {steps} steps: {final_stab:.6f}")
    
    if final_stab < initial_stab:
        print(f"   [CANDIDATE] Heptafoil (n={n}) self-stabilization observed toward the CDFD geometric attractor.")
    else:
        print(f"   [Result] Knot dissipation observed. n={n} requires higher flux to stabilize.")

    output_file = os.path.join(OUTPUT_DIR, "discovery_knot_n7.h5")
    with h5py.File(output_file, 'w') as f:
        f.create_dataset('stability_history', data=history)
    print(f"   Done. Results in {output_file}")

if __name__ == "__main__":
    run_knot_discovery()
