from domains.base import DomainAdapter
class NuclearMedicineAdapter(DomainAdapter):
    def map_to_engine(self, data):
        tracer_uptake    = data.get("tracer_uptake_norm", 0.7)
        image_quality    = data.get("image_quality_norm", 0.7)
        radiation_dose_norm = data.get("radiation_dose_norm", 0.2)
        scanner_resolution  = data.get("scanner_resolution_norm", 0.7)
        phi = max(tracer_uptake*0.4 + image_quality*0.3 + scanner_resolution*0.3, 0.01)
        C   = max(radiation_dose_norm*0.5 + (1.0-image_quality)*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Non-diagnostic nuclear study — tracer failure or poor resolution"
        if psi < 0.6:  return "Suboptimal nuclear imaging — dose or quality limiting interpretation"
        if psi <= 1.2: return "Nuclear medicine study diagnostic — physiological data obtained"
        return "Excellent nuclear medicine imaging — high resolution, optimal tracer uptake"
