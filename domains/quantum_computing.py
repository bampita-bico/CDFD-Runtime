from domains.base import DomainAdapter

class QuantumComputingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        qubit_count_norm = data.get("logical_qubit_norm", 0.3)
        gate_fidelity    = data.get("gate_fidelity", 0.99)
        error_rate       = data.get("error_rate", 0.01)
        decoherence_norm = data.get("decoherence_norm", 0.3)
        phi = max(qubit_count_norm * 0.4 + gate_fidelity * 0.6, 0.01)
        C   = max(error_rate * 0.5 + decoherence_norm * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "NISQ failure — error rates too high for useful computation"
        if psi < 0.6:  return "Limited quantum advantage — decoherence constraining circuits"
        if psi <= 1.2: return "Functional quantum processor — advantage in specific tasks"
        return "Fault-tolerant quantum computing — exponential advantage demonstrated"
