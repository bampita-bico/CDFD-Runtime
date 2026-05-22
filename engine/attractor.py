"""Level 15 — Attractor Detection.

Identifies the long-run fate of the system from trajectory data alone:
  - Fixed point: Ψ converges to a constant
  - Limit cycle: Ψ oscillates with stable amplitude
  - Chaos: two nearby initial conditions diverge exponentially
  - Transient: not enough data to classify yet

No AI. No guessing. Pure trajectory math.
"""
import numpy as np
from engine.state import State
from engine.physics import run as physics_run


def _tail_variance(values, tail_fraction=0.3):
    n = max(1, int(len(values) * tail_fraction))
    tail = values[-n:]
    mean = sum(tail) / len(tail)
    return sum((v - mean) ** 2 for v in tail) / len(tail)


def _tail_mean(values, tail_fraction=0.3):
    n = max(1, int(len(values) * tail_fraction))
    tail = values[-n:]
    return sum(tail) / len(tail)


def detect_attractor(history, fixed_point_threshold=0.002, cycle_threshold=0.05):
    """Classify attractor type from a psi time series history."""
    if len(history) < 10:
        return "transient"

    psi = [h["psi"] for h in history]
    tail_var = _tail_variance(psi)

    if tail_var < fixed_point_threshold:
        return "fixed_point"

    if tail_var < cycle_threshold:
        crossings = sum(
            1 for i in range(1, len(psi))
            if (psi[i] - _tail_mean(psi)) * (psi[i-1] - _tail_mean(psi)) < 0
        )
        if crossings >= 4:
            return "limit_cycle"

    if tail_var > 0.2:
        return "chaotic"

    return "complex"


def lyapunov_estimate(state, steps=30, perturbation=1e-5,
                      alpha=0.1, beta=0.05, gamma=0.1):
    """
    Estimate Lyapunov exponent by running two nearby trajectories.
    Positive → chaos. Near zero → limit cycle. Negative → fixed point.
    """
    import copy

    s1 = State(nx=state.nx, ny=state.ny)
    s1.phi = state.phi.copy()
    s1.C = state.C.copy()

    s2 = State(nx=state.nx, ny=state.ny)
    s2.phi = state.phi.copy() + perturbation
    s2.C = state.C.copy()

    exponents = []
    d0 = perturbation * (state.nx * state.ny) ** 0.5

    for _ in range(steps):
        try:
            from engine.physics import step as physics_step
            physics_step(s1, alpha=alpha, beta=beta, gamma=gamma)
            physics_step(s2, alpha=alpha, beta=beta, gamma=gamma)
            d1 = float(np.sqrt(np.mean((s1.psi - s2.psi) ** 2)))
            if d1 > 1e-12 and d0 > 1e-12:
                exponents.append(np.log(d1 / d0))
                d0 = d1
                s2.phi = s1.phi + (s2.phi - s1.phi) * (perturbation / max(d1, 1e-12))
        except Exception:
            break

    if not exponents:
        return 0.0
    return float(np.mean(exponents))


def attractor_report(state, steps=40, alpha=0.1, beta=0.05, gamma=0.1):
    """Full attractor analysis: run trajectory, classify, estimate Lyapunov."""
    s = State(nx=state.nx, ny=state.ny)
    s.phi = state.phi.copy()
    s.C = state.C.copy()

    history = physics_run(s, steps=steps, alpha=alpha, beta=beta, gamma=gamma)
    attractor_type = detect_attractor(history)

    lyap = 0.0
    try:
        lyap = lyapunov_estimate(state, steps=min(steps, 20),
                                  alpha=alpha, beta=beta, gamma=gamma)
    except Exception:
        pass

    psi_vals = [h["psi"] for h in history]
    return {
        "attractor": attractor_type,
        "lyapunov": round(lyap, 6),
        "final_psi": round(psi_vals[-1], 4) if psi_vals else None,
        "tail_variance": round(_tail_variance(psi_vals), 6),
        "interpretation": _interpret(attractor_type, lyap),
    }


def _interpret(attractor_type, lyap):
    if attractor_type == "fixed_point":
        return "system converges to equilibrium — fully predictable"
    if attractor_type == "limit_cycle":
        return "system oscillates with stable rhythm — periodic behavior"
    if attractor_type == "chaotic" or lyap > 0.1:
        return "sensitive dependence on initial conditions — unpredictable long-term"
    if attractor_type == "complex":
        return "complex dynamics — may require longer observation"
    return "insufficient data"
