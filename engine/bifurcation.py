"""Level 11 — Bifurcation Mapper.

Scans a 2D parameter space and records which regime each point produces.
Output is a phase diagram: a grid of (param_a, param_b) → regime label.

No AI. No guessing. Just running the engine and reading Ψ.
"""
import numpy as np
from engine.state import State
from engine.physics import run as physics_run


_REGIMES = {
    "stable": 0,
    "collapse": 1,
    "unstable_growth": 2,
    "oscillation": 3,
    "growth": 4,
    "decay": 5,
}


def _classify(history):
    if not history:
        return "empty"
    psi = [h["psi"] for h in history]
    mx, mn = max(psi), min(psi)
    final = psi[-1]
    mean = sum(psi) / len(psi)

    if mx > 2.5:
        return "unstable_growth"
    if mn < 0.25:
        return "collapse"
    crossings = sum(
        1 for i in range(1, len(psi)) if (psi[i] - mean) * (psi[i-1] - mean) < 0
    )
    if crossings >= 4:
        return "oscillation"
    if final > mean * 1.1:
        return "growth"
    if final < mean * 0.9:
        return "decay"
    return "stable"


def map_phase(
    param_a_name="alpha",
    param_b_name="beta",
    param_a_range=(0.01, 1.0),
    param_b_range=(0.01, 0.5),
    resolution=10,
    steps=40,
    nx=8, ny=8,
    fixed_params=None,
):
    fixed = {"alpha": 0.1, "beta": 0.05, "gamma": 0.1}
    if fixed_params:
        fixed.update(fixed_params)

    a_vals = np.linspace(*param_a_range, resolution)
    b_vals = np.linspace(*param_b_range, resolution)
    grid = []

    for a in a_vals:
        row = []
        for b in b_vals:
            params = dict(fixed)
            params[param_a_name] = float(a)
            params[param_b_name] = float(b)
            try:
                state = State(nx=nx, ny=ny)
                history = physics_run(state, steps=steps, **params)
                regime = _classify(history)
            except Exception:
                regime = "error"
            row.append({
                param_a_name: round(float(a), 4),
                param_b_name: round(float(b), 4),
                "regime": regime,
                "regime_id": _REGIMES.get(regime, -1),
            })
        grid.append(row)

    return {
        "param_a": param_a_name,
        "param_b": param_b_name,
        "a_values": [round(float(v), 4) for v in a_vals],
        "b_values": [round(float(v), 4) for v in b_vals],
        "grid": grid,
    }


def find_bifurcation_boundary(phase_map, regime_a="stable", regime_b="collapse"):
    """Extract the boundary cells where regime_a meets regime_b."""
    boundary = []
    grid = phase_map["grid"]
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell["regime"] != regime_a:
                continue
            neighbors = []
            if r > 0:
                neighbors.append(grid[r-1][c])
            if r < len(grid) - 1:
                neighbors.append(grid[r+1][c])
            if c > 0:
                neighbors.append(row[c-1])
            if c < len(row) - 1:
                neighbors.append(row[c+1])
            if any(n["regime"] == regime_b for n in neighbors):
                boundary.append(cell)
    return boundary


def regime_summary(phase_map):
    counts = {}
    for row in phase_map["grid"]:
        for cell in row:
            r = cell["regime"]
            counts[r] = counts.get(r, 0) + 1
    total = sum(counts.values())
    return {k: round(v / total, 3) for k, v in sorted(counts.items())}
