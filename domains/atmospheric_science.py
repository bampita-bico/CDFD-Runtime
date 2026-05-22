from domains.base import DomainAdapter

class AtmosphericScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        circulation      = data.get("atmospheric_circulation", 0.6)
        precipitation    = data.get("precipitation_index", 0.5)
        aerosol_load     = data.get("aerosol_optical_depth", 0.2)
        ozone_depletion  = data.get("ozone_depletion", 0.1)
        phi = max(circulation * 0.5 + precipitation * 0.5, 0.01)
        C   = max(aerosol_load * 0.5 + ozone_depletion * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Atmospheric collapse — circulation broken, extreme events"
        if psi < 0.6:  return "Disrupted atmosphere — aerosols and ozone loss significant"
        if psi <= 1.2: return "Atmospheric system balanced"
        return "Vigorous atmospheric circulation — active weather systems"
