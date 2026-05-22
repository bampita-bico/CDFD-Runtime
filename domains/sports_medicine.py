from domains.base import DomainAdapter

class SportsMedicineAdapter(DomainAdapter):
    def map_to_engine(self, data):
        vo2max    = data.get("VO2max", 45)        # mL/kg/min
        injury_l  = data.get("injury_load", 0.0) # 0-1
        training_l= data.get("training_load", 0.5) # AU
        recovery  = data.get("recovery_score", 0.8) # 0-1
        phi = max(min(vo2max/60.0,1.0) * 0.4 + recovery * 0.4 + (1.0-injury_l) * 0.2, 0.01)
        C   = max(injury_l * 0.5 + min(training_l,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Injured/overtrained — rest and rehabilitation"
        if psi < 0.6:  return "Under-recovered — reduce load, prioritise sleep"
        if psi < 0.8:  return "Functional training state — moderate load"
        if psi <= 1.2: return "Optimal athletic performance window"
        return "Peak fitness — maintain and taper for competition"
