from domains.base import DomainAdapter
class RefugeeCrisisAdapter(DomainAdapter):
    def map_to_engine(self, data):
        displaced_millions = data.get("displaced_millions", 1.0) / 50.0
        conflict_driver    = data.get("conflict_driver_intensity", 0.4)
        climate_driver     = data.get("climate_driver_intensity", 0.2)
        host_capacity      = data.get("host_country_capacity", 0.5)
        international_aid  = data.get("international_aid_index", 0.5)
        phi = max(min(displaced_millions,1.0)*0.3 + conflict_driver*0.4 + climate_driver*0.3, 0.01)
        C   = max(host_capacity*0.5 + international_aid*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Refugee situation contained — aid and host capacity sufficient"
        if psi < 0.6:  return "Refugee pressure building — host capacity strained"
        if psi <= 1.2: return "Refugee crisis — humanitarian system overwhelmed"
        return "Catastrophic displacement — mass suffering, system collapse"
