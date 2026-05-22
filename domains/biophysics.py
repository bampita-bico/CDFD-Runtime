from domains.base import DomainAdapter

class BiophysicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        membrane_potential = data.get("membrane_potential_norm", 0.6)
        ion_channel_flux   = data.get("ion_channel_flux", 0.5)
        mechanical_stress  = data.get("cell_mechanical_stress", 0.2)
        osmotic_pressure   = data.get("osmotic_imbalance", 0.15)
        phi = max(membrane_potential * 0.5 + ion_channel_flux * 0.5, 0.01)
        C   = max(mechanical_stress * 0.5 + osmotic_pressure * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cell dysfunction — membrane integrity compromised"
        if psi < 0.6:  return "Biophysical stress — ion gradients disrupted"
        if psi <= 1.2: return "Normal biophysical function"
        return "High biophysical activity — intense signalling and mechanical work"
