from domains.base import DomainAdapter
class CartographyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        spatial_accuracy = data.get("spatial_accuracy_norm", 0.7)
        coverage_fraction= data.get("coverage_fraction", 0.8)
        resolution_norm  = data.get("resolution_norm", 0.6)
        projection_error = data.get("projection_distortion", 0.15)
        temporal_currency= data.get("map_currency_norm", 0.7)
        phi = max(spatial_accuracy*0.3 + coverage_fraction*0.3 + resolution_norm*0.2 + temporal_currency*0.2, 0.01)
        C   = max(projection_error*0.5 + (1.0-temporal_currency)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cartographic void — no reliable spatial data"
        if psi < 0.6:  return "Poor cartography — significant gaps and distortions"
        if psi <= 1.2: return "Reliable maps — accurate and current spatial data"
        return "Excellent cartographic coverage — high resolution, precise, up-to-date"
