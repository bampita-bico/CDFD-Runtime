from domains.base import DomainAdapter
class ChemicalEngineeringAdapter(DomainAdapter):
    def map_to_engine(self, data):
        conversion_rate  = data.get("conversion_rate", 0.7)
        selectivity      = data.get("selectivity", 0.8)
        energy_efficiency= data.get("energy_efficiency", 0.6)
        catalyst_deact   = data.get("catalyst_deactivation", 0.1)
        side_reactions   = data.get("side_reaction_rate", 0.1)
        phi = max(conversion_rate*0.4 + selectivity*0.3 + energy_efficiency*0.3, 0.01)
        C   = max(catalyst_deact*0.5 + side_reactions*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Process failing — catalyst deactivation or runaway side reactions"
        if psi < 0.6:  return "Below-target process performance — yield and selectivity poor"
        if psi <= 1.2: return "Chemical process running efficiently"
        return "Optimal chemical process — high yield, selectivity and energy efficiency"
