from domains.base import DomainAdapter

class RheumatologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        das28    = data.get("DAS28", 2.0)         # disease activity 0-9.4
        esr      = data.get("ESR", 10)            # mm/hr
        crp      = data.get("CRP", 5)             # mg/L
        joint_dmg= data.get("joint_damage_score", 0.0)  # 0-1
        phi = max((1.0 - min(das28/9.4,1.0)) * 0.5 + (1.0 - joint_dmg) * 0.5, 0.01)
        C   = max(min(esr/100.0,1.0) * 0.3 + min(crp/100.0,1.0) * 0.4 + joint_dmg * 0.3, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe active-disease signal"
        if psi < 0.6:  return "Moderate disease-activity signal"
        if psi < 0.8:  return "Low disease-activity band"
        if psi <= 1.2: return "Remission model band"
        return "Paradoxical-inflammation signal"
