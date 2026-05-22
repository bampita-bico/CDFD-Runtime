from domains.base import DomainAdapter
class WaterScarcityAdapter(DomainAdapter):
    def map_to_engine(self, data):
        renewable   = data.get("renewable_water_per_capita", 0.5)
        efficiency  = data.get("water_use_efficiency", 0.5)
        demand_ratio= data.get("demand_to_supply_ratio", 0.6)
        infra_def   = data.get("infrastructure_deficit", 0.3)
        phi = max(min(renewable,1.0)*0.5 + efficiency*0.5, 0.01)
        C   = max(min(demand_ratio,1.0)*0.5 + infra_def*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Water abundant — supply exceeds demand"
        if psi < 0.6:  return "Water stress — demand approaching supply limits"
        if psi <= 1.2: return "Water scarcity — allocation conflicts emerging"
        return "Acute water crisis — supply exhausted, health emergency"
