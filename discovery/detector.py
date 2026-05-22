def detect_pattern(history):
    if not history:
        return "empty"
    psi_values = [h["psi"] for h in history]
    max_psi = max(psi_values)
    min_psi = min(psi_values)
    final_psi = psi_values[-1]
    mean_psi = sum(psi_values) / len(psi_values)

    if max_psi > 2.0:
        return "unstable_growth"
    if min_psi < 0.3:
        return "collapse"
    if _is_oscillating(psi_values):
        return "oscillation"
    if final_psi > mean_psi * 1.1:
        return "growth"
    if final_psi < mean_psi * 0.9:
        return "decay"
    return "stable"


def _is_oscillating(values, min_crossings=3):
    if len(values) < 6:
        return False
    mean = sum(values) / len(values)
    crossings = 0
    above = values[0] > mean
    for v in values[1:]:
        now_above = v > mean
        if now_above != above:
            crossings += 1
            above = now_above
    return crossings >= min_crossings
