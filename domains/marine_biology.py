from domains.base import DomainAdapter
class MarineBiologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        species     = data.get("species_richness_norm", 0.7)
        productivity= data.get("primary_productivity", 0.6)
        habitat     = data.get("habitat_integrity", 0.7)
        pollution   = data.get("pollution_index", 0.15)
        overfishing = data.get("overfishing_index", 0.2)
        phi = max(species*0.4 + productivity*0.4 + habitat*0.2, 0.01)
        C   = max(pollution*0.5 + overfishing*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Marine ecosystem collapse — biodiversity failing"
        if psi < 0.6:  return "Marine degradation — overfishing and pollution damaging"
        if psi <= 1.2: return "Healthy marine biology — balanced ecosystem"
        return "Thriving ocean — high biodiversity and abundant productivity"
