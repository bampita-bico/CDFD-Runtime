from domains.base import DomainAdapter
class MedievalHistoryAdapter(DomainAdapter):
    def map_to_engine(self, data):
        surplus     = data.get("agricultural_surplus", 0.5)
        trade       = data.get("trade_route_activity", 0.4)
        church      = data.get("church_stability", 0.5)
        feudal      = data.get("feudal_order", 0.5)
        plague      = data.get("plague_index", 0.1)
        invasion    = data.get("invasion_index", 0.2)
        famine      = data.get("famine_index", 0.15)
        phi = max(surplus*0.3 + trade*0.3 + church*0.2 + feudal*0.2, 0.01)
        C   = max(plague*0.4 + invasion*0.3 + famine*0.3, 0.01)
        return phi, C
    def interpret(self, state):
        psi = state.mean_psi()
        if psi < 0.3:  return "Medieval collapse — plague, famine or invasion"
        if psi < 0.6:  return "Feudal stress — population and trade declining"
        if psi <= 1.2: return "Stable medieval order — surplus and trade maintained"
        return "High medieval florescence — cathedral building, trade expansion"
