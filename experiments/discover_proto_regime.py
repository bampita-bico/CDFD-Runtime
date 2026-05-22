import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.state import State
from engine.physics import step, update_psi

print("--- CDFD Runtime: Proto-Regime Boundary Probe ---")

# Initialize a vacuum space (Assuming State(nx, ny) or check kwargs)
try:
    state = State(5, 5)
except TypeError:
    state = State(shape=(5, 5))

# Force the Proto-Regime boundary-test conditions.
state.C.fill(1e-9)
state.phi.fill(1e6)
state.S.fill(1.0)
state.Ms.fill(1.0)

print(f"Initial State: C = {state.C[0,0]:.1e}, Phi = {state.phi[0,0]:.1e}")
update_psi(state)
print(f"Initial Psi_s (Operating Ratio) = {state.psi_s[0,0]:.1e}")

print("\nRunning CDFD Physics Kernel (10 cycles)...")
try:
    for i in range(10):
        step(state, dt=0.01)
except Exception as e:
    print(f"Engine Exception (Expected at C->0 limits): {e}")

print(f"\nFinal State:")
print(f"C = {state.C[0,0]:.1e}")
print(f"Phi = {state.phi[0,0]:.1e}")
print(f"Psi_s = {state.psi_s[0,0]:.1e}")
print(f"M_s = {state.Ms[0,0]:.1f}")

print("\n--- BOUNDARY LOG ---")
if state.psi_s[0,0] > 1.5:
    print("Candidate Proto-Regime boundary detected.")
    print("Interpretation: forcing C toward a numerical floor with extreme Phi drives Psi_s to a very large value.")
    print("Status: numerical stress test and falsification target, not proof of vacuum manipulation or device behavior.")
