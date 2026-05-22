from domains.base import DomainAdapter
class PostcolonialAdapter(DomainAdapter):
    def map_to_engine(self, data):
        institutional_recovery = data.get("institutional_recovery", 0.5)
        economic_sovereignty   = data.get("economic_sovereignty", 0.5)
        cultural_revival       = data.get("cultural_revival_index", 0.4)
        structural_inequality  = data.get("structural_inequality", 0.4)
        dependency_index       = data.get("external_dependency", 0.4)
        phi = max(institutional_recovery*0.3 + economic_sovereignty*0.4 + cultural_revival*0.3, 0.01)
        C   = max(structural_inequality*0.5 + dependency_index*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Postcolonial dependency entrapped — institutions and economy still captured"
        if psi < 0.6:  return "Slow decolonisation — structural inequalities persisting"
        if psi <= 1.2: return "Postcolonial recovery progressing — sovereignty being rebuilt"
        return "Successful decolonisation — autonomous institutions and economy"
