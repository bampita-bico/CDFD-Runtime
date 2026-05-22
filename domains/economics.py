from domains.base import DomainAdapter


class EconomicsAdapter(DomainAdapter):
    def map_to_engine(self, economy):
        phi = economy.get("capital_flow", 1.0)
        C = economy.get("transaction_friction", 1.0)
        return max(phi, 0.01), max(C, 0.01)

    def interpret(self, state):
        psi = state.mean_psi()
        if psi > 1.2:
            return "high market efficiency — low friction"
        if psi < 0.8:
            return "market inefficiency — friction dominates"
        return "balanced market"
