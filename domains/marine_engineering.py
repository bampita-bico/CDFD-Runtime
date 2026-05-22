from domains.base import DomainAdapter
class MarineEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        propulsion_efficiency = data.get("propulsion_efficiency", 0.7)
        hull_integrity        = data.get("hull_integrity", 0.9)
        cargo_capacity_norm   = data.get("cargo_capacity_norm", 0.6)
        corrosion_rate        = data.get("corrosion_rate_norm", 0.1)
        fuel_consumption_norm = data.get("fuel_consumption_norm", 0.4)
        phi = max(propulsion_efficiency*0.4 + hull_integrity*0.3 + cargo_capacity_norm*0.3, 0.01)
        C   = max(corrosion_rate*0.5 + fuel_consumption_norm*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Vessel compromised — structural or propulsion failure"
        if psi < 0.6:  return "Below-standard marine performance — corrosion and fuel issues"
        if psi <= 1.2: return "Vessel operational — seaworthy and efficient"
        return "Excellent marine engineering — high efficiency, durable, full capacity"
