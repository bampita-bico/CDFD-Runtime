from domains.base import DomainAdapter
class SoilHealthAdapter(DomainAdapter):
    def map_to_engine(self, data):
        organic_matter = data.get("organic_matter_pct", 3.0) / 10.0
        microbial_div  = data.get("microbial_diversity_norm", 0.6)
        water_retention= data.get("water_retention_norm", 0.6)
        compaction     = data.get("compaction_index", 0.2)
        chemical_input = data.get("chemical_input_load", 0.3)
        phi = max(min(organic_matter,1.0)*0.4 + microbial_div*0.3 + water_retention*0.3, 0.01)
        C   = max(compaction*0.5 + chemical_input*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Soil biologically dead — compaction and chemicals have destroyed function"
        if psi < 0.6:  return "Degraded soil health — microbial diversity and structure poor"
        if psi <= 1.2: return "Soil health adequate — biological activity maintained"
        return "Exceptional soil health — rich microbiome, excellent structure"
