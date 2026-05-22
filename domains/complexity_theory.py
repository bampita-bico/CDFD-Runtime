from domains.base import DomainAdapter
class ComplexityTheoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        emergent_order = data.get("emergent_order", 0.5)
        self_org       = data.get("self_organisation_index", 0.5)
        entropy_prod   = data.get("entropy_production", 0.3)
        crit_transition= data.get("critical_transition_risk", 0.2)
        phi = max(emergent_order*0.5 + self_org*0.5, 0.01)
        C   = max(entropy_prod*0.5 + crit_transition*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "System frozen — ordered but rigid, no emergence"
        if psi < 0.6:  return "Edge of order — some self-organisation emerging"
        if psi <= 1.2: return "Complex adaptive system — rich emergence, balanced order/chaos"
        return "Chaotic regime — structure dissolving, phase transition imminent"
