from domains.base import DomainAdapter
class MechanicalEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        efficiency       = data.get("mechanical_efficiency", 0.7)
        reliability      = data.get("system_reliability", 0.8)
        wear_rate        = data.get("wear_rate_norm", 0.1)
        vibration_index  = data.get("vibration_index", 0.1)
        phi = max(efficiency*0.5 + reliability*0.5, 0.01)
        C   = max(wear_rate*0.5 + vibration_index*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Mechanical failure — wear or vibration causing breakdown"
        if psi < 0.6:  return "Below design performance — reliability and efficiency poor"
        if psi <= 1.2: return "Mechanical system performing within specification"
        return "High-performance machinery — excellent efficiency and reliability"
