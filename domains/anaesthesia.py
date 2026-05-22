from domains.base import DomainAdapter

class AnaesthesiaAdapter(DomainAdapter):
    def map_to_engine(self, data):
        drug_effect      = data.get("anaesthetic_depth_norm", 0.6)
        haemodynamics    = data.get("haemodynamic_stability", 0.7)
        comorbidity      = data.get("asa_score", 2) / 5.0
        airway_difficulty= data.get("airway_difficulty", 0.2)
        phi = max(drug_effect * 0.5 + haemodynamics * 0.5, 0.01)
        C   = max(comorbidity * 0.5 + airway_difficulty * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Anaesthetic crisis — haemodynamic instability, airway compromise"
        if psi < 0.6:  return "Suboptimal anaesthesia — inadequate depth or monitoring concern"
        if psi <= 1.2: return "Adequate anaesthesia — patient stable"
        return "Deep anaesthesia — monitor for oversedation and cardiac depression"
