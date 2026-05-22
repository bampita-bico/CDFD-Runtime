"""Large-scale flow dynamics — expansion, inflow, spacetime resistance."""


def apply_cosmos(state, dt=0.01, expand_rate=0.0005):
    try:
        _expand(state, expand_rate, dt)
        _inflow(state, dt)
    except Exception:
        pass


def _expand(state, rate, dt):
    state.C *= (1.0 + rate * dt)


def _inflow(state, dt):
    state.phi[0, :] += dt * 0.01
    state.phi[-1, :] += dt * 0.01
