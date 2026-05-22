from domains.base import DomainAdapter
class InternationalLawAdapter(DomainAdapter):
    def map_to_engine(self, data):
        treaty_compliance = data.get("treaty_compliance_rate", 0.7)
        institutional_strength = data.get("institutional_strength", 0.6)
        enforcement_capacity   = data.get("enforcement_capacity", 0.4)
        great_power_defection  = data.get("great_power_defection", 0.2)
        norm_erosion           = data.get("norm_erosion_index", 0.2)
        phi = max(treaty_compliance*0.4 + institutional_strength*0.3 + enforcement_capacity*0.3, 0.01)
        C   = max(great_power_defection*0.5 + norm_erosion*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "International law irrelevant — great powers defecting from norms"
        if psi < 0.6:  return "International law eroding — compliance and enforcement weak"
        if psi <= 1.2: return "International law functioning — norms largely respected"
        return "Strong rules-based order — compliance high, institutions effective"
