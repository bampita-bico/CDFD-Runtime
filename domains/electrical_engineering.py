from domains.base import DomainAdapter
class ElectricalEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        power_factor     = data.get("power_factor", 0.9)
        voltage_stability= data.get("voltage_stability", 0.8)
        harmonic_distortion = data.get("harmonic_distortion_norm", 0.1)
        fault_rate       = data.get("fault_rate_norm", 0.05)
        phi = max(power_factor*0.5 + voltage_stability*0.5, 0.01)
        C   = max(harmonic_distortion*0.5 + fault_rate*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Electrical system failing — voltage instability or faults critical"
        if psi < 0.6:  return "Degraded electrical performance — power quality issues"
        if psi <= 1.2: return "Electrical system healthy — power quality maintained"
        return "Excellent electrical system — stable, efficient, low fault rate"
