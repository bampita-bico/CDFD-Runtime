from domains.base import DomainAdapter
class CoralReefsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        coral_cover = data.get("coral_cover_fraction", 0.4)
        fish_biomass= data.get("fish_biomass_norm", 0.5)
        bleaching   = data.get("bleaching_frequency", 0.2)
        temp_anomaly= data.get("ocean_temp_anomaly_norm", 0.3)
        acidif      = data.get("acidification_index", 0.2)
        phi = max(coral_cover*0.5 + fish_biomass*0.5, 0.01)
        C   = max(bleaching*0.4 + temp_anomaly*0.3 + acidif*0.3, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Reef collapse — bleaching and acidification destroying coral"
        if psi < 0.6:  return "Severely degraded reef — fragmented coral, declining fish"
        if psi <= 1.2: return "Reef stable — coral cover maintained"
        return "Pristine reef — high coral cover, rich biodiversity"
