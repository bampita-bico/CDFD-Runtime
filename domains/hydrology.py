from domains.base import DomainAdapter

class HydrologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        river_discharge  = data.get("river_discharge_norm", 0.6)
        groundwater      = data.get("groundwater_level_norm", 0.5)
        evapotranspiration= data.get("evapotranspiration_norm", 0.3)
        contamination    = data.get("contamination_index", 0.1)
        phi = max(river_discharge * 0.5 + groundwater * 0.5, 0.01)
        C   = max(evapotranspiration * 0.5 + contamination * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Hydrological collapse — drought or contamination critical"
        if psi < 0.6:  return "Water stress — supplies inadequate for demand"
        if psi <= 1.2: return "Hydrological balance — water cycle functioning"
        return "Abundant water — high discharge and groundwater recharge"
