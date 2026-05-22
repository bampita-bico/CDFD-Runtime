from domains.base import DomainAdapter
class VisualArtsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        production  = data.get("artistic_production", 0.6)
        patronage   = data.get("patronage_index", 0.5)
        engagement  = data.get("public_engagement", 0.5)
        censorship  = data.get("censorship_index", 0.1)
        market_sat  = data.get("market_saturation", 0.3)
        phi = max(production*0.4 + patronage*0.3 + engagement*0.3, 0.01)
        C   = max(censorship*0.5 + market_sat*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Arts suppressed — censorship or economic collapse"
        if psi < 0.6:  return "Constrained arts — patronage and market weak"
        if psi <= 1.2: return "Active arts scene — production and engagement healthy"
        return "Arts flourishing — innovation, patronage and public reach peak"
