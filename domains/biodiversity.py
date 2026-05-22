from domains.base import DomainAdapter
class BiodiversityAdapter(DomainAdapter):
    def map_to_engine(self, data):
        richness    = data.get("species_richness_norm", 0.6)
        habitat     = data.get("habitat_area_norm", 0.6)
        genetic_div = data.get("genetic_diversity", 0.5)
        extinction  = data.get("extinction_rate_norm", 0.1)
        invasive    = data.get("invasive_pressure", 0.2)
        phi = max(richness*0.4 + habitat*0.3 + genetic_div*0.3, 0.01)
        C   = max(extinction*0.5 + invasive*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Biodiversity crisis — mass extinction underway"
        if psi < 0.6:  return "Biodiversity threatened — habitat loss accelerating species loss"
        if psi <= 1.2: return "Biodiversity maintained — ecosystems intact"
        return "High biodiversity — species-rich, genetically diverse ecosystems"
