from domains.base import DomainAdapter
class DiplomacyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        treaty_net  = data.get("treaty_network_density", 0.5)
        dip_cap     = data.get("diplomatic_capacity", 0.6)
        multilateral= data.get("multilateral_participation", 0.6)
        tensions    = data.get("bilateral_tensions", 0.2)
        negot_fail  = data.get("negotiation_failure_rate", 0.15)
        phi = max(treaty_net*0.4 + dip_cap*0.3 + multilateral*0.3, 0.01)
        C   = max(tensions*0.5 + negot_fail*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Diplomatic isolation — channels broken, conflict risk high"
        if psi < 0.6:  return "Diplomatic stress — tensions undermining negotiations"
        if psi <= 1.2: return "Active diplomacy — treaties and dialogue functioning"
        return "Diplomatic excellence — dense treaty network, trusted mediator"
