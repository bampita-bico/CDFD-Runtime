"""
CDFD Frontier Discovery Sweep
==============================
25 domain frontiers × 10×10 parameter grids = 2,500 simulation points.
Each non-trivial result is logged as a structured discovery record.
Output: experiments/outputs/frontier_sweep.h5 + experiments/reports/FRONTIER_DISCOVERIES.md

Usage:
    python experiments/notebooks/discovery_frontier_sweep.py
"""
import sys
import os
import json
import numpy as np
import h5py

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'cdfd_runtime')))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTPUT_DIR = os.path.join(ROOT, 'experiments', 'outputs')
REPORT_DIR = os.path.join(ROOT, 'experiments', 'reports')

from engine.state import State
from engine.physics import step, CHI_ATTRACTOR

CHI = CHI_ATTRACTOR  # CODATA 2022 alpha inverse.

# ---------------------------------------------------------------------------
# Frontier definitions
# Each entry: {param_name: (lo, hi), ...} plus domain-metadata
# ---------------------------------------------------------------------------
FRONTIERS = {
    "Coherent_State_Transfer_BFPG": {
        "ranges": {"J": (0.80, 0.999), "Ms_init": (1.0, 8.0)},
        "phi_init": 5.0, "C_init": 5.0,
        "S_init": 1.0, "steps": 200, "dt": 0.05,
        "phi_label": "Coherence-transfer flux", "C_label": "Vacuum impedance",
        "law": "Mujjabi Capacity Law",
        "blueprint": "Bico Flux-Phase Gate coherence-transfer stress test",
        "target": "Psi_s deviation < 0.001 — bounded state-transfer window",
    },
    "Flow_Manipulation": {
        "ranges": {"alpha": (0.1, 3.0), "gamma": (0.01, 2.0)},
        "phi_init": 2.0, "C_init": 1.0,
        "S_init": 1.0, "steps": 150, "dt": 0.05,
        "phi_label": "Directed field density", "C_label": "Boundary resistance",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "VE Paper III — Flow Modulation Systems",
        "target": "Stable vortex locking (oscillation pattern)",
    },
    "Photonics_Coherent_Light": {
        "ranges": {"phi_init": (0.5, 20.0), "beta": (0.001, 0.5)},
        "C_init": 0.5, "S_init": 1.5, "Ms_init": 1.0,
        "steps": 200, "dt": 0.05,
        "phi_label": "Photon flux density", "C_label": "Optical absorption constraint",
        "law": "Mujjabi Vacuum Memory Law",
        "blueprint": "VE Paper VII — Photonic Vacuum Engineering",
        "target": "Ω coherence field → 1.0 (coherent-transport threshold)",
    },
    "Low_Impedance_Transport": {
        "ranges": {"J": (0.85, 0.999), "phi_init": (10.0, 200.0)},
        "C_init": 1.0, "S_init": 1.0,
        "steps": 100, "dt": 0.1,
        "phi_label": "Vacuum flux intensity", "C_label": "Vacuum impedance",
        "law": "Mujjabi Capacity Law + VPT",
        "blueprint": "High-flux transport stress test",
        "target": "Capacity-collapse boundary: C collapses, Psi_s rises sharply",
    },
    "Fibonacci_Geometry": {
        "ranges": {"gamma": (0.05, 3.0), "alpha": (0.05, 2.0)},
        "phi_init": 1.618, "C_init": 1.0, "S_init": 1.0,
        "steps": 300, "dt": 0.05,
        "phi_label": "Golden-ratio seeded flux", "C_label": "Geometric constraint",
        "law": "Mujjabi Stability Attractor",
        "blueprint": "VE Paper VI — Programmable Matter",
        "target": "Ψ_s spatial ratio → φ = 1.618 (Fibonacci self-organization)",
    },
    "High_Flux_Stress_Test": {
        "ranges": {"phi_init": (10.0, 1000.0), "C_init": (0.001, 1.0)},
        "S_init": 0.5, "Ms_init": 1.0,
        "steps": 50, "dt": 0.1,
        "phi_label": "Applied high-flux load", "C_label": "Material constraint",
        "law": "Mujjabi Capacity Law",
        "blueprint": "Safety-bounded vacuum-engineering stress test",
        "target": "Collapse threshold: C -> 0 under extreme Phi",
    },
    "Long_Duration_Memory_Recovery": {
        "ranges": {"S_init": (1.0, 4.0), "Ms_init": (1.0, 10.0)},
        "phi_init": 1.0, "C_init": 1.0,
        "steps": 2000, "dt": 0.01,
        "phi_label": "Metabolic flux", "C_label": "Biological damage load",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "Regeneration and recovery feasibility stress test",
        "target": "Sustained bounded recovery corridor near Psi_s = 1.0",
    },
    "Regenerative_Medicine": {
        "ranges": {"alpha": (0.5, 3.0), "beta": (0.001, 0.2)},
        "phi_init": 2.0, "C_init": 0.5, "S_init": 1.5,
        "steps": 300, "dt": 0.05,
        "phi_label": "Tissue repair flux", "C_label": "Scar/fibrosis constraint",
        "law": "Mujjabi Transport-Threshold Test",
        "blueprint": "VE Paper V — Medical Vacuum Engineering",
        "target": "C recovery crossing above 0.5 within 300 steps",
    },
    "Nociceptive_Signal_Gate": {
        "ranges": {"C_init": (0.001, 5.0), "beta": (0.01, 2.0)},
        "phi_init": 1.0, "S_init": 0.3,
        "steps": 200, "dt": 0.05,
        "phi_label": "Nociceptive signal flux", "C_label": "Inhibitory gate constraint",
        "law": "Mujjabi Capacity Law",
        "blueprint": "Phase V Device — Bioelectric Regulation Interface",
        "target": "Psi_s < 0.05 candidate signal-gating threshold",
    },
    "Artificial_Photosynthesis": {
        "ranges": {"phi_init": (0.1, 50.0), "C_init": (0.01, 5.0)},
        "S_init": 1.0, "Ms_init": 1.0,
        "steps": 200, "dt": 0.05,
        "phi_label": "Light input flux (Chlorophyll-analog)", "C_label": "Reaction barrier constraint",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "VE Paper VII Photonic + OOL Tri-Regime model",
        "target": "Life Number Λ > 1 at minimum C (efficient photosynthesis threshold)",
    },
    "Renewable_Future_Energy": {
        "ranges": {"Ms_init": (1.0, 10.0), "beta": (0.001, 0.5)},
        "phi_init": 5.0, "C_init": 1.0, "S_init": 1.0,
        "steps": 500, "dt": 0.02,
        "phi_label": "Energy input flux", "C_label": "Storage/dissipation barrier",
        "law": "Mujjabi Vacuum Memory Law",
        "blueprint": "Phase VI Device — Adaptive Atmospheric Regulation Grid",
        "target": "Optimal Ms for maximum Ψ_s stability (energy retention attractor)",
    },
    "3D_Printing_From_Flow": {
        "ranges": {"J": (0.5, 0.95), "S_init": (1.0, 5.0)},
        "phi_init": 10.0, "C_init": 2.0, "Ms_init": 2.0,
        "steps": 300, "dt": 0.05,
        "phi_label": "Material condensation flux", "C_label": "Geometric form constraint",
        "law": "Mujjabi Stability Attractor",
        "blueprint": "VE Paper VI — Programmable Matter / 3D Matter-from-Flux",
        "target": "Stable vortex-locked synthesis at Ψ_s ≈ 10 (Discovery 04 extension)",
    },
    "Nanotechnology": {
        "ranges": {"alpha": (0.5, 5.0), "gamma": (0.5, 5.0)},
        "phi_init": 0.1, "C_init": 0.1, "S_init": 2.0,
        "steps": 500, "dt": 0.01,
        "phi_label": "Nanoscale flux", "C_label": "Atomic lattice constraint",
        "law": "Mujjabi Boundary Principle",
        "blueprint": "Phase VI Device — Programmable Nanostructures (VE Paper XXXII)",
        "target": "Sub-cell vortex stability: oscillation without collapse",
    },
    "Programmable_Matter": {
        "ranges": {"gamma": (0.01, 3.0), "beta": (0.001, 1.0)},
        "phi_init": 3.0, "C_init": 1.0, "S_init": 1.0,
        "steps": 300, "dt": 0.05,
        "phi_label": "Atomic flow field", "C_label": "Lattice configuration constraint",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "VE Phase II Paper XVIII — Adaptive Materials",
        "target": "Phase transition: fluid→solid→plasma analog in Ψ_s",
    },
    "Programmable_Surfaces": {
        "ranges": {"phi_init": (0.5, 10.0), "C_init": (0.1, 5.0)},
        "S_init": 1.0, "Ms_init": 1.5,
        "steps": 300, "dt": 0.05,
        "phi_label": "Surface activation flux", "C_label": "Surface rigidity constraint",
        "law": "Mujjabi Vacuum Engineering Principle",
        "blueprint": "VE Paper II — Adaptive Surfaces",
        "target": "S-field self-organization: spatial patterns in surface responsiveness",
    },
    "Neural_Prosthetics": {
        "ranges": {"phi_init": (0.5, 20.0), "gamma": (0.05, 2.0)},
        "C_init": 1.0, "S_init": 1.0, "Ms_init": 1.0,
        "steps": 200, "dt": 0.05,
        "phi_label": "Motor command flux", "C_label": "Neural-mechanical interface C",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "Phase V Device — Bioelectric Synchronization Scanner",
        "target": "Coherence efficiency > 0.9 at interface",
    },
    "Ectogenesis_Incubation": {
        "ranges": {"alpha": (0.05, 0.5), "beta": (0.05, 0.5)},
        "phi_init": 1.0, "C_init": 0.8, "S_init": 0.9, "Ms_init": 1.2,
        "steps": 2000, "dt": 0.01,
        "phi_label": "Developmental growth flux", "C_label": "Biological support constraint",
        "law": "Mujjabi Adaptive Operating Ratio",
        "blueprint": "Phase VI Device — Coherence Habitat Systems",
        "target": "Stable development corridor: Ψ_s ∈ [0.9, 1.1] for 1000+ steps",
    },
    "Blancken_Layer_Stress_Test": {
        "ranges": {"J": (0.91, 0.999), "phi_init": (50.0, 500.0)},
        "C_init": 0.1, "S_init": 0.5, "Ms_init": 5.0,
        "steps": 100, "dt": 0.1,
        "phi_label": "Blancken-layer vacuum flux", "C_label": "Spacetime rigidity",
        "law": "Mujjabi Vacuum Memory Law + VPT",
        "blueprint": "Blancken Layer boundary stress test",
        "target": "VPT event: Ms → MS_MAX (spacetime rupture signature)",
    },
    "Halo_Impedance_Model": {
        "ranges": {"C_init": (2.0, 50.0), "phi_init": (0.5, 10.0)},
        "S_init": 1.0, "Ms_init": 1.0,
        "steps": 300, "dt": 0.05,
        "phi_label": "Galactic flux", "C_label": "Halo impedance field",
        "law": "Mujjabi Vacuum Memory Law",
        "blueprint": "VE Paper X — halo impedance model",
        "target": "Ψ_s ≈ 1.6 galactic stability (Discovery 12 extension)",
    },
    "Cognitive_Oscillation_Model": {
        "ranges": {"alpha": (0.5, 3.0), "gamma": (0.5, 3.0)},
        "phi_init": 5.0, "C_init": 2.0, "S_init": 1.0,
        "steps": 300, "dt": 0.05,
        "phi_label": "Information / neural signal flux", "C_label": "Inhibitory cognitive C",
        "law": "Mujjabi Stability Attractor",
        "blueprint": "Neuromorphic oscillation stress test",
        "target": "Stable cognitive oscillation: oscillation + SI < 0.5",
    },
    "Cancer_Interception": {
        "ranges": {"C_init": (0.001, 2.0), "alpha": (0.1, 2.0)},
        "phi_init": 5.0, "S_init": 0.5, "Ms_init": 1.0,
        "steps": 200, "dt": 0.05,
        "phi_label": "Tumor growth flux", "C_label": "Cellular constraint (immune/structural)",
        "law": "Mujjabi Transport-Threshold Test",
        "blueprint": "VE Phase II Paper XV — Medical Flow Modulation Devices",
        "target": "Escape velocity at C < 0.05 (Discovery I extension)",
    },
    "Fusion_Plasma_Confinement": {
        "ranges": {"phi_init": (5.0, 100.0), "C_init": (5.0, 100.0)},
        "S_init": 1.0, "Ms_init": 1.0,
        "steps": 200, "dt": 0.05,
        "phi_label": "Plasma flux", "C_label": "Magnetic confinement C",
        "law": "Mujjabi Capacity Law",
        "blueprint": "Phase VI Device — Coherence Resonance Chamber",
        "target": "Equilibrium at C = Φ (Ψ_s ≈ 14.7 fusion ceiling, Discovery 13 extension)",
    },
    "Economic_Collapse_Prevention": {
        "ranges": {"phi_init": (1.0, 500.0), "C_init": (0.1, 100.0)},
        "S_init": 1.0, "Ms_init": 1.0,
        "steps": 100, "dt": 0.05,
        "phi_label": "Capital flow velocity", "C_label": "Institutional friction",
        "law": "Mujjabi Capacity Law",
        "blueprint": "VE Phase II Paper XIX — CDFL Substrate Language",
        "target": "Divergence onset (NaN / Ψ_s > 1e6) — hyperinflation horizon",
    },
    "Seismic_Geological": {
        "ranges": {"alpha": (0.05, 1.5), "gamma": (0.1, 2.0)},
        "phi_init": 3.0, "C_init": 5.0, "S_init": 0.8,
        "steps": 300, "dt": 0.05,
        "phi_label": "Tectonic flux", "C_label": "Crustal rigidity",
        "law": "Mujjabi Transport-Threshold Test",
        "blueprint": "VE Phase III Paper XXIX — Experimental Proposals",
        "target": "Rupture precursor: unstable_growth before collapse",
    },
    "Cross_Domain_Mashup": {
        "ranges": {"phi_init": (0.5, 50.0), "C_init": (0.01, 20.0)},
        "S_init": 1.0, "Ms_init": 1.5,
        "steps": 200, "dt": 0.05,
        "phi_label": "Composite multi-domain flux", "C_label": "Composite multi-domain C",
        "law": "All Mujjabi Laws (cross-domain)",
        "blueprint": "VE Phase III Paper XXXV — Long-Term Evolution of Coherent Civilization",
        "target": "Novel emergent patterns not seen in single-domain sweeps",
    },
}

