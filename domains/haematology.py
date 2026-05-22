from domains.base import DomainAdapter

class HaematologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        hb        = data.get("Hb", 13.0)          # g/dL
        platelets = data.get("platelets", 250)     # x10^9/L
        wbc       = data.get("WBC", 7.0)           # x10^9/L
        inr       = data.get("INR", 1.0)
        phi = max(hb / 15.0 * 0.4 + platelets / 400.0 * 0.3 + (1.0 - abs(wbc-7.0)/20.0) * 0.3, 0.01)
        C   = max(inr * 0.4 + (1.0 - hb / 17.0) * 0.4 + (1.0 - min(platelets/500.0,1.0)) * 0.2, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Haematological crisis — transfusion and bone marrow support"
        if psi < 0.6:  return "Severe cytopaenia — investigate bone marrow pathology"
        if psi < 0.8:  return "Mild haematological impairment — targeted replacement"
        if psi <= 1.2: return "Haematological equilibrium"
        return "Hyperviscosity/thrombotic risk — consider cytoreduction"
