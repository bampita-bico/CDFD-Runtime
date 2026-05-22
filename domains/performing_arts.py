from domains.base import DomainAdapter
class PerformingArtsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        performance_freq = data.get("performance_frequency_norm", 0.5)
        audience_size    = data.get("audience_size_norm", 0.5)
        funding          = data.get("funding_index", 0.5)
        venue_closure    = data.get("venue_closure_rate", 0.1)
        digital_comp     = data.get("digital_competition", 0.3)
        phi = max(performance_freq*0.4 + audience_size*0.3 + funding*0.3, 0.01)
        C   = max(venue_closure*0.5 + digital_comp*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Performing arts collapsed — venues closed, no audiences"
        if psi < 0.6:  return "Performing arts in crisis — funding and audiences declining"
        if psi <= 1.2: return "Performing arts active — regular performances and audiences"
        return "Performing arts thriving — packed houses, strong funding, innovation"
