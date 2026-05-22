from domains.base import DomainAdapter

class AcousticsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        amplitude    = data.get("amplitude_dB", 60) / 120.0
        frequency_hz = data.get("frequency_hz", 1000)
        damping      = data.get("damping_coeff", 0.1)
        noise_floor  = data.get("noise_floor_dB", 20) / 120.0
        phi = max(min(amplitude, 1.0) * 0.6 + min(1.0 - abs(frequency_hz-1000)/5000, 1.0) * 0.4, 0.01)
        C   = max(damping * 0.5 + noise_floor * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Signal lost — excessive damping or noise"
        if psi < 0.6:  return "Poor acoustic environment — significant attenuation"
        if psi <= 1.2: return "Good acoustic propagation"
        return "Resonance — signal amplified, risk of feedback"
