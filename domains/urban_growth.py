from domains.base import DomainAdapter

class UrbanGrowthAdapter(DomainAdapter):
    def map_to_engine(self, data):
        pop_growth   = data.get("population_growth_pct", 2.0)
        investment   = data.get("investment_index", 0.5)
        connectivity = data.get("connectivity_index", 0.5)
        infra_deficit= data.get("infrastructure_deficit", 0.3)
        inequality   = data.get("gini_coefficient", 0.4)
        phi = max(min(pop_growth/10.0,1.0)*0.3 + investment*0.4 + connectivity*0.3, 0.01)
        C   = max(infra_deficit*0.5 + inequality*0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "City in decline — population leaving, investment dried up"
        if psi < 0.6:  return "Urban stagnation — growth blocked by infrastructure and inequality"
        if psi <= 1.2: return "Steady urban growth — this city will develop further"
        return "Urban boom — next major city, investment and population surging"
