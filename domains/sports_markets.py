"""
======================================================================
CDFD UNIVERSAL ENGINE — Sports Markets Domain
Φ = sharp-money flow | C = bookmaker implied constraint
======================================================================
"""
from domains.base import DomainAdapter


class SportsMarketsAdapter(DomainAdapter):
    """
    Maps live market observations into engine Φ/C fields.

    Expected payload keys (from GhostSport observation ingest):
      phi_flow, implied_prob, tier, metabolic_edge, structural_capacity
    """

    _TIER_S = {"TIER_1": 1.0, "TIER_2": 0.7, "TIER_3": 0.4}

    def map_to_engine(self, data: dict) -> tuple[float, float]:
        phi_flow = float(data.get("phi_flow", data.get("phi", 0.0)))
        implied = float(data.get("implied_prob", data.get("c", 0.5)))
        tier = data.get("tier", "TIER_2")
        s_cap = float(data.get("structural_capacity", self._TIER_S.get(tier, 0.5)))
        ms = float(data.get("metabolic_edge", data.get("ms", 0.0)))

        # Φ: scale probability flow into engine intensity units
        phi = max(phi_flow * 50.0 + ms * 5.0, 0.01)
        # C: book constraint wall (implied probability, liquidity-weighted)
        C = max(implied * (2.0 - 0.3 * s_cap), 0.01)
        self._last = {"phi_flow": phi_flow, "implied": implied, "S": s_cap, "Ms": ms}
        return phi, C

    def interpret(self, state) -> str:
        psi = state.mean_psi()
        last = getattr(self, "_last", {})
        if psi > 1.2:
            return "market overload — steam overshoot (Ψ>1.2)"
        if psi < 0.8:
            return "market constrained — flow blocked by book wall (Ψ<0.8)"
        if last.get("phi_flow", 0) > 0 and last.get("Ms", 0) > 0:
            return "sharp inflow with positive edge — equilibrium band"
        return "near-efficient market equilibrium"
