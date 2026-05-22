from domains.base import DomainAdapter
class InvasiveSpeciesAdapter(DomainAdapter):
    def map_to_engine(self, data):
        native_int  = data.get("native_species_integrity", 0.7)
        eco_resist  = data.get("ecosystem_resistance", 0.5)
        invasion_p  = data.get("invasion_pressure", 0.2)
        control     = data.get("control_effectiveness", 0.5)
        phi = max(native_int*0.5 + eco_resist*0.5, 0.01)
        C   = max(invasion_p*0.5 + (1.0-control)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Ecosystem overrun — invasives dominant, native collapse"
        if psi < 0.6:  return "Significant invasion — native species impacted"
        if psi <= 1.2: return "Invasives present but managed — natives intact"
        return "Native ecosystem intact — invasives contained"
