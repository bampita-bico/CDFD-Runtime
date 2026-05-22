from domains.base import DomainAdapter
class EconomicWarfareAdapter(DomainAdapter):
    def map_to_engine(self, data):
        financial_pressure = data.get("financial_pressure_index", 0.4)
        supply_chain_disruption = data.get("supply_chain_disruption", 0.3)
        export_restriction = data.get("export_restriction_index", 0.3)
        economic_resilience= data.get("economic_resilience", 0.6)
        alternative_partners= data.get("alternative_partners_index", 0.4)
        phi = max(financial_pressure*0.4 + supply_chain_disruption*0.3 + export_restriction*0.3, 0.01)
        C   = max(economic_resilience*0.5 + alternative_partners*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Economic pressure negligible — target has sufficient resilience"
        if psi < 0.6:  return "Economic pressure mounting — some sectors affected"
        if psi <= 1.2: return "Significant economic coercion — growth and stability impacted"
        return "Economic warfare decisive — target economy severely damaged"
