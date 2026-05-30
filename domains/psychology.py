from domains.base import DomainAdapter

class PsychologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        wellbeing   = data.get("wellbeing_score", 7.0)   # 0-10
        stress      = data.get("stress_level", 3.0)      # 0-10
        resilience  = data.get("resilience_score", 7.0)  # 0-10
        trauma_load = data.get("trauma_load", 0.2)       # 0-1
        phi = max(wellbeing/10.0 * 0.5 + resilience/10.0 * 0.5, 0.01)
        C   = max(stress/10.0 * 0.5 + trauma_load * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Psychological-crisis signal"
        if psi < 0.6:  return "Significant psychological-burden signal"
        if psi <= 1.2: return "Psychological equilibrium"
        return "Flourishing — high wellbeing and resilience"
