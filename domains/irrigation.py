from domains.base import DomainAdapter
class IrrigationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        water_delivery = data.get("water_delivery_efficiency", 0.6)
        coverage       = data.get("irrigated_area_fraction", 0.4)
        water_source   = data.get("water_source_reliability", 0.7)
        waterlogging   = data.get("waterlogging_risk", 0.15)
        salinity_buildup = data.get("salinity_buildup", 0.1)
        phi = max(water_delivery*0.4 + coverage*0.3 + water_source*0.3, 0.01)
        C   = max(waterlogging*0.5 + salinity_buildup*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Irrigation failing — waterlogging or salinity destroying cropland"
        if psi < 0.6:  return "Irrigation stressed — delivery efficiency poor"
        if psi <= 1.2: return "Irrigation functional — crops receiving adequate water"
        return "Excellent irrigation — high efficiency, wide coverage, healthy soils"
