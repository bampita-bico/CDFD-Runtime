from domains.base import DomainAdapter
class SanctionsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        coverage    = data.get("sanction_coverage_norm", 0.5)
        enforcement = data.get("enforcement_tightness", 0.6)
        multilateral= data.get("multilateral_support", 0.5)
        evasion     = data.get("evasion_capacity", 0.3)
        economic_div= data.get("economic_diversification", 0.4)
        phi = max(coverage*0.4 + enforcement*0.3 + multilateral*0.3, 0.01)
        C   = max(evasion*0.5 + economic_div*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Sanctions ineffective — target evading through diversification"
        if psi < 0.6:  return "Partial sanctions impact — some evasion limiting effect"
        if psi <= 1.2: return "Sanctions biting — economic pressure building"
        return "Maximum sanctions pressure — target economy severely constrained"
