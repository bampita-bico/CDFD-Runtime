from domains.base import DomainAdapter

class PathologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cell_viability   = data.get("cell_viability", 0.8)
        tissue_integrity = data.get("tissue_integrity", 0.7)
        mutation_load    = data.get("mutation_burden", 0.1)
        necrosis_fraction= data.get("necrosis_fraction", 0.05)
        phi = max(cell_viability * 0.5 + tissue_integrity * 0.5, 0.01)
        C   = max(mutation_load * 0.5 + necrosis_fraction * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Extensive necrosis — tissue non-viable"
        if psi < 0.6:  return "Significant tissue damage — repair mechanisms overwhelmed"
        if psi <= 1.2: return "Tissue health maintained — normal cellular architecture"
        return "Hyperplastic tissue — rapid proliferation, screen for malignancy"
