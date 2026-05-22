from domains.base import DomainAdapter
class GameTheoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cooperation  = data.get("cooperation_index", 0.5)
        info_sym     = data.get("information_symmetry", 0.6)
        defection_p  = data.get("defection_pressure", 0.3)
        coord_fail   = data.get("coordination_failure", 0.2)
        phi = max(cooperation*0.5 + info_sym*0.5, 0.01)
        C   = max(defection_p*0.5 + coord_fail*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Prisoner dilemma — defection dominant, social optimum unreached"
        if psi < 0.6:  return "Fragile cooperation — defection incentives rising"
        if psi <= 1.2: return "Cooperative equilibrium — players cooperating"
        return "Dominant cooperation — coordination achieved, mutual gains realised"
