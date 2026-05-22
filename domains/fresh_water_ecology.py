from domains.base import DomainAdapter
class FreshwaterEcologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        aquatic_biodiversity = data.get("aquatic_biodiversity_norm", 0.6)
        water_flow_norm      = data.get("water_flow_norm", 0.6)
        riparian_integrity   = data.get("riparian_integrity", 0.5)
        eutrophication       = data.get("eutrophication_index", 0.2)
        heavy_metals         = data.get("heavy_metal_contamination", 0.1)
        phi = max(aquatic_biodiversity*0.4 + water_flow_norm*0.3 + riparian_integrity*0.3, 0.01)
        C   = max(eutrophication*0.5 + heavy_metals*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Freshwater ecosystem collapse — pollution or flow disruption critical"
        if psi < 0.6:  return "Freshwater degraded — eutrophication and contamination damaging"
        if psi <= 1.2: return "Freshwater ecosystem healthy — flow and biodiversity maintained"
        return "Pristine freshwater — high biodiversity, clean water, intact riparian zones"
