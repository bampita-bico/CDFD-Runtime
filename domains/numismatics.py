from domains.base import DomainAdapter
class NumismaticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        monetary_stability = data.get("monetary_stability", 0.7)
        coinage_quality    = data.get("coinage_quality_norm", 0.6)
        circulation_volume = data.get("circulation_volume_norm", 0.5)
        debasement_index   = data.get("debasement_index", 0.1)
        counterfeit_rate   = data.get("counterfeit_rate_norm", 0.05)
        phi = max(monetary_stability*0.4 + coinage_quality*0.3 + circulation_volume*0.3, 0.01)
        C   = max(debasement_index*0.5 + counterfeit_rate*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Monetary collapse — debasement and counterfeiting destroying trust"
        if psi < 0.6:  return "Currency under pressure — quality and stability declining"
        if psi <= 1.2: return "Sound money — stable coinage, adequate circulation"
        return "Monetary excellence — stable, trusted, high-quality currency"
