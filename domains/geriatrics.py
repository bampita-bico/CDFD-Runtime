from domains.base import DomainAdapter

class GeriatricsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        frailty   = data.get("frailty_score", 2)    # CFS 1-9
        adl       = data.get("ADL_score", 6)         # 0-6
        comorbid  = data.get("comorbidity_count", 2)
        polypharm = data.get("drug_count", 3)
        phi = max(adl / 6.0 * 0.5 + (1.0 - min(frailty/9.0,1.0)) * 0.5, 0.01)
        C   = max(min(comorbid/10.0,1.0) * 0.5 + min(polypharm/15.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe frailty signal"
        if psi < 0.6:  return "Moderate frailty signal"
        if psi < 0.8:  return "Pre-frail model band"
        if psi <= 1.2: return "Healthy-ageing model band"
        return "Exceptional functional-reserve model band"
