from domains.base import DomainAdapter

class EmpireAdapter(DomainAdapter):
    def map_to_engine(self, data):
        territory         = data.get("territory_km2_millions", 1.0)
        gdp_index         = data.get("gdp_index", 0.5)
        cohesion          = data.get("social_cohesion", 0.6)
        fragmentation     = data.get("fragmentation_index", 0.3)
        overextension     = data.get("overextension", 0.2)
        external_pressure = data.get("external_pressure", 0.2)
        phi = max(min(territory/5.0,1.0)*0.3 + gdp_index*0.4 + cohesion*0.3, 0.01)
        C   = max(fragmentation*0.4 + overextension*0.3 + external_pressure*0.3, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Collapse imminent — empire fragmenting under its own weight"
        if psi < 0.6:  return "Imperial decline — territory contracting, cohesion failing"
        if psi <= 1.2: return "Stable empire — balanced expansion and internal order"
        return "Peak expansion — hegemonic dominance, watch for overextension"
