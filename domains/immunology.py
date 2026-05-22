from domains.base import DomainAdapter

class ImmunologyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        immune_activation = data.get("immune_activation", 0.5)
        antibody_titre    = data.get("antibody_titre_norm", 0.5)
        pathogen_load     = data.get("pathogen_load", 0.3)
        immune_exhaustion = data.get("immune_exhaustion", 0.2)
        phi = max(immune_activation * 0.5 + antibody_titre * 0.5, 0.01)
        C   = max(pathogen_load * 0.5 + immune_exhaustion * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Immune collapse — overwhelming infection or exhaustion"
        if psi < 0.6:  return "Immune compromise — inadequate response to pathogen"
        if psi <= 1.2: return "Immune balance — adequate defence"
        return "Hyperimmune response — autoimmune or cytokine storm risk"
