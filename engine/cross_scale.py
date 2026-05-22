"""Level 9 — Cross-Scale Coupling.

Connects states at different spatial scales using the same Φ/C/Ψ equations.
Upward: micro mean feeds macro source term.
Downward: macro Ψ modulates micro constraint.

Examples:
  cell → tissue → organ → body
  particle → atom → molecule → bulk
  individual → community → civilization
"""
import numpy as np
from engine.state import State


class ScaleLevel:
    def __init__(self, name, state, scale_factor=1.0):
        self.name = name
        self.state = state
        self.scale_factor = scale_factor


class CrossScaleCoupler:
    """Manages a stack of scale levels and propagates flow between them."""

    def __init__(self, upward_strength=0.05, downward_strength=0.03):
        self.levels = []
        self.upward = upward_strength
        self.downward = downward_strength

    def add_level(self, name, state, scale_factor=1.0):
        self.levels.append(ScaleLevel(name, state, scale_factor))

    def couple(self):
        """One full coupling pass — upward then downward."""
        if len(self.levels) < 2:
            return
        self._propagate_up()
        self._propagate_down()

    def _propagate_up(self):
        for i in range(len(self.levels) - 1):
            micro = self.levels[i].state
            macro = self.levels[i + 1].state
            # Mean micro Ψ acts as a source boost in macro phi
            signal = float(np.mean(micro.psi)) * self.upward
            macro.phi += signal * micro.scale_factor if hasattr(micro, "scale_factor") else signal

    def _propagate_down(self):
        for i in range(len(self.levels) - 1, 0, -1):
            macro = self.levels[i].state
            micro = self.levels[i - 1].state
            # Macro constraint pressure modulates micro C
            pressure = float(np.mean(macro.C)) * self.downward
            micro.C += pressure
            micro.C = np.clip(micro.C, 1e-9, 1e6)

    def summary(self):
        return [
            {
                "level": lvl.name,
                "mean_phi": float(np.mean(lvl.state.phi)),
                "mean_C": float(np.mean(lvl.state.C)),
                "mean_psi": float(np.mean(lvl.state.psi)),
            }
            for lvl in self.levels
        ]


def build_scale_stack(names, nx=8, ny=8, upward=0.05, downward=0.03):
    """Convenience: build a stack of uniform-sized scale levels."""
    coupler = CrossScaleCoupler(upward_strength=upward, downward_strength=downward)
    for i, name in enumerate(names):
        state = State(nx=nx, ny=ny)
        coupler.add_level(name, state, scale_factor=10.0 ** i)
    return coupler
