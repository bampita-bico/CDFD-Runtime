"""Universal Φ/C/Ψ demo: map any registered domain adapter through engine.physics.step."""
import math
from typing import Any

from domains.registry import DomainRegistry
from engine.config import DEFAULT_DT
from engine.physics import step as physics_step
from engine.state import State


def run_domain_demo(
    name: str,
    payload: dict[str, Any] | None = None,
    *,
    nx: int = 16,
    ny: int = 16,
    steps: int = 24,
    dt: float | None = None,
) -> dict[str, Any]:
    registry = DomainRegistry.default()
    adapter = registry.get(name)
    if adapter is None:
        raise KeyError(f"Unknown domain {name!r}; use DomainRegistry.default().list_domains()")

    payload = payload or {}
    phi_s, c_s = adapter.map_to_engine(payload)

    state = State(nx=nx, ny=ny)
    state.phi[:] = float(phi_s)
    state.C[:] = float(c_s)
    state.psi = state.phi / state.C

    dt_eff = DEFAULT_DT if dt is None else float(dt)
    initial = {
        "mean_phi": float(math.fsum(state.phi.flat) / state.phi.size),
        "mean_C": float(math.fsum(state.C.flat) / state.C.size),
        "mean_psi": float(state.mean_psi()),
    }

    for _ in range(steps):
        physics_step(state, dt=dt_eff)

    final = {
        "mean_phi": float(math.fsum(state.phi.flat) / state.phi.size),
        "mean_C": float(math.fsum(state.C.flat) / state.C.size),
        "mean_psi": float(state.mean_psi()),
    }

    return {
        "domain": name,
        "payload_keys": sorted(payload.keys()),
        "nx": nx,
        "ny": ny,
        "steps": steps,
        "dt": dt_eff,
        "initial": initial,
        "final": final,
        "regime": state.regime(),
        "interpretation": adapter.interpret(state),
    }
