from domains.base import DomainAdapter

class EvolutionAdapter(DomainAdapter):
    def map_to_engine(self, data):
        mutation_r  = data.get("mutation_rate", 1e-6)
        selection_p = data.get("selection_pressure", 0.5)  # 0-1
        pop_size    = data.get("population_size", 10000)
        env_change  = data.get("environmental_change_rate", 0.1)  # 0-1
        phi = max(mutation_r * 1e7 * 0.3 + selection_p * 0.4 + (1.0-env_change) * 0.3, 0.01)
        C   = max(env_change * 0.5 + (1.0 - min(pop_size/100000.0,1.0)) * 0.5, 0.01)
        return phi, C

    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Extinction risk — population below critical threshold"
        if psi < 0.6:  return "Evolutionary bottleneck — low genetic diversity"
        if psi <= 1.2: return "Adaptive evolution in progress"
        return "Rapid adaptive radiation — high evolutionary flux"
