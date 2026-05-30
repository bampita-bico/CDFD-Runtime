from domains.base import DomainAdapter

class NeurosurgeryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        cerebral_perfusion = data.get("cerebral_perfusion_norm", 0.7)
        icp_norm           = data.get("icp_norm", 0.2)
        gcs                = data.get("gcs_score", 15) / 15.0
        haematoma_volume   = data.get("haematoma_volume_norm", 0.05)
        phi = max(cerebral_perfusion * 0.5 + gcs * 0.5, 0.01)
        C   = max(icp_norm * 0.6 + haematoma_volume * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Neurosurgical-emergency signal - herniation/perfusion-failure band"
        if psi < 0.6:  return "Critical neurological-compromise signal"
        if psi <= 1.2: return "Neurological function preserved post-operatively"
        return "Excellent neurological recovery — full function maintained"
