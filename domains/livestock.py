from domains.base import DomainAdapter
class LivestockAdapter(DomainAdapter):
    def map_to_engine(self, data):
        productivity= data.get("herd_productivity_norm", 0.6)
        vet_health  = data.get("veterinary_health_index", 0.7)
        feed        = data.get("feed_availability", 0.6)
        disease     = data.get("disease_outbreak_risk", 0.15)
        overgrazing = data.get("overgrazing_index", 0.2)
        phi = max(productivity*0.4 + vet_health*0.3 + feed*0.3, 0.01)
        C   = max(disease*0.5 + overgrazing*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Livestock collapse — disease or feed failure"
        if psi < 0.6:  return "Livestock under stress — productivity declining"
        if psi <= 1.2: return "Healthy livestock sector — production and animal health good"
        return "Excellent livestock system — high yield, disease-free"
