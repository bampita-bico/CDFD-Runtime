from domains.base import DomainAdapter
class DevelopmentEconomicsAdapter(DomainAdapter):
    def map_to_engine(self, data):
        gdp_growth  = data.get("gdp_growth_norm", 0.5)
        hdi         = data.get("human_development_index", 0.6)
        fdi         = data.get("fdi_norm", 0.3)
        poverty     = data.get("poverty_rate", 0.3)
        debt        = data.get("debt_burden_norm", 0.3)
        phi = max(gdp_growth*0.3 + hdi*0.4 + fdi*0.3, 0.01)
        C   = max(poverty*0.5 + debt*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Development trap — poverty and debt constraining all growth"
        if psi < 0.6:  return "Slow development — structural barriers limiting progress"
        if psi <= 1.2: return "Developing economy on track — growth and HDI rising"
        return "Rapid development — strong growth, improving human development"
