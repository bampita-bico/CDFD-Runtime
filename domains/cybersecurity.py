from domains.base import DomainAdapter

class CybersecurityAdapter(DomainAdapter):
    def map_to_engine(self, data):
        defence_strength = data.get("defence_index", 0.7)
        patch_coverage   = data.get("patch_coverage", 0.8)
        threat_level     = data.get("threat_level", 0.3)
        vulnerability_count = data.get("vulnerability_norm", 0.2)
        phi = max(defence_strength * 0.5 + patch_coverage * 0.5, 0.01)
        C   = max(threat_level * 0.5 + vulnerability_count * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Breach-risk signal - defences overwhelmed by threats"
        if psi < 0.6:  return "High risk — significant vulnerabilities unpatched"
        if psi <= 1.2: return "Security posture adequate — threats managed"
        return "Strong security — proactive defence exceeds threat landscape"
