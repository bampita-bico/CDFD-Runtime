def extract_features(history):
    if not history:
        return {}
    psi = [h.get("psi", h.get("psi_s")) for h in history]
    if any(p is None for p in psi):
        raise KeyError("history rows must include 'psi' or 'psi_s'")
    n = len(psi)
    mean_p = sum(psi) / n
    variance = sum((p - mean_p) ** 2 for p in psi) / n
    growth_rate = (psi[-1] - psi[0]) / max(n - 1, 1)

    time_to_collapse = None
    for i, p in enumerate(psi):
        if p < 0.3:
            time_to_collapse = i
            break

    return {
        "mean_psi": mean_p,
        "max_psi": max(psi),
        "min_psi": min(psi),
        "variance": variance,
        "growth_rate": growth_rate,
        "final_psi": psi[-1],
        "time_to_collapse": time_to_collapse,
        "n_steps": n,
    }


def extract_features_numeric(history):
    """Same as extract_features but every value is float (for ML / DataFrame columns)."""
    d = extract_features(history)
    if not d:
        return {}
    out = dict(d)
    if out.get("time_to_collapse") is None:
        out["time_to_collapse"] = float(out["n_steps"])
    return {k: float(v) for k, v in out.items()}
