from domains.base import DomainAdapter
class PrehistoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        pop_density = data.get("population_density_norm", 0.3)
        tool_complex= data.get("tool_complexity_norm", 0.4)
        resources   = data.get("resource_abundance", 0.5)
        climate_str = data.get("climate_stress", 0.3)
        predation   = data.get("predation_pressure", 0.2)
        phi = max(pop_density*0.4 + tool_complex*0.3 + resources*0.3, 0.01)
        C   = max(climate_str*0.5 + predation*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Population collapse — resource failure or climate catastrophe"
        if psi < 0.6:  return "Survival struggle — technology minimal, population fragmented"
        if psi <= 1.2: return "Stable prehistoric band — technology and resources in balance"
        return "Flourishing — population growth, tool innovation, surplus"
