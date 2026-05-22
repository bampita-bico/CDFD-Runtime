from domains.base import DomainAdapter

class VolcanologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        magma_flux       = data.get("magma_flux_norm", 0.3)
        inflation_rate   = data.get("ground_inflation_norm", 0.2)
        crustal_strength = data.get("crustal_strength", 0.8)
        gas_flux         = data.get("so2_flux_norm", 0.2)
        phi = max(magma_flux * 0.5 + inflation_rate * 0.5, 0.01)
        C   = max(crustal_strength * 0.6 + (1.0 - gas_flux) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Dormant — no significant volcanic activity"
        if psi < 0.6:  return "Unrest — magma intruding, elevated monitoring"
        if psi <= 1.2: return "Active volcano — eruptions possible"
        return "Eruption imminent — magma flux overwhelming crustal containment"
