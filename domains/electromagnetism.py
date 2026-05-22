from domains.base import DomainAdapter

class ElectromagnetismAdapter(DomainAdapter):
    def map_to_engine(self, data):
        field_strength   = data.get("field_strength_norm", 0.5)
        current_density  = data.get("current_density_norm", 0.5)
        resistance_norm  = data.get("resistance_norm", 0.3)
        shielding        = data.get("shielding_index", 0.2)
        phi = max(field_strength * 0.5 + current_density * 0.5, 0.01)
        C   = max(resistance_norm * 0.5 + shielding * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Electromagnetic field suppressed — shielding or resistance dominant"
        if psi < 0.6:  return "Weak field — significant ohmic losses"
        if psi <= 1.2: return "Electromagnetic system balanced"
        return "Strong EM field — high energy density, potential interference"
