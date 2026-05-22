from domains.base import DomainAdapter
class SoilDegradationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        organic_c   = data.get("soil_organic_carbon", 0.5)
        structure   = data.get("soil_structure_norm", 0.6)
        microbial   = data.get("microbial_activity", 0.5)
        erosion     = data.get("erosion_rate_norm", 0.2)
        salinity    = data.get("salinity_index", 0.1)
        phi = max(organic_c*0.4 + structure*0.3 + microbial*0.3, 0.01)
        C   = max(erosion*0.5 + salinity*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Soil collapse — desertification, land unproductive"
        if psi < 0.6:  return "Severe soil degradation — agricultural productivity threatened"
        if psi <= 1.2: return "Soil in acceptable condition — fertility maintained"
        return "Healthy soil — rich organic matter, excellent structure"
