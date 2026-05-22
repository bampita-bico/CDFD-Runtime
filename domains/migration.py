from domains.base import DomainAdapter

class MigrationAdapter(DomainAdapter):
    def map_to_engine(self, data):
        conflict_push  = data.get("conflict_intensity", 0.3)
        climate_push   = data.get("climate_stress", 0.2)
        border_enforce = data.get("border_enforcement", 0.5)
        distance_index = data.get("distance_index", 0.4)
        phi = max(conflict_push*0.6 + climate_push*0.4, 0.01)
        C   = max(border_enforce*0.5 + distance_index*0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "No significant movement — push factors weak or barriers absolute"
        if psi < 0.6:  return "Contained displacement — significant but manageable"
        if psi <= 1.2: return "Mass movement — large-scale migration underway"
        return "Refugee crisis — conflict and climate overwhelming all barriers"
