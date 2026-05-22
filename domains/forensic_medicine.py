from domains.base import DomainAdapter
class ForensicMedicineAdapter(DomainAdapter):
    def map_to_engine(self, data):
        evidence_quality = data.get("evidence_quality_norm", 0.7)
        post_mortem_interval = data.get("post_mortem_interval_norm", 0.3)
        cause_certainty  = data.get("cause_of_death_certainty", 0.7)
        decomposition    = data.get("decomposition_index", 0.2)
        sample_integrity = data.get("sample_integrity", 0.8)
        phi = max(evidence_quality*0.3 + cause_certainty*0.4 + sample_integrity*0.3, 0.01)
        C   = max(post_mortem_interval*0.5 + decomposition*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Forensic evidence compromised — cause of death undeterminable"
        if psi < 0.6:  return "Forensic analysis limited — decomposition or evidence quality poor"
        if psi <= 1.2: return "Forensic findings reliable — cause and manner of death established"
        return "High-quality forensic evidence — complete analysis, court-ready"
