from domains.base import DomainAdapter

class PlasmaPhysicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        temperature_keV = data.get("temperature_keV", 10) / 100.0
        density_norm    = data.get("plasma_density_norm", 0.5)
        confinement     = data.get("confinement_index", 0.5)
        instability     = data.get("mhd_instability", 0.2)
        phi = max(min(temperature_keV, 1.0) * 0.4 + density_norm * 0.6, 0.01)
        C   = max((1.0 - confinement) * 0.5 + instability * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Plasma collapse — confinement lost"
        if psi < 0.6:  return "Unstable plasma — MHD instabilities growing"
        if psi <= 1.2: return "Stable plasma confinement — fusion conditions approaching"
        return "Ignition conditions — plasma self-heating"
