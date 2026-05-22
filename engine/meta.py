"""Meta-evolution — spawn universes with varied parameters, select top performers."""
import numpy as np
from engine.state import State
from engine.physics import run as physics_run


def life_score(history):
    if not history:
        return 0.0
    psi_values = [h["psi"] for h in history]
    mean_p = sum(psi_values) / len(psi_values)
    variance = sum((p - mean_p) ** 2 for p in psi_values) / len(psi_values)
    stability = 1.0 / (1.0 + abs(mean_p - 1.0))
    complexity = float(np.tanh(variance * 10))
    return stability * (1.0 + complexity)


def mutate_params(params, scale=0.1):
    return {
        k: max(1e-6, v + np.random.normal(0, scale * abs(v) if v != 0 else scale))
        for k, v in params.items()
    }


def run_meta(count=5, generations=10, steps=50, nx=16, ny=16):
    param_keys = ["alpha", "beta", "gamma"]
    population = [
        {"alpha": np.random.uniform(0.05, 0.5),
         "beta": np.random.uniform(0.01, 0.2),
         "gamma": np.random.uniform(0.01, 0.3)}
        for _ in range(count)
    ]

    best_params = None
    best_score = -1.0

    for gen in range(generations):
        scored = []
        for params in population:
            try:
                state = State(nx=nx, ny=ny)
                history = physics_run(state, steps=steps, **params)
                score = life_score(history)
            except Exception:
                score = 0.0
            scored.append((score, params))

        scored.sort(key=lambda x: x[0], reverse=True)
        if scored[0][0] > best_score:
            best_score, best_params = scored[0]

        top_half = [p for _, p in scored[:max(1, count // 2)]]
        population = top_half + [mutate_params(p) for p in top_half]
        population = population[:count]

    return {"best_params": best_params, "best_score": best_score}
