from domains.base import DomainAdapter

class GeriatricsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        frailty   = data.get("frailty_score", 2)    # CFS 1-9
        adl       = data.get("ADL_score", 6)         # 0-6
        comorbid  = data.get("comorbidity_count", 2)
        polypharm = data.get("medications", 3)
        phi = max(adl / 6.0 * 0.5 + (1.0 - min(frailty/9.0,1.0)) * 0.5, 0.01)
        C   = max(min(comorbid/10.0,1.0) * 0.5 + min(polypharm/15.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe frailty — palliative goals of care discussion"
        if psi < 0.6:  return "Moderate frailty — comprehensive geriatric assessment"
        if psi < 0.8:  return "Pre-frail — falls prevention and deprescribing"
        if psi <= 1.2: return "Healthy ageing — maintain activity and nutrition"
        return "Exceptional functional reserve — continue current approach"
