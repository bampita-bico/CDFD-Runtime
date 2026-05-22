def correlation(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    den_y = sum((y - my) ** 2 for y in ys) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def sensitivity(knowledge, outcome_key="mean_psi"):
    records = knowledge.query()
    if not records:
        return {}

    param_keys = list(records[0]["params"].keys())
    outcomes = [r["features"].get(outcome_key, 0) for r in records]

    importance = {}
    for p in param_keys:
        param_vals = [r["params"].get(p, 0) for r in records]
        importance[p] = abs(correlation(param_vals, outcomes))

    return dict(sorted(importance.items(), key=lambda x: -x[1]))
