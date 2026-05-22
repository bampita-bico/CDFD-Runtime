from domains.base import DomainAdapter

class PulmonologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        fev1     = data.get("FEV1_pct", 80)     # % predicted
        spo2     = data.get("SpO2", 98)          # %
        rr       = data.get("resp_rate", 16)     # breaths/min
        fibrosis = data.get("fibrosis_score", 0) # 0-4
        phi = max(fev1 / 80.0 * 0.4 + spo2 / 98.0 * 0.4 + (1.0 - abs(rr-16)/30.0) * 0.2, 0.01)
        C   = max(fibrosis / 4.0 * 0.5 + (1.0 - fev1/100.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Respiratory failure — ventilatory support required"
        if psi < 0.6:  return "Severe obstruction/restriction — escalate bronchodilators"
        if psi < 0.8:  return "Moderate respiratory impairment — optimise inhalers"
        if psi <= 1.2: return "Adequate respiratory function"
        return "Hyperventilation state — anxiety or early compensation"
