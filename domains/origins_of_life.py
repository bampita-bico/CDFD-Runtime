"""Origins-of-life / tri-regime domain adapter (OOL series + plants sketch)."""

from domains.base import DomainAdapter


class OriginsOfLifeAdapter(DomainAdapter):
    """
    Maps coarse scalar knobs to Φ/Lambda (C == Lambda), then interprets via Ψ and tri-regime Λ
    (engine.origins_of_life) after the demo physics step.
    """

    def map_to_engine(self, data):
        energy_capture = float(data.get("energy_capture", 1.0))  # chlorophyll-like input
        mineral_resistance = float(data.get("mineral_resistance", 1.0))  # Fe-S / pore / bulk Lambda
        phi = max(0.05, energy_capture * 1.1)
        c = max(0.05, mineral_resistance)
        return phi, c

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

        return f"{life}; {flux} (tri-regime scalars in state.meta: ool_*)"
