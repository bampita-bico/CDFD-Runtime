from domains.base import DomainAdapter

class ChemistryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        rxn_rate  = data.get("reaction_rate", 1.0)
        temp_k    = data.get("temperature_K", 298)
        catalyst  = data.get("catalyst_efficiency", 0.5)  # 0-1
        inhibitor = data.get("inhibitor_conc", 0.0)       # relative
        phi = max(rxn_rate * 0.4 + min(temp_k/500.0,1.0) * 0.3 + catalyst * 0.3, 0.01)
        C   = max(inhibitor * 0.6 + (1.0 - catalyst) * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Reaction quenched — activation energy barrier not overcome"
        if psi < 0.6:  return "Slow reaction — increase temperature or catalyst"
        if psi <= 1.2: return "Optimal reaction conditions"
        return "Runaway reaction — control temperature and inhibitor"
