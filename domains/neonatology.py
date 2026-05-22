from domains.base import DomainAdapter
class NeonatologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        gestational_age  = data.get("gestational_age_weeks", 37) / 42.0
        birth_weight_norm= data.get("birth_weight_norm", 0.8)
        apgar_score      = data.get("apgar_score", 8) / 10.0
        respiratory_index= data.get("respiratory_support_need", 0.1)
        sepsis_risk      = data.get("sepsis_risk", 0.05)
        phi = max(min(gestational_age,1.0)*0.3 + birth_weight_norm*0.3 + apgar_score*0.4, 0.01)
        C   = max(respiratory_index*0.5 + sepsis_risk*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Neonatal emergency — critical immaturity or severe compromise"
        if psi < 0.6:  return "Premature — significant NICU support required"
        if psi <= 1.2: return "Neonatal transition normal — healthy adaptation"
        return "Robust newborn — excellent transition, no complications expected"
