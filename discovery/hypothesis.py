def generate_hypothesis(knowledge):
    hypotheses = []
    collapse_records = knowledge.query("collapse")
    if collapse_records:
        threshold = _mean_feature(collapse_records, "mean_psi")
        hypotheses.append(
            f"Collapse occurs when mean Ψ falls below {threshold:.3f}"
        )

    growth_records = knowledge.query("unstable_growth")
    if growth_records:
        threshold = _mean_feature(growth_records, "mean_psi")
        hypotheses.append(
            f"Unstable growth occurs when mean Ψ exceeds {threshold:.3f}"
        )

    stable_records = knowledge.query("stable")
    if stable_records:
        mean_alpha = _mean_param(stable_records, "alpha")
        mean_beta = _mean_param(stable_records, "beta")
        hypotheses.append(
            f"Stability favored when alpha/beta ratio ≈ {mean_alpha/mean_beta:.2f}"
            if mean_beta > 0 else "Stability requires non-zero beta"
        )

    return hypotheses


def _mean_feature(records, key):
    vals = [r["features"].get(key, 0) for r in records if key in r["features"]]
    return sum(vals) / len(vals) if vals else 0.0


def _mean_param(records, key):
    vals = [r["params"].get(key, 0) for r in records if key in r["params"]]
    return sum(vals) / len(vals) if vals else 0.0
