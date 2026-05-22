from domains.base import DomainAdapter

class EnergySystemsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        generation    = data.get("generation_GW", 100)
        demand        = data.get("demand_GW", 90)
        grid_losses   = data.get("grid_losses_pct", 5) / 100.0
        renewable_pct = data.get("renewable_fraction", 0.3)
        phi = max(min(generation/demand,2.0) * 0.4 + renewable_pct * 0.4 +
                  (1.0-grid_losses) * 0.2, 0.01)
        C   = max(grid_losses * 0.5 + max(demand/generation - 1.0, 0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Blackout risk — critical grid instability"
        if psi < 0.6:  return "Energy deficit — demand exceeds reliable supply"
        if psi <= 1.2: return "Grid in balance — energy security maintained"
        return "Energy surplus — storage and export opportunity"
