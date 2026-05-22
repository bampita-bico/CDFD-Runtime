from domains.base import DomainAdapter
class FoodSecurityAdapter(DomainAdapter):
    def map_to_engine(self, data):
        caloric     = data.get("caloric_availability", 0.7)
        diversity   = data.get("dietary_diversity", 0.5)
        access      = data.get("food_access_index", 0.6)
        supply_frag = data.get("supply_chain_fragility", 0.2)
        price_vol   = data.get("price_volatility", 0.3)
        conflict_d  = data.get("conflict_disruption", 0.15)
        phi = max(caloric*0.4 + diversity*0.3 + access*0.3, 0.01)
        C   = max(supply_frag*0.4 + price_vol*0.3 + conflict_d*0.3, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Food crisis — acute hunger, supply chains broken"
        if psi < 0.6:  return "Food insecurity — access and availability strained"
        if psi <= 1.2: return "Food security maintained — adequate supply and access"
        return "Food abundance — surplus, diverse diet, resilient supply"
