from domains.base import DomainAdapter
class UrbanFarmingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        production_norm = data.get("urban_production_norm", 0.3)
        space_utilisation = data.get("space_utilisation", 0.5)
        community_engagement = data.get("community_engagement", 0.5)
        land_cost_norm  = data.get("land_cost_norm", 0.6)
        contamination   = data.get("soil_contamination_risk", 0.2)
        phi = max(production_norm*0.3 + space_utilisation*0.4 + community_engagement*0.3, 0.01)
        C   = max(land_cost_norm*0.5 + contamination*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Urban farming negligible — costs and contamination prohibitive"
        if psi < 0.6:  return "Limited urban production — space and cost constraining"
        if psi <= 1.2: return "Urban farming contributing — community food resilience building"
        return "Urban food system thriving — significant local production and engagement"
