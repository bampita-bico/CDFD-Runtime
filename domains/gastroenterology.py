from domains.base import DomainAdapter

class GastroenterologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        motility  = data.get("motility_score", 0.8)    # 0-1
        absorption= data.get("absorption_score", 0.9)  # 0-1
        crohn_hbi = data.get("HBI", 0)                 # Harvey-Bradshaw index
        calprotect= data.get("calprotectin", 50)       # ug/g
        phi = max(motility * 0.5 + absorption * 0.5, 0.01)
        C   = max(min(crohn_hbi / 16.0, 1.0) * 0.5 + min(calprotect / 1000.0, 1.0) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Severe intestinal-failure signal"
        if psi < 0.6:  return "Active IBD/malabsorption signal"
        if psi < 0.8:  return "Partial-remission model band"
        if psi <= 1.2: return "GI equilibrium"
        return "Functional GI disorder — motility dysregulation"
