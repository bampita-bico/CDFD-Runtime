from domains.base import DomainAdapter

class OceanographyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        current_speed    = data.get("current_speed_m_s", 0.5) / 2.0
        upwelling        = data.get("upwelling_index", 0.4)
        acidification    = data.get("ocean_acidification", 0.2)
        dead_zone        = data.get("dead_zone_fraction", 0.1)
        phi = max(min(current_speed, 1.0) * 0.5 + upwelling * 0.5, 0.01)
        C   = max(acidification * 0.5 + dead_zone * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Ocean system failing — acidification and dead zones critical"
        if psi < 0.6:  return "Degraded ocean circulation — nutrient flow disrupted"
        if psi <= 1.2: return "Ocean circulation balanced"
        return "Vigorous ocean system — strong currents and upwelling"
