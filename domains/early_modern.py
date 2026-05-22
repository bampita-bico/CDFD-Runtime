from domains.base import DomainAdapter
class EarlyModernAdapter(DomainAdapter):
    def map_to_engine(self, data):
        trade_expansion  = data.get("trade_expansion_index", 0.5)
        state_centralisation = data.get("state_centralisation", 0.5)
        intellectual_flux= data.get("intellectual_flux", 0.4)
        reformation_conflict = data.get("religious_conflict_index", 0.3)
        plague_pressure  = data.get("plague_pressure", 0.1)
        phi = max(trade_expansion*0.3 + state_centralisation*0.3 + intellectual_flux*0.4, 0.01)
        C   = max(reformation_conflict*0.5 + plague_pressure*0.5, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Early modern crisis — religious wars and plague collapsing society"
        if psi < 0.6:  return "Turbulent transition — reformation and state-building in conflict"
        if psi <= 1.2: return "Early modern consolidation — trade and states stabilising"
        return "Renaissance or Enlightenment peak — intellectual and commercial florescence"
