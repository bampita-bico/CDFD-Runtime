from domains.base import DomainAdapter

class UrologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        urine_flow_rate  = data.get("urine_flow_mL_s", 15) / 30.0
        bladder_capacity = data.get("bladder_capacity_norm", 0.7)
        obstruction      = data.get("obstruction_index", 0.2)
        infection_index  = data.get("uti_severity", 0.1)
        phi = max(min(urine_flow_rate, 1.0) * 0.5 + bladder_capacity * 0.5, 0.01)
        C   = max(obstruction * 0.6 + infection_index * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Urological failure — obstruction or infection critical"
        if psi < 0.6:  return "Urological dysfunction — flow impaired, treatment needed"
        if psi <= 1.2: return "Normal urological function"
        return "High flow state — monitor for overactive bladder or polyuria"
