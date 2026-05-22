from domains.base import DomainAdapter

class PsychiatryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        phq9      = data.get("PHQ9", 5)          # 0-27 depression
        gad7      = data.get("GAD7", 3)          # 0-21 anxiety
        panss     = data.get("PANSS", 30)        # 30-210 psychosis
        sleep_hrs = data.get("sleep_hours", 7)
        phi = max((1.0 - min(phq9/27.0,1.0)) * 0.3 + (1.0 - min(gad7/21.0,1.0)) * 0.3 +
                  min(sleep_hrs/9.0,1.0) * 0.4, 0.01)
        C   = max(min(phq9/27.0,1.0) * 0.3 + min(gad7/21.0,1.0) * 0.3 +
                  min((panss-30)/180.0,1.0) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Acute psychiatric crisis — inpatient stabilisation"
        if psi < 0.6:  return "Severe psychiatric burden — intensive therapy and medication review"
        if psi < 0.8:  return "Moderate symptoms — CBT and pharmacotherapy optimisation"
        if psi <= 1.2: return "Mental equilibrium maintained"
        return "Hypomanic or activated state — mood stabiliser review"
