from domains.base import DomainAdapter

class NutritionAdapter(DomainAdapter):
    def map_to_engine(self, data):
        bmi       = data.get("BMI", 22.0)
        albumin   = data.get("albumin", 40)      # g/L
        muac      = data.get("MUAC_cm", 26)      # mid-upper arm circumference
        intake_pct= data.get("intake_pct", 100)  # % of requirements
        phi = max(min(intake_pct/100.0,1.0) * 0.4 + albumin/45.0 * 0.3 +
                  (1.0 - abs(bmi-22)/20.0) * 0.3, 0.01)
        C   = max((1.0 - min(intake_pct/100.0,1.0)) * 0.4 +
                  (1.0 - albumin/50.0) * 0.3 + (1.0 - min(muac/30.0,1.0)) * 0.3, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe malnutrition — therapeutic feeding required"
        if psi < 0.6:  return "Moderate malnutrition — supplementary feeding"
        if psi < 0.8:  return "At-risk nutritional status — dietary intervention"
        if psi <= 1.2: return "Adequate nutritional status"
        return "Overnutrition — dietary counselling recommended"
