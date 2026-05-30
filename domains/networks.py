from domains.base import DomainAdapter

class NetworksAdapter(DomainAdapter):
    def map_to_engine(self, data):
        throughput    = data.get("throughput_Gbps", 10)
        bandwidth     = data.get("bandwidth_Gbps", 20)
        packet_loss   = data.get("packet_loss_pct", 0.1) / 100.0
        latency_ms    = data.get("latency_ms", 20)
        phi = max(min(throughput/bandwidth,1.0) * 0.5 + (1.0-packet_loss) * 0.5, 0.01)
        C   = max(packet_loss * 0.5 + min(latency_ms/500.0,1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Network failure — congestion or infrastructure fault"
        if psi < 0.6:  return "Degraded network - traffic-shaping/rerouting flag"
        if psi <= 1.2: return "Network operating efficiently"
        return "Network underutilised — capacity expansion opportunity"
