def generate_experiments(
    alphas=(0.1, 0.5, 1.0),
    betas=(0.01, 0.1),
    gammas=(0.05, 0.1, 0.2),
    steps=50,
    nx=16,
    ny=16,
):
    experiments = []
    for alpha in alphas:
        for beta in betas:
            for gamma in gammas:
                experiments.append({
                    "alpha": alpha,
                    "beta": beta,
                    "gamma": gamma,
                    "steps": steps,
                    "nx": nx,
                    "ny": ny,
                })
    return experiments


def run_experiments(experiments):
    from engine.state import State
    from engine.physics import run as physics_run

    results = []
    for exp in experiments:
        try:
            state = State(nx=exp["nx"], ny=exp["ny"])
            history = physics_run(
                state,
                steps=exp["steps"],
                alpha=exp["alpha"],
                beta=exp["beta"],
                gamma=exp["gamma"],
            )
            results.append({"params": exp, "history": history, "error": None})
        except Exception as e:
            results.append({"params": exp, "history": [], "error": str(e)})
    return results
