from domains.base import DomainAdapter
class ArcticEcologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        sea_ice_extent   = data.get("sea_ice_extent_norm", 0.6)
        permafrost_integrity = data.get("permafrost_integrity", 0.7)
        arctic_biodiversity  = data.get("arctic_biodiversity_norm", 0.5)
        warming_rate     = data.get("warming_rate_norm", 0.4)
        methane_release  = data.get("methane_release_norm", 0.15)
        phi = max(sea_ice_extent*0.3 + permafrost_integrity*0.4 + arctic_biodiversity*0.3, 0.01)
        C   = max(warming_rate*0.5 + methane_release*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Arctic collapse — ice, permafrost and biodiversity failing"
        if psi < 0.6:  return "Arctic severely degraded — warming accelerating ecosystem loss"
        if psi <= 1.2: return "Arctic ecosystem functional — ice and species adapted"
        return "Arctic stable — ice extent and biodiversity well-maintained"
