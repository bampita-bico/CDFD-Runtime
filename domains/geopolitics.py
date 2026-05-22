from domains.base import DomainAdapter

class GeopoliticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        military_power = data.get("military_power_index", 0.5)
        economic_power = data.get("economic_power_index", 0.5)
        soft_power     = data.get("soft_power_index", 0.4)
        rival_pressure = data.get("rival_pressure", 0.3)
        instability    = data.get("internal_instability", 0.2)
        phi = max(military_power*0.4 + economic_power*0.4 + soft_power*0.2, 0.01)
        C   = max(rival_pressure*0.6 + instability*0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Power collapse — state losing control of its strategic position"
        if psi < 0.6:  return "Declining power — rivals gaining ground on all fronts"
        if psi <= 1.2: return "Stable power — holding strategic position against rivals"
        return "Hegemonic — dominant regional or global power"
