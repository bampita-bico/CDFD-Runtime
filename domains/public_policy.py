from domains.base import DomainAdapter
class PublicPolicyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        effectiveness   = data.get("policy_effectiveness", 0.6)
        institutions    = data.get("institutional_quality", 0.6)
        impl_gap        = data.get("implementation_gap", 0.3)
        corruption      = data.get("corruption_index", 0.2)
        phi = max(effectiveness*0.5 + institutions*0.5, 0.01)
        C   = max(impl_gap*0.5 + corruption*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Policy failure — corruption and implementation gap overwhelming intent"
        if psi < 0.6:  return "Weak governance — policies poorly implemented"
        if psi <= 1.2: return "Effective governance — policies achieving goals"
        return "Excellent public institutions — transparent and accountable"
