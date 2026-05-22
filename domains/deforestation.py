from domains.base import DomainAdapter
class DeforestationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cover       = data.get("forest_cover_fraction", 0.6)
        reforest    = data.get("reforestation_rate", 0.2)
        deforest_r  = data.get("deforestation_rate_norm", 0.1)
        logging     = data.get("logging_pressure", 0.2)
        phi = max(cover*0.5 + reforest*0.5, 0.01)
        C   = max(deforest_r*0.5 + logging*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Forests collapsing — deforestation rate critical"
        if psi < 0.6:  return "Forest loss accelerating — biodiversity and carbon at risk"
        if psi <= 1.2: return "Forest cover stable — deforestation matched by regrowth"
        return "Forest expanding — reforestation exceeding loss"
