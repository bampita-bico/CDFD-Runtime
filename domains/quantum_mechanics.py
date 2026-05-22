from domains.base import DomainAdapter

class QuantumMechanicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        coherence_time   = data.get("coherence_time_norm", 0.5)
        entanglement     = data.get("entanglement_index", 0.4)
        decoherence      = data.get("decoherence_rate", 0.3)
        noise_index      = data.get("quantum_noise", 0.2)
        phi = max(coherence_time * 0.5 + entanglement * 0.5, 0.01)
        C   = max(decoherence * 0.6 + noise_index * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Quantum decoherence — classical regime dominates"
        if psi < 0.6:  return "Partial quantum coherence — significant noise"
        if psi <= 1.2: return "Quantum coherence maintained"
        return "Strong quantum regime — entanglement and coherence maximal"
