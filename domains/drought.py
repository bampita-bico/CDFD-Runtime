from domains.base import DomainAdapter
class DroughtAdapter(DomainAdapter):
    def map_to_engine(self, data):
        precip_def   = data.get("precipitation_deficit", 0.2)
        soil_def     = data.get("soil_moisture_deficit", 0.3)
        streamflow   = data.get("streamflow_deficit", 0.2)
        storage      = data.get("water_storage_norm", 0.6)
        demand       = data.get("demand_pressure", 0.4)
        phi = max(precip_def*0.4 + soil_def*0.3 + streamflow*0.3, 0.01)
        C   = max((1.0-storage)*0.5 + demand*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Adequate water supply — no drought stress"
        if psi < 0.6:  return "Drought watch — deficits accumulating"
        if psi <= 1.2: return "Drought emergency — agriculture and supply at risk"
        return "Severe drought — water crisis, ecological and economic damage"
