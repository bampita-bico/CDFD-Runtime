from domains.base import DomainAdapter

class EndocrinologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        hba1c    = data.get("HbA1c", 5.5)       # %
        tsh      = data.get("TSH", 2.0)          # mIU/L
        cortisol = data.get("cortisol", 15.0)    # ug/dL
        insulin_r= data.get("insulin_resistance", 1.0)
        phi = max((1.0 - abs(hba1c - 5.5) / 10.0) * 0.4 +
                  (1.0 - abs(tsh - 2.0) / 10.0) * 0.3 +
                  (1.0 - min(cortisol / 50.0, 1.0)) * 0.3, 0.01)
        C   = max(insulin_r * 0.5 + hba1c / 15.0 * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.4:  return "Endocrine-crisis signal"
        if psi < 0.7:  return "Poor hormonal-control signal"
        if psi <= 1.2: return "Hormonal balance achieved"
        return "Hormonal excess — risk of end-organ damage"
