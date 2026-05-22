from domains.base import DomainAdapter

class NanotechnologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        synthesis_precision = data.get("synthesis_precision", 0.7)
        self_assembly       = data.get("self_assembly_yield", 0.6)
        toxicity_risk       = data.get("nanoparticle_toxicity", 0.15)
        scalability         = data.get("scalability_index", 0.4)
        phi = max(synthesis_precision * 0.5 + self_assembly * 0.5, 0.01)
        C   = max(toxicity_risk * 0.4 + (1.0 - scalability) * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Nanotechnology failing — synthesis or scaling impossible"
        if psi < 0.6:  return "Lab-scale only — not yet manufacturable"
        if psi <= 1.2: return "Nanomaterial functional — properties as designed"
        return "Breakthrough nanotech — precise, scalable, high-performance"
