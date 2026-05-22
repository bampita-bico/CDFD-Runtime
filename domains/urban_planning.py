from domains.base import DomainAdapter
class UrbanPlanningAdapter(DomainAdapter):
    def map_to_engine(self, data):
        land_use     = data.get("land_use_efficiency", 0.6)
        transport    = data.get("transport_connectivity", 0.5)
        green_space  = data.get("green_space_fraction", 0.2)
        housing_stress = data.get("housing_affordability_stress", 0.3)
        congestion   = data.get("congestion_index", 0.3)
        phi = max(land_use*0.4 + transport*0.3 + green_space*0.3, 0.01)
        C   = max(housing_stress*0.5 + congestion*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Urban dysfunction — congestion and unaffordable housing critical"
        if psi < 0.6:  return "Strained city — infrastructure lagging behind growth"
        if psi <= 1.2: return "Well-planned urban environment"
        return "Model city — efficient, green and connected"
