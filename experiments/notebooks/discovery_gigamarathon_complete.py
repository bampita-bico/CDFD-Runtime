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

def run_gigamarathon():
    print("--- CDFD GIGAMARATHON: THE 1,000 DISCOVERY SWEEP ---")
    
    # We will simulate 1,000 parameter points across 10 high-order domains
    domains = {
        "Vacuum_Propulsion": {"J": (0.1, 0.99), "phi": (10, 100)},
        "Bio_Regeneration":  {"S": (0.1, 2.0), "Ms": (0.5, 5.0)},
        "Cancer_Escape":     {"C": (0.01, 10.0), "alpha": (0.1, 2.0)},
        "Economic_Resilience":{"phi": (1.0, 500.0), "beta": (0.01, 0.5)},
        "Information_Decay": {"gamma": (0.1, 2.0), "S": (0.01, 1.0)},
        "Tectonic_Stress":   {"alpha": (0.05, 1.0), "gamma": (0.1, 1.0)},
        "Immune_Thresholds": {"phi": (1.0, 50.0), "Ms": (0.1, 10.0)},
        "Knot_Stability":    {"phi": (50.0, 200.0), "C": (10.0, 500.0)},
        "Cognitive_Dogma":   {"C": (10.0, 1000.0), "S": (0.01, 0.5)},
        "Neural_Formation":  {"gamma": (0.1, 2.0), "alpha": (0.1, 2.0)}
    }
    
    output_file = os.path.join(OUTPUT_DIR, "gigamarathon_1000_results.h5")
    with h5py.File(output_file, 'w') as f:
        for domain, ranges in domains.items():
            print(f"   [REACTOR] Simulating Domain: {domain}...")
            points = 100
            results = np.zeros(points)
            
            # Extract range keys
            keys = list(ranges.keys())
            r1 = np.linspace(ranges[keys[0]][0], ranges[keys[0]][1], 10)
            r2 = np.linspace(ranges[keys[1]][0], ranges[keys[1]][1], 10)
            
            idx = 0
            for v1 in r1:
                for v2 in r2:
                    state = State(nx=16, ny=16) # Minimal grid for 1000 runs on 6GB RAM
                    # Apply params
                    setattr(state, keys[0], np.full((16,16), v1) if keys[0] != 'J' else v1)
                    setattr(state, keys[1], np.full((16,16), v2) if keys[1] != 'J' else v2)
                    
                    for _ in range(50): # 50 steps per discovery
                        step(state, dt=0.1)
                    
                    results[idx] = state.mean_psi()
                    idx += 1
            
            f.create_dataset(domain, data=results)
            
    print(f"\n--- SUCCESS: 1,000 Scientific Targets Secured in {output_file} ---")

if __name__ == "__main__":
    run_gigamarathon()
