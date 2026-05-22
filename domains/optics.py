from domains.base import DomainAdapter

class OpticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        intensity    = data.get("light_intensity", 0.7)
        wavelength_nm= data.get("wavelength_nm", 550)
        absorption   = data.get("absorption_coeff", 0.1)
        scattering   = data.get("scattering_coeff", 0.1)
        phi = max(intensity * 0.6 + min(1.0 - abs(wavelength_nm-550)/500, 1.0) * 0.4, 0.01)
        C   = max(absorption * 0.5 + scattering * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Optical system opaque — absorption or scattering dominant"
        if psi < 0.6:  return "Significant optical loss — transmission degraded"
        if psi <= 1.2: return "Optical system efficient — good transmission"
        return "Near-perfect optics — minimal loss, coherent propagation"
