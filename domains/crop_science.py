from domains.base import DomainAdapter
class CropScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        crop_yield  = data.get("yield_norm", 0.6)
        soil_fert   = data.get("soil_fertility", 0.6)
        variety_res = data.get("variety_resilience", 0.5)
        pest_disease= data.get("pest_disease_pressure", 0.2)
        climate_str = data.get("climate_stress", 0.2)
        phi = max(crop_yield*0.4 + soil_fert*0.3 + variety_res*0.3, 0.01)
        C   = max(pest_disease*0.5 + climate_str*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Crop failure — pests, disease or climate destroying yield"
        if psi < 0.6:  return "Below-target yield — significant crop stress"
        if psi <= 1.2: return "Good harvest — yield meeting food demand"
        return "Exceptional yield — optimal growing conditions"
