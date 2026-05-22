from domains.base import DomainAdapter
class AgroforestryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        canopy_cover    = data.get("canopy_cover_fraction", 0.3)
        crop_yield_norm = data.get("crop_yield_norm", 0.5)
        biodiversity    = data.get("agroforestry_biodiversity", 0.5)
        land_pressure   = data.get("land_conversion_pressure", 0.2)
        soil_erosion    = data.get("soil_erosion_index", 0.15)
        phi = max(canopy_cover*0.3 + crop_yield_norm*0.4 + biodiversity*0.3, 0.01)
        C   = max(land_pressure*0.5 + soil_erosion*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Agroforestry failing — land cleared, monocultures dominating"
        if psi < 0.6:  return "Agroforestry under pressure — canopy thinning, yields dropping"
        if psi <= 1.2: return "Agroforestry productive — trees and crops in balance"
        return "Exemplary agroforestry — high yield, biodiversity and soil health"