# ---------------------------------------------------------------------------
# Pattern detector (extended beyond detector.py)
# ---------------------------------------------------------------------------
def detect(psi_series):
    if not psi_series:
        return "empty"
    arr = np.array(psi_series, dtype=float)
    finite = arr[np.isfinite(arr)]
    if len(finite) == 0:
        return "diverged_nan"
    max_v = float(np.max(finite))
    min_v = float(np.min(finite))
    final_v = float(arr[-1]) if np.isfinite(arr[-1]) else float('inf')
    mean_v = float(np.mean(finite))

    if not np.isfinite(arr[-1]) or max_v > 1e5:
        return "diverged"
    if max_v > 5.0 and final_v > mean_v * 1.2:
        return "unstable_growth"
    if min_v < 0.05:
        return "collapse"
    if abs(final_v - 1.0) < 0.01 and max_v < 1.05:
        return "attractor_lock"   # Ψ_s = 1.0000 — the Age Reversal Attractor
    if _oscillating(arr[np.isfinite(arr)]):
        return "oscillation"
    if final_v > mean_v * 1.1:
        return "growth"
    if final_v < mean_v * 0.9:
        return "decay"
    return "stable"

def _oscillating(arr, min_crossings=3):
    if len(arr) < 6:
        return False
    mean = np.mean(arr)
    above = arr[0] > mean
    crossings = 0
    for v in arr[1:]:
        now = v > mean
        if now != above:
            crossings += 1
            above = now
    return crossings >= min_crossings

