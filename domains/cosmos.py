from domains.base import DomainAdapter


class CosmosAdapter(DomainAdapter):
    def map_to_engine(self, cosmos):
        phi = cosmos.get("inflow", 1.0)
        C = cosmos.get("spacetime_resistance", 1.0)
        return max(phi, 0.01), max(C, 0.01)

    def interpret(self, state):
        psi = state.mean_psi()
        if psi > 1.5:
            return "expansion accelerating — low spacetime resistance"
        if psi < 0.5:
            return "collapse — constraint dominates inflow"
        return "expansion equilibrium"
