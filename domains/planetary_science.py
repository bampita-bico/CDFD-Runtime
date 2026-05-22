from domains.base import DomainAdapter

class PlanetaryScienceAdapter(DomainAdapter):
    def map_to_engine(self, data):
        solar_flux       = data.get("solar_flux_norm", 0.5)
        magnetic_field   = data.get("magnetic_field_norm", 0.5)
        atmospheric_loss = data.get("atmospheric_loss_rate", 0.1)
        impact_rate      = data.get("impact_flux_norm", 0.05)
        phi = max(solar_flux * 0.5 + magnetic_field * 0.5, 0.01)
        C   = max(atmospheric_loss * 0.6 + impact_rate * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Hostile world — atmosphere stripped, unshielded"
        if psi < 0.6:  return "Marginal habitability — significant atmospheric loss"
        if psi <= 1.2: return "Planetary equilibrium — stable conditions"
        return "Highly active planet — strong magnetic field, rich energy environment"
