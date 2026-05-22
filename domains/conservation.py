from domains.base import DomainAdapter
class ConservationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        protected   = data.get("protected_area_fraction", 0.15)
        restoration = data.get("restoration_rate", 0.3)
        enforcement = data.get("enforcement_index", 0.5)
        poaching    = data.get("poaching_pressure", 0.2)
        encroachment= data.get("development_encroachment", 0.3)
        phi = max(protected*0.4 + restoration*0.3 + enforcement*0.3, 0.01)
        C   = max(poaching*0.5 + encroachment*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Conservation failing — protected areas degraded, poaching rampant"
        if psi < 0.6:  return "Conservation under pressure — enforcement and area insufficient"
        if psi <= 1.2: return "Conservation effective — species and habitats protected"
        return "Conservation success — habitat restored, species recovering"
