from domains.base import DomainAdapter
class ModernHistoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        political_stability = data.get("political_stability", 0.6)
        economic_growth     = data.get("economic_growth_norm", 0.5)
        social_progress     = data.get("social_progress_index", 0.5)
        conflict_intensity  = data.get("conflict_intensity", 0.2)
        ideological_polarisation = data.get("ideological_polarisation", 0.3)
        phi = max(political_stability*0.3 + economic_growth*0.3 + social_progress*0.4, 0.01)
        C   = max(conflict_intensity*0.5 + ideological_polarisation*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Era of crisis — war, depression or ideological conflict"
        if psi < 0.6:  return "Turbulent period — instability and conflict elevated"
        if psi <= 1.2: return "Stable modern period — growth and progress maintained"
        return "Post-war boom or golden age — rapid progress on all dimensions"
