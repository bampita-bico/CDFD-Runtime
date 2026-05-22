from domains.base import DomainAdapter
class InformationWarfareAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cyber_off   = data.get("cyber_offensive_capacity", 0.4)
        disinfo     = data.get("disinformation_scale", 0.3)
        social_pen  = data.get("social_media_penetration", 0.6)
        resilience  = data.get("resilience_index", 0.6)
        detection   = data.get("detection_capability", 0.5)
        phi = max(cyber_off*0.4 + disinfo*0.3 + social_pen*0.3, 0.01)
        C   = max(resilience*0.5 + detection*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Information space secure — attacks contained"
        if psi < 0.6:  return "Information space contested — disinformation causing confusion"
        if psi <= 1.2: return "Information warfare active — significant social disruption"
        return "Information collapse — democratic discourse undermined"
