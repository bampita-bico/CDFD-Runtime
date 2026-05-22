from domains.base import DomainAdapter
class ArchitectureArtsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        design_inn  = data.get("design_innovation", 0.5)
        build_q     = data.get("build_quality_norm", 0.7)
        cultural_ex = data.get("cultural_expression", 0.5)
        standard_p  = data.get("standardisation_pressure", 0.3)
        cost_c      = data.get("cost_constraint", 0.4)
        phi = max(design_inn*0.4 + build_q*0.3 + cultural_ex*0.3, 0.01)
        C   = max(standard_p*0.5 + cost_c*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Architectural decline — only functional boxes, no cultural expression"
        if psi < 0.6:  return "Constrained design — cost and standardisation limiting architecture"
        if psi <= 1.2: return "Good architecture — quality and identity expressed"
        return "Architectural golden age — iconic design shaping civilisation"
