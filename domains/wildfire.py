from domains.base import DomainAdapter
class WildfireAdapter(DomainAdapter):
    def map_to_engine(self, data):
        fuel_load   = data.get("fuel_load_norm", 0.4)
        drought     = data.get("drought_index", 0.3)
        ignition    = data.get("ignition_risk", 0.2)
        suppression = data.get("suppression_capacity", 0.6)
        wind        = data.get("wind_index", 0.3)
        phi = max(fuel_load*0.4 + drought*0.3 + ignition*0.3, 0.01)
        C   = max(suppression*0.5 + (1.0-wind)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Low fire risk — conditions unfavourable for ignition"
        if psi < 0.6:  return "Elevated fire risk — fuel and drought accumulating"
        if psi <= 1.2: return "Active fire conditions — suppression resources engaged"
        return "Extreme fire danger — megafire conditions, suppression overwhelmed"
