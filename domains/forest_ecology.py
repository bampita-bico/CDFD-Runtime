from domains.base import DomainAdapter
class ForestEcologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        canopy_cover     = data.get("canopy_cover_fraction", 0.7)
        species_richness = data.get("species_richness_norm", 0.6)
        carbon_stock_norm= data.get("carbon_stock_norm", 0.7)
        disturbance_index= data.get("disturbance_index", 0.2)
        fragmentation    = data.get("fragmentation_index", 0.2)
        phi = max(canopy_cover*0.3 + species_richness*0.3 + carbon_stock_norm*0.4, 0.01)
        C   = max(disturbance_index*0.5 + fragmentation*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Forest degraded — canopy collapse, biodiversity lost"
        if psi < 0.6:  return "Forest under threat — disturbance and fragmentation damaging"
        if psi <= 1.2: return "Forest ecosystem healthy — canopy and biodiversity intact"
        return "Old-growth forest — maximum biodiversity and carbon storage"
