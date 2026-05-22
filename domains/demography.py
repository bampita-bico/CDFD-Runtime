from domains.base import DomainAdapter
class DemographyAdapter(DomainAdapter):
    def map_to_engine(self, data):
        growth = data.get("population_growth_rate", 0.01)
        life_exp = data.get("life_expectancy_norm", 0.75)
        dependency = data.get("dependency_ratio", 0.4)
        migration = data.get("migration_pressure", 0.2)
        phi = max(min(growth/0.05,1.0)*0.4 + life_exp*0.6, 0.01)
        C   = max(dependency*0.5 + migration*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Demographic crisis — ageing or collapsing population"
        if psi < 0.6:  return "Demographic stress — imbalanced age structure"
        if psi <= 1.2: return "Healthy demographic balance"
        return "Demographic boom — rapid growth, youth dividend"
