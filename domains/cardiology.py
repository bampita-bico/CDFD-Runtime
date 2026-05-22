from domains.base import DomainAdapter

class CardiologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        ef        = data.get("ejection_fraction", 60)   # %
        bp_sys    = data.get("bp_systolic", 120)
        troponin  = data.get("troponin", 0.01)          # ng/mL
        hr        = data.get("heart_rate", 70)
        phi = max(ef / 60.0 * 0.5 + (1.0 - abs(hr - 70) / 150.0) * 0.5, 0.01)
        C   = max(bp_sys / 120.0 * 0.4 + min(troponin * 10, 2.0) * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cardiogenic shock — critical cardiac failure"
        if psi < 0.6:  return "Severe heart failure — urgent optimisation"
        if psi < 0.8:  return "Reduced cardiac output — titrate therapy"
        if psi <= 1.2: return "Compensated cardiac function"
        return "Hypertensive overload — risk of acute event"
