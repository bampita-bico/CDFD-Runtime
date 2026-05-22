from domains.base import DomainAdapter

class AstrophysicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        luminosity  = data.get("luminosity_solar", 1.0)   # relative to sun
        mass_solar  = data.get("mass_solar", 1.0)
        age_gyr     = data.get("age_Gyr", 4.6)
        metallicity = data.get("metallicity", 0.02)       # Z
        phi = max(min(luminosity/100.0,1.0) * 0.5 + min(metallicity/0.05,1.0) * 0.5, 0.01)
        C   = max(min(mass_solar/100.0,1.0) * 0.5 + min(age_gyr/12.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Stellar remnant — white dwarf / neutron star / black hole"
        if psi < 0.6:  return "Post-main-sequence — red giant / supergiant phase"
        if psi <= 1.2: return "Main sequence equilibrium — stable hydrogen burning"
        return "Young energetic star — intense radiation and stellar wind"