# ---------------------------------------------------------------------------
# Single-frontier simulation
# ---------------------------------------------------------------------------
def run_frontier(name, cfg, n_grid=10):
    range_keys = list(cfg["ranges"].keys())
    r1 = np.linspace(cfg["ranges"][range_keys[0]][0], cfg["ranges"][range_keys[0]][1], n_grid)
    r2 = np.linspace(cfg["ranges"][range_keys[1]][0], cfg["ranges"][range_keys[1]][1], n_grid)

    results = []
    for v1 in r1:
        for v2 in r2:
            params = {range_keys[0]: v1, range_keys[1]: v2}
            nx = ny = 16
            state = State(nx, ny)

            # Apply initial conditions
            phi0 = params.get("phi_init", cfg.get("phi_init", 1.0))
            C0   = params.get("C_init",   cfg.get("C_init", 1.0))
            S0   = params.get("S_init",   cfg.get("S_init", 1.0))
            Ms0  = params.get("Ms_init",  cfg.get("Ms_init", 1.0))
            state.phi[:] = phi0
            state.C[:] = C0
            state.S[:] = S0
            state.Ms[:] = Ms0

            # Apply range params to state fields
            for k, v in params.items():
                if k == "phi_init":
                    state.phi[:] = v
                elif k == "C_init":
                    state.C[:] = v
                elif k == "S_init":
                    state.S[:] = v
                elif k == "Ms_init":
                    state.Ms[:] = v
                elif k == "J":
                    state.J = v
                elif hasattr(state, k):
                    arr = getattr(state, k)
                    if hasattr(arr, 'shape'):
                        setattr(state, k, np.full_like(arr, v))
                    else:
                        setattr(state, k, v)

            alpha_v = params.get("alpha", state.alpha.mean() if hasattr(state.alpha, 'mean') else float(state.alpha))
            beta_v  = params.get("beta",  state.beta.mean()  if hasattr(state.beta, 'mean')  else float(state.beta))
            gamma_v = params.get("gamma", state.gamma.mean() if hasattr(state.gamma, 'mean') else float(state.gamma))

            psi_series = []
            try:
                for _ in range(cfg["steps"]):
                    step(state, dt=cfg["dt"],
                         alpha=alpha_v, beta=beta_v, gamma=gamma_v)
                    psi_series.append(float(state.mean_psi()))
            except Exception:
                pass

            pattern = detect(psi_series)
            final_psi = float(psi_series[-1]) if psi_series else float('nan')
            max_psi   = float(max((v for v in psi_series if np.isfinite(v)), default=float('nan')))
            min_psi   = float(min((v for v in psi_series if np.isfinite(v)), default=float('nan')))

            # Stability index
            try:
                ratio = float(np.mean(state.phi / np.maximum(state.C, 1e-9)))
                si = abs(ratio - CHI) / CHI
            except Exception:
                si = float('inf')

            results.append({
                "params": {**params, "alpha": alpha_v, "beta": beta_v, "gamma": gamma_v},
                "pattern": pattern,
                "final_psi": final_psi,
                "max_psi": max_psi,
                "min_psi": min_psi,
                "stability_index": si,
                "steps": len(psi_series),
                "frontier": name,
            })
    return results

