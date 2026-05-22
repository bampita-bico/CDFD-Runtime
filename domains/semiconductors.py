from domains.base import DomainAdapter

class SemiconductorsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        transistor_density = data.get("transistor_density_norm", 0.7)
        yield_rate         = data.get("fab_yield_rate", 0.85)
        defect_density     = data.get("defect_density_norm", 0.1)
        thermal_resistance = data.get("thermal_resistance_norm", 0.2)
        phi = max(transistor_density * 0.5 + yield_rate * 0.5, 0.01)
        C   = max(defect_density * 0.5 + thermal_resistance * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Fabrication failing — yield too low for commercial viability"
        if psi < 0.6:  return "Below-par semiconductor — defects limiting performance"
        if psi <= 1.2: return "Functional semiconductor — meeting specifications"
        return "Leading-edge chip — high density, low defect, excellent yield"
