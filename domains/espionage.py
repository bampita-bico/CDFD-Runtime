from domains.base import DomainAdapter
class EspionageAdapter(DomainAdapter):
    def map_to_engine(self, data):
        intelligence_quality = data.get("intelligence_quality", 0.6)
        collection_reach     = data.get("collection_reach", 0.5)
        counterintelligence  = data.get("counterintelligence_strength", 0.6)
        penetration_risk     = data.get("penetration_risk", 0.2)
        phi = max(intelligence_quality*0.5 + collection_reach*0.5, 0.01)
        C   = max(counterintelligence*0.5 + (1.0-penetration_risk)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Intelligence blind — collection failing or heavily penetrated"
        if psi < 0.6:  return "Intelligence weak — gaps and counterintelligence limiting reach"
        if psi <= 1.2: return "Intelligence functional — actionable collection maintained"
        return "Intelligence dominance — comprehensive picture, operations effective"
