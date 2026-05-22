from domains.base import DomainAdapter

class ComputationalPhysicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        compute_power    = data.get("compute_flops_norm", 0.5)
        algorithm_efficiency = data.get("algorithm_efficiency", 0.6)
        numerical_error  = data.get("numerical_error_norm", 0.1)
        convergence_fail = data.get("convergence_failure_rate", 0.05)
        phi = max(compute_power * 0.4 + algorithm_efficiency * 0.6, 0.01)
        C   = max(numerical_error * 0.5 + convergence_fail * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Simulation failing — numerical instability or resource exhaustion"
        if psi < 0.6:  return "Poor convergence — results unreliable"
        if psi <= 1.2: return "Simulation converging — reliable results"
        return "High-performance simulation — fast convergence, high fidelity"
