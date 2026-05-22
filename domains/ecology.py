from domains.base import DomainAdapter

class EcologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        biodiversity= data.get("biodiversity_index", 0.7)  # 0-1
        energy_flow = data.get("energy_flow", 0.8)         # relative
        habitat_loss= data.get("habitat_loss_pct", 10) / 100.0
        invasive_sp = data.get("invasive_species", 0)      # 0-1
        phi = max(energy_flow * 0.5 + biodiversity * 0.5, 0.01)
        C   = max(habitat_loss * 0.6 + invasive_sp * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Ecosystem collapse — intervention critical"
        if psi < 0.6:  return "Degraded ecosystem — habitat restoration needed"
        if psi <= 1.2: return "Healthy ecosystem equilibrium"
        return "Boom-bust cycle — monitor for trophic cascade"
