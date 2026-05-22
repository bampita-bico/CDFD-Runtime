from domains.base import DomainAdapter
class DesertEcologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        endemic_species_norm = data.get("endemic_species_norm", 0.4)
        water_pulse_events   = data.get("water_pulse_frequency_norm", 0.3)
        vegetation_cover     = data.get("vegetation_cover_norm", 0.2)
        desertification      = data.get("desertification_advance_norm", 0.2)
        human_pressure       = data.get("human_pressure_index", 0.3)
        phi = max(endemic_species_norm*0.4 + water_pulse_events*0.3 + vegetation_cover*0.3, 0.01)
        C   = max(desertification*0.5 + human_pressure*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Hyperarid collapse — desertification eliminating endemic life"
        if psi < 0.6:  return "Desert degraded — human pressure and desertification advancing"
        if psi <= 1.2: return "Desert ecosystem in balance — adapted species thriving"
        return "Biodiverse desert — rich endemic flora and fauna, intact water pulses"
