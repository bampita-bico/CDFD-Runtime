from domains.base import DomainAdapter
class FamineRiskAdapter(DomainAdapter):
    def map_to_engine(self, data):
        food_prod   = data.get("food_production_index", 0.6)
        market_acc  = data.get("market_access", 0.5)
        purchasing  = data.get("purchasing_power", 0.5)
        aid_cap     = data.get("aid_response_capacity", 0.5)
        conflict    = data.get("conflict_intensity", 0.15)
        climate_sh  = data.get("climate_shock_index", 0.3)
        export_ban  = data.get("export_ban_index", 0.1)
        phi = max(food_prod*0.3 + market_acc*0.3 + purchasing*0.2 + aid_cap*0.2, 0.01)
        C   = max(conflict*0.4 + climate_sh*0.3 + export_ban*0.3, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Famine averted — food production and access adequate"
        if psi < 0.6:  return "Food crisis warning — access and production under stress"
        if psi <= 1.2: return "Famine conditions — acute hunger, supply disrupted"
        return "Catastrophic famine — mass starvation without immediate intervention"
