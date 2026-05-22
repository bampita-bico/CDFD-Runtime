from domains.base import DomainAdapter

class CloudComputingAdapter(DomainAdapter):
    def map_to_engine(self, data):
        uptime_norm      = data.get("uptime_fraction", 0.999)
        compute_utilisation = data.get("compute_utilisation", 0.6)
        latency_norm     = data.get("latency_norm", 0.2)
        cost_efficiency  = data.get("cost_efficiency", 0.6)
        phi = max(uptime_norm * 0.4 + compute_utilisation * 0.3 + cost_efficiency * 0.3, 0.01)
        C   = max(latency_norm * 0.5 + (1.0 - uptime_norm) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Cloud outage — services unavailable"
        if psi < 0.6:  return "Degraded cloud performance — latency and cost issues"
        if psi <= 1.2: return "Cloud infrastructure healthy — services responsive"
        return "Optimal cloud operations — high availability, low cost, low latency"
