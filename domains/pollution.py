from domains.base import DomainAdapter
class PollutionAdapter(DomainAdapter):
    def map_to_engine(self, data):
        air_q   = data.get("air_quality_norm", 0.7)
        water_q = data.get("water_quality_norm", 0.7)
        soil_q  = data.get("soil_quality_norm", 0.6)
        reg     = data.get("regulation_strength", 0.5)
        emission= data.get("industrial_emission_norm", 0.3)
        waste   = data.get("waste_generation_norm", 0.2)
        phi = max(air_q*0.3 + water_q*0.3 + soil_q*0.2 + reg*0.2, 0.01)
        C   = max(emission*0.5 + waste*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe pollution — toxic levels threatening public health"
        if psi < 0.6:  return "High pollution — regulation and mitigation failing"
        if psi <= 1.2: return "Pollution managed — within safe thresholds"
        return "Clean environment — pollution minimal, ecosystem healthy"
