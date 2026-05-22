from domains.base import DomainAdapter

class PhysicalChemistryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        gibbs_driving    = data.get("gibbs_energy_norm", 0.5)
        reaction_rate    = data.get("reaction_rate_norm", 0.5)
        activation_norm  = data.get("activation_barrier_norm", 0.4)
        equilibrium_shift= data.get("equilibrium_displacement", 0.2)
        phi = max(gibbs_driving * 0.5 + reaction_rate * 0.5, 0.01)
        C   = max(activation_norm * 0.6 + equilibrium_shift * 0.4, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Reaction blocked — activation barrier too high"
        if psi < 0.6:  return "Slow kinetics — thermodynamics unfavourable"
        if psi <= 1.2: return "Reaction proceeding efficiently"
        return "Spontaneous fast reaction — high driving force"
