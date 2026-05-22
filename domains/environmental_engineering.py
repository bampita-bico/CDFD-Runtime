from domains.base import DomainAdapter

class EnvironmentalEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        treatment_efficiency = data.get("treatment_efficiency", 0.8)
        waste_diversion      = data.get("waste_diversion_rate", 0.5)
        pollutant_load       = data.get("pollutant_load_norm", 0.2)
        regulatory_compliance= data.get("compliance_index", 0.8)
        phi = max(treatment_efficiency * 0.5 + waste_diversion * 0.5, 0.01)
        C   = max(pollutant_load * 0.5 + (1.0 - regulatory_compliance) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Environmental system failing — pollution uncontrolled"
        if psi < 0.6:  return "Below standards — treatment capacity insufficient"
        if psi <= 1.2: return "Environmental engineering effective — compliance met"
        return "Best-practice environmental management — pollution minimised"