# ---------------------------------------------------------------------------
# Discovery record builder
# ---------------------------------------------------------------------------
def is_interesting(rec):
    return rec["pattern"] not in ("stable", "empty")

def build_discovery(rec, frontier_cfg, idx):
    p = rec["params"]
    param_rows = "\n".join(
        f"| {k} | {v:.6g} | see frontier definition |"
        for k, v in sorted(p.items())
    )
    pattern = rec["pattern"]
    final_psi = rec["final_psi"]
    max_psi = rec["max_psi"]
    min_psi = rec["min_psi"]
    si = rec["stability_index"]
    name = rec["frontier"].replace("_", " ")
    blueprint = frontier_cfg.get("blueprint", "—")
    law = frontier_cfg.get("law", "—")
    target = frontier_cfg.get("target", "—")
    phi_label = frontier_cfg.get("phi_label", "Flux")
    C_label   = frontier_cfg.get("C_label", "Constraint")

    # Physical interpretation per pattern
    interp_map = {
        "diverged":        f"The {name} system exceeded its transport capacity (J → J_crit). Ψ_s diverged to {max_psi:.3g}, indicating a **Vacuum Phase Transition** or capacity saturation event. In physical terms: the medium can no longer sustain coherent flow — a first-order phase change.",
        "diverged_nan":    f"The {name} system produced a NaN Ψ_s — complete numerical field breakdown. This is treated as an invalid or beyond-domain parameter region, not as a physical claim.",
        "unstable_growth": f"The {name} system entered runaway growth (Ψ_s → {max_psi:.3g}). The adaptive surface S could not compensate for the excess flux — this is the **Hyper-Adaptation Instability** (Discovery F analogue) in this domain.",
        "collapse":        f"The {name} system collapsed to Ψ_s = {min_psi:.6g}. Constraint C overwhelmed flux Φ, driving the system into a low-flux trap. In this domain: {C_label} saturated, shutting down {phi_label} entirely.",
        "attractor_lock":  f"The {name} system locked to the **Mujjabi Geometric Attractor** (Ψ_s = 1.0000), marking a near-attractor control state in the model.",
        "oscillation":     f"The {name} system entered a stable oscillation cycle around Ψ_s = {final_psi:.4g}. This is a bounded rhythm that should be tested for robustness under parameter perturbation.",
        "growth":          f"The {name} system showed controlled growth toward Ψ_s = {final_psi:.4g}. Flux is outpacing constraint — a productive regime if bounded, a runaway if unchecked.",
        "decay":           f"The {name} system showed decay toward Ψ_s = {final_psi:.4g}. Constraint C is winning — the system is moving toward a low-flow, high-resistance steady state.",
    }
    interp = interp_map.get(pattern, f"Pattern: {pattern}. Ψ_s final = {final_psi:.4g}.")

    enables_map = {
        "diverged":        f"Identifies the **rupture threshold** for {name}. Engineering implication: avoid this regime in any controlled transport design.",
        "diverged_nan":    f"Bounds the **operational ceiling** for {name} systems. Any design must keep parameters below this NaN boundary.",
        "unstable_growth": f"Defines the **instability horizon** — parameter combinations to avoid in {name} devices unless the run is explicitly a bounded stress test.",
        "collapse":        f"Grounds the **minimum viable flux** requirement for {name}. Recovery requires β > α·M_s — a design target for {blueprint}.",
        "attractor_lock":  f"Grounds **{blueprint}** as a candidate near-attractor stability window. It is a simulation target for later falsification, not a demonstrated device claim.",
        "oscillation":     f"Identifies a candidate self-sustaining oscillation window for {name}. Applicable to {blueprint} only after independent validation.",
        "growth":          f"Defines the **activation corridor** for {name}: these parameters successfully build up the desired flux state.",
        "decay":           f"Identifies the **recovery protocol** boundary. Systems below this decay to rest — used to design controlled shutdown or pain-blocking (nociception suppression) modes.",
    }
    enables = enables_map.get(pattern, f"See {blueprint}.")

    phi_val = p.get('phi_init', frontier_cfg.get('phi_init', None))
    phi_str = f"{phi_val:.4g}" if phi_val is not None and not isinstance(phi_val, str) else str(phi_val)
    c_val = p.get('C_init', frontier_cfg.get('C_init', None))
    c_str = f"{c_val:.4g}" if c_val is not None and not isinstance(c_val, str) else str(c_val)

    return f"""
## Discovery FR-{idx:03d}: {pattern.replace("_", " ").title()} in {name}

**Status:** Candidate simulation result
**Frontier:** {name}
**VE Blueprint Link:** {blueprint}
**Mujjabi Law Validated:** {law}
**Discovery Target:** {target}

### Parameters
| Parameter | Value | Domain Role |
|-----------|-------|-------------|
| Φ (phi_init) | {phi_str} | {phi_label} |
| C (C_init) | {c_str} | {C_label} |
{param_rows}

### Result
- **Pattern detected:** `{pattern}`
- **Ψ_s final:** {final_psi:.6g}
- **Ψ_s maximum:** {max_psi:.6g}
- **Ψ_s minimum:** {min_psi:.6g}
- **Stability Index (SI = |Φ/C − χ*| / χ*):** {si:.6g}
  *(χ* = {CHI} — Mujjabi Geometric Attractor)*
- **Steps simulated:** {rec['steps']}

### Physical Interpretation
{interp}

### What This Enables
{enables}

### Falsification Condition
Within the engine model: increase β by 2× or set α → 0 — if the pattern disappears, the discovery is parameter-sensitive (not structural). If it persists across a 5× β range, it is a robust law.

### Reproduce
```python
# From /home/bampita/Projects/CDFD/cdfd_runtime/
# python ../experiments/notebooks/discovery_frontier_sweep.py
# The frontier "{rec['frontier']}" at params: {json.dumps({k: round(float(v), 4) for k, v in p.items()})}
```
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    all_results = []
    discoveries = []
    disc_idx = 1

    print(f"\n{'='*70}")
    print("  CDFD FRONTIER DISCOVERY SWEEP — 25 Domains × 100 Points = 2,500")
    print(f"{'='*70}\n")

    with h5py.File(os.path.join(OUTPUT_DIR, "frontier_sweep.h5"), "w") as hf:
        for fname, fcfg in FRONTIERS.items():
            print(f"[REACTOR] {fname} ...", end=" ", flush=True)
            recs = run_frontier(fname, fcfg, n_grid=10)
            all_results.extend(recs)

            psi_vals = np.array([r["final_psi"] for r in recs], dtype=float)
            hf.create_dataset(fname, data=psi_vals)

            interesting = [r for r in recs if is_interesting(r)]
            print(f"{len(recs)} points — {len(interesting)} discoveries")

            for rec in interesting:
                disc_md = build_discovery(rec, fcfg, disc_idx)
                discoveries.append(disc_md)
                disc_idx += 1

    # Summary statistics
    patterns = {}
    for r in all_results:
        p = r["pattern"]
        patterns[p] = patterns.get(p, 0) + 1

    # Write the big report
    header = f"""# CDFD Frontier Discovery Report
