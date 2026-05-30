"""Domain-neutral operating-state guidance for CDFL runtime output."""
from __future__ import annotations

from typing import Any


def _reason_with_meta(reason: str, meta: dict[str, Any]) -> str:
    parts = [reason]
    if "high_flux_biomarkers" in meta:
        parts.append(f"High flux drivers: {meta['high_flux_biomarkers']}.")
    if "high_constraint_biomarkers" in meta:
        parts.append(f"Elevated constraints: {meta['high_constraint_biomarkers']}.")
    if "life_number" in meta:
        lam = float(meta["life_number"])
        if lam > 1.0:
            band = "sustained"
        elif lam >= 0.8:
            band = "near-critical"
        else:
            band = "subcritical"
        parts.append(f"Life Number Lambda={lam:.3f} ({band}).")
    return " ".join(parts)


def classify_operating_state(
    psi: float,
    meta: dict[str, Any] | None = None,
    domain: str = "generic",
) -> dict[str, Any]:
    """Map Psi to neutral model-guidance labels without deployment directives."""
    meta = meta or {}
    if psi > 1.5:
        state = "critical_overload"
        actions = ["reduce_model_flux", "increase_constraint_capacity", "mark_for_review"]
        reason = f"Psi={psi:.3f} is far above the overload band (>1.5)."
    elif psi > 1.2:
        state = "overloaded"
        actions = ["reduce_model_flux", "inspect_constraint_capacity", "rerun_with_controls"]
        reason = f"Psi={psi:.3f} is above the overload threshold (1.2)."
    elif psi >= 0.8:
        state = "balanced"
        actions = ["keep_parameters", "continue_monitoring"]
        reason = f"Psi={psi:.3f} is inside the balanced band [0.8, 1.2]."
    elif psi >= 0.5:
        state = "constrained"
        actions = ["inspect_low_flux", "inspect_constraint_load", "rerun_with_controls"]
        reason = f"Psi={psi:.3f} is below the balanced band (<0.8)."
    else:
        state = "critical_constraint"
        actions = ["inspect_low_flux_state", "relax_excess_constraint", "mark_for_review"]
        reason = f"Psi={psi:.3f} is critically low (<0.5)."

    return {
        "psi": psi,
        "state": state,
        "actions": actions,
        "reason": _reason_with_meta(reason, meta),
        "domain": domain,
        "life_number": meta.get("life_number"),
    }
