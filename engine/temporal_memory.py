"""Level 10 — Temporal Memory.

The system remembers its own Ψ trajectory and uses that history to
modulate current dynamics — constraint hysteresis, flow memory, fatigue.

Biological analogue: epigenetic memory, immune priming.
Physical analogue: hysteresis in magnetic materials.
Social analogue: institutional memory, trauma.
"""
import numpy as np
from collections import deque


class TemporalMemory:
    def __init__(self, window=50, decay=0.95):
        self.window = window
        self.decay = decay
        self._psi_history = deque(maxlen=window)
        self._phi_history = deque(maxlen=window)
        self._C_history = deque(maxlen=window)

    def record(self, state):
        self._psi_history.append(float(np.mean(state.psi)))
        self._phi_history.append(float(np.mean(state.phi)))
        self._C_history.append(float(np.mean(state.C)))

    def mean_remembered_psi(self):
        if not self._psi_history:
            return 1.0
        weights = [self.decay ** i for i in range(len(self._psi_history) - 1, -1, -1)]
        total_w = sum(weights)
        return sum(p * w for p, w in zip(self._psi_history, weights)) / total_w

    def fatigue(self):
        """How long has the system been under stress (Ψ < 0.8)?"""
        if not self._psi_history:
            return 0.0
        stress_steps = sum(1 for p in self._psi_history if p < 0.8)
        return stress_steps / len(self._psi_history)

    def overload_exposure(self):
        """Fraction of history spent in overload (Ψ > 1.2)."""
        if not self._psi_history:
            return 0.0
        return sum(1 for p in self._psi_history if p > 1.2) / len(self._psi_history)

    def apply(self, state):
        """Modulate current state based on remembered history."""
        try:
            remembered_psi = self.mean_remembered_psi()
            fatigue_level = self.fatigue()
            overload_level = self.overload_exposure()

            # Fatigue: prolonged stress hardens constraints (scar tissue)
            if fatigue_level > 0.4:
                hardening = 1.0 + 0.002 * fatigue_level
                state.C *= hardening
                state.C = np.clip(state.C, 1e-9, 1e6)

            # Overload memory: system anticipates excess by pre-constraining
            if overload_level > 0.3:
                state.C += 0.001 * overload_level

            # Recovery priming: if history was bad but now Ψ recovering,
            # boost phi slightly (immune-like rebound)
            current_psi = float(np.mean(state.psi))
            if remembered_psi < 0.7 and current_psi > remembered_psi:
                recovery_boost = 0.001 * (current_psi - remembered_psi)
                state.phi += recovery_boost

        except Exception:
            pass

    def trend(self):
        if len(self._psi_history) < 2:
            return "unknown"
        recent = list(self._psi_history)[-10:]
        slope = (recent[-1] - recent[0]) / len(recent)
        if slope > 0.01:
            return "improving"
        if slope < -0.01:
            return "declining"
        return "stable"

    def summary(self):
        return {
            "remembered_psi": self.mean_remembered_psi(),
            "fatigue": self.fatigue(),
            "overload_exposure": self.overload_exposure(),
            "trend": self.trend(),
            "memory_depth": len(self._psi_history),
        }
