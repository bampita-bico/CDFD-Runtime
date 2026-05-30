from domains.base import DomainAdapter
class DecisionTheoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        utility_clarity  = data.get("utility_clarity", 0.6)
        information_set  = data.get("information_completeness", 0.7)
        uncertainty_load = data.get("uncertainty_index", 0.3)
        cognitive_bias   = data.get("decision_bias", 0.2)
        phi = max(utility_clarity*0.5 + information_set*0.5, 0.01)
        C   = max(uncertainty_load*0.5 + cognitive_bias*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Decision paralysis — uncertainty and bias overwhelming choice"
        if psi < 0.6:  return "Poor-decision-risk signal - information gaps and biases dominant"
        if psi <= 1.2: return "Rational decision-making — adequate information and clarity"
        return "Optimal decisions — complete information, clear utilities, minimal bias"
