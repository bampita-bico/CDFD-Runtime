from domains.base import DomainAdapter
class InformationTheoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        channel_cap  = data.get("channel_capacity_norm", 0.7)
        entropy_eff  = data.get("entropy_efficiency", 0.6)
        noise        = data.get("noise_level", 0.2)
        redundancy   = data.get("redundancy_waste", 0.15)
        phi = max(channel_cap*0.5 + entropy_eff*0.5, 0.01)
        C   = max(noise*0.5 + redundancy*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Channel saturated — noise destroying information"
        if psi < 0.6:  return "Below Shannon limit — inefficient encoding"
        if psi <= 1.2: return "Near-optimal information transfer"
        return "Shannon capacity achieved — maximum error-free transmission"
