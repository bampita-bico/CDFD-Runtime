from domains.base import DomainAdapter
class NuclearEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        thermal_power_norm = data.get("thermal_power_norm", 0.7)
        fuel_burnup_norm   = data.get("fuel_burnup_norm", 0.5)
        safety_margin      = data.get("safety_margin", 0.8)
        coolant_integrity  = data.get("coolant_integrity", 0.95)
        radiation_leak_norm= data.get("radiation_leak_norm", 0.01)
        phi = max(thermal_power_norm*0.4 + fuel_burnup_norm*0.2 + coolant_integrity*0.4, 0.01)
        C   = max((1.0-safety_margin)*0.5 + radiation_leak_norm*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Reactor shutdown — power below minimum or coolant failure"
        if psi < 0.6:  return "Reactor degraded — safety margins thinning"
        if psi <= 1.2: return "Reactor nominal — safe and productive operation"
        return "Peak reactor performance — high output, excellent safety margins"
