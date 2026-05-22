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

from ontology.origins_of_life.tri_regime_bioenergetics import TriRegimeBioenergeticsProcess
from engine.state import State
from engine.kernel import Kernel

def run_discovery():
    print("--- Discovery Target A: OOL Phase Diagram (Life Number ~ 1) ---")
    
    # Range of sweeps
    n_points = 50
    phi_range = np.linspace(0.1, 10.0, n_points)
    c_range = np.linspace(0.1, 10.0, n_points)
    
    # Results matrix
    lambda_grid = np.zeros((n_points, n_points))
    
    # Instantiate OOL process
    ool = TriRegimeBioenergeticsProcess()
    
    print(f"Sweeping Energy Flux vs. Constraint ({n_points}x{n_points})...")
    
    for i, phi in enumerate(phi_range):
        for j, c in enumerate(c_range):
            # Create a localized 'cell' for this point
            cell = ool.spawn_protocell(f"cell_{i}_{j}")
            
            # Apply parameters
            # C_input = capture_efficiency (phi)
            # C_electron = sigma_e (fixed for sweep)
            # C_proton = sigma_p (fixed for sweep)
            # E_maintenance (fixed)
            
            # Mock the capacity contributions
            cell.C_input = phi
            cell.C_electron = 0.8
            cell.C_proton = 0.9
            cell.S = 1.0 + (c / 10.0) # S increases with constraint (resistance)
            
            # Compute the CDFD Life Number in the ontology adapter.
            lam = ool.compute_lambda(cell)
            lambda_grid[i, j] = lam
            
    # Save discovery results to HDF5
    output_file = os.path.join(OUTPUT_DIR, "discovery_ool_phase_results.h5")
    with h5py.File(output_file, 'w') as f:
        f.create_dataset('phi_range', data=phi_range)
        f.create_dataset('c_range', data=c_range)
        f.create_dataset('lambda_grid', data=lambda_grid)
        f.attrs['description'] = "Discovery Sweep: Emergence of Life Number near-critical window"
        
    print(f"   [DONE] Results saved to {output_file}")
    
    # Identify the threshold
    threshold_mask = (lambda_grid >= 0.98) & (lambda_grid <= 1.02)
    print(f"   Critical threshold (Life Number ~ 1.0) identified at {np.sum(threshold_mask)} points.")

if __name__ == "__main__":
    run_discovery()
