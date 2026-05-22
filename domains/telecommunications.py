from domains.base import DomainAdapter

class TelecommunicationsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        spectral_efficiency = data.get("spectral_efficiency_norm", 0.6)
        coverage_fraction   = data.get("coverage_fraction", 0.75)
        interference        = data.get("interference_norm", 0.2)
        infrastructure_age  = data.get("infrastructure_age_norm", 0.3)
        phi = max(spectral_efficiency * 0.5 + coverage_fraction * 0.5, 0.01)
        C   = max(interference * 0.5 + infrastructure_age * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Communications blackout — coverage or interference critical"
        if psi < 0.6:  return "Degraded communications — patchy coverage and high interference"
        if psi <= 1.2: return "Reliable telecommunications — adequate coverage and capacity"
        return "Excellent communications infrastructure — high capacity, wide coverage"
