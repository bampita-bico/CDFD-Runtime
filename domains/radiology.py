from domains.base import DomainAdapter

class RadiologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        signal_to_noise  = data.get("snr_norm", 0.7)
        contrast         = data.get("contrast_index", 0.6)
        artefact_load    = data.get("artefact_index", 0.15)
        tissue_attenuation = data.get("tissue_attenuation", 0.2)
        phi = max(signal_to_noise * 0.5 + contrast * 0.5, 0.01)
        C   = max(artefact_load * 0.5 + tissue_attenuation * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Non-diagnostic — image quality insufficient"
        if psi < 0.6:  return "Poor image quality — artefacts limiting interpretation"
        if psi <= 1.2: return "Diagnostic quality — clear anatomical detail"
        return "Excellent imaging — high resolution and contrast"
