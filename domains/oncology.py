from domains.base import DomainAdapter

class OncologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        tumour_size     = data.get("tumour_size_cm", 2.0)
        treatment_resp  = data.get("treatment_response", 0.5)  # 0=none, 1=complete
        immune_score    = data.get("immune_score", 0.5)        # tumour infiltrating lymphocytes
        metastasis      = data.get("metastasis", 0)            # 0=no, 1=yes
        phi = max(tumour_size / 5.0 * 0.5 + (1.0 - treatment_resp) * 0.5, 0.01)
        C   = max(immune_score * 0.5 + treatment_resp * 0.3 + (1.0 - metastasis * 0.8) * 0.2, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.5:  return "Treatment controlling disease — continue current regimen"
        if psi < 0.8:  return "Partial response — consider escalation"
        if psi <= 1.2: return "Stable disease — monitor closely"
        return "Progressive disease — treatment resistance likely"
