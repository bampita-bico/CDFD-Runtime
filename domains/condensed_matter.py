from domains.base import DomainAdapter

class CondensedMatterAdapter(DomainAdapter):
    def map_to_engine(self, data):
        electron_density = data.get("electron_density", 0.6)
        conductivity     = data.get("conductivity_index", 0.5)
        disorder         = data.get("lattice_disorder", 0.2)
        temperature_norm = data.get("temperature_norm", 0.3)
        phi = max(electron_density * 0.5 + conductivity * 0.5, 0.01)
        C   = max(disorder * 0.5 + temperature_norm * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Insulating regime — electron flow blocked by disorder"
        if psi < 0.6:  return "Semiconducting — partial conductivity"
        if psi <= 1.2: return "Conducting material — balanced electron flow"
        return "Superconducting-like regime — near-zero resistance"
