from domains.base import DomainAdapter

class AnthropologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cultural_flow = data.get("cultural_exchange_rate", 0.6)  # 0-1
        isolation     = data.get("cultural_isolation", 0.2)      # 0-1
        language_div  = data.get("language_diversity_index", 0.6) # 0-1
        taboo_burden  = data.get("taboo_constraint_index", 0.2)   # 0-1
        phi = max(cultural_flow * 0.5 + language_div * 0.5, 0.01)
        C   = max(isolation * 0.5 + taboo_burden * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cultural stagnation — isolation and constraint dominating"
        if psi < 0.6:  return "Limited cultural exchange — identity under pressure"
        if psi <= 1.2: return "Healthy cultural vitality"
        return "Rapid cultural transformation — hybridisation and innovation"