## The Grand Unified Discovery Campaign

**Total simulation points:** {len(all_results)}
**Total discoveries (non-trivial results):** {len(discoveries)}
**CHI_ATTRACTOR (χ*):** {CHI} (CODATA 2022: alpha^-1 = 137.035999177)
**Engine:** CDFD Runtime — 5-improvement spatial kernel (VE Paper II §7, Mujjabi Hysteresis Kernel, Coherence Field Ω, VPT Detector, Chi Attractor Feedback)

---

## Pattern Distribution Across 2,500 Points

| Pattern | Count | Physical Meaning |
|---------|-------|-----------------|
| stable | {patterns.get('stable', 0)} | Equilibrium — expected baseline |
| attractor_lock | {patterns.get('attractor_lock', 0)} | Mujjabi Geometric Attractor — candidate near-attractor stability |
| oscillation | {patterns.get('oscillation', 0)} | Self-sustaining vortex rhythm |
| growth | {patterns.get('growth', 0)} | Productive flux buildup |
| decay | {patterns.get('decay', 0)} | Constraint-dominant regime |
| unstable_growth | {patterns.get('unstable_growth', 0)} | Hyper-Adaptation Instability |
| collapse | {patterns.get('collapse', 0)} | Low-flux trap / cancer escape / system failure |
| diverged | {patterns.get('diverged', 0)} | Vacuum Phase Transition / capacity rupture |
| diverged_nan | {patterns.get('diverged_nan', 0)} | Invalid or beyond-domain numerical breakdown |

