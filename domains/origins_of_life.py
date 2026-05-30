"""Origins-of-life / tri-regime domain adapter (OOL series + plants sketch)."""

from typing import Any

from domains.base import DomainAdapter
from runtime.diagnostics import (
    LIFE_NUMBER_SUPPLY_GUARDRAIL,
    AROMATIC_SOURCE_SCENARIOS,
    aromatic_source_mix_row,
    aromatic_source_mix_scenario,
    photochemical_material_status,
)


class OriginsOfLifeAdapter(DomainAdapter):
    """
    Maps coarse scalar knobs to Φ/Lambda (C == Lambda), then interprets via Ψ and tri-regime Λ
    (engine.origins_of_life) after the demo physics step.
    """

    _DIRECT_SOURCE_KEYS = (
        "terrestrial_feedstock",
        "exogenous_feedstock",
        "retention_factor",
        "coupling_factor",
        "damage_load",
        "aromatic_terrestrial_feedstock",
        "aromatic_exogenous_feedstock",
        "aromatic_retention_factor",
        "aromatic_coupling_factor",
        "aromatic_damage_load",
    )

    def __init__(self):
        self._runtime_diagnostics = self._base_diagnostics()

    def _base_diagnostics(self) -> dict[str, Any]:
        return {
            "life_number_guardrail": LIFE_NUMBER_SUPPLY_GUARDRAIL,
            "photochemical_material_status": photochemical_material_status(),
            "available_source_scenarios": [row[0] for row in AROMATIC_SOURCE_SCENARIOS],
        }

    @staticmethod
    def _first_float(data: dict[str, Any], *names: str, default: float) -> float:
        for name in names:
            if name in data:
                return float(data[name])
        return default

    def _source_mix_from_payload(self, data: dict[str, Any]) -> dict[str, Any] | None:
        scenario = data.get("source_scenario") or data.get("aromatic_source_scenario")
        if scenario:
            return aromatic_source_mix_scenario(str(scenario))
        if not any(key in data for key in self._DIRECT_SOURCE_KEYS):
            return None
        return aromatic_source_mix_row(
            str(data.get("source_label", data.get("aromatic_source_label", "payload_source_mix"))),
            self._first_float(data, "terrestrial_feedstock", "aromatic_terrestrial_feedstock", default=1.0),
            self._first_float(data, "exogenous_feedstock", "aromatic_exogenous_feedstock", default=0.0),
            self._first_float(data, "retention_factor", "aromatic_retention_factor", default=0.6),
            self._first_float(data, "coupling_factor", "aromatic_coupling_factor", default=0.7),
            self._first_float(data, "damage_load", "aromatic_damage_load", default=0.4),
            str(data.get("source_interpretation", data.get("aromatic_source_interpretation", "payload source mix"))),
        )

    def map_to_engine(self, data):
        energy_capture = float(data.get("energy_capture", 1.0))  # chlorophyll-like input
        mineral_resistance = float(data.get("mineral_resistance", 1.0))  # Fe-S / pore / bulk Lambda
        source_mix = self._source_mix_from_payload(data)
        self._runtime_diagnostics = self._base_diagnostics()
        if source_mix is not None:
            self._runtime_diagnostics["aromatic_source_mix"] = source_mix

        source_gain = 0.0 if source_mix is None else float(source_mix["functional_score"])
        phi = max(0.05, energy_capture * 1.1 + source_gain)
        c = max(0.05, mineral_resistance)
        return phi, c

    def runtime_diagnostics(self) -> dict[str, Any]:
        return dict(self._runtime_diagnostics)

    def interpret(self, state):
        from engine.origins_of_life import compute_life_number

        lam = compute_life_number(state)
        psi = state.mean_psi()
        if lam < 0.95:
            life = "Λ < 1 — sub-critical life-number readout on this grid"
        elif lam <= 1.15:
            life = "Λ ≈ 1 — marginal proto-biological window"
        else:
            life = "Λ > 1 — sustained throughput readout (model-dependent)"

        if psi < 0.8:
            flux = "low Ψ — flux starved relative to Lambda (C == Lambda)"
        elif psi <= 1.2:
            flux = "Ψ near unity — balanced transport"
        else:
            flux = "high Ψ — overload / surge-prone regime"

        parts = [life, flux]
        source_mix = self._runtime_diagnostics.get("aromatic_source_mix")
        if source_mix:
            parts.append(
                "aromatic source mix "
                f"{source_mix['scenario']} score={float(source_mix['functional_score']):.3f}"
            )
        parts.append("eumelanin is a mature stabilization endpoint, not an origin requirement")
        return "; ".join(parts) + " (tri-regime scalars in state.meta: ool_*)"
