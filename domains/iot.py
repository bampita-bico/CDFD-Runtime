from domains.base import DomainAdapter
class IoTAdapter(DomainAdapter):
    def map_to_engine(self, data):
        device_density   = data.get("device_density_norm", 0.5)
        connectivity     = data.get("connectivity_reliability", 0.7)
        data_throughput  = data.get("data_throughput_norm", 0.6)
        security_risk    = data.get("security_vulnerability_norm", 0.3)
        latency_norm     = data.get("latency_norm", 0.2)
        phi = max(device_density*0.3 + connectivity*0.4 + data_throughput*0.3, 0.01)
        C   = max(security_risk*0.5 + latency_norm*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "IoT system failing — connectivity or security breach critical"
        if psi < 0.6:  return "IoT underperforming — latency and vulnerabilities degrading value"
        if psi <= 1.2: return "IoT network operational — devices connected and data flowing"
        return "High-performance IoT — dense, secure, low-latency network"
