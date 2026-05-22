from domains.base import DomainAdapter

class GeologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        seismic_r  = data.get("seismic_rate", 0.1)    # events/yr normalised
        magma_flux = data.get("magma_flux", 0.2)       # relative
        fault_lock = data.get("fault_lock_index", 0.7) # 0-1
        erosion_r  = data.get("erosion_rate", 0.3)     # relative
        phi = max(magma_flux * 0.4 + seismic_r * 0.3 + erosion_r * 0.3, 0.01)
        C   = max(fault_lock * 0.6 + (1.0 - erosion_r) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Geologically locked — stress accumulating, major event risk"
        if psi < 0.6:  return "Elevated tectonic stress — monitor fault systems"
        if psi <= 1.2: return "Stable geological regime"
        return "Active tectonics — frequent small releases reducing major event risk"
