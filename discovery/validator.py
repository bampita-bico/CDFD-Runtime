def validate(hypothesis_text, knowledge, n_new=10, nx=8, ny=8, steps=30):
    from discovery.generator import generate_experiments, run_experiments
    from discovery.detector import detect_pattern
    from discovery.features import extract_features

    experiments = generate_experiments(steps=steps, nx=nx, ny=ny)[:n_new]
    results = run_experiments(experiments)

    consistent = 0
    total = 0
    for res in results:
        if res["error"] or not res["history"]:
            continue
        features = extract_features(res["history"])
        if _check_consistency(hypothesis_text, features):
            consistent += 1
        total += 1

    if total == 0:
        return {"consistent": False, "ratio": 0.0, "reason": "no data"}

    ratio = consistent / total
    return {
        "consistent": ratio > 0.6,
        "ratio": ratio,
        "consistent_count": consistent,
        "total": total,
    }


def check_consistency(results, expected_pattern=None):
    if expected_pattern is None:
        return True
    from discovery.detector import detect_pattern
    patterns = [detect_pattern(r.get("history", [])) for r in results if not r.get("error")]
    if not patterns:
        return False
    dominant = max(set(patterns), key=patterns.count)
    return dominant == expected_pattern


def _check_consistency(hypothesis_text, features):
    if "Collapse" in hypothesis_text and "below" in hypothesis_text:
        try:
            threshold = float(hypothesis_text.split("below")[-1].strip())
            return features.get("mean_psi", 1.0) >= threshold
        except ValueError:
            pass
    return True
