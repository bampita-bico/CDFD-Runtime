from domains.base import DomainAdapter

class NeurologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        mmse         = data.get("MMSE", 28)           # 0-30
        lesion_vol   = data.get("lesion_volume_ml", 0.5)
        seizure_freq = data.get("seizures_per_month", 0)
        nihss        = data.get("NIHSS", 0)           # stroke severity 0-42
        phi = max(mmse / 30.0 * 0.6 + (1.0 - min(seizure_freq / 10.0, 1.0)) * 0.4, 0.01)
        C   = max(lesion_vol / 10.0 * 0.5 + nihss / 42.0 * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe neurological-deficit signal"
        if psi < 0.6:  return "Significant neurological-impairment signal"
        if psi < 0.8:  return "Mild-moderate neurological-deficit band"
        if psi <= 1.2: return "Neurologically compensated"
        return "Hyperexcitable state — seizure or migraine risk"
