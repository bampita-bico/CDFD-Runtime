from domains.base import DomainAdapter
class AquacultureAdapter(DomainAdapter):
    def map_to_engine(self, data):
        yield_n     = data.get("production_yield_norm", 0.6)
        water_q     = data.get("water_quality_norm", 0.7)
        feed_conv   = data.get("feed_conversion_efficiency", 0.6)
        disease     = data.get("disease_pressure", 0.2)
        env_impact  = data.get("environmental_impact_norm", 0.2)
        phi = max(yield_n*0.4 + water_q*0.3 + feed_conv*0.3, 0.01)
        C   = max(disease*0.5 + env_impact*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Aquaculture failing — disease or water quality collapse"
        if psi < 0.6:  return "Below-target production — stress reducing yields"
        if psi <= 1.2: return "Aquaculture productive — yields and water quality maintained"
        return "High-performance aquaculture — excellent yield, minimal impact"
