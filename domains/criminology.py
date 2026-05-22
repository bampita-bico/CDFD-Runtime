from domains.base import DomainAdapter
class CriminologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        crime_rate = data.get("crime_rate_norm", 0.2)
        clearance  = data.get("clearance_rate", 0.5)
        social_cap = data.get("social_capital", 0.5)
        recidivism = data.get("recidivism_rate", 0.3)
        inequality = data.get("inequality_norm", 0.3)
        phi = max((1.0-crime_rate)*0.4 + clearance*0.3 + social_cap*0.3, 0.01)
        C   = max(recidivism*0.5 + inequality*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Crime crisis — rule of law breaking down"
        if psi < 0.6:  return "High crime — deterrence and social capital inadequate"
        if psi <= 1.2: return "Crime managed — enforcement and prevention working"
        return "Low crime society — strong social fabric and effective justice"
