from domains.base import DomainAdapter

class BiomedicalEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        device_efficacy  = data.get("device_efficacy", 0.8)
        biocompatibility = data.get("biocompatibility", 0.9)
        device_failure   = data.get("device_failure_rate", 0.02)
        regulatory_risk  = data.get("regulatory_risk", 0.2)
        phi = max(device_efficacy * 0.5 + biocompatibility * 0.5, 0.01)
        C   = max(device_failure * 0.4 + regulatory_risk * 0.6, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Device recall risk — biocompatibility or failure rate critical"
        if psi < 0.6:  return "Suboptimal medical device — efficacy or approval barriers"
        if psi <= 1.2: return "Medical device functional and safe"
        return "Breakthrough medical device — excellent efficacy and safety profile"
