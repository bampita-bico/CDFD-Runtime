from domains.base import DomainAdapter

class BiotechnologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        expression_yield = data.get("protein_expression_norm", 0.6)
        process_efficiency = data.get("bioprocess_efficiency", 0.6)
        contamination    = data.get("contamination_risk", 0.1)
        regulatory_burden= data.get("regulatory_hurdle", 0.3)
        phi = max(expression_yield * 0.5 + process_efficiency * 0.5, 0.01)
        C   = max(contamination * 0.4 + regulatory_burden * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Bioprocess failing — contamination or regulatory block"
        if psi < 0.6:  return "Low biotech productivity — yield and efficiency below target"
        if psi <= 1.2: return "Bioprocess operational — meeting production targets"
        return "High-performance biotech — excellent yield, clear regulatory path"
