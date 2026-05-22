from domains.base import DomainAdapter
class IndustrialAgeAdapter(DomainAdapter):
    def map_to_engine(self, data):
        industrial_output = data.get("industrial_output_norm", 0.6)
        urbanisation_rate = data.get("urbanisation_rate", 0.5)
        technological_change = data.get("technological_change_rate", 0.5)
        labour_conflict   = data.get("labour_conflict_index", 0.3)
        environmental_cost= data.get("environmental_cost_norm", 0.3)
        phi = max(industrial_output*0.4 + urbanisation_rate*0.2 + technological_change*0.4, 0.01)
        C   = max(labour_conflict*0.5 + environmental_cost*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Pre-industrial — mechanisation not yet transforming economy"
        if psi < 0.6:  return "Early industrialisation — social disruption, growth beginning"
        if psi <= 1.2: return "Industrial economy running — growth and urbanisation underway"
        return "Industrial peak — maximum output, technological acceleration"
