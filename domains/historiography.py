from domains.base import DomainAdapter
class HistoriographyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        source_diversity = data.get("source_diversity_norm", 0.6)
        methodological_rigour = data.get("methodological_rigour", 0.7)
        archival_access  = data.get("archival_access", 0.6)
        political_distortion = data.get("political_distortion", 0.2)
        presentism_bias  = data.get("presentism_bias", 0.2)
        phi = max(source_diversity*0.3 + methodological_rigour*0.4 + archival_access*0.3, 0.01)
        C   = max(political_distortion*0.5 + presentism_bias*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "History fabricated — political distortion and bias dominant"
        if psi < 0.6:  return "Historical understanding limited — methodology and access poor"
        if psi <= 1.2: return "Sound historiography — rigorous methods and diverse sources"
        return "Excellent historical scholarship — comprehensive, rigorous, politically neutral"
