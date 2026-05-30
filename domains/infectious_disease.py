from domains.base import DomainAdapter

class InfectiousDiseaseAdapter(DomainAdapter):
    def map_to_engine(self, data):
        pathogen_load = data.get("pathogen_load", 1.0)   # relative units
        temp          = data.get("temperature", 37.0)    # Celsius
        crp           = data.get("CRP", 5.0)             # mg/L
        antibiotic_r  = data.get("antibiotic_resistance", 0.0)  # 0-1
        phi = max(pathogen_load * 0.5 + (temp - 37.0) / 5.0 * 0.3 + crp / 100.0 * 0.2, 0.01)
        C   = max((1.0 - antibiotic_r) * 0.6 + (1.0 - min(crp/200.0, 1.0)) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Septic-shock signal - critical-instability band"
        if psi < 0.6:  return "Sepsis signal - high-pathogen-load band"
        if psi < 0.8:  return "Active-infection signal"
        if psi <= 1.2: return "Infection-control model band"
        return "Immune overactivation — monitor for cytokine storm"
