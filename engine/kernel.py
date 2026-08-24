"""Orchestrator for the slim CDFD Runtime physics kernel."""
from __future__ import annotations

import json
import logging
import time

import numpy as np

from engine.config import DEFAULT_DT, LOG_FAILURES
from engine.physics import step as apply_physics, update_psi

logger = logging.getLogger(__name__)


class Kernel:
    def __init__(
        self,
        dt: float = DEFAULT_DT,
        *,
        use_self_regulation: bool = False,
        use_temporal_memory: bool = False,
        use_coherence: bool = False,
        use_vpt_detector: bool = False,
        regulation_params=None,
        memory_window: int = 50,
    ) -> None:
        self.dt = dt
        self.telemetry: dict[str, float] = {}
        self.use_self_regulation = use_self_regulation
        self.use_temporal_memory = use_temporal_memory
        self.use_coherence = use_coherence
        self.use_vpt_detector = use_vpt_detector

        self._coherence = None
        if use_coherence:
            from engine.coherence import CoherenceField

            self._coherence = CoherenceField(32, 32)

        self._vpt_detector = None
        if use_vpt_detector:
            from engine.quantum_vacuum import VacuumPhaseDetector

            self._vpt_detector = VacuumPhaseDetector()

        self._regulator = None
        if use_self_regulation:
            from engine.self_regulation import RegulationParams, SelfRegulator

            params = regulation_params or RegulationParams(
                alpha=DEFAULT_DT * 10,
                beta=DEFAULT_DT * 5,
                gamma=DEFAULT_DT * 10,
            )
            self._regulator = SelfRegulator(params)

        self._memory = None
        if use_temporal_memory:
            from engine.temporal_memory import TemporalMemory

            self._memory = TemporalMemory(window=memory_window)

    def save_checkpoint(self, state, filepath) -> None:
        state.save_h5(filepath)
        logger.info(json.dumps({"event": "checkpoint_saved", "filepath": filepath, "t": state.t}))

    def load_checkpoint(self, filepath):
        from engine.state import State

        state = State.load_h5(filepath)
        logger.info(json.dumps({"event": "checkpoint_loaded", "filepath": filepath, "t": state.t}))
        self.log_telemetry(state)
        state.meta["checkpoint_loaded"] = filepath
        return state

    def log_telemetry(self, state) -> None:
        log_record = {
            "event": "step_complete",
            "t": state.t,
            "mean_psi": state.mean_psi(),
            "telemetry_ms": self.telemetry,
        }
        logger.info(json.dumps(log_record))

    def run_cycle(self, state):
        active_constraints: list[str] = []
        status = "ok"

        try:
            t0 = time.perf_counter()
            apply_physics(state, dt=self.dt)
            self.telemetry["physics"] = (time.perf_counter() - t0) * 1000
        except Exception as exc:
            status = "physics_error"
            if LOG_FAILURES:
                logger.warning("physics update failed: %s", exc)

        try:
            update_psi(state)
        except Exception as exc:
            if LOG_FAILURES:
                logger.warning("psi synchronization failed: %s", exc)

        if self.use_temporal_memory and self._memory is not None:
            try:
                self._memory.record(state)
                self._memory.apply(state)
                update_psi(state)
                active_constraints.append("temporal_memory")
            except Exception as exc:
                if LOG_FAILURES:
                    logger.warning("temporal_memory failed: %s", exc)

        if self.use_self_regulation and self._regulator is not None:
            try:
                self._regulator.regulate(state)
                active_constraints.append("self_regulation")
            except Exception as exc:
                if LOG_FAILURES:
                    logger.warning("self_regulation failed: %s", exc)

        if self._coherence is not None:
            try:
                nx, ny = state.phi.shape
                if self._coherence.Omega.shape != (nx, ny):
                    from engine.coherence import CoherenceField

                    self._coherence = CoherenceField(nx, ny)
                self._coherence.update(state, self.dt)
                if isinstance(state.meta, dict):
                    state.meta["coherence"] = self._coherence.mean_coherence()
                    state.meta["coherence_efficiency"] = self._coherence.coherence_efficiency(state)
                active_constraints.append("coherence")
            except Exception as exc:
                if LOG_FAILURES:
                    logger.warning("coherence update failed: %s", exc)

        if self._vpt_detector is not None:
            try:
                vpt_triggered = self._vpt_detector.check(state)
                si = self._vpt_detector.stability_index(state)
                if isinstance(state.meta, dict):
                    state.meta["stability_index"] = si
                    state.meta["vpt_triggered"] = vpt_triggered
                if vpt_triggered:
                    active_constraints.append("vpt")
            except Exception as exc:
                if LOG_FAILURES:
                    logger.warning("vpt detector failed: %s", exc)

        try:
            update_psi(state)
        except Exception as exc:
            if LOG_FAILURES:
                logger.warning("final psi synchronization failed: %s", exc)

        memory_summary = self._memory.summary() if self._memory else None
        regulation_status = self._regulator.status(state) if self._regulator else None

        return {
            "state": state,
            "equilibrium_psi_s": state.mean_psi(),
            "status": status,
            "active_constraints": active_constraints,
            "memory": memory_summary,
            "regulation": regulation_status,
        }

    def run(self, state, steps: int):
        history = []
        for _ in range(steps):
            try:
                result = self.run_cycle(state)
                psi_s = result["equilibrium_psi_s"]
                history.append(
                    {
                        "t": float(state.t),
                        "psi": psi_s,
                        "psi_s": psi_s,
                        "phi": float(np.mean(state.phi)),
                        "C": float(np.mean(state.C)),
                        "S": float(np.mean(state.S)),
                        "Ms": float(np.mean(state.Ms)),
                        "regime": state.regime(),
                        "status": result["status"],
                    }
                )
            except Exception:
                continue
        return history
