from domains.base import DomainAdapter
class PalliativeCareAdapter(DomainAdapter):
    def map_to_engine(self, data):
        symptom_control  = data.get("symptom_control_index", 0.7)
        qol_score        = data.get("quality_of_life_norm", 0.6)
        family_support   = data.get("family_support_index", 0.6)
        pain_burden      = data.get("pain_burden", 0.3)
        existential_distress = data.get("existential_distress", 0.3)
        phi = max(symptom_control*0.4 + qol_score*0.3 + family_support*0.3, 0.01)
        C   = max(pain_burden*0.5 + existential_distress*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe palliative-crisis signal"
        if psi < 0.6:  return "Inadequate symptom-control signal"
        if psi <= 1.2: return "Palliative-care stability band"
        return "High palliative-comfort model band"
