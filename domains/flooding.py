from domains.base import DomainAdapter
class FloodingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        rainfall    = data.get("rainfall_intensity_norm", 0.3)
        saturation  = data.get("catchment_saturation", 0.4)
        upstream    = data.get("upstream_flow_norm", 0.4)
        defence     = data.get("flood_defence_capacity", 0.6)
        impervious  = data.get("urban_impervious_fraction", 0.4)
        phi = max(rainfall*0.4 + saturation*0.3 + upstream*0.3, 0.01)
        C   = max((1.0-defence)*0.5 + impervious*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "No flood risk — catchment dry, defences adequate"
        if psi < 0.6:  return "Flood watch — defences tested, overflow possible"
        if psi <= 1.2: return "Flooding underway — infrastructure stressed"
        return "Catastrophic flood — defences overwhelmed, major damage"
