from domains.base import DomainAdapter

class NuclearPhysicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        binding_energy   = data.get("binding_energy_MeV_per_A", 8.0) / 10.0
        neutron_flux     = data.get("neutron_flux_norm", 0.5)
        criticality      = data.get("criticality_index", 0.5)
        decay_heat       = data.get("decay_heat_norm", 0.1)
        phi = max(binding_energy * 0.4 + neutron_flux * 0.6, 0.01)
        C   = max(criticality * 0.5 + decay_heat * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Sub-critical — reaction cannot sustain itself"
        if psi < 0.6:  return "Near-critical — reaction marginal"
        if psi <= 1.2: return "Critical — stable controlled reaction"
        return "Super-critical — uncontrolled chain reaction risk"
