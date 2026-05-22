from domains.base import DomainAdapter

class ThermodynamicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        heat_flux    = data.get("heat_flux_W_m2", 100) / 1000.0
        temp_diff_K  = data.get("temp_difference_K", 50) / 500.0
        entropy_gen  = data.get("entropy_generation", 0.2)
        insulation   = data.get("insulation_index", 0.5)
        phi = max(min(heat_flux, 1.0) * 0.5 + min(temp_diff_K, 1.0) * 0.5, 0.01)
        C   = max(entropy_gen * 0.5 + (1.0 - insulation) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Thermal equilibrium — no useful work extractable"
        if psi < 0.6:  return "Low thermodynamic efficiency — high entropy generation"
        if psi <= 1.2: return "Efficient heat transfer — good thermodynamic balance"
        return "High thermal gradient — maximum work potential"