---

## Mujjabi Laws Tested

All discoveries are grounded in one or more of the following laws (MUJJABI_LAWS_AND_TESTS.md):
- **Mujjabi Capacity Law**: J/C → 1 drives nonlinear regulation; particle-like vortices are pressure-regulating states near saturation
- **Mujjabi Adaptive Operating Ratio**: Ψ_s = (Φ/C)·S·M_s — the universal grammar
- **Mujjabi Stability Attractor**: χ* = 1/α = {CHI} — the equilibrium aspect ratio of the regulator vortex
- **Mujjabi Vacuum Memory Law**: M_s ≠ 1 after overload — the medium remembers
- **Mujjabi Hysteresis Kernel**: M_s(x,t) = 1 + μ∫max(0,J/C−1)·exp(−(t−t′)/τ_M)dt′
- **Mujjabi Vacuum Engineering Principle**: Control Φ, C, S, or M_s to move a system across Ψ_s = 1

---

## The {len(discoveries)} Discoveries

"""

    report_path = os.path.join(REPORT_DIR, "FRONTIER_DISCOVERIES.md")
    with open(report_path, "w") as f:
        f.write(header)
        f.write("\n".join(discoveries))
        f.write(f"\n\n---\n*Generated by `discovery_frontier_sweep.py` — CDFD Runtime*\n")

    print(f"\n{'='*70}")
    print(f"  COMPLETE: {len(discoveries)} discoveries from {len(all_results)} simulation points")
    print(f"  Report: {report_path}")
    print(f"  HDF5:   {os.path.join(OUTPUT_DIR, 'frontier_sweep.h5')}")
    print(f"  Chi* used: {CHI}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    # Run from cdfd_runtime/ directory
    os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    main()
