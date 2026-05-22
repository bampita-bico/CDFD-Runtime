"""Shared CDFD Runtime diagnostics and JSON-safe result helpers.

This module centralizes helpers that had drifted into paper-local release
scripts. The CLI and later web app can use this layer without depending on
manuscript folders.
"""
from __future__ import annotations

import csv
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np


EPS = 1e-12
VALUE_FLOOR = 1e-9
VALUE_CAP = 1e4
PSI_CAP = 1e4


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def runtime_provenance(command: str | None = None) -> dict[str, Any]:
    return {
        "runtime": "CDFD Runtime",
        "language": "CDFL",
        "timestamp_utc": utc_timestamp(),
        "command": command,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def clean_json(value: Any) -> Any:
    """Convert runtime values into strict JSON-safe values."""
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return clean_json(value.tolist())
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        v = float(value)
        return v if math.isfinite(v) else None
    return value


def bounded_float(value: Any, low: float = 0.0, high: float = VALUE_CAP) -> float:
    """Return a finite scalar clipped to a declared diagnostic range."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return low
    if not math.isfinite(v):
        return high if v > 0 else low
    return float(np.clip(v, low, high))


def finite_stats(values: Any) -> dict[str, float | bool | int]:
    """Compact finite-value audit for scalars, lists, and arrays."""
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return {
            "all_finite": False,
            "count": int(arr.size),
            "finite_count": 0,
            "min": float("nan"),
            "max": float("nan"),
            "mean": float("nan"),
        }
    return {
        "all_finite": bool(finite.size == arr.size),
        "count": int(arr.size),
        "finite_count": int(finite.size),
        "min": float(np.min(finite)),
        "max": float(np.max(finite)),
        "mean": float(np.mean(finite)),
    }


def finite_audit(value: Any, path: str = "$") -> dict[str, Any]:
    """Recursively report non-finite numeric leaves in a result payload."""
    failures: list[str] = []

    def walk(obj: Any, obj_path: str) -> None:
        if isinstance(obj, dict):
            for key, item in obj.items():
                walk(item, f"{obj_path}.{key}")
            return
        if isinstance(obj, (list, tuple)):
            for idx, item in enumerate(obj):
                walk(item, f"{obj_path}[{idx}]")
            return
        if isinstance(obj, np.ndarray):
            arr = np.asarray(obj, dtype=float)
            if not bool(np.all(np.isfinite(arr))):
                failures.append(obj_path)
            return
        if isinstance(obj, (np.integer, int, np.floating, float)):
            try:
                if not math.isfinite(float(obj)):
                    failures.append(obj_path)
            except (TypeError, ValueError):
                pass

    walk(value, path)
    return {
        "all_finite": len(failures) == 0,
        "non_finite_paths": failures,
    }


def laplacian_2d(z: np.ndarray) -> np.ndarray:
    """Periodic five-point Laplacian used by CDFD toy diagnostics."""
    return (
        -4.0 * z
        + np.roll(z, 1, 0)
        + np.roll(z, -1, 0)
        + np.roll(z, 1, 1)
        + np.roll(z, -1, 1)
    )


def adaptive_ratio(
    phi: np.ndarray | float,
    constraint: np.ndarray | float,
    S: np.ndarray | float = 1.0,
    M_s: np.ndarray | float = 1.0,
) -> np.ndarray:
    """CDFL adaptive operating ratio Psi_s = (Phi / C) S M_s."""
    phi_arr = np.asarray(phi, dtype=float)
    c_arr = np.asarray(constraint, dtype=float)
    safe_constraint = np.maximum(np.abs(c_arr), EPS)
    return (phi_arr / safe_constraint) * S * M_s


def operating_ratio(phi: float, c: float, s: float = 1.0, m_s: float = 1.0) -> float:
    """Bounded scalar form of Psi_s for CLI diagnostics and paper examples."""
    phi_b = bounded_float(phi)
    c_b = bounded_float(c, low=VALUE_FLOOR)
    s_b = bounded_float(s)
    ms_b = bounded_float(m_s)
    return bounded_float((phi_b / max(c_b, VALUE_FLOOR)) * s_b * ms_b, high=PSI_CAP)


def life_number(
    input_energy: float,
    sigma_e: float,
    sigma_p: float,
    tau_relax: float,
    stabilization: float,
    maintenance_energy: float = 1.0,
    S: float = 1.0,
    M_s: float = 1.0,
) -> float:
    """Tri-regime Life Number used by the Part II and biology releases."""
    denominator = max(stabilization * maintenance_energy, EPS)
    return float((input_energy * sigma_e * sigma_p * tau_relax / denominator) * S * M_s)


def regime_label(psi: float, low: float = 0.8, high: float = 1.2) -> str:
    if not math.isfinite(float(psi)):
        return "non_finite"
    if psi < low:
        return "constrained"
    if psi > high:
        return "overload"
    return "balanced"


def life_regime(value: float, low: float = 1.0, high: float = 2.0) -> str:
    if not math.isfinite(float(value)):
        return "non_finite"
    if value < low:
        return "decay_dominated"
    if value < high:
        return "near_critical"
    return "sustained"


def bounded_adaptive_update(
    phi: np.ndarray,
    constraint: np.ndarray,
    S: np.ndarray,
    M_s: np.ndarray,
    dt: float,
    kappa_s: float,
    memory_decay: float,
    max_state: float = 100.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Apply bounded CDFL S/M_s updates for explicit toy models."""
    psi = adaptive_ratio(phi, constraint, S, M_s)
    dM_s = np.clip(phi * S - memory_decay * M_s, -max_state, max_state)
    M_s = np.clip(M_s + dt * dM_s, 0.0, max_state)
    dS = np.clip(kappa_s * (psi - S), -max_state, max_state)
    S = np.clip(S + dt * dS, 0.01, max_state)
    phi = np.clip(phi, 0.0, max_state)
    return phi, S, M_s


def euler_step(
    phi: float,
    c: float,
    s: float,
    m_s: float,
    alpha: float,
    beta: float,
    kappa_s: float,
    d_m: float,
    dt: float,
) -> tuple[float, float, float]:
    """Bounded scalar diagnostic step used by release-local Part III models."""
    phi_b = bounded_float(phi)
    c_b = bounded_float(c, low=VALUE_FLOOR)
    s_b = bounded_float(s, low=0.01)
    ms_b = bounded_float(m_s)
    dc = alpha * abs(phi_b) - beta * c_b
    c_new = bounded_float(c_b + dt * dc, low=VALUE_FLOOR)
    psi = operating_ratio(phi_b, c_b, s_b, ms_b)
    s_new = bounded_float(s_b + dt * kappa_s * (psi - s_b), low=0.01)
    dms = np.clip(phi_b * s_b - d_m * ms_b, -VALUE_CAP, VALUE_CAP)
    ms_new = bounded_float(ms_b + dt * dms)
    return c_new, s_new, ms_new


def state_summary(state: Any) -> dict[str, Any]:
    """JSON-safe scalar summary of a CDFD State."""
    if hasattr(state, "update_psi"):
        state.update_psi()
    return {
        "t": float(getattr(state, "t", 0.0)),
        "phi": finite_stats(getattr(state, "phi")),
        "C": finite_stats(getattr(state, "C")),
        "S": finite_stats(getattr(state, "S")),
        "M_s": finite_stats(getattr(state, "Ms")),
        "psi_s": finite_stats(getattr(state, "psi_s")),
        "regime": state.regime() if hasattr(state, "regime") else None,
        "meta": clean_json(getattr(state, "meta", {})),
    }


def result_envelope(
    kind: str,
    command: str,
    payload: Mapping[str, Any],
    *,
    status: str = "ok",
    warnings: Iterable[str] | None = None,
    errors: Iterable[str] | None = None,
) -> dict[str, Any]:
    body = clean_json(dict(payload))
    return {
        "status": status,
        "kind": kind,
        "provenance": runtime_provenance(command),
        "warnings": list(warnings or []),
        "errors": list(errors or []),
        "finite_audit": finite_audit(body),
        "payload": body,
    }


def write_json(path: str | Path, payload: Mapping[str, Any]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True, allow_nan=False) + "\n")
    return out


def write_csv(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [clean_json(dict(row)) for row in rows]
    if not rows:
        out.write_text("")
        return out
    fieldnames = list(rows[0].keys())
    with out.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return out
