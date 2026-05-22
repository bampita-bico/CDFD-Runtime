from domains.base import DomainAdapter

class PharmacologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        efficacy  = data.get("efficacy_score", 0.8)    # 0-1
        toxicity  = data.get("toxicity_score", 0.1)    # 0-1
        resistance= data.get("resistance_score", 0.0)  # 0-1
        adherence = data.get("adherence", 0.9)         # 0-1
        phi = max(efficacy * 0.5 + adherence * 0.5, 0.01)
        C   = max(toxicity * 0.5 + resistance * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Drug failure — switch or combination therapy needed"
        if psi < 0.6:  return "Subtherapeutic — dose optimisation or adherence support"
        if psi <= 1.2: return "Therapeutic window achieved"
        return "Drug toxicity risk — dose reduction or drug holiday"
