from domains.base import DomainAdapter
class AncientCivilisationsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        surplus     = data.get("surplus_production", 0.6)
        trade       = data.get("trade_volume_norm", 0.4)
        admin       = data.get("administrative_complexity", 0.4)
        culture     = data.get("cultural_output", 0.4)
        invasion    = data.get("invasion_pressure", 0.2)
        revolt      = data.get("internal_revolt", 0.2)
        phi = max(surplus*0.3 + trade*0.3 + admin*0.2 + culture*0.2, 0.01)
        C   = max(invasion*0.5 + revolt*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Civilisation collapse — dark age, knowledge and trade lost"
        if psi < 0.6:  return "Declining civilisation — surplus and trade shrinking"
        if psi <= 1.2: return "Stable civilisation — administration and trade functioning"
        return "Golden age — cultural and economic florescence"
